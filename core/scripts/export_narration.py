"""storyboard.md → script.md: chỉ lời thuyết minh, dán thẳng vào AI tạo giọng. Không còn ghi chú, tiêu đề, chữ số; chữ đọc lấy từ công cụ ngôn ngữ của kênh (lang.speech).
Kênh có lang.script_srt: true xuất thêm script_srt.md: cùng lời, chữ viết thông thường, làm căn cứ phụ đề. Từ điển tự đoán cách đọc thì ghi ra qa/tts_readings.tsv để soát.
Trong mỗi phần, các câu nối liền thành đoạn; chỉ xuống dòng ở chỗ storyboard có dòng trống giữa hai nhịp, để AI giọng ngắt lâu hơn. Mỗi phần cách nhau 1 dòng trống.
Dùng: python core/scripts/export_narration.py <episode_dir>. Còn chữ giọng AI dễ đọc sai thì báo lỗi, mã thoát 1."""
import re, sys
from pathlib import Path

ep = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel as chan
import status
status.require_brief(ep)
cfg = chan.load(ep)
lang, sp = cfg["lang"], chan.speech(cfg)
SEP = "" if lang["tokenize"] == "char" else " "
text = re.sub(r"<!--.*?-->", "", (ep / "storyboard.md").read_text(encoding="utf-8"), flags=re.S)
lines = []  # None = hết nhịp, "" = hết phần
for line in text.splitlines():
    if line.startswith("## "):
        lines.append("")
    if line.startswith("#"):
        continue
    if not line.strip():
        lines.append(None)
        continue
    s = re.sub(r"\s{2,}", " ", re.sub(r"[*_`]", "", re.sub(r"\[[^\]]*\]", "", line))).strip()
    if s:
        lines.append(s)


def build(convert):
    out, para, cur = [], [], []

    def flush_line():
        nonlocal cur
        if cur:
            para.append(SEP.join(cur)); cur = []

    for s in lines:
        if s is None or s == "":
            flush_line()
            if s == "" and para:
                out.append("\n".join(para)); para = []
        else:
            cur.append(convert(s))
    flush_line()
    if para:
        out.append("\n".join(para))
    return "\n\n".join(out) + "\n"


spoken = [s for s in lines if s]
tts = build(sp.speak)
(ep / "script.md").write_text(tts, encoding="utf-8")
units = sum(sp.count(s) for s in spoken)
pace = lang["pace"]
print(ep / "script.md", units, pace["unit"], "≈", round(units / pace["per_min"], 1), "phút")
if lang.get("script_srt"):
    (ep / "script_srt.md").write_text(build(sp.display), encoding="utf-8")
    print(ep / "script_srt.md", "(bản chữ thông thường, căn cứ phụ đề)")
if getattr(sp, "AUTO", None):
    (ep / "qa").mkdir(exist_ok=True)
    (ep / "qa" / "tts_readings.tsv").write_text("".join(f"{k}\t{v}\n" for k, v in sorted(sp.AUTO.items())), encoding="utf-8")
    print(f"{len(sp.AUTO)} cách đọc do từ điển đoán: qa/tts_readings.tsv. Sai thì ghi 《》 hoặc thêm vào script/readings.tsv.")
issues = sorted({c for c in (sp.leftover(tts) if hasattr(sp, "leftover") else re.findall(r"\d", tts))})
if issues:
    print("LỖI: chữ đọc còn ký tự dễ đọc sai:", " ".join(issues))
written = sorted({w for s in spoken for w in (sp.problems(s) if hasattr(sp, "problems") else [])})
if written:
    print("LỖI: số đi với lượng từ biến âm phải ghi cách đọc 《》:", " ".join(written))
sys.exit(1 if issues or written else 0)
