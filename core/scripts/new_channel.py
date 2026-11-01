"""Tạo kênh mới. Dùng: python core/scripts/new_channel.py <slug> --lang <mã> [--from <kênh cùng ngôn ngữ>]
--from sao chép quy định ngôn ngữ từ kênh có sẵn. Không có thì tạo mẫu để điền; thiếu mục nào channel.py và doctor.py sẽ báo."""
import argparse, shutil
from paths import ROOT

ap = argparse.ArgumentParser()
ap.add_argument("slug")
ap.add_argument("--lang", default="")
ap.add_argument("--from", dest="src", default="")
a = ap.parse_args()
dst = ROOT / "channels" / a.slug
if dst.exists():
    raise SystemExit(f"Đã có kênh {a.slug}")
shutil.copytree(ROOT / "channels" / (a.src or "_template"), dst, ignore=shutil.ignore_patterns("episodes", "archive", "backlog.csv", "learnings.md", "research"))
for d in ("episodes", "research"):
    (dst / d).mkdir(exist_ok=True)
for f in ("backlog.csv", "learnings.md"):
    shutil.copy(ROOT / "channels" / "_template" / f, dst / f)
y = dst / "channel.yaml"
s = y.read_text(encoding="utf-8").replace("slug: CHANGE_ME", f"slug: {a.slug}")
if a.lang:
    s = s.replace("language: CHANGE_ME", f"language: {a.lang}")
y.write_text(s, encoding="utf-8")
print(f"Đã tạo {dst.relative_to(ROOT)}. Điền channel.yaml (khối lang), theme.json, script/style.md, script/lang.md. Kiểm tra: python core/scripts/channel.py {a.slug}")
