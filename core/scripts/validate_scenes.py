"""Kiểm tra scenes.json theo schema và kiểm tra asset có tồn tại. Không tốn token.
Sếp 2026-11-06: chỉ chặn (Cần sửa) điều sai khách quan hoặc quyết định của Sếp: thiếu asset, lệch audio, nhịp, lộ đáp án, câu hỏi thiếu thẻ,
thiếu dấu, cảnh không có gì chuyển động, quá nhiều thẻ chữ, bản đồ thiếu đảo. Luật thẩm mỹ (số hiệu ứng, cutout đứng yên, hình lệch lời theo tên gọi...) là cảnh báo.
Dùng: python core/scripts/validate_scenes.py <tập>/scenes.json [--report <file.json>] (ghi số cảnh vi phạm theo từng luật của scene_rules.py)."""
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
problems, warn = [], []
if data.get("format") == "9:16":
    bad = [s["id"] for s in data["scenes"] if s["component"] != "Stage"]
    if bad:
        problems.append("Video 9:16 hiện chỉ dùng được Stage: " + ", ".join(bad))
svg = [s["id"] for s in data["scenes"] if s["component"] == "Creature"]
if svg:
    problems.append("Creature vẽ SVG đã bỏ, dùng Parallax với cutout PNG: " + ", ".join(svg))
tl = p.parent / "timeline.json"
if tl.exists():  # dựng từ audio + srt: tổng thời lượng phải khớp audio, nhịp cảnh theo style
    end = json.loads(tl.read_text(encoding="utf-8"))["audio_end"]
    if abs(total - end) > 1.0:
        problems.append(f"Tổng {total:.1f}s lệch audio {end:.1f}s")
    # Nhịp (research/2026-11-02_nhip-hinh.md: 7 video nổi bật cùng ngách, thân video trung vị 3,9-6,4 giây/cảnh).
    # (từ giây, đến giây, cảnh dài nhất). Thân video: trung bình ≤ BODY_AVG, ≤ 25% cảnh dài hơn 8 giây.
    # Sếp chốt 2026-11-03: (từ giây, đến giây, ngắn nhất, dài nhất)
    PACE = [(0, 15, 3, 5), (15, 60, 4, 7), (60, 180, 5, 8), (180, end - 60, 4, 12), (end - 60, end + 1, 4, 12)]
    BODY_AVG = (6.0, 8.0)  # thân video khoảng 6-8 giây mỗi cảnh, tối đa 12
    DIAGRAM = ("GeoMap", "MapDrift", "SizeCompare", "GeoClock")  # có diễn biến bên trong thì được tới 20 giây
    t, body = 0.0, []
    for s in data["scenes"]:
        d = s["duration_s"]
        lo_s, cap = next((m0, c) for a0, b0, m0, c in PACE if a0 <= t < b0) if t < end else (4, 12)
        if s["component"] in DIAGRAM and t >= 180:
            cap = 20
        if end < 45:  # bản thử máy rất ngắn: không áp nhịp
            pass
        elif d > cap + 0.5 and s["component"] != "TitleCard":
            problems.append(f"Cảnh {s['id']} ở {int(t // 60)}:{int(t % 60):02} dài {d:.1f}s, đoạn này tối đa {cap}s")
        elif d < lo_s - 0.5 and s["component"] != "TitleCard":
            warn.append(f"Cảnh {s['id']} ở {int(t // 60)}:{int(t % 60):02} chỉ {d:.1f}s, đoạn này nên {lo_s}-{cap}s (ngắn hơn chỉ khi cắt có chủ ý)")
        if 180 <= t < end - 60 and s["component"] != "TitleCard":
            body.append(d)
        t += d
    if body and not BODY_AVG[0] - 0.3 <= sum(body) / len(body) <= BODY_AVG[1]:
        (problems if sum(body) / len(body) > BODY_AVG[1] else warn).append(f"Thân video trung bình {sum(body) / len(body):.1f}s/cảnh, cần {BODY_AVG[0]:.0f}-{BODY_AVG[1]:.0f}s")
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

# Giới hạn chuyển động: mỗi cảnh 1 chuyển động máy + tối đa 1 hiệu ứng chính + nhiều lớp lặp được (Sếp 2026-11-06), trên 3 lớp thì cảnh báo rối
shakes, hero_use, prev_cam, prev_hero = 0, {}, None, set()


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
        warn.append(f"Cảnh {s['id']}: {len(hero)} hiệu ứng chính ({', '.join(sorted(hero))}), chỉ giữ 1")
    if sum(1 for x in parts if x.get("motion")) > 3:
        warn.append(f"Cảnh {s['id']}: hơn 3 lớp motion, dễ rối mắt; giữ nhân vật lời đang nói và vài nhân vật phụ gần nhất")
    if len(pr.get("annotate", [])) > 2:
        warn.append(f"Cảnh {s['id']}: quá 2 nét annotate")
    shakes += "shake" in hero
    for h in hero:
        hero_use[h] = hero_use.get(h, 0) + 1
    if hero & prev_hero:
        warn.append(f"Cảnh {s['id']} lặp hiệu ứng {', '.join(sorted(hero & prev_hero))} của cảnh trước")
    cam = camera(s)
    if cam and cam == prev_cam:
        warn.append(f"Cảnh {s['id']} cùng hướng máy ({cam}) với cảnh trước")
    prev_cam, prev_hero = cam, hero
# Hình khớp lời: asset_plan.json khai "subjects": {khóa: [tên gọi trong lời đọc...]} và mỗi asset có "subject": khóa.
# Lời đọc của cảnh nhắc đối tượng A mà hình chỉ là đối tượng B → lỗi (ảnh cũ ở lại khi lời đã chuyển). Nhãn, thẻ cũng phải thuộc đối tượng của hình.
import re
plan_p = p.parent / "asset_plan.json"
plan = json.loads(plan_p.read_text(encoding="utf-8")) if plan_p.exists() else {}
SUBJ = {k: [re.compile(rf"(?<!\w){re.escape(a)}(?!\w)", re.I) for a in v] for k, v in plan.get("subjects", {}).items()}
subj_of = {}
for x in plan.get("assets", []):
    if x.get("subject"):  # 1 khóa hoặc danh sách khóa (ảnh hang ở Ninh Bình: ["thung-binh-1", "ninh-binh"])
        sj = x["subject"] if isinstance(x["subject"], list) else [x["subject"]]
        subj_of[x["file"]] = subj_of[str(Path(x["file"]).with_suffix(".png"))] = set(sj)
mentions = lambda text: {k for k, pats in SUBJ.items() if any(r.search(text or "") for r in pats)}
tl_lines = json.loads(tl.read_text(encoding="utf-8"))["lines"] if tl.exists() else []
if SUBJ:
    for x in plan.get("assets", []):
        if x.get("kind") == "real" and not x.get("subject"):
            warn.append(f"Asset {x['id']} (ảnh thật) chưa khai subject: ghi khóa đối tượng hoặc \"chung\"")
    carry = set()
    for s in data["scenes"]:
        pr = s.get("props", {})
        shown = set().union(*[subj_of[a] for a in used(s) if a in subj_of]) - {"chung"}
        if s["component"] == "GeoMap":  # bản đồ chỉ nơi chốn: lời nhắc nơi khác mà bản đồ không có chấm nơi đó thì cảnh báo
            marked = set().union(*[mentions(m.get("label")) for m in pr.get("markers", [])]) if pr.get("markers") else set()
            if marked and "lines" in s:
                said = set().union(*[mentions(tl_lines[i]["text"]) for i in range(s["lines"][0], min(s["lines"][1], len(tl_lines) - 1) + 1)])
                if said and not said & marked:
                    warn.append(f"Cảnh {s['id']}: bản đồ chấm {', '.join(sorted(marked))} nhưng lời nói về {', '.join(sorted(said))}, kiểm lại")
            carry = set()
            continue
        if not shown or "lines" not in s:
            carry = set()
            continue
        lo, hi = s["lines"]
        for i in range(lo, min(hi, len(tl_lines) - 1) + 1):
            m = mentions(tl_lines[i]["text"])
            if m and not m & shown:
                warn.append(f"Cảnh {s['id']}: câu {i} nói về {', '.join(sorted(m))} nhưng hình là {', '.join(sorted(shown))}. Tách cảnh tại câu {i} hoặc đổi hình")
            elif not m and carry and not carry & shown and i == lo:
                warn.append(f"Cảnh {s['id']}: lời đang tiếp tục về {', '.join(sorted(carry))} nhưng hình là {', '.join(sorted(shown))}, kiểm lại")
            carry = m or carry
        texts = [pr.get("label"), pr.get("sub")] + [c.get("text") for c in pr.get("cards", [])] + [m.get("label") for m in pr.get("markers", [])] + [x.get("label") for x in pr.get("annotate", [])]
        for t in filter(None, texts):
            m = mentions(t)
            if m and not m & shown:
                warn.append(f"Cảnh {s['id']}: nhãn \"{t}\" thuộc {', '.join(sorted(m))} nhưng hình là {', '.join(sorted(shown))}")
elif plan.get("assets"):
    warn.append("asset_plan.json chưa có subjects: chưa kiểm được hình khớp lời theo đối tượng")

# Dùng lại asset (Sếp chốt 2026-11-02): ảnh AI không dùng lại ở cảnh không liền kề, trừ nền địa điểm quay lại (asset_plan "sync": true)
# và lần quay lại phải đổi trạng thái (grade) hoặc hướng máy. Ảnh thật dùng lại phải đổi vùng phóng (region), zoom hoặc trôi.
kind_of = {}
for x in plan.get("assets", []):
    kind_of[x["file"]] = kind_of[str(Path(x["file"]).with_suffix(".png"))] = x
seen = {}
for idx, s in enumerate(data["scenes"]):
    pr = s.get("props", {})
    look = json.dumps([pr.get("grade"), pr.get("cam"), pr.get("region"), pr.get("z"), pr.get("pan"), pr.get("x0"), pr.get("z0")], sort_keys=True)
    for a in {a for a in used(s) if a and a in kind_of}:
        x = kind_of[a]
        prev = seen.get(a)
        seen[a] = (idx, s["id"], look)
        if not prev or prev[0] == idx - 1:
            continue
        if x.get("kind") == "ai" and not x.get("sync"):
            problems.append(f"Cảnh {s['id']}: ảnh AI {a} đã dùng ở cảnh {prev[1]}. Tạo biến thể mới (cùng species, khác tư thế, góc nhìn, ánh sáng); chỉ nền địa điểm quay lại mới ghi sync: true")
        elif prev[2] == look and a == s.get("asset"):
            warn.append(f"Cảnh {s['id']}: {a} quay lại giống hệt cảnh {prev[1]}, đổi grade, hướng máy, region hoặc zoom")

# Chính tả chữ trên màn hình: từ không dấu mà lời đọc chỉ có dạng có dấu (vd "Thung Binh" / "Thung Bình") là thiếu dấu
import unicodedata
bare = lambda w: unicodedata.normalize("NFD", w).encode("ascii", "ignore").decode().replace("đ", "d").replace("Đ", "D").lower()
forms = {}
for l in tl_lines:
    for w in re.findall(r"\w+", l["text"]):
        forms.setdefault(bare(w), set()).add(w.lower())


def screen_texts(pr):
    yield from (pr.get(k) for k in ("label", "sub", "title", "kicker"))
    for k in ("cards", "markers", "annotate", "items"):
        for x in pr.get(k, []):
            yield x.get("text") or x.get("label") or x.get("name")


if forms:
    for s in data["scenes"]:
        for t in filter(None, screen_texts(s.get("props", {}))):
            for w in re.findall(r"\w+", str(t)):
                f = forms.get(bare(w))
                if w.isascii() and not w.isdigit() and f and w.lower() not in f:
                    problems.append(f"Cảnh {s['id']}: chữ \"{w}\" trong \"{t}\" thiếu dấu, lời đọc viết {'/'.join(sorted(f))}")

# Câu hỏi nào cũng phải được gắn thẻ: [HỎI]/[ĐÁP] nếu có đáp án về sau (hình đáp án phải ẩn), [TU-TỪ] nếu không
for l in tl_lines:
    if l.get("ask") and not l.get("qa"):
        problems.append(f"Câu {l['i']} là câu hỏi chưa gắn [HỎI: q]/[ĐÁP: q] hoặc [TU-TỪ]: {l['text'][:60]}")

# Không có khoảnh khắc tĩnh: cảnh sân khấu phải có ít nhất 1 yếu tố tự chuyển động ngoài máy quay, cutout chính phải cử động
LIVE = ("motion", "path", "sprite", "wind", "drift")
for s in data["scenes"]:
    pr = s.get("props", {})
    if s["component"] not in ("Stage", "Parallax"):
        continue
    layers = [x for x in pr.get("layers", []) if not x.get("hide")]
    if layers and not any(layers[0].get(k) for k in LIVE):
        warn.append(f"Cảnh {s['id']}: cutout chính {layers[0].get('asset') or 'sprite'} đứng yên, thêm motion/path/drift/wind hợp với chủ thể")
    alive = pr.get("atmosphere") or pr.get("water") or pr.get("quake") or len(pr.get("grade", [])) > 1 or any(x.get(k) for x in layers for k in LIVE)
    if not alive:
        problems.append(f"Cảnh {s['id']}: không có gì chuyển động ngoài máy quay, thêm cutout cử động (motion/path/wind), water, atmosphere leaves/dust hoặc đổi grade")

# Cảnh dài hơn 6 giây: cứ tối đa 4 giây phải có một sự kiện hình (thẻ, badge, nét khoanh, lớp mới, marker, lộ đáp án, đổi grade, path, hiệu ứng).
# Chuyển động máy không tính. Lấy từ research nhịp hình: video mẫu giữ cảnh lâu nhưng 1-3 giây lại hiện thêm chi tiết.
def events(s):
    pr = s.get("props", {})
    ts = [x.get("at_s") for k in ("cards", "badges", "annotate", "markers", "arrows", "layers", "items", "grade", "atmosphere") for x in pr.get(k, [])]
    ts += [x.get("unmask_s") for x in pr.get("layers", []) + pr.get("items", [])]
    ts += [k.get("at_s") for x in pr.get("layers", []) for k in x.get("path", [])]
    ts += [(pr.get(k) or {}).get("at_s") for k in ("spotlight", "shake", "quake")]
    if pr.get("region"):
        ts.append(1.2)
    if s["component"] == "PhotoCard" and pr.get("sweep", s["duration_s"] >= 4):
        ts.append(s["duration_s"] * 0.25 + 0.7)
    return sorted({round(x, 2) for x in ts if isinstance(x, (int, float)) and 0 < x < s["duration_s"]})


for s in data["scenes"]:
    d = s["duration_s"]
    if d <= 6 or s["component"] == "TitleCard":
        continue
    marks = [0.0] + events(s) + [d]
    gap = max(b0 - a0 for a0, b0 in zip(marks, marks[1:]))
    if gap > 4.0:
        problems.append(f"Cảnh {s['id']} dài {d:.1f}s có quãng {gap:.1f}s không có gì mới hiện ra: thêm thẻ, nét khoanh, lớp, marker hoặc đổi trạng thái (≤ 4s một lần)")

# Ít chữ (Sếp 2026-11-03): thẻ, nhãn chỉ khi số hoặc tên thật sự quan trọng. Tối đa trung bình 2 khối chữ mỗi phút.
n_text = sum(len(s.get("props", {}).get("cards", [])) + bool(s.get("props", {}).get("label")) for s in data["scenes"])
if total >= 60 and n_text > max(3, round(total / 60 * 2)):
    problems.append(f"{n_text} thẻ/nhãn chữ trong {total / 60:.1f} phút, tối đa {max(3, round(total / 60 * 2))}: chỉ giữ số liệu, tên thật sự quan trọng")
# Đom đóm chỉ khi cảnh thật sự cần (đêm, rừng tối, lời nhắc); thay bằng dust, leaves (mist/smoke không dùng trên cảnh có chủ thể, Sếp 2026-11-05)
ff = [s for s in data["scenes"] if any(a.get("type") == "fireflies" for a in s.get("props", {}).get("atmosphere", []))]
for s in ff:
    if not re.search(r"đom đóm|ban đêm|đêm|tối mịt|hoàng hôn", s.get("narration", ""), re.I):
        warn.append(f"Cảnh {s['id']}: đom đóm không hợp lời đọc, dùng dust, leaves hoặc đổi grade")
if len(ff) > 1:
    warn.append(f"{len(ff)} cảnh dùng đom đóm, hạn chế tối đa")

# Không lặp bố cục: 3 ảnh thật dạng khung giữa nền mờ liền nhau thì đổi 1 cảnh sang fill hoặc cảnh khác
run_pc = 0
for s in data["scenes"]:
    run_pc = run_pc + 1 if s["component"] == "PhotoCard" and not s.get("props", {}).get("fill") else 0
    if run_pc == 3:
        warn.append(f"Cảnh {s['id']}: 3 ảnh khung liền nhau cùng bố cục, đổi 1 cảnh sang fill: true hoặc cảnh khác")

# Hiệu ứng theo nội dung: lời nói mưa, động đất, lửa... mà cảnh không có hiệu ứng tương ứng thì gợi ý; có hiệu ứng mà lời không nhắc thì cảnh báo
FX_WORDS = {"rain": r"mưa|giông|bão", "quake": r"động đất|rung chuyển|sụt lún|địa chấn", "embers": r"lửa|bếp|cháy|đốt", "firerain": r"thiên thạch|mưa lửa|va chạm",
            "ash": r"tro|núi lửa|phun trào", "snow": r"tuyết|băng hà|giá rét", "lightning": r"sét|chớp"}
for s in data["scenes"]:
    pr = s.get("props", {})
    if s["component"] not in ("Stage", "Parallax") or not s.get("narration"):
        continue
    have = {a.get("type") for a in pr.get("atmosphere", [])} | ({"quake"} if pr.get("quake") else set())
    for fx, pat in FX_WORDS.items():
        said = re.search(pat, s["narration"], re.I)
        if said and fx not in have and fx in ("rain", "quake", "snow"):
            warn.append(f"Cảnh {s['id']}: lời nhắc \"{said[0]}\", cân nhắc hiệu ứng {fx}")
        if fx in have and not said:
            warn.append(f"Cảnh {s['id']}: có hiệu ứng {fx} nhưng lời đọc không nhắc tới, kiểm lại cho hợp nội dung")

# Luật máy đo được (HT-02, HT-04): bản đồ, sương, dải phụ đề, ảnh nhỏ, tĩnh, giữ bố cục, region cắt chủ thể, ảnh nhiều ô
import scene_rules
_rd = lambda q: json.loads(q.read_text(encoding="utf-8")) if q.exists() else {}
rule_hits = scene_rules.check(data, p.parent.resolve(), plan, _rd(p.parent / "qa" / "zones.json"), _rd(p.parent / "qa" / "asset_check.json"))
for k, hits in rule_hits.items():
    for _, m in hits:
        (problems if scene_rules.MODE[k] == "chan" else warn).append(f"[{k}] {m}")
if "--report" in sys.argv:
    Path(sys.argv[sys.argv.index("--report") + 1]).write_text(json.dumps({k: sorted({sid for sid, _ in v}) for k, v in rule_hits.items()}, ensure_ascii=False), encoding="utf-8")

if shakes > 3:
    warn.append(f"{shakes} cảnh có shake, tối đa 3 mỗi tập")
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
