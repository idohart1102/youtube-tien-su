---
name: produce
description: Chạy pipeline phụ đề, render cho một tập đã có audio (do gen_voice.py tạo hoặc Sếp gửi). Chỉ chạy lệnh, không đọc source.
---
Chạy `python core/scripts/produce.py channels/<slug>/episodes/<tap>` để ra bản cuối (render/final.mp4) và kiểm tra máy. Tập chưa dựng cảnh thì dùng skill build-video. Chưa có `audio/voice.*` và `.srt`: kênh có mục `tts` trong `channel.yaml` thì chạy `python core/scripts/gen_voice.py <tap>`, kênh khác thì báo Sếp. `--no-subs` để tắt phụ đề. Kênh có mục `music` trong `channel.yaml` thì script tự chọn 1 bản trong kho và lặp hết video; đổi bản khác bằng `python core/scripts/pick_music.py <tap> --repick`.
- Cổng render (Sếp 2026-11-06): precheck 0 lỗi cao (trừ `qa/accepted.json`); lỗi vừa chỉ là nên sửa. Precheck sập (mã 3) thì không render. `--force --note "lý do"` chỉ approver dùng, tính vào trần render. Trần: 1 lần đầu + 2 lần render lại; chạm trần hoặc precheck 4 vòng chưa qua thì script ghi `can_sep` và dừng, báo Sếp. `--sep` chỉ khi Sếp nói rõ.
- Bản đầy đủ render theo đoạn, giữ ở `render/chunks/`: lần render lại chỉ render đoạn có thay đổi, nhanh hơn nhiều khi sửa vài cảnh.
- Nếu lỗi: chỉ đọc 20 dòng cuối của log. Chỉ mở đúng script báo lỗi, không mở cả thư mục.
- Không in log dài ra cho người dùng. Báo kết quả gồm đường dẫn file mp4 và thời lượng.
- Bản cuối dùng cấu hình chung `config/video-output.json`, theo `core/standard/video-output.md`, áp dụng từ tập 1 Denisova. Không ghi đè fps hoặc thông số mã hóa riêng theo tập. Kiểm tra sau render là bắt buộc: lỗi kỹ thuật hoặc lỗi máy thì lệnh dừng, không coi là bản đạt và không tự chạy lại để bỏ qua lỗi. Biên nhận `qa/encoding.json` và báo cáo `qa/render_check.json` phải khớp video, cấu hình và đầu vào hiện tại trước khi duyệt/bàn giao. Bản xem thử không thay thế bản cuối.
