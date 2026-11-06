# Vai trò: tạo ảnh
Không cần AI hội thoại. Chạy `python core/scripts/gen_assets.py <tập>`. Model mặc định `cx/gpt-image-2.6-sunburst` nằm trong `core/scripts/router.py`, đổi bằng `NINEROUTER_IMAGE_MODEL` trong `.env`. 9router không sẵn sàng thì báo lỗi và dừng; không tự chuyển model/provider. Ảnh hạn chế ám vàng theo `core/standard/visual.md`.
Không dùng ảnh tham chiếu: 9router hiện bỏ qua tham số này. Muốn cùng một con vật nhiều tư thế thì rig từ một ảnh gốc.
