# 교재 생성 도구 (HWPX/HWP)

서문여고 공통수학2 기말 고난도 교재(48제)를 만든 도구입니다.

## 구성

| 경로 | 내용 |
|---|---|
| `gen.py` | 문항 데이터(`content_*/s?.py`)로 HWPX 교재를 만드는 생성기 |
| `yx/` | 생성기가 쓰는 HWPX 양식 (압축 해제된 상태) |
| `content_hi/` | 고난도 교재 문항 데이터 (`meta.py`: 표지·구성, `s1`: 직렬·병렬 융합 20, `s2`: 비보편 필수 유형 20, `s3`: 탐구활동 변형 8) |
| `hwpconv.py` | 한글 COM으로 HWPX → HWP / PDF 변환 |
| `hwp2txt.py` | HWP 5.0 파일에서 수식 포함 텍스트 추출 |
| `verify/` | 정답 검증 스크립트 (brute force · sympy · numpy) |

## 사용법

```
pip install lxml sympy numpy olefile pywin32
python gen.py lesson out/hi.hwpx content_hi
python hwpconv.py out/hi.hwpx out/hi.hwp HWP
python hwpconv.py out/hi.hwp out/hi.pdf PDF
```

`hwpconv.py`는 한컴오피스 한글이 설치된 Windows에서만 동작합니다.

## 문항 데이터 형식

각 문항은 dict이며 키는 `tag, q, cond, after_cond, bogi, choices, ans, sol, full`입니다.
수식은 `$...$` 안에 한글 수식 스크립트로 씁니다. `full: True`이면 한 쪽에 한 문항만 배치합니다.
