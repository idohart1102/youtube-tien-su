"""Tách hiện vật thật (xương, hóa thạch, mẫu đá, người trong ảnh tư liệu) khỏi ảnh thật thành cutout PNG (Sếp 2026-11-07). Chỉ dùng với ảnh hiện vật chụp trên nền sạch (bảo tàng, nền trơn); hóa thạch lẫn trong đá cùng màu thì để nguyên ảnh trong khung giấy.
Không phải rig, không cắt tay chân; không phải tách nền nhiều lớp độ sâu. Cutout giữ nguồn của ảnh gốc: ghi vào credits.json của tập.
Dùng: python core/scripts/cut_real.py <tập> <photos/ảnh.jpg> <tên-ra> [--box x0 y0 x1 y1] [--model isnet-general-use]
  --box: vùng (0..1) chứa vật cần tách, để mô hình không lấy cả bàn, giá đỡ, người xung quanh.
Ra: assets/creatures/<tên-ra>.png và qa/cut_<tên-ra>.jpg (xem trên nền xám và nền tối)."""
import argparse, json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from rig_cutout import clean_edges

ap = argparse.ArgumentParser()
ap.add_argument("ep"); ap.add_argument("photo"); ap.add_argument("name")
ap.add_argument("--box", nargs=4, type=float)
ap.add_argument("--model", default="isnet-general-use")
a = ap.parse_args()
ep = Path(a.ep)
src = ep / "assets" / a.photo
im = Image.open(src).convert("RGB")
if a.box:
    W, H = im.size
    im = im.crop((int(a.box[0] * W), int(a.box[1] * H), int(a.box[2] * W), int(a.box[3] * H)))
if max(im.size) < 800:
    print(f"  ! ảnh nguồn {im.size} nhỏ hơn 800 px: cutout sẽ mờ khi phóng")
from rembg import remove, new_session
out = remove(im, session=new_session(a.model), post_process_mask=True)
al = out.getchannel("A").point(lambda v: 255 if v > 235 else (0 if v < 12 else v))
out.putalpha(al)
out = clean_edges(out)
box = out.getchannel("A").getbbox()
if not box:
    sys.exit("  ! không tách được vật thể")
out = out.crop((max(0, box[0] - 6), max(0, box[1] - 6), min(out.width, box[2] + 6), min(out.height, box[3] + 6)))
dst = ep / "assets" / "creatures" / f"{a.name}.png"
dst.parent.mkdir(parents=True, exist_ok=True)
out.save(dst)
# xem kiểm trên nền xám và nền tối
sheet = Image.new("RGB", (out.width * 2 + 30, out.height + 20), "#222")
for i, c in enumerate(("#5a6470", "#15120e")):
    bg = Image.new("RGBA", out.size, c); bg.alpha_composite(out)
    sheet.paste(bg.convert("RGB"), (10 + i * (out.width + 10), 10))
(ep / "qa").mkdir(exist_ok=True)
sheet.thumbnail((1600, 900)); sheet.save(ep / "qa" / f"cut_{a.name}.jpg", quality=88)
# nguồn: dùng chung nguồn ảnh gốc
cp = ep / "credits.json"
cr = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
items = cr if isinstance(cr, list) else cr.setdefault("items", []) if "items" in cr else None
src_credit = None
if isinstance(cr, dict) and a.photo in cr:
    src_credit = cr[a.photo]
    cr[f"creatures/{a.name}.png"] = src_credit
    cp.write_text(json.dumps(cr, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{dst.relative_to(ep)} {out.size}" + ("" if src_credit else "  (chưa ghi nguồn: credits.json không có ảnh gốc)"))
