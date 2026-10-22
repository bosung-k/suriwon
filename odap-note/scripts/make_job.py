# -*- coding: utf-8 -*-
"""build_note.py 용 job.json 만들기.

  python make_job.py <out.json> <선생님> <학생폴더> <파일이름.hwp> <교재> <단원> <이미지prefix> 쪽:번호[:단원] ...

예)
  python make_job.py job.json 현승T "신재희(잠원초6)" "신재희 쎈 중2-1 11. 일차함수와 일차방정식의 관계 261021.hwp" ^
      "쎈 중2-1" "11. 일차함수와 일차방정식의 관계" C:\\tmp\\ss 193:1213 194:1219
이미지 경로 = <이미지prefix>_<번호>.png  (crop_batch.py 결과와 같은 규칙, '-'는 '_'로)
단원이 문제마다 다르면 쪽:번호:단원 으로 덮어쓴다.
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

out, teacher, folder, fname, book, unit, prefix, *items = sys.argv[1:]
its = []
for it in items:
    parts = it.split(":", 2)
    page, num = parts[0], parts[1]
    u = parts[2] if len(parts) > 2 else unit
    img = f"{prefix}_{num.replace('-', '_')}.png"
    if not os.path.isfile(img):
        sys.exit(f"ERROR: 이미지 없음 {img}")
    its.append({"book": book, "unit": u, "page": page, "num": num, "image": img})
with open(out, "w", encoding="utf-8") as f:
    json.dump({"teacher": teacher, "student_folder": folder, "file_name": fname, "items": its},
              f, ensure_ascii=False, indent=1)
print(out, f"{len(its)}문제")
