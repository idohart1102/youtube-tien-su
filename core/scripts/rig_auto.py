"""Tự rig nhân vật của tập: AI chỉ khớp xương trên ảnh, script tạo rig.json, uốn khung hình, rồi AI độc lập soát lỗi.
Dùng: python core/scripts/rig_auto.py <episode_dir> <file cutout trong assets/> --plan biped|quad [--name ten] [--clips idle,raise,alert,walk,run]
biped: có đi và chạy. quad: chỉ cổ và đuôi, di chuyển bằng path. Không đạt thì in FAIL và mã thoát 2: scenes.json dùng ảnh gốc với motion, không chặn tiến độ."""
import argparse, json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
import review

ap = argparse.ArgumentParser()
ap.add_argument("ep")
ap.add_argument("source")
ap.add_argument("--plan", choices=["biped", "quad"], required=True)
ap.add_argument("--name")
ap.add_argument("--clips", default="")
a = ap.parse_args()
ep = Path(a.ep).resolve()
name = a.name or Path(a.source).stem
src = ep / "assets" / a.source
im = Image.open(src).convert("RGBA")
W, H = im.size
tmp = ep / "qa"
tmp.mkdir(exist_ok=True)

# Lưới 0-1000 giúp AI đọc toạ độ chính xác hơn
scale = 1024 / max(W, H)
grid = Image.new("RGBA", im.size, "#ffffff")
grid.alpha_composite(im)
dr = ImageDraw.Draw(grid)
for n in range(0, 1001, 100):
    x, y = W * n / 1000, H * n / 1000
    dr.line([(x, 0), (x, H)], fill="#ff0066", width=max(1, W // 900))
    dr.line([(0, y), (W, y)], fill="#0066ff", width=max(1, W // 900))
    dr.text((x + 3, 3), str(n), fill="#ff0066", font_size=max(14, W // 60))
    dr.text((3, y + 3), str(n), fill="#0066ff", font_size=max(14, W // 60))
gp = tmp / f"rig_{name}_grid.png"
grid.convert("RGB").resize((round(W * scale), round(H * scale))).save(gp)

KEYS = "neck_base head_base nose tail_base tail_mid tail_tip arm_top arm_hand"
if a.plan == "biped":
    KEYS += " near_hip near_knee near_foot far_hip far_knee far_foot"
kp = review.ask_json(
    "This is a side-view animal cutout on a grid. Red numbers give x (0-1000, left to right), blue numbers give y (0-1000, top to bottom). "
    f"Give the position of each body point as [x,y] on that scale: {KEYS}. neck_base is where the neck leaves the shoulders, head_base where the head meets the neck, "
    "tail_base where the tail leaves the hips, arm_top the shoulder joint of the visible front limb and arm_hand its lowest point. "
    "near_* is the hind leg closest to the camera, far_* the other hind leg. Reply ONLY JSON with those keys.", [gp], edge=1024)
P = {k: (v[0] * W / 1000, v[1] * H / 1000) for k, v in kp.items()}


def unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy) or 1
    return dx / d, dy / d


def half_plane(p, q, far):
    """Vùng phía q của đường vuông góc đi qua p: khi xoay vẫn nằm trong vùng nên không rách."""
    u = unit(p, q)
    v = (-u[1], u[0])
    return [[p[0] + v[0] * far, p[1] + v[1] * far], [p[0] + (u[0] + v[0]) * far, p[1] + (u[1] + v[1]) * far],
            [p[0] + (u[0] - v[0]) * far, p[1] + (u[1] - v[1]) * far], [p[0] - v[0] * far, p[1] - v[1] * far]]


def capsule(pts, r):
    left, right = [], []
    for i, p in enumerate(pts):
        a0, b0 = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        u = unit(a0, b0)
        v = (-u[1], u[0])
        left.append([p[0] + v[0] * r, p[1] + v[1] * r])
        right.append([p[0] - v[0] * r, p[1] - v[1] * r])
    e = unit(pts[-2], pts[-1])
    return left + [[pts[-1][0] + e[0] * r, pts[-1][1] + e[1] * r]] + right[::-1]


far = 2 * max(W, H)
arm = capsule([P["arm_top"], P["arm_hand"]], 0.05 * W)
bones = [
    {"name": "neck", "pivot": list(P["neck_base"]), "feather": 45, "poly": half_plane(P["neck_base"], P["head_base"], far), "exclude": [arm]},
    {"name": "head", "pivot": list(P["head_base"]), "feather": 22, "poly": half_plane(P["head_base"], P["nose"], far)},
    {"name": "tail", "pivot": list(P["tail_base"]), "feather": 60, "poly": half_plane(P["tail_base"], P["tail_mid"], far)},
    {"name": "tail2", "pivot": list(P["tail_mid"]), "feather": 50, "poly": half_plane(P["tail_mid"], P["tail_tip"], far)},
]

# Góc nâng cổ: đưa cổ về gần ngang hoặc ngẩng nhẹ. Ảnh quay trái thì góc đổi dấu.
vec = unit(P["neck_base"], P["head_base"])
face = 1 if P["nose"][0] >= P["tail_base"][0] else -1
now = math.degrees(math.atan2(vec[1], vec[0] * face))  # >0 là cổ chúi xuống
lift = -max(6.0, min(42.0, now + 4)) * face
S = lambda deg: deg * face  # đuôi và chân đổi dấu theo hướng nhìn
idle = {"neck": {"amp": 1.4, "cycles": 1}, "head": {"amp": 2, "cycles": 2, "phase": 0.15}, "tail": {"amp": 1.4, "cycles": 1}, "tail2": {"amp": 2.2, "cycles": 1, "phase": 0.2}}
up = {"neck": {"from": lift, "to": lift, "amp": 1.2, "cycles": 1}, "head": {"from": lift * 0.2, "to": lift * 0.2, "amp": 2, "cycles": 2}, "tail": {"amp": 1.2, "cycles": 1}, "tail2": {"amp": 2, "cycles": 1, "phase": 0.2}}
clips = {
    "idle": {"n": 90, "bones": idle},
    "raise": {"n": 24, "bones": {"neck": {"from": 0, "to": lift}, "head": {"from": 0, "to": lift * 0.2}}},
    "alert": {"n": 60, "bones": up},
}
limbs = []
if a.plan == "biped":
    r = 0.06 * W
    limbs = [
        {"name": "far", "under": True, "feather": 5, "poly": capsule([P["far_hip"], P["far_knee"], P["far_foot"]], r),
         "bones": [{"name": "leg_far", "pivot": list(P["far_hip"]), "ramp_y": [P["far_hip"][1], P["far_hip"][1] + 0.1 * H]}, {"name": "shin_far", "pivot": list(P["far_knee"]), "ramp_y": [P["far_knee"][1] - 10, P["far_knee"][1] + 0.1 * H]}]},
        {"name": "near", "under": False, "feather": 5, "poly": capsule([P["near_hip"], P["near_knee"], P["near_foot"]], r),
         "bones": [{"name": "leg_near", "pivot": list(P["near_hip"]), "ramp_y": [P["near_hip"][1], P["near_hip"][1] + 0.1 * H]}, {"name": "shin_near", "pivot": list(P["near_knee"]), "ramp_y": [P["near_knee"][1] - 10, P["near_knee"][1] + 0.1 * H]}]},
    ]
    gait = lambda amp, sh: {"leg_near": {"amp": amp, "cycles": 1}, "shin_near": {"from": S(sh), "to": S(sh), "amp": amp * 0.42, "cycles": 1, "phase": 0.2},
                            "leg_far": {"amp": amp, "cycles": 1, "phase": 0.5}, "shin_far": {"from": S(sh), "to": S(sh), "amp": amp * 0.42, "cycles": 1, "phase": 0.7}}
    clips["walk"] = {"n": 30, "bob": 5, "bob_cycles": 2, "bones": {**{k: v for k, v in up.items()}, "neck": {"from": lift * 0.85, "to": lift * 0.85, "amp": 1.6, "cycles": 2}, **gait(14, 3)}}
    clips["run"] = {"n": 16, "bob": 12, "bob_cycles": 2, "bones": {**{k: v for k, v in up.items()}, "neck": {"from": lift * 0.65, "to": lift * 0.65, "amp": 2.5, "cycles": 2}, **gait(24, 6)}}
if a.clips:
    keep = set(a.clips.split(","))
    clips = {k: v for k, v in clips.items() if k in keep}

spec = {"source": a.source, "out": f"creatures/rig/{name}", "scale": 0.5, "pad": {"left": 0, "top": round(0.2 * H), "right": round(0.08 * W)},
        "outline_from": "alert" if "alert" in clips else next(iter(clips)), "bones": bones, "limbs": limbs, "clips": clips}
(ep / "rig").mkdir(exist_ok=True)
sp = ep / "rig" / f"{name}.rig.json"
sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
print("Khớp xương:", {k: [round(x) for x in v] for k, v in kp.items()})
subprocess.run([sys.executable, str(Path(__file__).with_name("rig_cutout.py")), str(sp)], check=True)

# Bảng khung hình: khung rủi ro nhất của mỗi chuyển động
out = ep / "assets" / spec["out"]
samples = []
for c, v in clips.items():
    samples += [f"{c}/{i:03d}" for i in sorted({0, v["n"] // 4, v["n"] // 2, 3 * v["n"] // 4})]
cols, tw, th = 4, 480, 260
sheet = Image.new("RGB", (cols * tw, -(-len(samples) // cols) * th), "#5a6470")
for n, f in enumerate(samples):
    fr = Image.open(out / f"{f}.webp").convert("RGBA")
    fr.thumbnail((tw - 8, th - 8))
    sheet.paste(fr, ((n % cols) * tw + 4, (n // cols) * th + 4), fr)
sheet_p = tmp / f"rig_{name}_sheet.jpg"
sheet.save(sheet_p, quality=85)
verdict = review.ask_json(
    "These are frames of one animated animal cutout. Check for animation defects only: detached fragments, broken or torn limbs, stretched or collapsed neck, "
    'head separated from body, floating pieces. Reply ONLY JSON: {"score":0-10,"defects":["..."]}. 10 means clean. Any detached piece means score below 6.', [sheet_p], edge=1536)
(tmp / f"rig_{name}.json").write_text(json.dumps({"plan": a.plan, "keypoints": kp, "verdict": verdict}, ensure_ascii=False, indent=1), encoding="utf-8")
gp.unlink(missing_ok=True)
ok = verdict.get("score", 0) >= 7
print(("OK" if ok else "FAIL"), verdict)
sys.exit(0 if ok else 2)
