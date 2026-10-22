# 오답노트 자동 제작 스킬 — 설치 가이드

버전: v1.0 (2026-10-21)

선생님이 준 **오답노트 작업 지시서**(학생·교재명·쪽/번호, 손글씨 스캔 PDF 가능)를 Claude Code에 주면,
교재 PDF에서 문제를 찾아 잘라 `오답노트 양식.hwp`에 채우고
`05. 강사별 폴더\00. 오답노트\<선생님>T\<학생 폴더>\` 에 HWP로 저장해 주는 스킬입니다.

---

## 1. 준비물 (설치 전에 확인)

| 항목 | 확인 방법 | 없으면 |
|---|---|---|
| Windows 10/11 | — | — |
| 한컴오피스 **한글** | 한글이 실행되는지 | 한글 설치 |
| **Python 3.10 이상** | 명령 프롬프트에서 `python --version` | `winget install Python.Python.3.12` 실행 후 새 창에서 다시 확인 |
| **Claude Code** (데스크톱 앱 또는 CLI) | Claude 데스크톱 앱의 Code 탭 | claude.ai/download 에서 설치 |
| **Google Drive 데스크톱** + 학원 공유폴더 | 탐색기에서 `01.수리원수학학원` 폴더가 보이는지 | Drive 설치 후 로그인, 공유폴더를 "내 드라이브에 바로가기 추가" |

> Python 설치 화면이 나오면 **"Add python.exe to PATH"에 체크**해야 합니다.

## 2. 설치 (PC마다 1회, 약 2분)

1. 설치 파일 받기 — 둘 중 하나
   - Google Drive: `01.수리원수학학원\AutoHwp\오답노트 프로토콜` 폴더를 열거나
   - 압축 파일 `오답노트 스킬 설치파일.zip`을 받아 **아무 폴더에 압축 해제**
2. 폴더 안의 **`install.bat` 더블클릭**
3. 창에 아래 6단계가 모두 `[OK]`로 나오면 끝입니다.

```
1) Python 확인                  [OK] Python 3.12.x
2) 파이썬 패키지 설치            [OK] 패키지 설치 완료
3) 한글(HWP) 확인               [OK] 한글 자동화 객체 있음
4) 한글 보안모듈 등록            [OK] 보안모듈 등록
5) Claude Code 스킬 설치        [OK] 설치 위치: C:\Users\<이름>\.claude\skills\odap-note
6) Google Drive 경로 찾기       [OK] 경로 설정 완료
```

설치가 하는 일:
- 파이썬 패키지 `pymupdf`, `pillow`, `pywin32` 설치 (이미 있으면 버전을 바꾸지 않음)
- 한글 보안모듈 등록 → 자동화할 때 뜨는 "접근 허용" 팝업 방지
  (`C:\HwpAutomation\Security\FilePathCheckerModuleExample.dll` + 현재 사용자 레지스트리)
- 스킬 복사 → `%USERPROFILE%\.claude\skills\odap-note`
- `01.수리원수학학원` 위치 자동 탐색 → `%USERPROFILE%\.claude\오답노트_config.json`

## 3. 6단계에서 경로를 못 찾을 때

Google Drive 위치는 PC마다 다릅니다 (드라이브 문자 G:/H:, "내 드라이브", 공유 드라이브 등).
탐색기에서 `01.수리원수학학원` 폴더를 찾아 **주소창 경로를 복사**한 뒤:

```bat
python "%USERPROFILE%\.claude\skills\odap-note\scripts\setup_paths.py" --root "여기에 복사한 경로"
```

예: `--root "H:\내 드라이브\01.수리원수학학원"`

또는 Claude에게 "오답노트 경로 다시 잡아줘"라고 하면 경로를 물어보고 설정해 줍니다.

## 4. 설치 확인

```bat
python "%USERPROFILE%\.claude\skills\odap-note\scripts\setup_paths.py"
```
5줄이 모두 `OK`면 정상입니다 (양식, 오답노트 폴더, 초등부·중등부·고등부).

## 5. 사용법

Claude 데스크톱 앱 → Code 탭 → 폴더로 `01.수리원수학학원`을 열고:

> 오답노트 만들어줘. 작업지시서: C:\Users\...\Documents\S36BW-826102115530.pdf

진행 순서:
1. 지시서 손글씨를 읽어 **표로 보여주고 확인을 받습니다**
2. 교재 PDF를 찾고 **22개정/15개정 중 어느 판인지 묻습니다** (예: "모두 22개정, 없으면 15개정")
3. 쪽·번호를 찾습니다. 안 맞으면 앞뒤 쪽에서 찾고 **바뀐 내용을 알려줍니다**
4. 문제를 잘라(공통 지문·표 포함) 양식에 교재 / 단원(중단원) / 쪽수 / 번호와 함께 넣습니다
5. `<선생님>T\<학생 폴더>\<이름> <교재> <단원> <YYMMDD>.hwp` 로 저장하고 완성본을 확인해 보고합니다

팁
- 중간에 "○○까지만"이라고 하면 그 학생까지만 저장합니다.
- 같은 이름 파일이 있으면 덮어쓰지 않고 `(2)`를 붙여 저장합니다.
- 학생 폴더가 없으면 그 선생님 폴더의 기존 이름 규칙대로 만들기 전에 확인합니다.

## 6. 업데이트

공유 드라이브의 `오답노트 프로토콜` 폴더 내용이 바뀌면, 각 PC에서 `install.bat`을 다시 실행하면 됩니다.
경로 설정(`오답노트_config.json`)은 그대로 유지됩니다.

## 7. 삭제

```bat
rmdir /s "%USERPROFILE%\.claude\skills\odap-note"
del "%USERPROFILE%\.claude\오답노트_config.json"
```

## 8. 문제 해결

| 증상 | 해결 |
|---|---|
| `install.bat`이 바로 닫힘 / Python 없음 | Python 설치 시 "Add to PATH" 체크했는지 확인 → 새 창에서 다시 실행 |
| 한글 "접근 허용" 팝업이 뜸 | `install.bat` 다시 실행 (4단계 보안모듈 등록) |
| 작업 후 `Hwp.exe`가 작업관리자에 남음 | 창 없는 한글만 종료: PowerShell에서 `Get-Process Hwp \| ? {-not $_.MainWindowTitle} \| Stop-Process -Force` |
| 교재를 못 찾음 | 교재 PDF가 `100. 초등부` / `200. 중등부` / `300. 고등부` 아래에 있는지 확인, Claude에게 파일 위치를 알려주기 |
| 경로 오류 (`MISSING`) | 3번 항목대로 경로 다시 지정 |

## 9. 파일 구성

| 파일 | 역할 |
|---|---|
| `install.bat` / `install.ps1` | 설치 |
| `SKILL.md` | Claude가 따르는 작업 프로토콜 본문 |
| `scripts\setup_paths.py` | Google Drive 경로 자동 탐색 / 수동 지정 |
| `scripts\pdf_tool.py` | 지시서 렌더, 교재 검색(22/15개정 표시), 쪽 찾기, 번호 찾기, 썸네일, 크롭, 목차 |
| `scripts\crop_batch.py` | 여러 문제 일괄 크롭 + 확인용 몽타주 |
| `scripts\make_job.py` | HWP 생성용 job.json 만들기 |
| `scripts\build_note.py` | 양식 복제·칸 채우기·그림 삽입 → HWP 저장 + 미리보기 PDF |
| `scripts\common.py` | 공통 경로 설정 |
| `tools\FilePathCheckerModuleExample.dll` | 한컴 제공 한글 자동화 보안모듈 |
