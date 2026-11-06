"""Chấm kịch bản độc lập: AI không tham gia viết đọc brief, kịch bản, lớp 1 và DNA kênh, chấm cổng, điểm và đánh dấu câu nghe như AI hoặc như dịch.
Dùng: python core/scripts/qc_script.py <episode_dir> [--file ten.md] [--part] [--force]. Kết quả qa/script_vN.md, kèm bản đã chấm qa/snapshot_vN.md. Không sửa kịch bản.
Tối đa 5 vòng cho mỗi file (--force để chấm thêm khi Sếp yêu cầu). Xong thì: python core/scripts/qc_script.py <episode_dir> --use-best để lấy lại bản tốt nhất.
Nhà cung cấp theo review_provider trong config/machine.yaml. Không thay được người bản xứ: độ tự nhiên chỉ là đánh giá của AI.
Chấm lại có trọng tâm (Sếp 2026-11-05): từ vòng 2, sửa ≤ 20% số câu thì chỉ chấm câu đã sửa, câu liền kề và các cổng đã trượt;
cổng, tiêu chí và lỗi ở câu không đổi giữ kết quả vòng trước. Sửa > 20% thì chấm lại toàn bài (giữ kiểm nhịp, mạch). --full: luôn chấm toàn bài.
Chạm 5 vòng mà chưa đạt: status.yaml ghi can_sep để báo Sếp. Báo nhầm đã xét: qa/script_accepted.json (không chặn nữa). Fact sai hoặc chưa xác minh phải xử lý xong trước (status.require_brief chặn)."""
import json, shutil, sys
from pathlib import Path
import channel as chan
import learn, review, router, status
from paths import ROOT

ep = Path(sys.argv[1]).resolve()
fname = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "storyboard.md"
part = "--part" in sys.argv
MAX_ROUNDS, PASS_PCT = 5, 80  # Sếp nâng lên 5 vòng 2026-11-02
qa = ep / "qa"
qa.mkdir(exist_ok=True)
rows = [x for x in (json.loads(p.read_text(encoding="utf-8")) for p in qa.glob("script_v*.json")) if x["file"] == fname]


def report_best():
    b = review.best_round(rows)
    print(f"Bản tốt nhất: vòng {b['round']}, qa/snapshot_v{b['n']}.md, điểm {b['pct']:.0f}%, cổng trượt {b['gates_failed']}, lỗi fact {b['fact_errors']}")
    return b


if "--use-best" in sys.argv:
    if not rows:
        sys.exit("Chưa có vòng chấm nào")
    shutil.copy(qa / f"snapshot_v{report_best()['n']}.md", ep / fname)
    print(f"Đã chép bản tốt nhất vào {fname}. Xuất lại: python core/scripts/export_narration.py {ep}")
    sys.exit(0)
if len(rows) >= MAX_ROUNDS and "--force" not in sys.argv:
    report_best()
    sys.exit(f"Đã đủ {MAX_ROUNDS} vòng cho {fname}. Dùng --use-best, không chấm thêm nếu Sếp không yêu cầu.")
status.require_brief(ep)
cfg = chan.load(ep)
d = Path(cfg["_dir"]) / "script"
read = lambda p: Path(p).read_text(encoding="utf-8") if Path(p).exists() else ""
# Danh sách cổng cố định: cổng lớp 1 (mục 3 của tiêu chuẩn) + cổng mảng script trong criteria.yaml. AI phải trả đúng mã này.
import re
sec = re.search(r"^## 3\..*?(?=^## )", read(ROOT / "core/standard/script-standard.md"), re.M | re.S)
GATES = {f"L1-{m[1]}": m[2].strip() for m in re.finditer(r"^(\d+)\.\s+(.+)$", sec[0] if sec else "", re.M)}
GATES |= {m[1]: m[2] for m in re.finditer(r'id:\s*([\w-]+),\s*rule:\s*"([^"]+)".*?area:\s*script', read(ROOT / "core/standard/criteria.yaml"))}


def gate_rule(gid):
    """Mã cổng AI trả (có khi lệch: '1', 'L1-1', '1-fact-source') → bài học có nội dung cổng."""
    gid = str(gid).strip()
    key = gid if gid in GATES else next((k for k in GATES if not k.startswith("L1-") and k in gid), None)
    if not key and (m := re.match(r"(?:L1-)?(\d+)", gid)):
        key = f"L1-{m[1]}" if f"L1-{m[1]}" in GATES else None
    return f"Tránh trượt cổng {key}: {GATES[key]}" if key else ""


# Chấm lại có trọng tâm: so với bản đã chấm vòng trước
split = lambda text: [x.strip() for x in re.split(r"(?<=[.!?…])\s+|\n+", text) if len(x.strip()) > 1]
cur = split(read(ep / fname))
prev_row = max(rows, key=lambda x: x["n"], default=None)
prev_raw = json.loads(read(qa / f"script_v{prev_row['n']}.raw.json") or "null") if prev_row else None
focus = None
if prev_raw and "--full" not in sys.argv:
    old_list = split(read(qa / f"snapshot_v{prev_row['n']}.md"))
    old = set(old_list)
    changed = [i for i, x in enumerate(cur) if x not in old]
    removed = [x for x in old_list if x not in set(cur)]
    kept = [x for x in cur if x in old]
    reordered = kept != [x for x in old_list if x in set(cur)]
    # Câu xóa cũng tính là thay đổi; xóa nhiều hoặc đổi thứ tự thì chấm lại toàn bài
    if (len(changed) + len(removed)) <= 0.2 * max(1, len(cur), len(old_list)) and not reordered:
        near = sorted({j for i in changed for j in (i - 1, i, i + 1) if 0 <= j < len(cur)})
        failed = [g.get("id") for g in prev_raw.get("gates", []) if g.get("ket_qua") == "truot"]
        focus = {"near": [cur[j] for j in near], "changed": [cur[i] for i in changed], "failed": failed}
focus_txt = ""
if focus:
    focus_txt = ("\nVÒNG CHẤM LẠI CÓ TRỌNG TÂM: kịch bản đã chấm vòng trước, chỉ sửa " + str(len(focus["changed"])) + "/" + str(len(cur)) + " câu.\n"
                 "Chấm kỹ: (a) các câu dưới đây (câu đã sửa và câu liền kề), (b) các cổng đã trượt vòng trước: " + (", ".join(focus["failed"]) or "không có") + ".\n"
                 "Trong gates vẫn trả ĐỦ mọi cổng cho cả bài (cổng đạt vòng trước xét nhanh xem còn đạt không). Trong tieu_chi chỉ trả dòng checklist bị ảnh hưởng bởi các câu ở (a). fact_loi và cau_khong_tu_nhien chỉ xét câu ở (a).\n"
                 "Các câu cần chấm:\n" + "\n".join("- " + x for x in focus["near"]) + "\n")

prompt = f"""Bạn là người chấm độc lập, không tham gia viết kịch bản. Kênh tiếng {cfg['language']}, nước {cfg['country']}. Trả lời bằng tiếng Việt, từ nước ngoài có nghĩa tiếng Việt bên cạnh.
{"Đây chỉ là một đoạn của kịch bản: chấm phần có mặt, tiêu chí chưa tới thì ghi na." if part else ""}
Việc phải làm:
1. Chấm từng cổng: dat hoặc truot. Trường id ghi đúng một mã trong danh sách sau, không tự đặt mã khác: {"; ".join(f"{k} = {v}" for k, v in GATES.items())}.
2. Chấm từng dòng checklist, 5 điểm mỗi dòng, ghi na nếu chưa tới.
3. Đối chiếu từng con số và mệnh đề khoa học với bảng fact trong brief. Không có trong brief là lỗi.
4. Đọc từng câu như người bản xứ đang nghe. Liệt kê câu nghe như AI viết hoặc như dịch, nói vì sao, đề xuất câu thay giữ nguyên nghĩa khoa học. Không bắt bẻ câu đã tự nhiên.
Video không dùng thẻ Tái hiện theo quyết định của chủ kênh, đừng báo thiếu thẻ này. Tiêu đề do chủ kênh duyệt có thể nói theo cách thông dụng; chỉ báo nếu video không làm rõ phạm vi. Chỉ báo điều có thật trong văn bản, không khen. Trả lời ONLY JSON:
{{"gates":[{{"id":"","ket_qua":"dat|truot","ly_do":""}}],"diem":0,"diem_toi_da":0,"tieu_chi":[{{"so":0,"diem":"0-5 hoặc na","ly_do":""}}],"fact_loi":[{{"cau":"","van_de":""}}],"cau_khong_tu_nhien":[{{"cau":"","vi_sao":"","cau_thay":""}}],"tong_ket":""}}

=== TIÊU CHUẨN LỚP 1 ===
{read(ROOT / "core/standard/script-standard.md")}
=== CHUẨN CHÍNH XÁC ===
{read(ROOT / "core/standard/accuracy.md")}
=== CỔNG THEO MẢNG (chỉ xét area: script) ===
{read(ROOT / "core/standard/criteria.yaml")}
=== DNA ===
{read(d / "dna.yaml")}
=== KIM CHỈ NAM (nguyên tắc, không phải cổng; chỉ trừ điểm khi vi phạm làm hại câu chuyện) ===
{read(d / "guide.md")}
=== STYLE ===
{read(d / "style.md")}
=== NGÔN NGỮ ===
{read(d / "lang.md")}
=== CHECKLIST ===
{read(d / "qa-checklist.md")}
=== BRIEF ===
{read(ep / "brief.md")}
=== KỊCH BẢN ({fname}) ===
{read(ep / fname)}
{focus_txt}"""
r = router.json_in(review.ask_text(prompt))
raw = r
if focus:  # ghép với kết quả vòng trước: phần không chấm lại giữ nguyên
    gates = {g.get("id"): g for g in prev_raw.get("gates", [])}
    gates.update({g.get("id"): g for g in r.get("gates", [])})
    crit = {str(x.get("so")): x for x in prev_raw.get("tieu_chi", [])}
    crit.update({str(x.get("so")): x for x in r.get("tieu_chi", [])})
    bare = lambda t: re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", "", str(t))).strip()
    import difflib
    cur_b = [bare(c) for c in cur]
    near_set = set(bare(c) for c in focus["near"])
    units = cur_b + [a + " " + b for a, b in zip(cur_b, cur_b[1:])]  # AI hay trích gộp 2 câu

    def keep(xs):
        """Lỗi cũ còn hiệu lực khi câu bị trích vẫn còn nguyên trong bài và không nằm trong các câu vừa chấm lại.
        Câu đã sửa hoặc đã xóa thì lỗi cũ bỏ (câu mới đã được chấm lại); so gần đúng vì AI hay trích bỏ thẻ [F..]."""
        out = []
        for x in xs:
            q = bare(x.get("cau"))
            if not q:
                continue
            best = max(units, key=lambda u: difflib.SequenceMatcher(None, q, u).ratio(), default="")
            if best and difflib.SequenceMatcher(None, q, best).ratio() >= 0.85 and not any(p and p in best for p in near_set):
                out.append(x)
        return out
    nums = [float(x["diem"]) for x in crit.values() if str(x.get("diem")).replace(".", "", 1).isdigit()]
    r = {"gates": list(gates.values()), "tieu_chi": list(crit.values()), "diem": sum(nums), "diem_toi_da": 5 * len(nums),
         "fact_loi": keep(prev_raw.get("fact_loi", [])) + r.get("fact_loi", []),
         "cau_khong_tu_nhien": keep(prev_raw.get("cau_khong_tu_nhien", [])) + r.get("cau_khong_tu_nhien", []),
         "tong_ket": f"Chấm lại có trọng tâm ({len(focus['changed'])} câu sửa, {len(focus['near'])} câu chấm). " + str(r.get("tong_ket", ""))}
# Báo nhầm đã xét (reviewer hoặc approver ghi, kèm lý do): qa/script_accepted.json
# [{"gate": "L1-3", "reason": "..."}] hoặc [{"fact": "đoạn câu bị báo", "reason": "..."}]. Lỗi fact thật vẫn chặn.
acc = json.loads(read(qa / "script_accepted.json") or "[]")
acc_gates = {a["gate"] for a in acc if a.get("gate")}
acc_facts = [a["fact"] for a in acc if a.get("fact")]
r["fact_loi"] = [x for x in r.get("fact_loi", []) if not any(f in str(x.get("cau", "")) for f in acc_facts)]
n = 1 + len(list(qa.glob("script_v*.md")))
bad = [g for g in r.get("gates", []) if g.get("ket_qua") == "truot" and g.get("id") not in acc_gates]
L = [f"# Chấm kịch bản lần {n}: {fname}", f"- Điểm: {r.get('diem')}/{r.get('diem_toi_da')}. Cổng trượt: {len(bad)}. Lỗi fact: {len(r.get('fact_loi', []))}. Câu không tự nhiên: {len(r.get('cau_khong_tu_nhien', []))}.", f"- {r.get('tong_ket', '')}", "- Độ tự nhiên là đánh giá của AI, chưa được người bản xứ xác nhận.", "", "## Cổng"]
L += [f"- {g.get('ket_qua')}: {g.get('id')}. {g.get('ly_do', '')}" for g in r.get("gates", [])]
L += ["", "## Lỗi fact"] + [f"- {x.get('cau')}: {x.get('van_de')}" for x in r.get("fact_loi", [])]
L += ["", "## Câu không tự nhiên"] + [f"- {x.get('cau')} | {x.get('vi_sao')} | Đề xuất: {x.get('cau_thay')}" for x in r.get("cau_khong_tu_nhien", [])]
L += ["", "## Tiêu chí"] + [f"- {x.get('so')}: {x.get('diem')}. {x.get('ly_do', '')}" for x in r.get("tieu_chi", [])]
out = qa / f"script_v{n}.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
learn.record_defects(cfg, ep.name, "script", [gate_rule(g.get("id", "")) for g in bad])
shutil.copy(ep / fname, qa / f"snapshot_v{n}.md")
try:
    pct = float(r.get("diem") or 0) / max(float(r.get("diem_toi_da") or 0), 1) * 100
except (TypeError, ValueError):
    pct = 0.0
row = {"n": n, "round": len(rows) + 1, "file": fname, "pct": pct, "gates_failed": len(bad), "fact_errors": len(r.get("fact_loi", [])), "unnatural": len(r.get("cau_khong_tu_nhien", []))}
(qa / f"script_v{n}.json").write_text(json.dumps(row, ensure_ascii=False, indent=1), encoding="utf-8")
(qa / f"script_v{n}.raw.json").write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
rows.append(row)
passed = not bad and not row["fact_errors"] and pct >= PASS_PCT
print(out, "| vòng", row["round"], "/", MAX_ROUNDS, "| điểm", r.get("diem"), "/", r.get("diem_toi_da"), "| cổng trượt", len(bad), "| lỗi fact", row["fact_errors"], "|", "ĐẠT" if passed else "CẦN SỬA")
if passed or row["round"] >= MAX_ROUNDS:
    report_best()
if not passed and row["round"] >= MAX_ROUNDS:
    st = status.read(ep)
    st["can_sep"] = f"kịch bản {fname} đã {MAX_ROUNDS} vòng chưa đạt (cổng trượt {len(bad)}, lỗi fact {row['fact_errors']}), xem {out.name}"
    status.write(ep, st)
    print("Chạm 5 vòng: DỪNG, báo Sếp kèm lỗi và đề xuất (status.yaml ghi can_sep)")
