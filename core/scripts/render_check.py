"""Kiểm tra video đã render, không tốn token: đứng hình, đoạn đen, phụ đề quá dài, tổng thời lượng; xuất bảng khung hình có mốc giờ cho QC.
Dùng: python core/scripts/render_check.py <episode_dir> [--every 3]. Mã thoát 1 nếu có lỗi cần sửa. Kết quả ghi qa/render_check.json."""
import json, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import channel as chan
import video_output

ep = Path(sys.argv[1]).resolve()
every = float(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 3.0
video = ep / "render" / "final.mp4"
if not video.exists():
    sys.exit("Chưa có render/final.mp4")
cfg = chan.load(ep)
problems, notes = [], []
technical = video_output.inspect(ep)
problems += technical['problems']
if not technical['passed']:
    qa = ep / 'qa'
    qa.mkdir(exist_ok=True)
    (qa / 'render_check.json').write_text(json.dumps({'technical': technical, 'problems': problems, 'notes': [], 'sheets': []}, ensure_ascii=False, indent=1), encoding='utf-8')
    print('CÓ LỖI KỸ THUẬT:', '; '.join(problems))
    sys.exit(1)

probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height", "-of", "json", str(video)], capture_output=True, text=True, check=True)
info = json.loads(probe.stdout)
dur = float(info["format"]["duration"])
vs = next(s for s in info["streams"] if s["codec_type"] == "video")
scenes_doc = json.loads((ep / "scenes.json").read_text(encoding="utf-8")) if (ep / "scenes.json").exists() else {}
want = (1080, 1920) if scenes_doc.get("format") == "9:16" else (1920, 1080)
if (vs["width"], vs["height"]) != want:
    problems.append(f"Độ phân giải {vs['width']}x{vs['height']}, cần {want[0]}x{want[1]}")
if not any(s["codec_type"] == "audio" for s in info["streams"]):
    problems.append("Video không có âm thanh")

log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "freezedetect=n=0.002:d=3.0,blackdetect=d=1.5:pic_th=0.98", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
freezes = re.findall(r"freeze_start: ([\d.]+)[\s\S]*?freeze_duration: ([\d.]+)", log)
blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)
problems += [f"Đứng hình {float(b):.1f} giây từ giây {float(a):.1f}" for a, b in freezes]
notes += [f"Đoạn đen từ giây {float(a):.1f} đến {float(b):.1f}, kiểm tra có chủ ý không" for a, b in blacks]

# Khoảnh khắc tĩnh: khung gần như không đổi (đã làm mờ để bỏ hạt nhiễu). Ngưỡng hiệu chỉnh trên tập Tràng An: ảnh thật zoom 3% đo ra dưới 0,15.
import numpy as np
SW, SH, FPS, STILL = 160, 90, 4, 0.15
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={FPS},scale={SW}:{SH},gblur=sigma=1.5,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8)[: len(raw) // (SW * SH) * SW * SH].reshape(-1, SH, SW).astype(np.float32)
low = list(np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2)) < STILL) + [False]
still, i = [], 0
while i < len(low):
    j = i
    while low[j]:
        j += 1
    if (j - i) / FPS >= 1.5:
        still.append((i / FPS, (j - i) / FPS))
    i = j + 1
mmss = lambda x: f"{int(x // 60)}:{int(x % 60):02}"
problems += [f"Khoảnh khắc tĩnh {l:.1f} giây ở {mmss(a)}: thêm chuyển động (zoom chậm, quét sáng, bụi, cutout cử động)" for a, l in still if l >= 2.0]
if any(l < 2.0 for a, l in still):
    notes.append("Gần tĩnh 1,5-2 giây ở " + ", ".join(mmss(a) for a, l in still if l < 2.0))

tl = ep / "timeline.json"
if tl.exists():
    doc = json.loads(tl.read_text(encoding="utf-8"))
    limit = cfg["lang"]["subtitle"]["max"] + 6
    long_subs = [s for s in doc["subs"] if len(s["text"]) > limit]
    problems += [f"Phụ đề dài {len(s['text'])} ký tự ở giây {s['start']:.1f}: {s['text'][:40]}" for s in long_subs[:10]]
    if abs(doc["audio_end"] - dur) > 1.5:
        problems.append(f"Video {dur:.1f} giây lệch audio {doc['audio_end']:.1f} giây")

# Bảng khung hình: mỗi bảng 5x4 ô có mốc giờ, QC đọc được cả video mà không tốn nhiều token
qa = ep / "qa"
qa.mkdir(exist_ok=True)
for old in qa.glob("frames_*.jpg"):
    old.unlink()
sheets = []
with tempfile.TemporaryDirectory() as td:
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps=1/{every},scale=480:-1", f"{td}/f%05d.jpg"], check=True)
    frames = sorted(Path(td).glob("f*.jpg"))
    font = ImageFont.load_default(20)
    cell_h = round(480 * vs["height"] / vs["width"])  # đúng tỷ lệ video, video dọc không bị cắt
    for k in range(0, len(frames), 20):
        part = frames[k:k + 20]
        sheet = Image.new("RGB", (5 * 480, -(-len(part) // 5) * cell_h), "#000")
        for n, f in enumerate(part):
            x, y = (n % 5) * 480, (n // 5) * cell_h
            sheet.paste(Image.open(f), (x, y))
            t = (k + n + 0.5) * every  # bộ lọc fps lấy khung ở giữa mỗi khoảng
            d = ImageDraw.Draw(sheet)
            d.rectangle([x, y, x + 76, y + 26], fill="#000")
            d.text((x + 4, y + 2), f"{int(t // 60)}:{int(t % 60):02}", fill="#ffd23f", font=font)
        p = qa / f"frames_{k // 20:03d}.jpg"
        sheet.save(p, quality=82)
        sheets.append(p.name)
problems += video_output.report_problems(ep, {'technical': technical})
(qa / "render_check.json").write_text(json.dumps({"duration": round(dur, 2), "every": every, "technical": technical, "problems": problems, "notes": notes, "sheets": sheets}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{dur:.1f} giây, {len(sheets)} bảng khung hình")
for n in notes:
    print("  Lưu ý:", n)
for p in problems:
    print("  Lỗi:", p)
print("OK" if not problems else "CÓ LỖI")
sys.exit(1 if problems else 0)
