"""kc_sheet.py T|C start end -> work/kc/fig/_sheet_<k>.png : figures actually used, per spec item"""
import sys, importlib
from PIL import Image, ImageDraw
import kcx
kind, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
S = importlib.import_module('kc_spec_t' if kind == 'T' else 'kc_spec_c')
spec = S.T if kind == 'T' else S.C
tiles = []
for n in sorted(spec):
    if not (a <= n <= b):
        continue
    for it in spec[n]:
        fs, _ = kcx.save(it['k'])
        import kc_build as KB
        sel = KB.SEL.get(it['k'], it.get('figs'))
        if sel is None and it['k'] not in KB.MULTI:
            sel = [1] if fs else []
        if sel is not None:
            fs = [fs[i - 1] for i in sel]
        for j, f in enumerate(fs):
            t = f.copy(); t.thumbnail((380, 330)); tiles.append(('%d %s_%d' % (n, it['k'], j + 1), t))
        if not fs:
            tiles.append(('%d %s NONE' % (n, it['k']), Image.new('L', (120, 30), 200)))
cols = 4
rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
H = sum(max(t.size[1] for _, t in r) + 18 for r in rows)
s = Image.new('RGB', (cols * 390, H), 'white'); d = ImageDraw.Draw(s); y = 0
for r in rows:
    x = 0
    for k, t in r:
        s.paste(t, (x, y + 16)); d.text((x, y + 2), k, fill='red'); x += 390
    y += max(t.size[1] for _, t in r) + 18
s.save(kcx.os.path.join(kcx.FIG, '_sheet_%s.png' % kind)); print(s.size)
