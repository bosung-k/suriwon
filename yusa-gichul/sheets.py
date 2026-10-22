"""sheets.py PDF prefix [pages...]  -> prefix_sN.png 2x2 sheets (all pages or listed 1-based pages)"""
import sys, pymupdf
from PIL import Image
d = pymupdf.open(sys.argv[1]); pre = sys.argv[2]
pages = [int(p) - 1 for p in sys.argv[3:]] or list(range(len(d)))
print(len(d))
for g in range(0, len(pages), 4):
    ims = []
    for i in pages[g:g + 4]:
        p = d[i].get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)); ims.append(Image.frombytes('RGB', (p.width, p.height), p.samples))
    w, h = ims[0].size; s = Image.new('RGB', (w * 2, h * 2), 'white')
    for j, im in enumerate(ims):
        s.paste(im, ((j % 2) * w, (j // 2) * h))
    s.save('%s_s%d.png' % (pre, g // 4 + 1))
