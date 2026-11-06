# Vai trò: dựng
**Làm theo:** skill `core/skills/build-video`, `core/standard/visual.md`, `core/remotion/README.md`.
- Mỗi hình cần cho video là 1 mục trong `asset_plan.json`. Làm mới mỗi video, chỉ `assets/shared/` là dùng lại.
- Chạy `gen_assets.py`. Xem `asset_sheet.jpg` trước khi viết cảnh.
- Nhân vật theo `cast` trong `asset_plan.json`: mỗi mục có `plan` khác `none` chạy `rig_auto.py`. In FAIL thì dùng ảnh gốc với `motion`, không chặn tiến độ, ghi vào `status.yaml note`.
- Nhân vật chính đã ghi từ bước brief. Có đổi thì cập nhật: `status.py <tập> species=<tên>`.
