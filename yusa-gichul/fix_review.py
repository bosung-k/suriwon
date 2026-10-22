# -*- coding: utf-8 -*-
"""Apply reviewer fixes: edited print figures (C5 shading, C14 '8 cm' label) + text edits in C_probs.json."""
import json, os
from PIL import Image, ImageDraw, ImageFont
from hx import W
PR = os.path.join(W, 'pr')

# --- C5: shade region bounded by PA, PB and minor arc AB
src = os.path.join(PR, 'C_img', 'p05_image5.png')
im = Image.open(src).convert('RGB')
big = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
g = big.convert('L').point(lambda v: 0 if v < 200 else 255)
mask = Image.new('L', big.size, 0)
seed = (int(big.width * 0.24), int(big.height * 0.545))
filled = g.copy()
ImageDraw.floodfill(filled, seed, 128, thresh=10)
px_f, px_b = filled.load(), big.load()
cnt = 0
for y in range(big.height):
    for x in range(big.width):
        if px_f[x, y] == 128:
            r, gg, b = px_b[x, y]
            px_b[x, y] = (min(r, 190), min(gg, 190), min(b, 190)); cnt += 1
print('C5 shaded px', cnt, 'of', big.width * big.height, 'seed', seed)
big.save(os.path.join(PR, 'C_img', 'p05_fixed.png'))

# --- C14: label '8 cm' cut at left edge -> pad left and redraw
src = os.path.join(PR, 'C_img', 'p14_image14.png')
im = Image.open(src).convert('RGB')
pad = 40
new = Image.new('RGB', (im.width + pad, im.height), 'white'); new.paste(im, (pad, 0))
d = ImageDraw.Draw(new)
d.rectangle((0, 192, pad + 78, 236), fill='white')
font = ImageFont.truetype(r'C:\Windows\Fonts\times.ttf', 48)
d.text((pad - 30, 192), '8 cm', fill='black', font=font)
new.save(os.path.join(PR, 'C_img', 'p14_fixed.png'))

# --- text edits
P = json.load(open(os.path.join(PR, 'C_probs.json'), encoding='utf-8'))
def setpic(n, fn, scale):
    for it in P[n - 1]['items']:
        if it[0] == 'pic':
            w, h = Image.open(fn).size
            it[1] = fn; it[2] = int(w * scale); it[3] = int(h * scale)
setpic(5, os.path.join(PR, 'C_img', 'p05_fixed.png'), 60 / 3 * 1.0)
setpic(14, os.path.join(PR, 'C_img', 'p14_fixed.png'), 12058 / 426)
P[13]['items'][0][1] = ('원 $rm O$는 삼각형 $rm ABC$의 내접원이다. $overline {rm AB} =8 rm cm$, $overline {rm BC} =10 rm cm$, '
                        '$overline {rm CA} =7 rm cm$이고 $overline {rm DE}$가 원 $rm O$에 접할 때, 삼각형 $rm BDE$의 둘레의 길이를 구하여라.')
P[21]['items'][0][1] = ('삼각형 $rm ABC$의 내심 $rm I$와 외심 $rm O$가 있다. $angle rm A =60 DEG$일 때, 사각형 $rm IBCO$는 원에 내접함을 설명하여라. '
                        '(단, 두 점 $rm I ,~ O$는 서로 다른 점이다.)')
json.dump(P, open(os.path.join(PR, 'C_probs_fixed.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
