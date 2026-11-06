# Áp dụng chuẩn xuất YouTube

**Mục tiêu:** áp dụng chuẩn Sếp chốt cho mọi kênh, bắt đầu từ tập Denisova.
**Thiết kế:** `core/standard/video-output.md`.
**Cách làm:** sửa trực tiếp các tệp liên quan trong cây làm việc hiện có vì tập đang triển khai phụ thuộc nhiều thay đổi chưa commit; không ghi đè các thay đổi khác. Sếp đã yêu cầu áp dụng ngay.

- [x] Tạo cấu hình chung JSON và cấu hình render dùng nó; ảnh PNG, chuyển BT.709 thật, CRF18, H.264 High, GOP15 đóng, AAC48k stereo384k, MP4 faststart/no edit list. Kiểm tra cấu hình trên bản xuất thử thật.
- [x] Thêm kiểm tra tệp thật và báo cáo SHA-256: metadata, cấu trúc MP4, fps/thời lượng khung hình, GOP, giải mã đầy đủ hình–tiếng, mốc thời gian so với timeline. Không QC giọng/nhịp hoặc đổi âm lượng.
- [x] Chặn produce khi lỗi; chặn final và bàn giao khi báo cáo thiếu, lỗi, hoặc không khớp video/cấu hình/đầu vào hiện tại. Bàn giao thêm SRT và báo cáo.
- [x] Kiểm thử hồi quy: cấu hình sai, MP4 hỏng, báo cáo cũ cùng mtime, thiếu âm thanh, bản ngang/dọc; chạy bộ kiểm tra hệ thống. Ghi áp dụng trong ghi chú tập 1, giữ nguyên bước thực tế.

**Các trường hợp cần chú ý:** video ít chuyển động và audio im lặng không bị loại vì bitrate thấp; khung dọc không bị ép ngang; thiếu timeline không được coi là kiểm tra đủ; báo cáo cũ không vượt cổng nhờ đổi mtime; bản preview không có báo cáo đạt cho final.

## Xác minh
- `.venv/bin/python -m unittest discover -s core/tests -p test_video_output.py`: 13/13 đạt.
- `.venv/bin/python core/tests/run.py`: ĐẠT, có render Remotion thật 15 giây và render_check không lỗi.
- Đoạn thử trước đó 3,8 giây: render_check OK, xác nhận chuyển BT.709 thật, tỷ lệ điểm ảnh, MP4 và âm thanh đúng chuẩn.
- Review code độc lập: đã sửa hai điểm về hash audio nguồn và xác minh CRF/preset/bitrate mục tiêu trong lệnh mã hóa; bổ sung kiểm thử hồi quy.
- Tập Denisova chưa có scenes.json nên chưa render bản cuối; giữ nguyên bước và audio, thêm ghi chú áp dụng chuẩn từ tập 1.
