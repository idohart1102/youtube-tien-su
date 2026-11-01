---
name: produce
description: Chạy pipeline phụ đề, render cho một tập từ audio Sếp gửi. Chỉ chạy lệnh, không đọc source.
---
Chạy `python core/scripts/produce.py channels/<slug>/episodes/<tap>` để ra bản cuối (render/final.mp4) và kiểm tra máy. Audio do Sếp tạo ở ngoài hệ thống: tập chưa dựng cảnh thì dùng skill build-video, chưa có `audio/voice.*` và `.srt` thì báo Sếp. `--no-subs` để tắt phụ đề.
- Nếu lỗi: chỉ đọc 20 dòng cuối của log. Chỉ mở đúng script báo lỗi, không mở cả thư mục.
- Không in log dài ra cho người dùng. Báo kết quả gồm đường dẫn file mp4 và thời lượng.
