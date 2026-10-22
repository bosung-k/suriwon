"""부교재(교사용 PDF) 문제 그림을 잘라 파란 풀이 흔적을 지운다.  python crop_jd_figs.py <교사용.pdf>"""
import sys, os, colorsys, pymupdf
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'figs')
d = pymupdf.open(sys.argv[1])
# id: (page, region rect(pt), y limit for figure, remove_blue)
T = {'JD-04A22': (37, (313, 355, 570, 597), 455, False),
     'JD-05A08': (49, (313, 561, 570, 800), 800, True),
     'JD-06A23': (65, (313, 332, 570, 561), 561, True),
     'JD-06A34': (67, (45, 256, 300, 441), 441, True),
     'JD-06A35': (67, (45, 441, 300, 642), 642, True),
     'JD-06B12': (69, (313, 512, 570, 800), 640, True),
     'JD-06B15': (70, (45, 466, 300, 800), 712, True),
     'JD-06B16': (70, (313, 112, 570, 373), 215, True),
     'JD-07A13': (77, (313, 112, 570, 301), 301, True),
     'JD-07A19': (78, (45, 422, 300, 637), 637, True),
     'JD-08A03': (84, (45, 415, 300, 566), 566, True),
     'JD-08A04': (84, (45, 566, 300, 800), 800, True),
     'JD-08B02': (86, (45, 282, 300, 586), 486, True)}
def isblue(c):
    return c is not None and c[2] > 0.5 and c[2] - c[0] > 0.25
def strip_blue(im):
    a = np.asarray(im.convert('RGB')).astype(float) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); sat = (mx - mn) / np.maximum(mx, 1e-6)
    blue = (b >= g - 0.02) & (b - r > 0.08) & (sat > 0.12)
    a[blue] = 1.0
    return Image.fromarray((a * 255).astype('uint8'))
# 확인 후 정한 잘라낼 영역(pt, 교사용 PDF 좌표) — 문제 그림만, 문제 글·풀이 제외
CLIP = {'JD-04A22': (474, 380, 562, 462), 'JD-05A08': (467, 586, 565, 652), 'JD-06A23': (316, 403, 565, 500),
        'JD-06A34': (201, 278, 297, 366), 'JD-06A35': (193, 463, 293, 556), 'JD-06B12': (483, 534, 565, 622),
        'JD-06B15a': (200, 488, 296, 578), 'JD-06B15b': (47, 583, 298, 712), 'JD-06B16': (325, 155, 512, 230),
        'JD-07A13': (458, 133, 566, 230), 'JD-07A19': (197, 443, 298, 541), 'JD-08A03': (198, 436, 298, 515),
        'JD-08A04': (198, 587, 298, 668), 'JD-08B02a': (200, 302, 296, 376), 'JD-08B02b': (48, 376, 296, 495)}
PAGE = {k: v[0] for k, v in T.items()}
os.makedirs(OUT, exist_ok=True)
for k, box in CLIP.items():
    base = k[:8]
    p = PAGE[base]; rb = T[base][3]
    pix = d[p - 1].get_pixmap(dpi=300, clip=pymupdf.Rect(box))
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    if rb: im = strip_blue(im)
    name = 'jd_' + k[3:].lower()
    im.save(os.path.join(OUT, name + '.png'))
    print(k, name, im.size)

