# Bàn giao: cần gì để vận hành trên máy khác
Không ghi mật khẩu hay khóa vào repo. Khóa nằm trong `.env`, mật khẩu nằm trong trình quản lý mật khẩu của chủ kênh.

## Cài đặt
1. Cài Git, Node 22, Python 3.12, FFmpeg. macOS: `brew install git node@22 python@3.12 ffmpeg`.
2. `git clone <repo> && cd <repo>`. Git không chứa media: `doctor.py` tự sinh kết cấu dùng chung, nhạc và tiếng động tự đặt vào `assets/shared/` khi cần.
3. macOS/Linux: `bash setup.sh`. Windows: `powershell -ExecutionPolicy Bypass -File setup.ps1`. Script tự chọn Python 3.12, không có thì dừng.
4. Điền `.env`, sửa `config/machine.yaml`.
5. `.venv/bin/python core/scripts/doctor.py --smoke` (Windows: `.\.venv\Scripts\python core\scripts\doctor.py --smoke`). Ra `ALL OK` là đạt. Dòng `!` là cảnh báo về phiên bản hoặc dịch vụ chưa sẵn sàng, không chặn phần còn lại.
6. Mọi lệnh `python` trong tài liệu nghĩa là Python của `.venv`: chạy `source .venv/bin/activate` (Windows: `.\.venv\Scripts\Activate.ps1`) trước, hoặc gọi thẳng `.venv/bin/python`.
7. Bài dựng thử phải chạy ở nơi Chrome khởi động được. Trong sandbox của AI (ví dụ Codex `workspace-write` trên macOS), Chrome có thể báo `bootstrap_check_in ... Permission denied`: đó là giới hạn sandbox, chạy lại ngoài sandbox. Không chạy `doctor.py --smoke` và `tests/run.py` cùng lúc vì dùng chung kênh tạm.

## Dịch vụ
| Dịch vụ | Để làm gì | Thiết lập | Nếu không có |
|---|---|---|---|
| Claude Code | Vai trò chính, đọc `CLAUDE.md` | Đăng nhập tài khoản được giao | Codex đọc `AGENTS.md` |
| 9router | Tạo ảnh, chấm, tìm ảnh | Chạy trên máy, khai `router_url`; khóa ở `NINEROUTER_API_KEY` hoặc tự đọc từ `~/.9router` | Chấm và tìm ảnh: `review_provider: codex`, `gen_assets.py --codex`. Tạo ảnh: tự chuyển Codex CLI |
| Codex CLI | Dự phòng chấm, tìm ảnh, tạo ảnh | `codex login` | Mất dự phòng |
| API TTS dùng chung (KingCong) | Tạo audio + srt cho kênh có mục `tts` (`gen_voice.py`) | Dịch vụ chạy trên máy, khai `TTS_URL` trong `.env` (bỏ trống là `http://127.0.0.1:8791`). Kiểm tra: `tts service status` và credit | Sếp tạo audio ngoài hệ thống và gửi vào cùng srt |
| Kho nhạc nền | Nhạc cho kênh có mục `music` (`pick_music.py`) | Đồng bộ thư mục Drive của kênh bằng Drive Desktop, khai đường dẫn ở `music_libraries` trong `config/machine.yaml` | `produce.py` dừng ở bước chọn nhạc |
| vidIQ | Nghiên cứu, số liệu | Kết nối trong tài khoản Claude | Sếp xuất số liệu từ YouTube Studio |
| Google Drive | Lưu thành phẩm | `drive_mode: desktop` + `drive_path`, hoặc `rclone` + `drive_remote` | Không chạy được `publish_clean.py` |
| GitHub | Lưu repo | Quyền truy cập repo | Không đồng bộ được |
| YouTube | Đăng video | Chủ kênh đăng tay | Không đăng được |

Lưu ý rclone: nên tạo client_id riêng, client mặc định của rclone đang được thông báo ngừng trong 2026. Không chạy `rclone config show` vì lệnh này in token.

## 9router
Dịch vụ cổng AI chạy trên máy, tương thích OpenAI, do chủ hệ thống cài và cấp key. Repo này không chứa bộ cài của nó: xin người bàn giao cách cài và tài khoản.
- Hệ thống gọi: `GET /v1/models`, `POST /v1/images/generations`, `POST /v1/responses`. Dịch vụ nào có các điểm này và model tương ứng đều thay được, đổi `router_url` và biến `NINEROUTER_IMAGE_MODEL`, `NINEROUTER_SEARCH_MODEL`.
- Kiểm tra: `doctor.py` không báo dòng 9router. Thử thật: `python core/scripts/review.py "Mô tả ảnh này" <ảnh>`.

**Hai phương án cho việc chấm và tìm ảnh:** 9router (`review_provider: 9router`, máy hiện tại) hoặc Codex CLI (`review_provider: codex`, `gen_assets.py --codex`). Bên chính lỗi thì tự chuyển sang bên còn lại.
**Tạo ảnh:** 9router `cx/gpt-image-2.5-sunburst` là chính, không sẵn sàng thì tự chuyển Codex CLI (chậm hơn, cần `codex login`).

## Nhận việc
1. `git pull`.
2. `python core/scripts/status.py` xem từng tập đang ở đâu.
3. Đọc `docs/decisions.md`, `core/standard/pipeline.md`, file vai trò của mình trong `core/roles/`.
4. `python core/scripts/learn.py brief --area <mảng> --channel <slug>` trước khi làm.

GitHub chỉ chứa hệ thống, không có dữ liệu tập (`channels/*/episodes/`, `channels/*/archive/`). Tập đã xong có video, meta, brief, kịch bản trên Drive. Đổi máy giữa chừng thì chép thư mục tập sang máy mới. Muốn giữ luật không lặp nhân vật thì chép cả các tập gần nhất.
