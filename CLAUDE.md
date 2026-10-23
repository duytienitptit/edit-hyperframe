# EditHyperframe — video editing with Claude Code + HyperFrames

Goal: edit many kinds of video; each kind becomes one skill, packaged only after 2–3 real videos of that kind are finished. Step-by-step process (Vietnamese, for the user): [WORKFLOW.md](WORKFLOW.md).

Sibling project `../EditRemotion` does the same job with Remotion (LHV video). Do not mix the two: this project renders with HyperFrames only.

## Language
- Files Claude reads (this file, `project.md` logs, skills, code comments, JSON `_note`) → **English**.
- Docs the user reads (WORKFLOW.md, guides, reports) → **Vietnamese**. Chat replies → Vietnamese.
- On-screen text (captions, highlights) stays in the video's language.

## Stack
- HyperFrames 0.8.155, installed locally (`node_modules`, run via `npx hyperframes`). Compositions are HTML + CSS + GSAP; timing via `data-start` / `data-duration` / `data-track-index`; GSAP timeline registered on `window.__timelines`.
- Skills: 21 HyperFrames skills in `.claude/skills/` (project-only; NOT the global plugin, NOT the claude.ai connector). Entry point `/hyperframes`; footage + narration usually routes to `/general-video`.
- FFmpeg (Homebrew, no drawtext/libass → all text is built in HyperFrames).
- mlx-whisper (large-v3-turbo) via `tools/.venv` (on the original machine a symlink to `../EditRemotion/tools/.venv`; elsewhere a venv built from `tools/requirements.txt`, see CAI-DAT.md) → word-level transcripts. Prefer it over HyperFrames' whisper-cpp path (not installed).
- Python tools in `tools/` (copied from EditRemotion; a fix here may need copying back): `transcribe.py`, `align_captions.py`, `build_captions.py` (draft only), `finish_audio.py` (−14 LUFS), `detect_scenes.py` (scdet sampled at 4fps → hard cuts and dissolves).
- Analysis tools (EditHyperframe only): `transcribe_chunks.py` (chunked whisper + context prompt; use when a full pass hallucinates in silences), `quiet_points.py` (20 ms RMS silence finder for audio cut points), `noise_scan.py` (speech vs ambience SNR per section), `denoise_voice.py` (highpass + RNNoise `tools/models/bd.rnnn` → same-clock clean voice track, A/B samples), `voice_activity.py` (finds real lines inside "chatter" sections), `section_loudness.py` (LUFS/TP per range; `--ab` = SFX level vs mix), `music_beats.py` (tempo / beat grid for bar-aligned music edits), `separate_stems.py` (voice vs music from a pre-mixed track; model in `tools/models/separator/`), `make_look_lut.py` (Sony S-Log3/S-Gamut3.Cine → Rec.709 + parametric look → .cube; bake with ffmpeg `lut3d` on the 10-bit source — HyperFrames' own grading is Rec.709-only and Chrome cannot decode 10-bit 4:2:2 camera files).
- Telemetry disabled (`npx hyperframes telemetry status`). When scaffolding, set `HYPERFRAMES_SKIP_SKILLS=1` so `init` does not touch global skills.

## Layout
```
tools/                     shared scripts
library/sfx/               shared SFX library (user-supplied) + index.json
.claude/skills/            HyperFrames skills (project-local)
projects/<PROJECT>/
  source/                  symlinks to the original files (never copy)
  analysis/                transcript, contact sheet, scenes.json
  edit/                    cues_*.txt (1 line = 1 caption), captions.json, highlights.json, … (all edit data)
  comp/                    HyperFrames composition (index.html, compositions/, assets/) — reads data from ../edit
  review/                  style frames, QC stills
  output/                  renders vN
  project.md               session log (read first when resuming)
talking-head/              independent sub-project for vertical talking-head shorts: own CLAUDE.md, styles/, projects/
library/broll/<theme>/     shared b-roll library (user-supplied, grows per video)
library/bg_music/          shared background music library + index.json
```
Scaffold a comp: `cd projects/<P> && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init comp --example=blank --non-interactive --skip-transcribe` (it writes its own CLAUDE.md/AGENTS.md; this file's rules win on conflict).

## Hard rules
1. The user approves strategy + style frames BEFORE a full render.
2. Never cut mid-word: cut points sit in silences between sentences (from the transcript), 30 ms audio fade at each cut.
3. All edit data (captions, highlights, EDL) lives in JSON under `projects/<P>/edit/`; the composition only reads it (e.g. `--variables-file` or a loader script). No hard-coded copy in HTML.
4. Fonts must support Vietnamese (`subset=vietnamese`). Check diacritics on a still before rendering.
5. Highlight text: reveal with cubic-ish easing (never linear), line by line, landing exactly when the keyword is spoken, gone before the shot change (use `analysis/scenes.json`).
6. Self-QC before sending: stills at each highlight + mid-animation, ffprobe duration, ebur128 (target −14 LUFS, true peak ≤ −1 dB), spelling.
7. Captions are always **1 line** (≤ 52 chars/cue; shrink font if long). Break cues at natural phrase boundaries, never split compound words (e.g. not "dự án khu / du lịch").
8. Two cues closer than 0.5 s switch instantly, no cross-fade (avoids overlapping text).
9. Gold shine: separate layer over a static gold fill, runs once right after the text lands, finishes before the text exits.
10. Use highlights sparingly: only for ideas that truly need emphasis (numbers, key slogans); leave many shots empty so viewers can enjoy the footage.
11. Map shots with colored regions → label each region (swatch = region color), shown when the region is colored / named, hidden before the shot change. If a region is unclear, ask the user — never guess silently.
12. Join segments by re-cutting seamlessly from the source (0 → new cut point), never by concatenating renders.
13. After each render, update `project.md` (decisions, reasons, open items).
14. Audio: ask for separate files (raw video, voiceover, music) first. With only a pre-mixed track, stem separation is allowed: `tools/separate_stems.py` (audio-separator + BS-Roformer) → vocals + music on the same clock. Use it only when the edit needs the voice or music on its own (replace/remove music, duck differently); otherwise keep the mix and only normalize. Have the user listen to the separated stems before building on them. Demucs is not installed.
15. B-roll: the user supplies it, or Claude finds it on free stock sites (Pexels first: free license, no attribution) — shot list (line + time range + reason) → main + alt candidate per slot → user approves the download list (file, source, size) → files land in `library/broll/<theme>/`. No AI-generated video / external generation APIs yet.
16. Color (LUT): follow the LUT section in WORKFLOW.md — Claude proposes and measures, the user chooses. Ask before downloading any LUT.
17. SFX: follow "Sound design (SFX)" below; pick from the shared library, never synthesize when the library has a fitting sound.

## Sound design (SFX)
Library: `library/sfx/` (user-supplied, shared by every project; ~1300 sounds: Mister Horse Free SFX by type, QUẠ BASIC memes/cartoon, Anime SFX gags, SFX NHẬT BẢN UI/title stings, SUSPEND ALERT tension/horror/risers). `library/sfx/index.json` (from `tools/sfx_index.py`) gives per sound: duration, peak, hit time (loudest instant — align it to the picture event, i.e. clip start = event − hit), effective length, brightness (centroid Hz, >4 kHz share) and tags (bright/dark/transient/riser/long). Re-run the indexer after adding sounds. In a comp, symlink the chosen files into `comp/assets/sfx/` and list each cue (time, file, gain, reason) in `edit/sfx.json`.
1. Hook the opening: a few short accents at the key moments of the first seconds (title, first key word, first reveal). Never one per movement or per shot change.
2. Opening timbre may be sharp / high / slightly piercing / lightly tense (metallic "ding"/"clang", "crack", horror-style sting) — matched to the content's tone; do not turn every video into horror.
3. Attention comes from timbre, not level: keep SFX under the voice (typically −10 to −18 dB below dialogue peaks), never startle by volume.
4. Tension sounds are rationed with rests: roughly one tense SFX per ~7 s as a reference ceiling (not a schedule, not a limit for ordinary SFX). No repeated sharp/startling hits back to back.
5. Sync: the sound's hit lands on the moment that needs attention (action, key text landing, key idea spoken) — chosen by edit rhythm and meaning, never just because a sound exists.
6. Stylized beats literal: a sound only has to feel right and sit on the motion.
7. Restraint: every sound must have a job (grab attention, sell an action, support the cut rhythm); if not, drop it. Leave gaps so the important hits land.
Outcome: clear sonic hook in the opening; SFX in sync and serving content; tension sounds just enough; overall never dense, repetitive or tiring. Present the cue list (and an A/B: without vs with) for approval like any style change.

## Common commands
```bash
tools/.venv/bin/python tools/transcribe.py <video> <out.json> --lang vi [--start S --dur D]
tools/.venv/bin/python tools/align_captions.py <cues.txt> <transcript.json> <captions.json> --end <s>
python3 tools/detect_scenes.py <video> analysis/scenes.json   # t = middle of change, dissolves ±0.5 s
python3 tools/finish_audio.py <render_raw.mp4> <final.mp4>     # −14 LUFS, TP −1.5
cd projects/<P>/comp && npx hyperframes preview                # Studio in the browser
cd projects/<P>/comp && npx hyperframes lint
# demo (style/pacing check, light on the machine)
cd projects/<P>/comp && npx hyperframes render -o ../output/<name>_demo.mp4 --fps 30 --quality draft --workers 4 --gpu
# final
cd projects/<P>/comp && npx hyperframes render -o ../output/<name>_vN.mp4 --fps 60 --quality delivery
npx hyperframes doctor
```

## Shared repo (GitHub, two people)
This folder is the private GitHub repo `edit-hyperframe`, shared by two people; its sibling `../Channel_Dad` is `channel-dad`. New machine → `CAI-DAT.md`.
- Start of a session: `git pull` here and in the channel repo. After each finished piece of work (a style decision, a project.md update, edit data): commit with a short message and push.
- Only text is versioned: media, renders, review stills, `comp/assets/`, libraries (except their `index.json`) and `projects/` (personal test projects) are git-ignored. Rebuild generated files instead of committing them.
- On a merge conflict, stop and show the user both versions; never overwrite the other person's change.
