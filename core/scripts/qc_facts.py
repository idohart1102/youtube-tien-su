"""Kiểm tra bảng fact trong brief bằng tìm web, trước khi Sếp duyệt brief: nguồn có thật không, có nói đúng mệnh đề đó không.
Dùng: python core/scripts/qc_facts.py <episode_dir> [--force]. Kết quả qa/facts_vN.md và qa/facts_vN.json. Không sửa brief.
Tối đa 3 lần cho mỗi tập (--force khi Sếp yêu cầu). Sửa bảng fact thì phải chạy lại, status.py mới nhận brief=ok.
Nhà cung cấp theo review_provider trong config/machine.yaml, có tự chuyển sang bên còn lại khi lỗi."""
import json, re, sys
from pathlib import Path
import review, router, status

MAX_ROUNDS, TRIES = 3, 3
ep = Path(sys.argv[1]).resolve()
brief = ep / "brief.md"
if not brief.exists():
    sys.exit("Chưa có brief.md")
section = status.facts_section(brief.read_text(encoding="utf-8"))
rows = [l for l in section.splitlines() if l.startswith("|")][2:]
rows = [l for l in rows if re.sub(r"[|\s-]", "", l)]
if not rows:
    sys.exit("Bảng 'Fact và nguồn' trong brief.md còn trống")
qa = ep / "qa"
qa.mkdir(exist_ok=True)
n = 1 + len(list(qa.glob("facts_v*.json")))
if n > MAX_ROUNDS and "--force" not in sys.argv:
    sys.exit(f"Đã đủ {MAX_ROUNDS} lần kiểm tra. Báo Sếp các fact còn lại, không chạy thêm nếu Sếp không yêu cầu.")

ids = [f"F{i}" for i in range(1, len(rows) + 1)]
numbered = "\n".join(f"{i}: {l}" for i, l in zip(ids, rows))
prompt = f"""Bạn là người kiểm tra fact độc lập, không tham gia viết brief. Dùng tìm web cho TỪNG dòng trong bảng dưới ({len(rows)} dòng), không dựa vào trí nhớ.
Với mỗi dòng, xác định: nguồn ghi trong bảng có thật không; nguồn hoặc tài liệu khoa học khác có nói đúng mệnh đề đó không; mức chắc chắn ghi trong bảng có hợp lý không.
ket_qua chỉ được là: dung (đã thấy tài liệu xác nhận), sai (mệnh đề, con số, nguồn hoặc mức chắc chắn sai), chua_xac_minh (không tìm được tài liệu để kết luận).
Không suy đoán. Ghi chú bằng tiếng Việt. Mỗi mã F một dòng kết quả, đủ tất cả các mã. Trả lời ONLY JSON:
{{"facts":[{{"id":"F1","menh_de":"","ket_qua":"dung|sai|chua_xac_minh","ghi_chu":"","nguon_tim_thay":"URL"}}],"tong_ket":""}}

{numbered}"""

for attempt in range(TRIES):
    try:
        r = router.json_in(review.ask_web(prompt))
        facts = review.check_facts(r, ids)
        break
    except ValueError as e:
        if attempt == TRIES - 1:
            sys.exit(f"Không kiểm tra được: {e}")

count = {k: sum(1 for f in facts if f.get("ket_qua") == k) for k in ("dung", "sai", "chua_xac_minh")}
L = [f"# Kiểm tra fact lần {n}", f"- Đúng: {count['dung']}. Sai: {count['sai']}. Chưa xác minh: {count['chua_xac_minh']}.", f"- {r.get('tong_ket', '')}", "",
     "| Kết quả | Mệnh đề | Ghi chú | Nguồn tìm thấy |", "|---|---|---|---|"]
order = {"sai": 0, "chua_xac_minh": 1, "dung": 2}
for f in sorted(facts, key=lambda x: order.get(x.get("ket_qua"), 3)):
    L.append("| " + " | ".join(str(f.get(k, "")).replace("|", "/") for k in ("ket_qua", "menh_de", "ghi_chu", "nguon_tim_thay")) + " |")
(qa / f"facts_v{n}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
row = {"n": n, "sha": status.facts_sha(ep), "tong": len(facts), **count}
(qa / f"facts_v{n}.json").write_text(json.dumps(row, ensure_ascii=False, indent=1), encoding="utf-8")
print(qa / f"facts_v{n}.md", "| đúng", count["dung"], "| sai", count["sai"], "| chưa xác minh", count["chua_xac_minh"])
