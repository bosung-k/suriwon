# 학교프린트 유사 기출 자료 제작 스크립트

학교프린트(HWP)의 각 문항과 비슷한 기출문제를 학교 배포 기출(PDF/HWP)에서 찾아,
왼쪽 단에 프린트 문항, 오른쪽 단에 유사 기출을 배치한 HWP 문서를 만드는 작업 스크립트입니다.
(2026 세화여중3 2학기 중간고사 삼각비 / 원과 직선·원주각 자료 제작에 사용)

## 필요 환경
- Windows + 한컴오피스 한글 (COM 자동화: `HWPFrame.HwpObject`)
- Python 3, `pywin32`, `pymupdf`, `Pillow`, `numpy`, `scipy`
- 스캔본 PDF 글자 인식: Windows 기본 OCR (`ocr.ps1`, 한국어 OCR 언어팩)

중간 산출물은 모두 `work/` 폴더(저장소에 포함하지 않음)에 만들어집니다.

## 작업 순서
| 단계 | 스크립트 | 하는 일 |
|---|---|---|
| 1 | `kc_scan.py` | 기출 폴더에서 3학년 2학기 시험지를 찾아 `work/kc/K00…`로 복사 |
| 2 | `kc_render.py` | PDF 쪽을 이미지로 렌더링, 스캔본 여부 판별 |
| 2-1 | `pgimg.py` | 배포용(PDF 저장 불가) HWP 쪽을 이미지로 렌더링 |
| 3 | `ocr.ps1` | 스캔본 쪽 이미지 OCR → `work/kc/ocr/*.json` |
| 4 | `kc_dump.py` | 쪽별 글자 줄과 위치 정리 (`lines.json`) |
| 5 | `kc_seg.py` | 문항 단위로 분할 (`probs.json`, `probs.txt`) |
| 6 | `kc_crop.py`, `kc_view.py` | 후보 문항 이미지 확인 (눈으로 유사 여부 검토) |
| 7 | `kcx.py`, `kc_sheet.py` | 문항 영역에서 그림만 자동 크롭, 검수용 시트 |
| 8 | `pr_extract.py` | 학교프린트 HWP에서 문항 글·그림·정답 추출 |
| 9 | `kc_build.py` | 유사 기출 문서 생성 (기본 양식) |
| 10 | `kc_build2.py` | '03-1. 세화여중 양식'으로 생성 — `python kc_build2.py T|C <전체쪽수>` |
| - | `fix_review.py`, `u_fix.py` | 검토 의견 반영(그림 음영·라벨 수정, 기존 파일의 특정 문항만 수정) |
| - | `conv.py`, `hx.py`, `scan.py`, `sheets.py`, `numap.py`, `insp.py` | HWP↔HWPX/PDF 변환, HWPX 입출력, 검수 도구 |

## 저장소에 넣지 않은 파일
- `kc_spec_t.py`, `kc_spec_c.py`(타이핑한 기출 문항 본문), `kc_ans.py`(정답):
  학교 시험지 원문이 그대로 들어 있어 공개 저장소에 올리지 않았습니다.
  `kc_build.py`를 실행하려면 이 세 파일이 같은 폴더에 있어야 합니다.
