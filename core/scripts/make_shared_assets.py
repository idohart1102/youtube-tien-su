"""Sinh asset dùng chung bằng code, vì git không chứa media. Có file rồi thì giữ nguyên.
Dùng: python core/scripts/make_shared_assets.py. doctor.py, produce.py và bộ test tự gọi khi thiếu."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from paths import ROOT

SHARED = ROOT / "assets" / "shared"
W, H = 1920, 1080


def paper(path):
    """Hạt giấy mịn, chồng lớp multiply trên toàn video."""
    rng = np.random.default_rng(7)
    base = Image.fromarray(rng.integers(0, 256, (H, W), dtype=np.uint8), "L").filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(base, dtype=np.float32)
    a = 235 + (a - a.mean()) / max(a.std(), 1) * 6
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L").save(path)


def strata(path):
    """Các lớp đá nằm ngang, màu đất trung tính, dùng cho hiệu ứng StrataWipe."""
    rng = np.random.default_rng(11)
    colors = np.array([[92, 82, 74], [138, 118, 98], [112, 100, 92], [158, 138, 114], [84, 78, 76], [128, 108, 90], [168, 150, 128], [100, 88, 80]], dtype=np.float32)
    edges = np.cumsum(rng.uniform(45, 150, 24))
    x = np.arange(W, dtype=np.float32)
    warp = 16 * np.sin(x / 310) + 7 * np.sin(x / 83 + 1.3) + 3 * np.sin(x / 29 + 0.4)
    y = np.arange(H, dtype=np.float32)[:, None] - warp[None, :]
    picks = rng.integers(0, len(colors), len(edges) + 1)
    img = colors[picks[np.searchsorted(edges, y + 40)]]
    grain = Image.fromarray(rng.integers(0, 256, (H // 3, W // 12), dtype=np.uint8), "L").resize((W, H), Image.BICUBIC)
    img = img + ((np.asarray(grain, dtype=np.float32) - 128) * 0.16)[:, :, None] + rng.normal(0, 7, (H, W, 1))
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.GaussianBlur(0.6)).save(path, quality=88)


def fixtures(dest):
    """Ảnh nền và cutout giả cho bộ test: bg.jpg, cutout.png."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(3)
    top, low = np.array([70, 92, 110], dtype=np.float32), np.array([30, 38, 34], dtype=np.float32)
    t = np.linspace(0, 1, 540, dtype=np.float32)[:, None, None]
    bg = (top * (1 - t) + low * t) * np.ones((540, 960, 3), dtype=np.float32) + rng.normal(0, 5, (540, 960, 3))
    Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB").save(dest / "bg.jpg", quality=85)
    cut = Image.new("RGBA", (400, 317), (0, 0, 0, 0))
    d = ImageDraw.Draw(cut)
    d.ellipse((60, 90, 340, 250), fill=(96, 92, 80, 255))
    d.ellipse((300, 60, 390, 140), fill=(96, 92, 80, 255))
    d.rectangle((110, 220, 150, 317), fill=(80, 76, 68, 255))
    d.rectangle((250, 220, 290, 317), fill=(80, 76, 68, 255))
    cut.save(dest / "cutout.png")


def ensure():
    """Tạo các file còn thiếu, trả về danh sách file vừa tạo."""
    (SHARED / "textures").mkdir(parents=True, exist_ok=True)
    (SHARED / "music").mkdir(exist_ok=True)
    (SHARED / "sfx").mkdir(exist_ok=True)
    made = []
    for name, fn in (("paper.png", paper), ("tang-da.jpg", strata)):
        p = SHARED / "textures" / name
        if not p.exists():
            fn(p)
            made.append(p)
    return made


if __name__ == "__main__":
    made = ensure()
    print("Đã tạo:", *[str(p.relative_to(ROOT)) for p in made], sep="\n  ") if made else print("Đã đủ asset dùng chung")
    sys.exit(0)
