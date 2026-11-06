"""Vai trò chấm độc lập: gửi ảnh cho AI và nhận JSON. Nhà cung cấp lấy từ config/machine.yaml (review_provider: 9router | codex).
Người viết hoặc tạo asset không tự chấm bài của mình."""
import base64, io, json, subprocess, tempfile, threading
from pathlib import Path
import requests
from PIL import Image
from paths import machine
import router


def _jpeg(path, edge=1024, matte="#5a6470"):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGBA", im.size, matte)
        bg.alpha_composite(im.convert("RGBA"))
        im = bg
    im = im.convert("RGB")
    im.thumbnail((edge, edge))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=84)
    return b.getvalue()


def _via_9router(prompt, images):
    content = [{"type": "input_text", "text": prompt}]
    for b in images:
        content.append({"type": "input_image", "image_url": "data:image/jpeg;base64," + base64.b64encode(b).decode()})
    d = router._post("/responses", {"model": router.SEARCH_MODEL, "input": [{"role": "user", "content": content}]}, 300)
    return d.get("output_text") or "".join(c.get("text", "") for o in d.get("output", []) if o.get("type") == "message" for c in o.get("content", []))


def _via_codex(prompt, images, search=False):
    with tempfile.TemporaryDirectory() as td:
        files = []
        for n, b in enumerate(images):
            f = Path(td) / f"i{n}.jpg"
            f.write_bytes(b)
            files.append(str(f))
        out = Path(td) / "out.txt"
        cmd = ["codex"] + (["--search"] if search else []) + ["exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "-o", str(out)]
        for f in files:
            cmd += ["-i", f]
        subprocess.run(cmd + ["--", prompt], stdin=subprocess.DEVNULL, capture_output=True, timeout=600, cwd=td, check=True)
        return out.read_text(encoding="utf-8")


def ask_images(prompt, paths, edge=1024, provider=None):
    """Trả về chữ câu trả lời. Nhà cung cấp chính lỗi thì chuyển sang nhà cung cấp còn lại."""
    images = [_jpeg(p, edge) for p in paths]
    first = provider or machine().get("review_provider", "9router")
    order = [first] + [x for x in ("9router", "codex") if x != first]
    err = None
    for name in order:
        try:
            return (_via_codex if name == "codex" else _via_9router)(prompt, images)
        except (Exception, SystemExit) as e:  # lỗi mạng, hết hạn mức, không tìm thấy key 9router: thử bên còn lại
            err = e
    raise RuntimeError(f"Không chấm được bằng {order}: {err}")


def ask_text(prompt, provider=None):
    """Chấm văn bản không kèm ảnh, cùng thứ tự nhà cung cấp."""
    first = provider or machine().get("review_provider", "9router")
    order = [first] + [x for x in ("9router", "codex") if x != first]
    err = None
    for name in order:
        try:
            return _via_codex(prompt, []) if name == "codex" else router.ask(prompt, web=False)
        except (Exception, SystemExit) as e:
            err = e
    raise RuntimeError(f"Không chấm được bằng {order}: {err}")


def ask_web(prompt, provider=None):
    """Hỏi có tìm web, cùng thứ tự nhà cung cấp. Dùng cho kiểm tra fact."""
    first = provider or machine().get("review_provider", "9router")
    order = [first] + [x for x in ("9router", "codex") if x != first]
    err = None
    for name in order:
        try:
            return _via_codex(prompt, [], search=True) if name == "codex" else router.ask(prompt, web=True)
        except (Exception, SystemExit) as e:
            err = e
    raise RuntimeError(f"Không kiểm tra được bằng {order}: {err}")


def best_round(rows):
    """Chọn vòng chấm tốt nhất: ít cổng trượt, ít lỗi fact, điểm cao, ít câu không tự nhiên; bằng nhau lấy vòng sau."""
    return min(rows, key=lambda r: (r["gates_failed"], r["fact_errors"], -r["pct"], r["unnatural"], -r["round"]))


def ask_json(prompt, paths, edge=1024, provider=None):
    return router.json_in(ask_images(prompt, paths, edge, provider))


def check_qc(r):
    """Kết quả QC video phải đủ điểm và danh sách lỗi đúng dạng, không thì coi như chưa chấm."""
    if not isinstance(r, dict) or isinstance(r.get("score"), bool) or not isinstance(r.get("score"), (int, float)) or not 0 <= r["score"] <= 10:
        raise ValueError("Thiếu điểm QC hợp lệ")
    if not isinstance(r.get("issues"), list) or any(not isinstance(x, dict) or x.get("severity") not in ("cao", "vừa", "thấp") for x in r["issues"]):
        raise ValueError("Danh sách lỗi QC không hợp lệ")
    return r


def check_facts(r, ids):
    """Kết quả kiểm tra fact phải có đúng mỗi mã một dòng, với 3 kết quả cho phép."""
    facts = r.get("facts") if isinstance(r, dict) else None
    if not isinstance(facts, list) or any(not isinstance(f, dict) for f in facts):
        raise ValueError("Thiếu danh sách fact")
    if sorted(str(f.get("id")) for f in facts) != sorted(ids):
        raise ValueError("Thiếu, thừa hoặc trùng dòng fact")
    if any(f.get("ket_qua") not in ("dung", "sai", "chua_xac_minh") for f in facts):
        raise ValueError("Kết quả fact không hợp lệ")
    return facts


_CACHE_LOCK = threading.Lock()


def ask_json_cached(cache_path, key, prompt, paths, edge=1024, provider=None, tries=3, validate=check_qc):
    """Như ask_json nhưng lưu từng kết quả: lỗi giữa chừng thì chạy lại không tốn lượt đã chấm. Trả lời sai dạng thì hỏi lại.
    An toàn khi nhiều luồng chấm song song: chỉ khóa lúc đọc/ghi file, không khóa lúc chờ AI."""
    cache_path = Path(cache_path)
    with _CACHE_LOCK:
        cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    if key in cache:
        return validate(cache[key])
    for attempt in range(tries):
        try:
            r = validate(ask_json(prompt, paths, edge, provider))
            break
        except ValueError:
            if attempt == tries - 1:
                raise
    with _CACHE_LOCK:
        cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
        cache[key] = r
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return r


if __name__ == "__main__":
    import sys
    print(ask_images(sys.argv[1], sys.argv[2:]))
