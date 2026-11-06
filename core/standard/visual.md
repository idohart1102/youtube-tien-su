# Tiêu chuẩn hình: sân khấu tiền sử sống (mọi kênh)
Bảng màu và font do kênh khai trong `theme.json`. Chữ hiển thị do kênh khai trong `channel.yaml`.

## Phong cách
- Video storytelling dựng từ bối cảnh, asset và chuyển động. Phong cách ảnh chung cho mọi kênh: `art_style_prompt` trong theme.json là Semi-Realistic Paleoart Concept Art, giải phẫu đúng, ánh sáng điện ảnh, không có chữ trong ảnh AI.
- Dùng `Stage`: 1 ảnh nền + cutout + lớp lá cận cảnh nhòe + không khí (sương, tàn lửa, mưa lửa, tro) + mặt nước gợn.
- Cutout trong video không viền trắng, không thẻ "Tái hiện". Cutout phải hòa vào nền: bóng tiếp đất, chỉnh tone theo nền, viền sáng theo nguồn sáng, rìa đã làm sạch. `Stage` tự làm bóng tiếp đất, mép mềm và cân màu theo nền dưới chân (`stage_prep.py`, kênh tắt được ở `theme.json` mục `stage`). Ảnh ghép nhiều cutout phải cùng ánh sáng với nền.
- Sương, khói (`mist`, `smoke`) nên tránh trên cảnh có nhân vật, layer chủ thể hoặc ảnh thật: tập 1 QC thấy thành dải che hình (bài học 87). `Stage` vẽ sương sau nhân vật; `validate_scenes` chỉ cảnh báo. Thay bằng bụi, lá rơi hoặc đổi `grade`.
- Hạn chế ám vàng: ảnh và màu chỉnh trong `Stage` giữ cân bằng trung tính, không phủ vàng, cam hay sepia toàn cảnh. Màu vàng chỉ dùng khi đó là màu thật của chi tiết trong ảnh, hoặc cảnh có lửa, dung nham, hoàng hôn theo nội dung.
- Asset làm mới mỗi video. Nhân vật chính không lặp trong `no_repeat_species` video gần nhất.
- Trong một video (Sếp chốt 2026-11-02): ảnh AI minh họa chung không dùng lại ở cảnh không liền kề, mỗi lần là 1 biến thể; nhân vật chính giữ đặc điểm nhưng mỗi cảnh 1 tư thế hoặc góc nhìn; chỉ nền địa điểm quay lại được dùng lại và phải đổi trạng thái hoặc hướng máy. Ảnh thật dùng lại thì đổi vùng phóng hoặc cách cắt.
- Tài liệu minh họa thật (ảnh, hình khoa học, bản đồ) tìm trên toàn internet bằng 9router `cx/gpt-6.1-sol`, không bắt buộc giấy phép. Giữ màu gốc, khung mảnh màu accent, ghi nguồn khi cần. Không dùng AI giả ảnh thật.

## Bốn dấu ấn của hệ thống
1. **Xuyên lớp đất** (`props.strata_in`): chỉ dùng khi đổi thời đại, đi lên là về hiện tại, chìm xuống là về quá khứ. Có số đếm khi đổi mốc thời gian lớn.
2. **Một chỗ đứng, nhiều trạng thái** (`props.grade`): một bối cảnh quay lại nhiều lần với trạng thái khác để thấy thời gian trôi.
3. **Từ hóa thạch thành sinh vật** (`FossilReveal`): ảnh thật, viền vàng thoáng qua, con vật hiện dần, 1-2 lần mỗi video. Nhãn ghi rõ loài và nơi tìm thấy.
4. **Một nhân vật xuyên suốt:** theo một con vật cụ thể qua câu chuyện, cử động bằng rig từ một ảnh gốc.

## Chuyển động
- Mỗi cảnh 1 chuyển động máy, tối đa 1 hiệu ứng chính, chỉ nhân vật chính có chuyển động lặp. Hai cảnh liền nhau khác hướng máy. Zoom không quá 1,08.
- Rung tối đa 3 lần mỗi video. Một hiệu ứng không dùng quá 15% số cảnh.
- Chừa dải phụ đề: chủ thể (người, vật, mặt sọ) không nằm trong 1/5 dưới khung (y > 864), kể cả lúc máy phóng to (bài học 90). Ảnh dọc phóng to phải kiểm phụ đề không đè mặt.
- Câu hỏi chỉ minh họa bằng sự bí ẩn. Hình đáp án ẩn (`hide`) đến đúng câu trả lời. Mọi câu hỏi gắn `[HỎI]/[ĐÁP]` hoặc `[TU-TỪ]`.
- Hình khớp lời: hình luôn là đối tượng lời đang nói. Lời chuyển sang di cốt, địa điểm, nhân vật khác thì cắt cảnh, không để ảnh cũ ở lại. Nhãn, vòng khoanh đặt đúng vật và đúng vị trí.
- Không có khoảnh khắc tĩnh: ngoài chuyển động máy, mỗi cảnh có ít nhất 1 yếu tố tự chuyển động hợp chủ thể (cutout cử động, khói, bụi, nước, lá, ánh sáng đổi). Ảnh thật: zoom chậm, trôi nhẹ, vệt sáng quét, không thêm hiệu ứng giả. Đoạn gần như đứng yên từ 2 giây là lỗi.
- Không lạm dụng đom đóm: chỉ dùng khi cảnh thật sự cần (đêm, lời nhắc tới); thường dùng bụi, lá rơi hoặc đổi ánh sáng cho đỡ nổi bật.
- Hiệu ứng theo nội dung: lời nói mưa có hạt mưa, động đất thì khung rung lắc và đá vụn rơi, lửa có tàn lửa, khói. Không dùng hiệu ứng mà lời không nhắc.

## Nhịp
- Thời gian lấy từ srt, không đoán. Cắt cảnh ở đầu câu.
- Nhịp dựng (Sếp chốt 2026-11-03, tham khảo `channels/tiensu-vn/research/2026-11-02_nhip-hinh.md`): 0-15 giây: 3-5 giây mỗi cảnh; 15-60 giây: 4-7; phút 1-3: 5-8; thân video: khoảng 6-8, tối đa 12. Bản đồ, sơ đồ có diễn biến bên trong được tới 20.
- Cảnh dài hơn 6 giây: tối đa 4 giây phải có một sự kiện hình mới (thẻ, nét khoanh, lớp, marker, đổi trạng thái, hiệu ứng). Chuyển động máy không tính. `validate_scenes` kiểm.
- Ở 25%, 50%, 75%: đổi hẳn loại hình.
- Chuyển cảnh mặc định `fade`, sang phần mới `dip`, nhấn mạnh hoặc xuyên lớp đất `cut`.

## Chữ trên màn hình
- Ít chữ: chỉ thêm thẻ, nhãn khi số liệu hoặc tên cực kỳ quan trọng và cần thiết, trung bình tối đa 2 khối chữ mỗi phút (Sếp 2026-11-03). Chỉ keyword hoặc số liệu, giới hạn theo `lang.card`. Mỗi lúc 1 khối chữ, không tính phụ đề. Thẻ hiện 3 giây.
- Thẻ chỉ hiện khi thật sự cần, và chỉ ở góc trên màn hình (trái hoặc phải, chọn góc không đè chủ thể, nhãn, badge), không ở giữa màn hình (Sếp 2026-11-03). Ngoại lệ thẻ là chú thích của một vật (số đo, niên đại của vật đó): khi ấy thẻ đứng cạnh vật, có đường dẫn trỏ vào (`card_anchor`). Số liệu và thẻ dùng font riêng của kênh (`theme.font_numbers`), không dùng font chữ hẹp, khác font phụ đề để không giống slide.
- Sơ đồ khoa học và ảnh nhiều chữ: phóng vào đúng vùng đang nói và đánh dấu, chữ trong hình phải đọc được trên điện thoại, không bị cắt mép. Nhãn bản đồ không đè nhau. Chữ tiếng Việt đủ dấu.
- Ảnh khoa học nhiều ô: cắt riêng từng ô thành file, không dùng `region` trên cả bảng (bài học 83). `region` không cắt dở mẫu vật: giữ trọn chủ thể hoặc phóng hẳn vào một chi tiết.
- Vòng khoanh, mũi tên chỉ đặt vào chi tiết thật sự thấy được trong ảnh đúng như lời đọc; không chắc vị trí thì bỏ khoanh, chỉ phóng vùng (bài học 89).
- Ảnh không có chữ rác, sai giải phẫu, sai thời kỳ hoặc vật thể lạ (bài học 85). Kiểm ngay sau khi tải/tạo (`check_assets.py`).
- Lỗi xuất hiện ở 2 bản liên tiếp (duyệt nháp hoặc QC) thì không chỉnh prop nữa: đổi asset, đổi bố cục hoặc bỏ cảnh, ghi trong báo cáo (Sếp 2026-11-05).
- Phụ đề 1 dòng, chữ trắng, không nền, viền tối mảnh, độ đậm vừa (600, viền 4 px), chạy đúng srt, giới hạn theo `lang.subtitle`. Bật mặc định, tắt bằng `--no-subs`.
- Không chú thích bất kỳ nội dung nào về việc dùng AI trong video: không dòng ghi chú AI, không chữ hay lời đọc nhắc tới AI (Sếp 2026-11-03). Kênh không khai `lang.labels.ai_notice`.

## Bản đồ
- Có Việt Nam hoặc liên quan đến Việt Nam: luôn có Hoàng Sa, Trường Sa trong khung (bài học 86, 88). Dùng mẫu `preset` của `GeoMap` (`vn`, `dna`, `asia`, đã qua kiểm đảo); tự đặt khung thì `validate_scenes` chặn khi thiếu đảo.
- Chỉ tô màu nước chứa địa điểm đang nói, không tô cùng màu Việt Nam với nước láng giềng khi có chấm địa điểm; ghi tên nước trong nhãn chấm, ví dụ "Hang Cốc Muối, Việt Nam" (bài học 82).
- Chữ bản đồ tối thiểu 34 px ở khung 1080, nhãn tự né nhau và né dải phụ đề.
- Tên địa danh theo ngôn ngữ của kênh, khai ở `lang.labels`. Bản đồ khác dùng `GeoMap` chung.
- Không vẽ đường yêu sách lên vùng biển của nước khác.
- Bản đồ cổ phải xem ảnh trước khi dùng: không nhận ảnh có chú giải riêng của bài báo.

## Âm thanh
- Giọng lớn hơn nhạc nền 18-20 dB (`scenes.json`: `music: {asset, db: -19}`). Kênh có mục `music` trong `channel.yaml`: `produce.py` tự chọn ngẫu nhiên 1 bản trong kho, lặp hết video, chỉnh theo `db` của kênh, không ghi tay. Nhạc phải có giấy phép dùng thương mại. Không nhạc horror, không jump-scare.
