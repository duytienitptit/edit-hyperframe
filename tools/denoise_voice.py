"""Denoised full-length copy of a video's sound (same clock as the source) for picture/sound-split edits.

Usage: python3 tools/denoise_voice.py <video> <out.wav> [--level B|C] [--ab out_dir START:DUR ...]
  B (default, approved on BaiThi1017/1018): highpass 90 Hz + RNNoise (tools/models/bd.rnnn) mix 0.8 — natural voice.
  C: highpass 100 Hz + RNNoise mix 1 + soft gate — cleaner, but kills table chatter/laughter.
  --ab writes A_goc / B_loc_vua / C_loc_manh .m4a listening samples of the given ranges (loudness-matched).
Latency vs source ≈ 10 ms (ignored). For removing music (not noise) use tools/separate_stems.py instead.
"""
import argparse, os, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "models", "bd.rnnn")  # github.com/richardpl/arnndn-models
FX = {"A": "anull",
      "B": f"highpass=f=90,arnndn=m={MODEL}:mix=0.8",
      "C": f"highpass=f=100,arnndn=m={MODEL}:mix=1,agate=threshold=0.02:ratio=2:range=0.25:attack=5:release=250"}
NAMES = {"A": "A_goc", "B": "B_loc_vua", "C": "C_loc_manh"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--level", default="B", choices=["B", "C"])
    ap.add_argument("--ab", nargs="+", metavar="ARG", help="out_dir then START:DUR ranges")
    a = ap.parse_args()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vn", "-ac", "2", "-ar", "48000", "-af", FX[a.level], a.out], check=True)
    print("wrote", a.out)
    if a.ab:
        out_dir, ranges = a.ab[0], a.ab[1:]
        os.makedirs(out_dir, exist_ok=True)
        tmp = tempfile.mkdtemp()
        for lv in "ABC":
            lst = os.path.join(tmp, lv + ".txt")
            with open(lst, "w") as f:
                for k, rg in enumerate(ranges):
                    s, d = map(float, rg.split(":"))
                    w = os.path.join(tmp, f"{lv}_{k}.wav")
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-t", str(d), "-i", a.video, "-vn", "-ac", "2", "-ar", "48000",
                                    "-af", f"{FX[lv]},afade=t=in:d=0.05,afade=t=out:st={d - 0.05}:d=0.05,apad=pad_dur=0.8", w], check=True)
                    f.write(f"file '{w}'\n")
            dst = os.path.join(out_dir, NAMES[lv] + ".m4a")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                            "-af", "loudnorm=I=-16:TP=-1.5,aresample=48000", "-c:a", "aac_at", "-b:a", "192k", dst], check=True)
            print("wrote", dst)


if __name__ == "__main__":
    main()
