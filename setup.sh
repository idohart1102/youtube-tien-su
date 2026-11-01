#!/usr/bin/env bash
# Cài đặt trên máy mới. Chạy lại nhiều lần cũng an toàn.
set -e
cd "$(dirname "$0")"
ok=1
for c in node npm python3 ffmpeg; do
  if command -v $c >/dev/null 2>&1; then echo "✓ $c"; else echo "✗ thiếu $c (macOS: brew install ${c/npm/node})"; ok=0; fi
done
[ $ok = 1 ] || { echo "Cài các công cụ còn thiếu rồi chạy lại."; exit 1; }
# Chọn đúng Python 3.12: python3 mặc định của máy có thể là bản khác
PY=$(command -v python3.12 || true)
[ -z "$PY" ] && [ -x /opt/homebrew/opt/python@3.12/bin/python3.12 ] && PY=/opt/homebrew/opt/python@3.12/bin/python3.12
[ -n "$PY" ] || { echo "✗ thiếu Python 3.12 (macOS: brew install python@3.12)"; exit 1; }
if [ -d .venv ] && [ "$(.venv/bin/python -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null)" != "3.12" ]; then
  echo "✗ .venv không phải Python 3.12. Đổi tên hoặc xóa .venv rồi chạy lại."; exit 1
fi
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install -q -r requirements.txt
npm install --silent
[ -f config/machine.yaml ] || cp config/machine.example.yaml config/machine.yaml
[ -f .env ] || cp .env.example .env
echo "Xong. Điền .env và kiểm tra config/machine.yaml, sau đó chạy: .venv/bin/python core/scripts/doctor.py"
