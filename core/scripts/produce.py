"""Pipeline không tốn token, chạy được trên Windows/macOS/Linux: (srt → thời gian cảnh) → kiểm tra cảnh → render.
Dùng: python core/scripts/produce.py channels/<slug>/episodes/<tap> [--preview] [--no-subs] [--force --note "lý do"] [--sep]
Trước khi render cả video: stage_prep.py (tỷ lệ, cân màu cutout), validate_scenes.py, rồi precheck.py duyệt nháp ảnh tĩnh từng cảnh.
Cổng render (Sếp 2026-11-06): precheck 0 lỗi cao (trừ qa/accepted.json); lỗi vừa chỉ là nên sửa. Precheck sập thì không render.
--force: chỉ approver dùng, bắt buộc --note "lý do", ghi vào status.yaml và vẫn tính vào trần render.
Trần render: 1 lần đầu + 2 lần render lại (status.MAX_RENDERS). Chạm trần thì dừng, ghi cờ can_sep; --sep chỉ khi Sếp nói rõ cho render thêm.
Cần audio/voice.* và audio/*.srt: kênh có mục tts thì chạy gen_voice.py, kênh khác do Sếp gửi. Kênh có mục music thì tự chọn nhạc nền."""
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
full = "--preview" not in sys.argv
force = "--force" in sys.argv
note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
if force and not note.strip():
    sys.exit("--force phải kèm --note \"lý do\" (chỉ approver dùng, tính vào trần render)")
st = status.read(ep)
if full and int(st.get("renders") or 0) >= status.MAX_RENDERS and "--sep" not in sys.argv:
    st["can_sep"] = f"đã render {st['renders']} lần (1 lần đầu + 2 lần render lại), cần Sếp quyết render thêm"
    status.write(ep, st)
    sys.exit("Đã chạm trần render: báo Sếp kèm danh sách lỗi và đề xuất (status.yaml ghi can_sep). Chỉ chạy --sep khi Sếp nói rõ.")
srt = [p for p in (ep / "audio").glob("*.srt") if not p.name.endswith(".clean.srt")] if (ep / "audio").exists() else []
if srt:
    subprocess.run([py, str(HERE / "align_srt.py"), str(ep)], check=True)
    if '"lines"' in (ep / "scenes.json").read_text(encoding="utf-8"):
        subprocess.run([py, str(HERE / "align_srt.py"), str(ep), "--apply"], check=True)
subprocess.run([py, str(HERE / "stage_prep.py"), str(ep)], check=True)
subprocess.run([py, str(HERE / "validate_scenes.py"), str(ep / "scenes.json")], check=True)
has_voice = status.has_voice(ep)
if "--preview" not in sys.argv and not has_voice and not (ep / "audio" / "narration.mp3").exists():
    sys.exit("Chưa có audio: đặt file Sếp gửi vào audio/voice.* và audio/voice.srt rồi chạy lại.")
if "--preview" not in sys.argv:
    rc = subprocess.run([py, str(HERE / "precheck.py"), str(ep)]).returncode
    if rc not in (0, 1, 2):
        sys.exit(f"Duyệt nháp bị sập (mã {rc}, không phải còn lỗi): xem log ở trên, sửa nguyên nhân rồi chạy lại. Không render, kể cả --force")
    if rc == 2 and not force:
        sys.exit("Duyệt nháp đã 4 vòng chưa qua cổng: DỪNG, báo Sếp kèm lỗi còn lại trong qa/precheck_vN.md (status.yaml ghi can_sep)")
    if rc and not force:
        sys.exit("Duyệt nháp còn lỗi cao: sửa theo qa/precheck_vN.md rồi chạy lại produce.py (lỗi vừa chỉ là nên sửa)")
    if rc:
        st = status.read(ep)
        st["note"] = f"render --force (precheck chưa qua cổng): {note}"
        status.write(ep, st)
    import pick_music
    pick_music.pick(ep)  # kênh có kho nhạc: thiếu kho thì dừng, không render bản không nhạc
args = [a for i, a in enumerate(sys.argv[2:], 2) if a not in ("--force", "--sep", "--note") and sys.argv[i - 1] != "--note"]
subprocess.run(["node", str(HERE / "render.mjs"), str(ep)] + args, check=True)
if full:
    st = status.read(ep)
    st["renders"] = int(st.get("renders") or 0) + 1
    status.write(ep, st)
    subprocess.run([py, str(HERE / "render_check.py"), str(ep)], check=True)
    print("Chạy QC độc lập: python core/scripts/qc_video.py", ep)
