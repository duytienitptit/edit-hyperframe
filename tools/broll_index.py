"""Shared b-roll library (library/broll) -> library/broll/index.json: probe, check, search.

Usage:
  python3 tools/broll_index.py scan [--thumbs]     probe every clip, refresh technical fields, add stub entries
                                                  for new files, (re)build thumbnail strips, report problems
  python3 tools/broll_index.py check              report only: missing files, files not indexed, untagged clips
  python3 tools/broll_index.py search <words...> [--mood M] [--people P] [--shot S] [--orient O]
                                                  [--min-dur SEC] [--style STYLE] [--unused]

Technical fields come from ffprobe and are rewritten on every scan: duration, width, height, fps, orientation,
has_audio, color_transfer, hdr, size_mb. Descriptive fields are written by hand (vocabulary in index.json
"_vocab"): idea, tags (Vietnamese + English keywords), mood, shot, subject, people, motion, good_ranges
([in, out, note]), fits_styles, notes. A stub entry has "todo": true until those are filled.
Thumbnails: library/broll/_thumbs/<theme>/<stem>.jpg (5 frames across the clip; local, not versioned).
Search ignores Vietnamese diacritics and also lists past web searches from library/broll/searches.json.
"""
import argparse, json, os, subprocess, sys, unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "library", "broll")
INDEX = os.path.join(ROOT, "index.json")
SEARCHES = os.path.join(ROOT, "searches.json")
THUMBS = os.path.join(ROOT, "_thumbs")
EXT = (".mp4", ".mov", ".m4v", ".webm")
HDR = ("arib-std-b67", "smpte2084")
DESCRIPTIVE = ("tags", "mood", "shot", "subject", "people", "motion")


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


def fold(text):
    text = str(text).lower().replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def files_on_disk():
    out = []
    for theme in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, theme)
        if theme.startswith(("_", ".")) or not os.path.isdir(d):
            continue
        out += [f"{theme}/{n}" for n in sorted(os.listdir(d)) if n.lower().endswith(EXT)]
    return out


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration,size:stream=codec_type,width,height,r_frame_rate,color_transfer",
                        "-of", "json", path], capture_output=True, text=True)
    j = json.loads(r.stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    w, h = v["width"], v["height"]
    ct = v.get("color_transfer", "unknown")
    return {"duration": round(float(j["format"]["duration"]), 2), "width": w, "height": h,
            "fps": round(num / den, 2) if den else 0.0,
            "orientation": "portrait" if h > w else "landscape" if w > h else "square",
            "has_audio": any(s["codec_type"] == "audio" for s in j["streams"]),
            "color_transfer": ct, "hdr": ct in HDR,
            "size_mb": round(int(j["format"]["size"]) / 1e6, 1)}


def thumb(rel, dur):
    out = os.path.join(THUMBS, os.path.splitext(rel)[0] + ".jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(ROOT, rel), "-vf",
                    f"fps=5/{max(dur, 0.5)},scale=200:200:force_original_aspect_ratio=decrease,"
                    "pad=200:200:(ow-iw)/2:(oh-ih)/2,tile=5x1:padding=2", "-frames:v", "1", out], check=False)


def report(index):
    disk = set(files_on_disk())
    known = {c["file"] for c in index["clips"]}
    problems = 0
    for f in sorted(known - disk):
        print(f"MISSING FILE  {f}")
        problems += 1
    for f in sorted(disk - known):
        print(f"NOT INDEXED   {f}")
        problems += 1
    for c in index["clips"]:
        empty = [k for k in DESCRIPTIVE if not c.get(k)]
        if c.get("todo") or empty:
            print(f"UNTAGGED      {c['file']}  (empty: {', '.join(empty) or '-'})")
            problems += 1
        if c.get("hdr"):
            print(f"HDR           {c['file']}  ({c.get('color_transfer')}) -> convert to bt709 when baking")
    print(f"{len(index['clips'])} clips, {len({c['theme'] for c in index['clips']})} themes, {problems} problems")


def cmd_scan(args):
    index = load(INDEX, {"clips": []})
    by_file = {c["file"]: c for c in index["clips"]}
    for rel in files_on_disk():
        c = by_file.get(rel)
        if c is None:
            theme, name = rel.split("/", 1)
            stem = os.path.splitext(name)[0]
            src, _, sid = stem.partition("_")
            c = {"file": rel, "theme": theme, "idea": "", "title": "", "source": src,
                 "source_id": int(sid) if sid.isdigit() else sid, "page": "", "license": "",
                 **{k: [] if k in ("tags", "mood") else "" for k in DESCRIPTIVE},
                 "good_ranges": [], "fits_styles": [], "notes": "", "used_in": [], "todo": True}
            index["clips"].append(c)
            by_file[rel] = c
        c.update(probe(os.path.join(ROOT, rel)))
        if args.thumbs:
            thumb(rel, c["duration"])
    index["clips"].sort(key=lambda c: c["file"])
    save(INDEX, index)
    report(index)


def cmd_check(args):
    report(load(INDEX, {"clips": []}))


def cmd_search(args):
    index = load(INDEX, {"clips": []})
    words = [fold(w) for w in args.words]
    hits = []
    for c in index["clips"]:
        if args.mood and args.mood not in c.get("mood", []):
            continue
        if args.people and c.get("people") != args.people:
            continue
        if args.shot and c.get("shot") != args.shot:
            continue
        if args.orient and c.get("orientation") != args.orient:
            continue
        if args.min_dur and c.get("duration", 0) < args.min_dur:
            continue
        if args.style and c.get("fits_styles") and args.style not in c["fits_styles"]:
            continue
        if args.unused and c.get("used_in"):
            continue
        hay = fold(" ".join([c["theme"], c.get("idea", ""), c.get("title", ""), c.get("notes", ""),
                             " ".join(c.get("tags", []))]))
        score = sum(w in hay for w in words) if words else 1
        if score:
            hits.append((score, c))
    hits.sort(key=lambda x: (-x[0], len(x[1].get("used_in", []))))
    for score, c in hits:
        used = ", ".join(u["project"] for u in c.get("used_in", [])) or "unused"
        print(f"{score}  {c['file']:<38} {c.get('duration', 0):>5.1f}s {c.get('width')}x{c.get('height')}"
              f"  {c.get('shot', '')}/{c.get('people', '')}  {c.get('idea', '')}  [{used}]")
    if not hits:
        print("no clip matches")
    past = [s for s in load(SEARCHES, {"searches": []})["searches"]
            if words and any(w in fold(s["query"] + " " + s.get("for", "")) for w in words)]
    for s in past:
        print(f"past search {s['date']} {s['site']} \"{s['query']}\" -> picked {s.get('picked', [])}, "
              f"seen {len(s.get('seen', []))}, rejected {len(s.get('rejected', {}))}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--thumbs", action="store_true")
    s.set_defaults(fn=cmd_scan)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    s = sub.add_parser("search")
    s.add_argument("words", nargs="*")
    s.add_argument("--mood")
    s.add_argument("--people")
    s.add_argument("--shot")
    s.add_argument("--orient")
    s.add_argument("--min-dur", type=float)
    s.add_argument("--style")
    s.add_argument("--unused", action="store_true")
    s.set_defaults(fn=cmd_search)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
