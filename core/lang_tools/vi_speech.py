"""Tiếng Việt: giọng AI đọc đơn vị viết thành chữ, số đọc thành chữ, còn màn hình hiện số và ký hiệu; tên Latin kèm cách đọc trong ngoặc. Luật ở script/lang.md của kênh.
display: "Chicxulub (chích-xu-lúp), 10 ki-lô-mét" → "Chicxulub, 10 km".   speak: → "chích-xu-lúp, mười ki-lô-mét"."""
import re
from plain import words  # noqa: F401

LATIN = r"[A-Za-z]+(?: [A-Za-z]+)? \(([^()]*-[^()]*)\)"
UNITS = [(r"ki-lô-mét vuông", "km²"), (r"ki-lô-mét", "km"), (r"ki-lô-gam", "kg"), (r"phần trăm", "%"), (r"độ C", "°C"), (r"mét", "m")]
SPOKEN_UNITS = [("km²", "ki-lô-mét vuông"), ("km/h", "ki-lô-mét một giờ"), ("km/s", "ki-lô-mét một giây"), ("km", "ki-lô-mét"), ("kg", "ki-lô-gam"), ("cm", "xen-ti-mét"), ("mm", "mi-li-mét"), ("m", "mét"), ("%", "phần trăm"), ("°C", "độ C")]
DIGIT = "không một hai ba bốn năm sáu bảy tám chín".split()
NUM = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?"


def _group(n, full):
    """Đọc nhóm 3 chữ số. full: đứng sau nhóm lớn hơn nên đọc đủ "không trăm", "lẻ"."""
    h, t, o = n // 100, n // 10 % 10, n % 10
    out = [DIGIT[h], "trăm"] if h or full else []
    if t == 0:
        if o:
            out += (["lẻ"] if out else []) + [DIGIT[o]]
    elif t == 1:
        out += ["mười"] + ([{5: "lăm"}.get(o, DIGIT[o])] if o else [])
    else:
        out += [DIGIT[t], "mươi"] + ([{1: "mốt", 4: "tư", 5: "lăm"}.get(o, DIGIT[o])] if o else [])
    return out


def integer(n):
    if n == 0:
        return "không"
    if n >= 10**12:
        rest = n % 10**9
        return f"{integer(n // 10**9)} tỷ" + (f" {integer(rest)}" if rest else "")
    out = []
    for size, name in ((10**9, "tỷ"), (10**6, "triệu"), (10**3, "nghìn"), (1, "")):
        g = n // size % 1000
        if g:
            out += _group(g, bool(out)) + ([name] if name else [])
    return " ".join(out)


def number(tok):
    whole, _, dec = tok.replace(".", "").partition(",")
    s = integer(int(whole))
    if dec:
        s += " phẩy " + (" ".join(DIGIT[int(d)] for d in dec) if dec[0] == "0" or len(dec) > 2 else integer(int(dec)))
    return s


def _fraction(m):
    a, b = int(m[1]), int(m[2])
    return f"{integer(a)} phần {'tư' if b == 4 else integer(b)}"


def screen(text):
    for word, sym in UNITS:
        text = re.sub(rf"(\d[\d.,]*) {word}\b", (rf"\1{sym}" if sym in ("%", "°C") else rf"\1 {sym}"), text)
    return text


def display(s):
    s = screen(re.sub(r" \(([^()]*-[^()]*)\)", "", s))
    return re.sub(r"\s+([.,?!:;…)])", r"\1", s)  # kịch bản để " ." cho TTS ngắt nghỉ, phụ đề thì bỏ


def speak(s):
    s = re.sub(LATIN, r"\1", s)
    s = re.sub(r"(?<=[^\W\d_])(?=\d)", " ", s)  # TBH1 → TBH một
    for sym, word in SPOKEN_UNITS:
        s = re.sub(rf"(\d)\s?{re.escape(sym)}(?![\w/²])", rf"\1 {word}", s)
    s = re.sub(r"(?<![\d.,/])(\d{1,3})/(\d{1,3})(?![\d/])", _fraction, s)
    s = re.sub(r"\b(\d{1,2}):(\d{2})\b", lambda m: f"{integer(int(m[1]))} giờ" + (f" {integer(int(m[2]))}" if int(m[2]) else ""), s)
    s = re.sub(rf"({NUM})\s?[-–—]\s?(?=\d)", r"\1 đến ", s)
    s = re.sub(r"\bthứ 1\b", "thứ nhất", s)
    s = re.sub(r"\bthứ 4\b", "thứ tư", s)
    return re.sub(NUM, lambda m: number(m[0]), s)


def count(s):
    """Đếm theo chữ thật sự đọc: "66 triệu" là 4 âm tiết."""
    return len(speak(s).split())


def leftover(s):
    """Ký tự trong chữ đọc mà giọng AI có thể đọc sai. Rỗng là sạch."""
    return re.findall(r"[\d%°^=+×²³]", s)


def problems(s):
    return []
