"""Ghép srt của Sếp với storyboard.md để lấy thời gian thật. Không tốn token, mọi ngôn ngữ.
Dùng: python core/scripts/align_srt.py <episode_dir>          → timeline.json + audio/subs.clean.srt
      python core/scripts/align_srt.py <episode_dir> --apply  → điền duration_s, narration, badge, thẻ vào scenes.json
srt chỉ dùng để lấy thời gian. Chữ phụ đề lấy từ storyboard (viết hoa, dấu câu, tên riêng chuẩn)."""
import json, re, sys
from difflib import SequenceMatcher
from pathlib import Path

ep = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel as chan
cfg = chan.load(ep)
lang, sp = cfg["lang"], chan.speech(cfg)
CHAR = lang["tokenize"] == "char"  # ngôn ngữ không có khoảng trắng: khớp srt theo ký tự, cắt phụ đề sau dấu ngắt
SPLIT = lang["sentence_split"]
MAX_CHARS = lang["subtitle"]["max"]  # phụ đề 1 dòng
BREAK = lang["subtitle"]["break_after"]
MIN_MATCH = 0.90    # dưới mức này thì dừng và báo câu lệch
BADGES = {v.lower(): k for k, v in lang["labels"].items() if k in ("xac-nhan", "co-the", "tranh-cai")}
CARD = lang["card"]
QA = re.compile(r"(?:(HỎI|ĐÁP)\s*:\s*(\w+)|(TU-TỪ))$", re.I)  # [HỎI: q1] ... [ĐÁP: q1]; [TU-TỪ]: câu hỏi tu từ, không có đáp án về sau


def ts(s):
    h, m, rest = s.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def fmt(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


words = sp.words


def read_srt():
    srts = sorted((ep / "audio").glob("*.srt"))
    srts = [p for p in srts if not p.name.endswith(".clean.srt")]
    if not srts:
        sys.exit("Không thấy file .srt trong audio/")
    cues = []
    for block in re.split(r"\n\s*\n", srts[0].read_text(encoding="utf-8-sig").strip()):
        lines = block.strip().splitlines()
        i = next((k for k, l in enumerate(lines) if "-->" in l), None)
        if i is None:
            continue
        a, b = [ts(x.strip().split()[0]) for x in lines[i].split("-->")]
        cues.append((a, b, " ".join(lines[i + 1:])))
    return cues


def read_storyboard():
    """Mỗi câu lời đọc: chương, chữ hiển thị, chữ đọc, ghi chú [ ] đứng trước hoặc cùng dòng."""
    out, chapter, pending, pending_qa = [], "", [], []
    for raw in (ep / "storyboard.md").read_text(encoding="utf-8").splitlines():
        if raw.startswith("## "):
            chapter = raw[3:].strip()
            continue
        if raw.startswith("#"):
            continue
        # Ghi chú gắn đúng câu đứng ngay sau nó (ghi chú giữa dòng thuộc câu sau nó, không phải câu đầu dòng).
        # [HỎI: q1] / [ĐÁP: q1] / [TU-TỪ] cuối dòng thì gắn câu ngay trước. Ghi chú thay bằng mã chỗ để dấu chấm bên trong không cắt câu.
        box = []

        def hold(m):
            box.append(m[1].strip())
            return f"\x00{len(box) - 1}\x00"
        marked = re.sub(r"\[([^\]]*)\]", hold, raw)
        k = 0
        for seg in re.split(SPLIT, marked.strip()):
            here = [box[int(i)] for i in re.findall(r"\x00(\d+)\x00", seg)]
            qa = [QA.match(n) for n in here if QA.match(n)]
            qa = [f"{m[1].upper()}:{m[2]}" if m[1] else "TU-TỪ" for m in qa]
            plain = [n for n in here if not QA.match(n)]
            sent = re.sub(r"\s{2,}", " ", re.sub(r"\x00\d+\x00", "", seg)).strip()
            if not sent:
                if k and qa:
                    out[-1].setdefault("qa", []).extend(qa)
                else:
                    pending_qa += qa
                pending += plain
                continue
            out.append({"chapter": chapter, "text": sp.display(sent), "speak": sp.speak(sent), "notes": pending + plain})
            if pending_qa + qa:
                out[-1]["qa"] = pending_qa + qa
            if sent.endswith(("?", "？", "؟")):
                out[-1]["ask"] = True
            pending, pending_qa, k = [], [], k + 1
    return out


cues, sents = read_srt(), read_storyboard()
# Thời gian từng từ trong srt: chia đều theo độ dài chữ trong mỗi cue
sw, st = [], []
for a, b, text in cues:
    ws = words(sp.speak(text))  # srt có thể ghi số hoặc kanji: quy về cùng dạng chữ đọc
    tot = sum(len(w) for w in ws) or 1
    acc = 0
    for w in ws:
        st.append((a + (b - a) * acc / tot, a + (b - a) * (acc + len(w)) / tot))
        sw.append(w)
        acc += len(w)
bw, owner = [], []
for i, s in enumerate(sents):
    for w in words(s["speak"]):
        bw.append(w)
        owner.append(i)
sm = SequenceMatcher(None, bw, sw, autojunk=False)
t0, t1 = [None] * len(bw), [None] * len(bw)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        t0[blk.a + k], t1[blk.a + k] = st[blk.b + k]
matched = sum(x is not None for x in t0)
ratio = matched / max(1, len(bw))
# Từ không khớp: nội suy giữa hai từ khớp gần nhất
known = [k for k, x in enumerate(t0) if x is not None]
for k in range(len(bw)):
    if t0[k] is None:
        prev = max((j for j in known if j < k), default=None)
        nxt = min((j for j in known if j > k), default=None)
        a = t1[prev] if prev is not None else 0.0
        b = t0[nxt] if nxt is not None else cues[-1][1]
        n0 = prev if prev is not None else -1
        n1 = nxt if nxt is not None else len(bw)
        frac = (k - n0) / (n1 - n0)
        t0[k] = t1[k] = a + (b - a) * frac
bad = []
for i, s in enumerate(sents):
    idx = [k for k, o in enumerate(owner) if o == i]
    s["start"], s["end"] = (round(t0[idx[0]], 3), round(t1[idx[-1]], 3)) if idx else (0.0, 0.0)
    hit = sum(1 for k in idx if k in set(known))
    if idx and hit / len(idx) < 0.6:
        bad.append(f"  câu {i}: {s['text'][:70]}")

# Phụ đề 1 dòng: cắt câu thành đoạn ≤ MAX_CHARS, ưu tiên sau dấu phẩy, thời gian chia theo số ký tự
subs = []
def char_chunks(text, limit):
    """Không có khoảng trắng: cắt sau dấu ngắt, đoạn nào vẫn dài thì cắt cứng."""
    out, cur = [], ""
    for part in re.split(rf"(?<={re.escape(BREAK)})", text):
        if cur and len(cur) + len(part) > limit:
            out.append(cur); cur = ""
        cur += part
        while len(cur) > limit + 6:
            out.append(cur[:limit]); cur = cur[limit:]
    return out + ([cur] if cur else [])


def word_chunks(text, limit):
    chunks, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > limit:
            cut = cur.rfind(BREAK + " ")
            if cut > limit * 0.4:
                chunks.append(cur[:cut + 1]); cur = cur[cut + 2:]
            else:
                chunks.append(cur); cur = ""
        cur = f"{cur} {w}".strip()
    return chunks + ([cur] if cur else [])


for s in sents:
    chunks = (char_chunks if CHAR else word_chunks)(s["text"], MAX_CHARS)
    tot, acc = sum(len(c) for c in chunks), 0
    for c in chunks:
        a = s["start"] + (s["end"] - s["start"]) * acc / tot
        acc += len(c)
        subs.append({"start": round(a, 3), "end": round(s["start"] + (s["end"] - s["start"]) * acc / tot, 3), "text": c})
chapters, seen = [], set()
for s in sents:
    if s["chapter"] and s["chapter"] not in seen:
        seen.add(s["chapter"]); chapters.append({"title": s["chapter"], "start": s["start"]})

if "--apply" not in sys.argv:
    doc = {"audio_end": cues[-1][1], "match": round(ratio, 3), "chapters": chapters,
           "lines": [{"i": i, **{k: s[k] for k in ("chapter", "start", "end", "text", "notes", "qa", "ask") if k in s}} for i, s in enumerate(sents)],
           "subs": subs}
    (ep / "timeline.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (ep / "audio" / "subs.clean.srt").write_text(
        "\n".join(f"{n}\n{fmt(c['start'])} --> {fmt(c['end'])}\n{c['text']}\n" for n, c in enumerate(subs, 1)), encoding="utf-8")
    print(f"{len(sents)} câu, khớp {ratio:.0%}, audio {cues[-1][1] / 60:.1f} phút → timeline.json, audio/subs.clean.srt")
    untagged = [f"  câu {l['i']}: {l['text'][:70]}" for l in doc["lines"] if l.get("ask") and not l.get("qa")]
    if untagged:
        print("Câu hỏi chưa gắn [HỎI: q]/[ĐÁP: q] hoặc [TU-TỪ] trong storyboard (validate_scenes sẽ chặn render):", *untagged[:30], sep="\n")
    if ratio < MIN_MATCH or bad:
        print("Câu lệch nhiều (kiểm lại storyboard và srt):", *bad[:20], sep="\n")
        sys.exit(2 if ratio < MIN_MATCH else 0)
    sys.exit(0)

# --apply: scenes.json có "lines": [đầu, cuối] (chỉ số câu trong timeline.json), tuỳ chọn "fixed_s" cho TitleCard
doc = json.loads((ep / "scenes.json").read_text(encoding="utf-8"))
sc, end = doc["scenes"], cues[-1][1] + 0.6
starts = []
def word_start(line, phrase):
    """Cắt cảnh giữa câu (đoạn hook cần cảnh 2,5-5 giây): thời điểm bắt đầu cụm từ phrase trong câu line."""
    want = words(sp.speak(phrase))
    idx = [k for k, o in enumerate(owner) if o == line]
    for n, k in enumerate(idx):
        if [bw[j] for j in idx[n:n + len(want)]] == want:
            return t0[k]
    sys.exit(f"Không thấy start_word \"{phrase}\" trong câu {line}: {sents[line]['text']}")


for i, s in enumerate(sc):
    a = 0.0 if i == 0 else sents[s["lines"][0]]["start"]
    if i and s.get("start_word"):
        a = word_start(s["lines"][0], s["start_word"])
    if i and sc[i - 1].get("fixed_s"):
        a = max(a, starts[-1] + sc[i - 1]["fixed_s"])
    starts.append(a)
for i, s in enumerate(sc):
    s["duration_s"] = round((starts[i + 1] if i + 1 < len(sc) else end) - starts[i], 3)
    lo, hi = s["lines"]
    s["narration"] = " ".join(x["text"] for x in sents[lo:hi + 1])
    props = s.setdefault("props", {})
    if s.get("fixed_s"):  # thẻ chương: không gắn badge hay thẻ keyword
        continue
    # Badge và thẻ lấy từ storyboard được tính lại mỗi lần apply, nên sửa hay bỏ [THẺ] trong storyboard là có hiệu lực.
    # Muốn giữ thẻ/badge tự viết trong scenes.json thì ghi "manual": true. Bản cũ chưa có cờ: cảnh có ghi chú tương ứng thì coi là tự động.
    own = lambda j: [] if (j == lo and s.get("start_word")) else sents[j]["notes"]  # cắt giữa câu: ghi chú của câu đầu thuộc cảnh trước
    notes = [n for j in range(lo, hi + 1) for n in own(j)]
    has_card = any(n.upper().startswith("THẺ:") for n in notes)
    has_badge = any(BADGES.get(n.strip().lower()) for n in notes)
    for key, has in (("cards", has_card), ("badges", has_badge)):
        keep = [c for c in props.get(key, []) if c.get("manual") or (not c.get("auto") and not has)]
        if keep:
            props[key] = keep
        else:
            props.pop(key, None)
    for j in range(lo, hi + 1):
        x = sents[j]
        at = round(max(0.0, x["start"] - starts[i]), 2)
        for n in own(j):
            key = BADGES.get(n.strip().lower())
            if key and not any(b["type"] == key for b in props.get("badges", [])):
                props.setdefault("badges", []).append({"type": key, "at_s": at, "auto": True})
            if n.upper().startswith("THẺ:") and not props.get("cards"):
                # thẻ chỉ giữ keyword/số liệu: cắt ở dấu ngắt, trừ dấu phẩy thập phân (0,4 gam) và dấu chấm/phẩy giữa hai chữ số
                raw = n.split(":", 1)[1].strip()
                card = sp.display(re.split(rf"(?<!\d)[,{re.escape(BREAK)}]|[,{re.escape(BREAK)}](?!\d)", raw)[0].strip())
                if card != sp.display(raw):
                    print(f"Cảnh {s['id']}: thẻ chỉ giữ phần trước dấu phẩy: \"{card}\" (bỏ \"{raw[len(card):].strip(' ,')}\")")
                if (len(card) if CARD["unit"] == "char" else len(card.split())) <= CARD["max"]:
                    props["cards"] = [{"text": card, "at_s": at, "auto": True}]
                else:
                    print(f"Bỏ thẻ quá dài ở cảnh {s['id']}: {card}")
# Vị trí thẻ số liệu: đặt vào vùng trống của ảnh (qa/zones.json, asset_zones.py), né cutout và ảnh trong PhotoCard. Thẻ manual có pos thì giữ.
zp = ep / "qa" / "zones.json"
zones = json.loads(zp.read_text(encoding="utf-8")) if zp.exists() else {}
FW, FH = (1080, 1920) if doc.get("format") == "9:16" else (1920, 1080)


CARD_FONT = 52  # thẻ ở góc: nhỏ hơn thẻ giữa màn hình cũ


def card_w(text):
    return len(text) * CARD_FONT * 0.56 + 70


def card_pos(s, text=""):
    """Thẻ chỉ ở góc trên màn hình (Sếp 2026-11-03), chọn góc trái hoặc phải ít đè chủ thể nhất.
    Ngoại lệ: thẻ chú thích một vật (props.card_anchor) đứng cạnh vật, có đường dẫn."""
    pr = s.get("props", {})
    a = s.get("asset")
    cw, chh = card_w(text), CARD_FONT * 1.6
    if pr.get("card_anchor"):
        ax, ay = pr["card_anchor"]
        return [round(ax + cw / 2 + 120 if ax < FW * 0.6 else ax - cw / 2 - 120), round(min(max(ay - 60, 90), FH * 0.72))]
    y = 66 if s["component"] == "PhotoCard" else 92
    corners = {"left": [70 + cw / 2, y], "right": [FW - 70 - cw / 2, y]}
    if pr.get("label"):  # nhãn cảnh nằm góc trên trái
        corners.pop("left")
    if pr.get("badges") and len(corners) > 1:  # badge nằm góc trên phải
        corners.pop("right")
    busy = []  # các khung cần né: chủ thể của ảnh nền, cutout
    z = zones.get(a)
    if z and s["component"] != "PhotoCard":
        x0, y0, w0, h0 = z["subject"]
        busy.append((x0 * FW, y0 * FH, (x0 + w0) * FW, (y0 + h0) * FH))
    for l in pr.get("layers", []):
        lh = l.get("h", 600); lw = lh * 0.6; lx, ly = l.get("x", FW / 2), l.get("y", FH - 80)
        busy.append((lx - lw / 2, ly - lh, lx + lw / 2, ly))
    def overlap(c):
        r = (c[0] - cw / 2, c[1] - chh / 2, c[0] + cw / 2, c[1] + chh / 2)
        return sum(max(0, min(r[2], b[2]) - max(r[0], b[0])) * max(0, min(r[3], b[3]) - max(r[1], b[1])) for b in busy)
    best = min(corners, key=lambda k: (overlap(corners[k]), k != "left"))
    return [round(v) for v in corners[best]]


for s in sc:
    for c in s.get("props", {}).get("cards", []):
        if c.get("auto") or c.get("pos_auto") or not c.get("pos"):  # pos ghi tay (không có pos_auto) thì giữ
            pos = card_pos(s, c.get("text", ""))
            if pos:
                half = card_w(c.get("text", "")) / 2 + 40  # luôn nằm trọn trong khung
                c["pos"] = [round(min(max(pos[0], half), FW - half)), round(min(max(pos[1], 80), FH * 0.75))]
                c["pos_auto"] = True
        if s.get("props", {}).get("card_anchor"):
            c["anchor"] = s["props"]["card_anchor"]
        else:
            c.pop("anchor", None)

# Ảnh thật: tự điền dòng nguồn từ credits.json của tập (gen_assets.py ghi khi tải ảnh)
cr_p = ep / "credits.json"
credits = json.loads(cr_p.read_text(encoding="utf-8")) if cr_p.exists() else {}
for s in sc:
    pr = s.setdefault("props", {})
    if s["component"] == "PhotoCard" and not pr.get("credit") and s.get("asset") in credits:
        pr["credit"] = credits[s["asset"]]["credit"]
    for it in pr.get("items", []):
        if it.get("photo") and not it.get("credit") and it.get("asset") in credits:
            it["credit"] = credits[it["asset"]]["credit"]
# Asset đáp án (answer_of trong asset_plan.json) đang ẩn: tự điền unmask_s = lúc đọc câu [ĐÁP] nằm trong cảnh
plan_p = ep / "asset_plan.json"
answer_of = {}
if plan_p.exists():
    for x in json.loads(plan_p.read_text(encoding="utf-8")).get("assets", []):
        if x.get("answer_of"):
            answer_of[x["file"]] = answer_of[str(Path(x["file"]).with_suffix(".png"))] = x["answer_of"]
for i, s in enumerate(sc):
    lo, hi = s["lines"]
    ans = {q.split(":", 1)[1]: round(max(0.0, x["start"] - starts[i]), 2)
           for x in sents[lo:hi + 1] for q in x.get("qa", []) if q.startswith("ĐÁP:")}
    pr = s["props"]
    hidden = [(x, x.get("asset") or x.get("cutout")) for x in pr.get("layers", []) + pr.get("items", []) if x.get("hide")]
    if isinstance(pr.get("hide"), dict):
        hidden.append((pr["hide"], s.get("asset")))
    for x, f in hidden:
        q = x.get("answer_of") or answer_of.get(f)
        if q in ans and "unmask_s" not in x:
            x["unmask_s"] = ans[q]
(ep / "scenes.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(sc)} cảnh, {sum(s['duration_s'] for s in sc) / 60:.1f} phút, khớp audio {end / 60:.1f} phút")
