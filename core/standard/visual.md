# Tiêu chuẩn hình: sân khấu tiền sử sống (mọi kênh)
Bảng màu và font do kênh khai trong `theme.json`. Chữ hiển thị do kênh khai trong `channel.yaml`.

## Phong cách
- Video storytelling dựng từ bối cảnh, asset và chuyển động. Phong cách ảnh chung cho mọi kênh: `art_style_prompt` trong theme.json là Semi-Realistic Paleoart Concept Art, giải phẫu đúng, ánh sáng điện ảnh, không có chữ trong ảnh AI.
- Dùng `Stage`: 1 ảnh nền + cutout + lớp lá cận cảnh nhòe + không khí (sương, tàn lửa, mưa lửa, tro) + mặt nước gợn.
- Cutout trong video không viền trắng, không thẻ "Tái hiện". Cutout phải hòa vào nền: bóng tiếp đất, chỉnh tone theo nền, viền sáng theo nguồn sáng, rìa đã làm sạch. Sương đặt sau nhân vật.
- Hạn chế ám vàng: ảnh và màu chỉnh trong `Stage` giữ cân bằng trung tính, không phủ vàng, cam hay sepia toàn cảnh. Màu vàng chỉ dùng khi đó là màu thật của chi tiết trong ảnh, hoặc cảnh có lửa, dung nham, hoàng hôn theo nội dung.
- Asset làm mới mỗi video. Nhân vật chính không lặp trong `no_repeat_species` video gần nhất.
- Tài liệu minh họa thật (ảnh, hình khoa học, bản đồ) tìm trên toàn internet bằng 9router `cx/gpt-6.1-sol`, không bắt buộc giấy phép. Giữ màu gốc, khung mảnh màu accent, ghi nguồn khi cần. Không dùng AI giả ảnh thật.

## Bốn dấu ấn của hệ thống
1. **Xuyên lớp đất** (`props.strata_in`): chỉ dùng khi đổi thời đại, đi lên là về hiện tại, chìm xuống là về quá khứ. Có số đếm khi đổi mốc thời gian lớn.
2. **Một chỗ đứng, nhiều trạng thái** (`props.grade`): một bối cảnh quay lại nhiều lần với trạng thái khác để thấy thời gian trôi.
3. **Từ hóa thạch thành sinh vật** (`FossilReveal`): ảnh thật, viền vàng thoáng qua, con vật hiện dần, 1-2 lần mỗi video. Nhãn ghi rõ loài và nơi tìm thấy.
4. **Một nhân vật xuyên suốt:** theo một con vật cụ thể qua câu chuyện, cử động bằng rig từ một ảnh gốc.

## Chuyển động
- Mỗi cảnh 1 chuyển động máy, tối đa 1 hiệu ứng chính, chỉ nhân vật chính có chuyển động lặp. Hai cảnh liền nhau khác hướng máy. Zoom không quá 1,08.
- Rung tối đa 3 lần mỗi video. Một hiệu ứng không dùng quá 15% số cảnh.
- Chừa dải phụ đề: nội dung chính không nằm dưới y 900.
- Câu hỏi chỉ minh họa bằng sự bí ẩn. Hình đáp án ẩn (`hide`) đến đúng câu trả lời.

## Nhịp
- Thời gian lấy từ srt, không đoán. Cắt cảnh ở đầu câu.
- 60 giây đầu: cảnh 4-8 giây, cho phép ngắn hơn khi cắt có chủ ý. Sau đó 8-20 giây, không cảnh nào quá 20 giây.
- Ở 25%, 50%, 75%: đổi hẳn loại hình.
- Chuyển cảnh mặc định `fade`, sang phần mới `dip`, nhấn mạnh hoặc xuyên lớp đất `cut`.

## Chữ trên màn hình
- Chỉ keyword hoặc số liệu, giới hạn theo `lang.card`. Mỗi lúc 1 khối chữ, không tính phụ đề. Thẻ hiện 3 giây.
- Phụ đề 1 dòng, chữ trắng, không nền, viền tối mảnh, độ đậm vừa (600, viền 4 px), chạy đúng srt, giới hạn theo `lang.subtitle`. Bật mặc định, tắt bằng `--no-subs`.
- 4 giây cuối có dòng ghi chú AI nhỏ ở góc dưới phải, tự động theo `lang.labels.ai_notice`.

## Bản đồ
- Có Việt Nam hoặc liên quan đến Việt Nam: luôn có Hoàng Sa, Trường Sa. `GeoMap` tự vẽ khi nằm trong khung.
- Tên địa danh theo ngôn ngữ của kênh, khai ở `lang.labels`. Bản đồ khác dùng `GeoMap` chung.
- Không vẽ đường yêu sách lên vùng biển của nước khác.
- Bản đồ cổ phải xem ảnh trước khi dùng: không nhận ảnh có chú giải riêng của bài báo.

## Âm thanh
- Giọng lớn hơn nhạc nền 18-20 dB (`scenes.json`: `music: {asset, db: -19}`). Nhạc phải có giấy phép dùng thương mại. Không nhạc horror, không jump-scare.
