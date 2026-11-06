# Remotion – tham chiếu component (build-video chỉ cần đọc file này, không đọc source)

Khung 1920x1080. Toạ độ x,y theo pixel. Video dọc: ghi `"format": "9:16"` ở đầu `scenes.json` và `asset_plan.json`, khung thành 1080x1920, hiện chỉ dùng được component `Stage`. `asset`: `shared/...` là dùng chung (assets/shared), còn lại thuộc tập (<tập>/assets), ví dụ `backgrounds/forest.jpg`.
Tốc độ dựng và xuất chung: 30 fps. Thông số bản cuối lấy từ `config/video-output.json`; tiêu chí kiểm tra tại `core/standard/video-output.md`. `produce.py` dừng nếu kiểm tra sau render không đạt; không coi preview là bản cuối.
Ví dụ đầy đủ: core/templates/scenes.example.json

| component | asset | props |
|---|---|---|
| KenBurns | ảnh nền | z0,z1 (zoom), x0,x1,y0,y1 (pan px), focus:[x,y] (điểm zoom tới), filter, label, sub |
| TitleCard | ảnh nền (tối đi) | kicker, title, sub |
| Parallax | ảnh nền AI | cam (in, out, left, right, up, down, rack), focus:[x,y] (điểm zoom tới khi in/out), layers:[{asset (cutout PNG), x, y (giữa-đáy px), h (cao px), depth (0 xa..1 gần), at_s, enter (pop, rise, fade), sticker (mặc định true), flip, drift (px), motion (breathe, sway, bob, walk), hide, unmask_s}], label, sub |
| Collage | ảnh nền (làm tối) hoặc trống | items (≤3):[{asset, x, y (tâm), w (rộng px), rot (độ), at_s, photo (ảnh thật: khung mảnh accent + credit), credit, reveal ("wipe": lộ dần trái→phải), hide, unmask_s}], label, sub |
| GeoMap | không cần | preset: vn \| dna \| asia (mẫu đã qua kiểm đảo, `lib/map_presets.json`) hoặc center:[lon,lat], scale (3000 = Việt Nam cận, 800 = châu Á, 260 = thế giới; có Việt Nam thì phải thấy cả Hoàng Sa, Trường Sa), cam (in, out), highlight:[mã ISO số, "704" = VN; chỉ tô nước chứa địa điểm], markers (≤3):[{lon,lat,label,at_s}], arrows (≤2):[{from:[lon,lat], to:[lon,lat], at_s}] |
| SizeCompare | ảnh nền | title, items:[{name, size_m, label, cutout}] (cutout: PNG nhìn ngang, rộng ảnh = size_m; người: name "human", size_m = chiều cao) |
| GeoClock | ảnh nền | from_ma, to_ma (triệu năm trước), label, sub |
| MapDrift | ảnh bản đồ cổ (ảnh thật) | markers:[{x,y (0..1), label}], arrows:[{from:[x,y], to:[x,y]}], label, sub |
| Stage | ảnh nền AI | Sân khấu sống: như Parallax, thêm grade (đổi trạng thái bối cảnh theo thời gian), atmosphere (mist, embers, firerain, ash, rain, snow, dust, fireflies, smoke, leaves, debris, lightning; xem đầu Stage.tsx), water (mặt nước gợn), layers có sprite (cử động từ rig_cutout.py), path, shadow ({w, o} với w ≤ 3 là tỷ lệ bề ngang cutout, hoặc false), tone, blur, wind, float (bay, không bóng). Mặc định: bóng tiếp đất, mép mềm, tone_auto cân màu theo nền (stage_prep.py ghi; kênh tắt ở theme.json `stage`). mist/smoke vẽ sau nhân vật (`front: true` để vẽ trước, `spread` px độ tản dọc) nên tránh trên cảnh có nhân vật (validate cảnh báo). Chân cutout y ≤ 820 để chừa dải phụ đề |
| FossilReveal | ảnh hóa thạch thật | sprite, x, y, h, outline, reveal_at, credit, label: đường viền quét qua ảnh rồi sinh vật hiện dần |
| PhotoCard | ảnh thật | credit (bắt buộc), label, sub, z (zoom cuối, mặc định 1.08), pan:[dx,dy], region:[x,y,w,h] (0..1: sơ đồ, ảnh nhiều chi tiết thì phóng vào đúng vùng đang nói), sweep (vệt sáng quét qua, mặc định bật khi cảnh ≥ 4 giây), fill (ảnh ngang phủ kín khung; không quá 2 ảnh khung liền nhau) |

Mọi cảnh có thể thêm: `props.strata_in: {dir (up: về hiện tại, down: về quá khứ), dur_s, from_asset, from_filter, counter: {from_ma, end}}` (xuyên lớp đất khi đổi thời đại, dùng với transition cut), `transition` ("fade" mặc định, "dip" khi sang chặng, "cut"),
`props.cards: [{text, at_s, dur_s, pos}]` (thẻ keyword ≤6 từ; `pos: [x, y]` do align_srt tự đặt ở góc trên màn hình, chọn góc ít đè chủ thể nhất theo qa/zones.json; thẻ là chú thích của 1 vật thì ghi `props.card_anchor: [x, y]` (điểm trên vật), thẻ đứng cạnh vật kèm chấm và đường dẫn), `props.badges: [{type: xac-nhan|co-the|tranh-cai, at_s}]`,
`props.annotate: [{type: circle|arrow|underline|highlight, x, y, w, h | from:[x,y], to:[x,y], at_s, color}]` (nét bút khoanh, mũi tên kiểu Vox).

Chuyển động (mỗi cảnh: 1 chuyển động máy + tối đa 1 hiệu ứng chính + mọi cutout nhân vật đều có thể có `motion`, các lớp tự lệch nhịp theo thứ tự; trên 3 lớp lặp validate cảnh báo rối):
- Máy Parallax: `up`/`down` lia dọc lộ con vật cao; `rack` nền nhòe dần, cutout giữ nét. Lớp `motion`: breathe (thở), sway (đung đưa quanh chân: cây, cổ dài), bob (bơi, bay), walk (nhún bước, đi cùng `drift`).
- Không có khoảnh khắc tĩnh: cảnh Stage/Parallax phải có ít nhất 1 yếu tố tự chuyển động ngoài máy quay (atmosphere, water, grade đổi, lớp có motion/path/drift/wind), cutout chính phải cử động. Chuyển động hợp chủ thể: con vật, người: breathe, walk, sprite; cây, cỏ: wind, sway; xương, đá, công cụ: không thở, dùng path trôi chậm, dust trong nắng hoặc ánh sáng đổi (grade). Ưu tiên dust, leaves, grade đổi; mist/smoke tránh trên cảnh có nhân vật; fireflies chỉ khi cảnh thật sự cần (đêm, lời nhắc tới).
- Hiệu ứng theo nội dung: lời nói mưa thì atmosphere rain (kèm grade tối), động đất thì `props.quake: {at_s, dur_s, amp}` + atmosphere debris, lửa thì embers/smoke, sét thì lightning. Không dùng hiệu ứng mà lời không nhắc.
- Hiệu ứng chính, chọn 1: `props.spotlight: {x, y, r, at_s, dim}` (tối cả khung, chừa vòng sáng), `props.shake: {at_s, dur_s, amp}` (rung khi va chạm, ≤3 lần/tập), `props.quake` (động đất), item Collage `reveal: "wipe"`, hoặc hé lộ đáp án (`unmask_s`).
- Ẩn đáp án cho câu hỏi: lớp/item `hide: silhouette | fog | blur | keyhole`; cả ảnh nền: `props.hide: {mode: blur | fog | keyhole, x, y, r}`. `unmask_s` = lúc bắt đầu lộ (0,8 giây), `align_srt.py --apply` tự điền khi câu [ĐÁP: q] nằm trong cảnh; không có thì ẩn suốt cảnh.
Dựng từ srt: ghi `lines: [đầu, cuối]` thay cho `duration_s`; cắt cảnh giữa câu bằng `start_word: "cụm từ"` (cảnh bắt đầu ở cụm từ đó trong câu `lines[0]`, cảnh trước có thể kết thúc cùng câu), `fixed_s` cho TitleCard; `align_srt.py --apply` tự tính thời gian, thẻ và badge.
Chữ cố định trong component lấy từ `lang.labels` trong channel.yaml, số theo `locale`. Không có dòng ghi chú AI (kênh niche tiền sử không khai `ai_notice`). Nhạc nền: `scenes.json` có `music: {asset, db}`. Phụ đề 1 dòng lấy từ timeline.json; tắt bằng theme.subtitles=false hoặc --no-subs.

Không có timeline.json: `narration` của cảnh hiện làm phụ đề nếu theme.subtitles khác false.

Hình minh hoạ là ảnh (gen_assets.py), không vẽ SVG. Creature và thư viện SVG trong registry.tsx chỉ giữ cho tập cũ, validate_scenes báo lỗi nếu dùng.
GeoMap luôn vẽ quần đảo Hoàng Sa, Trường Sa và nhãn Biển Đông khi nằm trong khung. Chữ tối thiểu 34 px; nhãn đảo đặt trước, nhãn marker né nhãn đảo, né nhau và né dải phụ đề, lệch chỗ thì có đường dẫn mảnh.
Ngoại lệ luật máy đã xét: `props.allow: {"mã luật": "lý do"}` (approver ghi, ví dụ ảnh hang phủ kín khung cố ý), mã luật xem `core/scripts/scene_rules.py`.
Duyệt nháp: `node core/scripts/render.mjs <tập> --stills <file.json>` chụp ảnh tĩnh ([{t, out}]), precheck.py dùng để chấm trước khi render.

Render: `node core/scripts/render.mjs <tập>` (bản đầy đủ) hoặc thêm `--preview` (mỗi cảnh 2 giây, nửa độ phân giải, không âm thanh).
Bản đầy đủ chia đoạn 2400 khung (`--chunk-frames N`, 0 để tắt), giữ ở `render/chunks/` kèm mã băm: lần sau chỉ render đoạn có cảnh, phụ đề, asset hoặc mã nguồn component đổi; tiếng luôn render cả bài. `qa/encoding.json` ghi số đoạn dùng lại.
Asset: `python core/scripts/gen_assets.py <tập>` theo asset_plan.json (mẫu core/templates/asset_plan.example.json).
