# Lịch sử phiên bản
## 2.0.0 (2026-11-13)
Nâng cấp sau 6 tập đầu tiensu-vn; chỗ tắc chuyển từ render sang fact và kịch bản.
- `qc_facts`: mã F cố định, cache theo dòng, chia lô 30 dòng; hướng dẫn nguồn trích nguyên văn trong plan-topics.
- `produce`/`render.mjs`: sửa nhỏ (≤25% đoạn) không tính trần render, tối đa 3 lần; `--max-new-ratio` dừng trước khi render nếu sửa quá lớn.
- `qc_video`: dùng lại kết quả bảng không đổi (`qa/qc_memo.json`), chấm 2 lượt khi điểm sát ngưỡng.
- Bản đồ: mẫu `sunda`, luật `ban-do-vung`, `ban-do-cham`, thêm 3 cảnh vào bộ mẫu lỗi.
- `gen_voice`: ước độ dài trước khi tốn credit; thiếu srt thì `tts align`.
- Orchestrator: 2-3 tập đi trước ở bước fact/kịch bản. Kho bài học bác 11 bài.

## 1.0.0 (2026-11-01)
Phiên bản đầu tiên hoàn chỉnh.
- Luồng tự động: 9router `cx/gpt-6.1-sol` QC, Codex CLI dự phòng. Claude (vai trò approver) duyệt brief, quyết định render lại, chốt bản cuối. Sếp gửi audio + srt và đăng YouTube.
- Tạo ảnh bằng 9router `cx/gpt-image-2.5-sunburst`, Codex CLI dự phòng, hạn chế ám vàng. Tự QC asset tối đa 5 lần.
- Cổng trong code: kiểm tra fact có tìm web, brief không đổi sau duyệt, QC đúng bản render, không lặp nhân vật theo lịch đăng.
- Tiêu chuẩn chung ở `core/standard/`, quy định ngôn ngữ và DNA kịch bản ở từng kênh.
- Phong cách sân khấu sống: Stage, FossilReveal, StrataWipe, rig nhân vật. Tiến độ ở `status.yaml`, lên Drive bằng `publish_clean.py`, học hỏi ở `knowledge/`.
- GitHub chỉ chứa hệ thống, không có media và dữ liệu tập.
