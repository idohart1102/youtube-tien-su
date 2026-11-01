"""Pipeline không tốn token, chạy được trên Windows/macOS/Linux: (srt → thời gian cảnh) → kiểm tra cảnh → render.
Dùng: python core/scripts/produce.py channels/<slug>/episodes/<tap> [--preview] [--no-subs]
Audio do Sếp tạo ở ngoài hệ thống: cần audio/voice.* và audio/*.srt."""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ep = Path(sys.argv[1]).resolve()
py = sys.executable
sys.path.insert(0, str(HERE))
import status
status.require_brief(ep)
import make_shared_assets
make_shared_assets.ensure()
srt = [p for p in (ep / "audio").glob("*.srt") if not p.name.endswith(".clean.srt")] if (ep / "audio").exists() else []
if srt:
    subprocess.run([py, str(HERE / "align_srt.py"), str(ep)], check=True)
    if '"lines"' in (ep / "scenes.json").read_text(encoding="utf-8"):
        subprocess.run([py, str(HERE / "align_srt.py"), str(ep), "--apply"], check=True)
subprocess.run([py, str(HERE / "validate_scenes.py"), str(ep / "scenes.json")], check=True)
has_voice = status.has_voice(ep)
if "--preview" not in sys.argv and not has_voice and not (ep / "audio" / "narration.mp3").exists():
    sys.exit("Chưa có audio: đặt file Sếp gửi vào audio/voice.* và audio/voice.srt rồi chạy lại.")
subprocess.run(["node", str(HERE / "render.mjs"), str(ep)] + sys.argv[2:], check=True)
if "--preview" not in sys.argv:
    subprocess.run([py, str(HERE / "render_check.py"), str(ep)])  # có lỗi vẫn đi tiếp: QC ghi lại để approver quyết định
    print("Chạy QC độc lập: python core/scripts/qc_video.py", ep)
