# Vai trò: dựng
**Làm theo:** skill `core/skills/build-video`, `core/standard/visual.md`, `core/remotion/README.md`.
- Mỗi hình cần cho video là 1 mục trong `asset_plan.json`. Làm mới mỗi video, chỉ `assets/shared/` là dùng lại.
- Chạy `gen_assets.py`. Xem `asset_sheet.jpg` trước khi viết cảnh.
- Nhân vật theo `cast` trong `asset_plan.json`: không rig (Sếp 2026-11-07), mỗi tư thế 1 ảnh, cử động bằng `motion`/`path`/`drift`; khai `size_m` để kiểm tỉ lệ.
- Nhân vật chính đã ghi từ bước brief. Có đổi thì cập nhật: `status.py <tập> species=<tên>`.
