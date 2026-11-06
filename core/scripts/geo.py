"""Phép chiếu Mercator giống GeoMap.tsx (d3 geoMercator, translate [960, 540]) để máy kiểm bản đồ mà không cần render.
Mẫu bản đồ dùng chung với GeoMap: core/remotion/lib/map_presets.json."""
import json, math
from paths import ROOT

PRESETS = json.loads((ROOT / "core/remotion/lib/map_presets.json").read_text(encoding="utf-8"))
ISLANDS = {"Hoàng Sa": (112.0, 16.5), "Trường Sa": (114.3, 10.0)}
# Điểm nằm trong lãnh thổ Việt Nam: có 1 điểm trong khung là bản đồ có Việt Nam
VN_POINTS = [(105.85, 21.03), (103.0, 22.4), (106.7, 10.8), (108.2, 16.05), (105.0, 9.2), (107.6, 21.5), (104.9, 19.0), (108.0, 13.0)]
ZOOM_MAX = 1.08  # GeoMap cam in/out phóng tối đa 8% quanh tâm khung


def view(pr):
    pre = PRESETS.get(pr.get("preset") or "", {})
    return pr.get("center") or pre.get("center") or [108, 14], pr.get("scale") or pre.get("scale") or 2200


def project(lon, lat, center, scale):
    y = lambda p: math.log(math.tan(math.pi / 4 + math.radians(p) / 2))
    return 960 + scale * math.radians(lon - center[0]), 540 - scale * (y(lat) - y(center[1]))


def on_screen(x, y, margin=40, zoom=ZOOM_MAX):
    """Điểm còn trong khung kể cả lúc máy phóng tối đa."""
    x, y = 960 + (x - 960) * zoom, 540 + (y - 540) * zoom
    return margin < x < 1920 - margin and margin < y < 1080 - margin


def island_problems(pr):
    """Bản đồ có Việt Nam trong khung mà Hoàng Sa hoặc Trường Sa ngoài khung."""
    c, s = view(pr)
    if not any(on_screen(*project(lo, la, c, s), margin=0, zoom=1.0) for lo, la in VN_POINTS):
        return []
    return [k for k, (lo, la) in ISLANDS.items() if not on_screen(*project(lo, la, c, s))]
