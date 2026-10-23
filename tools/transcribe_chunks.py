"""Chunked mlx-whisper transcription with a context prompt (fixes names / hallucinations in quiet parts).

Usage:
  tools/.venv/bin/python tools/transcribe_chunks.py <media> <out.json> --chunks 0:15,15:16,30:30 [--prompt "..."] [--lang vi]
  tools/.venv/bin/python tools/transcribe_chunks.py <media> <out.json> --every 25 [--start S --end E]

Why: one full-file pass hallucinated in long silences ("Hãy subscribe…", "Cảm ơn các bạn đã theo dõi") and
misheard proper names. Cutting the file into chunks that start in silences, giving an initial_prompt with the
names/terms, and disabling condition_on_previous_text fixes most of it.
Chunk starts should sit in silences (check with tools/quiet_points.py); a word cut by a chunk edge is
mis-timed (BaiThi1018: 'Khép' at 59.25 reported as 60.00 when a chunk began at 60).
Output: {"language", "segments":[{start,end,text,no_speech,words:[{word,start,end,p}]}]} in absolute seconds.
Still drops known hallucination strings; always eyeball the printed lines.
"""
import argparse, json, subprocess, tempfile
import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"
HALLUCINATIONS = ("subscribe", "Ghiền Mì Gõ", "Cảm ơn các bạn đã theo dõi", "hẹn gặp lại")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("out")
    ap.add_argument("--chunks", help="start:dur,start:dur,... (seconds)")
    ap.add_argument("--every", type=float, help="fixed window length when --chunks is not given")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float)
    ap.add_argument("--prompt", default="", help="names, places, theme words the speaker uses")
    ap.add_argument("--lang", default="vi")
    a = ap.parse_args()

    if a.chunks:
        chunks = [tuple(map(float, c.split(":"))) for c in a.chunks.split(",")]
    else:
        end = a.end or float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.media],
                                            capture_output=True, text=True).stdout)
        step = a.every or 25.0
        chunks, t = [], a.start
        while t < end - 0.5:
            chunks.append((t, min(step, end - t)))
            t += step

    segs = []
    for s, d in chunks:
        wav = tempfile.mktemp(suffix=".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-t", str(d), "-i", a.media, "-ac", "1", "-ar", "16000", wav], check=True)
        r = mlx_whisper.transcribe(wav, path_or_hf_repo=MODEL, language=a.lang, initial_prompt=a.prompt or None,
                                   word_timestamps=True, condition_on_previous_text=False,
                                   no_speech_threshold=0.5, compression_ratio_threshold=2.0)
        for seg in r["segments"]:
            text = seg["text"].strip()
            if not text or any(h.lower() in text.lower() for h in HALLUCINATIONS):
                continue
            words = [{"word": w["word"].strip(), "start": round(w["start"] + s, 2), "end": round(w["end"] + s, 2),
                      "p": round(w.get("probability", 0), 2)} for w in seg.get("words", [])]
            segs.append({"start": round(seg["start"] + s, 2), "end": round(seg["end"] + s, 2), "text": text,
                         "no_speech": round(seg.get("no_speech_prob", 0), 2), "words": words})
            print(f"[{seg['start'] + s:7.2f}-{seg['end'] + s:7.2f}] ns={seg.get('no_speech_prob', 0):.2f} {text}")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"language": a.lang, "segments": segs}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
