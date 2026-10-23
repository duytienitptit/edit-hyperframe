"""Turn a word-level transcript JSON into caption chunks for Remotion.

Usage:
  tools/.venv/bin/python tools/build_captions.py <transcript.json> <captions.json>
      [--start S] [--end E] [--max-words 9] [--fixes fixes.json]

- Chunks break on punctuation, on pauses >= 0.3s, or at --max-words.
- Only words inside [start, end) are kept; times are shifted so `start` becomes 0.
- fixes.json: {"wrong phrase": "right phrase"} applied to chunk text (spelling fixes).
Output: [{"text", "startMs", "endMs", "words": [{"text","startMs","endMs"}]}]
"""
import argparse, json

PAUSE = 0.3
MIN_CUE = 0.8  # never flash a cue shorter than this (seconds)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("transcript")
    p.add_argument("out")
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, default=1e9)
    p.add_argument("--max-words", type=int, default=18)
    p.add_argument("--fixes")
    a = p.parse_args()

    fixes = json.load(open(a.fixes, encoding="utf-8")) if a.fixes else {}
    words = [w for s in json.load(open(a.transcript, encoding="utf-8"))["segments"] for w in s["words"]
             if w["start"] >= a.start and w["end"] <= a.end + 0.05]

    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        punct = w["word"][-1:] in ",.;:!?"
        pause = nxt is not None and nxt["start"] - w["end"] >= PAUSE
        if nxt is None or punct or pause:
            # split long phrases into balanced parts instead of hard-cutting at max_words
            n = -(-len(cur) // a.max_words)
            size = -(-len(cur) // n)
            chunks.extend(cur[k:k + size] for k in range(0, len(cur), size))
            cur = []

    # merge chunks that are too short in time into the previous one
    merged = []
    for c in chunks:
        if merged and c[-1]["end"] - c[0]["start"] < MIN_CUE and len(merged[-1]) + len(c) <= a.max_words + 3:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)

    out = []
    for c in merged:
        text = " ".join(w["word"] for w in c).strip().rstrip(",.;:")
        for k, v in fixes.items():
            text = text.replace(k, v)
        ms = lambda t: int(round((t - a.start) * 1000))
        out.append({
            "text": text,
            "startMs": ms(c[0]["start"]),
            "endMs": ms(c[-1]["end"]),
            "words": [{"text": w["word"].rstrip(",.;:"), "startMs": ms(w["start"]), "endMs": ms(w["end"])} for w in c],
        })
    # apply fixes to word texts too (single-word fixes only)
    for cue in out:
        for w in cue["words"]:
            for k, v in fixes.items():
                if " " not in k and w["text"] == k:
                    w["text"] = v

    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in out:
        print(f"{c['startMs']/1000:6.2f}-{c['endMs']/1000:6.2f}  {c['text']}")


if __name__ == "__main__":
    main()
