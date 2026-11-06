"""Chọn ngẫu nhiên 1 bản nhạc trong kho của kênh cho một tập, chép vào <tập>/assets/music/ và ghi vào scenes.json. Remotion tự lặp nhạc cho khớp thời lượng video.
Dùng: python core/scripts/pick_music.py <episode_dir> [--repick]. Tập đã có nhạc thì giữ nguyên để render lại vẫn cùng một bản; --repick để chọn lại.
Cấu hình: channel.yaml có music: {library: <tên kho>, db: <mức chỉnh>}; config/machine.yaml có music_libraries: {<tên kho>: <đường dẫn thư mục trên máy>}. Kênh không có mục music thì bỏ qua."""
import argparse, json, random, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel as chan
from paths import machine

TYPES = {".mp3", ".wav", ".m4a"}


def pick(ep, repick=False):
    ep = Path(ep).resolve()
    conf = chan.load(ep).get("music")
    if not conf:
        return None
    doc_path = ep / "scenes.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    current = doc.get("music")
    if current and not repick and (ep / "assets" / current["asset"]).exists():
        return current
    folder = (machine().get("music_libraries") or {}).get(conf["library"])
    if not folder:
        sys.exit(f"Chưa khai music_libraries.{conf['library']} trong config/machine.yaml")
    folder = Path(folder)
    if not folder.is_dir():
        sys.exit(f"Không thấy kho nhạc: {folder}. Kiểm tra Google Drive Desktop.")
    tracks = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in TYPES and not p.name.startswith("."))
    if not tracks:
        sys.exit(f"Kho nhạc trống: {folder}")
    track = random.choice(tracks)
    rel = f"music/nhac-nen{track.suffix.lower()}"
    dest = ep / "assets" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(track, dest)
    doc["music"] = {"asset": rel, "db": conf.get("db", 0), "source": track.name}
    doc_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc["music"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--repick", action="store_true")
    a = ap.parse_args()
    m = pick(a.episode, a.repick)
    print(f"Nhạc nền: {m['source']}, chỉnh {m['db']} dB" if m else "Kênh này không có kho nhạc.")
