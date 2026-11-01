"""Tạo và tìm asset riêng cho một tập theo <tập>/asset_plan.json, tự chấm và chọn bản tốt nhất, rồi xuất asset_sheet.jpg để soát.
Dùng: python core/scripts/gen_assets.py <episode_dir> [--only ai|real] [--redo id1,id2] [--max 60] [--tries 5] [--codex]
  kind "ai":     ảnh AI qua 9router. role "bg" = nền 1920x1080; role "cutout" = PNG nền trong suốt.
  kind "real":   tài liệu minh họa thật tìm trên internet bằng 9router cx/gpt-6.1-sol, không bắt buộc giấy phép, ghi nguồn vào <tập>/credits.json.
  kind "shared": asset dùng chung trong assets/shared, chỉ kiểm tra tồn tại.
Mỗi asset thử tối đa --tries lần: tạo, AI độc lập chấm, sửa prompt theo lỗi, tạo lại. Đạt thì dừng sớm. Chọn bản điểm cao nhất, xóa các bản khác.
Bản tốt nhất vẫn dưới ngưỡng thì không đưa vào sản xuất: ghi missing_assets.md để báo Sếp. Điểm từng lần ghi vào qa/assets.json."""
import argparse, io, json, re, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import pillow_avif  # noqa: F401  (ảnh web hay ở dạng AVIF)
from paths import ROOT
import review, router
from rig_cutout import clean_edges

ap = argparse.ArgumentParser()
ap.add_argument("ep")
ap.add_argument("--only", choices=["ai", "real"])
ap.add_argument("--redo", default="")
ap.add_argument("--max", type=int, default=60)
ap.add_argument("--tries", type=int, default=5)
ap.add_argument("--codex", action="store_true")
a = ap.parse_args()
ep = Path(a.ep).resolve()
import status
status.require_brief(ep)
A = ep / "assets"
CAND = ep / ".cand"
plan = json.loads((ep / "asset_plan.json").read_text(encoding="utf-8"))
theme = json.loads((ep.parents[1] / "theme.json").read_text(encoding="utf-8"))
STYLE = theme.get("art_style_prompt", "")
SPECIES = plan.get("species", {})
redo = set(filter(None, a.redo.split(",")))
UA = {"User-Agent": "youtube-tien-su-asset-bot/1.0 (https://github.com/idohart1102/youtube-tien-su; education channel)"}
NEUTRAL = ("Natural, neutral color balance with clean whites and shadows. No overall yellow, amber, orange or sepia color cast. "
           "Use yellow or gold only on objects whose real color is yellow or gold")
PASS, FLOOR = 8.0, 6.0  # đạt thì dừng sớm; dưới FLOOR thì không dùng


def out_path(x):
    return A / (str(Path(x["file"]).with_suffix(".png")) if x.get("role") == "cutout" else x["file"])


todo = [x for x in plan["assets"] if x["kind"] in ("ai", "real") and (x["id"] in redo or not out_path(x).exists())]
todo = [x for x in todo if not a.only or x["kind"] == a.only]
for x in plan["assets"]:
    if x["kind"] == "shared" and not (ROOT / "assets" / x["file"]).exists():
        print(f"Thiếu asset dùng chung: {x['file']}")
if sum(x["kind"] == "ai" for x in todo) > a.max:
    sys.exit(f"Cần tạo {sum(x['kind'] == 'ai' for x in todo)} ảnh AI, vượt --max {a.max}. Gộp cảnh dùng chung hình hoặc tăng --max.")


def fit_bg(im):  # cắt về 16:9 rồi đưa về 1920x1080
    w, h = im.size
    if w / h > 16 / 9:
        nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    return im.convert("RGB").resize((1920, 1080), Image.LANCZOS)


def crop_cutout(im):  # alpha gần đặc → đặc, cắt sát vật thể, làm sạch rìa
    im = im.convert("RGBA")
    al = im.getchannel("A").point(lambda v: 255 if v > 240 else (0 if v < 10 else v))
    im.putalpha(al)
    box = al.getbbox()
    if box:
        p = 12
        im = im.crop((max(0, box[0] - p), max(0, box[1] - p), min(im.width, box[2] + p), min(im.height, box[3] + p)))
    return clean_edges(im)


def qc_prompt(x, kind):
    want = x.get("prompt") or x.get("query")
    sp = SPECIES.get(x.get("species", ""), "")
    extra = ("Also score clean_background: transparent background shown here as flat grey-blue, no halo, no leftover ground." if x.get("role") == "cutout"
             else "Set clean_background to 10.")
    real = " This must be a genuine photograph, scientific figure, map or document image, not an AI-generated picture. Labels and captions that belong to a scientific figure or map are fine: set has_text true only for a large watermark or logo over the subject." if kind == "real" else " Style must be: " + STYLE + "."
    return (f"You are an independent asset checker for a science documentary. Requested: {want}. {sp}{real} {extra} "
            'Reply ONLY JSON: {"subject_match":0-10,"anatomy":0-10,"style":0-10,"clean_background":0-10,"has_text":true|false,"yellow_cast":true|false,"defects":["short fix instructions in English"]}. '
            "Be strict: wrong species or wrong subject means subject_match below 5. Any letters, logos or watermarks means has_text true. "
            "yellow_cast is true when the whole picture has a yellow, amber, orange or sepia tint that the subject does not justify; then add a defect asking for neutral color balance. "
            "A truly yellow or golden object, or fire, lava or a sunset that was requested, is not a cast. Genuine photographs and documents keep their original colors: yellow_cast false.")


def total(s):
    v = (s.get("subject_match", 0) + s.get("anatomy", 0) + s.get("style", 0) + s.get("clean_background", 0)) / 4
    if s.get("has_text") or s.get("subject_match", 0) < 5:
        v = min(v, 4.0)
    if s.get("yellow_cast"):
        v = min(v, PASS - 0.5)  # chưa đạt: tạo lại theo lỗi, hết lượt thì chọn bản tốt nhất
    return round(v, 2)


def make_ai(x, n, fix):
    sp = SPECIES.get(x.get("species", ""), "")
    tail = f" Avoid these problems seen before: {fix}." if fix else ""
    f = CAND / f"{x['id']}-{n}.png"
    if x.get("role") == "cutout":
        prompt = (f"{x['prompt']}. {sp} {STYLE}. {NEUTRAL}. Single subject, entire body visible with margin, "
                  f"isolated on a fully transparent background, no ground, no cast shadow, no text, no letters, no watermark.{tail}")
        crop_cutout(Image.open(io.BytesIO(router.image(prompt, transparent=True)))).save(f)
    else:
        prompt = (f"{x['prompt']}. {sp} {STYLE}. {NEUTRAL}. Wide 16:9 cinematic composition, keep the main subject inside the central area, "
                  f"leave calm areas for overlays, no text, no letters, no logos, no watermark.{tail}")
        fit_bg(Image.open(io.BytesIO(router.image(prompt)))).save(f)
    return f


def fetch(url):
    for wait in (0, 20, 45):
        time.sleep(wait)
        r = requests.get(url, headers=UA, timeout=180)
        if r.status_code != 429:
            r.raise_for_status()
            return r.content
    r.raise_for_status()


def commons_thumb(url):
    """Ảnh Commons: lấy bản 2400px qua API chính thức, tải thẳng upload.wikimedia.org hay bị chặn 429."""
    m = re.search(r"/commons/(?:thumb/)?\w/\w\w/([^/?]+)", url) or re.search(r"/wiki/File:([^?#]+)", url)
    if not m:
        return None
    d = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, timeout=60, params={
        "action": "query", "titles": "File:" + requests.utils.unquote(m[1]), "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 2400, "format": "json"}).json()
    info = next(iter(d["query"]["pages"].values())).get("imageinfo")
    return (info[0].get("thumburl") or info[0]["url"]) if info else None


def page_image(html, page):
    """Link trả về trang web thay vì ảnh: lấy ảnh đại diện của trang."""
    m = re.search(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)', html, re.I) or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)', html, re.I)
    if not m:
        raise RuntimeError(f"không có ảnh ở {page[:80]}")
    return requests.compat.urljoin(page, m[1])


TRIED = {}  # id → link đã thử, không nhận lại


def make_real(x, n, fix):
    fix = " ".join(filter(None, [fix, *TRIED.get(x["id"], [])]))
    q = (f"Find ONE real photograph, scientific figure, map or document image for this need: {x['query']}. "
         "Search the whole internet in any language: Wikimedia Commons, papers, museums, universities, news sites, blogs. The licence does not limit the choice. "
         "Pick the image that shows the need most exactly, at the highest resolution, preferably without a watermark. Never pick an AI-generated image. "
         f"{'Do not return these rejected results: ' + fix + '. ' if fix else ''}"
         'Reply ONLY with JSON: {"title":"","file_page_url":"","direct_image_url":"","license":"","author":"","source_name":""}. '
         "license is what the page states, empty if it states nothing. direct_image_url must be the image file itself (upload.wikimedia.org/... for Commons).")
    if a.codex:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["codex", "--search", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "-o", f"{d}/out.txt", q],
                           stdin=subprocess.DEVNULL, capture_output=True, timeout=600, cwd=d)
            r = router.json_in(Path(f"{d}/out.txt").read_text())
    else:
        r = router.json_in(router.ask(q))
    url = r["direct_image_url"]
    TRIED.setdefault(x["id"], []).append(url)
    data = fetch(commons_thumb(url) or url)
    if data[:200].lstrip().lower().startswith((b"<!doctype", b"<html")):
        url = page_image(data.decode("utf-8", "ignore"), url)
        data = fetch(url)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((2400, 2400))
    f = CAND / f"{x['id']}-{n}.jpg"
    im.save(f, quality=92)
    who = r.get("author") or r.get("source_name") or re.sub(r"^https?://(www\.)?([^/]+).*", r"\2", r.get("file_page_url") or url)
    return f, {"title": r.get("title"), "author": r.get("author"), "license": r.get("license") or "", "url": r.get("file_page_url") or url,
               "credit": " · ".join(filter(None, [who, r.get("license") if len(r.get("license") or "") <= 30 else ""])), "seen": r.get("file_page_url") or url}


def run(x):
    kind, best, history, fix = x["kind"], None, [], ""
    tries = a.tries
    for n in range(1, tries + 1):
        try:
            meta = None
            if kind == "ai":
                f = make_ai(x, n, fix)
            else:
                f, meta = make_real(x, n, fix)
            s = review.ask_json(qc_prompt(x, kind), [f])
            score = total(s)
        except Exception as e:
            history.append({"try": n, "error": str(e)[:200]})
            print(f"  ! {x['id']} lần {n}: {str(e)[:120]}")
            continue
        history.append({"try": n, "score": score, **{k: s.get(k) for k in ("subject_match", "anatomy", "style", "clean_background", "has_text", "defects")}})
        print(f"  · {x['id']} lần {n}: {score}")
        if best is None or score > best[0]:
            if best:
                best[1].unlink(missing_ok=True)
            best = (score, f, meta)
        else:
            f.unlink(missing_ok=True)
        if score >= PASS:
            break
        fix = "; ".join(s.get("defects") or []) if kind == "ai" else "; ".join(filter(None, [fix, meta["seen"] if meta else ""]))
    if not best or best[0] < FLOOR:
        if best:
            best[1].unlink(missing_ok=True)
        print(f"  ✗ {x['id']}: không có bản đạt")
        return x, None, history
    dst = out_path(x)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.suffix.lower() in (".jpg", ".jpeg"):
        Image.open(best[1]).convert("RGB").save(dst, quality=90)
        best[1].unlink()
    else:
        shutil.move(str(best[1]), dst)
    print(f"  ✓ {x['id']}: {best[0]}")
    return x, {"score": best[0], "real": best[2]}, history


CAND.mkdir(parents=True, exist_ok=True)
print(f"{len(todo)} asset cần làm ({sum(x['kind'] == 'ai' for x in todo)} AI, {sum(x['kind'] == 'real' for x in todo)} ảnh thật)")
with ThreadPoolExecutor(3) as pool:
    done = list(pool.map(run, todo))
shutil.rmtree(CAND, ignore_errors=True)

# Ghi kết quả: điểm QC, nguồn ảnh thật, asset thiếu
(ep / "qa").mkdir(exist_ok=True)
qa_p, cr_p = ep / "qa" / "assets.json", ep / "credits.json"
qa = json.loads(qa_p.read_text(encoding="utf-8")) if qa_p.exists() else {}
credits = json.loads(cr_p.read_text(encoding="utf-8")) if cr_p.exists() else {}
missing = []
for x, res, history in done:
    qa[x["id"]] = {"file": str(out_path(x).relative_to(A)), "kept": bool(res), "score": res["score"] if res else None, "tries": history}
    if not res:
        last = next((h.get("defects") for h in reversed(history) if h.get("defects")), None)
        missing.append(f"- {x['id']}: {x.get('prompt') or x.get('query')} | lỗi: {last}")
    elif res["real"]:
        credits[x["file"]] = {k: res["real"][k] for k in ("title", "author", "license", "url", "credit")}
qa_p.write_text(json.dumps(qa, ensure_ascii=False, indent=1), encoding="utf-8")
if credits:
    cr_p.write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
if missing:
    with open(ep / "missing_assets.md", "a", encoding="utf-8") as f:
        f.write("\n".join(missing) + "\n")

# Bảng hình thu nhỏ để soát
files = [(x["id"], out_path(x) if x["kind"] != "shared" else ROOT / "assets" / x["file"]) for x in plan["assets"]]
files = [(i, p) for i, p in files if p.exists()]
if files:
    cols, tw, th = 4, 480, 300
    sheet = Image.new("RGB", (cols * tw, -(-len(files) // cols) * (th + 30)), "#16120e")
    dr = ImageDraw.Draw(sheet)
    for n, (i, p) in enumerate(files):
        im = Image.open(p); bgc = Image.new("RGBA", im.size, "#5a6470"); bgc.alpha_composite(im.convert("RGBA"))
        im = bgc.convert("RGB"); im.thumbnail((tw - 10, th - 10))
        x0, y0 = (n % cols) * tw, (n // cols) * (th + 30)
        sheet.paste(im, (x0 + 5, y0 + 5)); dr.text((x0 + 8, y0 + th + 4), i, fill="#f1e7d3", font=ImageFont.load_default(18))
    sheet.save(ep / "asset_sheet.jpg", quality=85)
fails = [x["id"] for x, r, _ in done if not r]
print(f"Xong. Không đạt: {', '.join(fails) or 'không'}. Bảng hình: {ep / 'asset_sheet.jpg'}")
sys.exit(1 if fails else 0)
