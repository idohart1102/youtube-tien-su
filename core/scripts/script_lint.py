"""Soát kịch bản bằng máy, không tốn token. Dùng: python core/scripts/script_lint.py <episode_dir> [--file ten.md] [--part]
Chỉ đánh dấu vị trí để người đọc xét, không phán quyết văn AI và không tự sửa. Lỗi cứng chỉ dành cho điều máy đo chắc được (thiếu thẻ, từ cấm, sai độ dài, số thiếu mã fact), cho mã thoát 1.
Chuyện câu chữ (rào, từ tuyệt đối) xét theo đoạn và chỉ nhắc, để không ép người viết làm gãy nhịp văn; qc_script chấm theo nghĩa.
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
sents, steps, t, para = [], 0, 0.0, 0
marks = {}
for line in raw.splitlines():
    if line.startswith("## "):
        steps += 1
    if line.startswith("#") or not line.strip():
        para += 1  # dòng trống hoặc heading mở đoạn mới
        continue
    for piece in re.split(lang["sentence_split"], line.strip()):
        tags = re.findall(r"\[([^\]]*)\]", piece)
        lead = re.match(r"^\s*((?:\[[^\]]*\]\s*)+)", piece)  # thẻ fact đứng ngay sau dấu chấm thuộc về câu trước
        if lead and sents:
            sents[-1]["facts"] += re.findall(r"\[F\s*(\d+)\]", lead[1], re.I)
        text = re.sub(r"\s{2,}", " ", re.sub(r"\[[^\]]*\]", "", piece)).strip()
        fids = re.findall(r"\[F\s*(\d+)\]", piece[lead.end() if lead else 0:], re.I)
        at = t
        for k in tags:
            if k in ("LỜI HỨA", "ĐĂNG KÝ"):
                marks.setdefault(k, at)
        if text:
            n = sp.count(text)
            sents.append({"text": text, "units": n, "at": t, "facts": fids, "para": para})
            t += n / pace * 60
total = sum(s["units"] for s in sents)
minutes = total / pace

# Thứ tự và thời điểm
for k in ("LỜI HỨA", "ĐĂNG KÝ"):
    if k not in marks:
        hard.append(f"Thiếu thẻ [{k}]")
if "LỜI HỨA" in marks and marks["LỜI HỨA"] > dna["promise_before_s"]:
    flags.append(f"Lời hứa ở khoảng giây {marks['LỜI HỨA']:.0f}, quá đích {dna['promise_before_s']} giây (style: đích, không kéo cho bằng được)")
if "LỜI HỨA" in marks and "ĐĂNG KÝ" in marks:
    if marks["ĐĂNG KÝ"] < marks["LỜI HỨA"]:
        hard.append("Lời mời đăng ký đứng trước câu hỏi lớn")
    # position: end (kênh khai trong dna.yaml) thì lời mời nằm ở phần kết, sau 85% thời lượng
    if dna["subscribe"].get("position") == "end" and not part and marks["ĐĂNG KÝ"] < 0.85 * total / pace * 60:
        hard.append(f"Lời mời đăng ký ở giây {marks['ĐĂNG KÝ']:.0f}, kênh quy định đặt ở phần kết")
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

# Gắn fact (Sếp duyệt 2026-11-02): câu có số phải ghi mã fact của brief, ví dụ "... nặng 0,4 gam [F31]." Mã không được đọc, export tự bỏ.
# Fact mức "Có thể"/"Còn tranh cãi" thì câu phải nói thành lời mức đó. Từ tuyệt đối phải có fact chứng minh.
brief = (ep / "brief.md").read_text(encoding="utf-8") if (ep / "brief.md").exists() else ""
LEVEL = {}
for m in re.finditer(r"^\|\s*(\d+)\.\s*[^|]*\|\s*([^|]+)\|", brief, re.M):
    lv = m[2].lower()
    LEVEL[m[1]] = "tranh-cai" if "tranh" in lv else "co-the" if "có thể" in lv or "possible" in lv else "xac-nhan"
HEDGE = r"có thể|có lẽ|nhiều khả năng|khả năng|theo (?:nhóm|các tác giả|tác giả|bài báo|họ|nghiên cứu)|cho rằng|giả thuyết|chưa chắc|dường như|được cho là|ước tính|khoảng|chừng|tranh cãi|chưa rõ|chưa thể|nghi|suy luận|lập luận"
ABSOLUTE = r"chắc chắn|không thể|chẳng ai|không ai|chứ không phải|hoàn toàn|duy nhất|tuyệt đối|luôn luôn|lớn nhất|cổ nhất|sớm nhất|đầu tiên|100 ?%"
VI = cfg["language"] == "vi"
if LEVEL:
    for x in sents:
        for f in x["facts"]:
            if f not in LEVEL:
                hard.append(f"Mã [F{f}] không có trong bảng fact của brief: {x['text'][:50]}")
        if re.search(r"\d", re.sub(r"\b[A-ZÀ-Ỹ]\w*(?: [A-ZÀ-Ỹ]\w*)* \d+\b", "", x["text"])) and not x["facts"]:  # "Thung Bình 1" là tên, không phải số liệu
            hard.append(f"Câu có số chưa ghi mã fact: {x['text'][:60]}")
        if VI and not x["facts"] and (m := re.search(ABSOLUTE, x["text"], re.I)):
            flags.append(f"Từ tuyệt đối 「{m[0]}」 chưa có fact, xem câu có nói quá không: {x['text'][:60]}")
    # Mức chắc chắn nói một lần mỗi khối (Sếp 2026-11-03): đoạn có fact "có thể"/"tranh cãi" chỉ cần một lời rào ở trong đoạn, không bắt từng câu
    for pid in dict.fromkeys(x["para"] for x in sents):
        ps = [x for x in sents if x["para"] == pid]
        weak = [x for x in ps if {LEVEL.get(f) for f in x["facts"]} & {"co-the", "tranh-cai"} and "xac-nhan" not in {LEVEL.get(f) for f in x["facts"]}]
        if VI and weak and not any(re.search(HEDGE, x["text"], re.I) for x in ps):
            hard.append(f"Đoạn dùng fact mức có thể/tranh cãi mà chưa nói mức chắc chắn lần nào: {weak[0]['text'][:60]}")
elif not part:
    flags.append("brief.md chưa có bảng fact đánh số, chưa kiểm được mã fact")
# Tính cách người dẫn trong style.md (vd "thám tử thời gian") là giọng, không phải nhân vật: nói thẳng ra thì người xem không biết là ai
style = (Path(cfg["_dir"]) / "script" / "style.md")
for persona in re.findall(r'[Nn]gười dẫn là "([^"]+)"', style.read_text(encoding="utf-8") if style.exists() else ""):
    head = persona.split()[0:2]
    for m in re.finditer(re.escape(" ".join(head)), narr, re.I):
        flags.append(f"Lời đọc gọi tên tính cách người dẫn 「{m[0]}」 mà chưa giới thiệu: {narr[max(0, m.start() - 30):m.end() + 30]!r}")

# Không nhắc tới AI trong lời đọc, tiêu đề, mô tả, tag (Sếp 2026-11-03)
AI_WORDS = r"\bA\.?I\b|(?i:trí tuệ nhân tạo)|人工知能"  # "AI" phân biệt hoa thường: tiếng Việt có chữ "ai" (không ai, ai gây ra)
for m in re.finditer(AI_WORDS, narr):
    hard.append(f"Lời đọc nhắc tới AI 「{m[0]}」: {narr[max(0, m.start() - 30):m.end() + 30]!r}")
meta = ep / "meta.md"
if meta.exists():
    public = meta.read_text(encoding="utf-8").split("\n## 5.")[0]  # chỉ phần đăng lên YouTube: tiêu đề, mô tả, tag
    for m in re.finditer(AI_WORDS, public):
        hard.append(f"meta.md nhắc tới AI 「{m[0]}」: tiêu đề, mô tả, tag không nhắc AI")

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
# Tiếng Việt: câu quá dài thì người chỉ nghe không theo kịp, chỉ nhắc
if VI:
    for x in sents:
        if x["units"] > dna.get("sentence_warn_syllables", 35):
            flags.append(f"Câu {x['units']} âm tiết, người chỉ nghe khó theo, xem có tách được không: {x['text'][:40]}")
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
