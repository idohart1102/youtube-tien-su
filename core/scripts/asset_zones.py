"""Tìm vùng trống trên mỗi ảnh nền / ảnh thật để đặt thẻ số liệu không đè chủ thể và chi tiết quan trọng.
Dùng: python core/scripts/asset_zones.py <tập>. gen_assets.py tự gọi cho ảnh mới. Kết quả <tập>/qa/zones.json: {file: {"card": [cx, cy], "subject": [x, y, w, h], "ground": [x, y, w, h]}} (ground: mặt đất trống để đặt chân cutout, Sếp 2026-11-07) (0..1 theo ảnh).
align_srt.py --apply đọc file này để đặt vị trí thẻ (không tốn token). Chấm 9 ảnh một lần cho rẻ."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import review

PROMPT = """Each numbered cell is one image used in a documentary video. For each image find:
- subject: bounding box of the main subject and important details (the thing a viewer must see), as [x, y, w, h] in 0..1 of that image.
- ground: [x, y, w, h] (0..1) of the largest open walkable ground (dry earth, rock, sand, grass, shore) where a person or animal could stand, not water, not sky, not a wall. [0,0,0,0] if none.
- card: center [cx, cy] (0..1) of the best calm empty area for a text card about 34% of the image wide and 12% high, that does not cover the subject or important details. Never in the bottom 22% (subtitles). Prefer the upper half.
Reply ONLY JSON: {"cells":[{"n":1,"subject":[0,0,0,0],"ground":[0,0.6,1,0.3],"card":[0.5,0.25]}]}"""


def ensure(ep, files=None):
    ep = Path(ep)
    zp = ep / "qa" / "zones.json"
    zones = json.loads(zp.read_text(encoding="utf-8")) if zp.exists() else {}
    if files is None:
        plan = json.loads((ep / "asset_plan.json").read_text(encoding="utf-8"))
        files = [x["file"] for x in plan["assets"] if x.get("kind") in ("ai", "real") and x.get("role") != "cutout"]
    todo = [f for f in files if f not in zones and (ep / "assets" / f).exists()]
    for k in range(0, len(todo), 9):
        part = todo[k:k + 9]
        cw, ch = 640, 360
        sheet = Image.new("RGB", (3 * cw, -(-len(part) // 3) * ch), "#000")
        dr = ImageDraw.Draw(sheet)
        for n, f in enumerate(part):
            im = Image.open(ep / "assets" / f).convert("RGB").resize((cw - 4, ch - 4))  # kéo về 16:9 như trong khung; tọa độ vẫn theo ảnh
            X, Y = (n % 3) * cw, (n // 3) * ch
            sheet.paste(im, (X + 2, Y + 2))
            dr.rectangle([X + 2, Y + 2, X + 48, Y + 36], fill="#000")
            dr.text((X + 8, Y + 4), str(n + 1), fill="#ffd23f", font=ImageFont.load_default(28))
        tmp = ep / "qa" / "zones_sheet.jpg"
        tmp.parent.mkdir(exist_ok=True)
        sheet.save(tmp, quality=85)
        try:
            r = review.ask_json(PROMPT, [tmp], edge=1920)
        except Exception as e:
            print("  ! không chấm được vùng trống:", str(e)[:120])
            continue
        for c in r.get("cells", []):
            n = int(c.get("n", 0)) - 1
            if 0 <= n < len(part) and len(c.get("card") or []) == 2:
                zones[part[n]] = {"card": [min(0.85, max(0.15, float(c["card"][0]))), min(0.7, max(0.1, float(c["card"][1])))],
                                  "subject": [float(v) for v in (c.get("subject") or [0, 0, 0, 0])][:4],
                                  "ground": [float(v) for v in (c.get("ground") or [0, 0, 0, 0])][:4]}
        tmp.unlink(missing_ok=True)
        zp.write_text(json.dumps(zones, ensure_ascii=False, indent=1), encoding="utf-8")
    return zones


if __name__ == "__main__":
    z = ensure(sys.argv[1])
    print(len(z), "ảnh có vùng đặt thẻ → qa/zones.json")
