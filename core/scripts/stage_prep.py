"""Chuẩn bị layer của Stage trước khi kiểm và render (HT-12), không tốn token:
- aspect: tỷ lệ ngang/cao của cutout, để bóng tiếp đất (shadow.w ≤ 3) và máy kiểm dải phụ đề tính đúng bề ngang.
- tone_auto: CSS filter cân độ sáng và độ bão hòa của cutout theo vùng nền quanh chân (cutout sáng/rực hơn nền thì dịu lại).
  Layer có tone riêng thì giữ tone riêng. Kênh tắt bằng theme.json "stage": {"auto_tone": false}.
Dùng: python core/scripts/stage_prep.py <tập>. produce.py tự gọi. Chỉ ghi lại scenes.json khi có thay đổi."""
import json, sys
from pathlib import Path
from PIL import Image, ImageStat
from paths import resolve_asset

W, H = 1920, 1080
_cache = {}


def img(p):
    if p not in _cache:
        _cache[p] = Image.open(p).convert("RGBA") if p.exists() else None
    return _cache[p]


def stats(im, mask=None):
    """Độ sáng trung bình (0..1) và độ bão hòa trung bình (0..1)."""
    rgb = im.convert("RGB")
    l = ImageStat.Stat(rgb.convert("L"), mask).mean[0] / 255
    s = ImageStat.Stat(rgb.convert("HSV").split()[1], mask).mean[0] / 255
    return l, s


def cover(bg):
    """Ảnh nền phủ khung 1920x1080 như objectFit: cover."""
    k = max(W / bg.width, H / bg.height)
    im = bg.resize((round(bg.width * k), round(bg.height * k)))
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def tone_for(bg_full, cut, x, y, h):
    w = h * cut.width / cut.height
    box = (max(0, int(x - w * 0.6)), max(0, int(y - h * 0.45)), min(W, int(x + w * 0.6)), min(H, int(y + 40)))
    if box[2] - box[0] < 20 or box[3] - box[1] < 20:
        return None
    lb, sb = stats(bg_full.crop(box))
    small = cut.copy()
    small.thumbnail((256, 256))
    a = small.split()[3].point(lambda v: 255 if v > 200 else 0)
    if not a.getbbox():
        return None
    lc, sc = stats(small, a)
    clamp = lambda v, lo, hi: max(lo, min(hi, v))
    b = clamp((lb / max(lc, 0.02)) ** 0.5, 0.78, 1.12)  # khớp một nửa khoảng cách: cutout vẫn nổi rõ trên nền
    s = clamp((sb / max(sc, 0.02)) ** 0.5, 0.75, 1.1)
    if abs(b - 1) < 0.03 and abs(s - 1) < 0.03:
        return ""
    return f"brightness({b:.2f}) saturate({s:.2f})"


def prep(ep):
    ep = Path(ep).resolve()
    p = ep / "scenes.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    theme_p = ep.parents[1] / "theme.json"
    st = (json.loads(theme_p.read_text(encoding="utf-8")).get("stage") or {}) if theme_p.exists() else {}
    changed = 0
    for s in doc["scenes"]:
        if s["component"] != "Stage":
            continue
        layers = s.get("props", {}).get("layers", [])
        bg_full = None
        for l in layers:
            if not l.get("asset"):
                continue
            cut = img(resolve_asset(ep, l["asset"]))
            if cut is None:
                continue
            new = {"aspect": round(cut.width / cut.height, 3)}
            if st.get("auto_tone", True) and s.get("asset") and not l.get("tone"):
                if bg_full is None:
                    bg = img(resolve_asset(ep, s["asset"]))
                    bg_full = cover(bg.convert("RGB")) if bg else False
                if bg_full:
                    t = tone_for(bg_full, cut, l.get("x", W / 2), l.get("y", H - 80), l.get("h", 600))
                    if t is not None:
                        new["tone_auto"] = t
            for k, v in new.items():
                if l.get(k) != v:
                    l[k] = v
                    changed += 1
    if changed:
        p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"stage_prep: {changed} giá trị cập nhật")
    return changed


if __name__ == "__main__":
    prep(sys.argv[1])
