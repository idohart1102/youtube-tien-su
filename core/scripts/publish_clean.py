"""Đưa thành phẩm lên Drive, đối chiếu từng file, rồi xóa media không còn dùng trên máy. Chỉ chạy khi đã chốt không render lại.
  python core/scripts/publish_clean.py <tập> --dry-run   xem sẽ tải gì, xóa gì
  python core/scripts/publish_clean.py <tập>             tải lên, kiểm tra, xóa (cần status: final=ok)
  python core/scripts/publish_clean.py --expire          xóa gói nguồn trên Drive quá hạn 30 ngày, video thành phẩm giữ nguyên
Cấu hình trong config/machine.yaml: drive_mode (desktop | rclone), drive_path hoặc drive_remote. Sai checksum thì dừng, không xóa gì."""
import hashlib, os, shutil, subprocess, sys, tempfile, time, zipfile
from datetime import date, timedelta
from pathlib import Path
from paths import ROOT, machine
import status

KEEP_DAYS = 30
SOURCE = "nguon-30-ngay"
CLEAN = ["render", "audio", "assets", "thumb", ".cand"]  # chỉ được xóa các thư mục này, và chỉ trong đúng tập
CLEAN_FILES = ["asset_sheet.jpg"]
m = machine()
MODE = m.get("drive_mode", "desktop")


def sha(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Desktop:
    """Google Drive Desktop: chép vào thư mục đồng bộ rồi chờ Drive nhận file."""
    def __init__(self):
        self.root = Path(m.get("drive_path", ""))
        if not self.root.is_dir():
            raise SystemExit(f"Không thấy thư mục Drive: {self.root}. Kiểm tra drive_path trong config/machine.yaml")

    def put(self, src, rel):
        dst = self.root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        if sha(src) != sha(dst):
            raise SystemExit(f"Sai checksum: {rel}")
        return dst

    def wait_synced(self, dsts, minutes=60):
        """Drive Desktop gắn item-id lên file khi đã nhận. Chưa có sau thời gian chờ thì dừng, không xóa."""
        end = time.time() + minutes * 60
        pending = list(dsts)
        while pending and time.time() < end:
            pending = [d for d in pending if not _synced(d)]
            if pending:
                time.sleep(20)
        if pending:
            raise SystemExit("Drive chưa nhận xong: " + ", ".join(p.name for p in pending) + ". Chạy lại sau, chưa xóa gì.")

    def remove(self, rel):
        p = self.root / rel
        if p.exists():
            shutil.rmtree(p)


def _synced(p):
    r = subprocess.run(["xattr", "-p", "com.google.drivefs.item-id#S", str(p)], capture_output=True, text=True)
    return r.returncode == 0 and bool(r.stdout.strip())


class Rclone:
    def __init__(self):
        self.remote = m.get("drive_remote", "")
        if not self.remote:
            raise SystemExit("Chưa khai drive_remote trong config/machine.yaml")

    def put(self, src, rel):
        dst = f"{self.remote.rstrip('/')}/{rel}"
        subprocess.run(["rclone", "copyto", "--checksum", str(src), dst], check=True)
        got = subprocess.run(["rclone", "md5sum", dst], capture_output=True, text=True, check=True).stdout.split()
        if not got or got[0] != sha(src):
            raise SystemExit(f"Sai checksum: {rel}")
        return dst

    def wait_synced(self, dsts, minutes=0):
        return

    def remove(self, rel):
        subprocess.run(["rclone", "purge", f"{self.remote.rstrip('/')}/{rel}"], check=False)


def backend():
    return Rclone() if MODE == "rclone" else Desktop()


def expire():
    store, today = backend(), date.today()
    for ep in sorted(ROOT.glob("channels/*/episodes/*")):
        if not ep.is_dir():
            continue
        d = status.read(ep)
        when = d.get("publish", {}).get("source_expires")
        if when and not d["publish"].get("source_deleted") and date.fromisoformat(str(when)) <= today:
            store.remove(f"{ep.parent.parent.name}/{ep.name}/{SOURCE}")
            d["publish"]["source_deleted"] = today.isoformat()
            status.write(ep, d)
            print("Đã xóa gói nguồn:", ep.name)


def plan(ep):
    slug = ep.parent.parent.name
    base = f"{slug}/{ep.name}"
    files = []
    v = ep / "render" / "final.mp4"
    if not v.exists():
        raise SystemExit("Chưa có render/final.mp4")
    files.append((v, f"{base}/{slug}_{ep.name}.mp4"))
    thumbs = sorted((ep / "thumb").glob("*.jpg")) if (ep / "thumb").exists() else []
    files += [(t, f"{base}/thumbnail/{t.name}") for t in thumbs]
    for name in ("meta.md", "brief.md", "storyboard.md", "script.md"):  # dữ liệu tập không lên GitHub, Drive giữ bản chữ
        if (ep / name).exists():
            files.append((ep / name, f"{base}/{name}"))
    for q in sorted((ep / "qa").glob("qc_v*.md")) if (ep / "qa").exists() else []:
        files.append((q, f"{base}/qa/{q.name}"))
    return base, files


def source_pack(ep, tmp):
    """Gói nguồn giữ 30 ngày để sửa nhỏ mà không phải tạo lại asset: audio, srt, asset đã chọn."""
    z = Path(tmp) / "nguon.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as f:
        for sub in ("audio", "assets"):
            d = ep / sub
            if d.exists():
                for p in d.rglob("*"):
                    if p.is_file():
                        f.write(p, p.relative_to(ep))
    return z


def main():
    if "--expire" in sys.argv:
        return expire()
    ep = Path(sys.argv[1]).resolve()
    if not (ep.parent.name == "episodes" and (ep.parent.parent / "channel.yaml").exists()):
        raise SystemExit(f"Không phải thư mục tập: {ep}")
    dry = "--dry-run" in sys.argv
    d = status.read(ep)
    base, files = plan(ep)
    doomed = [ep / c for c in CLEAN if (ep / c).exists()] + [ep / f for f in CLEAN_FILES if (ep / f).exists()]
    size = sum(sum(p.stat().st_size for p in x.rglob("*") if p.is_file()) if x.is_dir() else x.stat().st_size for x in doomed)
    print("Tải lên:", *[f"  {r}" for _, r in files], f"  {base}/{SOURCE}/nguon.zip", sep="\n")
    print(f"Sẽ xóa trên máy ({size / 1e6:.0f} MB):", *[f"  {x.relative_to(ep)}" for x in doomed], sep="\n")
    if dry:
        return
    if status.final_stale(ep):
        raise SystemExit("Video đã đổi sau khi chốt. QC lại và chốt lại: python core/scripts/status.py <tập> final=ok")
    if d["approved"].get("final") == "ok":
        status.require_brief(ep)
        bad = status.final_problems(ep)
        if bad:
            raise SystemExit("Bản đã chốt không còn đủ điều kiện: " + "; ".join(bad))
    if not d["approved"].get("final"):
        raise SystemExit("Chưa chốt bản cuối. Vai trò approver chạy: python core/scripts/status.py <tập> final=ok")
    store = backend()
    dsts = [store.put(src, rel) for src, rel in files]
    with tempfile.TemporaryDirectory() as td:
        dsts.append(store.put(source_pack(ep, td), f"{base}/{SOURCE}/nguon.zip"))
    store.wait_synced(dsts)
    for x in doomed:  # đã đối chiếu xong, chỉ xóa trong danh sách cho phép của đúng tập này
        shutil.rmtree(x) if x.is_dir() else x.unlink()
    d["stage"] = "done"
    d["publish"] = {"drive": base, "at": date.today().isoformat(), "source_expires": (date.today() + timedelta(days=KEEP_DAYS)).isoformat()}
    status.write(ep, d)
    print("Xong. Trên Drive:", base, "| Gói nguồn hết hạn:", d["publish"]["source_expires"])


if __name__ == "__main__":
    main()
