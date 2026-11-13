# Quyết định của Sếp (mới nhất ở trên). Mọi AI phải tuân theo. Muốn đổi thì hỏi Sếp.
Dòng gạch ngang là quyết định đã bị thay, giữ lại để biết lịch sử, không làm theo.

## 2026-11-13 (Sếp duyệt đề xuất bản 2.0, `docs/de-xuat-v2.md`)
- Chỉ nâng cấp hệ thống, không sửa lại video đã làm; luật mới áp từ lần chạy sau.
- Fact: mã F cố định theo số đầu dòng; `qc_facts` chỉ kiểm lại dòng đã sửa, gửi lô 30 dòng; nguồn ghi câu trích nguyên văn, không lấy số qua Wikipedia, khoảng cách neo vào tọa độ địa danh có tên. Vẫn tối đa 3 lần.
- Render: lần render chỉ dựng mới ≤25% số đoạn là "sửa nhỏ", không tính vào trần render, tối đa 3 lần/tập, được chạy cả khi đã chạm trần. Thay một phần dòng "render lại chạm 2 lần thì dừng" ngày 2026-11-05.
- QC video: bảng khung hình không đổi dùng lại kết quả bản trước; điểm lượt 1 trong 8,5-9,3 thì tự chấm lượt 2 các bảng mới, lỗi nặng chỉ 1 lượt thấy hạ thành vừa. Vẫn 1 lần chạy mỗi bản render (thay một phần dòng 2026-11-03).
- Bản đồ: thêm mẫu `sunda`; vùng tô đa giác tay, tô cả nước nhiều đảo, chấm chồng/ngoài khung là cảnh báo máy.
- Kho bài học: bác 11 bài lỗi thời hoặc trùng.
- Giọng: tốc độ đọc tính 225 âm tiết/phút; kịch bản ước dưới 10 phút thì không tạo giọng. KingCong thiếu srt thì dựng bằng `tts align` (Whisper).

## 2026-11-08
- Tiền Sử Đất Việt: Sếp chốt tập 8 là đề thiên thạch, tiêu đề "Có Thật 800.000 Năm Trước Một Thiên Thạch Khổng Lồ Đã Rơi Sát Việt Nam?" (vidIQ 88), thay đề 8 cũ Titanoboa (không có liên hệ Việt Nam). Trung tâm: tektite Khe Sanh; hố ứng viên dưới dung nham Bolaven (Sieh 2020), còn tranh cãi. Thư mục `2026-11-08_thien-thach-bolaven`. Dòng "bỏ tập thiên thạch" ngày 2026-11-01 nói về đề tài cũ, không áp cho đề này.
- Tiền Sử Đất Việt: Sếp chốt tập 9 là "Có Thật King Kong Từng Sống Trong Rừng Việt Nam?" (đề 9 trong danh sách đề xuất tập 7-10, `channels/tiensu-vn/research/2026-11-03_10-de-dau-tien.md`). Thư mục `2026-11-08_king-kong-viet-nam`. Đề 7, 8, 10 vẫn chờ Sếp chốt.

## 2026-11-07 (Sếp duyệt tập 2 khủng long render-5, duyệt đề xuất `de-xuat-tap3`)
- Format tập 2 là chuẩn mọi tập tiensu-vn: viền mảnh màu theo nền, ảnh thật khung giấy, không rig, chuyển động theo bối cảnh, bản đồ chỉ hình đảo.
- Cutout được dùng lại trong một video (máy chỉ cảnh báo, không chặn); nên đổi lật, cỡ, chuyển động mỗi lần. Ảnh nền AI tối đa 3 cảnh/video (quá 3 là lỗi máy chặn). Thay dòng "Ảnh AI không dùng lại ở cảnh không liền kề" ngày 2026-11-02 và mức 2 cảnh/nền bên dưới.
- Nhiều cutout hơn: cảnh tái hiện có cutout ≥60% thời lượng, cảnh chính 2-3 cutout lệch nhịp, cutout phải gắn đối tượng lời đang nói (cảnh báo, không chặn). Thêm cutout đạo cụ/hiện vật, người hiện đại, sinh vật phụ đủ lớn. Ghép cutout có mặt đất đỡ, đúng tỉ lệ thật, không đứng trên nước.
- Bản đồ: chấm địa danh lấy từ bảng có nguồn `knowledge/places.json`; địa danh vùng/hướng (Tây Bắc, tây Quảng Bình) tô vùng, không dùng chấm. Camera bản đồ trôi đều suốt cảnh.
- Thumbnail: lập asset riêng cho thumbnail từ asset_plan; panel 3 người xem lạ (16, 30, 52 tuổi), mục tiêu tham khảo trung bình ≥8, vẫn giữ cổng đoán đúng chủ đề.
- 3 nguồn cutout: (1) AI tạo thẳng PNG nền trong suốt, mặc định; (2) AI vẽ trên nền trơn rồi tách nền, dự phòng khi (1) 3 lần chưa đạt hoặc cần ánh sáng đặc biệt (`cut_method: "bg"`), `gen_assets` tự chuyển; (3) ảnh thật tách nền (`cut_real.py`), chỉ hiện vật chụp nền sạch, ghi nguồn như ảnh thật; hóa thạch lẫn trong đá để nguyên trong khung giấy. AI không vẽ giả hiện vật thật.
- Không làm bản thử 30 giây: áp luật mới từ tập 3.

## 2026-11-07 (sau bản thử tập 2 khủng long)
- Viền asset (Sếp xem bản thử 32 giây): cutout trong video có viền mảnh màu giấy ngả theo nền (`stage_prep.py` lấy màu nền quanh cutout, sáng hơn rõ), không trắng tinh. Lớp nhòe cận cảnh không viền. Ảnh thật đặt trên khung giấy cắt dán, màu giấy theo tông ảnh, vân giấy, nghiêng nhẹ, bóng đổ; ảnh phủ kín khung (`fill`) không có khung. Thay dòng "Cutout trong video không viền trắng" ngày 2026-10-31.
- Không rig nữa: rig cắt tay chân từ ảnh phẳng hay rách, lộ vết nối và bóng ma chân (bản thử `_thu-vien`). Mọi người, con vật và vật thể chỉ cho asset chuyển động: `motion` (breathe, sway, bob, walk), `path`, `drift`, `wind`. Viền cutout mảnh 2-4 px. Thay phần rig của dòng 2026-11-06 (nhân vật chính rig, phụ rig khi cần).
- Asset chuyển động theo bối cảnh và tình huống: kiểu, độ mạnh (`amp`), hướng ngang (`drift`), xa gần (`dz`, `depth`) chọn theo lời đọc (bảng trong `visual.md`). Là hướng dẫn dựng, máy không chặn.
- Bản đồ: chỉ vẽ hình 2 quần đảo Hoàng Sa, Trường Sa, không ghi chữ "Quần đảo Hoàng Sa", "Quần đảo Trường Sa". Vẫn bắt buộc có đủ 2 quần đảo trong khung.
- Thumbnail: ảnh thật quan trọng được đưa vào thumbnail (khung giấy màu theo tông ảnh); vùng nền dưới chữ hook tối hơn để chữ nổi; viền chủ thể mảnh, màu hợp nền, không mặc định trắng; viền chữ mảnh vừa. Thay "Thumbnail vẫn có viền trắng" ngày 2026-10-31.
- Không tách ảnh nền thành nhiều lớp theo độ sâu: bản thử lệch nhẹ thì không thấy khác, lệch mạnh thì lộ vết vá.
- ~~Ảnh nền AI: mỗi nền dùng tối đa 2 cảnh trong một video, tốt nhất 1 cảnh; tính cả cảnh liền kề và nền địa điểm `sync`. Quá 2 cảnh là lỗi máy chặn (`validate_scenes`), 2 cảnh là cảnh báo. Ảnh thật không áp mức này, vẫn dùng lại được khi đổi vùng phóng. Thay phần "nền địa điểm sync được dùng lại" của dòng 2026-11-02.~~ (2026-11-07 sau: tối đa 3 cảnh)
- Nhân vật đang đi phải tiến theo hướng mặt, không trôi giật lùi: cutout đi lại khai `facing` trong `asset_plan.json`, `validate_scenes` chặn khi chuyển động so với nền ngược hướng mặt. Stage nhận `drift` (tiến đều cả cảnh).
- Cảnh mở đầu không cắt sang chính ảnh vừa xem; bối cảnh phải đúng địa điểm (bảo tàng Hà Nội không có chùa tháp kiểu Lào/Thái).

## 2026-11-06
- Asset: mỗi tập khai `cast` trong `asset_plan.json`. Tách cutout nhân vật nhiều nhất có thể, tùy tình huống; ~~nhân vật chính rig, nhân vật phụ rig khi cần~~ (2026-11-07: không rig, chỉ cho asset chuyển động), asset còn lại chỉ chuyển động, không rig. Mọi nhân vật trên cảnh đều cử động (thay luật "chỉ cutout chính có motion"); trên 3 lớp lặp là cảnh báo. Là hướng dẫn dựng, máy không chặn.
- Sếp: chỉ chặn lỗi thật sự nghiêm trọng, không siết luật cứng làm khó sáng tạo. Máy chỉ chặn điều sai khách quan: sai fact, bản đồ thiếu Hoàng Sa/Trường Sa, lộ đáp án, câu hỏi thiếu thẻ, lệch audio, thiếu dấu, thiếu asset, nhịp và số thẻ chữ đã chốt, lỗi precheck mức cao. Luật thẩm mỹ còn lại (sương, dải phụ đề, số hiệu ứng, cutout đứng yên, hình lệch lời theo tên gọi, ảnh nhỏ, giữ bố cục, region) là cảnh báo, người dựng tự xét. Thay các dòng cổng render và sương ngày 2026-11-05.
- Panel khán giả là tham khảo, không phải cổng. Lời hứa quá 35 giây là cảnh báo. Lỗi kịch bản báo nhầm ghi `qa/script_accepted.json`.

## 2026-11-05 (sau tập 1 gen-denisova)
- Sếp duyệt toàn bộ đề xuất HT-01 → HT-14 (`docs/de-xuat-he-thong.md`), không hạ chuẩn ≥9/10.
- Precheck và QC video dùng chung luật `core/standard/qc-video.md` và cùng thang mức; chữ không đọc được là lỗi cao ở cả hai.
- ~~Cổng render: render đầy đủ chỉ khi precheck 0 lỗi cao và 0 lỗi vừa thuộc nhóm QC hay bắt (chu-nho, chu-chong, cutout-loi, mau, hinh-loi-lech, anh-loi), trừ lỗi approver ghi vào `qa/accepted.json`. `--force` chỉ approver dùng, bắt buộc ghi lý do, tính vào trần render.~~ Thay 2026-11-06: chỉ chặn lỗi cao; lỗi vừa là nên sửa.
- Luật dừng: precheck 4 vòng chưa qua cổng, render lại chạm 2 lần, kịch bản chạm 5 vòng thì dừng và báo Sếp (status.yaml ghi `can_sep`).
- ~~Sương/khói không dùng trên cảnh có nhân vật, layer chủ thể hoặc ảnh thật cho tới khi bản sương mới (HT-12) qua precheck/QC; cảnh phong cảnh trống vẫn dùng được.~~ Thay 2026-11-06: là cảnh báo.
- Chủ thể không nằm trong 1/5 dưới khung (y > 864): dải phụ đề.
- Lỗi xuất hiện ở 2 bản liên tiếp thì không chỉnh prop nữa: đổi asset, đổi bố cục hoặc bỏ cảnh (khuyến nghị, không chặn).
- Kịch bản: vòng chấm sau chỉ chấm câu đã sửa, câu liền kề và cổng đã trượt; sửa quá 20% số câu thì chấm lại toàn bài.
- Stage tự cân màu layer theo nền, bóng tiếp đất mặc định, mép mềm (bật mặc định, kênh tắt được trong `theme.json` mục `stage`).

## 2026-11-04
- Sếp yêu cầu triển khai cấu hình xuất chung ngay từ tập 1 Denisova (`2026-11-03_gen-denisova`), không chỉ lưu tiêu chuẩn. Cấu hình máy đọc tại `config/video-output.json`; render và kiểm tra kỹ thuật nằm trong bước xuất, QC hình độc lập giữ nguyên, không tạo lại audio. Kiểm tra lỗi phải dừng; duyệt/bàn giao yêu cầu báo cáo khớp SHA-256 video, cấu hình và đầu vào hiện tại.
- Sếp chốt cấu hình đầu ra chung mọi kênh tại `core/standard/video-output.md`: 1080p30, MP4 H.264 High, CRF 18/medium, SDR BT.709 YUV 4:2:0, AAC-LC 48 kHz stereo 384 kbps; chi tiết nhóm khung hình và kiểm tra theo chuẩn đó. Render áp dụng mã hóa, kiểm tra sau render xác nhận tệp thật, QC hình độc lập giữ nguyên. Chốt chuẩn chưa đồng nghĩa đã triển khai đủ trong mã; phải kiểm chứng trước khi tuyên bố mọi bản xuất đạt.
- Tiền Sử Đất Việt: tiêu đề đạt khi vidIQ `score_title` trên 80/100 (thay sàn 85) và Sếp thấy tò mò; dưới 80 ký tự; đúng fact. Nguyên tắc tạo đề tài và tiêu đề ghi ở `core/skills/plan-topics/SKILL.md` và mục Tiêu đề của `channels/tiensu-vn/script/style.md`.
- Tiền Sử Đất Việt: Sếp chốt 6 tiêu đề đầu tiên, đăng theo thứ tự: 1 "Tổ Tiên Người Việt Từng Lấy Vợ Lấy Chồng Với Một Loài Người Khác?"; 2 "Tại Sao Việt Nam Chưa Tìm Thấy Hóa Thạch Khủng Long Nào?"; 3 "Không Thuốc, Không Bệnh Viện, Người Liệt Này Vẫn Sống 10 Năm Thời Tiền Sử" (vidIQ 83, Sếp cho ngoại lệ sàn 85); 4 "Có Thật Ngày Xưa Có Thể Đi Bộ Từ Việt Nam Sang Indonesia?"; 5 "Tại Sao Có Hóa Thạch Sinh Vật Biển Cổ Đại Trên Cao Nguyên Đá Đồng Văn?"; 6 "Tại Sao Có Nghĩa Địa 29 Con Cá Sấu Cổ Đại Dưới Mỏ Than Lạng Sơn?".
- ~~Tiền Sử Đất Việt: tiêu đề dưới 80 ký tự. Sếp chọn tiêu đề bằng cảm nhận độ tò mò; vidIQ `score_title` chỉ để tham khảo, sàn 85/100 để loại bản quá yếu (vidIQ chấm lệch với outlier thật của ngách). Tiêu đề phải đưa điều lạ có thật vào chữ, không chỉ nêu chủ đề; vẫn phải đúng fact.~~ Thay: sàn vidIQ >80.
- Tiền Sử Đất Việt: tiêu đề không dùng "như thế nào/thế nào" khi người xem chưa biết sự kiện (đa số đề của kênh): hé lộ bí ẩn và hỏi tại sao/ai/ở đâu. (6 tiêu đề kèm theo ở dòng này đã thay, xem dòng chốt bên trên)
- ~~Tiền Sử Đất Việt: 6 tiêu đề đầu tiên đổi theo vidIQ (score_title ≥90): 1 "Tổ Tiên Người Việt Đã Gặp Loài Người Cổ Đại Denisova Như Thế Nào?" (91); 2 "Tại Sao Việt Nam Chưa Tìm Thấy Hóa Thạch Khủng Long Nào?" (93); 3 "Bị Liệt 10 Năm, Người Tiền Sử Việt Nam Sống Sót Thế Nào?" (91); 4 "Người Tiền Sử Đã Đi Bộ Từ Việt Nam Sang Indonesia Thời Băng Hà Như Thế Nào?" (95); 5 "Đáy Biển Cổ Đại Đã Biến Thành Cao Nguyên Đá Đồng Văn Như Thế Nào?" (93); 6 "Tại Sao Mỏ Than Lạng Sơn Lại Chứa Cả Một Thế Giới Hóa Thạch?" (92). Thứ tự đăng giữ như cũ cho tới khi Sếp chốt đổi.~~ Thay lại cùng ngày: bỏ 'như thế nào'.
- ~~Tiền Sử Đất Việt: tiêu đề dưới 80 ký tự (thay mức dưới 60, dạng A tối đa 70). Tiêu đề chỉ qua khi vidIQ `score_title` từ 90/100 trở lên, vẫn phải đúng fact.~~ Thay ngay trong ngày: bỏ mức vidIQ ≥90.
- Tiền Sử Đất Việt: Sếp duyệt bản nghe thử mở đầu Denisova dài 63,4 giây và chọn làm giọng mặc định qua KingCong: mã giọng `7WNWm0yUcEolHsfg5Bhk`, Eleven Multilingual v2 (`eleven_multilingual_v2`), tốc độ 1.05, độ ổn định 30%, độ tương đồng 30%, phóng đại phong cách 10% (`style: 0.1`). Thay cấu hình giọng Thanh Eleven v4 trước đây. Áp dụng cho các lần tạo audio tiếp theo; không tự tạo lại audio đã có. KingCong không trả xác nhận riêng mức phong cách đã áp dụng; Sếp chốt theo bản nghe thử.

## 2026-11-03
- ~~Tiền Sử Đất Việt: 6 video đầu tiên của kênh, đăng đúng thứ tự (QC 9router 5 vòng, đều từ 9/10; căn cứ `channels/tiensu-vn/research/2026-11-03_10-de-dau-tien.md`): 1 "Người Việt Mang Gen Của Một Loài Người Đã Tuyệt Chủng?"; 2 "Lào, Thái Lan Có Khủng Long, Sao Việt Nam Chưa Tìm Thấy?"; 3 "Bị Liệt 10 Năm, Người Tiền Sử Việt Nam Sống Bằng Cách Nào?"; 4 "Từng Có Thời Đi Bộ Từ Việt Nam Sang Indonesia"; 5 "Vì Sao Đáy Biển Lại Nằm Trên Núi Cao Ở Đồng Văn?"; 6 "Vì Sao Mỏ Than Lạng Sơn Có Xương Của 29 Con Cá Sấu?". Tiêu đề là đề tài, giữ nguyên chữ. backlog.csv đặt score 99→94 để plan-topics chọn đúng thứ tự.~~ Thay tiêu đề 2026-11-04.
- Tiền Sử Đất Việt: độ dài linh động 10-20 phút theo lượng chất liệu, để video không lan man (thay mức 16-25 phút). Số bước khuyến nghị 5-10, mỗi bước chừng 1,5-2,5 phút.
- Không cấm cứng theo chữ "mình", "ta", "tập" (cả "chặng"): đây là từ thường, dùng đúng nghĩa thì được. Lint chỉ chặn cụm mà nghĩa luôn sai ("theo tôi", "các bạn", "quý vị", "thám tử"…); còn lại người chấm xét theo nghĩa. Người kể vẫn không tự xưng "tôi".
- Mỗi video bám một trung tâm cụ thể nhìn thấy được: người, sinh vật, hiện vật, vùng đất, biến cố hoặc nghịch lý (thay "một con người hoặc sinh vật"). Cơ chế vừa đủ chặt, không bó sáng tạo, đọc ít token.
- Lint không làm gãy nhịp văn: lỗi cứng chỉ cho điều máy đo chắc (thẻ, từ cấm, độ dài, số thiếu mã fact). Fact mức "có thể" chỉ cần nói mức chắc chắn một lần mỗi đoạn; từ tuyệt đối chỉ nhắc để xét, qc_script chấm theo nghĩa.
- Guide và chuẩn kịch bản viết thành tiêu chí chung, không đưa ví dụ hay câu mẫu cụ thể. Thêm: câu móc là câu hỏi mộc, không trả lời trước; mỗi câu thêm điều mới, một phép đối chiếu là đủ; người chỉ nghe theo kịp (1-2 ý mới mỗi câu); so sánh quy đổi và quan hệ địa lý, thời gian là fact trong brief; thử đoạn mở bằng panel trước khi viết cả bài.
- Kim chỉ nam kịch bản (`channels/tiensu-vn/script/guide.md`) là nguyên tắc và khuyến nghị chung, không gắn với đề tài cụ thể nào. Bài học riêng của một tập ghi vào `learn.py`, không viết vào guide.
- Không chú thích bất kỳ nội dung nào về việc dùng AI trong video, lời đọc, tiêu đề, mô tả, tag, thumbnail. Bỏ dòng ghi chú AI cuối video (kênh tiensu-vn, kodai-jp). Khai báo trong YouTube Studio là thiết lập lúc đăng, Sếp quyết.
- Nhịp dựng: 0-15 giây 3-5 giây/cảnh; 15-60 giây 4-7; phút 1-3 5-8; thân video khoảng 6-8, tối đa 12.
- Ít chữ: thẻ, nhãn chỉ khi số liệu hoặc tên cực kỳ quan trọng, trung bình tối đa 2 khối chữ mỗi phút.
- ~~Không lạm dụng đom đóm; dùng bụi, sương, khói nhẹ cho đỡ nổi bật.~~ Thay 2026-11-05: đom đóm vẫn hạn chế; sương/khói không dùng trên cảnh có nhân vật, chủ thể hoặc ảnh thật cho tới khi bản sương mới qua QC.
- QC video từ 9/10, không lỗi nặng, không lỗi máy mới đủ điều kiện gửi Sếp duyệt (status.py chặn final=ok dưới 9/10).
- QC video 1 lượt mỗi bản render, lấy điểm đó để duyệt hoặc sửa rồi QC bản mới; không chấm lại cùng bản (qc_video.py chặn, --force khi Sếp yêu cầu). Điểm tính từ danh sách lỗi theo công thức cố định, không dùng điểm AI tự cho.
- Niche Deerly là repo riêng (`projects/youtube/2. niche Deerly`), tách hẳn khỏi repo tiền sử. Kênh thử `deerly-ads` đã chuyển sang đó.

## 2026-11-02 (sau tập Tràng An)
- QC kịch bản tối đa 5 vòng. Câu có số ghi mã fact [F..]; fact mức "có thể" phải nói thành lời.
- Hình khớp lời theo đối tượng (`subjects`/`subject`), mọi câu hỏi gắn [HỎI]/[ĐÁP]/[TU-TỪ], duyệt nháp ảnh tĩnh trước khi render.
- Không có khoảnh khắc tĩnh; hiệu ứng thời tiết, động đất theo nội dung. ~~Ảnh AI không dùng lại ở cảnh không liền kề, trừ nền địa điểm `sync`.~~ (2026-11-07: cutout dùng lại được, nền tối đa 3 cảnh)
- Cảnh dài cứ ≤4 giây có chi tiết mới (nhịp: xem 2026-11-03).
- Thẻ chỉ khi thật sự cần, ở góc trên màn hình (2026-11-03), né chủ thể; thẻ chú thích một vật thì đứng cạnh vật có đường dẫn. Font số liệu kênh vi: Alata.
- Bỏ vai "thám tử thời gian": người kể vô hình, không tự xưng, "chúng ta" khi cùng xem bằng chứng, "bạn" khi hỏi thẳng.
- Không chia kịch bản hay scenes.json theo chương cho nhiều agent rồi gộp.

## 2026-11-02
- Tiền Sử Đất Việt có nhạc nền: mỗi video chọn ngẫu nhiên 1 bản trong kho Drive "Nhạc nền Tiền Sử Đất Việt" (id `1SNPBRZTjOChQ4iEI8i_9pK3vqu870w5c`), lặp lại cho khớp thời lượng video. File trong kho Sếp đã hạ âm lượng sẵn, hệ thống không giảm thêm. Một bản nhạc đều suốt video, thay phần nhạc đổi theo đoạn trong `style.md`.

## 2026-11-01
- Tiền Sử Đất Việt: hệ thống tự tạo audio và srt bằng `core/scripts/gen_voice.py`, qua KingCong: ElevenLabs Eleven v4 (`eleven_v4`), giọng Thanh - Clear, Steady and Informative (`N0Z0aL8qHhzwUHwRBcVo`), độ ổn định 0%, độ tương đồng 0% (Sếp chốt 2026-11-03, thay mức 60% và 75%). Tốc độ đo được 214 âm tiết/phút tính cả khoảng lặng, nên 1 phút video cần khoảng 214 âm tiết. Thay giọng `BGC20Gf5f36lf17lw2Y1N` và KingCong Speech V3 Pro đã thử trước đó. Sếp nghe bản thử và chốt đúng chuẩn ngày 2026-11-02. Thay quy định Sếp gửi audio cho kênh này; kênh khác giữ nguyên. Vẫn không QC audio và nhịp đọc.
- Tiền Sử Đất Việt, luật kịch bản v3 (Sếp duyệt 2026-11-03, căn cứ `channels/tiensu-vn/research/2026-11-03_*`): lời mời đăng ký chuyển về phần kết, sau chữ ký (`subscribe.position: end`); ~~độ dài 16-25 phút, mục tiêu 20~~ (thay bằng 10-20 phút, 2026-11-03), không độn chữ; số liệu chỉ có trần 4 số mỗi phút; chữ "vụ án" chỉ khi có người hoặc con vật chết cụ thể; tiêu đề dưới 60 ký tự, dạng chính "Vì Sao…", thêm dạng đảo niềm tin; kết 45-60 giây; rào mức chắc chắn một lần mỗi khối; cổng nhu cầu đề tài; câu "làm sao biết" mỗi bước; hài ít nhất mỗi 3-4 phút; đề tài Việt Nam bỏ đoạn "Còn ở Việt Nam thì sao?". Các luật ghi "(thử nghiệm)" trong style.md đang thử, đo lại sau 6 video. Kênh khác giữ mặc định của `core/standard/`.
- GitHub không chứa media nào. Kết cấu dùng chung và ảnh test sinh bằng code, bỏ Git LFS. Bỏ toàn bộ lịch sử cũ, commit này là phiên bản đầu tiên hoàn chỉnh 1.0.0.
- GitHub chỉ chứa hệ thống để tiếp nhận và vận hành đủ chức năng. Không đưa dữ liệu của bất kỳ tập nào lên GitHub.
- Tạo ảnh bằng 9router `cx/gpt-image-2.5-sunburst`, không sẵn sàng thì tự chuyển Codex CLI. Ảnh hạn chế ám vàng, màu vàng chỉ dùng khi đó là màu đặc trưng thật của chi tiết trong ảnh.
- Hệ thống chạy tự động: 9router `cx/gpt-6.1-sol` là QC chính (fact, kịch bản, asset, video), không tìm được 9router thì tự chuyển Codex CLI. Audio là đã duyệt, không QC audio và nhịp đọc. Claude duyệt brief, quyết định render lại, chốt bản cuối. Sếp đăng YouTube, gửi audio + srt với kênh không có `tts`, và quyết định việc đổi quy định. Thay các quyết định trước về việc Sếp duyệt. Còn fact sai hoặc hết số lần sửa thì báo Sếp.
- Brief phải qua kiểm tra nguồn có tìm web (`qc_facts.py`) trước khi duyệt. Chưa duyệt brief thì script các bước sau tự dừng.
- Bỏ skill build-scenes: audio luôn có trước khi dựng, chỉ dùng build-video.
- Mọi vai trò chạy bằng Claude mặc định dùng Opus 5.5.
- 9router `cx/gpt-6.1-sol` tìm tài liệu minh họa cho video trên toàn internet. Không bắt buộc giấy phép, có trên internet là dùng được, chú thích nguồn gốc khi cần. Thay các quy định trước đây chỉ cho dùng ảnh có giấy phép mở. Thumbnail vẫn cấm ảnh báo chí.
- Tiền Sử Đất Việt ra 1 video mỗi ngày, đăng 17:30. Kênh Nhật giữ 18:00 giờ Nhật.
- Kênh Nhật: lời hứa trước 1:00. Vòng tò mò mới mỗi 60-120 giây ở cả hai kênh.
- Bỏ toàn bộ đề tài cũ của 2 kênh, kể cả tập "thiên thạch". Đề tài mới tạo sau, bắt buộc hấp dẫn, không nhàm chán.
- Tên kênh Nhật: 太古の足あと (dấu chân thời cổ đại), không có số. Handle kênh Việt: `@tiensudatviet`.
- Audio các kênh do Sếp tạo ở ngoài hệ thống, gửi vào cùng srt, trừ Tiền Sử Đất Việt (xem quyết định giọng đọc ở trên).
- Trụ cột kênh Việt: kỷ địa chất 35%, người tiền sử 30%, Việt Nam 20%, biển và đất đã mất 10%, phương pháp 5%.
- Chữ ký kênh: kênh Việt đổi thành "Bằng chứng vẫn còn đó." (Sếp chê câu "Đất không quên." nghe quê). Kênh Nhật đổi thành 「地球の記憶は、足元に残っています。」 (ký ức của Trái Đất còn ngay dưới chân ta), vì câu cũ nói Trái Đất nhớ "tất cả", không đúng với hồ sơ địa chất có khoảng trống. Đây là đánh giá của AI, chưa có người bản xứ xác nhận.
- ~~Bước viết kịch bản có QC độc lập theo đúng bộ tiêu chuẩn, tối đa 3 vòng, chọn bản tốt nhất.~~ Thay bằng tối đa 5 vòng (2026-11-02 sau tập Tràng An).
- Kịch bản trình bày chỉ chứa lời thuyết minh, dùng nguyên làm đầu vào tạo giọng, chữ số đổi thành chữ. Kênh Nhật có 2 bản, cả hai cũng chỉ chứa lời thuyết minh: bản TTS bằng chữ AI khó đọc nhầm, bản SRT bằng chữ viết thông thường làm căn cứ phụ đề.
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
- Mọi kênh dạng tiền sử dài khoảng 20 phút (Tiền Sử Đất Việt: 10-20 phút từ 2026-11-03). Bỏ lộ trình 3 phần. ヤバい được trên tiêu đề khi có căn cứ, không dùng trong lời đọc.

## 2026-10-31 (bản 1.0.0)
- Luồng chuẩn dùng chung mọi kênh; điều phụ thuộc ngôn ngữ đặt ở kênh. Hiện làm tiếng Việt, tiếng Nhật; mở thêm theo kênh, tối đa 5 ngôn ngữ phổ biến.
- Kịch bản đứng độc lập theo kênh, chỉ chung nguyên tắc viral. Sếp và AI sẽ cùng hoàn thiện nguyên tắc này.
- Dựng full video, không duyệt mẫu 60 giây. QC độc lập đề xuất sửa. ~~Sếp quyết định render lại.~~ Thay bằng Claude (approver) quyết định render lại (2026-11-01).
- ~~Cutout trong video không viền trắng~~ (2026-11-07: viền màu giấy theo nền), không thẻ "Tái hiện". ~~Thumbnail vẫn có viền trắng.~~ (2026-11-07: viền mảnh màu theo nền) Giữ viền vàng thoáng qua ở cảnh hóa thạch.
- Phụ đề dày vừa (600, viền 4 px).
- ~~4 giây cuối có dòng ghi chú AI nhỏ ở góc dưới.~~ Bỏ từ 2026-11-03.
- Asset làm mới mỗi video, tránh lặp loài. Không có thư viện ảnh loài.
- QC asset tối đa 5 lần, chọn bản tốt nhất, xóa bản còn lại.
- Bản đồ: ưu tiên tên theo ngôn ngữ của kênh. Liên quan đến Việt Nam thì phải có Hoàng Sa, Trường Sa. Kênh Nhật ghi 南シナ海 (Biển Nam Trung Hoa).
- Sếp đăng tay. Meta có mốc thời gian từng phần. Thumbnail có hook đủ mạnh để tăng CTR.
- Thành phẩm lên Drive "00 Thành phẩm AI nộp", đối chiếu xong xóa media trên máy. Gói nguồn giữ 30 ngày rồi xóa.
- Claude dùng Opus 5.5. 9router dùng `cx/gpt-6.1-sol` cho chấm, ~~`cx/gpt-image-2.5`~~ ~~`cx/gpt-image-2.5-sunburst`~~ `cx/gpt-image-2.6-sunburst` cho ảnh (2026-11-11). Codex là phương án thay thế, ghi trong hướng dẫn.
- Thay toàn bộ repo cũ bằng bản này, đánh số 1.0.0.
- Có cơ chế học hỏi trong `knowledge/`.

## 2026-10-30
- Trao đổi với Sếp bằng tiếng Việt; sản phẩm video bằng ngôn ngữ kênh, viết như người bản xứ; từ nước ngoài có nghĩa tiếng Việt bên cạnh.


## 2026-11-06 — model tạo ảnh dùng chung
- Theo chỉ đạo Sếp: tạo/sửa ảnh qua 9router `cx/gpt-image-2.6-sunburst`. Không tự chuyển Codex CLI/built-in hoặc model khác khi lỗi hay ảnh áo chưa đạt; sửa prompt/tham chiếu trên cùng tuyến. Cấu hình `NINEROUTER_IMAGE_MODEL` vẫn là override tường minh của operator; không thấy override hiện hữu trong các file env đã kiểm.
