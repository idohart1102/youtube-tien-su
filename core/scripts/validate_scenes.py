"""Kiểm tra scenes.json theo schema và kiểm tra asset có tồn tại. Không tốn token."""
import json, sys
from pathlib import Path
from jsonschema import validate
from paths import ROOT, resolve_asset

p = Path(sys.argv[1])
data = json.loads(p.read_text(encoding="utf-8"))
validate(data, json.loads((ROOT / "core/templates/scenes.schema.json").read_text(encoding="utf-8")))
def used(s):  # ảnh nền + ảnh lớp (Parallax), mảnh cắt dán (Collage), cutout (SizeCompare)
    pr = s.get("props", {})
    yield s.get("asset")
    for x in pr.get("layers", []) + pr.get("items", []):
        yield x.get("asset") or x.get("cutout") or (x.get("sprite") or {}).get("base")
    if pr.get("sprite"):
        yield pr["sprite"]["base"]


missing = sorted({a for s in data["scenes"] for a in used(s) if a and not resolve_asset(p.parent.resolve(), a).exists()})
total = sum(s["duration_s"] for s in data["scenes"])
print(f"{len(data['scenes'])} cảnh, {total/60:.1f} phút")
problems = []
svg = [s["id"] for s in data["scenes"] if s["component"] == "Creature"]
if svg:
    problems.append("Creature vẽ SVG đã bỏ, dùng Parallax với cutout PNG: " + ", ".join(svg))
tl = p.parent / "timeline.json"
if tl.exists():  # dựng từ audio + srt: tổng thời lượng phải khớp audio, nhịp cảnh theo style
    end = json.loads(tl.read_text(encoding="utf-8"))["audio_end"]
    if abs(total - end) > 1.0:
        problems.append(f"Tổng {total:.1f}s lệch audio {end:.1f}s")
    t = 0.0
    for s in data["scenes"]:
        if s["duration_s"] > 20.5:
            problems.append(f"Cảnh {s['id']} dài {s['duration_s']:.1f}s (> 20s)")
        elif t < 60 and s["duration_s"] > 8.5 and s["component"] != "TitleCard":
            problems.append(f"Cảnh {s['id']} ở phút đầu dài {s['duration_s']:.1f}s (> 8s)")
        t += s["duration_s"]
    # Câu hỏi không được minh hoạ bằng đáp án: asset có answer_of (asset_plan.json) chỉ hiện rõ từ câu [ĐÁP] trở đi
    lines = json.loads(tl.read_text(encoding="utf-8"))["lines"]
    ans_at = {q.split(":", 1)[1]: l["start"] for l in lines for q in l.get("qa", []) if q.startswith("ĐÁP:")}
    plan_p = p.parent / "asset_plan.json"
    answer_of = {}
    if plan_p.exists():
        for x in json.loads(plan_p.read_text(encoding="utf-8")).get("assets", []):
            if x.get("answer_of"):
                answer_of[x["file"]] = answer_of[str(Path(x["file"]).with_suffix(".png"))] = x["answer_of"]
    t = 0.0
    for s in data["scenes"]:
        pr = s.get("props", {})
        hd = pr.get("hide") if isinstance(pr.get("hide"), dict) else {}
        shown = [(s.get("asset"), 0, hd.get("mode"), hd.get("unmask_s"), hd.get("answer_of"))]
        for i, x in enumerate(pr.get("layers", []) + pr.get("items", [])):
            shown.append((x.get("asset") or x.get("cutout"), x.get("at_s", 0 if s["component"] != "Collage" else i * 0.6),
                          x.get("hide"), x.get("unmask_s"), x.get("answer_of")))
        for a, at, hide, unmask, q in shown:
            q = q or answer_of.get(a)
            if not a or not q:
                continue
            if q not in ans_at:
                problems.append(f"Cảnh {s['id']}: {a} là đáp án của {q} nhưng storyboard chưa có [ĐÁP: {q}]")
                continue
            visible = t + (unmask if hide and unmask is not None else float("inf") if hide else at)
            if visible < ans_at[q] - 0.5:
                problems.append(f"Cảnh {s['id']}: lộ đáp án {q} ({a}) trước câu trả lời, thêm hide (silhouette/fog/blur/keyhole)")
        t += s["duration_s"]

# Giới hạn chuyển động: mỗi cảnh 1 chuyển động máy + tối đa 1 hiệu ứng chính + tối đa 1 lớp chuyển động lặp
warn, shakes, hero_use, prev_cam, prev_hero = [], 0, {}, None, set()


def camera(s):
    pr = s.get("props", {})
    if s["component"] in ("Parallax", "Stage"):
        return {"left": "pan-l", "right": "pan-r", "up": "tilt-d", "down": "tilt-u"}.get(pr.get("cam", "in"), pr.get("cam", "in"))
    if s["component"] == "KenBurns":
        dx, dy, dz = pr.get("x1", 0) - pr.get("x0", 0), pr.get("y1", 0) - pr.get("y0", 0), pr.get("z1", 1.15) - pr.get("z0", 1.05)
        return ("pan-r" if dx > 0 else "pan-l") if abs(dx) >= 20 else ("tilt-d" if dy > 0 else "tilt-u") if abs(dy) >= 20 else "in" if dz >= 0 else "out"
    return None


for s in data["scenes"]:
    pr = s.get("props", {})
    parts = pr.get("layers", []) + pr.get("items", [])
    hero = {k for k in ("spotlight", "shake") if pr.get(k)}
    if any(x.get("reveal") for x in parts):
        hero.add("wipe")
    if any(x.get("unmask_s") is not None for x in parts) or (isinstance(pr.get("hide"), dict) and pr["hide"].get("unmask_s") is not None):
        hero.add("unmask")
    if len(hero) > 1:
        problems.append(f"Cảnh {s['id']}: {len(hero)} hiệu ứng chính ({', '.join(sorted(hero))}), chỉ giữ 1")
    if sum(1 for x in parts if x.get("motion")) > 1:
        problems.append(f"Cảnh {s['id']}: nhiều lớp có motion, chỉ cutout chính được chuyển động lặp")
    if len(pr.get("annotate", [])) > 2:
        problems.append(f"Cảnh {s['id']}: quá 2 nét annotate")
    shakes += "shake" in hero
    for h in hero:
        hero_use[h] = hero_use.get(h, 0) + 1
    if hero & prev_hero:
        warn.append(f"Cảnh {s['id']} lặp hiệu ứng {', '.join(sorted(hero & prev_hero))} của cảnh trước")
    cam = camera(s)
    if cam and cam == prev_cam:
        warn.append(f"Cảnh {s['id']} cùng hướng máy ({cam}) với cảnh trước")
    prev_cam, prev_hero = cam, hero
if shakes > 3:
    problems.append(f"{shakes} cảnh có shake, tối đa 3 mỗi tập")
n = len(data["scenes"])
for h, c in hero_use.items():
    if n >= 20 and c > 0.15 * n and h != "unmask":
        warn.append(f"Hiệu ứng {h} dùng {c}/{n} cảnh (> 15%), đổi bớt cho đa dạng")
if warn:
    print("Cảnh báo:", *warn, sep="\n  ")
if problems:
    print("Cần sửa:", *problems, sep="\n  ")
if missing:
    print("Thiếu asset:", *missing, sep="\n  ")
    sys.exit(1)
if problems:
    sys.exit(1)
print("OK")
