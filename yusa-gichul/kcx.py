"""Problem regions + automatic figure extraction from exam page images (2.2x).
kcx.py KEY [KEY..]  -> work/kc/fig/KEY_1.png ... and work/kc/fig/_rev.png (review sheet: region | figures)
Manual override: MANUAL[key] = [(page, x0, y0, x1, y1), ...]  (page png pixel coords)
"""
import os, sys, json, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from hx import W
KC = os.path.join(W, 'kc'); FIG = os.path.join(KC, 'fig'); os.makedirs(FIG, exist_ok=True)
probs = json.load(open(os.path.join(KC, 'probs.json'), encoding='utf-8'))
L = json.load(open(os.path.join(KC, 'lines.json'), encoding='utf-8'))
idx = {}
for i, p in enumerate(probs):
    k = '%s-%s' % (p['tag'], p['num'])
    if k not in idx or len(p['text']) > len(probs[idx[k]]['text']):
        idx[k] = i
    idx['%s@%s' % (k, p['page'][-3:])] = i
MANUAL = {   # 반포중 (hwp page renders 1306x1847)
    'K02-2': [('K02_p01', 105, 1225, 460, 1530)],
    'K02-S1': [('K02_p06', 680, 505, 1045, 785)],
    'K03-1': [('K03_p01', 170, 470, 545, 760)],
    'K03-S1': [('K03_p05', 770, 1235, 1115, 1460)],
    'K01-1': [('K01_p01', 85, 575, 450, 900)],
    'K02-11': [('K02_p03', 700, 1080, 1045, 1420)],
    'K03-14': [('K03_p04', 805, 200, 1095, 505)],
    'K01-9': [('K01_p03', 85, 285, 430, 635)],
    'K30-1': [('K30_p01', 80, 440, 640, 1030)],
}
TH = {'K12-6': 235, 'K33-9': 235, 'K51-9': 215}
DIL = {'K40-15': 30, 'K30-1': 40, 'K15-9': 30, 'K32-1': 40}
KEEPTXT = set()   # keys whose figure contains Korean labels (only mask choice lines)
REGION = {}   # manual region override: key -> [(page, x0,y0,x1,y1)]
_img = {}


def img(page):
    if page not in _img:
        _img[page] = Image.open(os.path.join(KC, 'pg', page + '.png')).convert('L')
    return _img[page]


def region(key):
    if key in REGION:
        return REGION[key]
    i = idx[key]; p = probs[i]
    nxt = probs[i + 1] if i + 1 < len(probs) and probs[i + 1]['tag'] == p['tag'] else None
    pages = sorted(k for k in L if k.startswith(p['tag'] + '_'))
    endk = (nxt['page'], nxt['col'], nxt['y0'] - 8) if nxt else (p['end'][0], p['end'][1], p['end'][2] + 30)
    segs = []
    pg, col, ya = p['page'], p['col'], p['y0'] - 12
    while True:
        Wp, Hp = img(pg).size
        x0, x1 = (0, Wp // 2) if col == 0 else (Wp // 2, Wp)
        if (pg, col) == (endk[0], endk[1]):
            segs.append((pg, x0 + 6, max(0, ya), x1 - 6, min(Hp, endk[2]))); break
        segs.append((pg, x0 + 6, max(0, ya), x1 - 6, Hp * 0.93))
        if len(segs) > 2:
            break
        if col == 0:
            pg, col, ya = pg, 1, Hp * 0.04
        else:
            j = pages.index(pg) + 1
            if j >= len(pages):
                break
            pg, col, ya = pages[j], 0, Hp * 0.04
    return [s for s in segs if s[4] - s[2] > 20]


def text_mask(page, box, key_keep_text=False):
    """mask of long text lines (problem sentences, choices) inside box."""
    x0, y0, x1, y1 = box
    m = np.zeros((int(y1 - y0), int(x1 - x0)), bool)
    for l in L.get(page, []):
        t = l['t'].strip()
        long_ = len(t) > 9 or re.match(r'^\s*[①②③④⑤⑴⑵(㉦㉨㉭㉩@]', t) or re.search(r'[①②③④⑤]', t) or re.search(r'[가-힣]{2,}', t)
        if key_keep_text and re.search(r'[①②③④⑤]', t) is None:
            continue
        if not long_:
            continue
        a, b, c, d = l['x0'] - x0 - 2, l['y0'] - y0 - 2, l['x1'] - x0 + 2, l['y1'] - y0 + 2
        a, b = max(0, int(a)), max(0, int(b)); c, d = min(m.shape[1], int(c)), min(m.shape[0], int(d))
        if c > a and d > b:
            m[b:d, a:c] = True
    return m


def figures(key, minarea=9000):
    out = []
    if key in MANUAL:
        for pg, a, b, c, d in MANUAL[key]:
            im = img(pg).crop((a, b, c, d))
            ar = np.array(im) < 170
            ys, xs = np.where(ar)
            if len(xs):
                im = im.crop((max(0, xs.min() - 6), max(0, ys.min() - 6), min(im.size[0], xs.max() + 7), min(im.size[1], ys.max() + 7)))
            out.append(im)
        return out
    for pg, x0, y0, x1, y1 in region(key):
        im = img(pg).crop((int(x0), int(y0), int(x1), int(y1)))
        a = np.array(im) < TH.get(key, 160)
        a &= ~text_mask(pg, (int(x0), int(y0), int(x1), int(y1)), key in KEEPTXT)
        # drop long horizontal rules (column/footer lines)
        rows = a.sum(1); a[rows > a.shape[1] * 0.8, :] = False
        cols = a.sum(0); a[:, cols > a.shape[0] * 0.8] = False
        d = ndimage.binary_dilation(a, iterations=DIL.get(key, 9))
        lab, n = ndimage.label(d)
        objs = ndimage.find_objects(lab)
        cands = []
        for k, sl in enumerate(objs):
            h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
            ink = a[sl][lab[sl] == k + 1].sum()
            if w * h >= minarea and h > 50 and w > 60 and ink > 400:
                bx = (x0 + sl[1].start, y0 + sl[0].start, x0 + sl[1].stop, y0 + sl[0].stop)
                kor = sum(1 for l in L.get(pg, []) if re.search(r'[가-힣]{2,}', l['t'])
                          and l['x0'] >= bx[0] - 4 and l['x1'] <= bx[2] + 4 and l['y0'] >= bx[1] - 4 and l['y1'] <= bx[3] + 4)
                inside = ' '.join(l['t'] for l in L.get(pg, []) if l['x0'] >= bx[0] - 4 and l['x1'] <= bx[2] + 4 and l['y0'] >= bx[1] - 4 and l['y1'] <= bx[3] + 4)
                if re.search(r'과목|출제|실시|코드|이름|번호|계속|저작권|학년도|고사', inside):
                    continue
                if kor >= 3 and not re.search(r'sin|cos|tan|각도|사인', inside):
                    continue
                cands.append((sl[0].start, sl[1].start, sl[0].stop, sl[1].stop))
        for (r0, c0, r1, c1) in sorted(cands):
            out.append(im.crop((max(0, c0 - 2), max(0, r0 - 2), min(im.size[0], c1 + 2), min(im.size[1], r1 + 2))))
    return out


TRIM = {}   # (left, top, right, bottom) px to cut


def save(key):
    fs = figures(key)
    for j, f in enumerate(fs):
        if (key, j + 1) in TRIM:
            l, t, r, b = TRIM[(key, j + 1)]
            fs[j] = f.crop((l, t, f.size[0] - r, f.size[1] - b))
    names = []
    for j, f in enumerate(fs):
        fn = os.path.join(FIG, '%s_%d.png' % (key.replace('@', '_'), j + 1))
        f.save(fn); names.append(fn)
    return fs, names


if __name__ == '__main__':
    keys = sys.argv[1:]
    rows = []
    for k in keys:
        fs, _ = save(k)
        segs = region(k)
        reg = [img(s[0]).crop(tuple(int(v) for v in s[1:])) for s in segs]
        rows.append((k, reg, fs))
    sc = 0.45
    Wt = 1100; parts = []
    for k, reg, fs in rows:
        rh = sum(r.size[1] for r in reg); rw = max(r.size[0] for r in reg)
        fh = sum(f.size[1] + 6 for f in fs) if fs else 20; fw = max([f.size[0] for f in fs] or [100])
        H = int(max(rh, fh) * sc) + 16
        c = Image.new('RGB', (int((rw + fw) * sc) + 30, H), 'white'); dr = ImageDraw.Draw(c)
        y = 14
        for r in reg:
            c.paste(r.resize((int(r.size[0] * sc), int(r.size[1] * sc))), (0, y)); y += int(r.size[1] * sc)
        y = 14; x = int(rw * sc) + 20
        for f in fs:
            t = f.resize((max(1, int(f.size[0] * sc)), max(1, int(f.size[1] * sc))))
            c.paste(t, (x, y)); dr.rectangle((x, y, x + t.size[0], y + t.size[1]), outline='blue'); y += t.size[1] + 4
        dr.text((2, 0), '%s  figs=%d' % (k, len(fs)), fill='red')
        parts.append(c)
    Wt = max(p.size[0] for p in parts); Ht = sum(p.size[1] for p in parts)
    sh = Image.new('RGB', (Wt, Ht), 'white'); y = 0
    for p in parts:
        sh.paste(p, (0, y)); ImageDraw.Draw(sh).line((0, y, Wt, y), fill='red'); y += p.size[1]
    sh.save(os.path.join(FIG, '_rev.png')); print(sh.size)
