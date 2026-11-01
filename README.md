# 1. niche tiền sử
Hệ thống sản xuất video storytelling minh họa cho nhiều kênh, mỗi kênh một ngôn ngữ. Phiên bản xem ở `VERSION`, thay đổi ở `CHANGELOG.md`.

**Mọi lệnh `python` dùng Python của `.venv`.** **Người mới bắt đầu:** `docs/handover.md` (cài đặt, dịch vụ, nhận việc) → `core/standard/pipeline.md` (luồng làm việc) → `docs/decisions.md` (quyết định phải tuân theo).
**AI:** Claude Code đọc `CLAUDE.md`, Codex và AI khác đọc `AGENTS.md`. Phân công ở `config/ai_roles.yaml`, hướng dẫn vai trò ở `core/roles/`.

## Cấu trúc
```
docs/              bàn giao, quyết định, xử lý lỗi
config/            ai_roles.yaml (phân công), machine.example.yaml (cấu hình máy)
knowledge/         bài học tích lũy
assets/shared/     asset dùng chung, không vào git: kết cấu do doctor.py tự sinh, nhạc và tiếng động tự đặt
core/standard/     tiêu chuẩn chung, đúng với mọi ngôn ngữ
core/roles/        hướng dẫn từng vai trò AI
core/skills/       quy trình từng bước
core/scripts/      lệnh chạy
core/lang_tools/   công cụ xử lý chữ theo ngôn ngữ
core/remotion/     dựng hình
core/tests/        kiểm tra tự động: python core/tests/run.py
channels/<slug>/   mọi thứ riêng của kênh
  channel.yaml, theme.json, thumbnail.md, script/, research/, backlog.csv, learnings.md
  episodes/<ngày_tên>/  status.yaml, brief.md, storyboard.md, script.md, meta.md, scenes.json, timeline.json, credits.json, qa/
                        audio/ render/ thumb/ assets/  (không vào git, cả thư mục tập chỉ ở trên máy, thành phẩm lên Drive)
```

## Mở kênh, ngôn ngữ mới
`python core/scripts/new_channel.py <slug> --lang <mã>` hoặc thêm `--from <kênh cùng ngôn ngữ>`, điền khối `lang` trong `channel.yaml`, chạy `python core/scripts/channel.py <slug>`. Ngôn ngữ có chữ ngoài Latin, tiếng Việt, tiếng Nhật cần thêm font (xem `docs/runbook.md`). Tối đa 5 ngôn ngữ phổ biến.
