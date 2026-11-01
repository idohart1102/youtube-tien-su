"""Cho cutout cử động không cần tách lớp: uốn ảnh theo xương (cổ, đuôi, chân) rồi xuất chuỗi khung hình cho Stage (layer.sprite).
Dùng: python core/scripts/rig_cutout.py <file.rig.json> [clip1,clip2]  → <out>/<clip>/000.webp ..., <out>/outline.webp
      python core/scripts/rig_cutout.py --clean a.png b.png → a-clean.png, b-clean.png (chỉ làm sạch rìa)
Toạ độ trong rig.json theo pixel ảnh gốc. Trọng số xương là vùng đa giác làm mờ biên, nên chỗ uốn liền mạch, không lộ vết cắt.
limbs: chi tách thành lớp riêng (far nằm dưới thân, near nằm trên), trọng số theo độ cao nên chân quay nhiều cũng không rách."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

MAX_EDGE = 6  # px rìa cần thay màu: ảnh AI nền trong suốt hay có viền đỏ hoặc sáng ở mép


def blur(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype("uint8"))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype="float32") / 255


def clean_edges(im):
    """Bỏ viền màu lạ: lấy màu từ phần lõi bên trong rồi đẩy ra rìa, bo nhẹ alpha."""
    a = np.asarray(im.convert("RGBA"), dtype="float32") / 255
    al = a[..., 3]
    core = np.asarray(Image.fromarray(((al > 0.97) * 255).astype("uint8")).filter(ImageFilter.MinFilter(2 * MAX_EDGE + 1)), dtype="float32") / 255
    rgb = a[..., :3].copy()
    for r in (4, 10, 24):
        w = blur(core, r)[..., None] + 1e-4
        fill = np.stack([blur(a[..., c] * core, r) for c in range(3)], -1) / w
        rgb = np.where((core[..., None] < 0.5) & (w > 0.02), fill, rgb)
    al = np.clip((blur(al, 1.2) - 0.45) / 0.3, 0, 1)
    return Image.fromarray((np.dstack([rgb, al]) * 255).astype("uint8"), "RGBA")


def poly_mask(size, pts, feather):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(feather)), dtype="float32") / 255


def sample(a, x, y):
    """Lấy mẫu song tuyến, x y là mảng toạ độ."""
    h, w = a.shape[:2]
    x, y = np.clip(x, 0, w - 1.001), np.clip(y, 0, h - 1.001)
    x0, y0 = x.astype(int), y.astype(int)
    fx, fy = x - x0, y - y0
    if a.ndim == 3:
        fx, fy = fx[..., None], fy[..., None]
    return (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy)
            + a[y0 + 1, x0] * (1 - fx) * fy + a[y0 + 1, x0 + 1] * fx * fy)


def angle(spec, i, n):
    k = i / max(1, n - 1)
    k = k * k * (3 - 2 * k)
    base = spec.get("from", 0) + (spec.get("to", spec.get("from", 0)) - spec.get("from", 0)) * k
    return base + spec.get("amp", 0) * np.sin(2 * np.pi * (i / n * spec.get("cycles", 1) + spec.get("phase", 0)))


def warp(prem, bones, angles, dy):
    """Ánh xạ ngược: mỗi điểm đích tìm điểm nguồn, lặp 3 lần vì trọng số nằm ở không gian nguồn."""
    h, w = prem.shape[:2]
    py, px = np.mgrid[0:h, 0:w].astype("float32")
    py = py - dy
    inv = []
    for b, deg in zip(bones, angles):
        c, s = np.cos(np.radians(-deg)), np.sin(np.radians(-deg))
        qx, qy = px - b["pivot"][0], py - b["pivot"][1]
        inv.append((qx * c - qy * s + b["pivot"][0] - px, qx * s + qy * c + b["pivot"][1] - py))
    sx, sy = px.copy(), py.copy()
    for _ in range(3):
        dx_, dy_ = np.zeros_like(px), np.zeros_like(px)
        for b, (ix, iy) in zip(bones, inv):
            wt = sample(b["w"], sx, sy)
            dx_ += wt * ix
            dy_ += wt * iy
        sx, sy = px + dx_, py + dy_
    return sample(prem, sx, sy)


def over(top, bottom):
    return top + bottom * (1 - top[..., 3:])


def unprem(p):
    al = p[..., 3:]
    rgb = np.where(al > 1e-3, p[..., :3] / np.maximum(al, 1e-3), 0)
    return Image.fromarray((np.clip(np.dstack([rgb, al]), 0, 1) * 255).astype("uint8"), "RGBA")


def build(spec_path, only=None):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    A = Path(spec_path).resolve().parents[1] / "assets"  # <tập>/rig/x.rig.json → <tập>/assets
    out = A / spec["out"]
    src = clean_edges(Image.open(A / spec["source"]))
    pad = spec.get("pad", {})
    L, T, R = pad.get("left", 0), pad.get("top", 0), pad.get("right", 0)
    canvas = Image.new("RGBA", (src.width + L + R, src.height + T), (0, 0, 0, 0))
    canvas.paste(src, (L, T))
    a = np.asarray(canvas, dtype="float32") / 255
    prem = np.dstack([a[..., :3] * a[..., 3:], a[..., 3]])
    size = canvas.size
    bones = []
    for b in spec["bones"]:
        pts = [(x + L, y + T) for x, y in b["poly"]]
        w = poly_mask(size, pts, b.get("feather", 30))
        for ex in b.get("exclude", []):
            w = w * (1 - poly_mask(size, [(x + L, y + T) for x, y in ex], b.get("exclude_feather", 8)))
        bones.append({"name": b["name"], "pivot": (b["pivot"][0] + L, b["pivot"][1] + T), "w": w})
    limbs, body = [], prem
    yy = np.mgrid[0:size[1], 0:size[0]][0].astype("float32") - T
    for lb in spec.get("limbs", []):
        m = poly_mask(size, [(x + L, y + T) for x, y in lb["poly"]], lb.get("feather", 6))
        body = body * (1 - m[..., None])
        lbones = []
        for b in lb["bones"]:
            k = np.clip((yy - b["ramp_y"][0]) / (b["ramp_y"][1] - b["ramp_y"][0]), 0, 1)
            lbones.append({"name": b["name"], "pivot": (b["pivot"][0] + L, b["pivot"][1] + T), "w": k * k * (3 - 2 * k)})
        limbs.append({"under": lb.get("under", False), "img": prem * m[..., None], "bones": lbones})
    scale = spec.get("scale", 0.5)
    osize = (round(size[0] * scale), round(size[1] * scale))
    meta_p = out / "rig.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if only and meta_p.exists() else {"size": osize, "clips": {}}
    for name, clip in spec["clips"].items():
        if only and name not in only:
            continue
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        n = clip["n"]
        for i in range(n):
            ang = lambda bs: [angle(clip.get("bones", {}).get(b["name"], {}), i, n) for b in bs]
            dy = clip.get("bob", 0) * abs(np.sin(2 * np.pi * i / n * clip.get("bob_cycles", 1)))
            res = warp(body, bones, ang(bones), -dy)
            for lb in limbs:
                part = warp(lb["img"], lb["bones"], ang(lb["bones"]), -dy)
                res = over(res, part) if lb["under"] else over(part, res)
            im = unprem(res)
            im.resize(osize, Image.LANCZOS).save(d / f"{i:03d}.webp", quality=90, method=4)
        meta["clips"][name] = n
        print(name, n, "khung")
    if spec.get("outline_from"):
        first = Image.open(out / spec["outline_from"] / "000.webp").convert("RGBA").getchannel("A")
        wide = first.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1))
        edge = np.clip(np.asarray(wide, dtype="float32") - np.asarray(first.filter(ImageFilter.MinFilter(3)), dtype="float32"), 0, 255).astype("uint8")
        line = Image.new("RGBA", first.size, tuple(spec.get("outline_color", [255, 210, 63])) + (0,))
        line.putalpha(Image.fromarray(edge))
        line.save(out / "outline.webp", quality=90)
    meta_p.write_text(json.dumps(meta), encoding="utf-8")
    print("Xong:", out)


if __name__ == "__main__":
    if sys.argv[1] == "--clean":
        for f in sys.argv[2:]:
            p = Path(f)
            clean_edges(Image.open(p)).save(p.with_name(p.stem + "-clean.png"))
            print(p.with_name(p.stem + "-clean.png"))
    else:
        build(sys.argv[1], set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
