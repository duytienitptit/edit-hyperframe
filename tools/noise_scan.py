"""Speech vs ambience level per section, to decide whether/how hard to denoise.

Usage: python3 tools/noise_scan.py <media> <transcript.json> NAME:START:END [NAME:START:END ...]
Per section: median speech level, non-speech p50/p90 (100 ms RMS), rough SNR, and band balance of the
non-speech audio (0-150 / 150-500 / 500-2k / 2k-8k Hz, dB relative to the loudest band).
Reading it (BaiThi1017): outdoor sections had SNR ~12-14 dB with the lowest band dominant (wind/traffic
rumble) -> highpass 90 Hz + RNNoise; a meal section with SNR ~4 dB and mid-band dominant = chatter
(keep it soft under music, don't denoise it away).
"""
import json, subprocess, sys
import numpy as np

SR = 16000


def main():
    media, tr, secs = sys.argv[1], sys.argv[2], sys.argv[3:]
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", media, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                                     capture_output=True, check=True).stdout, np.int16).astype(np.float32) / 32768
    words = [w for s in json.load(open(tr, encoding="utf-8"))["segments"] for w in s.get("words", [])]
    speech = np.zeros(len(x) // (SR // 10) + 1, bool)
    for w in words:
        speech[int(w["start"] * 10):int(w["end"] * 10) + 1] = True
    db = lambda a: 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)
    for sec in secs:
        name, a, b = sec.split(":")
        a, b = float(a), float(b)
        fr = [(i / 10, db(x[int(i / 10 * SR):int((i + 1) / 10 * SR)])) for i in range(int(a * 10), int(b * 10))]
        sp = [v for t, v in fr if speech[int(t * 10)]]
        ns = [v for t, v in fr if not speech[int(t * 10)]]
        seg = np.concatenate([x[int(t * SR):int((t + 0.1) * SR)] for t, v in fr if not speech[int(t * 10)]] or [np.zeros(1600)])[:SR * 4]
        spec = np.abs(np.fft.rfft(seg))
        f = np.fft.rfftfreq(len(seg), 1 / SR)
        be = [10 * np.log10(np.sum(spec[(f >= lo) & (f < hi)] ** 2) + 1e-9) for lo, hi in [(0, 150), (150, 500), (500, 2000), (2000, 8000)]]
        sp_m = np.median(sp) if sp else float("nan")
        ns_m = np.median(ns) if ns else float("nan")
        print(f"{name:14s} speech {sp_m:6.1f} | non-speech p50 {ns_m:6.1f} p90 {np.percentile(ns, 90) if ns else float('nan'):6.1f} "
              f"| SNR~{sp_m - ns_m:5.1f} | bands " + " ".join(f"{v - max(be):5.1f}" for v in be))


if __name__ == "__main__":
    main()
