"""Soát kịch bản bằng máy, không tốn token. Dùng: python core/scripts/script_lint.py <episode_dir> [--file ten.md] [--part]
Chỉ đánh dấu vị trí để người đọc xét, không phán quyết văn AI và không tự sửa. Lỗi cứng (thiếu thẻ, từ cấm, sai độ dài) cho mã thoát 1.
--part: kiểm một đoạn, bỏ qua độ dài và số bước. Kết quả ghi qa/lint.json. Giới hạn lấy từ script/dna.yaml của kênh."""
import json, re, shutil, subprocess, sys
from pathlib import Path
import channel as chan
from paths import ROOT, load_yaml

ep = Path(sys.argv[1]).resolve()
fname = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else "storyboard.md"
part = "--part" in sys.argv
cfg = chan.load(ep)
lang, sp = cfg["lang"], chan.speech(cfg)
dna = load_yaml(Path(cfg["_dir"]) / "script" / "dna.yaml")
pace = lang["pace"]["per_min"]
hard, flags = [], []

raw = (ep / fname).read_text(encoding="utf-8")
sents, steps, t = [], 0, 0.0
marks = {}
for line in raw.splitlines():
    if line.startswith("## "):
        steps += 1
    if line.startswith("#"):
        continue
    for piece in re.split(lang["sentence_split"], line.strip()):
        tags = re.findall(r"\[([^\]]*)\]", piece)
        text = re.sub(r"\s{2,}", " ", re.sub(r"\[[^\]]*\]", "", piece)).strip()
        at = t
        for k in tags:
            if k in ("LỜI HỨA", "ĐĂNG KÝ"):
                marks.setdefault(k, at)
        if text:
            n = sp.count(text)
            sents.append({"text": text, "units": n, "at": t})
            t += n / pace * 60
total = sum(s["units"] for s in sents)
minutes = total / pace

# Thứ tự và thời điểm
for k in ("LỜI HỨA", "ĐĂNG KÝ"):
    if k not in marks:
        hard.append(f"Thiếu thẻ [{k}]")
if "LỜI HỨA" in marks and marks["LỜI HỨA"] > dna["promise_before_s"]:
    hard.append(f"Lời hứa ở khoảng giây {marks['LỜI HỨA']:.0f}, quá hạn {dna['promise_before_s']} giây")
if "LỜI HỨA" in marks and "ĐĂNG KÝ" in marks:
    if marks["ĐĂNG KÝ"] < marks["LỜI HỨA"]:
        hard.append("Lời mời đăng ký đứng trước câu hỏi lớn")
    cta = [s for s in sents if s["at"] >= marks["ĐĂNG KÝ"]]
    # Đoạn đăng ký kết thúc ở dòng có thẻ: lấy theo các câu cùng dòng với thẻ
    m = re.search(r"\[ĐĂNG KÝ\]([^\n]*)", raw)
    if m:
        secs = sp.count(re.sub(r"\[[^\]]*\]", "", m[1])) / pace * 60
        if secs > dna["subscribe"]["max_s"] + 2:
            flags.append(f"Lời mời đăng ký khoảng {secs:.0f} giây, giới hạn {dna['subscribe']['max_s']} giây")
if not part:
    L = dna["length_minutes"]
    if not L["min"] <= minutes <= L["max"]:
        hard.append(f"Ước lượng {minutes:.1f} phút, cần {L['min']}-{L['max']} phút")
    if not dna["steps"][0] <= steps <= dna["steps"][1]:
        flags.append(f"{steps} bước, khuyến nghị {dna['steps'][0]}-{dna['steps'][1]}")
    if dna.get("signature") and raw.count(dna["signature"]) != 1:
        flags.append(f"Chữ ký kênh xuất hiện {raw.count(dna['signature'])} lần, cần đúng 1")

# Từ cấm trong lời đọc. Dòng tiêu đề không tính.
narr = "\n".join(s["text"] for s in sents)
for pat in dna.get("banned_self_reference", []):
    for m in re.finditer(pat, narr, re.I):
        hard.append(f"Từ cấm 「{m[0]}」: {narr[max(0, m.start() - 20):m.end() + 20]!r}")
# Cụm cần soát: đánh dấu từ lần thứ 2, hoặc lần đầu với cụm quảng cáo
for w in dna.get("watch_phrases", []):
    c = len(re.findall(re.escape(w), narr, re.I))
    if c >= 2:
        flags.append(f"「{w}」 {c} lần, xem có thêm nghĩa không")

# Nhịp: nhiều câu liền gần bằng nhau
run = 1
for a, b in zip(sents, sents[1:]):
    run = run + 1 if a["units"] and abs(a["units"] - b["units"]) <= max(1, a["units"] * 0.15) else 1
    if run == 4:
        flags.append(f"4 câu liền cùng độ dài ở khoảng giây {b['at']:.0f}: {b['text'][:30]}")
# Từ nối đầu câu liên tiếp, câu hỏi tu từ dày
CONN = ("Tuy nhiên", "Hơn nữa", "Ngoài ra", "Bên cạnh đó", "また", "さらに", "そして", "しかし")
for a, b in zip(sents, sents[1:]):
    if a["text"].startswith(CONN) and b["text"].startswith(CONN):
        flags.append(f"Từ nối đầu câu liên tiếp: {b['text'][:30]}")
asks = sum(s["text"].endswith(("?", "？")) for s in sents)
if sents and minutes and asks / max(minutes, 0.5) > 4:
    flags.append(f"{asks} câu hỏi trong {minutes:.1f} phút, dày hơn 4 câu mỗi phút")
# Mật độ số
nums = len(re.findall(r"\d[\d.,]*", narr))
lo, hi = dna["numbers_per_min"]
if minutes and not part and not lo <= nums / minutes <= hi:
    flags.append(f"{nums / minutes:.1f} số mỗi phút, khoảng khởi đầu {lo}-{hi}")
# Tiếng Nhật: câu dài, đuôi câu lặp nhiều chỉ cảnh báo
warn = dna.get("sentence_warn_chars")
if warn:
    for s in sents:
        if len(s["text"]) > warn:
            flags.append(f"Câu {len(s['text'])} ký tự: {s['text'][:30]}")
# textlint nếu kênh và máy có cài: bổ sung, không bắt buộc
tl = ROOT / "node_modules" / ".bin" / "textlint"
if cfg["language"] == "ja" and tl.exists() and shutil.which("node"):
    tmp = ep / "qa" / "_lint.md"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(narr, encoding="utf-8")
    r = subprocess.run([str(tl), "--no-color", "--format", "unix", str(tmp)], capture_output=True, text=True, cwd=ROOT)
    flags += [re.sub(r"^.*?:(\d+:\d+): ", r"textlint \1 ", l) for l in r.stdout.splitlines() if ":" in l and "problem" not in l][:40]
    tmp.unlink(missing_ok=True)

(ep / "qa").mkdir(exist_ok=True)
(ep / "qa" / "lint.json").write_text(json.dumps({"file": fname, "units": total, "minutes": round(minutes, 1), "steps": steps, "numbers": nums, "questions": asks, "hard": hard, "flags": flags}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{total} {lang['pace']['unit']}, ước lượng {minutes:.1f} phút, {steps} phần, {nums} số, {asks} câu hỏi")
for h in hard:
    print("  Lỗi:", h)
for f in flags:
    print("  Xét:", f)
print("OK" if not hard else "CẦN SỬA")
sys.exit(1 if hard else 0)
