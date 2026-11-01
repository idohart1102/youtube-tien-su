# Cài đặt trên Windows. Chạy: powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$ok = $true
foreach ($c in "node","npm","python","ffmpeg") {
  if (Get-Command $c -ErrorAction SilentlyContinue) { Write-Host "OK $c" }
  else { Write-Host "THIEU $c  (winget install OpenJS.NodeJS.LTS / Python.Python.3.12 / Gyan.FFmpeg)"; $ok = $false }
}
if (-not $ok) { Write-Host "Cai cac cong cu con thieu roi chay lai."; exit 1 }
# Chọn đúng Python 3.12 bằng trình chạy py của Windows
if (-not (Test-Path .venv)) { py -3.12 -m venv .venv; if ($LASTEXITCODE -ne 0) { Write-Host "THIEU Python 3.12: winget install Python.Python.3.12"; exit 1 } }
.\.venv\Scripts\pip install -q -r requirements.txt
npm install --silent
if (-not (Test-Path config\machine.yaml)) { Copy-Item config\machine.example.yaml config\machine.yaml }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Xong. Dien .env, kiem tra config\machine.yaml, roi chay: .\.venv\Scripts\python core\scripts\doctor.py"
