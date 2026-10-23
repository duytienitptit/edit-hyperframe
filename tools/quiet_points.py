"""Find the quietest instant (20 ms RMS) near candidate cut points, so audio cuts land in real silences.

Usage: python3 tools/quiet_points.py <media> <t1> [t2 ...] [--win 0.6] [--json]
Prints, per candidate: the minimum (dB, time) within ±win and a coarse profile (every 60 ms).
Rule of thumb from BaiThi1017/1018: a usable cut needs ≥ ~0.15 s below about −28 dB (phone audio);
ASR word boundaries alone are not enough (words often touch: '…khu vườn' / 'Mỗi cây' had no gap).
"""
import argparse, json, subprocess
import numpy as np

SR = 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("times", nargs="+", type=float)
    ap.add_argument("--win", type=float, default=0.6)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.media, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                                     capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
    hop = int(0.02 * SR)

    def db(t):
        seg = x[int(t * SR):int(t * SR) + hop]
        return float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)) if len(seg) else -120.0

    out = []
    for c in a.times:
        ts = np.arange(max(0, c - a.win), c + a.win, 0.02)
        v = [db(t) for t in ts]
        i = int(np.argmin(v))
        # longest run within 4 dB of the minimum around it = usable silence
        lo = hi = i
        while lo > 0 and v[lo - 1] < v[i] + 4:
            lo -= 1
        while hi < len(v) - 1 and v[hi + 1] < v[i] + 4:
            hi += 1
        out.append({"candidate": c, "min_t": round(float(ts[i]), 2), "min_db": round(v[i], 1),
                    "silence": [round(float(ts[lo]), 2), round(float(ts[hi]) + 0.02, 2)]})
        if not a.json:
            prof = " ".join(f"{t:.2f}:{d:.0f}" for t, d in zip(ts[::3], v[::3]))
            print(f"{c:7.2f}: min {v[i]:6.1f} dB at {ts[i]:.2f}  silence {ts[lo]:.2f}-{ts[hi] + 0.02:.2f} | {prof}")
    if a.json:
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
