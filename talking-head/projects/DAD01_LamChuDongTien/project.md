# DAD01_LamChuDongTien — first talking-head test, style bw-film-quote

## Inputs (2026-10-21)
- `source/dad.mp4` → `~/01_Projects/Channel_Dad/assets/videos/goc/2026-10-21_lam-chu-dong-tien_goc.mp4` (moved from `~/Downloads/Dad.mp4` on 2026-10-23): 26.01 s, 1080×1920 HEVC 59.94 fps, 22 Mbps, −15.3 LUFS. Older man in a dark mandarin-collar jacket + bead necklace, armchair in a warm library. Medium shot 0–20.0 s, closer shot 20.0–26.0 s (only camera switch). Clean voice, no music (pauses near silent) → background music can be added freely.
- Style reference (NOT footage): `../../styles/refs/bw-film-quote_ref.mp4` (TikTok quote clip). User: "only to learn the editing style".

## Brief (user, 2026-10-21)
- Vertical 9:16, Vietnamese; captions, zoom, pause trimming, highlights, b-roll, SFX all wanted.
- Main job: fitting b-roll. User found the shot list too hard to source → Claude searches free stock sites (Pexels) itself and asks before downloading.

## Transcript (`analysis/transcript.json`)
1. 0.00–5.28 Con à, nghĩ lại xem, mình đang làm chủ đồng tiền hay vẫn bị đồng tiền làm chủ?
2. 5.80–8.92 Kiếm được nhiều tiền mà không dám nghỉ lấy một ngày.
3. 10.00–13.80 Đi chiếc xe cả tỉ mà tháng nào cũng mất ngủ vì lo tiền trả nợ.
4. 14.18–19.38 Muốn tiền làm việc cho mình, con phải hiểu nó được dùng vào đâu, lời từ đâu mà có.
5. 20.24–25.56 Chứ tiêu tiền chỉ vì thú vui, đam mê của bản thân, thì nhiều đâu cũng hết con ạ.
Pauses that could be trimmed: 8.92→10.00 (1.08 s), 19.38→20.24 (0.86 s).

## B-roll plan (`edit/broll.json`)
6 slots ≈ 13.9 s (53 %): B1 counting cash 2.84–5.50, B2 asleep at desk 6.94–10.00, B3a luxury car 10.00–11.82, B3b sleepless man on bed 11.82–14.00, B4 stock chart on phone 18.24–20.24 (also hides the camera switch), B5 shopping bags 20.24–22.42. Speaker on screen for the hook (0–2.84), 14.00–18.24 (the advice) and the conclusion (22.42–end).
Candidates: Pexels, main + alt per slot. All 12 downloaded 2026-10-21 (user approved, 229 MB) → `library/broll/<theme>/pexels_<id>.mp4`, indexed in `library/broll/index.json`; frame strips in `review/broll_board.jpg`, all match their slot.
Pexels served 720×1280 (not 1080) for 4 clips: B1 main 6266251, B4 main 7247871, B4 alt 7247861, B5 main 5836561 — acceptable under the B&W grain look; their sources exist in 4K if they look soft on the style frames.

## Music (`edit/music.json`)
User: "pick any". Chosen `tiktok_music_7348621740001545474` (instrumental — BS-Roformer vocal stem −70 LUFS; 69.6 BPM, dark/soft, 60 s), in 1.5 s (track silent before ~1.6 s), volume 0.18 ≈ −15 dB under the voice, fade in 0.6 / out 1.5. Preview mix (ffmpeg, not a render): `review/music_preview_v1.m4a` (first 14 s).

## Composition (built for style frames only, 2026-10-21)
- `comp/build.py` reads `edit/{captions,broll,style,music}.json` → `comp/index.html` (generated, never hand-edit). Speaker plays whole (no pause trims yet); b-roll = picture-only clips over it, symlinked from `library/broll/`.
- Look = HyperFrames `data-color-grading` on every video (canonical media treatment instead of CSS/canvas overlays): preset mono-clean, adjust contrast .3 / blacks −.25 / highlights −.1, vignette .85 (midpoint .34, roundness .3, feather .55), grain .4, effects.filmArtifacts .55 (dust + short scratches). Per-clip override `adjust` in broll.json: B3b exposure +.7 / shadows +.4 (was nearly black).
- Push-in: speaker +4 % per on-screen stretch, b-roll +6 % per slot (linear). Fade to black last 1.5 s.
- Captions: `edit/cues_vi.txt` (14 phrase cues, ≤ 34 chars) → align_captions → `edit/captions.json`; Georgia Bold Italic 50 px #F2D03B, 3 px dark stroke + shadow, y 62 %, hard cut in/out (ref style). Fonts copied from macOS (Georgia / Times New Roman Bold Italic); Vietnamese diacritics checked on 2× crops (`review/cap_zoom.png`).
- B3a in-point 0.0 (car large, caption sits on the dark roof — readable); in 3–5 put the roof edge right under the text.
- Storyboard v1: `review/storyboard_v1.jpg` (1.0 / 4.2 / 10.9 / 12.5 / 16.8 / 21.2 s, snapshots `review/sb1/`), font sheet `review/font_options_v1.jpg` (A Georgia vs B Times). Sent for approval — no demo render before OK.

## Storyboard v2 (2026-10-21)
- User on v1: font A (Georgia) OK; picture too dark — darken only the edges, the speaker's face must be clearly visible.
- Grade now: adjust exposure .18 / contrast .12 / shadows .3 / blacks −.05 / highlights −.12 (no more crushed blacks); vignette .9 with midpoint .62 + feather .42 (clear center, dark rim only). B3b override exposure .6 / shadows .45.
- `review/storyboard_v2.jpg` (snapshots `review/sb2/`), `review/compare_v1v2.jpg` (speaker at 1.0 / 16.8 s).

## Storyboard v3 (2026-10-21)
- User while v2 was being sent: "đừng chuyển qua màu đen trắng nữa" → full color. Grade: no preset; adjust exposure .06 / contrast .08 / shadows .15 / highlights −.08 / saturation −.12; vignette, grain, filmArtifacts unchanged from v2. B3b override exposure .5 / shadows .4.
- Yellow captions stay readable on every frame (dark stroke carries them over the warm library and the orange bedroom).
- `review/storyboard_v3.jpg` (snapshots `review/sb3/`). Style spec updated: color, not B&W.

## Storyboard v4 (2026-10-21)
- User on v3: swap the luxury-car b-roll for the driving POV clip; the dark rim looks rough; apply their safe-zone template (`edit/safe_zone_template.webp`) to grab attention; add text animations at the key moments with nice typography.
- Clarified (AskUserQuestion): video stays full-bleed, zones are a grid — face in the red zone / focus brackets, captions in the green band, text animations in the white box, nothing important in the black/UI areas. Highlights: the 4 proposed moments (③ split into XE CẢ TỈ / MẤT NGỦ because a picture cut sits between them → 5 lockups H1–H5).
- B3a = pexels_36632263 (POV, in 3.0). Vignette 0, grain .3, filmArtifacts .4.
- `edit/framing.json`: speaker scale 1.10 / y −157 (0–20 s) and 1.13 / y −250 (20 s+); Vision measures the rendered face at (543, 631) and (557, 598) — inside the focus box. Close shot face drifts to x ≈ 611 at 25 s (still inside).
- `edit/highlights.json` → lockups in the white box (see style spec "Keyword highlights"). QC: later lines hidden until their word (tl.set at clip start), Vietnamese caps marks verified on crops after raising the key line box to 1.4, shines at 2.99 / 7.79 / 10.79 / 12.57 / 24.87 all end before exits; H1's second key line has no shine (lands 0.4 s before the exit forced by the 5.5 cut).
- Captions in the green band (center y 995), hidden under highlights.
- `review/storyboard_v4.jpg` (snapshots `review/sb4/`, incl. mid-reveal 2.85 / shine 3.25), `review/safezone_check_v4.jpg` (template over frames).

## Demo v1 (2026-10-21) — user approved storyboard v4
- `output/th01_demo.mp4`: 26.05 s, 1080×1920, 30 fps draft, −13.9 LUFS, TP −1.9 dBFS (finish_audio from −14.75).
- First two renders were broken (all captions + highlights visible at once, no reframe, 7 min): B3a POV clip is HLG HDR (arib-std-b67/bt2020) → HDR layered-composite path. Fixed with `--sdr` (35 s render) + timeline registered synchronously (key sizes from fontTools in build.py; KHÔNG DÁM NGHỈ → 101.5 px). Found by bisecting 6 s / 12 s test renders and the `--debug` perf summary (hdrPerf.domLayerCaptures).
- H1 first line moved to at 2.99 so its motion starts exactly on the 2.84 cut (was 0.15 s early over the speaker).
- QC on the MP4: `review/qc/qc_demo_sheet.jpg` (12 frames), `review/qc/cut_check.png`; Vision face center (546, 632) at 1.0 s, (592, 676) at 24 s.

## Demo v2 — color (2026-10-21)
- User on demo v1: colors pale, make them richer / more eye-catching; "only the color left, then it's OK".
- Cause 1: v3 grade itself (saturation −.12, shadow lift). Cause 2: HyperFrames `data-color-grading` washes renders — same 1.0 s frame: source sat 149 / luma 56 → 2 s test render with grading 128.6 / 64.6 (with or without --sdr), without grading 147.5 / 58.2; full demo v1 105 / 64.
- Fix: look baked with ffmpeg (`edit/grade.json` → `comp/prep_graded.py` → `comp/assets/graded/`): vibrance .22, eq contrast 1.10 / saturation 1.12 / gamma .98, gentle S-curve, light temporal grain (noise 4). Per clip: B3a HLG → bt709 via colorspace (bt2020-10 approximation, checked visually), B3b gamma 1.35 / brightness +.04. B-roll excerpts = in − 1 s .. out + 1 s, keyframe every 30 frames (also clears the sparse-keyframe warnings). Film dust (filmArtifacts) dropped with the HF grading.
- `output/th01_demo_v2.mp4`: 26.05 s, −13.9 LUFS, TP −2.0 dBFS, render 26 s. Frame 1.0 s: sat 177 (graded file 181), face luma 120 (v1 128, source 127). Comparison `review/color_v1_vs_v2.jpg`.

## Tone options (2026-10-21)
- User: make 3 color tones to approve before the next demo. `edit/grade_options.json` → `review/tone_options_v1.jpg` (original + A/B/C on speaker, B1, B2, B3b, B5; stills only, no render).
- Speaker frame numbers: original sat 149 / R÷B 2.09 / face luma 118 · A warm gold (= demo v2) 181 / 3.98 / 114 · B teal & orange 200 / 2.67 / 116 (teal shadows, orange skin, contrast 1.16) · C bright clean 159 / 2.16 / 130 (colortemperature 9500 to pull the orange cast, brighter, vibrance .32).

## Demo v3 — tone C (2026-10-21)
- User picked tone C "Rực rỡ tươi sáng" → grade.json look, all clips re-baked (`prep_graded.py --force`).
- `output/th01_demo_v3.mp4`: 26.05 s, −13.9 LUFS, TP −2.0 dBFS, render 26 s. Render matches the baked file (frame 1.0 s: sat 170 vs 166, face luma 134 vs 137 — brightest face of all versions). QC sheet `review/qc/qc_demo_v3_sheet.jpg`.

## Final v1 (2026-10-21) — user approved demo v3
- `output/th01_v1.mp4`: 1080×1920, 60 fps, H.264 19.8 Mb/s, 26.03 s (1561 frames), −13.9 LUFS, LRA 1.8, TP −2.0 dBFS. Render: `--fps 60 --quality delivery --no-best-effort --sdr` (2 m 10 s), then finish_audio.
- QC on the MP4: `review/qc/qc_final_v1_sheet.jpg` (14 frames incl. H1 mid-reveal 2.80/2.90 and shine 3.25, H2 exit 9.75, fade 25.9), crops `review/qc/final_text_5s.png`, `review/qc/final_cap_16.8s.png` — Vietnamese marks correct, captions match `edit/cues_vi.txt`.
- `library/broll/index.json` used_in filled for the 6 clips placed.

## Channel handoff (2026-10-23)
- Project renamed TH01_LamChuDongTien → DAD01_LamChuDongTien (channel prefix rule in `../../CLAUDE.md`); references in `library/broll/index.json`, the style spec and `comp/.hyperframes/video-state.json` updated. Render file names `output/th01_*.mp4` kept as they were.
- Source moved out of Downloads into Channel_Dad (see Inputs).
- `output/th01_v1.mp4` copied to `Channel_Dad/assets/videos/2026-10-21_lam-chu-dong-tien_khuon1.mp4` and logged in Channel_Dad `so-tay-kenh.md` §9.

## Open items
- None requested. Not done by choice: pause trims, SFX (ask before adding). DAD01 is talking-head video 1 of the 2–3 needed before packaging a skill (ask the user first).
- Not done yet: pause trims (8.92→10.00, 19.38→20.24), SFX cue list (hook only, sparse), final 60 fps delivery render.
- After OK: decide pause trims (8.92→10.00, 19.38→20.24) → demo render (draft 30 fps) → SFX cue list (hook only, sparse).
