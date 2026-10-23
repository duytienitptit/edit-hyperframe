"""Integrated loudness / true peak per time range, and SFX-vs-mix level from an A/B pair.

Usage:
  python3 tools/section_loudness.py <media> START:DUR [START:DUR ...]          # LUFS + TP per range
  python3 tools/section_loudness.py --ab <with_sfx> <without_sfx> START:DUR ... # mix vs SFX-only RMS (difference signal)

Targets used on BaiThi1017/1018: speech sections ≈ −13…−15 LUFS after finish_audio; music-only gaps level with
speech (user: "nhạc to ở đoạn không lời"); SFX ≈ 9–15 dB under the mix (at gains 0.2 the opening hooks sat ~20 dB
under and were inaudible). Note zsh: pass ranges as START:DUR (no spaces), not "START DUR".
"""
import math, re, subprocess, sys


def lufs(media, s, d):
    r = subprocess.run(["ffmpeg", "-nostats", "-ss", str(s), "-t", str(d), "-i", media, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    tail = r[r.rfind("Summary"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    return (float(i.group(1)) if i else None), (float(tp.group(1)) if tp else None)


def pcm(media, s, d):
    import array
    return array.array("h", subprocess.run(["ffmpeg", "-v", "error", "-ss", str(s), "-t", str(d), "-i", media, "-ac", "1", "-ar", "16000",
                                            "-f", "s16le", "-"], capture_output=True).stdout)


def rms_db(xs):
    return 20 * math.log10(math.sqrt(sum(v * v for v in xs) / max(len(xs), 1)) / 32768 + 1e-9)


def main():
    args = sys.argv[1:]
    if args[0] == "--ab":
        a_path, b_path, ranges = args[1], args[2], args[3:]
        for rg in ranges:
            s, d = map(float, rg.split(":"))
            a, b = pcm(a_path, s, d), pcm(b_path, s, d)
            n = min(len(a), len(b))
            print(f"{s:7.2f}+{d:<5}: mix {rms_db(b[:n]):6.1f} dB   sfx-only {rms_db([a[k] - b[k] for k in range(n)]):6.1f} dB")
    else:
        media, ranges = args[0], args[1:]
        for rg in ranges:
            s, d = map(float, rg.split(":"))
            i, tp = lufs(media, s, d)
            print(f"{s:7.2f}+{d:<5}: I {i} LUFS   TP {tp} dBFS")


if __name__ == "__main__":
    main()
