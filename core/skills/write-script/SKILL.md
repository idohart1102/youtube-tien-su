---
name: write-script
description: Viết storyboard.md, script.md (kênh Nhật thêm script_srt.md) và meta.md cho một tập theo phong cách kênh, dùng cho mọi ngôn ngữ.
---
Đọc đúng những file sau, không đọc thêm. Nguyên tắc chung: `core/standard/script-standard.md`, `core/standard/accuracy.md`:
1. `brief.md` của tập.
2. `channels/<slug>/channel.yaml`: chỉ lấy `language`, `length_min`, `lang.pace`, `lang.card`, `seo` (nếu có).
3. `channels/<slug>/script/lang.md`: luật ngôn ngữ, tốc độ đọc, cách viết cho TTS.
4. `channels/<slug>/script/guide.md` nếu có (nguyên tắc kể và giọng; đọc lại mục giọng trước lượt sửa giọng), rồi `dna.yaml`, `style.md`, `voice-samples.md`: số đo, luật cứng, khung tập, tiêu đề, thumbnail, điều cấm. Mâu thuẫn thì theo thứ tự ưu tiên ở đầu `script-standard.md`; guide là nguyên tắc, luật cứng trong style.md thắng guide.
5. Một file trong `channels/<slug>/script/examples/`, ưu tiên file bắt đầu bằng `01-`.
6. `channels/<slug>/script/sources.md`, nếu có.
7. `channels/<slug>/theme.json`: chỉ lấy `art_style` và `palette`, để viết prompt thumbnail.

Quy tắc chung cho mọi kênh:
- Ngôn ngữ: trao đổi, báo cáo, dòng QA và ghi chú cho Sếp luôn bằng tiếng Việt. Sản phẩm (lời đọc, tiêu đề, mô tả, tag, chữ thumbnail) viết bằng `language` của kênh, giọng người bản xứ, không dịch máy. Khi nhắc từ khóa tiếng nước ngoài trong báo cáo, ghi nghĩa tiếng Việt bên cạnh, ví dụ 化石 (hóa thạch).
- Lời đọc phải an toàn cho giọng AI theo file lang (xem script/lang.md của kênh).
- Độ dài theo `length_minutes` trong `dna.yaml` của kênh, đổi ra số chữ bằng `lang.pace`; độ dài đi theo lượng chất liệu, không độn. Xương sống phải có trong brief và qua cổng đề tài trước khi viết.
- Theo khung ở `core/standard/script-standard.md`. Ghi `[LỜI HỨA]` trước câu hỏi lớn, `[ĐĂNG KÝ]` trước lời mời đăng ký (vị trí theo `subscribe.position` trong dna.yaml), rồi một lượt riêng chỉ sửa giọng.
- Ghi chú hình trong [ ] ngay trong lời đọc, ví dụ [size:dunkleosteus-vs-human]. Badge mức chắc chắn cũng ghi trong [ ] nếu style.md yêu cầu. [THẺ: …] chỉ dùng cho số liệu hoặc tên cực kỳ quan trọng, trung bình tối đa 2 thẻ mỗi phút, giới hạn theo `lang.card`. Lời đọc và meta không nhắc tới AI.
- Câu hỏi có đáp án ở phía sau: ghi `[HỎI: q1]` ngay trước câu hỏi và `[ĐÁP: q1]` ngay trước câu trả lời (q1, q2… theo thứ tự). Ghi chú hình cho câu hỏi chỉ tả sự bí ẩn (bóng đen, sương, một chi tiết), không tả đáp án.
- Câu hỏi không có đáp án về sau (tu từ, hỏi người xem): ghi `[TU-TỪ]` ngay trước câu. Mọi câu kết bằng "?" phải có `[HỎI]`, `[ĐÁP]` hoặc `[TU-TỪ]`, thiếu thì không render được.
- Gắn fact: câu có số liệu hoặc mệnh đề khoa học ghi mã dòng trong bảng fact của brief ngay trước dấu câu, ví dụ `nặng 0,4 gam [F31].` Mã không được đọc, xuất bản đọc tự bỏ. Không có trong bảng fact thì không viết. Nói đúng phạm vi ghi ở cột Phạm vi (ai, ở đâu, mẫu nào), không mở rộng ra cả loài, cả vùng hay cả thời kỳ. Fact mức "Có thể" thì nói thành lời mức đó một lần trong đoạn (có lẽ, chừng, nhiều khả năng…), không rào lại từng câu. Từ tuyệt đối (chắc chắn, không thể, duy nhất, đầu tiên…) chỉ dùng khi fact chứng minh đúng như thế. `script_lint.py` kiểm cả ba.
- Tính cách người dẫn trong style.md là giọng kể, không gọi thành nhân vật hay vai trong lời đọc (không "thám tử", "nhà điều tra").
- Chỉ dùng sự thật có nguồn khoa học (brief hoặc sources.md). Không suy đoán gây sốc sai sự thật.

## Đầu ra: 3 file trong thư mục tập, đủ 5 phần
**storyboard.md** (bản làm việc, cho chia cảnh, chapter và QA)
1. Tiêu đề video, ở dòng đầu dạng `# <tiêu đề>`. Tiêu đề phải đúng nguyên văn tên tập trong backlog hoặc brief, không tự đổi.
2. Toàn bộ kịch bản: các heading `##` theo khung tập (heading cũng là chapter), lời đọc và ghi chú [ ]. Không có HTML comment.
Cuối file ghi dòng `# QA: <điểm>/10 (<điểm>/100), lỗi: …`.

**script.md** (chỉ lời thuyết minh, đầu vào tạo giọng: kênh có mục `tts` trong `channel.yaml` thì `gen_voice.py` tự đọc file này, kênh khác Sếp chép nguyên vào AI tạo giọng. Đây là bản trình Sếp, không trình storyboard)
- Không viết tay. Sau khi storyboard.md đã qua QC, chạy `python core/scripts/export_narration.py <tập>`. Script này bỏ tiêu đề, heading, ghi chú [ ] và dòng QA; chữ số đổi thành chữ; chữ được đổi theo công cụ ngôn ngữ của kênh. Script báo LỖI thì sửa storyboard rồi xuất lại.
- Kênh có `lang.script_srt` (kênh Nhật) nhận 2 bản: `script.md` là bản TTS, kanji và số đã đổi hết sang kana để AI khó đọc nhầm; `script_srt.md` là bản SRT, chữ viết thông thường, làm căn cứ phụ đề. Mở `qa/tts_readings.tsv` soát cách đọc do từ điển đoán, sai thì ghi 《》 hoặc thêm vào `script/readings.tsv`. Mỗi phần thành một đoạn; trong đoạn chỉ xuống dòng ở chỗ storyboard có dòng trống (ngắt nghỉ dài). Không có ký hiệu nào ngoài lời đọc.
- Sửa lời đọc thì sửa ở storyboard.md rồi xuất lại; không sửa trực tiếp script.md.

**meta.md** (theo `core/templates/meta.md`)
3. Mô tả chuẩn SEO, khoảng 200-350 từ:
   - Có ít nhất 3 từ khoá chính, mỗi từ khoá xuất hiện ít nhất 3 lần và đọc tự nhiên, không nhồi. 2 dòng đầu phải chứa từ khoá quan trọng nhất và cái móc của tập.
   - Có chỗ chừa sẵn cho chapters, có phần "Nguồn tham khảo và ảnh" ghi nguồn theo sources.md và credits.json, có giấy phép thì ghi kèm.
   - Kết bằng đúng 3 hashtag phổ biến. YouTube hiện 3 hashtag đầu trên tiêu đề, nên đặt hashtag mạnh nhất trước.
   - Từ khoá và hashtag lấy từ `seo` trong channel.yaml cộng 1-2 từ khoá riêng của tập. Chỉ gọi vidIQ khi cache trong `research/` cũ hơn 30 ngày.
4. Thẻ tag: đúng 5 tag, xếp từ rộng đến hẹp. Tag 1 là từ khoá chính của tập.
5. Thumbnail (chỉ ý tưởng, chưa tạo ảnh; ảnh được ghép sau khi render ở bước package). Nếu có `channels/<slug>/thumbnail.md` thì theo đúng file đó. Gồm:
   - Hook text gây tò mò và đủ nghĩa khi chỉ nhìn thumbnail, độ dài theo `channels/<slug>/thumbnail.md`, bổ sung cho tiêu đề chứ không lặp lại (câu hỏi, con số, đối lập hoặc lật niềm tin), kèm 1 phương án dự phòng. Không thêm vài từ cho xong.
   - Ý tưởng hình: khoảnh khắc nguy hiểm, hậu quả hoặc bí ẩn, 1 chủ thể chính, vật so kích thước, và cảnh hoặc ghi chú [ ] trong storyboard nên lấy asset.
   - Chữ do hệ thống ghép, không bao giờ để AI vẽ chữ.

Thử đoạn mở trước khi viết cả bài (kênh có `script/panel.yaml`): viết đoạn mở 30-60 giây vào `qa/mo_dau.md` (dòng đầu `# <tiêu đề>`), chạy `python core/scripts/panel_script.py <tập> --file qa/mo_dau.md --part`, sửa đến khi người xem muốn nghe tiếp. Lượt này tính riêng, không trừ vào 5 vòng chấm cả bài.

Sau khi viết xong:
- QC theo đúng bộ tiêu chuẩn, tối đa 5 vòng: chạy `python core/scripts/script_lint.py <tập>`, rồi `python core/scripts/qc_script.py <tập>`, rồi nếu kênh có `script/panel.yaml` thì `python core/scripts/panel_script.py <tập>` (panel khán giả giả lập, chỉ đọc lời đọc, không đọc quy chuẩn). Cổng trượt, lỗi fact hoặc dưới 80% thì sửa theo `qa/script_vN.md` rồi chấm lại. Panel là tham khảo, không phải cổng: dưới 80/100 thì sửa chỗ người xem bỏ đi nếu hợp lý, không bắt buộc đạt (tập 1 panel cao nhất 72 mà video đạt QC 9,7). Lỗi fact hoặc cổng bị báo nhầm: reviewer ghi `qa/script_accepted.json` kèm lý do. Sửa theo panel không được phá luật cứng hay fact; panel và người chấm trái nhau thì luật cứng và fact thắng, còn lại ưu tiên panel. Đạt hoặc hết 5 vòng: `python core/scripts/qc_script.py <tập> --use-best` để lấy bản tốt nhất, rồi mới xuất script.md. Từ vòng 2, sửa ≤ 20% số câu thì `qc_script.py` chỉ chấm câu đã sửa, câu liền kề và cổng đã trượt (sửa nhiều hơn thì chấm lại toàn bài), nên sửa đúng chỗ bị báo, không viết lại cả bài. Hết 5 vòng vẫn chưa đạt thì script ghi cờ `can_sep` vào status.yaml: báo Sếp các lỗi còn lại.
- Tự kiểm meta.md: đủ 5 phần, mỗi từ khoá chính xuất hiện ≥3 lần, đúng 3 hashtag, đúng 5 tag, tiêu đề trùng tên tập.
Viết thẳng vào các file, không giải thích lại cho người dùng.
