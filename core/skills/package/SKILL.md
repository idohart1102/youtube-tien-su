---
name: package
description: Hoàn thiện meta.md và ghép thumbnail cho tập đã render (chapters, kiểm SEO, thumbnail từ asset).
---
meta.md đã được write-script viết sẵn đủ 5 phần. Bước này chỉ hoàn thiện, không viết lại từ đầu.
- Điền mốc thời gian từng phần từ `chapters` trong timeline.json, đây là nguồn chuẩn. Mốc đầu luôn là 0:00.
- Kiểm lại: tiêu đề trùng dòng `#` đầu của storyboard.md; mỗi từ khoá chính xuất hiện ≥3 lần; đúng 3 hashtag; đúng 5 tag. Thiếu thì sửa.
- Nếu meta.md còn trống (tập cũ), viết đủ theo mục "Đầu ra" của core/skills/write-script/SKILL.md, chỉ đọc brief.md và các phần "Tiêu đề", "Thumbnail" của script/style.md.
- Thumbnail: sau khi render, ghép thumbnail từ asset của tập theo `core/standard/thumbnail.md` và `channels/<slug>/thumbnail.md`. Tạo ít nhất 3 phương án hook gây tò mò và đủ nghĩa khi chỉ nhìn thumbnail, ghép bằng `node core/scripts/thumb.mjs <tập> <spec.json>`, chọn thumbnail chính và dự phòng theo kết quả "người xem lạ chấm" trong `core/standard/thumbnail.md` (tác tử độc lập, không tự chấm). Có thể dùng vidIQ (`vidiq_youtube_search` theo từ khoá đề tài, sắp theo lượt xem) để tham khảo mẫu hook đang thắng. Dùng hook và ý tưởng đã có trong meta.md. Lưu `thumb/thumbnail.jpg` 1280x720, tự kiểm 5 mục rồi ghi kết quả vào meta.md. Chỉ tạo ảnh AI mới khi không có asset nào đạt.
- Luôn ghi "Made for kids: KHÔNG" cho kênh tài liệu. Ghi danh sách đăng cho Sếp theo `core/standard/thumbnail.md`, gồm mốc thời gian từng phần. Tiêu đề, mô tả, tag, chữ thumbnail không nhắc tới AI.
