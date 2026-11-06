"""Kiểm ảnh ngay sau khi tải/tạo (HT-09), trước khi dựng cảnh. gen_assets.py tự gọi ở cuối.
Dùng: python core/scripts/check_assets.py <tập> [--no-ai]
Kỹ thuật (máy, không tốn token):
- Ảnh thật thấp hơn 800 px: phóng lên 800 px cao (Lanczos), giữ bản gốc ở assets/_orig/.
- Ảnh nhiều ô (hình bài báo ghép nhiều panel): đếm ô theo dải nền đồng màu chạy hết chiều ảnh → validate_scenes chặn dùng cả bảng (bài học 83).
- Ám màu: ảnh AI phủ vàng/cam/sepia cả khung (ảnh thật giữ màu gốc, không báo).
- Cutout viền bẩn: mép alpha sáng hơn hẳn thân (viền trắng còn sót khi tách nền).
Nội dung (9router, vai QC, 1 lượt): chấm asset_sheet.jpg so với asset_plan.json: sai thời kỳ, sai giải phẫu, vật thể lạ, chữ rác.
Kết quả qa/asset_check.json và qa/asset_check.md. Mã thoát 1 khi có ảnh cần tạo lại; tạo lại trước khi dựng cảnh, không thêm vòng sau đó."""
import json, shutil, sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageStat
from paths import ROOT, resolve_asset

MIN_H = 800


def panels(im):
    """Số ô của ảnh ghép: dải ngang/dọc đồng màu (trắng hoặc đen) dày ≥ 4 px chạy hết ảnh, nằm trong 15-85% chiều ảnh."""
    g = im.convert("L")
    g.thumbnail((600, 600))
    w, h = g.size
    px = g.load()

    def gutters(n, m, get):
        """Rãnh = dải đồng màu ≥ 3 dòng, có nội dung ở CẢ HAI phía (viền trống quanh mẫu vật nền trơn không tính)."""
        flat = []
        for i in range(n):
            vals = [get(i, j) for j in range(0, m, 2)]
            flat.append(max(vals) - min(vals) < 18 and (min(vals) > 225 or max(vals) < 30))
        runs, i = 0, 0
        while i < n:
            if flat[i]:
                j = i
                while j < n and flat[j]:
                    j += 1
                if j - i >= 3 and i > 0 and j < n and not all(flat[:i]) and not all(flat[j:]):
                    runs += 1
                i = j
            else:
                i += 1
        return runs

    rows = gutters(h, w, lambda i, j: px[j, i])
    cols = gutters(w, h, lambda i, j: px[i, j])
    return (rows + 1) * (cols + 1)


def cast(im):
    r, g, b = ImageStat.Stat(im.convert("RGB").resize((128, 128))).mean
    m = max(1.0, (r + g + b) / 3)
    return (r - b) / m > 0.28 and r > g > b  # vàng/cam/sepia rõ trên cả khung


def halo(im):
    """Mép cutout sáng hơn thân: tỉ lệ sáng mép/thân > 1,35."""
    if im.mode != "RGBA":
        return False
    small = im.copy()
    small.thumbnail((400, 400))
    a = small.split()[3]
    solid = a.point(lambda v: 255 if v > 250 else 0)
    inner = solid.filter(ImageFilter.MinFilter(9))
    edge = Image.eval(Image.composite(Image.new("L", a.size, 0), solid, inner), lambda v: v)  # vùng sát mép: đặc nhưng không thuộc lõi
    lum = small.convert("L")
    if not edge.getbbox() or not inner.getbbox():
        return False
    le, li = ImageStat.Stat(lum, edge).mean[0], ImageStat.Stat(lum, inner).mean[0]
    return le > 60 and le / max(li, 1) > 1.35


def main(ep, use_ai=True):
    ep = Path(ep).resolve()
    plan = json.loads((ep / "asset_plan.json").read_text(encoding="utf-8"))
    out, need = {}, []
    for x in plan.get("assets", []):
        p = resolve_asset(ep, x["file"]) if x["kind"] != "shared" else ROOT / "assets" / x["file"]
        if not p.exists() and p.with_suffix(".png").exists():
            p = p.with_suffix(".png")
        if not p.exists():
            continue
        im = Image.open(p)
        r = {"w": im.width, "h": im.height}
        if x["kind"] == "real":
            r["panels"] = panels(im)
            if im.height < MIN_H:
                orig = ep / "assets" / "_orig" / Path(x["file"]).parent / p.name  # ngoài .cand: gen_assets xóa .cand mỗi lần chạy
                orig.parent.mkdir(parents=True, exist_ok=True)
                if not orig.exists():
                    shutil.copy2(p, orig)  # chép nguyên file, giữ đúng định dạng gốc
                k = MIN_H / im.height
                big = im.resize((round(im.width * k), MIN_H), Image.LANCZOS)
                (big.convert("RGB") if p.suffix.lower() in (".jpg", ".jpeg") else big).save(p, quality=92)
                r["upscaled_from"] = im.height
        elif x["kind"] == "ai":
            if x.get("role") == "cutout" or p.suffix == ".png":
                r["halo"] = halo(im)
                if r["halo"]:
                    need.append((x["file"], "cutout còn viền sáng ở mép: tách nền lại hoặc làm sạch viền"))
            elif cast(im):
                r["cast"] = True
                need.append((x["file"], "ảnh ám vàng/cam cả khung: tạo lại với cân bằng màu trung tính"))
        out[x["file"]] = r
    ai = []
    sheet = ep / "asset_sheet.jpg"
    if use_ai and sheet.exists():
        import review
        want = "\n".join(f"- {x['id']} ({x['kind']}): {x.get('prompt') or x.get('query', '')}" for x in plan.get("assets", []))
        prompt = ("You are an independent asset checker for a prehistory documentary (setting: " + str(plan.get("setting", "")) + "). The contact sheet shows each asset with its id under it. "
                  "Check each picture against what was requested: wrong period (modern objects, wrong era), wrong anatomy (extra limbs, wrong species features), "
                  "strange objects, garbage letters or watermarks. Genuine photos and scientific figures may contain their own labels: do not report those. "
                  "Report only real defects. Reply ONLY JSON: {\"issues\":[{\"id\":\"\",\"problem\":\"mô tả tiếng Việt\",\"fix\":\"cách sửa tiếng Việt\"}]}\n\nRequested:\n" + want)
        try:
            ai = review.ask_json(prompt, [sheet], edge=1920).get("issues", [])
        except Exception as e:  # không chấm được thì báo, không chặn
            print("Không chấm được nội dung ảnh:", str(e)[:200])
        by_id = {x["id"]: x["file"] for x in plan.get("assets", [])}
        for i in ai:
            f = by_id.get(i.get("id"))
            if f:
                out.setdefault(f, {})["ai"] = i.get("problem")
                need.append((f, f"{i.get('problem')} → {i.get('fix')}"))
    qa = ep / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "asset_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    multi = [f for f, r in out.items() if r.get("panels", 1) > 1]
    up = [f for f, r in out.items() if r.get("upscaled_from")]
    L = ["# Kiểm ảnh sau khi tải/tạo", f"- {len(out)} ảnh. Cần tạo lại: {len(need)}. Ảnh nhiều ô (phải tách ô): {len(multi)}. Đã phóng lên {MIN_H} px: {len(up)}.", ""]
    L += [f"- Tạo lại {f}: {why}" for f, why in need]
    L += [f"- Tách ô {f}: {out[f]['panels']} ô" for f in multi]
    (qa / "asset_check.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return need


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1], "--no-ai" not in sys.argv) else 0)
