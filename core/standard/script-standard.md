# Tiêu chuẩn kịch bản lớp 1 (mọi kênh, mọi ngôn ngữ)
Ưu tiên khi mâu thuẫn: `docs/decisions.md`, rồi file này, rồi `channels/<slug>/script/dna.yaml`, rồi `style.md`. Kênh được đổi trọng số, không được bỏ cổng.
Căn cứ: `channels/*/research/dna-2026-10.md`, chỉ từ video cùng ngách, ít nhất 100K view, ưu tiên từ 500K. Đây là tương quan từ mẫu nhỏ: khung để thử, không dự báo được view.

## 1. Khung kể chuyện (thứ tự bắt buộc, số giây do kênh khai)
1. **Hook:** cảnh, nghịch lý hoặc số. Không chào.
2. **Tiền cược, lời hứa, một câu hỏi lớn nói thành lời.** Ghi `[LỜI HỨA]` trước câu đó.
3. **Lời mời đăng ký trong lời dẫn,** vị trí do kênh khai ở `subscribe.position` trong `dna.yaml`: mặc định ngay sau câu hỏi lớn, trước bước đầu tiên; `end` là trong phần kết, sau câu trả lời câu hỏi lớn. Ghi `[ĐĂNG KÝ]`. Nêu lý do gắn với câu chuyện, chỉ xin một việc, không xin like hay bật chuông.
4. **Chuỗi bước leo thang,** số bước do kênh khai ở `steps` trong `dna.yaml` (mặc định 8-10), mỗi bước chừng 1,5-2,5 phút. Mỗi bước trả lời một câu hỏi khác và mở câu hỏi tiếp. Không chia 3 phần, không đọc lộ trình.
5. **Đổi nhịp ở khoảng 25%, 50%, 75%:** đổi hướng hoặc bằng chứng cụ thể; lật điều người xem vừa tin; đưa người xem vào cảnh trước cao trào.
6. **Kết:** trả lời câu hỏi lớn, quay về câu mở, chữ ký kênh, 1 câu hỏi bình luận.
- **Trục, chọn một:** đồng hồ, điều tra, chuyến đi nhập vai, "nếu như", đếm ngược. Tránh danh mục trần.
- **Điểm nhìn:** sớm xác định ai đang trải nghiệm điều gì. Thời đại chưa có người thì nói rõ cảnh nhập vai là giả định.
- **Năm lớp phải duyệt theo thứ tự:** góc kể, xương sống, bước, nhịp, câu.

## 2. Độ dài: theo kênh, không lan man
Dung sai do kênh khai ở `length_minutes` trong `dna.yaml` (mặc định 18-22 phút), đo bằng audio thật. Dựng theo lời đọc, không kéo chữ. Độ dài đi theo lượng chất liệu trong khung của kênh. Đề tài không đủ thông tin mới cho mức tối thiểu thì gộp đề tài, không độn bối cảnh.
**Fact** là một mệnh đề kiểm tra độc lập được, không đếm lại khi nhắc lại. Lập bảng trong `brief.md`: mệnh đề, nguồn, nhóm sinh vật, địa điểm, thời gian, mức chắc chắn.
**Đề tài phải qua cổng trước khi viết (ngưỡng ban đầu, sẽ chỉnh theo số liệu):**
1. Ít nhất 8 câu hỏi thực sự khác nhau.
2. Ít nhất 3 điểm đổi cách hiểu có bằng chứng.
3. Mọi khẳng định có nguồn, đủ `min_facts` trong `dna.yaml`.
4. Có neo địa phương có nguồn.
5. Mỗi bước có phương án hình, phân biệt ảnh bằng chứng với phục dựng.
6. **Có nhu cầu:** trong 6 tháng gần nhất có ít nhất 1 video outlier (view vượt xa trung bình kênh đó) cùng câu hỏi hoặc cùng chủ thể, ghi link trong brief. Đã có từ 2 video cùng góc thì phải đổi góc (Sếp 2026-11-03).
Không qua thì mở rộng góc, gộp đề tài hoặc bỏ. Video một loài chỉ làm khi kể được cả thế giới hoặc câu hỏi quanh loài đó.
**Khi viết:** cấm lặp không thêm chức năng. Được nhắc ngắn để định hướng, đối chiếu giả thuyết hoặc đóng vòng. Mỗi đoạn trên 45 giây phải có thông tin mới.
**Làm sao biết:** mỗi bước có ít nhất một câu nói rõ biết nhờ đâu (ai đo, đo cái gì, ở đâu). Số trong tiêu đề, thumbnail hoặc hook phải có câu này trong 60 giây sau khi xuất hiện.
**Mức chắc chắn:** mỗi khối suy luận nói mức chắc chắn một lần, rõ; điều đã xác nhận nói thẳng, không rào lại. Mỗi video có ít nhất một sự thật đã xác nhận làm phần thưởng chính.

## 3. Cổng bắt buộc (loại, không tính điểm)
1. Mọi fact có nguồn. Không lấy số từ video đối thủ.
2. Lời hứa của tiêu đề và thumbnail được chứng minh trong video, câu hỏi mở được trả lời đúng phạm vi.
3. Từ giật gân có căn cứ, nêu số đo hoặc bằng chứng trước. Từ so sánh tuyệt đối phải rõ tiêu chí. Không gọi nghi phạm là thủ phạm đã xác định.
4. Mức chắc chắn nói thành lời, khớp badge.
5. Có đủ thứ tự ở mục 1, có đúng 1 lời mời đăng ký ở vị trí kênh khai.
6. Không dịch từ kênh khác, không chép lời hay tiêu đề đối thủ.

## 4. Giọng native, tránh văn AI
Không dấu hiệu đơn lẻ nào chứng minh văn AI, công cụ phát hiện không đáng tin. Đây là danh sách soát, không phải luật ngôn ngữ.
**Mẫu cần soát:** nhiều câu liền cùng độ dài và cấu trúc; bộ ba chỉ để nghe hay; đoạn nào cũng kết bằng câu triết lý; đối xứng lặp "không chỉ... mà còn", "không phải X, mà là Y"; từ nối đầu câu liên tục; tính từ chung chung thay chi tiết; báo trước rỗng; câu hỏi tu từ ở mọi đoạn; ẩn dụ sáo lặp giữa các video; nghe như không có người nói.
**Thử đọc to:** chỗ nào không ai nói thành lời như vậy thì sửa. Mỗi 2 phút có một chi tiết cụ thể, kiểm chứng được, phục vụ suy luận hoặc cảnh kể.
**Quy trình:**
1. Viết nháp.
2. Một lượt riêng chỉ sửa giọng.
3. Kiểm tra bảo toàn: giữ nguyên phủ định, phạm vi, nhóm sinh vật, lượng từ, thời gian, nhân quả, mức chắc chắn. Không xóa câu rào nếu nó mang thông tin về độ tin cậy.
4. `script_lint.py` đánh dấu vị trí để người đọc xét, không phán quyết, không tự sửa.
5. `qc_script.py`: AI độc lập chấm, đánh dấu từng câu nghe như AI hoặc như dịch.
6. Người đọc to phần đầu nếu đọc được ngôn ngữ đó. Không có người bản xứ thì ghi rõ trong báo cáo: độ tự nhiên chưa được người bản xứ xác nhận, kiểm chứng thay bằng bình luận và giữ chân.

## 5. Đo và cập nhật
Đo từng video: lượt hiển thị và CTR theo nguồn, thời lượng và tỷ lệ xem trung bình, giữ chân trước, trong và sau lời mời đăng ký, số đăng ký trên 1.000 lượt xem. So cùng tuổi video. Sau 10 video đối chiếu từng tiêu chí, chỉ là tương quan. DNA chỉ đổi khi Sếp duyệt.
