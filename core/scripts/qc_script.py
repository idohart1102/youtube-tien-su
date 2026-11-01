"""Chấm kịch bản độc lập: AI không tham gia viết đọc brief, kịch bản, lớp 1 và DNA kênh, chấm cổng, điểm và đánh dấu câu nghe như AI hoặc như dịch.
Dùng: python core/scripts/qc_script.py <episode_dir> [--file ten.md] [--part] [--force]. Kết quả qa/script_vN.md, kèm bản đã chấm qa/snapshot_vN.md. Không sửa kịch bản.
Tối đa 3 vòng cho mỗi file (--force để chấm thêm khi Sếp yêu cầu). Xong thì: python core/scripts/qc_script.py <episode_dir> --use-best để lấy lại bản tốt nhất.
Nhà cung cấp theo review_provider trong config/machine.yaml. Không thay được người bản xứ: độ tự nhiên chỉ là đánh giá của AI."""
import json, shutil, sys
from pathlib import Path
import channel as chan
import learn, review, router, status
from paths import ROOT

ep = Path(sys.argv[1]).resolve()
fname = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "storyboard.md"
part = "--part" in sys.argv
MAX_ROUNDS, PASS_PCT = 3, 80
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
prompt = f"""Bạn là người chấm độc lập, không tham gia viết kịch bản. Kênh tiếng {cfg['language']}, nước {cfg['country']}. Trả lời bằng tiếng Việt, từ nước ngoài có nghĩa tiếng Việt bên cạnh.
{"Đây chỉ là một đoạn của kịch bản: chấm phần có mặt, tiêu chí chưa tới thì ghi na." if part else ""}
Việc phải làm:
1. Chấm từng cổng ở mục 3 của tiêu chuẩn: dat hoặc truot.
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
"""
r = router.json_in(review.ask_text(prompt))
n = 1 + len(list(qa.glob("script_v*.md")))
bad = [g for g in r.get("gates", []) if g.get("ket_qua") == "truot"]
L = [f"# Chấm kịch bản lần {n}: {fname}", f"- Điểm: {r.get('diem')}/{r.get('diem_toi_da')}. Cổng trượt: {len(bad)}. Lỗi fact: {len(r.get('fact_loi', []))}. Câu không tự nhiên: {len(r.get('cau_khong_tu_nhien', []))}.", f"- {r.get('tong_ket', '')}", "- Độ tự nhiên là đánh giá của AI, chưa được người bản xứ xác nhận.", "", "## Cổng"]
L += [f"- {g.get('ket_qua')}: {g.get('id')}. {g.get('ly_do', '')}" for g in r.get("gates", [])]
L += ["", "## Lỗi fact"] + [f"- {x.get('cau')}: {x.get('van_de')}" for x in r.get("fact_loi", [])]
L += ["", "## Câu không tự nhiên"] + [f"- {x.get('cau')} | {x.get('vi_sao')} | Đề xuất: {x.get('cau_thay')}" for x in r.get("cau_khong_tu_nhien", [])]
L += ["", "## Tiêu chí"] + [f"- {x.get('so')}: {x.get('diem')}. {x.get('ly_do', '')}" for x in r.get("tieu_chi", [])]
out = qa / f"script_v{n}.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
learn.record_defects(cfg, ep.name, "script", [g.get("id", "") for g in bad])
shutil.copy(ep / fname, qa / f"snapshot_v{n}.md")
try:
    pct = float(r.get("diem") or 0) / max(float(r.get("diem_toi_da") or 0), 1) * 100
except (TypeError, ValueError):
    pct = 0.0
row = {"n": n, "round": len(rows) + 1, "file": fname, "pct": pct, "gates_failed": len(bad), "fact_errors": len(r.get("fact_loi", [])), "unnatural": len(r.get("cau_khong_tu_nhien", []))}
(qa / f"script_v{n}.json").write_text(json.dumps(row, ensure_ascii=False, indent=1), encoding="utf-8")
rows.append(row)
passed = not bad and not row["fact_errors"] and pct >= PASS_PCT
print(out, "| vòng", row["round"], "/", MAX_ROUNDS, "| điểm", r.get("diem"), "/", r.get("diem_toi_da"), "| cổng trượt", len(bad), "| lỗi fact", row["fact_errors"], "|", "ĐẠT" if passed else "CẦN SỬA")
if passed or row["round"] >= MAX_ROUNDS:
    report_best()
