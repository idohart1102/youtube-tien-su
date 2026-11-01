---
name: review-stats
description: Mỗi tuần đọc số liệu các tập gần đây và viết lại learnings.md của kênh.
---
1. Đọc `stats.json` của 7 tập gần nhất (view 48h/7 ngày, CTR, thời gian xem trung bình, % giữ chân ở phút 1).
2. Viết lại TOÀN BỘ `learnings.md` trong ≤40 dòng, chia 3 mục: Đang thắng / Đang thua / Thử tiếp. Không nối thêm vào cuối.
3. Cộng điểm (+1 đến +3) trong backlog.csv cho đề tài cùng trụ cột hoặc cùng góc với tập thắng.
4. Ghi điều học được bằng `learn.py add`, cập nhật trạng thái bằng `learn.py mark`, xem `knowledge/README.md`. Mẫu số liệu: `core/templates/stats.example.json`.
5. Nếu một tập vượt trội rõ rệt (≥2 lần trung vị): thay 1 file trong script/examples/ bằng đoạn mở đầu 60 giây của tập đó.
