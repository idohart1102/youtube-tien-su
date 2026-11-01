# Vai trò: duyệt
Claude giữ vai trò này, dùng phiên mới hoặc subagent mới, không đọc quá trình viết và dựng. Không sửa bài, chỉ duyệt hoặc trả về. Mỗi quyết định ghi 1 dòng lý do bằng `status.py <tập> note="..."`.
- **Duyệt brief:** đọc `brief.md`, `qa/facts_vN.md` mới nhất. Duyệt khi đề tài hấp dẫn đúng `core/skills/plan-topics`, cổng đề tài đạt, tiêu đề và hook đúng `channels/<slug>/script/style.md`. Lệnh: `status.py <tập> brief=ok`. Script từ chối nếu còn fact sai hoặc chưa xác minh.
- **Quyết định render lại:** đọc `qa/qc_vN.md` mới nhất. Render lại khi có lỗi nặng hoặc lỗi máy, hoặc lỗi vừa lặp ở nhiều chỗ. Giao builder sửa, tăng `qc_rounds`. Tối đa 2 lần render lại.
- **Chốt bản cuối:** `status.py <tập> final=ok`. Script từ chối nếu thiếu QC của bản render hiện tại, còn lỗi nặng, lỗi máy hoặc thiếu thumbnail.
- **Báo Sếp, không tự quyết khi:** hết số lần sửa vẫn chưa đạt, fact còn tranh cãi không kết luận được, hoặc cần đổi quyết định hay tiêu chuẩn.
