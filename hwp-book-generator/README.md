# hwp-book-generator

수리원 HWPX 양식에 문항 원고를 채워 교재(HWPX → HWP/PDF)를 만드는 스크립트.

| 파일 | 역할 |
|---|---|
| `gen.py` | 양식(HWPX) 조작 공통 함수: 수식(`$...$` → 한글 수식), 보기·조건 상자, 선택지 표, 미주(정답·해설) |
| `gen_sc.py` | 단원 → 학습 묶음 → 문항 구조의 교재 생성기. 그림 삽입, 쪽당 2문항, 빠른 정답표 |
| `figs.py` | matplotlib으로 대응 그림·벤다이어그램·그래프 PNG 생성 |
| `hwpconv.py` | 한글 COM으로 HWPX → HWP → PDF 변환 (Windows + 한컴오피스 필요) |

## 사용법

```
python figs.py
python gen_sc.py out/book.hwpx
python hwpconv.py out/book.hwpx out/book.hwp HWP
python hwpconv.py out/book.hwp out/book.pdf PDF
```

## 저장소에 없는 것

- `yx/` : 수리원 교재 양식(HWPX를 푼 폴더) — 기존 교재 내용이 들어 있어 올리지 않음
- `content/s1.py ~ s4.py` : 문항 원고(`S = {'no', 'title', 'plan', 'bundles': [(묶음 제목, [문항 dict ...])]}`)
- `figs/`, `out/` : 생성 결과물

문항 dict 키: `id, src, q, cond, after_cond, bogi, choices, img, imgw, ans, quick, sol`.
학생용 출처 표시는 `src`가 ‘부교재’ 또는 ‘2025 기말’로 시작하고 ‘변형’이 없을 때만 나온다(`gen_sc.show_src`).
