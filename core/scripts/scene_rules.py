"""Luật máy đo được trên scenes.json (HT-02, HT-04), không tốn token. validate_scenes.py gọi check() rồi áp mức theo MODE.
Mỗi luật trả về [(mã cảnh, lời nhắc)]. Mức: "chan" = Cần sửa (produce dừng), "canh-bao" = chỉ in ra.
Luật mới chạy ở mức cảnh báo cho tới khi đo báo nhầm ≤ 10% số cảnh trên tập thật (đo ngày 2026-11-05 trên Tràng An và gen-denisova,
xem docs/de-xuat-he-thong.md mục Tình trạng triển khai). "anh-nho" và "giu-bo-cuc" giữ cảnh báo (thẻ ảnh nhỏ cố ý, cảnh dài tới 12 s được phép)."""
import json
from pathlib import Path
from PIL import Image
import geo
from paths import resolve_asset

W, H = 1920, 1080
SUB_Y = 864  # 1/5 dưới khung là dải phụ đề (bài học 90)
SUB_X = (160, 1760)  # phụ đề 1 dòng canh giữa, Overlay.tsx left/right 160
MODE = {
    # Đo 2026-11-05 (báo nhầm = báo trên bản cuối tập 1 mà QC v4 không thấy lỗi): ban-do-dao 0%, ban-do-to-mau 3,7%, mist 0%,
    # phu-de-layer 7,4%, phu-de-anh 4,4% (bắt đúng 9:46-9:58), region-cat 1,5%, tinh 0% tập 1 nhưng 16% Tràng An (tập cũ, chưa đo render).
    # Sếp 2026-11-06: chỉ chặn điều sai khách quan. Bản đồ thiếu Hoàng Sa/Trường Sa là chặn; còn lại là cảnh báo để người dựng tự xét.
    "ban-do-dao": "chan", "ban-do-to-mau": "canh-bao", "mist": "canh-bao", "phu-de-layer": "canh-bao", "phu-de-anh": "canh-bao",
    "anh-nho": "canh-bao", "tinh": "canh-bao", "giu-bo-cuc": "canh-bao", "region-cat": "canh-bao", "anh-nhieu-o": "canh-bao",
}
VN_NEIGHBORS = {"418", "116", "156"}  # Lào, Campuchia, Trung Quốc
CONTINUOUS_ATM = {"rain", "snow", "embers", "firerain", "ash", "leaves", "smoke", "mist", "fireflies", "debris"}
_size = {}


def size(ep, a):
    if a not in _size:
        p = resolve_asset(ep, a)
        try:
            with Image.open(p) as im:
                _size[a] = im.size
        except OSError:
            _size[a] = None
    return _size[a]


def photo_rect(ep, s, zones):
    """Vùng chủ thể (zones.json) của ảnh PhotoCard trên khung 1080 lúc cuối cảnh: (y_trên, y_dưới, cao hiển thị của ảnh)."""
    pr, a = s.get("props", {}), s.get("asset")
    wh = size(ep, a) if a else None
    if not wh:
        return None
    iw, ih = wh
    sub = (zones.get(a) or {}).get("subject") or [0, 0, 1, 1]
    z = pr.get("z", 1.08)
    r = pr.get("region")
    if pr.get("fill"):
        k = max(W / iw, H / ih) * z * 1.02
        dh, cy, top, bot = ih * k, 540, 0, H
        v = lambda u: cy + (u - 0.5) * dh
    else:
        k = min(1400 / iw, 800 / ih)
        dh, cy = ih * k, 510
        if r:
            rz = min(3, 1 / max(r[2], r[3] * 1.4 / 1.75))
            rc = r[1] + r[3] / 2
            v = lambda u: cy + (u - rc) * dh * z * rz
            top, bot = 110, 910  # khung có region cắt theo khung 1400x800
        else:
            v = lambda u: cy + (u - 0.5) * dh * z
            top, bot = 0, H
    y0, y1 = max(top, v(sub[1])), min(bot, v(sub[1] + sub[3]))
    return y0, y1, dh * z


def events(s):
    pr = s.get("props", {})
    ts = [x.get("at_s") for k in ("cards", "badges", "annotate", "markers", "arrows", "zones", "layers", "items", "grade", "atmosphere") for x in pr.get(k, [])]
    ts += [x.get("unmask_s") for x in pr.get("layers", []) + pr.get("items", [])]
    ts += [k.get("at_s") for x in pr.get("layers", []) for k in x.get("path", [])]
    ts += [(pr.get(k) or {}).get("at_s") for k in ("spotlight", "shake", "quake")]
    if isinstance(pr.get("hide"), dict):
        ts.append(pr["hide"].get("unmask_s"))
    if s["component"] == "GeoMap":
        ts += [0.5 + i * 0.5 for i, m in enumerate(pr.get("markers", [])) if m.get("at_s") is None]
    return sorted(x for x in ts if isinstance(x, (int, float)) and 0 <= x < s["duration_s"])


def moving(s):
    """Cảnh có chuyển động liên tục đủ thấy (không tính bụi: quá kín đáo, cảnh 1:58 tập 1 có bụi vẫn đo ra gần tĩnh)."""
    pr, d = s.get("props", {}), s["duration_s"]
    fog = isinstance(pr.get("hide"), dict) and pr["hide"].get("mode") in ("fog", "blur")
    layers = [x for x in pr.get("layers", []) + pr.get("items", []) if not x.get("hide")]
    if any(x.get(k) for x in layers for k in ("motion", "path", "drift", "wind", "sprite")):
        return True
    if pr.get("water") or pr.get("quake") or any(a.get("type") in CONTINUOUS_ATM for a in pr.get("atmosphere", [])):
        return True
    if fog:
        return False
    c = s["component"]
    if c == "PhotoCard":
        rate = (pr.get("z", 1.08) - 1) / d
    elif c == "KenBurns":
        rate = abs(pr.get("z1", 1.15) - pr.get("z0", 1.05)) / d + (abs(pr.get("x1", 0) - pr.get("x0", 0)) + abs(pr.get("y1", 0) - pr.get("y0", 0))) / d / 1500
    elif c in ("Stage", "Parallax"):
        rate = (0.06 if pr.get("cam", "in") in ("in", "out") else 80 / 1500) / d
    elif c == "GeoMap":
        rate = 0.1 / d  # camera tuyến tính từ 2026-11-07
    else:
        return True  # TitleCard, Collage, SizeCompare, GeoClock... có diễn biến riêng
    return rate >= 0.004  # hiệu chỉnh trên tập 1 bản cuối: chỉ còn 1:58 gần tĩnh, khớp render_check


def check(data, ep, plan=None, zones=None, asset_check=None):
    ep = Path(ep)
    plan, zones, asset_check = plan or {}, zones or {}, asset_check or {}
    out = {k: [] for k in MODE}
    t = 0.0
    run = []  # (asset chính, thời lượng) các cảnh liền nhau cùng bố cục
    for s in data["scenes"]:
        pr, sid, c, d = s.get("props", {}), s["id"], s["component"], s["duration_s"]
        at = f"{int(t // 60)}:{int(t % 60):02}"
        if c == "GeoMap":
            miss = geo.island_problems(pr)
            if miss:
                out["ban-do-dao"].append((sid, f"Cảnh {sid} ({at}): bản đồ có Việt Nam nhưng {', '.join(miss)} ngoài khung. Dùng preset \"vn\"/\"dna\"/\"asia\" hoặc chỉnh center/scale (bài học 88)"))
            hi = set(map(str, pr.get("highlight", ["704"])))
            if pr.get("markers") and "704" in hi and hi & VN_NEIGHBORS:
                out["ban-do-to-mau"].append((sid, f"Cảnh {sid} ({at}): tô cùng màu Việt Nam và nước láng giềng ({', '.join(sorted(hi & VN_NEIGHBORS))}) khi có chấm địa điểm: chỉ tô nước chứa địa điểm, ghi tên nước trong nhãn (bài học 82)"))
        # Sương/khói trên cảnh có nhân vật, layer chủ thể hoặc ảnh thật (bài học 87). Cảnh phong cảnh trống vẫn dùng được.
        fog = [a.get("type") for a in pr.get("atmosphere", []) if a.get("type") in ("mist", "smoke")]
        has_subject = c in ("PhotoCard", "KenBurns", "Collage", "FossilReveal") or any(not x.get("hide") for x in pr.get("layers", []))
        if fog and has_subject:
            out["mist"].append((sid, f"Cảnh {sid} ({at}): {'/'.join(fog)} trên cảnh có nhân vật hoặc ảnh chủ thể, dùng dust, leaves hoặc grade (bài học 87)"))
        # Dải phụ đề: cutout chủ thể đứng trong 1/5 dưới khung
        if c in ("Stage", "Parallax"):
            for x in pr.get("layers", []):
                if x.get("hide") or (x.get("h") or 600) < 200:
                    continue
                # Stage phóng layer quanh focus theo độ sâu: chân ở y thật = (y - cy) * s + cy lúc cuối cảnh
                cam = pr.get("cam", "in")
                zoom = 0.06 if cam in ("in", "out") else 0.04 if cam in ("up", "down") else 0.02
                dz = max(0, x.get("dz") or 0)  # đi lại gần: cuối cảnh to thêm dz, chân xuống thêm 160*dz
                k_s, cy = (1 + zoom * (1 + 2 * x.get("depth", 0.6))) * (1 + dz), (pr.get("focus") or [W / 2, H / 2])[1]
                ys = [(yy + 160 * dz - cy) * k_s + cy for yy in [x.get("y", H - 80)] + [k.get("y") for k in x.get("path", []) if k.get("y") is not None]]
                asp = x.get("aspect") or ((lambda wh: wh[0] / wh[1] if wh else 1)(size(ep, x["asset"]) if x.get("asset") else None))
                half = (x.get("h") or 600) * asp / 2
                xs = [x.get("x", W / 2)] + [k.get("x") for k in x.get("path", []) if k.get("x") is not None]
                over = any(xx + half > SUB_X[0] and xx - half < SUB_X[1] for xx in xs)
                if max(ys) > SUB_Y and over:
                    out["phu-de-layer"].append((sid, f"Cảnh {sid} ({at}): {x.get('asset') or 'sprite'} đứng ở y={max(ys):.0f}, chân chủ thể nằm trong dải phụ đề (y > {SUB_Y}): nâng y ≤ {SUB_Y} hoặc giảm h (bài học 90)"))
        if c == "PhotoCard" and s.get("asset"):
            rect = photo_rect(ep, s, zones)
            if rect:
                y0, y1, dh = rect
                spill = y1 - SUB_Y
                if spill > 30 and spill > 0.1 * max(1, y1 - y0):
                    out["phu-de-anh"].append((sid, f"Cảnh {sid} ({at}): vùng chủ thể ảnh tràn {spill:.0f} px vào dải phụ đề: dùng region phóng lên trên, bỏ fill hoặc giảm z (bài học 90)"))
                if not pr.get("fill") and not pr.get("region") and dh < 700:
                    out["anh-nho"].append((sid, f"Cảnh {sid} ({at}): ảnh thật chỉ cao {dh:.0f} px trên khung, nên ≥ 700 (fill, region hoặc ảnh lớn hơn)"))
            r, sub = pr.get("region"), (zones.get(s["asset"]) or {}).get("subject")
            if r and sub:
                ix = max(0, min(r[0] + r[2], sub[0] + sub[2]) - max(r[0], sub[0])) * max(0, min(r[1] + r[3], sub[1] + sub[3]) - max(r[1], sub[1]))
                k = ix / max(1e-6, sub[2] * sub[3])
                inside = ix / max(1e-6, r[2] * r[3])
                if 0.25 < k < 0.85 and inside < 0.9:
                    out["region-cat"].append((sid, f"Cảnh {sid} ({at}): region chỉ giữ {k:.0%} vùng chủ thể, cắt dở mẫu vật: mở rộng region hoặc phóng hẳn vào chi tiết (HT-04)"))
        for a in [s.get("asset")] if pr.get("region") or pr.get("annotate") else []:  # phóng/khoanh một phần của ảnh nhiều ô thì cắt dở ô bên cạnh
            if a and (asset_check.get(a) or {}).get("panels", 1) > 1:
                out["anh-nhieu-o"].append((sid, f"Cảnh {sid} ({at}): {a} là ảnh nhiều ô ({asset_check[a]['panels']} ô): cắt riêng từng ô thành file, không dùng region trên cả bảng (bài học 83)"))
        # Khoảnh khắc tĩnh: cùng ngưỡng render_check (gần tĩnh ≥ 1,5 s), tính từ sự kiện trong cảnh
        if not moving(s) and c != "TitleCard":
            busy = [(0.0, 0.5)] + [(e, e + 0.8) for e in events(s)]
            if c == "PhotoCard" and pr.get("region"):
                busy.append((0.0, 1.2))
            if c == "PhotoCard" and pr.get("sweep", d >= 4):
                busy.append((d * 0.25, d * 0.25 + 1.33))
            busy.sort()
            gap, cur, where = 0.0, 0.0, 0.0
            for a0, b0 in busy:
                if a0 - cur > gap:
                    gap, where = a0 - cur, cur
                cur = max(cur, b0)
            if d - cur > gap:
                gap, where = d - cur, cur
            if gap >= 1.5:
                out["tinh"].append((sid, f"Cảnh {sid} ({at}): khoảng {gap:.1f}s gần tĩnh từ giây {where:.1f} của cảnh (máy chậm, không sự kiện): thêm motion, lá, khói nhẹ ngoài chủ thể, nét khoanh hoặc tăng zoom/pan"))
        # Giữ một bố cục quá 6 s: cùng ảnh chính quay lại trong lúc chỉ chen cảnh ngắn ≤ 2,5 s
        main = (s.get("asset") or "") + "|" + ",".join(x.get("asset") or "" for x in pr.get("layers", []) + pr.get("items", [])) if s.get("asset") or pr.get("items") else (json.dumps(pr.get("center")) if c == "GeoMap" else None)
        cont = False
        if run and len(run) == 2 and run[0][0] == main:
            run, cont = [[main, run[0][1] + d]], True  # cảnh chen ngắn không tính là đổi bố cục
        elif run and len(run) == 1 and run[0][0] == main:
            run[0][1] += d
            cont = True
        elif run and len(run) == 1 and d <= 2.5:
            run.append([main, d])
        else:
            run = [[main, d]] if main else []
        if cont and run[0][1] > 6 and not events(s):
            out["giu-bo-cuc"].append((sid, f"Cảnh {sid} ({at}): bố cục {main.strip('|')} đã giữ {run[0][1]:.1f}s qua nhiều cảnh mà không có sự kiện mới: đổi góc, đổi ảnh hoặc thêm chi tiết"))
        t += d
    # Ngoại lệ đã xét: props.allow = {"mã luật": "lý do"} (approver ghi, ví dụ ảnh hang phủ kín khung cố ý)
    allow = {s["id"]: (s.get("props") or {}).get("allow") or {} for s in data["scenes"]}
    return {k: [(sid, m) for sid, m in v if k not in allow.get(sid, {})] for k, v in out.items()}
