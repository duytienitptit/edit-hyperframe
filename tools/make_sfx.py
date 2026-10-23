"""Synthesize a small set of soft, royalty-free SFX locally (no downloads, no generation APIs).

Usage:
  tools/.venv/bin/python tools/make_sfx.py <out_dir>

Writes 48 kHz stereo 16-bit WAVs:
  whoosh.wav  0.9 s  airy band-passed noise sweep (scene / chapter transitions)
  chime.wav   1.6 s  soft bell, C6 + G6 partials (title / highlight landing)
  tick.wav    0.15 s gentle wooden tick (small label pop-in)
Peaks are kept at about -6 dBFS; set the final level in the composition (data-volume).
"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)  # deterministic


def write(path, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-6 / 20)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def whoosh(dur=0.9):
    n = int(SR * dur); t = np.arange(n) / SR
    noise = rng.standard_normal((n, 2))
    # one-pole lowpass whose cutoff sweeps up then down -> "air moving past"
    fc = 300 + 2600 * np.sin(np.pi * t / dur) ** 2
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(noise); prev = np.zeros(2)
    for i in range(n):
        prev = (1 - a[i]) * noise[i] + a[i] * prev
        y[i] = prev
    y -= np.concatenate([np.zeros((1, 2)), y[:-1]]) * 0.6  # tame the rumble
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.6
    pan = 0.5 + 0.35 * np.sin(np.pi * (t / dur - 0.5))  # slow left -> right drift
    y[:, 0] *= env * (1 - pan) * 2; y[:, 1] *= env * pan * 2
    return y


def chime(dur=1.6):
    n = int(SR * dur); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, amp, dec in [(1046.5, 1.0, 1.9), (1568.0, 0.55, 2.6), (2093.0, 0.25, 3.5), (3136.0, 0.08, 5.0)]:
        y += amp * np.sin(2 * np.pi * f * t) * np.exp(-dec * t)
    y *= np.minimum(1, t / 0.006)  # soft attack, no click
    st = np.stack([y, y], axis=1)
    for d, g in [(0.043, 0.25), (0.071, 0.18), (0.113, 0.12)]:  # tiny stereo room
        k = int(d * SR)
        st[k:, 0] += g * y[:-k]; st[k + 97:, 1] += g * y[:-k - 97]
    return st


def tick(dur=0.15):
    n = int(SR * dur); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 420
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * np.minimum(1, t / 0.002)
    return y


if __name__ == "__main__":
    out = sys.argv[1].rstrip("/")
    write(f"{out}/whoosh.wav", whoosh())
    write(f"{out}/chime.wav", chime())
    write(f"{out}/tick.wav", tick())
    print("wrote whoosh.wav chime.wav tick.wav to", out)
