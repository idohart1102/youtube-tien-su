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
