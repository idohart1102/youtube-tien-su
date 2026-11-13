# Tiêu chuẩn hình: sân khấu tiền sử sống (mọi kênh)
Bảng màu và font do kênh khai trong `theme.json`. Chữ hiển thị do kênh khai trong `channel.yaml`.

## Phong cách
- Video storytelling dựng từ bối cảnh, asset và chuyển động. Phong cách ảnh chung cho mọi kênh: `art_style_prompt` trong theme.json là Semi-Realistic Paleoart Concept Art, giải phẫu đúng, ánh sáng điện ảnh, không có chữ trong ảnh AI.
- Dùng `Stage`: 1 ảnh nền + cutout + lớp lá cận cảnh nhòe + không khí (sương, tàn lửa, mưa lửa, tro) + mặt nước gợn.
- Cutout trong video có viền mảnh (2-4 px) màu giấy ngả theo nền (Sếp 2026-11-07), không trắng tinh, không thẻ "Tái hiện". `Stage` tự vẽ viền theo `outline_auto` (`stage_prep.py`), lớp nhòe không viền, kênh tắt ở `theme.json` `stage.outline`. Cutout vẫn phải khớp nền: bóng tiếp đất, chỉnh tone theo nền, rìa đã làm sạch.
- Ảnh thật (`PhotoCard`) đặt trên khung giấy cắt dán: màu giấy theo tông ảnh (`paper_auto`), vân giấy, nghiêng nhẹ, bóng đổ. Ảnh `fill` phủ kín khung, không khung. `Stage` tự làm bóng tiếp đất, mép mềm và cân màu theo nền dưới chân (`stage_prep.py`, kênh tắt được ở `theme.json` mục `stage`). Ảnh ghép nhiều cutout phải cùng ánh sáng với nền.
- Sương, khói (`mist`, `smoke`) nên tránh trên cảnh có nhân vật, layer chủ thể hoặc ảnh thật: tập 1 QC thấy thành dải che hình (bài học 87). `Stage` vẽ sương sau nhân vật; `validate_scenes` chỉ cảnh báo. Thay bằng bụi, lá rơi hoặc đổi `grade`.
- Hạn chế ám vàng: ảnh và màu chỉnh trong `Stage` giữ cân bằng trung tính, không phủ vàng, cam hay sepia toàn cảnh. Màu vàng chỉ dùng khi đó là màu thật của chi tiết trong ảnh, hoặc cảnh có lửa, dung nham, hoàng hôn theo nội dung.
- Asset làm mới mỗi video. Nhân vật chính không lặp trong `no_repeat_species` video gần nhất.
- Trong một video (Sếp 2026-11-07): cutout dùng lại được, mỗi lần đổi lật, cỡ, vị trí hoặc chuyển động; nhân vật chính giữ đặc điểm, có nhiều tư thế theo hành động. Mỗi ảnh nền AI tối đa 3 cảnh, lần quay lại đổi trạng thái hoặc hướng máy. Nhiều cutout: cảnh tái hiện có cutout ≥60% thời lượng, cảnh chính 2-3 cutout, gắn đối tượng lời đang nói. Ghép cutout có mặt đất đỡ, không đứng trên nước, đúng tỉ lệ thật. Nhân vật đang đi tiến theo hướng mặt, không trôi giật lùi. Ảnh thật dùng lại thì đổi vùng phóng hoặc cách cắt.
- Nguồn cutout (Sếp 2026-11-07): AI tạo PNG trong suốt (mặc định), AI vẽ nền trơn rồi tách (dự phòng), ảnh thật tách nền chỉ cho hiện vật chụp nền sạch. Không vẽ AI giả hiện vật thật.
- Tài liệu minh họa thật (ảnh, hình khoa học, bản đồ) tìm trên toàn internet bằng 9router `cx/gpt-6.1-sol`, không bắt buộc giấy phép. Giữ màu gốc, khung mảnh màu accent, ghi nguồn khi cần. Không dùng AI giả ảnh thật.

## Bốn dấu ấn của hệ thống
1. **Xuyên lớp đất** (`props.strata_in`): chỉ dùng khi đổi thời đại, đi lên là về hiện tại, chìm xuống là về quá khứ. Có số đếm khi đổi mốc thời gian lớn.
2. **Một chỗ đứng, nhiều trạng thái** (`props.grade`): một bối cảnh quay lại nhiều lần với trạng thái khác để thấy thời gian trôi.
3. **Từ hóa thạch thành sinh vật** (`FossilReveal`): ảnh thật, viền vàng thoáng qua, con vật hiện dần, 1-2 lần mỗi video. Nhãn ghi rõ loài và nơi tìm thấy.
4. **Một nhân vật xuyên suốt:** theo một con vật cụ thể qua câu chuyện, mỗi cảnh 1 tư thế, cử động bằng motion/path/drift.
   Mỗi tập khai dàn nhân vật (`cast`, Sếp 2026-11-06): tách cutout nhiều nhất có thể; không rig (Sếp 2026-11-07), mọi asset chỉ cho chuyển động (`motion`, `path`, `drift`, `wind`); không vẽ nhân vật chính, phụ chung vào ảnh nền.

## Chuyển động
- Mỗi cảnh 1 chuyển động máy, tối đa 1 hiệu ứng chính. Mọi nhân vật trên cảnh đều cử động (Sếp 2026-11-06): nhân vật chính rõ nhất, nhân vật phụ nhẹ hơn và khác kiểu để không cùng nhịp. Hai cảnh liền nhau khác hướng máy. Zoom không quá 1,08.
- Chuyển động asset theo bối cảnh và tình huống (Sếp 2026-11-07), không dùng một kiểu cho mọi cảnh. Chọn 4 thứ theo lời đọc: kiểu (`breathe`, `sway`, `bob`, `walk`, `run`), độ mạnh (`amp` 0,5-2), hướng ngang (`drift`, cùng hướng mặt), xa gần (`dz`: + đi lại gần máy, - đi ra xa; `depth` gần thì lệch theo máy nhiều).
  - Con vật lớn, cảnh rộng, yên bình: `walk` amp 0,5-0,8, drift chậm 80-160, depth 0,5-0,7.
  - Săn mồi, lao tới, hoảng loạn, chạy trốn: `run` amp 1,3-1,8, drift 300-500 hoặc dz +0,2-0,35 (lao về phía máy).
  - Rời đi, kết chặng, biến mất: `walk`, dz -0,15 đến -0,3, drift về phía mép.
  - Xuất hiện, được giới thiệu: dz +0,1-0,15 kèm walk nhẹ.
  - Người làm việc tại chỗ (đào, ghi chép, quan sát): `breathe` amp 0,6-1, không drift; người đi tìm, khảo sát: `walk` amp 0,8, drift 120-220.
  - Sinh vật biển, bay: `bob` amp 1-1,5, `float`, `path` cong. Cây, cỏ: `sway` amp 0,4-0,8. Xương, đá, công cụ: không motion, `path` trôi chậm.
  - Nhân vật chính cử động rõ hơn nhân vật phụ; 2 cảnh liền nhau không lặp cùng kiểu và cùng hướng.
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
- Có Việt Nam hoặc liên quan đến Việt Nam: luôn có hình quần đảo Hoàng Sa, Trường Sa trong khung (bài học 86, 88), không ghi chữ tên đảo (Sếp 2026-11-07). Dùng mẫu `preset` của `GeoMap` (`vn`, `dna`, `asia`, đã qua kiểm đảo); tự đặt khung thì `validate_scenes` chặn khi thiếu đảo.
- Chỉ tô màu nước chứa địa điểm đang nói, không tô cùng màu Việt Nam với nước láng giềng khi có chấm địa điểm; ghi tên nước trong nhãn chấm, ví dụ "Hang Cốc Muối, Việt Nam" (bài học 82).
- Chữ bản đồ tối thiểu 34 px ở khung 1080, nhãn tự né nhau và né dải phụ đề.
- Chấm địa danh lấy từ `knowledge/places.json` (tọa độ có nguồn), gọi theo tên trong `gm`; địa danh vùng hoặc hướng (Tây Bắc, tây Quảng Bình) tô `zones`, không dùng chấm. Camera bản đồ trôi đều suốt cảnh (Sếp 2026-11-07).
- Tên địa danh theo ngôn ngữ của kênh, khai ở `lang.labels`. Bản đồ khác dùng `GeoMap` chung.
- Không vẽ đường yêu sách lên vùng biển của nước khác.
- Bản đồ cổ phải xem ảnh trước khi dùng: không nhận ảnh có chú giải riêng của bài báo.

## Âm thanh
- Giọng lớn hơn nhạc nền 18-20 dB (`scenes.json`: `music: {asset, db: -19}`). Kênh có mục `music` trong `channel.yaml`: `produce.py` tự chọn ngẫu nhiên 1 bản trong kho, lặp hết video, chỉnh theo `db` của kênh, không ghi tay. Nhạc phải có giấy phép dùng thương mại. Không nhạc horror, không jump-scare.
