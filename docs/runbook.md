# Xử lý lỗi thường gặp
| Dấu hiệu | Cách xử lý |
|---|---|
| `align_srt.py` báo khớp dưới 90% | Audio đọc khác kịch bản. Đối chiếu các câu lệch, sửa storyboard, không ép |
| `channel.py` báo thiếu mục | Điền khối `lang` trong `channel.yaml`. Hệ thống không tự dùng ngôn ngữ khác thay thế |
| Chữ hiện ô vuông | Font chưa có. Thêm gói fontsource và import ở `compositions/LongForm.tsx` |
| Chữ đậm hơn mong muốn | Độ đậm chưa nạp sẽ nhảy lên mức trên. Chỉ dùng 400, 600, 800 |
| `gen_assets.py` lỗi 429 khi tải ảnh | Wikimedia giới hạn tải, chạy lại sau ít phút |
| `gen_assets.py` báo không đạt | Xem `qa/assets.json` và `missing_assets.md`, sửa prompt, chạy `--redo <id>` |
| `rig_auto.py` in FAIL | Dùng ảnh gốc với `motion`, ghi vào `status.yaml note` |
| `publish_clean.py`: Drive chưa nhận xong | Máy chưa xóa gì. Kiểm tra Drive Desktop, chạy lại |
| Thiếu tiến trình 9router | Mở lại dịch vụ, kiểm tra `router_url`. Việc chấm tự chuyển Codex CLI, không cần đổi cấu hình |
| Render in `Đang chờ: <tập> đang render` | Tập khác đang render, lần này tự chạy khi xong. Kẹt lâu: xem pid trong `.render.lock`, tiến trình đã tắt thì khóa tự gỡ |
| KingCong báo job xong nhưng `srt_url` rỗng (đã trừ credit) | Không gửi lại. Lấy `audio_path` của job, tạo srt theo câu bằng ghép quy hoạch động ranh giới câu vào khoảng lặng dài (bài học 80) |
| Render bản cuối báo `ENOSPC` (hết ổ) | Bản cuối ghi hết khung PNG trước khi mã hóa, tập 12 phút cần trên 150 GB. Render theo đoạn (mặc định 2400 khung, `--chunk-frames N`); đoạn giữ ở `render/chunks/`, lần sau chỉ render đoạn đổi (bài học 84) |
| `precheck.py` thoát mã 2 | Đã 4 vòng chưa qua cổng: dừng, báo Sếp kèm lỗi còn lại. Sếp trả lời xong xóa cờ `status.py <tập> can_sep=` |
| `produce.py` báo chạm trần render | Đã 1 lần đầu + 2 lần render lại. Báo Sếp; chỉ chạy `--sep` khi Sếp nói rõ |
| `validate_scenes` báo `[mã luật]` mà cảnh là cố ý | Approver xét rồi ghi `props.allow: {"mã luật": "lý do"}` vào cảnh đó |
| Đoạn render cũ còn sau khi sửa `render.mjs` hoặc component | Mã băm đoạn gồm mã nguồn component và cấu hình mã hóa, tự render lại. Muốn bỏ hẳn: xóa `render/chunks/` |
