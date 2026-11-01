# Vai trò: QC asset
Tự động trong `gen_assets.py`: tối đa 5 lần tạo, chấm, sửa prompt theo lỗi. Đạt từ 8/10 thì dừng sớm. Chọn bản cao nhất, xóa bản khác. Dưới 6/10 thì không dùng, ghi `missing_assets.md`.
Đổi nhà cung cấp: `review_provider` trong `config/machine.yaml`. Nhà cung cấp chính lỗi thì tự chuyển sang bên còn lại. Kết quả: `qa/assets.json`.
