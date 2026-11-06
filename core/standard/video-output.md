# Chuẩn kỹ thuật video đầu ra

Sếp chốt ngày 2026-11-04, áp dụng chung mọi kênh, bắt đầu từ tập 1 Denisova đang triển khai. Cấu hình máy đọc: `config/video-output.json`. Bộ render ghi biên nhận `qa/encoding.json`; bộ kiểm tra ghi kết quả kỹ thuật trong `qa/render_check.json`. Một tập chỉ đạt khi báo cáo của chính tệp đó đã qua kiểm tra, không suy từ kết quả của tập khác.

## Cấu hình bản cuối
- Khung ngang 1920×1080 (16:9), khung dọc 1080×1920 (9:16); không kéo méo hoặc chèn viền đen vào tệp.
- 30 khung hình/giây cố định, quét liên tục; dựng và xuất cùng tốc độ.
- MP4, Fast Start (thông tin phát ở đầu tệp), không dùng edit lists (danh sách chỉnh thời gian phát).
- H.264 High Profile, CABAC, 2 khung B liên tiếp; nhóm khung hình đóng, khoảng cách khung khóa 15 khung tại 30 fps.
- CRF 18 (ưu tiên chất lượng ổn định), preset medium (mức cân bằng). 8 Mbps ở 1080p30 là tham khảo của YouTube, không phải sàn để đánh trượt bản nén theo CRF.
- SDR BT.709, 8-bit YUV 4:2:0, dải giới hạn; chuyển màu đúng rồi khai báo đủ primaries, transfer và matrix (màu cơ sở, hàm truyền, ma trận màu) BT.709, không chỉ gắn nhãn lên dữ liệu màu khác.
- AAC-LC, 48 kHz, stereo, 384 kbps. Không tạo lại giọng, tự đổi mức âm lượng hay giảm thêm nhạc nền; các quyết định âm thanh hiện hành vẫn áp dụng.
- 384 kbps là bitrate mục tiêu của encoder, đối chiếu bằng biên nhận lệnh thực tế; bitrate đo được có thể thấp hơn ở đoạn im lặng hoặc tín hiệu đơn giản. CRF/preset cũng đối chiếu biên nhận, không suy từ bitrate tệp.
- Phụ đề đúng ngôn ngữ, không cắt chữ; bàn giao SRT cùng MP4.
- Không tự nâng mặc định lên 4K hoặc 60 fps. Shorts: khung dọc, thời lượng tối đa 3 phút.

## Trách nhiệm và kiểm soát
- Bước render áp dụng cấu hình mã hóa trên. Bản xem thử phải phân biệt với bản cuối và không được bàn giao thay bản cuối.
- Kiểm tra tự động sau render phải đọc chính MP4: kích thước, tỷ lệ, fps, mã hóa, màu, thông số âm thanh; giải mã toàn bộ để phát hiện tệp hỏng; đối chiếu thời lượng và mốc thời gian hình–tiếng với đầu vào. Thông số tệp không tự chứng minh nội dung đã khớp lời.
- Báo cáo kỹ thuật phải gắn mã SHA-256 của tệp đã kiểm tra. Chỉ cho duyệt và bàn giao khi báo cáo đạt, khớp bản cuối hiện tại. Thiếu kiểm tra thì không được coi là đã đạt.
- Báo cáo mất hiệu lực khi đổi cấu hình, cảnh, timeline, SRT, audio giọng hoặc bản nhạc được chọn. Render bị gián đoạn/lỗi mã hóa không ghi đè bản cuối cũ; bản cuối mới chưa qua kiểm tra không được duyệt.
- Độ nét ảnh nguồn, chữ, phụ đề, nội dung hình khớp lời vẫn thuộc dựng và QC hình độc lập. Bộ mã hóa không tự sửa được những lỗi này. Không mở rộng sang QC giọng và nhịp đọc.

Nguồn: [YouTube — cấu hình mã hóa đề xuất](https://support.google.com/youtube/answer/1722171), [Shorts tối đa ba phút](https://support.google.com/youtube/answer/15424877). CRF 18 và cơ chế chặn bàn giao là chuẩn nội bộ.
