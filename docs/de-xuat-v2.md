# Đề xuất bản 2.0 (2026-11-13)
Sếp duyệt ngày 2026-11-13: làm theo thứ tự đề xuất, chỉ nâng cấp hệ thống, không sửa lại video đã làm.
Nguồn: hồ sơ QA 10 tập tiensu-vn, 107 bài học trong `knowledge/lessons.jsonl`, `docs/decisions.md`.

## Số liệu 6 tập đầu
| Tập | Vòng kịch bản | Vòng fact | Precheck | Render | Điểm QC video |
|---|---|---|---|---|---|
| Denisova | 7 | 3 | 14 | 4 | 8,4 → 8,5 → 8,5 → 9,7 |
| Khủng long | 5 | 4 | ~20 | 5 | 9,0 → 9,5 → 8,5 → 8,5 |
| Indonesia | 8 | 7 | 6 | 4 | 8,4 → 8,5 → 8,5 |
| Người liệt | 5 | 3 | 4 | 3 | 8,5 → 9,1 |
| Đồng Văn | 5 | 4 | 5 | 3 | 9,1 → 8,5 → 9,6 |
| Thiên thạch | 5 | 10 | – | – | – |

Dựng đã nhanh hơn; chỗ tắc chuyển sang fact và kịch bản. Điểm QC dao động khoảng 1 điểm. Chưa có số liệu khán giả.

## Tình trạng
| Mã | Việc | Tình trạng |
|---|---|---|
| V2-09 | Commit việc đang dở | Xong (commit trên máy; push/PR chờ Sếp cho phép) |
| V2-01 | Fact: mã cố định, kiểm lại dòng đã sửa, lô 30 dòng, nguồn trích nguyên văn | Xong |
| V2-07 | Số liệu khán giả, viết lại learnings.md | Chờ Sếp: vidIQ chưa kết nối kênh |
| V2-03 | Sửa nhỏ không tính trần render | Xong |
| V2-04 | QC dùng lại bảng không đổi, chấm 2 lượt khi sát ngưỡng | Xong |
| V2-06 | Bản đồ mẫu sunda, luật cảnh báo bản đồ | Xong; ảnh thềm Sunda thật làm khi có tập cần |
| V2-05 | Dọn kho bài học | Xong: bác 11 bài, thêm luật bản đồ vào visual.md |
| V2-02 | 2-3 tập đi trước | Xong (orchestrator.md) |
| V2-08 | Whisper khi thiếu srt, ước độ dài trước khi tạo giọng | Xong |
