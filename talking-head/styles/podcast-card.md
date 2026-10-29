# Style: podcast card (DRAFT — first used on DAD02_NguoiDangTin, not yet a finished video)

Derived from reference `refs/podcast_ref.mp4` (TikTok podcast clip, 32.5 s, 576×1024, 30 fps; style only, not footage). Sheets: `refs/podcast_contact.jpg` (1 fps), `refs/podcast_contact_4fps.jpg`, `refs/podcast_frames.jpg` (full-res), `refs/podcast_lockup.jpg` (word build), `refs/podcast_intro_blink.jpg` (hook pause). Data: `refs/podcast_scenes.json`, `refs/podcast_transcript.json` (last line "Hãy subscribe…" is a whisper hallucination over the outro music).

Reference content: one guest at a podcast table (mic, coffee cup), two camera angles, cut against emotional cinematic b-roll. Its b-roll is Hollywood film footage — we do NOT copy that: b-roll comes from the shared library / Pexels only (root rule 15).

## Frame — rounded card on black
- Canvas 1080×1920, background pure black (#000).
- Every shot (speaker, b-roll, color cards) plays inside one fixed card: x 43–1037, y 398–1523 (994×1125, aspect ≈ 0.88, centered), corner radius ≈ 90 px. Media is cover-cropped into the card. The card never moves or resizes; only its content cuts.
- Card vs safe zone (`refs/safe_zone_9x16.webp`): card top/bottom sit inside the platform-safe band; the TikTok button column overlaps the card's lower-right (x > 865, y > 1068) → no text there.
- Bonus for b-roll: a 0.88 card crops 16:9 landscape to its middle 50 % width and 9:16 portrait to its middle 64 % height, so both orientations work (landscape Pexels pool is far larger than portrait).
- Optional channel mark: tiny white text at card bottom center (≈ 22 px, 60 % opacity), only if the user gives a channel name.

## Look
- No single unifying grade: each clip keeps a filmic look of its own (reference: warm natural speaker, teal, sepia, olive b-roll). Per clip, bake with ffmpeg (`comp/prep_graded.py` pattern): soft contrast, highlight roll-off, gentle desaturation toward the clip's dominant hue, light grain. Face always clearly lit.
- Show 2–3 tone options as stills before the first demo (as DAD01).
- No vignette, no film dust.

## Captions — word-by-word kinetic type (the core of the style)
- Font: bold geometric sans, tight tracking (reference ≈ SF Pro / Inter Display Bold). Candidates with full Vietnamese: Inter Bold/ExtraBold (installed), Be Vietnam Pro ExtraBold. Show a font sheet first.
- Plain white #FFF, no outline, no box, very soft drop shadow only for legibility on bright shots.
- Rhythm: 1–3 words on screen at a time, switched on word timings from the transcript (≈ 0.3–0.8 s per chunk). Words never repeat a chunk and never cover the face.
- Position: horizontally centered on the card, vertical center ≈ frame center (y ≈ 960); shift up to y ≈ 780 or down to y ≈ 1060 to sit on empty picture area. Always inside the card, left of x 865 when below y 1068.
- Size tiers (font size at 1080 wide): normal ≈ 60 px, emphasis ≈ 120–140 px, lead/tail ≈ 30–36 px.
- Default in/out: hard cut, no fade (root rule 8 holds naturally).
- One emphasis word per sentence at most — the word that carries the idea (reference: đổi thay, bình tĩnh, TỈNH TÁO, muốn, THAY ĐỔI, chút, được). Emphasis variants, mixed but not all in one video:
  - big size, quick pop-in (scale 1.12 → 1 + blur 8 → 0 px, 0.15 s, power3.out — never linear);
  - ALL CAPS for a command / turning point (TỈNH TÁO, THAY ĐỔI);
  - two-word split with the second word italic and dropped half a line (bình / *tĩnh*, THAY *ĐỔI*);
  - text behind the subject (depth matte — "muốn", "TỈNH"): 1–2 per video, only on clean single-subject b-roll; matte via `/embedded-captions` or `remove-background`.
- Lockup (≤ 2–3 per video, the video's key slogans): small lead stacked above-right of the key word ("chỉ có sự" / **đổi thay**; "tồn tại" / **muốn**; "chuyện gì" / **được**), then the tail appended word by word underneath in small size ("là không bao giờ thay đổi"). Lockup may take a tint from the scene (cream on warm shot via soft blend) instead of pure white. Lockup = highlight (root rules 5, 10): lands on the spoken word, gone before the shot change.
- Rare color word with a left-to-right letter wipe (reference: "bình thường" in pale violet): max 1 per video.
- Root rule 7 still holds: every line is 1 line; lockups are stacked lines, each ≤ 1 line.

## Pacing / shots
- Hook: the speaker's first sentence on camera with captions (reference 0–1.8 s).
- Hook pause "blink" (reference 1.8–4.6 s, music only): the speaker card flickers on/off with black frames (irregular, 2–4 frames each). Ours: kept, short (0.6–0.8 s) right after the hook sentence, music lifts under it (user, DAD02).
- Cuts every 1–2.5 s (reference: 17 cuts in 30 s). B-roll + color cards ≈ 60–65 % of runtime; speaker returns every 2–3 sentences and for the closing line.
- Use every camera angle the source has (reference: medium close + wide side angle). With one angle, alternate framing (scale 1.0 / 1.18 punch-in) on speaker returns.
- B-roll: cinematic, one person, emotion-led (lone figure at the sea, eyes closed in sunlight, walking away, head in hands, crowd), matching the spoken word or its feeling. Faces are fine in this style (unlike bw-film-quote); slow or still camera. One b-roll shot may hold across 2–3 caption chunks.
- Color cards (0.5–1 s, on a pause word): navy #062245 with a white word ("duy nhất"), or light grey #E0E0E0 with a navy italic word ("nếu"). 1–2 per video as breaths; for list scripts ("Thứ nhất / Thứ hai / Thứ ba") one card per item as a chapter marker, alternating navy / grey (user, DAD02).
- Hard cuts only, no dissolves.
- End: logo end card on navy #062245 (≈ 2 s) only if the user gives a logo; otherwise end on the speaker's last line.

## Audio
- Voice upfront; cinematic bed (piano / strings, emotional) under it — reference bed ≈ −24 LUFS in the gaps vs voice ≈ −18 LUFS. Ours: final −14 LUFS, bed ≈ −14 to −18 dB under dialogue peaks, rises a little during the hook pause.
- SFX (not measured on the reference — to be proposed): soft whoosh / tick on color cards and lockups, a low hit on the first emphasis; no horror stings.

## Open questions for the user (before the first video)
- Font (Inter vs Be Vietnam Pro) — font sheet with the first style frames. Channel_Dad uses no end card.
- Source: one podcast clip of the channel (preferably raw video + separate audio; more than one camera angle if it exists).
