"""Voice-activity regions on a (denoised) track — finds real lines hidden in "chatter" sections.

Usage: python3 tools/voice_activity.py <audio> [--start S --end E] [--thresh -32] [--min 0.3] [--merge 0.4] [--profile]
Prints regions (source seconds) where the 250 ms RMS stays above --thresh, merged across gaps < --merge.
Run it on assets/audio/voice_clean_B.wav (RNNoise keeps voices, removes most ambience), then confirm each region
with tools/transcribe_chunks.py on a short window. BaiThi1018 lesson: the meal section ASR'd as garbage, yet it held
the closing line ("Video … đến đây là kết thúc. Chào mọi người!") — the user heard music drowning it.
"""
import argparse, subprocess
import numpy as np

SR = 8000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--thresh", type=float, default=-32.0)
    ap.add_argument("--min", type=float, default=0.3)
    ap.add_argument("--merge", type=float, default=0.4)
    ap.add_argument("--profile", action="store_true", help="also print the 250 ms profile")
    a = ap.parse_args()
    cmd = ["ffmpeg", "-v", "error", "-ss", str(a.start)] + (["-t", str(a.end - a.start)] if a.end else []) + \
          ["-i", a.audio, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
    hop = SR // 4
    v = [20 * np.log10(np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(x) - hop + 1, hop)]
    if a.profile:
        print(" ".join(f"{a.start + i * 0.25:.2f}:{d:.0f}" for i, d in enumerate(v)))
    regs = []
    for i, d in enumerate(v):
        t = a.start + i * 0.25
        if d > a.thresh:
            if regs and t - regs[-1][1] <= a.merge:
                regs[-1][1] = t + 0.25
            else:
                regs.append([t, t + 0.25])
    for s, e in regs:
        if e - s >= a.min:
            print(f"{s:7.2f} - {e:7.2f}  ({e - s:4.1f} s)")


if __name__ == "__main__":
    main()
