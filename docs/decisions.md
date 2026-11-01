# Quyết định của Sếp (mới nhất ở trên). Mọi AI phải tuân theo. Muốn đổi thì hỏi Sếp.

## 2026-11-01
- GitHub không chứa media nào. Kết cấu dùng chung và ảnh test sinh bằng code, bỏ Git LFS. Bỏ toàn bộ lịch sử cũ, commit này là phiên bản đầu tiên hoàn chỉnh 1.0.0.
- GitHub chỉ chứa hệ thống để tiếp nhận và vận hành đủ chức năng. Không đưa dữ liệu của bất kỳ tập nào lên GitHub.
- Tạo ảnh bằng 9router `cx/gpt-image-2.5-sunburst`, không sẵn sàng thì tự chuyển Codex CLI. Ảnh hạn chế ám vàng, màu vàng chỉ dùng khi đó là màu đặc trưng thật của chi tiết trong ảnh.
- Hệ thống chạy tự động: 9router `cx/gpt-6.1-sol` là QC chính (fact, kịch bản, asset, video), không tìm được 9router thì tự chuyển Codex CLI. Audio do Sếp gửi vào là đã duyệt, không QC audio và nhịp đọc. Claude duyệt brief, quyết định render lại, chốt bản cuối. Sếp chỉ gửi audio + srt và đăng YouTube, vẫn quyết định việc đổi quy định. Thay các quyết định trước về việc Sếp duyệt. Còn fact sai hoặc hết số lần sửa thì báo Sếp.
- Brief phải qua kiểm tra nguồn có tìm web (`qc_facts.py`) trước khi duyệt. Chưa duyệt brief thì script các bước sau tự dừng.
- Bỏ skill build-scenes: audio luôn có trước khi dựng, chỉ dùng build-video.
- Mọi vai trò chạy bằng Claude mặc định dùng Opus 5.5.
- 9router `cx/gpt-6.1-sol` tìm tài liệu minh họa cho video trên toàn internet. Không bắt buộc giấy phép, có trên internet là dùng được, chú thích nguồn gốc khi cần. Thay các quy định trước đây chỉ cho dùng ảnh có giấy phép mở. Thumbnail vẫn cấm ảnh báo chí.
- Tiền Sử Đất Việt ra 1 video mỗi ngày, đăng 17:30. Kênh Nhật giữ 18:00 giờ Nhật.
- Kênh Nhật: lời hứa trước 1:00. Vòng tò mò mới mỗi 60-120 giây ở cả hai kênh.
- Bỏ toàn bộ đề tài cũ của 2 kênh, kể cả tập "thiên thạch". Đề tài mới tạo sau, bắt buộc hấp dẫn, không nhàm chán.
- Tên kênh Nhật: 太古の足あと (dấu chân thời cổ đại), không có số. Handle kênh Việt: `@tiensudatviet`.
- Audio mọi kênh do Sếp tạo ở ngoài hệ thống, gửi vào cùng srt. Hệ thống không tạo giọng đọc.
- Trụ cột kênh Việt: kỷ địa chất 35%, người tiền sử 30%, Việt Nam 20%, biển và đất đã mất 10%, phương pháp 5%.
- Chữ ký kênh: kênh Việt đổi thành "Bằng chứng vẫn còn đó." (Sếp chê câu "Đất không quên." nghe quê). Kênh Nhật đổi thành 「地球の記憶は、足元に残っています。」 (ký ức của Trái Đất còn ngay dưới chân ta), vì câu cũ nói Trái Đất nhớ "tất cả", không đúng với hồ sơ địa chất có khoảng trống. Đây là đánh giá của AI, chưa có người bản xứ xác nhận.
- Bước viết kịch bản có QC độc lập theo đúng bộ tiêu chuẩn, tối đa 3 vòng, chọn bản tốt nhất.
- Kịch bản trình bày chỉ chứa lời thuyết minh, chép nguyên sang AI tạo giọng, chữ số đổi thành chữ. Kênh Nhật có 2 bản, cả hai cũng chỉ chứa lời thuyết minh: bản TTS bằng chữ AI khó đọc nhầm, bản SRT bằng chữ viết thông thường làm căn cứ phụ đề.
- Hook thumbnail phải gây tò mò và đủ nghĩa khi chỉ nhìn thumbnail. Không thêm vài từ cho xong.
## 2026-10-31 (tên và đường dẫn dự án)
- Sếp yêu cầu chuyển nguyên dữ liệu local sang `/Users/admin/IDOHART UNIVERSE/projects/youtube/1. niche tiền sử`, tên thư mục và tên hiển thị Orca là `1. niche tiền sử`. Giữ toàn bộ channels, media, file chưa commit và Git history. Dùng đăng ký/phiên Orca mới; không cần nối lịch sử giao diện cũ.
## 2026-10-31 (kịch bản)
- Kịch bản có 2 lớp: lớp 1 chung mọi kênh, lớp 2 riêng từng kênh theo khán giả và ngôn ngữ.
- Mọi kênh kêu gọi đăng ký sau hook, trước khi đưa khán giả vào hành trình giải đáp. Lời kêu gọi viết khéo như một phần lời dẫn chuyện, hợp văn hóa khán giả nước đó. Thay các ghi chú trước đây về việc để kêu gọi ở cuối.
- Được dùng từ giật gân khi có căn cứ khoa học.
- DNA kịch bản từng kênh phải dựa trên nghiên cứu ít nhất 10 video từ 500K view cùng ngách, cùng phong cách, cùng ngôn ngữ.
- Chỉ tham chiếu video cùng ngách, ít nhất 100K view, ưu tiên từ 500K view trở lên.
- Kênh Nhật ra mỗi ngày 1 video. Không thuê người Nhật bản xứ, dùng công cụ kiểm tra thay thế và theo dõi phản hồi thật.
- Mọi kênh dạng tiền sử dài khoảng 20 phút. Bỏ lộ trình 3 phần. ヤバい được trên tiêu đề khi có căn cứ, không dùng trong lời đọc.
## 2026-10-31 (bản 1.0.0)
- Luồng chuẩn dùng chung mọi kênh; điều phụ thuộc ngôn ngữ đặt ở kênh. Hiện làm tiếng Việt, tiếng Nhật; mở thêm theo kênh, tối đa 5 ngôn ngữ phổ biến.
- Kịch bản đứng độc lập theo kênh, chỉ chung nguyên tắc viral. Sếp và AI sẽ cùng hoàn thiện nguyên tắc này.
- Dựng full video, không duyệt mẫu 60 giây. QC độc lập đề xuất sửa, Sếp quyết định render lại.
- Cutout trong video không viền trắng, không thẻ "Tái hiện". Thumbnail vẫn có viền trắng. Giữ viền vàng thoáng qua ở cảnh hóa thạch.
- Phụ đề dày vừa (600, viền 4 px).
- 4 giây cuối có dòng ghi chú AI nhỏ ở góc dưới.
- Asset làm mới mỗi video, tránh lặp loài. Không có thư viện ảnh loài.
- QC asset tối đa 5 lần, chọn bản tốt nhất, xóa bản còn lại.
- Bản đồ: ưu tiên tên theo ngôn ngữ của kênh. Liên quan đến Việt Nam thì phải có Hoàng Sa, Trường Sa. Kênh Nhật ghi 南シナ海 (Biển Nam Trung Hoa).
- Sếp đăng tay. Meta có mốc thời gian từng phần. Thumbnail có hook đủ mạnh để tăng CTR.
- Thành phẩm lên Drive "00 Thành phẩm AI nộp", đối chiếu xong xóa media trên máy. Gói nguồn giữ 30 ngày rồi xóa.
- Claude dùng Opus 5.5. 9router dùng `cx/gpt-6.1-sol` cho chấm, `cx/gpt-image-2.5` cho ảnh. Codex là phương án thay thế, ghi trong hướng dẫn.
- Thay toàn bộ repo cũ bằng bản này, đánh số 1.0.0.
- Có cơ chế học hỏi trong `knowledge/`.
## 2026-10-30
- Trao đổi với Sếp bằng tiếng Việt; sản phẩm video bằng ngôn ngữ kênh, viết như người bản xứ; từ nước ngoài có nghĩa tiếng Việt bên cạnh.
