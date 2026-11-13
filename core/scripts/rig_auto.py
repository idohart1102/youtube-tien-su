"""Tự rig nhân vật của tập: AI chỉ khớp xương trên ảnh, script tạo rig.json, uốn khung hình, rồi AI độc lập soát lỗi.
Dùng: python core/scripts/rig_auto.py <episode_dir> <file cutout trong assets/> --plan biped|quad|human [--name ten] [--clips idle,raise,alert,walk,run]
biped: con vật đi 2 chân có đuôi (khủng long chân thú), có đi và chạy. quad: thú 4 chân, cổ, đuôi và 4 chân, có đi.
human: người nhìn ngang, đầu, tay gần và 2 chân; mặc định idle (thở, đầu, tay), walk chỉ khi ảnh gốc đang bước, 2 chân tách rõ
(--clips idle,walk). Sếp 2026-11-07: mọi người và con vật đều rig.
Không đạt thì in FAIL và mã thoát 2: scenes.json dùng ảnh gốc với motion, không chặn tiến độ."""
import argparse, json, math, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw
import review

ap = argparse.ArgumentParser()
ap.add_argument("ep")
ap.add_argument("source")
ap.add_argument("--plan", choices=["biped", "quad", "human"], required=True)
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

LEGS = " near_hip near_knee near_foot far_hip far_knee far_foot"
if a.plan == "human":
    KEYS = "neck_base head_top nose shoulder elbow hand" + LEGS + " near_toe far_toe"
    what = ("This is a side-view human figure cutout on a grid. ", "neck_base is where the neck meets the shoulders, head_top the top of the head, nose the tip of the nose, "
            "shoulder, elbow and hand belong to the arm closest to the camera (hand = fingertips). near_* is the leg closest to the camera, far_* the other leg; foot = ankle, toe = tip of that foot's toes. ")
else:
    KEYS = "neck_base head_base nose tail_base tail_mid tail_tip arm_top arm_hand"
    if a.plan == "biped":
        KEYS += LEGS
    else:
        KEYS += " fnear_top fnear_knee fnear_foot ffar_top ffar_knee ffar_foot" + LEGS
    what = ("This is a side-view animal cutout on a grid. ", "neck_base is where the neck leaves the shoulders, head_base where the head meets the neck, "
            "tail_base where the tail leaves the hips, arm_top the shoulder joint of the visible front limb and arm_hand its lowest point. "
            "near_* is the hind leg closest to the camera, far_* the other hind leg (hip, knee or hock, foot). "
            "fnear_* is the front leg closest to the camera, ffar_* the other front leg (top = where it leaves the body). ")
kp = review.ask_json(
    what[0] + "Red numbers give x (0-1000, left to right), blue numbers give y (0-1000, top to bottom). "
    f"Give the position of each body point as [x,y] on that scale: {KEYS}. " + what[1] + "If a point is hidden, estimate it. Reply ONLY JSON with those keys.", [gp], edge=1024)
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
r = 0.06 * W


def leg(name, under, hip, knee, foot, rr=None, toe=None):
    """Chi tách lớp: xương trên quay quanh hông, xương dưới quanh gối (kéo theo cả bàn chân tới mũi chân), trọng số dọc theo chi."""
    pts = [P[hip], P[knee], P[foot]] + ([P[toe]] if toe else [])
    return {"name": name, "under": under, "feather": 5, "poly": capsule(pts, rr or r),
            "bones": [{"name": f"leg_{name}", "pivot": list(P[hip]), "ramp": [P[hip], [(P[hip][0] + P[knee][0]) / 2, (P[hip][1] + P[knee][1]) / 2]]},
                      {"name": f"shin_{name}", "pivot": list(P[knee]), "ramp": [P[knee], [(P[knee][0] * 2 + P[foot][0]) / 3, (P[knee][1] * 2 + P[foot][1]) / 3]]}]}


if a.plan == "human":
    face = 1 if P["nose"][0] >= P["neck_base"][0] else -1
    S = lambda deg: deg * face
    bones = [{"name": "head", "pivot": list(P["neck_base"]), "feather": 18, "poly": half_plane(P["neck_base"], P["head_top"], far)}]
    rr = 0.045 * max(W, H)
    limbs = [leg("far", True, "far_hip", "far_knee", "far_foot", rr, "far_toe"), leg("near", False, "near_hip", "near_knee", "near_foot", rr, "near_toe"),
             {"name": "arm", "under": False, "feather": 5, "poly": capsule([P["shoulder"], P["elbow"], P["hand"]], 0.035 * max(W, H)),
              "bones": [{"name": "arm", "pivot": list(P["shoulder"]), "ramp": [P["shoulder"], P["elbow"]]},
                        {"name": "fore", "pivot": list(P["elbow"]), "ramp": [P["elbow"], P["hand"]]}]}]
    gait = lambda amp: {"leg_near": {"amp": amp, "cycles": 1}, "shin_near": {"from": S(-6), "to": S(-6), "amp": amp * 0.5, "cycles": 1, "phase": 0.15},
                        "leg_far": {"amp": amp, "cycles": 1, "phase": 0.5}, "shin_far": {"from": S(-6), "to": S(-6), "amp": amp * 0.5, "cycles": 1, "phase": 0.65},
                        "arm": {"amp": amp * 0.8, "cycles": 1, "phase": 0.5}, "fore": {"from": S(-8), "to": S(-8), "amp": amp * 0.3, "cycles": 1, "phase": 0.6},
                        "head": {"amp": 1.2, "cycles": 2}}
    clips = {
        "idle": {"n": 90, "bob": 2, "bob_cycles": 1, "bones": {"head": {"amp": 2, "cycles": 1, "phase": 0.1}, "arm": {"amp": 2.5, "cycles": 1}, "fore": {"amp": 3, "cycles": 1, "phase": 0.2}}},
        "walk": {"n": 30, "bob": 4, "bob_cycles": 2, "bones": gait(12)},
    }
    if not a.clips:  # người: walk chỉ khi ảnh gốc đang bước, 2 chân tách rõ (--clips idle,walk); tư thế cúi, ngồi, chân chồng nhau thì rách
        clips.pop("walk")
else:
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
    limbs = [leg("far", True, "far_hip", "far_knee", "far_foot"), leg("near", False, "near_hip", "near_knee", "near_foot")]
    legs2 = lambda amp, sh, ph=0.0: {"leg_near": {"amp": amp, "cycles": 1, "phase": ph}, "shin_near": {"from": S(sh), "to": S(sh), "amp": amp * 0.42, "cycles": 1, "phase": ph + 0.2},
                                     "leg_far": {"amp": amp, "cycles": 1, "phase": ph + 0.5}, "shin_far": {"from": S(sh), "to": S(sh), "amp": amp * 0.42, "cycles": 1, "phase": ph + 0.7}}
    if a.plan == "biped":
        gait = lambda amp, sh: legs2(amp, sh)
    else:  # quad: thêm 2 chân trước, nhịp chéo (sau gần cùng pha trước xa)
        limbs = [leg("ffar", True, "ffar_top", "ffar_knee", "ffar_foot"), limbs[0], leg("fnear", False, "fnear_top", "fnear_knee", "fnear_foot"), limbs[1]]
        bones[0].pop("exclude")
        front = lambda amp, sh: {k.replace("near", "fnear").replace("far", "ffar"): v for k, v in legs2(amp, -sh, 0.5).items()}
        gait = lambda amp, sh: {**legs2(amp, sh), **front(amp * 0.9, sh)}
    clips["walk"] = {"n": 36 if a.plan == "quad" else 30, "bob": 3 if a.plan == "quad" else 5, "bob_cycles": 2,
                     "bones": {**up, "neck": {"from": lift * 0.85, "to": lift * 0.85, "amp": 1.6, "cycles": 2}, **gait(10 if a.plan == "quad" else 14, 3)}}
    if a.plan == "biped":
        clips["run"] = {"n": 16, "bob": 12, "bob_cycles": 2, "bones": {**up, "neck": {"from": lift * 0.65, "to": lift * 0.65, "amp": 2.5, "cycles": 2}, **gait(24, 6)}}
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
    "These are frames of one animated " + ("human figure" if a.plan == "human" else "animal") + " cutout. Check for animation defects only: detached fragments, broken or torn limbs, stretched or collapsed neck, "
    'head separated from body, floating pieces. Reply ONLY JSON: {"score":0-10,"defects":["..."]}. 10 means clean. Any detached piece means score below 6.', [sheet_p], edge=1536)
(tmp / f"rig_{name}.json").write_text(json.dumps({"plan": a.plan, "keypoints": kp, "verdict": verdict}, ensure_ascii=False, indent=1), encoding="utf-8")
gp.unlink(missing_ok=True)
ok = verdict.get("score", 0) >= 7
print(("OK" if ok else "FAIL"), verdict)
sys.exit(0 if ok else 2)
