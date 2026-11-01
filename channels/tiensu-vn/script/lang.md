# Luật tiếng Việt (vi) cho script và TTS
- Tốc độ: 190-220 âm tiết mỗi phút là điểm khởi đầu, đo lại trên giọng thật. Đếm âm tiết theo khoảng trắng.
- Viết đủ dấu và đúng chính tả; không dùng teencode, không dùng chữ viết tắt (viết "Việt Nam", không viết "VN").
- Đơn vị và ký hiệu viết thành chữ để TTS đọc đúng: "ki-lô-mét", "độ C", "phần trăm", "tấn". Không viết km, °C, %.
- Số trong storyboard: dấu chấm ngăn hàng nghìn (12.000), dấu phẩy cho số thập phân (2,5). Phụ đề hiện số; `script.md` do `export_narration.py` tự đổi hết thành chữ (66 triệu → sáu mươi sáu triệu).
- Tên loài Latin: lần đầu viết kèm cách đọc trong ngoặc, ví dụ Gigantopithecus (gi-gan-tô-pi-the-cus), rồi gọi bằng tên Việt hoặc tên ngắn.
- Tên riêng tiếng Anh của nhà khoa học: giữ nguyên, không phiên âm.
- Tránh câu chứa quá 3 dấu phẩy, vì TTS sẽ ngắt nhịp sai.
- Ngắt nghỉ: kịch bản phải sạch, không chèn ký hiệu hay từ ngữ ngoài lời đọc (không dùng `[nghỉ]`). Chỗ cần dừng lâu hơn (sau câu hook, sau lời kêu gọi đăng ký, trước cú lật, sau một câu chốt mạnh) thì để 1 dòng trống trong storyboard; script.md sẽ xuống dòng ở đó. Hạn chế, khoảng 1 lần mỗi 30-60 giây; các câu khác viết liền để giọng đọc trôi.
