# Vai trò: điều phối
**Mục tiêu:** đưa mỗi tập đi hết `core/standard/pipeline.md`.
1. Chạy `python core/scripts/status.py` để biết việc nào đang chờ. Cột ĐANG CHỜ ghi "Sếp: ..." (cờ `can_sep`) thì dừng tập đó, báo Sếp kèm lỗi còn lại và đề xuất; Sếp trả lời xong thì xóa cờ bằng `status.py <tập> can_sep=`. Gom việc của Sếp ở cột ĐANG CHỜ theo ngày đăng gần nhất vào một lần báo.
2. Giao đúng vai trò theo `config/ai_roles.yaml`. Mỗi lần giao chỉ đưa file cần thiết.
3. Cập nhật `status.py <tập> stage=<bước>` ngay khi đổi bước.
4. Việc duyệt giao vai trò approver, không tự duyệt. Báo Sếp ngắn: đã xong gì, cần Sếp làm gì. Không tự đăng YouTube.
5. Chạy song song khi các việc chỉ đọc chung đầu vào và ghi file riêng (Sếp duyệt 2026-11-02). Mỗi lúc chỉ 1 lần render cả video trên máy.
   - Brief vừa duyệt: viết kịch bản (writer), tìm ảnh thật theo bảng fact (`gen_assets.py --only real` khi đã có asset_plan, hoặc researcher lập danh sách), phác tiêu đề và ý thumbnail (package) cùng lúc.
   - Chấm kịch bản: `script_lint.py`, `qc_facts.py`, `qc_script.py` chạy cùng lúc trên cùng một bản; sửa xong mới chấm vòng sau.
   - Lúc đang tạo giọng đọc (`gen_voice.py`): chạy `check_assets.py <tập>` cho ảnh đã có, và viết sẵn `scene_plan.py` cho các cảnh không phụ thuộc mốc thời gian (bố cục, asset, bản đồ); chỉ `align_srt.py --apply` chờ srt.
   - Asset: `gen_assets.py --only ai` và `--only real` hai tiến trình riêng.
   - Đang render: viết meta, chương, thumbnail. Tập sau viết kịch bản trong lúc tập trước render hoặc QC.
   - Không chia `scenes.json` hay kịch bản theo chương cho nhiều agent viết rồi gộp: một người dựng cả video để nhịp, biến thể asset và giọng thống nhất.
   - `qc_video.py` và `precheck.py` tự chấm các bảng song song.
