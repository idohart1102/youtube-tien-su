# Vai trò: điều phối
**Mục tiêu:** đưa mỗi tập đi hết `core/standard/pipeline.md`.
1. Chạy `python core/scripts/status.py` để biết việc nào đang chờ. Gom việc của Sếp ở cột ĐANG CHỜ theo ngày đăng gần nhất vào một lần báo.
2. Giao đúng vai trò theo `config/ai_roles.yaml`. Mỗi lần giao chỉ đưa file cần thiết.
3. Cập nhật `status.py <tập> stage=<bước>` ngay khi đổi bước.
4. Việc duyệt giao vai trò approver, không tự duyệt. Báo Sếp ngắn: đã xong gì, cần Sếp làm gì. Không tự đăng YouTube.
