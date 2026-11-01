"""Gọi 9router trên máy (OpenAI-compatible): tạo ảnh cx/gpt-image-2.5-sunburst và hỏi model có tìm web.
9router không tạo được ảnh thì tự chuyển Codex CLI cho hết lượt chạy.
Key: NINEROUTER_API_KEY trong .env, nếu không có thì đọc ~/.9router/db/data.sqlite (chỉ đọc).
Có 2 key cùng bật thì đặt NINEROUTER_KEY_NAME=<tên key> trong .env để chọn đúng key."""
import base64, io, json, os, sqlite3, subprocess, tempfile, time
from pathlib import Path
import requests
from paths import load_env, machine

load_env()
BASE = machine().get("router_url", "http://localhost:20128/v1").rstrip("/")
IMAGE_MODEL = os.environ.get("NINEROUTER_IMAGE_MODEL", "cx/gpt-image-2.5-sunburst")
SEARCH_MODEL = os.environ.get("NINEROUTER_SEARCH_MODEL", "cx/gpt-6.1-sol")


def _key():
    if os.environ.get("NINEROUTER_API_KEY"):
        return os.environ["NINEROUTER_API_KEY"]
    db = Path.home() / ".9router/db/data.sqlite"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    name = os.environ.get("NINEROUTER_KEY_NAME")
    q = "select key from apiKeys where isActive=1" + (" and name=?" if name else "") + " order by createdAt limit 1"
    row = con.execute(q, (name,) if name else ()).fetchone()
    con.close()
    if not row:
        raise SystemExit("Không tìm thấy key 9router đang bật")
    return row[0]


KEY = None


def _post(path, body, timeout):
    global KEY
    KEY = KEY or _key()
    for attempt in range(3):
        try:
            r = requests.post(f"{BASE}{path}", json=body, timeout=timeout, headers={"Authorization": f"Bearer {KEY}"})
            if r.status_code == 200:
                return r.json()
            err = f"HTTP {r.status_code}: {r.text[:300]}"
        except requests.RequestException as e:
            err = str(e)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(err)


def _image_9router(prompt, transparent, size):
    body = {"model": IMAGE_MODEL, "prompt": prompt, "size": size, "n": 1, "output_format": "png"}
    if transparent:
        body["background"] = "transparent"
    d = _post("/images/generations", body, 300)["data"][0]
    if d.get("b64_json"):
        data = base64.b64decode(d["b64_json"])
    else:
        r = requests.get(d["url"], timeout=120)
        r.raise_for_status()
        data = r.content
    from PIL import Image
    Image.open(io.BytesIO(data)).verify()  # hỏng thì báo lỗi ở đây để image() chuyển Codex CLI
    return data


def _image_codex(prompt, transparent, size):
    """Tạo ảnh bằng công cụ tạo ảnh của Codex CLI."""
    from PIL import Image
    w, h = (int(x) for x in size.split("x"))
    shape = "wide 16:9 landscape" if w > h else "square"
    back = " The PNG must have a real alpha channel with a fully transparent background." if transparent else ""
    task = f"Use the image generation tool to create exactly one {shape} image, then save it as out.png in the current directory. Reply only with the file name.{back}\nImage prompt: {prompt}"
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "workspace-write", "-C", td, task],
                       stdin=subprocess.DEVNULL, capture_output=True, timeout=600, check=True)
        data = (Path(td) / "out.png").read_bytes()
    im = Image.open(io.BytesIO(data))
    if transparent and (im.mode != "RGBA" or im.getextrema()[3][0] == 255):
        raise RuntimeError("Codex CLI trả về ảnh không có nền trong suốt")
    return data


_image_down = False  # 9router đã lỗi thì không chờ thử lại cho từng ảnh trong lượt chạy này


def image(prompt, transparent=False, size="1536x1024"):
    """Trả về bytes PNG. Kích thước thật có thể khác size yêu cầu, script gọi tự cắt lại."""
    global _image_down
    if not _image_down:
        try:
            return _image_9router(prompt, transparent, size)
        except (Exception, SystemExit) as e:
            _image_down = True
            print(f"9router không tạo được ảnh, chuyển Codex CLI: {str(e)[:200]}", flush=True)
    return _image_codex(prompt, transparent, size)


def ask(prompt, web=True):
    """Hỏi model qua Responses API, bật tool web_search. Trả về chữ của câu trả lời."""
    body = {"model": SEARCH_MODEL, "input": prompt}
    if web:
        body["tools"] = [{"type": "web_search"}]
    d = _post("/responses", body, 300)
    if d.get("output_text"):
        return d["output_text"]
    return "".join(c.get("text", "") for o in d.get("output", []) if o.get("type") == "message" for c in o.get("content", []))


def json_in(text):
    """Lấy khối JSON đầu tiên trong câu trả lời."""
    a = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if a < 0:
        raise ValueError("Không có JSON trong câu trả lời")
    return json.JSONDecoder().raw_decode(text[a:])[0]
