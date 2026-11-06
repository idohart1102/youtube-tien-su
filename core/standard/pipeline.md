# Luồng chuẩn (mọi kênh, mọi ngôn ngữ)
Luật phân loại: dịch một quy định sang ngôn ngữ khác mà vẫn đúng nguyên văn thì nằm ở `core/standard/`. Phải đổi số, chữ hoặc font thì nằm ở `channels/<slug>/`.
Chi tiết lệnh từng bước nằm trong skill: `core/skills/build-video` (dựng khi đã có audio + srt), `core/skills/package`, `core/skills/publish-clean`. Audio đầu vào đặt ở `<tập>/audio/voice.mp3` và `voice.srt`. Ai làm bước nào: `config/ai_roles.yaml`. Hướng dẫn từng vai trò: `core/roles/`. Trước khi làm mỗi bước chạy `python core/scripts/learn.py brief --area <mảng> --channel <slug>`.

| # | Bước | Vai trò | Đầu ra | Kiểm soát |
|---|---|---|---|---|
| 0 | Nghiên cứu kênh, làm mới sau 30 ngày | researcher | `channels/<slug>/research/` | Cache trước, vidIQ sau |
| 1 | Chọn đề tài theo đợt | researcher | `backlog.csv` | Không lặp nhân vật trong `no_repeat_species` video gần nhất |
| 2 | Brief: tiêu đề, hook thumbnail, lời hứa, nguồn fact, dàn ý. Kiểm tra nguồn có tìm web | writer, reviewer | `brief.md`, `qa/facts_vN.md` | Chạy `qc_facts.py`, rồi **approver duyệt** (`status.py <tập> brief=ok`). Còn fact sai hoặc chưa xác minh thì không duyệt được. Chưa duyệt thì các script bước sau tự dừng |
| 3 | Viết kịch bản, chấm độc lập theo bộ tiêu chuẩn, kiểm tra fact, chọn bản tốt nhất | writer, reviewer | `storyboard.md`, `script.md` (kênh Nhật thêm `script_srt.md`), `meta.md`, `qa/script_vN.md` | Dưới ngưỡng thì sửa, tối đa 5 vòng, chốt bằng `qc_script.py --use-best` |
| 4 | Có audio và srt: kênh có mục `tts` trong `channel.yaml` chạy `gen_voice.py`, kênh khác do Sếp gửi. Khớp thời gian | script hoặc Sếp, script | `audio/voice.mp3`, `audio/voice.srt`, `timeline.json` | Dừng nếu khớp dưới 90% |
| 5 | Lập danh sách asset, tạo ảnh, tìm tài liệu minh họa, tự QC tối đa 5 lần, rig, kiểm ảnh ngay sau khi tải/tạo | builder, image, finder, qc-asset | `asset_plan.json`, `assets/`, `qa/assets.json`, `qa/asset_check.md` | Dưới ngưỡng ghi `missing_assets.md`, báo Sếp. Ảnh lỗi ở `asset_check` tạo lại trước khi dựng cảnh |
| 6 | Viết cảnh, kiểm tra | builder | `scenes.json` | `validate_scenes.py`: hình khớp đối tượng lời, câu hỏi có thẻ, nhịp, không tĩnh, không dùng lại ảnh AI |
| 6b | Duyệt nháp ảnh tĩnh từng cảnh trước khi render (produce.py tự chạy), cùng luật với QC video | qc-video | `qa/precheck_vN.md` | Cổng: 0 lỗi cao (trừ `qa/accepted.json`); lỗi vừa là nên sửa. Tối đa 4 vòng còn lỗi cao thì dừng, báo Sếp |
| 7 | Kênh có mục `music` thì chọn nhạc nền từ kho. Render full, kiểm tra máy | script | `render/final.mp4`, `qa/render_check.json` | `render_check.py` (có đo khoảnh khắc tĩnh) |
| 8 | QC độc lập, đề xuất sửa | qc-video | `qa/qc_vN.md` | **Approver quyết định** có render lại không, tối đa 2 lần (chạm trần thì `produce.py` dừng, ghi `can_sep`). Từ 9/10, không lỗi nặng mới đủ điều kiện gửi Sếp duyệt |
| 9 | Meta có mốc thời gian, thumbnail, danh sách đăng | packager | `meta.md`, `thumb/` | Xem `thumbnail.md` |
| 10 | Approver chốt bản cuối. Tải lên Drive, đối chiếu, dọn máy | approver, script | Link Drive trong `status.yaml` | Cần `final=ok`, script kiểm tra QC của bản render hiện tại. Sai checksum thì không xóa |
| 11 | Sếp đăng tay trên YouTube | Sếp | Video đã đăng | Theo danh sách đăng trong `meta.md` |
| 12 | Thu số liệu, học | analyst | `stats.json`, `learnings.md`, `knowledge/` | Hằng tuần |

## Quy tắc vận hành
- Chuẩn kỹ thuật bản cuối: `core/standard/video-output.md`. Render áp dụng mã hóa; kiểm tra sau render xác nhận tệp thực tế; QC hình độc lập kiểm tra nội dung. Chỉ được công bố tự động bảo đảm chuẩn sau khi đã triển khai và kiểm chứng các cổng kiểm tra trong chuẩn này.
- Mỗi tập có `status.yaml`. Đổi bước là cập nhật ngay: `python core/scripts/status.py <tập> stage=<bước>`.
- Người viết hoặc người tạo không tự chấm bài của mình. Người chấm dùng phiên mới, không đọc quá trình làm.
- Sửa lời đọc ở `storyboard.md` rồi xuất lại, không sửa `script.md`.
- GitHub chỉ chứa hệ thống: code, tiêu chuẩn, cấu hình kênh. Không đưa media hay dữ liệu của bất kỳ tập nào lên GitHub. Thư mục tập chỉ ở trên máy, thành phẩm và chữ của tập lên Drive.
- Asset làm mới mỗi video. Chỉ dùng lại `assets/shared/` (kết cấu đá, nhạc, tiếng động).
- Sau mỗi tập ghi điều học được bằng `learn.py add`. Xem `knowledge/README.md`.

Chạy song song các bước không phụ thuộc nhau: xem mục 5 của `core/roles/orchestrator.md`.
