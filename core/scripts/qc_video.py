"""QC độc lập cho video đã render: AI không tham gia dựng đọc bảng khung hình, đối chiếu kịch bản và tiêu chuẩn, đề xuất sửa.
Dùng: python core/scripts/render_check.py <tập> rồi python core/scripts/qc_video.py <tập>. Kết quả qa/qc_vN.md để approver quyết định có render lại không.
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
rc = json.loads((qa / "render_check.json").read_text(encoding="utf-8"))
cfg = chan.load(ep)
rules = (ROOT / "core" / "standard" / "qc-video.md").read_text(encoding="utf-8")
tl = json.loads((ep / "timeline.json").read_text(encoding="utf-8")) if (ep / "timeline.json").exists() else {"lines": []}
rows, summary = [], []
video_sha = status.file_sha(video)
cache = qa / "qc_cache.json"  # lỗi giữa chừng thì chạy lại không chấm lại các bảng đã xong
for name in rc["sheets"]:
    k = int(re.search(r"(\d+)", name)[1])
    every = rc.get("every", 3.0)
    a, b = k * 20 * every, (k + 1) * 20 * every
    said = " ".join(f"[{l['start']:.0f}s] {l['text']}" for l in tl["lines"] if a - 5 <= l["start"] < b)[:3500]
    prompt = (f"{rules}\n\nChannel language: {cfg['language']}, country: {cfg['country']}. Video length: {rc['duration']:.0f} seconds, so the AI notice is correct from {rc['duration'] - 4:.0f} seconds on.\nContact sheet covers {a:.0f}-{b:.0f} seconds, each cell has a timestamp.\n"
              f"Narration in this range: {said}\n"
              'Reply ONLY JSON: {"score":0-10,"issues":[{"severity":"cao|vừa|thấp","time":"m:ss","issue":"mô tả bằng tiếng Việt","fix":"cách sửa bằng tiếng Việt"}]}. Only report what is visible. No praise.')
    r = review.ask_json_cached(cache, hashlib.sha256((prompt + status.file_sha(qa / name)).encode()).hexdigest(), prompt, [qa / name], edge=2400)
    summary.append(r.get("score", 0))
    rows += r.get("issues", [])
    print(name, r.get("score"), len(r.get("issues", [])), "lỗi")
n = 1 + len(list(qa.glob("qc_v*.md")))
order = {"cao": 0, "vừa": 1, "thấp": 2}
rows.sort(key=lambda x: order.get(x.get("severity"), 3))
high = sum(1 for r in rows if r.get("severity") == "cao")
avg = round(sum(summary) / max(1, len(summary)), 1)
lines = [f"# QC video lần {n}", f"- Video: {video_sha}", f"- Điểm khung hình trung bình: {avg}/10. Lỗi nặng: {high}. Tổng lỗi: {len(rows)}.",
         f"- Kiểm tra máy: {'; '.join(rc['problems']) or 'không có lỗi'}. {'; '.join(rc['notes'])}".rstrip(),
         f"- Đề xuất: {'render lại' if high or rc['problems'] else 'không cần render lại'}.", "",
         "| Mức | Giây | Lỗi | Cách sửa |", "|---|---|---|---|"]
lines += [f"| {r.get('severity')} | {r.get('time')} | {str(r.get('issue')).replace('|', '/')} | {str(r.get('fix')).replace('|', '/')} |" for r in rows]
(qa / f"qc_v{n}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
cache.unlink(missing_ok=True)
learn.record_defects(cfg, ep.name, "video", [r.get("issue", "") for r in rows if r.get("severity") == "cao"])
print(qa / f"qc_v{n}.md", "| lỗi nặng:", high)
