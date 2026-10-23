# Style: old-film quote (originally B&W, now full color)

Derived from reference `refs/bw-film-quote_ref.mp4` (TikTok quote clip, 23.4 s, 576×1024, 59.94 fps; style only, not footage). Frames: `refs/bw-film-quote_frames.jpg`, `refs/bw-film-quote_contact.jpg`.

## Look
- FULL COLOR, rich and punchy — never black & white (DAD01 v3), never pale (DAD01 demo v1 → v2). Look baked with ffmpeg before the comp; DAD01 user pick among 3 tones = C "bright clean" (`edit/grade.json`: colortemperature 9500 mix .8 to pull orange casts, vibrance .32, saturation 1.15, brightness +.04, gamma 1.08, soft curve, light grain). For a new video, show 3 tone options as stills first (`edit/grade_options.json` pattern), applied to speaker and every b-roll clip; per-clip fixes for dark or HDR clips.
- Moderate contrast, NO crushed blacks: the speaker's face must stay clearly lit (user, DAD01 v1 → v2). Darkness lives only in the vignette rim.
- Strong vignette on the rim only (HF grading: vignette ~.9, midpoint ~.62, feather ~.42): center fully clear, corners near black. Reference values: `projects/DAD01_LamChuDongTien/edit/style.json`.
- Old-film texture over everything: fine grain, sparse dust specks, occasional thin horizontal scratch line, very light flicker. Subtle — never hides the face.
- Slow push-in (≈ 3–6 % over a shot) on close-ups; static on wide shots.
- Ending: fade to black over the last ~1.5 s while the final line finishes.

## Captions
- Short phrase chunks (2–6 words), NOT one cue per sentence; e.g. "Đừng bao giờ hy vọng" / "Cuộc sống này hết bất công".
- Yellow (~#F2D03B), italic serif, semi-bold, small (cap height ≈ 2.5 % of frame height), thin dark outline + soft shadow, no box.
- Centered at ≈ 62 % of frame height (below the face, above the mic hand). 1 line always.
- Plain cut in / out, no animated reveal.
- Reference also has a small italic bold channel mark just above the caption — ours: only if the user gives a channel name.

## Pacing / shots
- Speaker on screen for the hook and for the conclusion.
- Reference: ~30 % cutaways (audience, guest reaction). Ours: illustrative b-roll for abstract ideas (injustice, pain, hardship, storms, kindness), ≈ 40–50 % of runtime, 2–4 s per shot, picture cuts aligned near sentence starts or on the key word.
- B-roll is graded identically (same correction + vignette + texture) so it melts into the speaker shots.

## Audio
- Voice upfront; soft emotional bed (piano / ambient, ~68–90 BPM) well under the voice.
- Reference source is pre-mixed (music bed audible in pauses at ≈ −20 dB mean) → separate stems before swapping music.
- SFX: very sparse (maybe a film-projector / soft whoosh at the first b-roll); no tension stings — the tone is reflective.

## Layout — safe zone (user template, DAD01 storyboard v4)
Template: `refs/safe_zone_9x16.webp` (1080×1920). Video stays full-bleed; the zones are an alignment grid, not a frame:
- red [95,335 → 985,920] = subject / main content; focus brackets [385,455 → 695,795] = where the speaker's face sits (reframe per camera setup with scale ≥ 1 + translate, measured with `tools/faces.swift`).
- green [95,925 → 985,1065] = captions (1 line, centered at y ≈ 995).
- white [93,1068 → 865,1512] = keyword text animations, left-aligned at x ≈ 110, max width ≈ 745 (clear of the TikTok button column).
- black (top 0–335, right column below 1068, bottom) = platform UI: nothing important there.
- No vignette (user: the dark rim looked rough).

## Keyword highlights (text animation)
- Lockup = small serif italic lead line (Georgia Bold Italic, cream #FFF4DC, ~54 px) + big condensed caps key line (Avenir Next Condensed Demi Bold — the only Avenir Condensed face with full Vietnamese — gold gradient #FFE9A3 → #F2C94C → #C98E1E, ~128 px, auto-shrunk to the white box).
- Each line rises out of a mask (yPercent 110 → 0, power3.out 0.55 s, key also scaleX 1.1 → 1), starting 0.15 s before its spoken word; one white shine pass 0.3 s after the key lands, only if it ends before the exit; exit = fade + drift up 0.3 s, done before the next picture cut.
- Captions hide while a highlight is on. Key line box needs line-height ≈ 1.4: background-clip text only paints inside the box and stacked marks (Ấ, Ể, Ủ) sit above the caps.
