---
name: plan-topics
description: Chọn đề tài tiếp theo cho một kênh và viết brief.md. Dùng khi cần tập mới.
---
1. Đọc `channels/<slug>/backlog.csv` (chỉ các dòng status=todo) và `learnings.md`.
2. Đề tài phải hấp dẫn, không nhàm chán: có một câu hỏi khiến người xem muốn biết ngay, có sinh vật hoặc con người cụ thể, có tình huống căng và điều bất ngờ. Đề tài chỉ kể lại kiến thức sách giáo khoa thì bỏ, dù trụ cột đang thiếu. Chọn đề tài có score cao nhất. Không chọn trùng trụ cột với 2 tập gần nhất, trừ khi learnings.md nói trụ cột đó đang thắng.
3. Chạy `python core/scripts/new_episode.py <slug> <ten-ngan>` rồi điền đủ brief.md theo khung, không viết thừa.
4. Ghi nhân vật chính và ngày đăng dự kiến: `python core/scripts/status.py <tập> species=<tên> publish_date=YYYY-MM-DD`. Bị từ chối vì trùng nhân vật thì đổi đề tài.
5. Chạy `python core/scripts/qc_facts.py <tập>`, sửa bảng fact theo `qa/facts_vN.md`, tối đa 3 lần. Rồi giao vai trò approver duyệt brief. Hết 3 lần vẫn còn fact sai hoặc chưa xác minh thì báo Sếp.
6. Đổi status của đề tài trong backlog.csv thành `doing`.
Không chọn nhân vật chính đã có trong `no_repeat_species` video gần nhất (`species` trong status.yaml). Chỉ khi backlog còn dưới 10 dòng todo mới mở `channels/<slug>/research/` (cache) để bổ sung. Gọi vidIQ chỉ khi cache cũ hơn 30 ngày, kết quả lưu vào `channels/<slug>/research/` có ngày.
