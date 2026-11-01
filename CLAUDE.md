# 1. niche tiền sử — bản đồ định tuyến
`CLAUDE.md` và `AGENTS.md` phải giống hệt nhau: sửa file này thì chép sang file kia.
`core/standard/` = chuẩn chung mọi ngôn ngữ. `channels/<slug>/` = riêng của kênh. `<tap>` = `channels/<slug>/episodes/<tap>`. "Sếp" là người dùng.
**`python` trong mọi lệnh là `.venv/bin/python`**, Python hệ thống thiếu thư viện.

## Ai làm gì trong luồng tự động
- 9router `cx/gpt-6.1-sol` QC: fact, kịch bản, asset, video; không tìm được 9router thì tự chuyển Codex CLI. Claude (vai trò approver) duyệt brief, quyết định render lại, chốt bản cuối (`final=ok`).
- Việc của Sếp, AI không tự làm: gửi audio + srt (gửi vào là đã duyệt, không QC audio), đăng YouTube.
- Đổi quyết định, `dna.yaml` hoặc `core/standard/` phải hỏi Sếp. Người viết không tự chấm bài của mình.

## Ngôn ngữ
- Trao đổi, báo cáo, QA: tiếng Việt, ngắn gọn, không dán log dài.
- Sản phẩm video (kịch bản, tiêu đề, mô tả, tag, chữ thumbnail): ngôn ngữ của kênh, viết như người bản xứ.
- Từ nước ngoài trong trao đổi luôn có nghĩa tiếng Việt bên cạnh, ví dụ 大量絶滅 (đại tuyệt chủng).

## Trình tự mỗi việc
1. Mở file trong bảng: `core/skills/<skill>/SKILL.md` hoặc `core/roles/<vai-trò>.md`. File cần đọc, lệnh và thứ tự nằm trong đó; chỉ đọc đúng các file nó nêu.
2. Có mảng: `python core/scripts/learn.py brief --area <mảng> --channel <slug>`, mỗi mảng một lần.
3. Việc tạo sản phẩm: đọc `docs/decisions.md` một lần mỗi phiên. Các file mâu thuẫn thì `decisions.md` thắng, vẫn không rõ thì hỏi Sếp.
4. Đổi bước: `python core/scripts/status.py <tap> stage=<bước>`. Gặp lỗi mới hoặc cách hay: `python core/scripts/learn.py add --scope global|<slug> --area <mảng> --rule "..." --evidence "..."`.

| Việc | Skill / vai trò | Mảng |
|---|---|---|
| Chưa rõ bước tiếp theo | vai trò orchestrator | |
| Nghiên cứu kênh, đề tài | vai trò researcher | script |
| Chọn đề tài, viết brief | plan-topics | script |
| Viết kịch bản | write-script | script |
| Chấm kịch bản | vai trò reviewer (chạy `qc_script.py`, tối đa 3 vòng, không tự chấm) | |
| Dựng video (đã có audio + srt) | build-video | asset, motion, map |
| Render | produce | ops |
| QC video | vai trò qc-video | |
| Duyệt brief, render lại, bản cuối | vai trò approver | |
| Meta + thumbnail | package | thumbnail |
| Lên Drive, dọn máy | publish-clean | ops |
| Học từ số liệu | review-stats | stats |

## Luật tiết kiệm token
- Không quét cả repo. Không đọc `node_modules/`, `core/remotion/` (trừ `README.md`), `core/scripts/`, trừ khi đang sửa lỗi chúng.
- Không đọc `episodes/*/audio|render|thumb|assets`, trừ `asset_sheet.jpg`.
- Lệnh lỗi: tra `docs/runbook.md`, đọc 20 dòng cuối log, chỉ mở đúng script báo lỗi.
- Research: đọc cache trong `channels/<slug>/research/` trước. Chỉ gọi vidIQ khi cache cũ hơn 30 ngày.
- `learnings.md` ≤40 dòng, viết đè. `style.md` ≤60 dòng.

## Lệnh không có trong skill
- Tiến độ: `python core/scripts/status.py`. Duyệt brief theo vai trò approver: `python core/scripts/status.py <tap> brief=ok`. Chỉ dùng `brief=sep` hoặc `final=sep` khi Sếp nói rõ.
- Kiểm tra máy: `python core/scripts/doctor.py --smoke`. Kiểm tra toàn bộ: `python core/tests/run.py`.
- Kênh mới: `python core/scripts/new_channel.py <slug> --lang <mã>`. Tập mới: `python core/scripts/new_episode.py <slug> <ten-tap>`.
- Asset chỉ AI hoặc chỉ ảnh thật: `python core/scripts/gen_assets.py <tap> --only ai|real`.
- Rig nhân vật: `python core/scripts/rig_auto.py <tap> <file> --plan biped|quad`.
