# Tiêu chuẩn thumbnail (mọi kênh)
Font, độ dài hook, viết hoa hay không, công thức tiêu đề do kênh khai trong `channels/<slug>/thumbnail.md`.

- **Mục tiêu:** hook đủ gây ấn tượng để người xem bấm. Tạo ít nhất 3 phương án hook, chấm rồi chọn, giữ 1 dự phòng để Sếp thử A/B.
- **Hook:** gây tò mò thật sự. Người chưa biết gì về video, chỉ nhìn hình và hook, phải hiểu ngay chuyện đang nói về điều gì và muốn biết tiếp. Cấm thêm vài từ cho xong, cụm lửng phải đọc tiêu đề mới hiểu ("BÍ ẨN", "SỰ THẬT", "TA ĐÃ SAI"). Đủ nghĩa quan trọng hơn ngắn, nhưng vẫn đọc được ở 160x90 px. Bổ sung cho tiêu đề chứ không lặp lại. Ưu tiên câu hỏi, con số gây sốc, đối lập, hoặc lật niềm tin. Phải đúng sự thật.
- **Chủ thể:** 1 chủ thể chiếm 45-65% khung, có viền trắng 6-10 px (riêng thumbnail vẫn giữ viền), trong khoảnh khắc nguy hiểm, hậu quả hoặc bí ẩn, hướng về người xem hoặc hành động.
- **Chữ:** do hệ thống ghép (`core/scripts/thumb.mjs`), không để AI vẽ chữ. Viền đen dày, chữ không che mặt chủ thể, không đặt ở góc dưới phải vì bị thời lượng che.
- **Màu:** một cặp tương phản, 1 màu nhấn cho số hoặc từ khóa.
- **Cấm:** cờ, biểu tượng quốc gia, mặt người thật kiểu meme, ảnh báo chí.
- **Tự kiểm:** che tiêu đề đi, chỉ nhìn thumbnail vẫn hiểu và muốn bấm; thu nhỏ 160x90 vẫn đọc được; hook không lặp tiêu đề; có sự kiện; đúng 1 chủ thể; chữ không lỗi dấu.

## Danh sách đăng (ghi trong meta.md để Sếp đăng tay)
1. Tiêu đề, mô tả có **mốc thời gian từng phần** (mốc đầu 0:00), nguồn ảnh, hashtag, tag.
2. Thumbnail chính và dự phòng.
3. Kiểm tra quy định khai báo nội dung AI trong YouTube Studio, làm theo quy định hiện hành. Video, tiêu đề, mô tả, tag và thumbnail không nhắc tới AI; khai báo trong YouTube Studio là thiết lập lúc đăng, Sếp quyết.
4. Made for kids theo `channel.yaml`.
