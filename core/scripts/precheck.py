"""Duyệt nháp trước khi render cả video: chụp ảnh tĩnh từng cảnh (đúng như khi render, có thẻ, nhãn, phụ đề), ghép thành bảng kèm lời đọc
đúng lúc đó, AI không tham gia dựng chấm hình khớp lời. Rẻ hơn nhiều so với render 18 phút rồi mới thấy lỗi.
Dùng: python core/scripts/precheck.py <tập>. Kết quả qa/precheck_vN.md, bản scenes.json đã chấm chép ra qa/scenes_pre_vN.json.
Luật gốc là core/standard/qc-video.md (cùng bộ luật, cùng thang mức với QC video), thêm phần riêng của duyệt nháp.
Cổng (Sếp 2026-11-06: chỉ chặn lỗi nghiêm trọng): qua khi 0 lỗi cao, trừ lỗi trong qa/accepted.json. Lỗi vừa thuộc nhóm QC hay bắt (QC_TYPES)
đánh dấu "nên sửa", không chặn: precheck tập 1 chỉ khớp QC 3/36 lỗi, chặn lỗi vừa sẽ kẹt vì báo nhầm.
Mã thoát 3: precheck sập (AI, chụp ảnh tĩnh), produce dừng kể cả khi --force.
Mã thoát: 0 qua cổng, 1 còn lỗi chặn, 2 đã 4 vòng kể từ lần render đầy đủ gần nhất mà chưa qua cổng (dừng, báo Sếp).
Cache theo cảnh (mã băm props + asset + lời + mã nguồn component): vòng sau chỉ chụp và chấm cảnh đã đổi, lỗi còn mở của cảnh không đổi giữ nguyên.
Cảnh có chữ nhỏ (bản đồ, sơ đồ, ảnh khoa học có chữ, ảnh có nét khoanh) chấm bảng 2x2 ở độ phân giải đầy đủ của ảnh tĩnh, còn lại 3x3.
Mốc chụp: 60% cảnh, 1 giây sau mỗi thẻ, ngay trước lộ đáp án, đầu mỗi câu mới giữa cảnh (+0,5 s), lúc chú thích (annotate, marker, mũi tên) hiện (+0,8 s)."""
import hashlib, json, os, re, shutil, subprocess, sys, traceback


def _crash(t, v, tb):  # sập (không phải còn lỗi) → mã 3, produce không được render dù có --force
    traceback.print_exception(t, v, tb)
    os._exit(3)


sys.excepthook = _crash
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import learn, review, status
from paths import ROOT, resolve_asset

HERE = Path(__file__).resolve().parent
ep = Path(sys.argv[1]).resolve()
qa = ep / "qa"
stills = qa / "stills"
doc = json.loads((ep / "scenes.json").read_text(encoding="utf-8"))
lines = json.loads((ep / "timeline.json").read_text(encoding="utf-8"))["lines"] if (ep / "timeline.json").exists() else []
plan = json.loads((ep / "asset_plan.json").read_text(encoding="utf-8")) if (ep / "asset_plan.json").exists() else {}
QC_TYPES = {"chu-nho", "chu-chong", "cutout-loi", "mau", "hinh-loi-lech", "anh-loi"}  # nhóm QC video hay bắt: lỗi vừa đánh dấu nên sửa
MAX_ROUNDS = 4
plan_by_file, subj_of = {}, {}
for x in plan.get("assets", []):
    plan_by_file[x["file"]] = plan_by_file[str(Path(x["file"]).with_suffix(".png"))] = x
    if x.get("subject"):
        sj = x["subject"] if isinstance(x["subject"], list) else [x["subject"]]
        subj_of[x["file"]] = subj_of[str(Path(x["file"]).with_suffix(".png"))] = sj
answered = {q.split(":", 1)[1]: l["start"] for l in lines for q in l.get("qa", []) if q.startswith("ĐÁP:")}


def assets(s):
    pr = s.get("props", {})
    yield s.get("asset")
    for x in pr.get("layers", []) + pr.get("items", []):
        yield x.get("asset") or x.get("cutout")
        if (x.get("sprite") or {}).get("base"):
            yield x["sprite"]["base"]
    if (pr.get("sprite") or {}).get("base"):
        yield pr["sprite"]["base"]
    si = pr.get("strata_in") or {}
    yield si.get("asset")
    yield si.get("from_asset")


TEXT_HINT = re.compile(r"figure|fig\.|diagram|chart|map|plot|sơ đồ|bản đồ|biểu đồ|hình \d|bảng", re.I)


def dense(x):
    """Ảnh chụp có chữ nhỏ cần nhìn rõ: chấm bảng 2x2. Bản đồ: chỉ ảnh lúc đủ nhãn; ảnh thật: sơ đồ, hình bài báo, ảnh có chữ."""
    s = x["scene"]
    if s["component"] == "GeoMap":
        return x["kind"] == "chu-thich" or not s.get("props", {}).get("markers")
    for a in filter(None, assets(s)):
        x = plan_by_file.get(a) or {}
        if x.get("has_text") or (x.get("kind") == "real" and TEXT_HINT.search(" ".join([x.get("query", "")] + x.get("tags", [])))):
            return True
    return False


# Mốc chụp. kind: chung | loi-moi (câu mới bắt đầu giữa cảnh) | chu-thich (nét khoanh, chấm, mũi tên vừa hiện)
shots, t = [], 0.0
for s in doc["scenes"]:
    d, pr = s["duration_s"], s.get("props", {})
    times = {round(t + min(d * 0.6, d - 0.4), 2): "chung"}
    for c in pr.get("cards", []):
        if c.get("at_s", 0) + 1.0 < d:
            times[round(t + c.get("at_s", 0) + 1.0, 2)] = "chung"
    for x in pr.get("layers", []) + pr.get("items", []):
        if x.get("unmask_s"):
            times[round(t + x["unmask_s"] - 0.3, 2)] = "chung"
    for l in lines:
        if t + 0.8 < l["start"] < t + d - 0.6:
            times[round(l["start"] + 0.5, 2)] = "loi-moi"
    for x in pr.get("annotate", []):
        a = x.get("at_s", 0.5)
        if a + 0.8 < d:
            times[round(t + a + 0.8, 2)] = "chu-thich"
    pins = [x.get("at_s", 0.5 + i * 0.5) for i, x in enumerate(pr.get("markers", []))] + [x.get("at_s", 0) + 0.8 for x in pr.get("arrows", [])]
    if pins:  # bản đồ: 1 ảnh lúc mọi chấm và mũi tên đã hiện, đủ nhãn để kiểm đè chữ và đúng chỗ
        times[round(t + min(max(pins) + 0.8, d - 0.4), 2)] = "chu-thich"
    keep = []
    for tt in sorted(times):  # gộp mốc sát nhau (< 0,3 s), ưu tiên mốc chú thích
        if keep and tt - keep[-1][0] < 0.3:
            if times[tt] == "chu-thich":
                keep[-1] = (tt, "chu-thich")
            continue
        keep.append((tt, times[tt]))
    for k, (tt, kind) in enumerate(keep):
        shots.append({"t": tt, "kind": kind, "out": str(stills / f"{s['id']}_{k}.jpg"), "scene": s, "start": t})
    t += d


def said_at(tt):
    cur = [l for l in lines if l["start"] <= tt + 0.3 and l["end"] >= tt - 2.5]
    return " ".join(l["text"] for l in cur[-2:])


qtext = {q.split(":", 1)[1]: l["text"] for l in lines for q in l.get("qa", []) if q.startswith("HỎI:")}


def pending_q(tt):
    asked = {q.split(":", 1)[1] for l in lines if l["start"] <= tt for q in l.get("qa", []) if q.startswith("HỎI:")}
    return sorted(q for q in asked if answered.get(q, 1e9) > tt)


HINT = {"loi-moi": " | MỐC LỜI MỚI: câu mới vừa bắt đầu, hình còn đúng đối tượng câu này không (hinh-loi-lech)",
        "chu-thich": " | MỐC CHÚ THÍCH: vòng khoanh/mũi tên/chấm vừa hiện có đặt đúng vật, đúng chỗ lời đang nói không (nhan-sai, cao nếu sai vật)"}


def describe(n, x):
    s, pr = x["scene"], x["scene"].get("props", {})
    subj = sorted({k for a in assets(s) if a in subj_of for k in subj_of[a]})
    texts = [pr.get("label"), pr.get("sub")] + [c["text"] for c in pr.get("cards", [])] + [a.get("label") for a in pr.get("annotate", [])] + [m.get("label") for m in pr.get("markers", [])]
    q = [f"{k} (câu hỏi: \"{qtext.get(k, '')}\")" for k in pending_q(x["t"])]
    return (f"[{n}] {s['id']} {int(x['t'] // 60)}:{int(x['t'] % 60):02} | lời đang đọc: \"{said_at(x['t'])}\" | đối tượng khai của hình: {', '.join(subj) or 'chưa khai'}"
            f" | chữ khai trên hình: {'; '.join(filter(None, texts)) or 'không'}" + (f" | ĐANG HỎI, CHƯA TRẢ LỜI: {', '.join(q)} (hình không được lộ đáp án)" if q else "")
            + HINT.get(x["kind"], ""))


STD = (ROOT / "core/standard/qc-video.md").read_text(encoding="utf-8")
RULES = ("Bạn là người duyệt độc lập cho video tài liệu, không tham gia dựng. Mỗi ô là 1 khung hình chụp trước khi render, số ô ở góc trên trái.\n"
         "Chỉ báo lỗi thấy được, không khen.\n\nLUẬT GỐC (giống hệt QC video, áp dụng đủ):\n" + STD + """

RIÊNG DUYỆT NHÁP, kiểm từng ô:
1. hinh-loi-lech: hình có đúng đối tượng lời đang đọc không (di cốt, địa điểm, nhân vật, hiện vật). Ảnh còn ở lại khi lời đã chuyển sang đối tượng khác là lỗi vừa; chỉ là cao khi hình làm người xem hiểu sai fact (sai loài, sai mẫu vật, sai địa điểm). Ảnh minh họa chung giữ lại làm nền khi lời giải thích tiếp là lựa chọn dựng, không báo.
2. nhan-sai: nhãn, vòng khoanh, mũi tên có đặt đúng vật, đúng vị trí giải phẫu hoặc địa lý mà lời nói tới không.
3. lo-dap-an: ô ghi ĐANG HỎI mà hình đã cho thấy đáp án là lỗi cao.
4. chu-nho / chu-cat-mep / chu-chong: chữ trong sơ đồ, bản đồ hoặc ảnh không đọc được trên điện thoại, chữ bị cắt mép, nhãn đè nhau, hai khối chữ nội dung cùng lúc (không tính phụ đề).
5. so-de-chi-tiet: thẻ số liệu hoặc chữ đè lên chủ thể hoặc chi tiết quan trọng đang được nói tới; phụ đề đè mặt hoặc thân chủ thể.
6. chinh-ta: chữ trên hình sai chính tả hoặc thiếu dấu.
7. anh-loi, cutout-loi: chữ rác, sai giải phẫu, cutout bị cắt thân, viền trắng tinh hoặc viền đứt, quầng bẩn (viền mảnh màu giấy theo nền là cố ý), lơ lửng, ánh sáng hoặc tông màu của cutout/ảnh ghép không khớp nền (ghép lệch sáng là cutout-loi).
8. ban-do: bản đồ có Việt Nam mà thiếu hình quần đảo Hoàng Sa hoặc Trường Sa trong khung (không ghi chữ tên đảo là cố ý, không báo); tô cùng màu Việt Nam với nước láng giềng làm chấm địa điểm trông như nằm sai nước.
9. mau: cả cảnh ám vàng, cam hoặc sepia khi chủ đề không cần; sương/khói thành dải sáng nằm ngang che hình.
Mức (cùng thang với QC video): cao = phải sửa trước khi render: sai fact, asset hỏng, chữ không đọc được (chu-nho, chu-cat-mep), lỗi bản đồ, lộ đáp án, chữ nhắc AI. vừa = thấy rõ. thấp = trau chuốt.
Thẻ chữ không phải số liệu hoặc tên quan trọng là thừa (vừa). Đom đóm không hợp cảnh là lỗi (vừa).
Cố ý, không báo: dòng nguồn ảnh nhỏ góc dưới trái, phụ đề, thẻ đang mờ dần khi sắp hết, bóng đen hoặc sương che đáp án khi ô ghi ĐANG HỎI, ô ĐANG HỎI không lộ đáp án.""")


def sheet(part, k, cols):
    cw, ch = (960, 540) if cols == 2 else (640, 360)
    im = Image.new("RGB", (cols * cw, -(-len(part) // cols) * ch), "#000")
    dr = ImageDraw.Draw(im)
    font = ImageFont.load_default(28)
    for n, x in enumerate(part):
        c = Image.open(x["out"]).convert("RGB")
        c.thumbnail((cw - 4, ch - 4))
        X, Y = (n % cols) * cw, (n // cols) * ch
        im.paste(c, (X + 2, Y + 2))
        dr.rectangle([X + 2, Y + 2, X + 52, Y + 38], fill="#000")
        dr.text((X + 8, Y + 4), str(n + 1), fill="#ffd23f", font=font)
    p = qa / f"precheck_{k:03d}.jpg"
    im.save(p, quality=85)
    return p


# Mã băm từng cảnh: đổi props, asset, lời đọc, câu hỏi đang mở, mã nguồn component hoặc luật chấm thì chấm lại cảnh đó
def file_sig(p):
    if p.is_dir():  # sprite rig: base là thư mục khung hình, băm rig.json và danh sách khung
        rig = p / "rig.json"
        return hashlib.sha256(((status.file_sha(rig) if rig.exists() else "") + "|".join(sorted(str(f.relative_to(p)) for f in p.rglob("*.webp")))).encode()).hexdigest()
    return status.file_sha(p) if p.exists() else "thiếu"


RM = ROOT / "core" / "remotion"
# Băm cả mã nguồn Remotion (component dùng chung lẫn nhau, vd KenBurnsBg): sửa component nào cũng chấm lại, không giữ điểm cũ
SHARED_SRC = sorted([*RM.glob("lib/*"), *RM.glob("components/*.tsx"), *RM.glob("compositions/*.tsx"), RM / "types.ts", RM / "Root.tsx", RM / "index.ts"])
base = hashlib.sha256((RULES + "".join(file_sig(f) for f in SHARED_SRC if f.is_file())
                       + file_sig(ep.parents[1] / "theme.json") + file_sig(ep.parents[1] / "channel.yaml")).encode()).hexdigest()
asig = {}


def scene_hash(s, shot_list):
    for a in filter(None, assets(s)):
        if a not in asig:
            asig[a] = file_sig(resolve_asset(ep, a))
    # Không băm mã cảnh và giây tuyệt đối: đánh số lại cảnh hoặc đổi độ dài cảnh phía trước không làm chấm lại cảnh này
    body = {k: v for k, v in s.items() if k != "id"}
    blob = json.dumps({"s": body, "a": [asig.get(a) for a in assets(s) if a], "base": base,
                       "d": [describe(0, x).split(" | ", 1)[1] for x in shot_list], "t": [round(x["t"] - x["start"], 2) for x in shot_list]},
                      ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


by_scene = {}
for x in shots:
    by_scene.setdefault(x["scene"]["id"], []).append(x)
hashes = {sid: scene_hash(xs[0]["scene"], xs) for sid, xs in by_scene.items()}
# Khóa ngoại lệ: chỉ nội dung cảnh (props, asset, lời), không gồm mã nguồn Remotion, để sửa component không làm mất ngoại lệ đã duyệt
akey = {sid: hashlib.sha256(json.dumps({"s": {k: v for k, v in xs[0]["scene"].items() if k != "id"}, "a": [asig.get(a) for a in assets(xs[0]["scene"]) if a]},
                                       ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12] for sid, xs in by_scene.items()}
cache_p = qa / "precheck_scenes.json"
cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
graded, last = cache.setdefault("graded", {}), cache.setdefault("last", {})
todo = [sid for sid in by_scene if hashes[sid] not in graded]
todo_shots = [x for sid in todo for x in by_scene[sid]]

# Chỉ chụp ảnh tĩnh của cảnh cần chấm
stills.mkdir(parents=True, exist_ok=True)
for x in todo_shots:
    Path(x["out"]).unlink(missing_ok=True)
for old in qa.glob("precheck_[0-9][0-9][0-9].jpg"):
    old.unlink()
if todo_shots:
    spec = qa / "stills.json"
    spec.write_text(json.dumps([{"t": x["t"], "out": x["out"]} for x in todo_shots]), encoding="utf-8")
    subprocess.run(["node", str(HERE / "render.mjs"), str(ep), "--stills", str(spec)], check=True)

types = "; ".join(list(learn.VIDEO_DEFECTS) + ["so-de-chi-tiet"])
board_cache = qa / "precheck_cache.json"
boards = []  # (các ô, số cột): cảnh chữ nhỏ 2x2, còn lại 3x3
fine = [x for x in todo_shots if dense(x)]
rough = [x for x in todo_shots if not dense(x)]
boards += [(fine[k:k + 4], 2) for k in range(0, len(fine), 4)]
boards += [(rough[k:k + 9], 3) for k in range(0, len(rough), 9)]


def grade(job):
    k, (part, cols) = job
    img = sheet(part, k, cols)
    prompt = (RULES + "\n\nCác ô:\n" + "\n".join(describe(n + 1, x) for n, x in enumerate(part)) +
              '\n\nReply ONLY JSON: {"score":0-10,"issues":[{"cell":1,"severity":"cao|vừa|thấp","type":"' + types + '","issue":"mô tả tiếng Việt","fix":"cách sửa tiếng Việt, chỉ rõ prop cần đổi nếu được"}]}')
    key = hashlib.sha256((prompt + hashlib.md5(img.read_bytes()).hexdigest()).encode()).hexdigest()
    r = review.ask_json_cached(board_cache, key, prompt, [img], edge=1920)
    out = []
    for x in r.get("issues", []):
        try:
            c = part[max(0, min(len(part) - 1, int(x.get("cell", 1)) - 1))]
        except (TypeError, ValueError):
            c = part[0]
        out.append({**x, "scene": c["scene"]["id"], "time": f"{int(c['t'] // 60)}:{int(c['t'] % 60):02}", "t": c["t"], "dt": round(c["t"] - c["start"], 2)})
    print(f"bảng {k + 1}/{len(boards)} ({cols}x{cols}): {len(out)} lỗi")
    return out


fresh = {sid: [] for sid in todo}
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(4) as pool:  # các bảng độc lập, chấm song song
    for out in pool.map(grade, enumerate(boards)):
        for x in out:
            fresh[x["scene"]].append(x)

n = 1 + len(list(qa.glob("precheck_v*.md")))
# Lỗi lặp: cảnh đã sửa (mã băm đổi) mà vẫn cùng loại lỗi như lần chấm trước thì không chỉnh prop nữa (HT-04)
for sid, iss in fresh.items():
    prev = last.get(sid)
    if prev and prev["hash"] != hashes[sid]:
        for x in iss:
            if x.get("type") in prev["types"]:
                x["lap"] = True
    graded[hashes[sid]] = {"scene": sid, "round": n, "issues": iss}
    last[sid] = {"hash": hashes[sid], "types": sorted({x.get("type") for x in iss})}
cache_p.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

# Ngoại lệ gắn với mã băm cảnh lúc duyệt: cảnh đổi nội dung hoặc bị đánh số lại thì ngoại lệ không áp nhầm sang cảnh khác
acc_p = qa / "accepted.json"
acc = json.loads(acc_p.read_text(encoding="utf-8")) if acc_p.exists() else []
# Approver chép cột "Khóa" của báo cáo vào ngoại lệ: {"key": "...", "type": "...", "reason": "..."}. Ngoại lệ không có key thì không áp.
accepted = {(a.get("key"), a.get("type")) for a in acc if a.get("key") and a.get("type")}
issues = []
for sid, xs in by_scene.items():  # lỗi dùng lại: mã cảnh và giây theo vị trí hiện tại
    st0 = xs[0]["start"]
    for x in graded[hashes[sid]]["issues"]:
        tt = st0 + x.get("dt", 0)
        issues.append({**x, "scene": sid, "t": tt, "time": f"{int(tt // 60)}:{int(tt % 60):02}", "h": akey[sid]})
skipped = [x for x in issues if (x["h"], x.get("type")) in accepted]
issues = [x for x in issues if (x["h"], x.get("type")) not in accepted]
blocks = lambda x: x.get("severity") == "cao"
should = lambda x: x.get("severity") == "vừa" and x.get("type") in QC_TYPES
order = {"cao": 0, "vừa": 1, "thấp": 2}
issues.sort(key=lambda x: (not blocks(x), order.get(x.get("severity"), 3), x.get("t", 0)))
high = sum(x.get("severity") == "cao" for x in issues)
blocking = sum(map(blocks, issues))

# Vòng kể từ lần render đầy đủ gần nhất (luật dừng HT-06)
final = ep / "render" / "final.mp4"
since = final.stat().st_mtime if final.exists() else 0
rounds = 1 + sum(1 for p in qa.glob("precheck_v*.md") if p.stat().st_mtime > since)
stop = blocking and rounds >= MAX_ROUNDS
shutil.copy(ep / "scenes.json", qa / f"scenes_pre_v{n}.json")
L = [f"# Duyệt nháp lần {n} (vòng {rounds}/{MAX_ROUNDS} kể từ lần render gần nhất)",
     f"- {len(shots)} ảnh tĩnh, {len(doc['scenes'])} cảnh: chấm mới {len(todo)} cảnh ({len(boards)} bảng), dùng lại {len(by_scene) - len(todo)} cảnh không đổi.",
     f"- Lỗi nặng: {high}. Lỗi chặn render: {blocking}. Tổng lỗi: {len(issues)}. Đã chấp nhận (qa/accepted.json): {len(skipped)}.",
     "- Cổng: 0 lỗi cao. " + ("QUA CỔNG." if not blocking else "CHƯA QUA.") + f" Lỗi vừa nên sửa (nhóm QC hay bắt): {sum(map(should, issues))}, người dựng tự cân nhắc, không chặn.",
     "- Lỗi đánh dấu LẶP: cùng loại lỗi đã có ở bản trước của cảnh này; nếu đúng là cùng lỗi thì đổi asset, bố cục hoặc bỏ cảnh thay vì chỉnh prop.",
     "- Báo nhầm hoặc cố ý: approver ghi {\"key\": <cột Khóa>, \"type\", \"reason\"} vào qa/accepted.json; cảnh đổi nội dung thì khóa đổi, ngoại lệ tự hết hiệu lực.", ""]
if stop:
    L += [f"**DỪNG: đã {rounds} vòng mà chưa qua cổng. Báo Sếp kèm lỗi còn lại, không tự render.**", ""]
L += ["| Chặn/nên sửa | Mức | Giây | Cảnh | Khóa | Loại | Lỗi | Cách sửa |", "|---|---|---|---|---|---|---|---|"]
L += [f"| {'chặn' if blocks(x) else 'nên sửa' if should(x) else ''} | {x.get('severity')} | {x['time']} | {x['scene']} | {x['h']} | {x.get('type', '')}{' LẶP' if x.get('lap') else ''} | {str(x.get('issue')).replace('|', '/')} | {str(x.get('fix')).replace('|', '/')} |" for x in issues]
out = qa / f"precheck_v{n}.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(out, "| lỗi nặng:", high, "| lỗi chặn:", blocking, "| chấm mới", len(todo), "cảnh")
if stop:
    d = status.read(ep)
    d["can_sep"] = f"precheck {rounds} vòng chưa qua cổng, còn {blocking} lỗi chặn ({out.name})"
    status.write(ep, d)
    sys.exit(2)
sys.exit(1 if blocking else 0)
