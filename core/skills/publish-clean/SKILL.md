---
name: publish-clean
description: Tải video thành phẩm và gói nguồn lên Drive, đối chiếu checksum, rồi xóa media không còn dùng trên máy để repo và ổ cứng không phình. Dùng khi đã chốt bản cuối.
---
1. Chạy `python core/scripts/publish_clean.py <tập> --dry-run`, kiểm tra danh sách tải và xóa.
2. Vai trò approver chốt: `python core/scripts/status.py <tập> final=ok`. Script từ chối thì dừng.
3. Chạy `python core/scripts/publish_clean.py <tập>`. Script chỉ xóa `render/`, `audio/`, `assets/`, `thumb/`, `.cand/`, `asset_sheet.jpg` của đúng tập đó, sau khi Drive đã nhận và checksum khớp. File chữ giữ lại trên máy, bản sao lên Drive, không lên GitHub.
4. Mỗi tuần chạy `python core/scripts/publish_clean.py --expire`: xóa gói nguồn quá 30 ngày, video thành phẩm giữ nguyên.
5. Báo Sếp đường dẫn trên Drive, dung lượng đã giải phóng. Lỗi thì báo nguyên văn, không xóa tay.
