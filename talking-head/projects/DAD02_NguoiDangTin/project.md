# DAD02_NguoiDangTin — first video in style podcast-card (draft style)

## Inputs (2026-10-29)
- Six Flow clips from the user's `~/Downloads/v1..v6.mp4`, moved to `~/01_Projects/Channel_Dad/assets/videos/goc/2026-10-29_nguoi-dang-tin_goc_01..06.mp4`; `source/c01..c06.mp4` link there. Each 720×1280 H.264 24 fps, sRGB transfer, AAC; c01 4.03 s, c02 6.04 s, c03–c06 10.03 s.
- Character `cha-bac-bo` (Channel_Dad `so-tay-kenh.md` §3): old Hanoi café podcast set, grey sweater vest, silver glasses. Two angles: camera B close-up facing the lens = c01, c03, c06; camera A medium wide at the table, 3/4 to the interviewer = c02, c04, c05. Contact sheet `analysis/contact.jpg`.
- Audio: clean dry voice, no music (floor −60 to −80 dB) → music bed free to add; −18 to −21 LUFS per clip.
- Channel rule: no end card (so-tay-kenh §8).
- Style: `../../styles/podcast-card.md` (DRAFT; reference `../../styles/refs/podcast_ref.mp4`).

## Transcript (`analysis/transcript_c0N.json`, clip-local times)
- c01 0.86–3.94 Một người, con không nên tin khi có ba điều sau. (whisper wrote "còn"; caption uses "con" — father speaking to his child)
- c02 0.00–5.58 Thứ nhất, hãy xem khi nghe chuyện riêng tư, họ có giữ mồm giữ miệng không?
- c03 0.42–5.34 Người đem bí mật người khác kể cho con, sớm muộn cũng đem chuyện con kể cho người khác. · 6.60–9.30 Với người như vậy, đừng tin.
- c04 0.00–4.24 Thứ hai, con hãy nhìn cách họ đối diện với khó khăn thế nào. · 5.20–8.74 Người đáng tin sẽ đứng ra gánh lấy trách nhiệm.
- c05 0.00–3.00 Còn kẻ giả dối sẽ tìm cớ đổ lỗi, thoái thác. · 3.42–6.04 Thứ ba, hãy xem cách họ giữ lời. · 6.86–9.14 Người đáng tin đã hứa thì sẽ làm.
- c06 0.00–4.42 Người đáng tin không nhiều, nhưng nhận ra sớm thì tránh được tai họa. · 5.34–8.82 Tin sai một lần, đôi khi phải trả giá cả đời.
- Speech onsets (RMS): c01 1.08, c02 0.54, c03 0.48, c04 0.48, c05 0.36, c06 0.36. Long pauses (trim candidates, to ≈ 0.3 s): c02 0.84–1.56, c03 5.34–6.60, c04 4.24–5.20, c05 6.04–6.86, c06 4.42–5.34. Dramatic pauses kept ≈ 0.5 s: c03 7.68–8.36 (before "đừng tin"), c06 6.52–7.26 (before "đôi khi").
- Estimated runtime after trims ≈ 40 s.

## Strategy draft (sent 2026-10-29, awaiting approval)
- Sections: hook (c01) → điều 1 (c02 + c03) → điều 2 (c04 + c05a) → điều 3 (c05b + c05c) → kết (c06). Clip order already alternates the two angles.
- "Thứ nhất / Thứ hai / Thứ ba" each on a color card (navy / grey / navy, ≈ 0.7 s) as chapter markers.
- Speaker on screen: hook, "Với người như vậy, đừng tin", each "Thứ …" sentence start after its card, closing line "Tin sai một lần… cả đời".
- B-roll ≈ 60 % (~ 9–10 slots, 1.5–2.5 s): whispering a secret · finger on lips · gossip behind someone's back · person facing a storm / pressure · carrying a heavy load · pointing a finger / blaming · turning away · firm handshake · lone figure in a crowd · near-miss / danger. Internal pause trims sit under b-roll so the jump cuts are hidden.
- Emphasis words (≈ 1 per sentence): ba điều, giữ mồm giữ miệng, đừng TIN, khó khăn, TRÁCH NHIỆM, đổ lỗi, giữ lời, hứa → làm, không nhiều, tai họa, CẢ ĐỜI. Lockups (2–3): "con không nên tin / BA ĐIỀU", "đã hứa / thì sẽ LÀM", "trả giá / CẢ ĐỜI".
- 720p source is upscaled ≈ 1.38× into the card (lanczos in the bake step); check sharpness on style frames.

## Decisions (user, 2026-10-29)
- Strategy above approved.
- Color cards for "Thứ nhất / Thứ hai / Thứ ba": yes, 3 cards.
- Hook blink after c01: yes, short (0.6–0.8 s), music lifts under it.
- Shared b-roll library reorganisation: apply before downloading DAD02 b-roll.

## Open items
- Font sheet (Inter vs Be Vietnam Pro) with the style frames; music pick (2–3 candidates); b-roll download list approval.
