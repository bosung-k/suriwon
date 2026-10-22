# 세화고 1학년 공통수학2 2학기 기말고사 대비 (2026)

범위: 집합 → 명제 → 함수 → 유리함수와 무리함수 · 141제 (v2)

## 구성
- `00_분석/세화고_기말대비_제작기록.md` — 자료 목록, 2026 중간·2025 기말 문항 대응표와 연계율, 학교 변형 규칙(R1~R7), 검색·제작 이력, 배치표, 검수 기록, v2 변경 기록
- `00_분석/부교재_판독노트.md` — 절대등급 공통수학2 문항별 판독 메모
- `_생성도구/content/s1~s5.py` — 단원별 원고(문항·정답·해설·출처·발상·변형 정보)
- `_생성도구/gen_seh.py` — HWPX 생성기 (`gen.py`, `gen_sc.py` 공용 모듈 사용, 양식 `yx/`)
- `_생성도구/hwpconv.py` — 한글 COM으로 HWPX → HWP/PDF 변환
- `_생성도구/crop_jd_figs.py` — 교사용 PDF에서 문제 그림을 잘라 파란 풀이 흔적 제거
- `_생성도구/verify_variants.py`, `verify_sources.py` — 정답 재계산 검산

## 다시 만들기
```
cd _생성도구
python gen_seh.py student out.hwpx     # 학생용(본문+빠른 정답+미주 해설)
python gen_seh.py teacher out_t.hwpx   # 강사용 대응표
python hwpconv.py out.hwpx out.hwp HWP
```
필요: Python 3, lxml, Pillow (검산은 sympy), 변환은 한글 설치 필요.

결과 HWP/PDF와 원본 교재·기출 파일은 저장소에 포함하지 않는다.
상태: 검수 완료 초안 (강사 승인 전).
