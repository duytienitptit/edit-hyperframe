"""Detect shot changes (hard cuts and dissolves) with ffmpeg scdet.

Frames are sampled at --fps (default 4) and downscaled, so a ~1s dissolve shows up as one
jump between samples instead of 60 tiny per-frame differences. Nearby peaks are merged.

Usage:
  python3 tools/detect_scenes.py <video> <out.json> [--threshold 3] [--fps 4] [--merge 1.0]

Output: [{"t": 46.5, "score": 7.8}, ...]  (t = middle of the change, seconds; dissolves span ~±0.5s)
"""
import argparse, json, os, re, subprocess, tempfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("out")
    p.add_argument("--threshold", type=float, default=3.0, help="scdet score 0-100; lower = more sensitive")
    p.add_argument("--fps", type=float, default=4.0, help="sampling rate; higher catches short dissolves less")
    p.add_argument("--merge", type=float, default=1.0, help="peaks closer than this (s) count as one change")
    p.add_argument("--width", type=int, default=320)
    a = p.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "scd.txt")
        subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-an", "-vf",
                        f"fps={a.fps},scale={a.width}:-2,scdet=threshold=1,metadata=print:file={log}",
                        "-f", "null", "-"], check=True)
        text = open(log).read()

    samples = [(float(t), float(s)) for t, s in
               re.findall(r"pts_time:([\d.]+)\s+lavfi\.scd\.mafd=[\d.]+\s+lavfi\.scd\.score=([\d.]+)", text)]
    peaks = [(t, s) for t, s in samples[1:] if s >= a.threshold]  # first sample has no predecessor

    cuts = []
    for t, s in peaks:
        if cuts and t - cuts[-1]["t"] < a.merge:
            if s > cuts[-1]["score"]:
                cuts[-1] = {"t": t, "score": round(s, 1)}
        else:
            cuts.append({"t": t, "score": round(s, 1)})

    with open(a.out, "w") as f:
        json.dump(cuts, f, indent=1)
    print(f"{len(cuts)} changes -> {a.out}")
    for c in cuts:
        print(f"  {c['t']:7.2f}s  score {c['score']}")


if __name__ == "__main__":
    main()
