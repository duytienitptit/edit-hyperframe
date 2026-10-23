# Quy trình edit — EditHyperframe (dựng bằng HyperFrames)

Cùng quy trình với dự án EditRemotion (Remotion); chỉ khác công cụ dựng ở bước 5–6.

| # | Bước | Đầu ra | Ai duyệt |
|---|------|--------|----------|
| 0 | **Brief**: nền tảng, tỉ lệ, phong cách, màu/font, insight người xem, nguồn caption (file có sẵn / transcribe / cần dịch); **xin file riêng**: video thô, giọng đọc, nhạc | ghi vào `project.md` | Người dùng |
| 1 | **Setup** (đã xong 2026-10-14): ffmpeg, HyperFrames, mlx-whisper (dùng chung với EditRemotion) | — | — |
| 2 | **Phân tích**: ffprobe, contact sheet 1fps, mốc chuyển cảnh (`detect_scenes.py`), transcript từng từ | `analysis/` | — |
| 3 | **Caption text**: dùng file caption của người dùng (căn thời gian theo transcript) hoặc sửa transcript; nếu cần dịch → dịch theo từng câu, giữ mốc thời gian | `edit/captions.json` | Người dùng (nếu sửa/dịch) |
| 4 | **Chiến lược + cắt**: chọn đoạn, điểm cắt ở khoảng lặng, map shot ↔ lời đọc, chọn điểm nhấn | `edit/cut*.mp4`, `edit/highlights.json` | Người dùng |
| 5 | **Style frames**: 4–6 still tại điểm nhấn + preview ngắn (render demo 30fps, chất lượng draft) | `review/styleboard_vN.jpg` | **Người dùng duyệt phong cách** |
| 6 | **Dựng**: caption + chữ nhấn + hiệu ứng (grade, vignette, fade) | composition HyperFrames (`comp/`) | — |
| 7 | **Tự QC**: still giữa animation & quanh chuyển cảnh, thời lượng, loudness, chính tả | `review/qc_*` | — |
| 8 | **Bản vN → bản cuối**: chuẩn hóa âm −14 LUFS, export | `output/` + `project.md` | Người dùng |
| 9 | **Đóng gói skill** sau 2–3 video cùng dạng: template + quy tắc + ví dụ | `.claude/skills/<dạng>/SKILL.md` | Người dùng |

## Nguồn caption — 3 trường hợp
- **Có file caption** (SRT/text): căn câu chữ vào mốc thời gian từng từ của whisper (giữ đúng chính tả của file).
- **Không có file, cùng ngôn ngữ**: transcript whisper → sửa chính tả bằng `fixes.json` → người dùng duyệt.
- **Cần dịch** (vd. video tiếng Trung): whisper `--lang zh` → Claude dịch theo câu, giữ mốc thời gian của câu gốc → người dùng duyệt bản dịch.

## Âm thanh
- Ưu tiên file riêng (giọng đọc + nhạc) → chỉnh to/nhỏ nhạc theo điểm nhấn, ducking dưới lời đọc.
- Chỉ có bản trộn sẵn → mặc định giữ nguyên, chỉ chuẩn hóa loudness. Khi cần bỏ hoặc thay nhạc, cần giọng riêng: tách bằng `tools/separate_stems.py` (model BS-Roformer, chạy offline) → ra file giọng + file nhạc khớp thời gian với video. Bạn nghe thử file tách trước khi dựng tiếp.

## Hiệu ứng âm thanh (SFX)
Thư viện dùng chung cho mọi project: `library/sfx/` (danh mục đo sẵn `library/sfx/index.json`; thêm âm mới thì chạy lại `tools/.venv/bin/python tools/sfx_index.py`).
1. **Điểm nhấn ở mở đầu**: vài SFX ngắn ở khoảnh khắc quan trọng của những giây đầu; không chèn vào mọi chuyển động / mọi lần đổi hình.
2. **Chất âm gây chú ý**: mở đầu có thể dùng âm sắc, cao, hơi chói, hơi căng ("đinh", "keng", "rắc", âm hồi hộp) — hợp sắc thái nội dung, không biến video thành phim kinh dị.
3. **Chất âm ≠ âm lượng**: gây chú ý bằng đặc tính âm, SFX luôn nằm dưới giọng nói, không làm người nghe khó chịu.
4. **Mật độ âm căng thẳng**: có chọn lọc, có khoảng nghỉ; mốc tham khảo ~1 âm căng / 7 giây (không phải lịch cố định, không áp cho SFX thường). Không lặp liên tục âm sắc / giật mình.
5. **Đúng nhịp**: điểm nhấn của âm trùng lúc hành động xảy ra, chữ quan trọng xuất hiện, ý chính được nhấn.
6. **Cảm nhận hợp lý**: âm cách điệu được, miễn khớp nhịp và nghe hợp lý.
7. **Tiết chế**: mỗi âm phải có vai trò (thu hút / nhấn hành động / hỗ trợ nhịp dựng); không giúp thì bỏ; chừa khoảng trống.
Claude gửi danh sách SFX (mốc, âm, lý do) + bản nghe so sánh có/không SFX để người dùng duyệt.

## Màu (LUT) — Claude đề xuất & đo, người dùng chọn
1. Từ insight trong brief → hướng màu (vd. BĐS tâm linh, khách trung niên: ấm, vàng nhẹ, bão hòa vừa; video trẻ: tương phản, rực).
2. Loại LUT hỏng theo số đo: trời không cháy, lá không ngả ngọc, da không lệch màu (histogram/waveform ffmpeg).
3. Lưới so sánh: 3–4 frame tiêu biểu × 4–6 LUT → `review/lut_compare_vN.jpg` → người dùng chọn.
4. LUT đã chọn lưu theo mood để dùng lại . Tải LUT về phải hỏi trước.

## B-roll
- Người dùng cung cấp, hoặc Claude tự tìm trên kho video miễn phí (ưu tiên Pexels: miễn phí, không cần ghi nguồn): lập danh sách cảnh theo câu → mỗi cảnh 1 clip chính + 1 dự phòng → bạn duyệt danh sách tải (tên file, nguồn, dung lượng) → file vào `library/broll/<chủ đề>/` để video sau dùng lại.
- Chưa dùng video AI / API ngoài. Nếu sau này dùng: chỉ cho cảnh không khí, **không** dựng hình dự án thật.

## Xem & chỉnh
- `npx hyperframes preview` mở Studio trên trình duyệt để xem từng khoảnh khắc.
- Muốn sửa: ghi lại mốc thời gian + điều muốn đổi → Claude sửa dữ liệu JSON / composition.
