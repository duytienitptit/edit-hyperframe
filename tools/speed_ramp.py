#!/usr/bin/env python3
"""Speed-ramp-in clip renderer (reel style: shot enters fast + smeared, eases to 1x).

Reads a source range through an ffmpeg filter chain (crop/scale/grade), remaps time with
  v(t) = 1 + (v0 - 1) * (1 - t/T)^2   for t < T,   v = 1 after,
and fakes motion blur by averaging the source frames swept during each output frame
(window grows with speed, zero at 1x so the settled part stays sharp).

Usage:
  python3 tools/speed_ramp.py <src> <out.mp4> --in S --dur D [--v0 3.5] [--ramp 0.35]
         [--fps 30] [--size 1080x1920] [--vf "<ffmpeg filter chain>"] [--shutter 1.2]
--v0 1 = no ramp (plain trim through the filter chain).
"""
import argparse
import math
import subprocess
import numpy as np


def src_time(t, v0, T):
    """Source seconds consumed after t output seconds."""
    k = (v0 - 1.0) * T / 3.0
    if t < T:
        return t + k * (1.0 - (1.0 - t / T) ** 3)
    return t + k


def speed(t, v0, T):
    return 1.0 + (v0 - 1.0) * (1.0 - t / T) ** 2 if t < T else 1.0


def probe_fps(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=r_frame_rate", "-of", "csv=p=0", path], capture_output=True, text=True)
    n, d = r.stdout.strip().split("/")
    return float(n) / float(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--in", dest="tin", type=float, required=True)
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--v0", type=float, default=3.5)
    ap.add_argument("--ramp", type=float, default=0.35)
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--vf", default="null")
    ap.add_argument("--shutter", type=float, default=1.2)
    ap.add_argument("--crf", default="16")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x"))
    fs = probe_fps(a.src)
    nout = math.ceil(a.dur * a.fps) + 1  # one spare frame so the clip never ends before its slot
    need = src_time(a.dur, a.v0, a.ramp) + 3 / fs

    dec = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a.tin:.4f}", "-t", f"{need:.4f}", "-i", a.src,
                          "-vf", a.vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    fr = np.frombuffer(dec.stdout, np.uint8).reshape(-1, H, W, 3)
    last = len(fr) - 1

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", f"{a.fps}", "-i", "-", "-c:v", "libx264", "-crf", a.crf, "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    for n in range(nout):
        t = n / a.fps
        s = src_time(t, a.v0, a.ramp)
        w = (speed(t, a.v0, a.ramp) - 1.0) / a.fps * a.shutter  # blur window, 0 at 1x
        if w < 0.5 / fs:
            img = fr[min(last, round(s * fs))]
        else:
            idx = [min(last, max(0, round((s + w * (j / 7 - 0.5)) * fs))) for j in range(8)]
            img = np.mean(np.stack([fr[i].astype(np.float32) for i in idx]), axis=0).round().astype(np.uint8)
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"{a.out}: {nout} frames, src {a.tin:.2f}+{src_time(a.dur, a.v0, a.ramp):.2f}s of {len(fr)/fs:.2f}s read")


if __name__ == "__main__":
    main()
