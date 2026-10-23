"""Align caption text (one cue per line) to a word-level transcript.

Usage:
  tools/.venv/bin/python tools/align_captions.py <cues.txt> <transcript.json> <captions.json>
      [--start S] [--end E] [--max-chars 52]

cues.txt: one on-screen caption per line, already correctly spelled (from the user's caption
file, a corrected transcript, or a translation). Blank lines and lines starting with # are ignored.
Each line must fit on ONE line on screen -> warns if a line exceeds --max-chars.

Text comes from cues.txt (exact spelling); timing comes from whisper words (fuzzy-matched).
Only for cues in the same language as the audio.
Output: [{"text","startMs","endMs","words":[{"text","startMs","endMs"}]}]
"""
import argparse, difflib, json, re, unicodedata


def norm(w):
    w = unicodedata.normalize("NFC", w.lower())
    return re.sub(r"[^\w]", "", w)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cues")
    p.add_argument("transcript")
    p.add_argument("out")
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, default=1e9)
    p.add_argument("--max-chars", type=int, default=52)
    a = p.parse_args()

    lines = [l.strip() for l in open(a.cues, encoding="utf-8")]
    lines = [l for l in lines if l and not l.startswith("#")]
    tw = [w for s in json.load(open(a.transcript, encoding="utf-8"))["segments"] for w in s["words"]
          if w["start"] >= a.start and w["end"] <= a.end + 0.05]

    # cue tokens, remembering which line each belongs to
    toks = []
    for li, l in enumerate(lines):
        for w in l.split():
            toks.append({"line": li, "text": w, "n": norm(w)})

    sm = difflib.SequenceMatcher(a=[t["n"] for t in toks], b=[norm(w["word"]) for w in tw], autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            t, w = toks[blk.a + k], tw[blk.b + k]
            t["s"], t["e"] = w["start"], w["end"]

    # fill unmatched tokens by interpolating between matched neighbours
    for i, t in enumerate(toks):
        if "s" in t:
            continue
        prev = next((toks[j] for j in range(i - 1, -1, -1) if "s" in toks[j]), None)
        nxt = next((toks[j] for j in range(i + 1, len(toks)) if "s" in toks[j]), None)
        lo = prev["e"] if prev else (nxt["s"] - 0.3 if nxt else a.start)
        hi = nxt["s"] if nxt else lo + 0.3
        t["s"], t["e"] = lo, max(lo + 0.05, hi)
        t["interp"] = True

    ms = lambda x: int(round((x - a.start) * 1000))
    out, unmatched = [], 0
    for li, l in enumerate(lines):
        lt = [t for t in toks if t["line"] == li]
        unmatched += sum(1 for t in lt if t.get("interp"))
        display = l.rstrip(",.;:")
        out.append({
            "text": display,
            "startMs": ms(lt[0]["s"]),
            "endMs": ms(lt[-1]["e"]),
            "words": [{"text": t["text"].rstrip(",.;:") if i == len(lt) - 1 else t["text"],
                       "startMs": ms(t["s"]), "endMs": ms(t["e"])} for i, t in enumerate(lt)],
        })

    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in out:
        flag = "  <-- TOO LONG" if len(c["text"]) > a.max_chars else ""
        print(f"{c['startMs']/1000:6.2f}-{c['endMs']/1000:6.2f} [{len(c['text']):2d}] {c['text']}{flag}")
    print(f"matched {len(toks) - unmatched}/{len(toks)} tokens")


if __name__ == "__main__":
    main()
