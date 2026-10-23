"""Transcribe a video/audio file to word-level JSON with mlx-whisper.

Usage:
  tools/.venv/bin/python tools/transcribe.py <input> <out.json> [--lang vi|zh|en|auto] [--start S] [--dur D]

Output JSON: {"language", "segments": [{"start","end","text","words":[{"word","start","end","prob"}]}]}
Times are in seconds relative to <input> (offset by --start if given).
"""
import argparse, json, os, subprocess, tempfile

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("out")
    p.add_argument("--lang", default="auto")
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--dur", type=float, default=None)
    a = p.parse_args()

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-i", a.input]
        if a.dur:
            cmd += ["-t", str(a.dur)]
        cmd += ["-vn", "-ac", "1", "-ar", "16000", wav]
        subprocess.run(cmd, check=True)
        r = mlx_whisper.transcribe(
            wav,
            path_or_hf_repo=MODEL,
            language=None if a.lang == "auto" else a.lang,
            word_timestamps=True,
            condition_on_previous_text=False,
        )

    off = a.start
    segs = []
    for s in r["segments"]:
        segs.append({
            "start": round(s["start"] + off, 3),
            "end": round(s["end"] + off, 3),
            "text": s["text"].strip(),
            "words": [
                {"word": w["word"].strip(), "start": round(w["start"] + off, 3),
                 "end": round(w["end"] + off, 3), "prob": round(w.get("probability", 0), 3)}
                for w in s.get("words", [])
            ],
        })
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"language": r.get("language"), "segments": segs}, f, ensure_ascii=False, indent=1)
    for s in segs:
        print(f"[{s['start']:7.2f} - {s['end']:7.2f}] {s['text']}")


if __name__ == "__main__":
    main()
