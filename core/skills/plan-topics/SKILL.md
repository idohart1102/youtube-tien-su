---
name: plan-topics
description: Chọn đề tài tiếp theo cho một kênh và viết brief.md. Dùng khi cần tập mới.
---
1. Đọc `channels/<slug>/backlog.csv` (chỉ các dòng status=todo) và `learnings.md`.
2. Đề tài phải hấp dẫn, không nhàm chán: có một câu hỏi khiến người xem muốn biết ngay, có một trung tâm cụ thể nhìn thấy được (người, sinh vật, hiện vật, vùng đất, biến cố, hoặc nghịch lý neo vào vật hay nơi có thật), có tình huống căng và điều bất ngờ. Đề tài chỉ kể lại kiến thức sách giáo khoa thì bỏ, dù trụ cột đang thiếu. Chọn đề tài có score cao nhất. Không chọn trùng trụ cột với 2 tập gần nhất, trừ khi learnings.md nói trụ cột đó đang thắng.
2b. Tiêu đề chính là đề tài, làm trước brief:
   - Tìm điều lạ có thật của đề (con số, nghịch lý, điều đảo niềm tin, điều chạm thẳng khán giả) và đưa nó vào chữ. Nêu chủ đề hay hiện vật suông là chưa đạt.
   - Mỗi đề viết 3-4 phương án khác cơ chế, kiểm độ dài trước khi gửi chấm.
   - Chấm 2 cổng tách nhau: đúng fact (9router có tìm web) và sức kéo click. Người chấm chỉ được đề xuất bản mạnh hơn, không đề xuất bản an toàn, nhạt hơn.
   - vidIQ `score_title` chỉ tham khảo, mức đạt theo `style.md` của kênh. Nó thưởng câu hỏi chứa từ khóa, phạt câu khẳng định gây sốc, nên đối chiếu thêm outlier thật cùng ngách, cùng ngôn ngữ; không tối ưu theo một mình nó.
   - Sếp chốt bằng cảm nhận. Hai thang chấm mâu thuẫn lặp lại thì dừng hỏi Sếp, không đốt thêm credit.
   - Xếp thứ tự đăng: không trùng trụ cột 2 tập liền, đề mạnh nhất lên đầu, tránh nhiều tiêu đề liền nhau cùng một kiểu mở đầu.
   - Chỗ tiêu đề dùng ẩn dụ, suy luận hoặc số làm tròn ghi thành dòng trong bảng fact của brief.
3. Chạy `python core/scripts/new_episode.py <slug> <ten-ngan>` rồi điền đủ brief.md theo khung, không viết thừa. Mỗi dòng bảng fact ghi rõ phạm vi (ai hoặc loài, ở đâu, mẫu nào, thời gian) và mức chắc chắn, để người viết không nói rộng hơn nguồn (tập 1 trượt cổng fact 7 vòng vì nói rộng phạm vi). Phép so sánh quy đổi và quan hệ địa lý, thời gian định dùng (giáp nhau, gần nhau, cùng thời, to bằng vật quen) cũng ghi thành dòng trong bảng fact để `qc_facts` kiểm.
   Nghiên cứu fact trước, viết sau (bản 2.0):
   - Mỗi dòng bắt đầu bằng số cố định ("12. ..." là [F12]). Bỏ dòng thì giữ nguyên số các dòng khác, dòng mới lấy số tiếp theo.
   - Cột Nguồn ghi tác giả, năm, DOI hoặc URL, trang hoặc hình, kèm câu trích ngắn nguyên văn trong ngoặc kép. Mở bản gốc; không lấy số qua Wikipedia hay bài trích lại.
   - Giữ nguyên điều kiện của nguồn (mẫu nào, tuổi, "thường" chứ không phải "luôn"). Khoảng cách neo vào tọa độ công khai của hai địa danh có tên, không tự đo.
   - Tối đa khoảng 60 dòng. Chỉ giữ fact dùng trong câu chuyện.
4. Ghi nhân vật chính và ngày đăng dự kiến: `python core/scripts/status.py <tập> species=<tên> publish_date=YYYY-MM-DD`. Bị từ chối vì trùng nhân vật thì đổi đề tài.
5. Chạy `python core/scripts/qc_facts.py <tập>`, sửa bảng fact theo `qa/facts_vN.md`, tối đa 3 lần. Lần sau chỉ kiểm lại dòng đã sửa; dòng sai mà không sửa chữ thì giữ kết quả cũ, nên sửa hoặc bỏ dòng đó. Rồi giao vai trò approver duyệt brief. Hết 3 lần vẫn còn fact sai hoặc chưa xác minh thì báo Sếp.
6. Đổi status của đề tài trong backlog.csv thành `doing`.
Không chọn nhân vật chính đã có trong `no_repeat_species` video gần nhất (`species` trong status.yaml). Chỉ khi backlog còn dưới 10 dòng todo mới mở `channels/<slug>/research/` (cache) để bổ sung. Gọi vidIQ chỉ khi cache cũ hơn 30 ngày, kết quả lưu vào `channels/<slug>/research/` có ngày.
