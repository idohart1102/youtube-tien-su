"""Một nơi duy nhất đọc cấu hình kênh: channel.yaml + theme.json. Mọi script theo ngôn ngữ đều qua đây, không rẽ nhánh theo mã ngôn ngữ.
Dùng làm thư viện: cfg = load(ep); sp = speech(cfg). Kiểm tra kênh: python core/scripts/channel.py <slug hoặc thư mục tập>."""
import importlib, json, sys
from pathlib import Path
from paths import ROOT, load_yaml

TOOLS = ROOT / "core" / "lang_tools"
REQUIRED = {
    "language": "mã ngôn ngữ, vd vi",
    "locale": "mã vùng để định dạng số, vd vi-VN",
    "country": "mã quốc gia, vd VN",
    "lang.speech": "công cụ trong core/lang_tools, vd plain",
    "lang.tokenize": "word hoặc char",
    "lang.sentence_split": "biểu thức cắt câu",
    "lang.pace.unit": "syllable, word hoặc char",
    "lang.pace.per_min": "số đơn vị đọc mỗi phút",
    "lang.subtitle.max": "số ký tự tối đa mỗi dòng phụ đề",
    "lang.subtitle.break_after": "dấu ưu tiên ngắt dòng",
    "lang.card.max": "giới hạn thẻ chữ",
    "lang.card.unit": "word hoặc char",
    "lang.ago": "mẫu chữ số năm trước",
}
LABELS = ["xac-nhan", "co-the", "tranh-cai", "clock", "hoangsa", "truongsa", "biendong", "ai_notice", "today"]


def channel_of(path):
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = ROOT / "channels" / str(path)
    p = p.resolve()
    if (p / "channel.yaml").exists():
        return p
    if (p.parent.parent / "channel.yaml").exists():
        return p.parent.parent
    raise SystemExit(f"Không tìm thấy channel.yaml từ {path}")


def _get(d, dotted):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def check(cfg):
    """Trả về danh sách thiếu sót. Thiếu là báo lỗi, không ngầm dùng ngôn ngữ khác."""
    bad = [f"thiếu {k} ({why})" for k, why in REQUIRED.items() if _get(cfg, k) in (None, "", [])]
    labels = _get(cfg, "lang.labels") or {}
    bad += [f"thiếu lang.labels.{k}" for k in LABELS if not labels.get(k)]
    tool = _get(cfg, "lang.speech")
    if tool and not (TOOLS / f"{tool}.py").exists():
        bad.append(f"không có công cụ core/lang_tools/{tool}.py")
    return bad


def load(path):
    d = channel_of(path)
    cfg = load_yaml(d / "channel.yaml")
    cfg["_dir"] = str(d)
    th = d / "theme.json"
    cfg["_theme"] = json.loads(th.read_text(encoding="utf-8")) if th.exists() else {}
    return cfg


def speech(cfg):
    """Nạp công cụ ngôn ngữ của kênh: display(s), speak(s), words(s), count(s)."""
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    mod = importlib.import_module(cfg["lang"]["speech"])
    if hasattr(mod, "setup"):
        mod.setup(cfg)
    return mod


def theme(cfg):
    """Theme cho Remotion: theme.json của kênh + chữ cố định, mã vùng, mẫu năm từ channel.yaml."""
    lang = cfg["lang"]
    return {**cfg["_theme"], "lang": cfg["language"], "locale": cfg["locale"], "labels": lang["labels"], "ago": lang["ago"]}


if __name__ == "__main__":
    c = load(sys.argv[1])
    problems = check(c)
    print("\n".join("✗ " + p for p in problems) if problems else f"OK {Path(c['_dir']).name}")
    sys.exit(1 if problems else 0)
