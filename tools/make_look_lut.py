"""Build a 3D .cube LUT: Sony S-Log3/S-Gamut3.Cine -> Rec.709 (filmic tone map) + a parametric look.

Input of the LUT = RGB as ffmpeg's lut3d sees it (limited-range YUV expanded to 0..1),
so the 10-bit code value is CV = r*876 + 64.

Look parameters (JSON file or defaults):
  exposure     stops applied in scene-linear before tone mapping
  wb           [r,g,b] scene-linear white-balance gains (applied to the look only)
  tm_gain      scene-linear gain into the filmic curve (mid-gray placement)
  black        output lift/crush: out = (v - black) / (1 - black), clipped (positive = crush)
  contrast     S-curve strength around `pivot` in display space (0 = none)
  pivot        S-curve pivot
  gamma        display gamma tweak after contrast (>1 = darker mids)
  sat          global saturation multiplier (luma preserving, Rec.709 weights)
  shadow_tint  [r,g,b] added to shadows (weighted by (1-luma)^2)
  high_tint    [r,g,b] added to highlights (weighted by luma^2)
  white        output white clip (1.0 = none)

Usage:
  python3 tools/make_look_lut.py out.cube [--look look.json] [--size 65] [--technical]
  --technical ignores the look (pure S-Log3 -> 709 conversion).
The module also exposes `apply(rgb, look)` for numpy previews on stills.
"""
import argparse
import json

import numpy as np

# S-Gamut3.Cine -> Rec.709 primaries (linear, D65), from Sony's technical summary.
M = np.array([[1.6269474, -0.5401385, -0.0868089],
              [-0.1785155, 1.4179409, -0.2394254],
              [-0.0444361, -0.1959200, 1.2403561]])

DEFAULT = dict(exposure=0.0, wb=[1.0, 1.0, 1.0], tm_gain=0.6, black=0.0, contrast=0.0, pivot=0.4, gamma=1.0,
               sat=1.0, shadow_tint=[0, 0, 0], high_tint=[0, 0, 0], white=1.0)


def slog3_to_linear(v):
    cv = v * 876.0 + 64.0
    return np.where(cv >= 171.2102946929,
                    np.power(10.0, (cv - 420.0) / 261.5) * 0.19 - 0.01,
                    (cv - 95.0) * 0.01125 / (171.2102946929 - 95.0))


def filmic(x):
    # Narkowicz ACES fit: scene-linear -> display-linear, soft highlight roll-off.
    x = np.maximum(x, 0.0)
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0)


def luma(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def apply(rgb, look=None, technical=False):
    lk = dict(DEFAULT, **(look or {}))
    lin = slog3_to_linear(rgb) @ M.T
    if not technical:
        lin = lin * np.array(lk["wb"]) * (2.0 ** lk["exposure"])
    lin = lin * lk["tm_gain"]
    out = np.power(filmic(lin), 1 / 2.4)
    if technical:
        return np.clip(out, 0, 1)
    out = (out - lk["black"]) / (1.0 - lk["black"])
    out = np.clip(out, 0, 1)
    if lk["contrast"]:
        c, p = lk["contrast"], lk["pivot"]
        lo = p * np.power(np.clip(out / p, 0, 1), 1 + c)
        hi = 1 - (1 - p) * np.power(np.clip((1 - out) / (1 - p), 0, 1), 1 + c)
        out = np.where(out < p, lo, hi)
    out = np.power(np.clip(out, 0, 1), lk["gamma"])
    y = luma(out)[..., None]
    out = y + (out - y) * lk["sat"]
    out = out + np.array(lk["shadow_tint"]) * (1 - y) ** 2 + np.array(lk["high_tint"]) * y ** 2
    return np.clip(out / lk["white"], 0, 1)


def write_cube(path, size, look, technical):
    g = np.linspace(0, 1, size)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")  # red varies fastest
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = apply(rgb, look, technical)
    with open(path, "w") as f:
        f.write(f"TITLE \"{'SLog3 to 709' if technical else 'SLog3 look'}\"\nLUT_3D_SIZE {size}\n")
        for row in out:
            f.write(f"{row[0]:.6f} {row[1]:.6f} {row[2]:.6f}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--look")
    ap.add_argument("--size", type=int, default=65)
    ap.add_argument("--technical", action="store_true")
    a = ap.parse_args()
    write_cube(a.out, a.size, json.load(open(a.look)) if a.look else None, a.technical)
