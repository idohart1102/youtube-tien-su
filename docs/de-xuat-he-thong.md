# Đề xuất điều chỉnh hệ thống sau tập 1 (gen-denisova)
Bản: v3.2 (2026-11-05), qua 3 vòng QC độc lập (6.5 → 7 → 7.5/10), đã sửa hết mục "phải sửa" của vòng 3. Sếp duyệt toàn bộ HT-01 → HT-14 ngày 2026-11-05; tình trạng triển khai ở cuối file. Sếp gọi theo mã, ví dụ "sửa HT-03: ...".
Nguồn: qa/qc_v1-v4, precheck_v1-v12, script_v1-v7, facts_v1-v3 của tập `channels/tiensu-vn/episodes/2026-11-03_gen-denisova`; bài học 80-90.
Nguyên tắc: không hạ chuẩn (≥9/10, QC đúng SHA bản chốt, approver độc lập, Sếp duyệt bản cuối). Nhanh hơn bằng cách bắt lỗi trước render để render đầy đủ 1 lần, và khi sửa chỉ làm lại phần đổi.

## Số liệu tập 1
- Render 4 lần (~2 giờ/lần), vượt giới hạn 2 lần render lại (`approver.md:4`). QC video: 8.4 (9 dòng lỗi nặng) → 8.5 (2) → 8.5 (1) → 9.7 (0).
- Precheck 12 vòng, vòng cuối vẫn 36 lỗi (4 cao); không có luật dừng. Kịch bản 7 vòng, vượt giới hạn 5 (`decisions.md:32`), v7 vẫn trượt 2 cổng.
- Gốc chính:
  1. Precheck đã thấy nhiều lỗi (v12: 16 dòng chu-nho; ảnh voi 11:18 đã bị báo hinh-loi-lech mức vừa từ v1, cutout-loi xuất hiện từ v3) nhưng xếp mức vừa, còn cổng chỉ chặn lỗi cao (`precheck.py:131,140`). QC video xếp chữ không đọc được là cao (`qc-video.md:10`). Lỗi lọt vì lệch mức và cổng, không phải vì mắt AI.
  2. Luật precheck (`precheck.py:73-84`) thiếu bản đồ Hoàng Sa/Trường Sa, ám màu, ảnh ghép lệch sáng.
  3. Hình lệch lời (hinh-loi-lech) là loại lỗi nhiều nhất (precheck v1: 15 cao; QC v4 còn 3) vì lời đổi đối tượng giữa cảnh mà precheck chỉ chụp ở mốc 60% cảnh (`precheck.py:35-36`).
  4. Lỗi lặp suốt 4 bản render (9:52 răng hàm, 11:16 ảnh ghép, nhãn bản đồ nhỏ): chỉnh prop không hết, phải đổi asset hoặc sửa component.

## Bảng tổng
| Mã | Việc | Đợt | Cần Sếp duyệt |
|---|---|---|---|
| HT-01 | Một bộ luật, một thang mức, cổng chặn đúng | 1 | Có (sửa core/standard) |
| HT-02 | Máy chặn cứng lỗi đo được | 1 | Có (cấm mist/smoke trên cảnh có nhân vật, khác `decisions.md:26`) |
| HT-03 | Bản đồ đạt chuẩn mặc định | 1 | Có (GeoMap chung, đổi hình bản đồ mọi kênh) |
| HT-04 | Ảnh giữ trọn chủ thể; lỗi lặp thì đổi cách | 1 | Có (luật mới vào visual.md) |
| HT-05 | Cổng "render 1 lần" | 1 | Có (đổi điều kiện vào render) |
| HT-06 | Giới hạn vòng và báo Sếp | 1 | Có (đổi luật dừng) |
| HT-07 | Precheck chụp đúng lúc lời đổi ý và chú thích hiện | 2 | Không |
| HT-08 | Precheck cache theo cảnh | 2 | Không |
| HT-09 | Kiểm ảnh ngay sau khi tải/tạo | 2 | Không |
| HT-10 | Công cụ dựng cảnh chung | 2 | Không |
| HT-11 | Render lại theo đoạn | 2 | Không |
| HT-12 | Thành phần Stage: ảnh ghép, mist | 1 (trước render đầu tập 2) | Có (đổi hình mọi kênh; bật/tắt theo kênh) |
| HT-13 | Kịch bản ít vòng hơn | 3 | Có (đổi cách chấm lại) |
| HT-14 | Chạy song song và runbook | 3 | Không |

## Đợt 1: chặn lỗi trước render
### HT-01 Một bộ luật, một thang mức, cổng chặn đúng
- `precheck.py` đọc `core/standard/qc-video.md` làm luật gốc, chỉ thêm phần riêng (ô ĐANG HỎI không lộ đáp án; bóng/sương che đáp án khi đang hỏi không báo).
- Thống nhất mức: chữ không đọc được (chu-nho) = cao ở cả hai. Cổng precheck chặn cả lỗi vừa thuộc nhóm QC hay bắt (xem HT-05).
- Giữ độ phân giải hiện tại (still scale 0.5 = 960x540, bảng 3x3): precheck đã chấm ô lớn hơn QC video (480x270, `render_check.py:80-85`). Chỉ phóng 2x2 cho cảnh sơ đồ/ảnh khoa học có chữ (khoảng +4-6 lần gọi AI/vòng).
- Bài học 82-90 (đang ở mức giả thuyết, mỗi bài gặp 1 lần) chép vào `core/standard/visual.md` sau khi Sếp duyệt.
- Đạt khi: lưu bản scenes.json trước sửa của tập 2 (produce tự chép `qa/scenes_pre_vN.json` mỗi vòng); với bộ mẫu ở HT-02 (dựng lại từ lỗi tập 1), precheck báo các lỗi chữ nhỏ 5:43-6:04 và ảnh ghép 11:16 ở mức cao và produce dừng.

### HT-02 Máy chặn cứng lỗi đo được (`validate_scenes.py`)
- Thành "Cần sửa" (chặn produce):
  - GeoMap có Việt Nam trong khung mà Hoàng Sa hoặc Trường Sa ngoài khung; tô cùng màu VN với nước có địa điểm đang nói (bài học 82). Bỏ việc bỏ qua cảnh GeoMap (dòng 145).
  - atmosphere `mist`/`smoke` mặc định trên cảnh có nhân vật, layer chủ thể hoặc PhotoCard (đúng phạm vi bài học 87; cảnh phong cảnh trống vẫn dùng được) cho tới khi HT-12 sửa xong mist. Sửa 2 gợi ý đang khuyên mist/smoke (dòng 228, 262).
  - Dải phụ đề (y > 864, 1/5 dưới theo bài học 90): đáy layer chủ thể h ≥ 200 nằm trong dải; PhotoCard/region/zoom làm vùng chủ thể (theo qa/zones.json) tràn vào dải.
  - Ảnh thật hiển thị cao < 700 px (PhotoCard không fill, không region).
  - Khoảnh khắc tĩnh: dùng cùng ngưỡng với `render_check` (gần tĩnh ≥ 1,5 s) tính từ sự kiện trong scenes.json (tập 1: 8:45, 8:50 và 1:58 lặp 4 bản).
  - Giữ một bố cục quá 6 s không có sự kiện mới (lap-nhip, tập 1: 10:13-10:25 lặp v1, v3).
- Triển khai an toàn: mọi luật mới chạy ở mức cảnh báo trên tập Tràng An và scenes.json đầu tiên của tập 2 để đo báo nhầm; luật nào báo nhầm ≤ 10% mới chuyển sang chặn. Luật "ảnh < 700 px" và "giữ bố cục > 6 s" giữ mức cảnh báo ở tập 2 (thẻ ảnh nhỏ cố ý, cảnh dài tới 12 s được phép theo `decisions.md:24`).
- Giữ là cảnh báo: "lời nói X nhưng hình Y" (dòng 158, chỉ đúng câu đầu cảnh; phần chặn thật do HT-07).
- Đạt khi: bộ mẫu `core/tests/fixtures/scenes_loi_tap1.json` (dựng lại các cảnh lỗi thật: bản đồ thiếu đảo, mist, phụ đề đè layer và PhotoCard, ảnh nhỏ, tĩnh, giữ bố cục) bị bắt ≥ 90% theo cảnh; báo nhầm ≤ 10% số cảnh trên tập Tràng An và tập 2 (dữ liệu không dùng để viết luật).

### HT-03 Bản đồ đạt chuẩn mặc định (`GeoMap.tsx`)
- Cỡ chữ nhãn tối thiểu ≥ 34 px ở khung 1080, tự né nhãn đè nhau và né dải phụ đề.
- Mẫu có sẵn: Việt Nam (tâm ~[107.5,15.5], scale ~3000), Đông Nam Á, châu Á (scale ≥ 800), đều qua kiểm đảo.
- Đạt khi: precheck tập 2 không có chu-nho/chu-chong ở cảnh bản đồ.

### HT-04 Ảnh giữ trọn chủ thể; lỗi lặp thì đổi cách
- Luật visual.md + validate: region/zoom không cắt mất mẫu vật (so với zones.json); ảnh nhiều ô phải tách ô (bài học 83).
- Lỗi xuất hiện ở 2 bản liên tiếp (precheck hoặc QC) thì không chỉnh prop nữa: bắt buộc đổi asset, đổi bố cục hoặc bỏ cảnh, ghi trong báo cáo.
- Đạt khi: tập 2 không có lỗi xuất hiện ở 3 bản liên tiếp.

### HT-05 Cổng "render 1 lần"
- Render đầy đủ lần đầu chỉ khi precheck: 0 lỗi cao, và 0 lỗi vừa thuộc nhóm QC hay bắt (chu-nho, chu-chong, cutout-loi, mau, hinh-loi-lech, anh-loi), trừ lỗi trong danh sách chấp nhận.
- Đo độ chính xác precheck trước khi siết cổng: đối chiếu precheck v12 với QC v1 tập 1 (bao nhiêu lỗi QC xác nhận, bao nhiêu báo nhầm). Precheck cả 12 vòng chưa từng qua cổng hiện tại, 4 lần render đều dùng `--force` (`produce.py:26`).
- Danh sách chấp nhận `qa/accepted.json`: approver ghi lỗi đã xét là báo nhầm hoặc cố ý, kèm lý do; vòng sau không chặn và không báo lại lỗi đó (theo cảnh + loại).
- `--force`: chỉ approver được dùng, bắt buộc kèm `note` lý do, tính vào trần render.
- Đạt khi: tập 2 render lần 1 không cần `--force` và QC video lần 1 ≥ 9/10.

### HT-06 Giới hạn vòng và báo Sếp
- Precheck: sau 4 vòng (đã trừ danh sách chấp nhận) mà chưa qua cổng HT-05 thì dừng, báo Sếp kèm lỗi còn lại (không tự chuyển render khi còn lỗi nhóm QC hay bắt).
- Render lại chạm 2 lần, kịch bản chạm 5 vòng: tự dừng, báo Sếp kèm danh sách lỗi và đề xuất; status.py ghi cờ "cần Sếp".
- Đạt khi: không còn trường hợp vượt giới hạn mà không có câu hỏi Sếp.

### HT-12 Thành phần Stage (làm trước render đầu tập 2)
- Layer tự cân màu/độ sáng theo nền vùng chân, bóng tiếp đất mặc định, mép mềm; sửa mist không thành dải ngang rồi gỡ chặn ở HT-02.
- Lý do làm sớm: sửa component sau khi có cache đoạn (HT-11) làm mất cache mọi đoạn.
- Đạt khi: precheck/QC tập 2 không có cutout-loi về ánh sáng/mép.

## Đợt 2: nhanh hơn ở các vòng sửa
### HT-07 Precheck chụp đúng lúc
- Thêm mốc chụp: đầu mỗi câu mới nằm giữa cảnh (+0,5 s, lấy `start` của `lines` trong timeline.json), annotate/marker/arrow (at_s + 0,8 s). Đã có: 60% cảnh, thẻ +1 s, lộ lớp (`precheck.py:35-38`).
- Hỏi riêng ở mốc chú thích: "vòng khoanh/mũi tên có đúng vật lời đang nói không".
- Đạt khi: QC video tập 2 không có hinh-loi-lech mới và không có lỗi chú thích đặt sai (tập 1: 9:52, 1:43).

### HT-08 Precheck cache theo cảnh
- Hiện cache theo bảng 9 ô theo thứ tự (`precheck.py:105-113`): thêm/bớt 1 cảnh làm lệch mọi bảng sau. Đổi thành cache theo mã băm từng cảnh (props + asset + lời), gom cảnh đổi vào bảng mới; báo cáo giữ lỗi còn mở của cảnh không đổi.
- Bù chi phí HT-01 (2x2) và HT-07 (thêm mốc).
- Đạt khi: vòng precheck sau chỉ gửi AI cảnh đã đổi.

### HT-09 Kiểm ảnh ngay sau khi tải/tạo
- Kỹ thuật (máy): phóng ảnh thật lên ≥ 800 px cao; báo ảnh nhiều ô, chữ nước ngoài nhỏ, ám màu, cutout viền bẩn.
- Nội dung: 9router (vai QC, như qc_video) chấm `asset_sheet.jpg` so với `asset_plan.json` 1 lượt: sai thời kỳ, sai giải phẫu, vật thể lạ, chữ rác. Ảnh lỗi tạo lại trước khi dựng cảnh, không thêm vòng sau đó.
- Đạt khi: precheck tập 2 không có anh-loi do nội dung ảnh AI.

### HT-10 Công cụ dựng cảnh chung
- Đưa st/ph/gm/L của script tạm tập 1 thành `core/scripts/scene_dsl.py`, dùng mẫu bản đồ HT-03, mẫu ảnh khoa học có khoanh, mẫu nhân vật chừa dải phụ đề. Skill build-video trỏ tới.
- Đạt khi: tập 2 dựng cảnh không cần script tạm riêng.

### HT-11 Render lại theo đoạn (`render.mjs`, chế độ chunk có sẵn)
- Thư mục đoạn: đổi từ `mkdtemp` ngẫu nhiên (dòng 144) sang đường dẫn cố định theo tập, không xóa sau ghép (dòng 170).
- Mã băm đoạn gồm: cảnh chạm khoảng đoạn (cả cảnh vắt ranh giới, chuyển cảnh), phụ đề trong khoảng, theme, mã nguồn các component mà đoạn đó dùng (không băm cả thư mục Remotion), asset dùng trong khoảng. Trùng mã thì dùng lại.
- Đổi độ dài cảnh: render lại mọi đoạn từ cảnh đó trở đi. Tiếng vẫn render cả bài (dòng 159, vài phút).
- `encoding.json` ghi đoạn dùng lại; QC video vẫn chạy trên SHA file ghép cuối (không đổi quyết định).
- Đạt khi: sửa 3 cảnh trong 2 đoạn chỉ render 2 đoạn + tiếng; render_check không báo lỗi ở mối nối; thời gian ≤ 30% render đầy đủ.

## Đợt 3: kịch bản và vận hành
### HT-13 Kịch bản ít vòng hơn
- Bảng fact ghi phạm vi (ai, ở đâu, mẫu nào) và mức chắc chắn cho từng mã; người viết bám đúng phạm vi (gốc của L1-1, L1-4, fact-source trượt qua 7 vòng).
- Fact sai/chưa xác minh phải xử lý xong trước khi gửi chấm kịch bản.
- Vòng chấm sau chỉ chấm câu đã sửa và câu liền kề, kèm cổng đã trượt; sửa > 20% số câu thì chấm lại toàn bài (giữ kiểm nhịp, mạch).
- Không thêm lint cứng cho từ tuyệt đối (trái luật "xét theo nghĩa"); lint số thiếu mã fact đã có.
- Đạt khi: tập 2 qua cổng kịch bản ≤ 3 vòng.

### HT-14 Chạy song song và runbook
- Orchestrator: lúc tạo giọng đọc thì chạy HT-09 và dựng sẵn cảnh không phụ thuộc mốc thời gian.
- Bài học 80 (KingCong thiếu srt) và 84 (render theo đoạn) vào `docs/runbook.md`.

## Đã làm ở tập 1, cần Sếp xác nhận giữ
- ĐL-1 `GeoMap.tsx`: dời nhãn đảo, bỏ nhãn Biển Đông ở scale nhỏ.
- ĐL-2 `render.mjs --chunk-frames` (nền của HT-11).
- ĐL-3 `precheck.py` gửi kèm câu hỏi.
- ĐL-4 `vi_speech.py` bỏ khoảng trắng trước dấu câu; thêm test.

## Mục tiêu từ tập 2
| | Tập 1 | Tập 2 |
|---|---|---|
| Render | 4 lần đầy đủ, ~8 giờ | 1 lần đầy đủ (+ sửa theo đoạn nếu cần), ~2-2,5 giờ |
| Precheck | 12 vòng toàn bộ | ≤ 4 vòng, chỉ cảnh đổi |
| Kịch bản | 7 vòng | ≤ 3 vòng |
| QC video lần 1 | 8.4 | ≥ 9 |
| Một vòng precheck | chưa đo (16 bảng) | đo ở tập 2; vòng sau chỉ cảnh đổi (HT-08) |
| Tổng thời gian cả tập | chưa đo | đo ở tập 2 theo mốc đổi bước trong status.yaml, làm mốc so cho tập 3 |

## Tình trạng triển khai (2026-11-06)
Đã làm đủ 14 mục trong code và tài liệu, `core/tests/run.py` đạt. Các mục "Đạt khi" đo trên tập 2 thì chưa đo được.
| Mã | Đã làm | Kiểm chứng | Còn chờ |
|---|---|---|---|
| HT-01 | `precheck.py` đọc `qc-video.md` làm luật gốc; chu-nho, bản đồ là cao ở cả hai; thêm luật bản đồ, ám màu, ảnh ghép lệch sáng; 2x2 cho ảnh có chữ nhỏ; lưu `qa/scenes_pre_vN.json` | Chạy mô phỏng (giả AI) trên bản sao tập 1 | Đo lại độ khớp precheck/QC ở tập 2 |
| HT-02 | `scene_rules.py` + `validate_scenes.py`: 10 luật; bộ mẫu `core/tests/fixtures/scenes_loi_tap1.json` | Bộ mẫu bắt 12/12 cảnh; báo nhầm trên bản cuối tập 1 ≤ 7,4% mỗi luật | "tinh" giữ cảnh báo (Tràng An 12%), đo lại ở tập 2 |
| HT-03 | GeoMap: preset vn/dna/asia, chữ ≥ 34 px, nhãn né nhãn đảo, chấm đảo, nhau và dải phụ đề | Ảnh tĩnh 7:28 và 8:45 tập 1 hết đè chữ | — |
| HT-04 | Luật visual.md; region cắt chủ thể, ảnh nhiều ô; precheck đánh dấu LẶP | Mô phỏng | — |
| HT-05 | Cổng render mới, `qa/accepted.json`, `--force` cần `--note`, tính trần | Mô phỏng | Xem rủi ro bên dưới |
| HT-06 | Luật dừng: precheck 4 vòng (mã 2), trần render 3, kịch bản 5 vòng → `can_sep` | Mô phỏng | — |
| HT-07 | Mốc chụp đầu câu mới, lúc chú thích hiện, câu hỏi riêng ở mốc chú thích | Tập 1: 144 → 196 ảnh | — |
| HT-08 | Cache theo mã băm cảnh, chỉ chụp và chấm cảnh đổi | Sửa 1 cảnh → 1 bảng; không đổi → 0 | — |
| HT-09 | `check_assets.py` (gen_assets tự gọi) | Bắt đúng hình 6 ô `rang-tnh2.jpg`, 4 ảnh thật dưới 800 px | Phần chấm nội dung chưa chạy với 9router thật |
| HT-10 | `scene_dsl.py` + `scene_plan.py` | Test: mặc định không vi phạm luật bản đồ, sương, phụ đề | — |
| HT-11 | `render.mjs` giữ đoạn ở `render/chunks/`, mã băm đoạn, mặc định 2400 khung | Test: render lại không đổi → 0 đoạn mới; sửa cảnh cuối → chỉ đoạn cuối; mối nối sạch | Đo thời gian trên tập dài |
| HT-12 | Stage: bóng tiếp đất (sửa lỗi bóng 0,6 px cũ), mép mềm, `tone_auto`, sương sau nhân vật | Ảnh tĩnh tập 1: cải thiện nhẹ | Gỡ chặn sương khi precheck/QC tập 2 không còn lỗi sương |
| HT-13 | Bảng fact có cột Phạm vi; `qc_script.py` chấm lại có trọng tâm khi sửa ≤ 20% | Chưa chạy với AI thật | Đo số vòng ở tập 2 |
| HT-14 | Orchestrator chạy song song lúc tạo giọng; runbook thêm bài học 80, 84 | — | — |

Rủi ro chính: precheck v12 tập 1 chỉ khớp QC v1 ở 3/36 lỗi. Áp cổng mới lên v12 sẽ có 32 lỗi chặn, phần lớn QC không xác nhận. Tập 2 có thể chạm luật dừng 4 vòng vì báo nhầm. Cách giảm: approver ghi `qa/accepted.json`; nếu vẫn kẹt thì Sếp quyết thu hẹp nhóm lỗi vừa bị chặn (`QC_TYPES` trong `precheck.py`).

## Audit 3 vòng (2026-11-06)
Sếp: chỉ sửa lỗi thật sự nghiêm trọng, không siết luật cứng. Mỗi vòng do agent độc lập chấm (người viết code không tự chấm).
- Vòng 1: sửa ngoại lệ precheck gắn nhầm cảnh, cache render dùng lại đoạn cũ khi sửa component, chấm lại có trọng tâm cho kịch bản bị xóa bớt qua cổng, precheck sập bị hiểu là còn lỗi, bản gốc ảnh bị xóa, tạo giọng cho kịch bản chưa chấm; nới cổng (precheck chỉ chặn lỗi cao, luật thẩm mỹ thành cảnh báo, panel là tham khảo).
- Vòng 2: lỗi fact cũ tự biến mất khi chấm có trọng tâm, gen_voice nhận bản chấm trượt hoặc script.md cũ, ngoại lệ precheck theo khóa nội dung, 3 luật thẩm mỹ còn chặn.
- Vòng 3: lỗi fact đã sửa vẫn bị giữ mãi (kẹt bước kịch bản), gen_voice khi thiếu storyboard hoặc đang chờ Sếp, ngoại lệ thiếu type làm precheck sập.
