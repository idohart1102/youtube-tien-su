"""QC độc lập cho video đã render: AI không tham gia dựng đọc bảng khung hình, đối chiếu kịch bản và tiêu chuẩn, đề xuất sửa.
Dùng: python core/scripts/render_check.py <tập> rồi python core/scripts/qc_video.py <tập> (mỗi bản render 1 lượt; --force khi Sếp yêu cầu). Kết quả qa/qc_vN.md để approver quyết định có render lại không.
Chỉ chấm hình. Audio do Sếp gửi vào là đã duyệt, không QC âm thanh và nhịp đọc."""
import hashlib, json, re, sys
from pathlib import Path
from paths import ROOT
import channel as chan
import learn, review, status

ep = Path(sys.argv[1]).resolve()
qa = ep / "qa"
video = ep / "render" / "final.mp4"
if (qa / "render_check.json").stat().st_mtime < video.stat().st_mtime:
    sys.exit("Bảng khung hình là của bản render cũ. Chạy lại: python core/scripts/render_check.py <tập>")
if (ep / "scenes.json").exists() and (ep / "scenes.json").stat().st_mtime > video.stat().st_mtime:
    sys.exit("scenes.json đã sửa sau lần render cuối: video đang là bản cũ. Chạy produce.py tới khi render xong rồi mới QC")
rc = json.loads((qa / "render_check.json").read_text(encoding="utf-8"))
cfg = chan.load(ep)
rules = (ROOT / "core" / "standard" / "qc-video.md").read_text(encoding="utf-8")
tl = json.loads((ep / "timeline.json").read_text(encoding="utf-8")) if (ep / "timeline.json").exists() else {"lines": []}
TYPES = "; ".join(f"{k} ({v})" for k, v in learn.VIDEO_DEFECTS.items())
rows, summary = [], []
video_sha = status.file_sha(video)
done_qc = [q for q in qa.glob("qc_v*.md") if f"- Video: {video_sha}" in q.read_text(encoding="utf-8")]
if done_qc and "--force" not in sys.argv:  # Sếp 2026-11-03: mỗi bản render chỉ QC 1 lượt, không chấm lại để lấy điểm khác
    sys.exit(f"Bản render này đã có QC ({done_qc[0].name}). Dùng điểm đó để duyệt hoặc sửa rồi render bản mới. --force chỉ khi Sếp yêu cầu")
cache = qa / "qc_cache.json"  # lỗi giữa chừng thì chạy lại không chấm lại các bảng đã xong
def grade(name):
    k = int(re.search(r"(\d+)", name)[1])
    every = rc.get("every", 3.0)
    a, b = k * 20 * every, (k + 1) * 20 * every
    said = " ".join(f"[{l['start']:.0f}s] {l['text']}" for l in tl["lines"] if a - 5 <= l["start"] < b)[:3500]
    prompt = (f"{rules}\n\nChannel language: {cfg['language']}, country: {cfg['country']}. Video length: {rc['duration']:.0f} seconds. The video must not mention AI anywhere (no AI notice, no AI text); report any as cao.\nContact sheet covers {a:.0f}-{b:.0f} seconds, each cell has a timestamp.\n"
              f"Narration in this range: {said}\n"
              'Reply ONLY JSON: {"score":0-10,"issues":[{"severity":"cao|vừa|thấp","time":"m:ss","type":"loại lỗi","issue":"mô tả bằng tiếng Việt","fix":"cách sửa bằng tiếng Việt"}]}. '
              f"type must be exactly one of: {TYPES}, or khac if none fits. Only report what is visible. No praise. "
              "Report each distinct defect once: if the same defect shows in several cells, list it once and put all timestamps in time (e.g. 0:40, 0:43). "
              "Severity must follow the rule strictly; do not inflate or soften. score is only your impression, the final score is computed from the issue list.")
    r = review.ask_json_cached(cache, hashlib.sha256((prompt + status.file_sha(qa / name)).encode()).hexdigest(), prompt, [qa / name], edge=2400)
    print(name, r.get("score"), len(r.get("issues", [])), "lỗi")
    return r


# Điểm tính từ danh sách lỗi theo công thức cố định (Sếp 2026-11-03: QC 1 lượt, điểm phải ổn định).
# Mỗi bảng 1 phút video: 10 trừ 1,5 mỗi lỗi nặng, 0,5 mỗi lỗi vừa, 0,1 mỗi lỗi thấp. Còn lỗi nặng thì điểm cả video không quá 8,5.
PENALTY = {"cao": 1.5, "vừa": 0.5, "thấp": 0.1}


def sheet_score(issues):
    return max(0.0, 10 - sum(PENALTY.get(x.get("severity"), 0.5) for x in issues))


from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(4) as pool:  # các bảng độc lập (mỗi bảng 1 đoạn thời gian), chấm song song
    for r in pool.map(grade, rc["sheets"]):
        summary.append(sheet_score(r.get("issues", [])))
        rows += r.get("issues", [])
n = 1 + len(list(qa.glob("qc_v*.md")))
order = {"cao": 0, "vừa": 1, "thấp": 2}
rows.sort(key=lambda x: order.get(x.get("severity"), 3))
high = sum(1 for r in rows if r.get("severity") == "cao")
avg = round(sum(summary) / max(1, len(summary)), 1)
if high:
    avg = min(avg, 8.5)
lines = [f"# QC video lần {n}", f"- Video: {video_sha}", f"- Điểm khung hình trung bình: {avg}/10. Lỗi nặng: {high}. Tổng lỗi: {len(rows)}.",
         "- Điểm tính từ danh sách lỗi: mỗi phút video 10 điểm, trừ 1,5 mỗi lỗi nặng, 0,5 mỗi lỗi vừa, 0,1 mỗi lỗi thấp; còn lỗi nặng thì tối đa 8,5.",
         f"- Kiểm tra máy: {'; '.join(rc['problems']) or 'không có lỗi'}. {'; '.join(rc['notes'])}".rstrip(),
         f"- Đề xuất: {'render lại' if high or rc['problems'] or avg < 9 else 'không cần render lại'}. "
         f"{'Đủ điều kiện gửi Sếp duyệt (từ 9/10, không lỗi nặng, không lỗi máy).' if avg >= 9 and not high and not rc['problems'] else 'Chưa đủ điều kiện gửi Sếp duyệt: cần từ 9/10, không lỗi nặng, không lỗi máy.'}", "",
         "| Mức | Giây | Loại | Lỗi | Cách sửa |", "|---|---|---|---|---|"]
lines += [f"| {r.get('severity')} | {r.get('time')} | {r.get('type', '')} | {str(r.get('issue')).replace('|', '/')} | {str(r.get('fix')).replace('|', '/')} |" for r in rows]
(qa / f"qc_v{n}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
cache.unlink(missing_ok=True)
# Lỗi nặng, và lỗi vừa lặp từ 2 lần trong một video, thành bài học theo loại
cnt = {}
for r in rows:
    cnt[r.get("type")] = cnt.get(r.get("type"), 0) + 1
learn.record_defects(cfg, ep.name, "video", [learn.VIDEO_DEFECTS.get(r.get("type"), "") for r in rows
                                             if r.get("severity") == "cao" or (r.get("severity") == "vừa" and cnt[r.get("type")] >= 2)])
print(qa / f"qc_v{n}.md", "| lỗi nặng:", high)
