"""Bake the look from ../edit/grade.json into comp/assets/graded/ (speaker + every b-roll clip in broll.json).

Usage:  python3 comp/prep_graded.py [--force]

Only the used range of each b-roll clip is encoded (in-point − 1 s .. out + 1 s), so build.py shifts its media start by
the same amount. Output is SDR bt709 H.264 with a keyframe every 30 frames (seek-safe). Skips files that already exist
unless --force.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EDIT = os.path.join(HERE, "..", "edit")
LIB = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "library"))
OUT = os.path.join(HERE, "assets", "graded")
HANDLE = 1.0


def load(name):
    with open(os.path.join(EDIT, name), encoding="utf-8") as f:
        return json.load(f)


g, broll = load("grade.json"), load("broll.json")
os.makedirs(OUT, exist_ok=True)
force = "--force" in sys.argv


def bake(src, dst, start=None, dur=None, audio=False):
    if os.path.exists(dst) and not force:
        return
    chain = ",".join(x for x in (g["pre"].get(os.path.basename(src)), g["look"], g["grain"]) if x)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}", "-t", f"{dur:.3f}"]
    cmd += ["-i", src, "-vf", chain, *g["encode"]]
    cmd += ["-c:a", "aac", "-b:a", "256k"] if audio else ["-an"]
    subprocess.run(cmd + [dst], check=True)
    print("baked", os.path.basename(dst))


bake(os.path.join(HERE, "..", "source", "dad.mp4"), os.path.join(OUT, "dad.mp4"), audio=True)
for row in broll["timeline"]:
    if row["kind"] != "broll":
        continue
    src = os.path.join(LIB, os.path.relpath(row["file"], "library"))
    start = max(0.0, row["in"] - HANDLE)
    bake(src, os.path.join(OUT, f'{row["id"]}_{os.path.basename(src)}'), start, row["end"] - row["start"] + 2 * HANDLE)
