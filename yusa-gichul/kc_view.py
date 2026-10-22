"""kc_view.py KEY..  -> work/kc/fig/_view.png  (problem regions, 2 per row, scale 0.62) for typing"""
import sys, os
from PIL import Image, ImageDraw
import kcx
sc = float(os.environ.get('SC', '0.62'))
ims = []
for k in sys.argv[1:]:
    segs = kcx.region(k)
    reg = [kcx.img(s[0]).crop(tuple(int(v) for v in s[1:])) for s in segs]
    w = max(r.size[0] for r in reg); h = sum(r.size[1] for r in reg)
    c = Image.new('L', (w, h), 255); y = 0
    for r in reg:
        c.paste(r, (0, y)); y += r.size[1]
    lim = int(os.environ.get('LIM', '1500'))
    c = c.crop((0, 0, w, min(h, lim)))
    ims.append((k, c.resize((int(w * sc), int(c.size[1] * sc)))))
cols = 2
rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
Wt = max(sum(i.size[0] for _, i in r) + 10 * cols for r in rows)
Ht = sum(max(i.size[1] for _, i in r) + 6 for r in rows)
sh = Image.new('RGB', (Wt, Ht), 'white'); d = ImageDraw.Draw(sh); y = 0
for r in rows:
    x = 0
    for k, i in r:
        sh.paste(i, (x, y)); d.rectangle((x, y, x + i.size[0], y + i.size[1]), outline='red'); d.text((x + 3, y + 1), k, fill='red')
        x += i.size[0] + 10
    y += max(i.size[1] for _, i in r) + 6
sh.save(os.path.join(kcx.FIG, '_view.png')); print(sh.size)
