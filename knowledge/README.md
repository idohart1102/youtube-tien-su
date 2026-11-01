# Cơ chế học hỏi
Mọi điều hệ thống học được nằm trong repo, nên AI nào, máy nào cũng dùng được. Không để kiến thức chỉ nằm trong bộ nhớ riêng của một AI.

| Tầng | Nơi lưu | Nội dung | Ai đọc |
|---|---|---|---|
| Sự kiện | `knowledge/lessons.jsonl` | Từng bài học: phạm vi, mảng, luật, bằng chứng, trạng thái, số lần gặp | `learn.py brief` lọc đúng mảng |
| Kênh | `channels/<slug>/learnings.md` | Đang thắng, đang thua, thử tiếp. Tối đa 40 dòng, viết đè hằng tuần | writer, researcher |
| Tiêu chuẩn | `core/standard/` | Luật đã chứng minh | Mọi vai trò |
| Quyết định | `docs/decisions.md` | Quyết định của Sếp, có ngày | Mọi vai trò |

## Vòng học
1. **Trước khi làm:** `python core/scripts/learn.py brief --area <asset|motion|script|thumbnail|map|ops|stats> --channel <slug>`.
2. **Sau khi làm:** gặp lỗi mới hoặc cách hay thì `learn.py add --scope global|<slug> --area ... --rule "..." --evidence "..."`. Trùng nội dung sẽ tăng số lần gặp.
3. **Tự động:** `qc_video.py` ghi lỗi nặng thành bài học cấp kênh.
4. **Hằng tuần:** số liệu xác nhận hoặc bác bỏ: `learn.py mark <id> da-chung-minh|bi-bac --evidence "..."`. Trạng thái `bi-bac` không còn được đưa vào brief.
5. **Nâng cấp:** `learn.py review` liệt kê bài học đã chứng minh hoặc gặp từ 3 lần. AI đề xuất, **Sếp duyệt** rồi mới sửa `core/standard/`, ghi vào `CHANGELOG.md`.

Ghi một luật cụ thể làm được ngay, kèm bằng chứng. Không ghi nhận xét chung chung, không ghi bí mật.
