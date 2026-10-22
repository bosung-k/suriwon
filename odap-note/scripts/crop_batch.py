# -*- coding: utf-8 -*-
"""여러 문제를 한 번에 크롭 + 확인용 몽타주.

  python crop_batch.py <교재.pdf> <spec.txt> <out_dir> <prefix>

spec.txt 한 줄 = 번호 PDF쪽 x0 y0 x1 y1   (PDF pt 좌표, render 눈금 기준)
  0956 156 322 80 612 200
  0957 156 322 200 612 300
같은 번호를 여러 줄 쓰면(문제가 단/쪽을 넘어갈 때) 위에서 아래로 이어 붙인다.

결과: <out_dir>/<prefix>_<번호>.png, 확인용 <out_dir>/<prefix>_montage.png
"""
import os
import subprocess
import sys
from collections import OrderedDict

from PIL import Image, ImageDraw

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_tool.py")
DPI = 250


def main():
    pdf, spec, out, prefix = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    groups = OrderedDict()
    for line in open(spec, encoding="utf-8-sig"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        name, pg, *box = line.split()
        groups.setdefault(name, []).append((pg, box))

    results = []
    for name, parts in groups.items():
        key = name.replace("-", "_")
        pieces = []
        for k, (pg, box) in enumerate(parts):
            fp = os.path.join(out, f"{prefix}_{key}_part{k}.png")
            subprocess.run([sys.executable, TOOL, "crop", pdf, pg, *box, fp],
                           check=True, capture_output=True)
            pieces.append(Image.open(fp))
        if len(pieces) == 1:
            im = pieces[0]
        else:
            w = max(p.width for p in pieces)
            im = Image.new("RGB", (w, sum(p.height for p in pieces)), "white")
            y = 0
            for p in pieces:
                im.paste(p, (0, y))
                y += p.height
        final = os.path.join(out, f"{prefix}_{key}.png")
        im.save(final, dpi=(DPI, DPI))
        results.append((name, final, im))

    W = max(i.width for _, _, i in results) + 20
    H = sum(i.height + 40 for _, _, i in results)
    m = Image.new("RGB", (W, H), (230, 230, 230))
    d = ImageDraw.Draw(m)
    y = 0
    for name, _, i in results:
        d.text((5, y + 5), name, fill=(255, 0, 0))
        m.paste(i, (10, y + 30))
        y += i.height + 40
    m.thumbnail((1400, 6000))
    mp = os.path.join(out, f"{prefix}_montage.png")
    m.save(mp)
    for name, final, _ in results:
        print(name, final)
    print("MONTAGE:", mp, "← Read로 열어 잘림/군더더기 확인")


if __name__ == "__main__":
    main()
