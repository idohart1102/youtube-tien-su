# Lịch sử phiên bản
## 1.0.0 (2026-11-01)
Phiên bản đầu tiên hoàn chỉnh.
- Luồng tự động: 9router `cx/gpt-6.1-sol` QC, Codex CLI dự phòng. Claude (vai trò approver) duyệt brief, quyết định render lại, chốt bản cuối. Sếp gửi audio + srt và đăng YouTube.
- Tạo ảnh bằng 9router `cx/gpt-image-2.5-sunburst`, Codex CLI dự phòng, hạn chế ám vàng. Tự QC asset tối đa 5 lần.
- Cổng trong code: kiểm tra fact có tìm web, brief không đổi sau duyệt, QC đúng bản render, không lặp nhân vật theo lịch đăng.
- Tiêu chuẩn chung ở `core/standard/`, quy định ngôn ngữ và DNA kịch bản ở từng kênh.
- Phong cách sân khấu sống: Stage, FossilReveal, StrataWipe, rig nhân vật. Tiến độ ở `status.yaml`, lên Drive bằng `publish_clean.py`, học hỏi ở `knowledge/`.
- GitHub chỉ chứa hệ thống, không có media và dữ liệu tập.
