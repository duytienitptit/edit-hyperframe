"""Split a pre-mixed track into voice + music on the same clock as the source (CLAUDE.md rule 14).

Usage: tools/.venv/bin/python tools/separate_stems.py <video|audio> <out_dir> [--model FILE]
  Writes <out_dir>/<name>_voice.wav and <name>_music.wav (source sample rate, stereo, exact source length).
  Default model: BS-Roformer Viperx 1297 (vocals SDR 11.8 / instrumental 16.5), weights in tools/models/separator/.
  Other models: tools/.venv/bin/audio-separator --list_models --list_filter=vocals
Runs offline once the model is downloaded (first run fetches ~600 MB). Uses MPS on Apple Silicon.
"""
import argparse, json, os, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "models", "separator")
DEFAULT_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    return int(d["streams"][0]["sample_rate"]), float(d["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out_dir")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    a = ap.parse_args()
    from audio_separator.separator import Separator

    name = os.path.splitext(os.path.basename(a.src))[0]
    sr, dur = probe(a.src)
    os.makedirs(a.out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, name + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-vn", "-ac", "2", "-ar", str(sr), wav], check=True)

    sep = Separator(model_file_dir=MODEL_DIR, output_dir=tmp, output_format="WAV", sample_rate=sr)
    sep.load_model(model_filename=a.model)
    files = [f if os.path.isabs(f) else os.path.join(tmp, f) for f in sep.separate(wav)]

    for f in files:
        stem = "voice" if "(Vocals)" in f else "music"
        dst = os.path.join(a.out_dir, f"{name}_{stem}.wav")
        # pad/trim to the exact source length so the stem drops onto the video timeline unshifted
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-af", f"apad,atrim=0:{dur}", "-c:a", "pcm_s16le", dst], check=True)
        print("wrote", dst)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
