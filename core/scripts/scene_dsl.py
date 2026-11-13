"""Công cụ dựng cảnh chung (HT-10): viết scenes.json gọn bằng vài hàm, mặc định đã đạt chuẩn hình (bản đồ đủ đảo, chừa dải phụ đề,
chỉ tô nước chứa địa điểm). Thay các script tạm riêng từng tập.
Dùng: viết <tập>/scene_plan.py chỉ gồm lời gọi hàm, rồi chạy: python core/scripts/scene_dsl.py <tập>
    st([0, 1], "bg-cua-hang", "left", ["leaves"], [L("tre-em", 760, 840, 430, "breathe")], start_word="lũ trẻ")
    ph([2, 2], "cua-hang-tnh2", fill=True)
    sci([3, 3], "rang-tnh2-a", region=[0.2, 0.3, 0.5, 0.5], circle=(960, 510, 520, 360))
    gm([4, 4], "vn", [(103.41, 20.21, "Huà Phăn, Lào", 0.4)], highlight=["418"])
Sau đó chạy align_srt.py --apply (điền duration_s, narration, thẻ, nguồn ảnh) và validate_scenes.py như skill build-video.
Tên file không có "/" thì tự thêm thư mục và đuôi: nền backgrounds/<tên>.jpg, cutout creatures/<tên>.png, ảnh thật photos/<tên>.jpg."""
import json, runpy, sys
from pathlib import Path

SAFE_Y = 820  # chân cutout ở y ≤ 820: dải phụ đề là y > 864 (bài học 90); Stage phóng layer độ sâu 0,8 tới 1,156 lần quanh tâm khung → 820 thành 864
FOG = ("mist", "smoke")
S = []


def _path(name, folder, ext):
    return name if "/" in name else f"{folder}/{name}{ext}"


def _add(s, kw):
    for k in ("transition", "start_word", "fixed_s"):
        if k in kw:
            s[k] = kw.pop(k)
    s.setdefault("props", {}).update(kw)
    S.append(s)
    return s


def L(asset, x, y=SAFE_Y, h=380, motion="breathe", **kw):
    """Một cutout. y là chân cutout; quá SAFE_Y thì kéo lên (không để chân chủ thể trong dải phụ đề). Bóng tiếp đất, mép mềm, cân màu do Stage tự làm."""
    if y > SAFE_Y and not kw.get("hide"):
        print(f"  scene_dsl: {asset} y={y} nằm trong dải phụ đề, kéo lên {SAFE_Y}")
        y = SAFE_Y
    lay = {"asset": _path(asset, "creatures", ".png"), "x": x, "y": y, "h": h, "depth": kw.pop("depth", 0.8), "at_s": kw.pop("at_s", -1), "enter": kw.pop("enter", "fade")}
    if motion:
        lay["motion"] = motion
    lay.update(kw)
    return lay


def _atm(atm):
    return [{"type": a} if isinstance(a, str) else a for a in (atm or [])]


def st(lines, bg, cam="in", atm=("dust",), layers=None, **kw):
    """Stage: nền + cutout + không khí. Sương/khói trên cảnh có nhân vật chỉ cảnh báo (Sếp 2026-11-06)."""
    a = _atm(atm)
    if layers and any(x["type"] in FOG for x in a):
        print(f"  scene_dsl: cảnh câu {lines} có mist/smoke trên nhân vật: tập 1 từng thành dải che hình, cân nhắc dust, leaves hoặc grade")
    pr = {"cam": cam}
    if a:
        pr["atmosphere"] = a
    if layers:
        pr["layers"] = layers
    return _add({"lines": lines, "component": "Stage", "asset": _path(bg, "backgrounds", ".jpg"), "props": pr}, kw)


def ph(lines, photo, **kw):
    """Ảnh thật. Dòng nguồn do align_srt.py --apply điền từ credits.json."""
    return _add({"lines": lines, "component": "PhotoCard", "asset": _path(photo, "photos", ".jpg"), "props": {"credit": kw.pop("credit", "")}}, kw)


def sci(lines, photo, region, circle=None, **kw):
    """Ảnh khoa học: phóng vào region trong 1,2 giây đầu rồi khoanh chi tiết (tọa độ khung, mặc định giữa vùng phóng 960x510).
    Ảnh nhiều ô thì cắt riêng từng ô thành file trước (bài học 83); chỉ khoanh chi tiết thật sự thấy rõ (bài học 89)."""
    s = ph(lines, photo, region=region, **kw)
    if circle is not False:
        x, y, w, h = circle or (960, 510, 520, 360)
        s["props"]["annotate"] = [{"type": "circle", "x": x, "y": y, "w": w, "h": h, "at_s": 1.4}]
    return s


_PLACES = None


def _marker(m):
    """(lon, lat, nhãn, at_s) hoặc theo tên trong knowledge/places.json: ("Phu Wiang", at_s) / ("Phu Wiang", at_s, "nhãn riêng")."""
    global _PLACES
    if not isinstance(m[0], str):
        a, b, c, t = m
        return dict(lon=a, lat=b, label=c, at_s=t)
    if _PLACES is None:
        _PLACES = json.loads((Path(__file__).resolve().parents[2] / "knowledge/places.json").read_text(encoding="utf-8"))["places"]
    name, t = m[0], m[1]
    p = _PLACES.get(name)
    if not p:
        sys.exit(f"scene_dsl: chưa có địa danh '{name}' trong knowledge/places.json: thêm tọa độ kèm nguồn")
    if p["loai"] == "vung":
        sys.exit(f"scene_dsl: '{name}' là vùng ({p.get('ghi_chu', '')}): dùng zones=, không dùng chấm")
    return dict(lon=p["lon"], lat=p["lat"], label=m[2] if len(m) > 2 else p.get("label", name), at_s=t)


def gm(lines, preset="vn", markers=(), arrows=(), highlight=None, cam="in", **kw):
    """Bản đồ GeoMap. preset: vn | dna | asia | sunda (đã qua kiểm đảo), hoặc truyền center=, scale=.
    markers: ("Tên trong knowledge/places.json", at_s[, nhãn]) (ưu tiên, Sếp 2026-11-07) hoặc (lon, lat, nhãn, at_s); địa danh vùng/hướng dùng zones; arrows: ((lon, lat), (lon, lat), at_s). highlight: mã ISO số của nước chứa địa điểm (mặc định chỉ Việt Nam)."""
    pr = {"cam": cam, "highlight": list(highlight or ["704"]), "markers": [_marker(m) for m in markers]}
    if preset and "center" not in kw:
        pr["preset"] = preset
    if arrows:
        pr["arrows"] = [{"from": list(f), "to": list(to), "at_s": t} for f, to, t in arrows]
    return _add({"lines": lines, "component": "GeoMap", "props": pr}, kw)


def save(ep):
    out = [{"id": f"s{i:03d}", **s} for i, s in enumerate(S, 1)]
    p = Path(ep) / "scenes.json"
    old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    doc = {**{k: v for k, v in old.items() if k != "scenes"}, "fps": 30, "scenes": out}
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} cảnh → {p}. Tiếp: python core/scripts/align_srt.py {ep} --apply")


if __name__ == "__main__":
    ep = Path(sys.argv[1]).resolve()
    plan = ep / "scene_plan.py"
    if not plan.exists():
        sys.exit(f"Chưa có {plan}: viết lời gọi st/ph/sci/gm/L theo hướng dẫn đầu file này")
    runpy.run_path(str(plan), init_globals={"st": st, "ph": ph, "sci": sci, "gm": gm, "L": L})
    save(ep)
