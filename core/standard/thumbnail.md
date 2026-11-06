# Tiêu chuẩn thumbnail (mọi kênh)
Font, độ dài hook, viết hoa hay không, công thức tiêu đề do kênh khai trong `channels/<slug>/thumbnail.md`.

- **Mục tiêu:** hook đủ gây ấn tượng để người xem bấm. Tạo ít nhất 3 phương án hook, chấm rồi chọn, giữ 1 dự phòng để Sếp thử A/B.
- **Hook:** gây tò mò thật sự. Người chưa biết gì về video, chỉ nhìn hình và hook, phải hiểu ngay chuyện đang nói về điều gì và muốn biết tiếp. Cấm thêm vài từ cho xong, cụm lửng phải đọc tiêu đề mới hiểu ("BÍ ẨN", "SỰ THẬT", "TA ĐÃ SAI"). Đủ nghĩa quan trọng hơn ngắn, nhưng vẫn đọc được ở 160x90 px. Bổ sung cho tiêu đề chứ không lặp lại. Ưu tiên câu hỏi, con số gây sốc, đối lập, hoặc lật niềm tin. Phải đúng sự thật.
- **Chủ thể:** 1 chủ thể chiếm 45-65% khung, có viền trắng 6-10 px (riêng thumbnail vẫn giữ viền), trong khoảnh khắc nguy hiểm, hậu quả hoặc bí ẩn, hướng về người xem hoặc hành động.
- **Chữ:** do hệ thống ghép (`core/scripts/thumb.mjs`), không để AI vẽ chữ. Viền đen dày, chữ không che mặt chủ thể, không đặt ở góc dưới phải vì bị thời lượng che.
- **Màu:** một cặp tương phản, 1 màu nhấn cho số hoặc từ khóa.
- **Cấm:** cờ, biểu tượng quốc gia, mặt người thật kiểu meme, ảnh báo chí.
- **Hai việc của hook (Sếp chốt 2026-11-06):** vừa gây tò mò để người xem dừng lại bấm, vừa đủ để hiểu video nói về chủ đề gì. Hook phải gọi tên chủ thể của chủ đề (vd "loài người khác", "gen", "Việt Nam") rồi mới mở khoảng trống tò mò. Hook chỉ tò mò mà mơ hồ chủ đề ("ĐỨA TRẺ CHỈ ĐỂ LẠI MỘT CHIẾC RĂNG" cho video về gen Denisova trong người Việt) là trượt.
- **Người xem lạ chấm:** người làm không tự chấm. Một tác tử độc lập chỉ thấy các thumbnail (chưa biết tiêu đề) trả lời: video nói về gì, câu hỏi bật ra, muốn bấm 1-10, bản 160x90 đọc được không; rồi mới xem tiêu đề. Chỉ chọn phương án được đoán đúng chủ đề.
- **Tự kiểm:** che tiêu đề đi, chỉ nhìn thumbnail vẫn hiểu và muốn bấm; thu nhỏ 160x90 vẫn đọc được; hook không lặp tiêu đề; có sự kiện; đúng 1 chủ thể; chữ không lỗi dấu.

## Danh sách đăng (ghi trong meta.md để Sếp đăng tay)
1. Tiêu đề, mô tả có **mốc thời gian từng phần** (mốc đầu 0:00), nguồn ảnh, hashtag, tag.
2. Thumbnail chính và dự phòng.
   - Kênh có phụ đề in trong hình (`theme.json` subtitles: true): không tải srt lên YouTube, vì bật CC sẽ thành 2 lớp phụ đề chồng nhau. File srt trên Drive nằm riêng trong `phu-de/`, tên khác mp4 để trình phát không tự nạp.
3. Kiểm tra quy định khai báo nội dung AI trong YouTube Studio, làm theo quy định hiện hành. Video, tiêu đề, mô tả, tag và thumbnail không nhắc tới AI; khai báo trong YouTube Studio là thiết lập lúc đăng, Sếp quyết.
4. Made for kids theo `channel.yaml`.
