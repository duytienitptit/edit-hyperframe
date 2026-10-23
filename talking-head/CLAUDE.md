# talking-head/ — vertical talking-head shorts (independent sub-project)

Scope: 9:16 Vietnamese talking-head / quote shorts. Several styles are being tested here; the best ones become a `/talking-head` skill after 2–3 finished videos (ask the user before packaging). Everything in the root `../CLAUDE.md` still applies (HyperFrames only, hard rules, SFX rules, language rules); this file adds talking-head specifics and wins on conflict.

## Layout
```
talking-head/
  CLAUDE.md                 this file
  styles/<style>.md         one spec per style (look, captions, pacing, b-roll ratio, audio)
  projects/<CHnn_Name>/     same structure as ../projects/<P>/ (source, analysis, edit, comp, review, output, project.md)
../library/broll/           shared b-roll library, grows with every video (see below)
../library/bg_music/        shared background music library (user-supplied) + index.json
../tools/                   shared scripts — call as ../../../tools/<x>.py from a project folder
```
Project names: `<CHANNEL><nn>_<Theme>` — channel prefix, running number per channel, short Vietnamese theme without diacritics. Prefixes: `DAD` = Channel_Dad (`DAD01_LamChuDongTien`, `DAD02_…`). Add a prefix for a new channel when its first video arrives (ask the user).

## Channel handoff
Each video belongs to a channel folder in `~/01_Projects/` (e.g. `Channel_Dad`), which owns the channel decisions (characters, voice, scripts, posting log). This folder owns only how videos are edited.
- Source clips live in the channel folder (`<channel>/assets/videos/goc/`), never in `~/Downloads`. `source/` symlinks point there. If the user hands over a file from Downloads, move it into the channel's `goc/` first (name `YYYY-MM-DD_<chu-de>_goc.mp4`), then link.
- After the final render passes QC, copy it to `<channel>/assets/videos/YYYY-MM-DD_<chu-de>_khuon<N>.mp4` and add a row to the video table in that channel's `so-tay-kenh.md`.
- Channel facts (character, voice) are read from the channel's `so-tay-kenh.md`, not copied here.

## Styles
| Style | File | First used |
|---|---|---|
| Old-film quote, full color + safe-zone layout + keyword lockups (file name kept from its B&W start) | `styles/bw-film-quote.md` (refs in `styles/refs/`) | DAD01_LamChuDongTien |

Every project states its style in `project.md`. A new style gets its own file; do not silently edit a style another project depends on.

## B-roll
- Claude finds the b-roll (user asked, 2026-10-21): plan slots in `edit/broll.json` (timeline: start, end, line, theme), search Pexels in the built-in browser (`/search/videos/<q>/?orientation=portrait`; the page's `__NEXT_DATA__` JSON gives id, title, duration, size and the 1080-wide `video_files` link), pick a main + alt per slot from the thumbnails (prefer hands / no faces or Asian subjects, no readable foreign text), then ask the user to approve the download list (file, source, MB) before fetching.
- Files arriving go to `../library/broll/<theme>/` (theme = short kebab-case idea, e.g. `dem-tien`, `mat-ngu`, `xe-sang`), never into the project, named `<source>_<id>.mp4`; each clip gets an entry in `../library/broll/index.json` (theme, idea, source page, duration, size, used_in). The comp symlinks them into `comp/assets/broll/`. Search the index before searching the web. Pexels' "hd_1080_1920" links sometimes deliver 720p — check with ffprobe after download. Also check `color_transfer`: some phone clips are HDR (HLG `arib-std-b67` / PQ, bt2020) — see Render.
- Specs (search or ask for): ≥ slot length + 1 s handle each side, no burned-in text / logos / watermarks, steady or slow motion, subject centered (16:9 gets center-cropped to 9:16). Color does not matter when the style grades it.
- Picture cuts to b-roll may fall mid-sentence (audio stays continuous); the hook (first ~1.5 s) and the closing line stay on the speaker's face unless the style says otherwise.

## Music
- Pick from `../library/bg_music/` by tempo/length in `index.json`, then let the user listen to 2–3 candidates before building.
- If the source audio already carries music (pre-mixed), separate stems first (root rule 14) and let the user hear the voice stem.

## Render
- Always `--sdr` (and `--no-best-effort`): one HLG b-roll clip (DAD01 B3a) switched HyperFrames to the HDR layered-composite path, which ignored clip visibility and timeline state (every caption + highlight on screen at once) and took 7 min instead of 35 s; best-effort mode still wrote the file. Snapshots looked fine, so QC the rendered MP4 itself.
- Do not use HyperFrames `data-color-grading` for the look: it lifted blacks and cut saturation in renders (DAD01 demo v1). Bake color with ffmpeg into `comp/assets/graded/` (see DAD01 `comp/prep_graded.py`), which also converts HDR clips and re-keys sparse-keyframe stock files.
- Register the GSAP timeline synchronously; measure text fits in build.py (fontTools) instead of `document.fonts.ready`.
- Demo: `npx hyperframes render -o ../output/<name>_demo_raw.mp4 --fps 30 --quality draft --workers 4 --no-best-effort --sdr`, then `tools/finish_audio.py`.
