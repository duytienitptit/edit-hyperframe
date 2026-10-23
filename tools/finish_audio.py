"""Two-pass loudness normalization of a rendered video (video stream is copied, not re-encoded).

Usage:
  python3 tools/finish_audio.py <in.mp4> <out.mp4> [--lufs -14] [--tp -1.5]
"""
import argparse, json, re, subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument("inp")
    p.add_argument("out")
    p.add_argument("--lufs", type=float, default=-14.0)
    p.add_argument("--tp", type=float, default=-1.5)
    a = p.parse_args()

    target = f"I={a.lufs}:TP={a.tp}:LRA=11"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.inp, "-af", f"loudnorm={target}:print_format=json",
                        "-vn", "-f", "null", "-"], capture_output=True, text=True, check=True)
    m = json.loads(re.findall(r"\{[^{}]+\}", r.stderr)[-1])
    # loudnorm silently falls back to dynamic mode when linear gain would break the TP target, and its
    # output can still overshoot after AAC encoding (+2 dBTP seen on BaiThi1017). So: plain linear gain,
    # then a 4x-oversampled peak limiter with 0.5 dB of headroom for the encode. Prefer AudioToolbox
    # AAC: ffmpeg's native aac overshot +2.7 dB on clipped phone audio, aac_at only ~+0.3 dB.
    gain = a.lufs - float(m["input_i"])
    lim = 10 ** ((a.tp - 0.5) / 20)
    encs = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    enc = "aac_at" if " aac_at " in encs else "aac"
    af = (f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={lim:.4f}:attack=1:release=60:level=false,"
          f"aresample=48000")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-c:v", "copy", "-af", af,
                    "-c:a", enc, "-b:a", "256k", "-movflags", "+faststart", a.out], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.out, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary"):]
    oi = re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1)
    otp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1)
    print(f"input: {m['input_i']} LUFS, TP {m['input_tp']} dB -> gain {gain:+.2f} dB -> output {oi} LUFS, TP {otp} dBFS")


if __name__ == "__main__":
    main()
