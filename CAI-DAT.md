# Cài đặt EditHyperframe trên máy mới

Kho này là phần **dựng video**, dùng chung cho các kênh. Kho đi kèm: `channel-dad` (thư mục `Channel_Dad`). Hai thư mục phải nằm cạnh nhau trong `~/01_Projects/`, đúng tên `Channel_Dad` và `EditHyperframe`, vì các đường dẫn trong hướng dẫn dựa vào đó.

Cách nhanh nhất: mở Claude Code trong thư mục này và nói **"Cài đặt theo CAI-DAT.md"**. Claude làm lần lượt các bước dưới.

## Yêu cầu
- Mac chip Apple (M1 trở lên). Công cụ chép lời dùng MLX, chỉ chạy trên chip Apple.
- Homebrew, Claude Code, tài khoản GitHub đã được mời vào hai kho.

## Các bước
1. **Phần mềm nền** (Homebrew):
   ```bash
   brew install ffmpeg node python@3.12 gh
   ```
2. **Bộ dựng HyperFrames** (phiên bản ghi trong `package.json`):
   ```bash
   cd ~/01_Projects/EditHyperframe
   npm install
   npx hyperframes telemetry disable
   npx hyperframes doctor
   ```
3. **Công cụ Python** (chép lời, đo âm thanh, tách giọng):
   ```bash
   python3.12 -m venv tools/.venv
   tools/.venv/bin/pip install -r tools/requirements.txt
   tools/.venv/bin/python -c "import mlx_whisper, fontTools; print('ok')"
   ```
   Lần đầu chép lời, mô hình whisper tự tải về (khoảng 1,6 GB). Mô hình tách giọng cũng tự tải lần đầu dùng.
4. **Font cho kiểu dựng `bw-film-quote`** (font có sẵn của macOS, không đưa lên kho). Chép vào `comp/assets/fonts/` của dự án cần dựng lại, ví dụ DAD01:
   ```bash
   F=talking-head/projects/DAD01_LamChuDongTien/comp/assets/fonts; mkdir -p "$F"
   cp "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf" "$F/Georgia-BoldItalic.ttf"
   cp "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf" "$F/TimesNewRoman-BoldItalic.ttf"
   tools/.venv/bin/python -c "from fontTools.ttLib import TTCollection as C; [f.save('$F/AvenirNextCondensed-DemiBold.ttf') for f in C('/System/Library/Fonts/Avenir Next Condensed.ttc').fonts if f['name'].getDebugName(4)=='Avenir Next Condensed Demi Bold']"
   ```

## Không có trong kho
| Thứ | Lấy ở đâu |
|---|---|
| Clip gốc, video thành phẩm | Thư mục `Channel_Dad/assets/videos/` trên máy người làm clip, chia sẻ qua Google Drive khi cần |
| B-roll | Tự tải lại từ Pexels theo danh mục `library/broll/index.json` (ghi rõ mã clip và trang nguồn) |
| Nhạc nền, hiệu ứng âm thanh | Mỗi người tự xây thư viện trong `library/bg_music/`, `library/sfx/` |
| Bản render, ảnh duyệt, file màu đã nướng | Tạo lại khi dựng (`comp/prep_graded.py`, `npx hyperframes render`) |

## Làm việc hằng ngày
Claude tự làm: đầu buổi `git pull` cả hai kho; xong một việc thì commit và push kèm lời nhắn ngắn. Nếu hai người sửa cùng một chỗ và bị xung đột, Claude dừng lại hỏi.
