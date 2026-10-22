# 오답노트 프로토콜 설치 (PC마다 1회)
# 실행: 이 폴더의 install.bat 더블클릭  (또는 PowerShell에서 .\install.ps1)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
function Ok($m)   { Write-Host "  [OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  [!!] $m" -ForegroundColor Yellow }

Write-Host "1) Python 확인"
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py -or (& python --version) -notmatch "Python 3\.(1[0-9])") {
    Warn "Python 3.10 이상이 없습니다. 설치 후 다시 실행하세요:  winget install Python.Python.3.12"
    exit 1
}
Ok (& python --version)

Write-Host "2) 파이썬 패키지 설치 (pymupdf, pillow, pywin32)"
# --upgrade 하지 않음: 이미 깔린 버전은 그대로 둬서 다른 프로그램과 충돌 방지
& python -m pip install --quiet pymupdf pillow pywin32
if ($LASTEXITCODE -ne 0) { Warn "pip 설치 실패"; exit 1 }
Ok "패키지 설치 완료"

Write-Host "3) 한글(HWP) 확인"
if (Test-Path "Registry::HKEY_CLASSES_ROOT\HWPFrame.HwpObject") { Ok "한글 자동화 객체 있음" }
else { Warn "한컴오피스 한글이 설치되어 있지 않거나 등록되지 않았습니다. 한글 설치 후 다시 실행하세요."; exit 1 }

Write-Host "4) 한글 보안모듈 등록 (자동화 시 '접근 허용' 팝업 방지)"
$secDir = "C:\HwpAutomation\Security"
New-Item -ItemType Directory -Force $secDir | Out-Null
Copy-Item "$here\tools\FilePathCheckerModuleExample.dll" $secDir -Force
$reg = "HKCU:\Software\HNC\HwpAutomation\Modules"
New-Item -Path $reg -Force | Out-Null
Set-ItemProperty -Path $reg -Name "FilePathCheckerModuleExample" -Value "$secDir\FilePathCheckerModuleExample.dll"
Ok "보안모듈 등록"

Write-Host "5) Claude Code 스킬 설치"
$skill = Join-Path $env:USERPROFILE ".claude\skills\odap-note"
New-Item -ItemType Directory -Force "$skill\scripts" | Out-Null
Copy-Item "$here\SKILL.md", "$here\README.md" $skill -Force
Copy-Item "$here\scripts\*.py" "$skill\scripts" -Force
Ok "설치 위치: $skill"
$hasClaude = (Get-Command claude -ErrorAction SilentlyContinue) -or
             (Get-AppxPackage -Name "Claude" -ErrorAction SilentlyContinue) -or
             (Test-Path "$env:LOCALAPPDATA\Claude-Data") -or
             (Test-Path "$env:LOCALAPPDATA\AnthropicClaude") -or
             (Test-Path "$env:LOCALAPPDATA\Programs\Claude")
if (-not $hasClaude) { Warn "Claude Code(데스크톱 앱 또는 CLI)를 찾지 못했습니다. 설치되어 있지 않다면 claude.ai/download 에서 설치하세요." }

Write-Host "6) Google Drive 경로 찾기"
& python "$skill\scripts\setup_paths.py"
if ($LASTEXITCODE -ne 0) {
    Warn "자동으로 못 찾았습니다. 아래처럼 직접 지정하세요 (01.수리원수학학원 폴더 경로):"
    Write-Host "     python `"$skill\scripts\setup_paths.py`" --root `"D:\...\01.수리원수학학원`""
} else { Ok "경로 설정 완료" }

Write-Host ""
Write-Host "설치 끝. Claude Code에서 '오답노트 만들어줘 + 작업지시서 파일'로 사용하세요." -ForegroundColor Cyan
