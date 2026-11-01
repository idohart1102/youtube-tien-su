---
name: write-script
description: Viết storyboard.md, script.md (kênh Nhật thêm script_srt.md) và meta.md cho một tập theo phong cách kênh, dùng cho mọi ngôn ngữ.
---
Đọc đúng những file sau, không đọc thêm. Nguyên tắc chung: `core/standard/script-standard.md`, `core/standard/accuracy.md`:
1. `brief.md` của tập.
2. `channels/<slug>/channel.yaml`: chỉ lấy `language`, `length_min`, `lang.pace`, `lang.card`, `seo` (nếu có).
3. `channels/<slug>/script/lang.md`: luật ngôn ngữ, tốc độ đọc, cách viết cho TTS.
4. `channels/<slug>/script/dna.yaml`, `style.md`, `voice-samples.md`: số đo, giọng kể, khung tập, tiêu đề, thumbnail, điều cấm. Mâu thuẫn thì theo thứ tự ưu tiên ở đầu `script-standard.md`.
5. Một file trong `channels/<slug>/script/examples/`, ưu tiên file bắt đầu bằng `01-`.
6. `channels/<slug>/script/sources.md`, nếu có.
7. `channels/<slug>/theme.json`: chỉ lấy `art_style` và `palette`, để viết prompt thumbnail.

Quy tắc chung cho mọi kênh:
- Ngôn ngữ: trao đổi, báo cáo, dòng QA và ghi chú cho Sếp luôn bằng tiếng Việt. Sản phẩm (lời đọc, tiêu đề, mô tả, tag, chữ thumbnail) viết bằng `language` của kênh, giọng người bản xứ, không dịch máy. Khi nhắc từ khóa tiếng nước ngoài trong báo cáo, ghi nghĩa tiếng Việt bên cạnh, ví dụ 化石 (hóa thạch).
- Lời đọc phải an toàn cho giọng AI theo file lang (xem script/lang.md của kênh).
- Độ dài khoảng 20 phút, lấy từ `lang.pace`. Xương sống phải có trong brief và qua cổng đề tài trước khi viết.
- Theo khung ở `core/standard/script-standard.md`. Ghi `[LỜI HỨA]` trước câu hỏi lớn, `[ĐĂNG KÝ]` trước lời mời đăng ký, rồi một lượt riêng chỉ sửa giọng.
- Ghi chú hình trong [ ] ngay trong lời đọc, ví dụ [size:dunkleosteus-vs-human]. Badge mức chắc chắn cũng ghi trong [ ] nếu style.md yêu cầu. [THẺ: …] chỉ là keyword hoặc số liệu, giới hạn theo `lang.card`.
- Câu hỏi có đáp án ở phía sau: ghi `[HỎI: q1]` ngay trước câu hỏi và `[ĐÁP: q1]` ngay trước câu trả lời (q1, q2… theo thứ tự). Ghi chú hình cho câu hỏi chỉ tả sự bí ẩn (bóng đen, sương, một chi tiết), không tả đáp án.
- Chỉ dùng sự thật có nguồn khoa học (brief hoặc sources.md). Không suy đoán gây sốc sai sự thật.

## Đầu ra: 3 file trong thư mục tập, đủ 5 phần
**storyboard.md** (bản làm việc, cho chia cảnh, chapter và QA)
1. Tiêu đề video, ở dòng đầu dạng `# <tiêu đề>`. Tiêu đề phải đúng nguyên văn tên tập trong backlog hoặc brief, không tự đổi.
2. Toàn bộ kịch bản: các heading `##` theo khung tập (heading cũng là chapter), lời đọc và ghi chú [ ]. Không có HTML comment.
Cuối file ghi dòng `# QA: <điểm>/10 (<điểm>/100), lỗi: …`.

**script.md** (chỉ lời thuyết minh, Sếp chép nguyên vào AI tạo giọng. Đây là bản trình Sếp, không trình storyboard)
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

Sau khi viết xong:
- QC theo đúng bộ tiêu chuẩn, tối đa 3 vòng: chạy `python core/scripts/script_lint.py <tập>`, rồi `python core/scripts/qc_script.py <tập>`. Cổng trượt, lỗi fact hoặc dưới 80% thì sửa theo `qa/script_vN.md` rồi chấm lại. Đạt hoặc hết 3 vòng: `python core/scripts/qc_script.py <tập> --use-best` để lấy bản tốt nhất, rồi mới xuất script.md. Hết 3 vòng vẫn chưa đạt thì báo Sếp các lỗi còn lại.
- Tự kiểm meta.md: đủ 5 phần, mỗi từ khoá chính xuất hiện ≥3 lần, đúng 3 hashtag, đúng 5 tag, tiêu đề trùng tên tập.
Viết thẳng vào các file, không giải thích lại cho người dùng.
