"""kc_crop.py KEY [KEY ...]  (KEY = K31-8 / K31-S1) -> work/kc/crop/KEY.png ; also sheet of them -> work/kc/crop/_sheet.png"""
import os, sys, json
from PIL import Image
from hx import W
KC = os.path.join(W, 'kc'); OUT = os.path.join(KC, 'crop'); os.makedirs(OUT, exist_ok=True)
probs = json.load(open(os.path.join(KC, 'probs.json'), encoding='utf-8'))
L = json.load(open(os.path.join(KC, 'lines.json'), encoding='utf-8'))
idx = {}
for i, p in enumerate(probs):
    k = '%s-%s' % (p['tag'], p['num'])
    if k not in idx or len(p['text']) > len(probs[idx[k]]['text']):
        idx[k] = i
    idx['%s@%s' % (k, p['page'][-3:])] = i


def colbox(page, col, ya, yb):
    im = Image.open(os.path.join(KC, 'pg', page + '.png'))
    Wp, Hp = im.size
    x0, x1 = (0, Wp // 2) if col == 0 else (Wp // 2, Wp)
    return im.crop((x0 + 8, max(0, int(ya)), x1 - 8, min(Hp, int(yb))))


def crop(key):
    i = idx[key]; p = probs[i]
    nxt = probs[i + 1] if i + 1 < len(probs) and probs[i + 1]['tag'] == p['tag'] else None
    # segments: from (page,col,y0) to start of next problem
    pages = sorted(k for k in L if k.startswith(p['tag'] + '_'))
    segs = []
    pos = (p['page'], p['col'], p['y0'] - 12)
    endk = (nxt['page'], nxt['col'], nxt['y0'] - 8) if nxt else (p['end'][0], p['end'][1], p['end'][2] + 30)
    cur = pos
    while True:
        pg, col, ya = cur
        Hp = Image.open(os.path.join(KC, 'pg', pg + '.png')).size[1]
        if (pg, col) == (endk[0], endk[1]):
            segs.append(colbox(pg, col, ya, endk[2])); break
        # until end of this column: use last line y1 in column
        ys = [l['y1'] for l in L[pg] if l['col'] == col]
        yb = Hp * 0.93
        segs.append(colbox(pg, col, ya, yb))
        if col == 0:
            cur = (pg, 1, Hp * 0.04)
        else:
            j = pages.index(pg) + 1
            if j >= len(pages) or len(segs) > 3:
                break
            cur = (pages[j], 0, Hp * 0.04)
    segs = [s for s in segs if s.size[1] > 20]
    Wm = max(s.size[0] for s in segs); Ht = sum(s.size[1] for s in segs)
    out = Image.new('RGB', (Wm, Ht), 'white'); y = 0
    for s in segs:
        out.paste(s, (0, y)); y += s.size[1]
    out.save(os.path.join(OUT, key + '.png'))
    return out


if __name__ == '__main__':
    ims = []
    for k in sys.argv[1:]:
        try:
            ims.append((k, crop(k)))
        except Exception as e:
            print('ERR', k, e)
    if ims:
        sc = 0.5
        cols = 3
        rows = [ims[i:i + cols] for i in range(0, len(ims), cols)]
        Wt = int(max(sum(im.size[0] for _, im in r) for r in rows) * sc) + 20
        Ht = int(sum(max(im.size[1] for _, im in r) for r in rows) * sc) + 20
        sh = Image.new('RGB', (Wt, Ht), 'white'); y = 0
        from PIL import ImageDraw
        d = ImageDraw.Draw(sh)
        for r in rows:
            x = 0
            for k, im in r:
                t = im.resize((int(im.size[0] * sc), int(im.size[1] * sc)))
                sh.paste(t, (x, y)); d.rectangle((x, y, x + t.size[0], y + t.size[1]), outline='red')
                d.text((x + 4, y + 2), k, fill='red')
                x += t.size[0] + 4
            y += int(max(im.size[1] for _, im in r) * sc) + 4
        sh.save(os.path.join(OUT, '_sheet.png'))
        print(sh.size)
