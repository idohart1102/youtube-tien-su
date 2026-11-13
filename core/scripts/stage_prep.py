"""Chuẩn bị layer của Stage trước khi kiểm và render (HT-12), không tốn token:
- aspect: tỷ lệ ngang/cao của cutout, để bóng tiếp đất (shadow.w ≤ 3) và máy kiểm dải phụ đề tính đúng bề ngang.
- tone_auto: CSS filter cân độ sáng và độ bão hòa của cutout theo vùng nền quanh chân (cutout sáng/rực hơn nền thì dịu lại).
  Layer có tone riêng thì giữ tone riêng. Kênh tắt bằng theme.json "stage": {"auto_tone": false}.
- outline_auto: màu viền cutout = màu giấy ngả theo nền quanh cutout (sáng hơn rõ để vẫn tách khỏi nền, không trắng tinh).
- paper_auto: màu khung giấy của PhotoCard theo tông chính ảnh đó.
Thumbnail: python core/scripts/stage_prep.py --thumb <tập> <thumb_spec.json> ghi subject.outline_auto, photo.paper_auto (thumb.mjs tự gọi).
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


CREAM = (241, 231, 211)


def paper_color(region, mix=0.28):
    """Màu giấy theo tông vùng ảnh: mix phần màu trung bình + phần còn lại màu kem, sáng thêm 4%.
    Khung ảnh thật 0.28; viền cutout 0.4 (ngả theo nền rõ hơn, vẫn sáng hơn nền để tách khỏi nền)."""
    avg = ImageStat.Stat(region.convert("RGB")).mean
    c = [min(255, round((mix * a + (1 - mix) * k) * 1.04)) for a, k in zip(avg, CREAM)]
    return "#%02x%02x%02x" % tuple(c)


def bg_box(cut, x, y, h):
    w = h * cut.width / cut.height
    return (max(0, int(x - w * 0.6)), max(0, int(y - h * 0.45)), min(W, int(x + w * 0.6)), min(H, int(y + 40)))


def tone_for(bg_full, cut, x, y, h):
    box = bg_box(cut, x, y, h)
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
        pr = s.setdefault("props", {})
        if s["component"] == "PhotoCard" and s.get("asset") and not pr.get("fill"):
            ph = img(resolve_asset(ep, s["asset"]))
            if ph is not None:
                asp = ph.width / ph.height  # khung ảnh trong tờ giấy giữ đúng tỷ lệ ảnh, vừa trong 1300x760
                pw, phh = (1300, round(1300 / asp)) if asp > 1300 / 760 else (round(760 * asp), 760)
                for k, v in (("paper_auto", paper_color(ph)), ("photo_w", pw), ("photo_h", phh)):
                    if pr.get(k) != v:
                        pr[k] = v
                        changed += 1
        if s["component"] != "Stage":
            continue
        layers = s.get("props", {}).get("layers", [])
        bg_full = None
        for l in layers:
            if l.get("asset"):
                cut = img(resolve_asset(ep, l["asset"]))
            elif l.get("sprite"):  # sprite không có ảnh gốc: lấy khung đầu của clip đầu
                sp = l["sprite"]
                c0 = (sp.get("clips") or [{}])[0].get("name", "idle")
                cut = img(resolve_asset(ep, f'{sp["base"]}/{c0}/000.webp'))
            else:
                continue
            if cut is None:
                continue
            new = {"aspect": round(cut.width / cut.height, 3)} if l.get("asset") else {}
            if bg_full is None and s.get("asset"):
                bg = img(resolve_asset(ep, s["asset"]))
                bg_full = cover(bg.convert("RGB")) if bg else False
            x, y, h = l.get("x", W / 2), l.get("y", H - 80), l.get("h", 600)
            if bg_full and st.get("outline", True) and not l.get("blur"):
                box = bg_box(cut, x, y, h)
                if box[2] - box[0] >= 20 and box[3] - box[1] >= 20:
                    new["outline_auto"] = paper_color(bg_full.crop(box), 0.4)
            if bg_full and st.get("auto_tone", True) and l.get("asset") and not l.get("tone"):
                t = tone_for(bg_full, cut, x, y, h)
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


def prep_thumb(ep, spec_p):
    """Màu viền chủ thể và màu khung giấy ảnh thật trên thumbnail 1280x720, theo nền quanh chủ thể."""
    ep, spec_p = Path(ep).resolve(), Path(spec_p).resolve()
    specs = json.loads(spec_p.read_text(encoding="utf-8"))
    k = W / 1280  # toạ độ thumbnail → khung 1920 của cover()
    for sp in specs:
        bg = img(resolve_asset(ep, sp["bg"])) if sp.get("bg") else None
        bg_full = cover(bg.convert("RGB")) if bg else None
        sub = sp.get("subject")
        if sub and bg_full:
            cut = img(resolve_asset(ep, sub["asset"]))
            if cut is not None:
                box = bg_box(cut, sub["x"] * k, sub["y"] * k, sub["h"] * k)
                if box[2] - box[0] >= 20 and box[3] - box[1] >= 20:
                    sub["outline_auto"] = paper_color(bg_full.crop(box), 0.4)
        ph = sp.get("photo")
        if ph:
            im = img(resolve_asset(ep, ph["asset"]))
            if im is not None:
                ph["paper_auto"] = paper_color(im)
                ph.setdefault("h", round(ph["w"] * im.height / im.width))
    spec_p.write_text(json.dumps(specs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"stage_prep --thumb: {len(specs)} phương án")


if __name__ == "__main__":
    if sys.argv[1] == "--thumb":
        prep_thumb(sys.argv[2], sys.argv[3])
    else:
        prep(sys.argv[1])
