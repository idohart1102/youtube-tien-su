"""Panel khán giả giả lập: mỗi chân dung trong channels/<slug>/script/panel.yaml "xem" kịch bản như người xem thật và nói lúc nào bỏ đi, câu nào hay, câu nào nghe như AI.
Khác qc_script.py: panel KHÔNG đọc quy chuẩn, chỉ đọc tiêu đề, chữ thumbnail và lời đọc có mốc thời gian ước lượng. Đây là mô phỏng, không phải số liệu thật.
Dùng: python core/scripts/panel_script.py <episode_dir> [--file storyboard.md] [--force] [--channel <slug>] [--part].
--channel: chấm thư mục ngoài kênh (vd nháp trong scratchpad). --part: chỉ là một đoạn (vd đoạn mở), panel chấm như nghe đoạn đó, không hỏi rời đi lúc nào cả video. Kết quả qa/panel_vN.md + qa/panel_vN.json. Tối đa 5 vòng mỗi file.
Nhà cung cấp theo review_provider (9router, lỗi thì Codex CLI). Người viết không tự chấm: chạy script, không tự đóng vai panel."""
import json, re, statistics, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import channel as chan
import review, router
from paths import load_yaml

MAX_ROUNDS = 5
ep = Path(sys.argv[1]).resolve()
fname = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "storyboard.md"
qa = ep / "qa"
qa.mkdir(exist_ok=True)
done = [p for p in qa.glob("panel_v*.json") if json.loads(p.read_text(encoding="utf-8")).get("file") == fname]
if len(done) >= MAX_ROUNDS and "--force" not in sys.argv:
    sys.exit(f"Đã đủ {MAX_ROUNDS} vòng panel cho {fname}.")
part = "--part" in sys.argv
cfg = chan.load(sys.argv[sys.argv.index("--channel") + 1] if "--channel" in sys.argv else ep)
personas = load_yaml(Path(cfg["_dir"]) / "script" / "panel.yaml")["personas"]
per_min = float(cfg["lang"]["pace"]["per_min"])
text = (ep / fname).read_text(encoding="utf-8")
m = re.search(r"^# (.+)$", text, re.M)
title = m[1].strip() if m else ep.name
meta = (ep / "meta.md").read_text(encoding="utf-8") if (ep / "meta.md").exists() else ""
hook = next((ln.split(":", 1)[1].strip(" *") for ln in meta.splitlines() if re.search(r"hook", ln, re.I) and ":" in ln), "")


def narration(src):
    """Bỏ tiêu đề, heading, ghi chú [ ], dòng QA; giữ đoạn, gắn mốc thời gian theo tốc độ đọc của kênh."""
    out, syl = [], 0
    for para in re.split(r"\n\s*\n", src):
        lines = [ln for ln in para.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
        t = re.sub(r"\[[^\]]*\]", "", " ".join(lines))
        t = re.sub(r"\s+", " ", t).strip()
        if not t:
            continue
        mm, ss = divmod(int(syl / per_min * 60), 60)
        out.append(f"[{mm}:{ss:02d}] {t}")
        syl += len(t.split())
    mm, ss = divmod(int(syl / per_min * 60), 60)
    return "\n".join(out), f"{mm}:{ss:02d}"


body, total = narration(text)
SCHEMA = '{"bam_xem":"co|khong","ly_do_bam":"","roi_di":{"moc":"m:ss hoặc het","cau":"","ly_do":""},"diem":{"mo_dau":0,"cuon":0,"giong_viet":0,"tin_cay":0,"cam_xuc":0,"ket":0},"khoanh_khac_hay":[{"moc":"","cau":"","vi_sao":""}],"doan_chung":[{"moc":"","cau":"","vi_sao":""}],"cau_nghe_ai":[{"cau":"","vi_sao":"","cau_thay":""}],"binh_luan":"","dang_ky":"co|khong","ly_do_dang_ky":"","sua_mot_dieu":""}'


def ask(p):
    prompt = f"""Bạn đóng vai MỘT người xem YouTube thật ở Việt Nam, không phải nhà phê bình. Nói thật như người đó nghĩ, không lịch sự hộ kênh.
Bạn là: {p['who']}
Bạn thích: {p['wants']}
Bạn ghét: {p['hates']}
Bạn thấy video trên YouTube: tiêu đề "{title}"{f', chữ trên thumbnail "{hook}"' if hook else ''}. {'Dưới đây CHỈ là đoạn mở đầu của video (khoảng ' + total + '), giọng đọc thuyết minh, hình minh họa. Chấm như vừa nghe xong đoạn này: có muốn xem tiếp không; nếu bỏ thì bỏ ở câu nào, nếu muốn xem tiếp thì roi_di.moc ghi "het". Điểm cuon là độ muốn xem tiếp, ket là câu cuối đoạn có kéo được sang phần sau không.' if part else 'Video dài khoảng ' + total + ', giọng đọc thuyết minh, hình minh họa.'}
Đọc lời thuyết minh dưới đây theo đúng thứ tự, như đang nghe từng giây. Mốc [m:ss] là thời điểm ước lượng.
Việc phải làm:
1. Có bấm xem không, vì sao (chỉ dựa vào tiêu đề và chữ thumbnail).
2. Nếu bấm: bạn bỏ đi ở mốc nào (trích đúng câu làm bạn bỏ), hoặc "het" nếu xem hết. Người thật hiếm khi xem hết 20 phút; chỉ ghi "het" nếu thật sự bị cuốn.
3. Chấm 1-10: mở đầu, độ cuốn, giọng tiếng Việt tự nhiên như người Việt kể, độ tin cậy, cảm xúc, đoạn kết.
4. Tối đa 5 khoảnh khắc hay nhất và tối đa 5 đoạn chùng (trích nguyên văn ngắn, có mốc).
5. Mọi câu nghe như AI viết hoặc như dịch từ tiếng Anh: trích nguyên văn, nói vì sao, viết câu thay theo cách người Việt nói. Không bắt bẻ câu đã tự nhiên.
6. Bình luận bạn sẽ thật sự gõ dưới video (đúng giọng của bạn, có thể có lỗi gõ như người thật).
7. Có đăng ký kênh không, vì sao. 8. Một điều bạn muốn kênh sửa nhất.
Chỉ trả JSON đúng dạng: {SCHEMA}

=== LỜI THUYẾT MINH ===
{body}
"""
    last = None
    for _ in range(3):
        try:
            r = router.json_in(review.ask_text(prompt))
            if isinstance(r, dict) and isinstance(r.get("diem"), dict):
                return p["id"], r
        except (ValueError, RuntimeError) as e:
            last = e
    return p["id"], {"loi": str(last or "trả lời sai dạng")}


with ThreadPoolExecutor(max_workers=len(personas)) as ex:
    res = dict(ex.map(ask, personas))


def sec(s):
    m = re.match(r"(\d+):(\d{2})", str(s))
    return int(m[1]) * 60 + int(m[2]) if m else None


tot_s = sec(total) or 1
ok = {k: v for k, v in res.items() if "loi" not in v}
keys = ["mo_dau", "cuon", "giong_viet", "tin_cay", "cam_xuc", "ket"]
avg = {k: round(statistics.mean(float(v["diem"].get(k) or 0) for v in ok.values()), 1) if ok else 0 for k in keys}
watch = []
for v in ok.values():
    if v.get("bam_xem") != "co":
        watch.append(0.0)
        continue
    s = sec(v.get("roi_di", {}).get("moc"))
    watch.append(1.0 if s is None else min(s / tot_s, 1.0))
avd = round(statistics.mean(watch) * 100) if watch else 0
subs = sum(v.get("dang_ky") == "co" for v in ok.values())
score = round(statistics.mean(avg.values()) * 10) if ok else 0
n = 1 + len(list(qa.glob("panel_v*.md")))
L = [f"# Panel khán giả lần {n}: {fname}", "> Mô phỏng do AI đóng vai người xem, không phải số liệu thật. Không đọc quy chuẩn kênh. Điểm dao động chừng 1-2 giữa các lượt: chênh dưới 3 điểm thì đọc nhận xét, không đọc điểm.",
     f"- Độ dài ước lượng {total}. Điểm panel {score}/100. Giữ chân trung bình ước lượng {avd}%. Đăng ký {subs}/{len(ok)}.",
     "- Điểm trung bình: " + ", ".join(f"{k} {v}" for k, v in avg.items()), ""]
for p in personas:
    v = res[p["id"]]
    L.append(f"## {p['who'].split(',')[0]}")
    if "loi" in v:
        L += [f"- Lỗi: {v['loi']}", ""]
        continue
    rd = v.get("roi_di", {})
    L += [f"- Bấm: {v.get('bam_xem')} ({v.get('ly_do_bam', '')}). Rời: {rd.get('moc')} | \"{rd.get('cau', '')}\" | {rd.get('ly_do', '')}",
          "- Điểm: " + ", ".join(f"{k} {v['diem'].get(k)}" for k in keys),
          f"- Bình luận: {v.get('binh_luan', '')}", f"- Đăng ký: {v.get('dang_ky')} ({v.get('ly_do_dang_ky', '')}). Muốn sửa: {v.get('sua_mot_dieu', '')}"]
    L += [f"- Hay {x.get('moc')}: \"{x.get('cau')}\" ({x.get('vi_sao')})" for x in v.get("khoanh_khac_hay", [])]
    L += [f"- Chùng {x.get('moc')}: \"{x.get('cau')}\" ({x.get('vi_sao')})" for x in v.get("doan_chung", [])]
    L += [f"- Nghe AI: \"{x.get('cau')}\" | {x.get('vi_sao')} | Thay: {x.get('cau_thay')}" for x in v.get("cau_nghe_ai", [])]
    L.append("")
(qa / f"panel_v{n}.md").write_text("\n".join(L), encoding="utf-8")
(qa / f"panel_v{n}.json").write_text(json.dumps({"n": n, "file": fname, "score": score, "avd": avd, "subs": subs, "avg": avg, "raw": res}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"qa/panel_v{n}.md | vòng {len(done) + 1}/{MAX_ROUNDS} | điểm {score}/100 | giữ chân ước lượng {avd}% | đăng ký {subs}/{len(ok)} | lỗi {len(res) - len(ok)}")
