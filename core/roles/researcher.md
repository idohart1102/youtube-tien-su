# Vai trò: nghiên cứu
**Đầu vào:** `channel.yaml`, `research/` của kênh, `learnings.md`. **Đầu ra:** `research/*.md` có ngày, dòng mới trong `backlog.csv`.
- Đọc cache trước. Chỉ gọi vidIQ khi cache cũ hơn 30 ngày, lưu lại kết quả.
- Mỗi đề tài ghi bằng chứng nhu cầu: video tham chiếu, view, mức vượt trội so với kênh đó.
- Đề tài thắng ở nước khác vẫn phải kiểm chứng ở thị trường của kênh.
- Không chọn nhân vật chính đã dùng trong `no_repeat_species` video gần nhất.
