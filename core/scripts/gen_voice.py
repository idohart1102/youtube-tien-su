"""script.md → audio/voice.mp3 + audio/voice.srt qua API TTS dùng chung, theo mục tts trong channel.yaml. Kênh không có mục tts thì Sếp gửi audio.
Dùng: python core/scripts/gen_voice.py <episode_dir> [--replace]. Mỗi lần tạo tốn credit; yêu cầu trùng hệt được dịch vụ dùng lại, không tính tiền.
KingCong có thể trả srt một dòng dài cho cả đoạn. Khi đó thời gian mỗi câu tính theo độ dài câu rồi bám vào khoảng lặng thật trong audio; srt gốc lưu ở audio/voice.kingcong.txt.
Địa chỉ API: biến TTS_URL, mặc định http://127.0.0.1:8791."""
import argparse, json, os, re, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel as chan
import status
from paths import load_env

IN_PROGRESS = {"queued", "submitting", "polling", "downloading"}
MAX_CUE_S = 12.0     # cue dài hơn mức này thì không đủ để khớp thời gian từng câu
TIMEOUT_S = 3600


def call(base, method, path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API TTS báo lỗi {e.code}: {e.read().decode(errors='replace')[:300]}. Không tự gửi lại, kiểm tra credit trước khi thử lại.")
    except urllib.error.URLError as e:
        raise SystemExit(f"Không gọi được API TTS tại {base}: {e.reason}. Kiểm tra bằng: tts service status")


def ts(s):
    h, m, rest = s.strip().split(":")
    sec, ms = rest.replace(".", ",").split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def fmt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def cue_lengths(srt):
    return [ts(b) - ts(a) for a, b in re.findall(r"([\d:,.]+)\s*-->\s*([\d:,.]+)", srt)]


def media_info(path):
    """Tổng thời lượng và các khoảng lặng (bắt đầu, kết thúc), đọc từ ffmpeg."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-35dB:d=0.15", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return int(h) * 3600 + int(m) * 60 + float(s), list(zip(starts, ends))


def sentence_cues(text, split_re, count, dur, gaps):
    """Chia thời lượng theo độ dài từng câu, rồi đưa mỗi ranh giới về khoảng lặng gần nhất."""
    sents = [x.strip() for x in re.split(split_re, text) if x.strip()]
    weights = [max(1, count(x)) for x in sents]
    total, acc, cues, start, snapped = sum(weights), 0, [], 0.0, 0
    for i, (s, w) in enumerate(zip(sents, weights)):
        acc += w
        target = dur * acc / total
        window = max(1.0, dur * w / total * 0.5)
        near = [g for g in gaps if g[1] > start + 0.2 and abs((g[0] + g[1]) / 2 - target) <= window]
        if i == len(sents) - 1:
            end, next_start = dur, dur
        elif near:
            g = min(near, key=lambda g: abs((g[0] + g[1]) / 2 - target))
            end, next_start = g[0], g[1]
            snapped += 1
        else:
            end, next_start = target, target
        cues.append((start, max(end, start + 0.1), s))
        start = next_start
    body = "\n".join(f"{i}\n{fmt(a)} --> {fmt(b)}\n{s}\n" for i, (a, b, s) in enumerate(cues, 1))
    return body, len(cues), snapped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--replace", action="store_true", help="thay audio đang có trong tập")
    ap.add_argument("--force", action="store_true", help="bỏ qua kiểm kịch bản đã chấm (chỉ khi Sếp yêu cầu)")
    args = ap.parse_args()
    ep = Path(args.episode).resolve()
    cfg = chan.load(ep)
    tts = cfg.get("tts")
    if not tts:
        sys.exit("Kênh này không có mục tts trong channel.yaml: audio và srt do Sếp gửi.")
    script = ep / "script.md"
    if not script.exists():
        sys.exit("Chưa có script.md. Chạy export_narration.py trước.")
    # Tốn credit: chỉ tạo giọng khi storyboard.md đúng là bản đã qua qc_script (trùng một qa/snapshot_vN.md đạt, hoặc bản tốt nhất sau --use-best)
    sb = ep / "storyboard.md"
    if not args.force and not sb.exists():
        sys.exit("Chưa có storyboard.md đã chấm: không tạo giọng (tốn credit). --force chỉ khi Sếp yêu cầu.")
    if not args.force and status.read(ep).get("can_sep"):
        sys.exit(f"Tập đang chờ Sếp ({status.read(ep)['can_sep']}): không tạo giọng cho tới khi Sếp quyết và xóa cờ can_sep.")
    if not args.force and sb.exists():
        import review
        rows = [json.loads(q.read_text(encoding="utf-8")) for q in (ep / "qa").glob("script_v*.json") if not q.name.endswith(".raw.json")]
        rows = [x for x in rows if x.get("file") == "storyboard.md"]
        ok = [x for x in rows if not x["gates_failed"] and not x["fact_errors"] and x["pct"] >= 80]
        if len(rows) >= 5:
            ok.append(review.best_round(rows))  # hết 5 vòng: bản tốt nhất (--use-best)
        good = {(ep / "qa" / f"snapshot_v{x['n']}.md").read_text(encoding="utf-8") for x in ok if (ep / "qa" / f"snapshot_v{x['n']}.md").exists()}
        if sb.read_text(encoding="utf-8") not in good:
            sys.exit("storyboard.md không phải bản đã chấm đạt (hoặc bản tốt nhất sau 5 vòng): chạy qc_script.py / --use-best trước. --force chỉ khi Sếp yêu cầu.")
        if script.stat().st_mtime < sb.stat().st_mtime:
            sys.exit("script.md cũ hơn storyboard.md: chạy export_narration.py trước, không tạo giọng từ bản cũ.")
    audio_dir = ep / "audio"
    voice, srt = audio_dir / "voice.mp3", audio_dir / "voice.srt"
    if (voice.exists() or srt.exists()) and not args.replace:
        sys.exit("Tập đã có audio. Muốn thay thì thêm --replace.")
    base = load_env().get("TTS_URL", os.environ.get("TTS_URL", "http://127.0.0.1:8791")).rstrip("/")
    text = script.read_text(encoding="utf-8")
    body = {"text": text, "project": tts["project"], "provider": tts["provider"], "model_id": tts["model_id"],
            "voice_id": tts["voice_id"], "export_srt": True}
    body.update({k: tts[k] for k in ("speed", "stability", "similarity", "style") if k in tts})
    job = json.loads(call(base, "POST", "/v1/speech", body))
    deadline = time.monotonic() + TIMEOUT_S
    while job["state"] in IN_PROGRESS and time.monotonic() < deadline:
        time.sleep(3)
        job = json.loads(call(base, "GET", f"/v1/jobs/{job['id']}"))
    if job["state"] != "done":
        sys.exit(f"Job {job['id']} ở trạng thái {job['state']}: {job.get('error')}. Không tự gửi lại vì có thể đã bị trừ credit; báo Sếp.")
    if not job.get("srt_url"):
        sys.exit(f"Job {job['id']} không có phụ đề: {job.get('error')}")
    audio_dir.mkdir(parents=True, exist_ok=True)
    voice.write_bytes(call(base, "GET", job["audio_url"]))
    raw = call(base, "GET", job["srt_url"]).decode("utf-8-sig")
    dur, gaps = media_info(voice)
    longest = max(cue_lengths(raw) or [dur])
    note = f"srt gốc, cue dài nhất {longest:.1f} giây"
    if longest > MAX_CUE_S:
        (audio_dir / "voice.kingcong.txt").write_text(raw, encoding="utf-8")
        raw, n, snapped = sentence_cues(text, cfg["lang"]["sentence_split"], chan.speech(cfg).count, dur, gaps)
        note = f"srt tách theo câu: {n} câu, {snapped} ranh giới bám khoảng lặng"
    srt.write_text(raw, encoding="utf-8")
    cost = "dùng lại kết quả cũ, không tính tiền" if job.get("reused") else f"{job['credit_cost']} credit"
    print(f"audio/voice.mp3 {dur:.1f} giây, {note}, {cost}, job {job['id']}")


if __name__ == "__main__":
    main()
