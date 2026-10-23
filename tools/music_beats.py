"""Tempo + beat grid + energy curve for a music file (numpy/scipy only, no librosa).

Usage: python3 tools/music_beats.py <audio> <out.json> [--png out.png]
Output JSON: {duration, bpm, period, beats:[t...], downbeats:[t...], energy:[{t, rms_db}] (0.5 s hop), onsets:[{t, s}]}
Beat grid = constant tempo fit (autocorrelation of spectral-flux onset envelope, 60–180 BPM),
phase chosen to maximise onset energy on beats; downbeats = every 4th beat with the strongest phase.
"""
import argparse, json, subprocess
import numpy as np
from scipy.signal import stft, find_peaks

SR, HOP = 22050, 512

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)

def main():
    p = argparse.ArgumentParser(); p.add_argument("audio"); p.add_argument("out"); p.add_argument("--png")
    a = p.parse_args()
    y = load(a.audio); dur = len(y) / SR
    _, _, Z = stft(y, fs=SR, nperseg=2048, noverlap=2048 - HOP, boundary=None)
    mag = np.log1p(100 * np.abs(Z))
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode="same")
    env = np.maximum(flux, 0); env /= env.max() + 1e-9
    fps = SR / HOP
    # tempo by autocorrelation, weighted toward ~100 BPM
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lags = np.arange(len(ac)); bpms = 60 * fps / np.maximum(lags, 1)
    mask = (bpms >= 60) & (bpms <= 180)
    w = np.exp(-0.5 * (np.log2(bpms / 100) / 0.9) ** 2)
    score = np.where(mask, ac * w, 0)
    lag = int(np.argmax(score))
    # refine period with parabolic fit
    if 1 <= lag < len(score) - 1:
        y0, y1, y2 = score[lag - 1], score[lag], score[lag + 1]
        lagf = lag + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
    else:
        lagf = lag
    period = lagf / fps; bpm = 60 / period
    # dynamic-programming beat tracker (Ellis 2007): beats follow local onsets, tempo prior = period
    P = period * fps; N = len(env); alpha = 100.0
    score = env.copy(); back = np.full(N, -1)
    lo, hi = int(round(P / 2)), int(round(2 * P))
    for t in range(lo, N):
        prev = np.arange(max(0, t - hi), t - lo + 1)
        if len(prev) == 0: continue
        cand = score[prev] - alpha * np.log((t - prev) / P) ** 2
        k = int(np.argmax(cand)); score[t] = env[t] + cand[k]; back[t] = prev[k]
    tail = np.arange(max(0, N - int(P)), N); t = int(tail[np.argmax(score[tail])])
    path = []
    while t >= 0: path.append(t); t = back[t]
    beats = np.array(path[::-1]) / fps + (1024 + HOP) / SR  # STFT frame centre + diff lag
    bidx = np.clip((beats * fps).astype(int), 0, N - 1)
    bs = env[bidx]
    dphase = int(np.argmax([bs[k::4].mean() for k in range(4)]))
    downbeats = beats[dphase::4]
    # energy
    n = int(SR * 0.5); rms = [float(20 * np.log10(np.sqrt(np.mean(y[i:i + n] ** 2)) + 1e-9)) for i in range(0, len(y) - n, n)]
    pk, pr = find_peaks(env, height=0.25, distance=int(fps * 0.15))
    out = {"duration": round(dur, 3), "bpm": round(bpm, 2), "period": round(period, 4),
           "beats": [round(float(t), 3) for t in beats], "downbeats": [round(float(t), 3) for t in downbeats],
           "energy": [{"t": i * 0.5, "rms_db": round(r, 1)} for i, r in enumerate(rms)],
           "onsets": [{"t": round(float(i / fps), 3), "s": round(float(h), 2)} for i, h in zip(pk, pr["peak_heights"])]}
    json.dump(out, open(a.out, "w"), indent=0)
    print(f"{a.audio}: dur={dur:.1f}s bpm={bpm:.1f} beats={len(beats)} downbeat phase={dphase}")
    if a.png:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(22, 3.5))
        t = np.arange(len(rms)) * 0.5; ax.plot(t, rms, lw=1)
        for d in downbeats: ax.axvline(d, color="r", alpha=0.15, lw=0.6)
        ax.set_xticks(np.arange(0, dur, 10)); ax.grid(axis="x", alpha=0.4)
        ax.set_title(f"{a.audio}  bpm={bpm:.1f}  (red = downbeats)"); ax.set_ylabel("RMS dB"); ax.set_xlim(0, dur)
        fig.tight_layout(); fig.savefig(a.png, dpi=70)

if __name__ == "__main__":
    main()
