"""Kiểm tra bảng fact trong brief bằng tìm web, trước khi Sếp duyệt brief: nguồn có thật không, có nói đúng mệnh đề đó không.
Dùng: python core/scripts/qc_facts.py <episode_dir> [--force] [--all]. Kết quả qa/facts_vN.md và qa/facts_vN.json. Không sửa brief.
Mã fact cố định theo số đầu dòng ("12. ..." là F12, giống script_lint), xóa dòng không làm đổi mã các dòng khác.
Chỉ kiểm lại dòng mới hoặc đã sửa (cache qa/facts_cache.json theo nội dung dòng); --all kiểm lại cả bảng.
Gửi theo lô BATCH dòng để không quá giờ. Tối đa 3 lần cho mỗi tập (--force khi Sếp yêu cầu).
Sửa bảng fact thì phải chạy lại, status.py mới nhận brief=ok.
Nhà cung cấp theo review_provider trong config/machine.yaml, có tự chuyển sang bên còn lại khi lỗi."""
import hashlib, json, re, sys
from pathlib import Path
import review, router, status

MAX_ROUNDS, TRIES, BATCH, WARN_ROWS = 3, 3, 30, 60
ep = Path(sys.argv[1]).resolve()
brief = ep / "brief.md"
if not brief.exists():
    sys.exit("Chưa có brief.md")
section = status.facts_section(brief.read_text(encoding="utf-8"))
rows = [l for l in section.splitlines() if l.startswith("|")][2:]
rows = [l.strip() for l in rows if re.sub(r"[|\s-]", "", l)]
if not rows:
    sys.exit("Bảng 'Fact và nguồn' trong brief.md còn trống")
qa = ep / "qa"
qa.mkdir(exist_ok=True)
n = 1 + len(list(qa.glob("facts_v*.json")))
if n > MAX_ROUNDS and "--force" not in sys.argv:
    sys.exit(f"Đã đủ {MAX_ROUNDS} lần kiểm tra. Báo Sếp các fact còn lại, không chạy thêm nếu Sếp không yêu cầu.")
if len(rows) > WARN_ROWS:
    print(f"Cảnh báo: bảng fact {len(rows)} dòng (nên ≤{WARN_ROWS}); bỏ fact không cần cho câu chuyện.")

ids = []
for i, l in enumerate(rows, 1):
    m = re.match(r"\|\s*(\d+)\.", l)
    ids.append(f"F{m[1]}" if m else f"F{i}")
dup = sorted({x for x in ids if ids.count(x) > 1})
if dup:
    sys.exit(f"Trùng mã fact {', '.join(dup)}: mỗi dòng một số đầu dòng riêng")

key = lambda l: hashlib.sha256(re.sub(r"\s+", " ", l).encode()).hexdigest()[:16]
cache_path = qa / "facts_cache.json"
cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
todo = [(i, l) for i, l in zip(ids, rows) if "--all" in sys.argv or key(l) not in cache]

PROMPT = """Bạn là người kiểm tra fact độc lập, không tham gia viết brief. Dùng tìm web cho TỪNG dòng trong bảng dưới ({k} dòng), không dựa vào trí nhớ.
Với mỗi dòng, xác định: nguồn ghi trong bảng có thật không; nguồn hoặc tài liệu khoa học khác có nói đúng mệnh đề đó không (đúng con số, đúng phạm vi, giữ điều kiện của nguồn); mức chắc chắn ghi trong bảng có hợp lý không. Dòng có câu trích nguyên văn thì đối chiếu câu trích với nguồn trước.
ket_qua chỉ được là: dung (đã thấy tài liệu xác nhận), sai (mệnh đề, con số, nguồn hoặc mức chắc chắn sai), chua_xac_minh (không tìm được tài liệu để kết luận).
Không suy đoán. Ghi chú bằng tiếng Việt; dòng sai hoặc chưa xác minh thì ghi chú nêu cách sửa cụ thể (đổi chữ gì, nguồn nào). Mỗi mã F một dòng kết quả, đủ tất cả các mã. Trả lời ONLY JSON:
{{"facts":[{{"id":"F1","menh_de":"","ket_qua":"dung|sai|chua_xac_minh","ghi_chu":"","nguon_tim_thay":"URL"}}],"tong_ket":""}}

{body}"""

summaries = []
for s in range(0, len(todo), BATCH):
    part = todo[s:s + BATCH]
    pids = [i for i, _ in part]
    prompt = PROMPT.format(k=len(part), body="\n".join(f"{i}: {l}" for i, l in part))
    for attempt in range(TRIES):
        try:
            r = router.json_in(review.ask_web(prompt))
            got = review.check_facts(r, pids)
            break
        except ValueError as e:
            if attempt == TRIES - 1:
                sys.exit(f"Không kiểm tra được lô {pids[0]}-{pids[-1]}: {e}")
    summaries.append(r.get("tong_ket", ""))
    by_id = {str(f["id"]): f for f in got}
    for i, l in part:
        cache[key(l)] = {k: v for k, v in by_id[i].items() if k != "id"}
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

new = {i for i, _ in todo}
facts = [{"id": i, **cache[key(l)], "moi": i in new} for i, l in zip(ids, rows)]
count = {k: sum(1 for f in facts if f.get("ket_qua") == k) for k in ("dung", "sai", "chua_xac_minh")}
L = [f"# Kiểm tra fact lần {n}", f"- Đúng: {count['dung']}. Sai: {count['sai']}. Chưa xác minh: {count['chua_xac_minh']}. Kiểm mới {len(new)}/{len(facts)} dòng, còn lại lấy kết quả cũ (dòng không đổi).",
     *(f"- {x}" for x in summaries if x), "",
     "| Mã | Kết quả | Mệnh đề | Ghi chú | Nguồn tìm thấy |", "|---|---|---|---|---|"]
order = {"sai": 0, "chua_xac_minh": 1, "dung": 2}
for f in sorted(facts, key=lambda x: order.get(x.get("ket_qua"), 3)):
    L.append(f"| {f['id']}{'' if f['moi'] else ' (cũ)'} | " + " | ".join(str(f.get(k, "")).replace("|", "/") for k in ("ket_qua", "menh_de", "ghi_chu", "nguon_tim_thay")) + " |")
(qa / f"facts_v{n}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
row = {"n": n, "sha": status.facts_sha(ep), "tong": len(facts), "kiem_moi": len(new), **count}
(qa / f"facts_v{n}.json").write_text(json.dumps(row, ensure_ascii=False, indent=1), encoding="utf-8")
print(qa / f"facts_v{n}.md", "| đúng", count["dung"], "| sai", count["sai"], "| chưa xác minh", count["chua_xac_minh"], "| kiểm mới", len(new))
