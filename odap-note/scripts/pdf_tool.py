# -*- coding: utf-8 -*-
"""교재 PDF/작업지시서 다루기.

  python pdf_tool.py books <초등|중등|고등> 키워드 [키워드...]   교재 PDF 검색 (22개정/15개정 표시)
  python pdf_tool.py order <지시서.pdf> <out_dir> [--rotate 90]   작업지시서를 PNG로 (Claude가 읽음)
  python pdf_tool.py findpage <교재.pdf> <인쇄쪽수>               인쇄 쪽수 → PDF 쪽(0부터) 후보
  python pdf_tool.py render <교재.pdf> <pdf쪽> <out.png>          좌표 눈금 포함 렌더 (크롭 영역 정하기용)
  python pdf_tool.py numbers <교재.pdf> <pdf쪽> [번호]            문제 번호로 보이는 글자 위치
  python pdf_tool.py crop <교재.pdf> <pdf쪽> x0 y0 x1 y1 <out.png>  영역(PDF pt 좌표) 잘라 PNG 저장
  python pdf_tool.py toc <교재.pdf>                               PDF 목차(단원명) 출력
  python pdf_tool.py findnum <교재.pdf> 번호 [번호...]             쪽 없이 번호만 있을 때 전체 검색
  python pdf_tool.py thumbs <교재.pdf> <시작> <끝> <out.png> [dpi]  스캔본: 여러 쪽 썸네일 한 장
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_config  # noqa: E402

import pymupdf  # noqa: E402
from PIL import Image, ImageDraw, ImageOps  # noqa: E402

LEVEL = {"초등": "elem", "중등": "middle", "고등": "high"}


def curriculum(path):
    s = path.replace(" ", "")
    if re.search(r"22개정|2022개정|22년개정", s):
        return "22개정"
    if re.search(r"15개정|2015개정|새교육과정|\(2019\)|2019", s):
        return "15개정"
    return "?"


def cmd_books(level, *kw):
    cfg = load_config()
    root = cfg["paths"][LEVEL[level]]
    kws = [k.lower().replace(" ", "") for k in kw]
    hits = []
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if not f.lower().endswith(".pdf"):
                continue
            full = os.path.join(dp, f)
            key = full[len(root):].lower().replace(" ", "")
            if all(k in key for k in kws):
                hits.append(full)
    for h in sorted(hits):
        tag = curriculum(h)
        ans = " [정답/해설]" if re.search(r"정답|해설|답지", os.path.basename(h)) else ""
        print(f"[{tag}]{ans} {h}")
    print(f"-- {len(hits)}개")


def cmd_order(pdf, out_dir, *rest):
    rot = 0
    if "--rotate" in rest:
        rot = int(rest[rest.index("--rotate") + 1])
    os.makedirs(out_dir, exist_ok=True)
    d = pymupdf.open(pdf)
    for i, p in enumerate(d):
        pix = p.get_pixmap(dpi=150)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if rot:
            im = im.rotate(-rot, expand=True)
        out = os.path.join(out_dir, f"order_p{i + 1}.png")
        im.save(out)
        print(out)


def page_label_numbers(page):
    """쪽 위/아래 여백에 있는 숫자(인쇄 쪽수 후보)."""
    h = page.rect.height
    res = []
    for b in page.get_text("words"):
        x0, y0, x1, y1, w = b[:5]
        if re.fullmatch(r"\d{1,3}", w) and (y1 < h * 0.08 or y0 > h * 0.92):
            res.append(int(w))
    return res


def cmd_findpage(pdf, printed):
    printed = int(printed)
    d = pymupdf.open(pdf)
    offsets = {}
    exact = []
    for i, p in enumerate(d):
        for n in page_label_numbers(p):
            offsets[i - n] = offsets.get(i - n, 0) + 1
            if n == printed:
                exact.append(i)
    print(f"PDF 총 {len(d)}쪽, 텍스트 {'있음' if any(p.get_text().strip() for p in d[:5]) else '없음(스캔본)'}")
    if exact:
        print("여백 쪽번호가 일치하는 PDF쪽(0부터):", exact)
    if offsets:
        best = sorted(offsets.items(), key=lambda x: -x[1])[:3]
        for off, cnt in best:
            print(f"  추정 오프셋 {off:+d} (근거 {cnt}쪽) → PDF쪽 {printed + off}")
    else:
        print("쪽번호 자동 인식 실패 → 몇 쪽을 render 해서 눈으로 쪽수를 확인하세요.")
    print("※ 펼침(2쪽이 한 장)인 PDF는 한 PDF쪽에 인쇄쪽 2개가 들어있음.")


def cmd_render(pdf, idx, out, dpi="110"):
    d = pymupdf.open(pdf)
    p = d[int(idx)]
    z = int(dpi) / 72
    pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z))
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    dr = ImageDraw.Draw(im)
    W, H = p.rect.width, p.rect.height
    for v in range(0, int(max(W, H)) + 1, 50):
        c = (255, 0, 0) if v % 100 == 0 else (255, 160, 160)
        if v <= W:
            dr.line([(v * z, 0), (v * z, 8)], fill=c, width=2)
            dr.line([(v * z, H * z - 8), (v * z, H * z)], fill=c, width=2)
            if v % 100 == 0:
                dr.text((v * z + 2, 10), str(v), fill=(255, 0, 0))
        if v <= H:
            dr.line([(0, v * z), (8, v * z)], fill=c, width=2)
            dr.line([(W * z - 8, v * z), (W * z, v * z)], fill=c, width=2)
            if v % 100 == 0:
                dr.text((10, v * z + 2), str(v), fill=(255, 0, 0))
    im.save(out)
    print(f"{out}  (page {W:.0f}x{H:.0f}pt, 빨간 눈금=PDF pt 좌표, 100pt마다 숫자)")


def cmd_numbers(pdf, idx, num=None):
    p = pymupdf.open(pdf)[int(idx)]
    W = p.rect.width
    found = 0
    for b in p.get_text("words"):
        x0, y0, x1, y1, w = b[:5]
        t = w.strip(".")
        if re.fullmatch(r"\d{1,4}(-\d{1,2})?", t) and (num is None or t == str(num)):
            col = "왼쪽단" if x0 < W / 2 else "오른쪽단"
            print(f"'{w}'  x0={x0:.0f} y0={y0:.0f} x1={x1:.0f} y1={y1:.0f}  ({col})")
            found += 1
    if not found:
        print("텍스트로 못 찾음(스캔본/그림 번호일 수 있음) → render 이미지를 보고 좌표를 정하세요.")


def cmd_crop(pdf, idx, x0, y0, x1, y1, out, dpi=250):
    p = pymupdf.open(pdf)[int(idx)]
    clip = pymupdf.Rect(float(x0), float(y0), float(x1), float(y1)) & p.rect
    z = dpi / 72
    pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # 바깥 흰 여백 정리 (테두리 5px 남김)
    bbox = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 25 else 0).getbbox()
    if bbox:
        pad = 12
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                      min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    # dpi 정보 = 원본 교재 크기 그대로 한글에 들어가게
    im.save(out, dpi=(dpi, dpi))
    print(f"{out}  {im.width}x{im.height}px  ≈ {im.width / dpi * 25.4:.0f}x{im.height / dpi * 25.4:.0f}mm")


def cmd_findnum(pdf, *nums):
    """쪽 없이 번호만 적힌 경우: PDF 전체에서 번호 위치 찾기 (왼쪽 여백 쪽 = 문제번호일 가능성 높음)."""
    d = pymupdf.open(pdf)
    if not any(p.get_text().strip() for p in d[:30]):
        print("텍스트 없는 스캔본 → 목차/쪽을 render 해서 눈으로 찾으세요.")
        return
    pats = {n: re.compile(rf"^0*{re.escape(n)}(?!\d)") for n in nums}
    for i, p in enumerate(d):
        W = p.rect.width
        for b in p.get_text("words"):
            t = next((n for n, rx in pats.items() if rx.match(b[4])), None)
            if t:
                labels = page_label_numbers(p)
                print(f"{t}: PDF쪽 {i} (인쇄쪽 {labels or '?'}) x0={b[0]:.0f} y0={b[1]:.0f}"
                      f" {'왼쪽단' if b[0] < W / 2 else '오른쪽단'}")


def cmd_thumbs(pdf, start, end, out, dpi="40"):
    """스캔본 쪽 찾기용: PDF쪽 start~end 썸네일을 한 장에 (각 칸 위에 PDF쪽 번호)."""
    d = pymupdf.open(pdf)
    ims = []
    for i in range(int(start), min(int(end) + 1, len(d))):
        pix = d[i].get_pixmap(dpi=int(dpi))
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ImageDraw.Draw(im).text((5, 5), f"PDF {i}", fill=(255, 0, 0))
        ims.append(im)
    cols = min(6, len(ims))
    w, h = max(i.width for i in ims), max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), "white")
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * w, (k // cols) * h))
    sheet.save(out)
    print(out)


def cmd_toc(pdf):
    d = pymupdf.open(pdf)
    toc = d.get_toc()
    if not toc:
        print("PDF 목차(북마크) 없음 → 목차 쪽이나 문제 쪽 머리말/옆 탭을 render 해서 단원명을 읽으세요.")
        return
    for lvl, title, page in toc:
        print(f"{'  ' * (lvl - 1)}{title}  (PDF쪽 {page - 1})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmds = {"books": cmd_books, "order": cmd_order, "findpage": cmd_findpage,
            "render": cmd_render, "numbers": cmd_numbers, "crop": cmd_crop, "toc": cmd_toc, "findnum": cmd_findnum, "thumbs": cmd_thumbs}
    cmds[sys.argv[1]](*sys.argv[2:])
