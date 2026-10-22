import os, json, re
import pymupdf
from hx import W
KC = os.path.join(W, 'kc')
info = json.load(open(os.path.join(KC, 'info.json'), encoding='utf-8'))
EXCL = re.compile(r'\\(1학년|2학년)\\')
keep = []
for e in info:
    if EXCL.search(e['rel']) or not e['rel'].lower().endswith('.pdf'):
        continue
    d = pymupdf.open(os.path.join(KC, e['tag'] + '.pdf'))
    os.makedirs(os.path.join(KC, 'pg'), exist_ok=True)
    for i, p in enumerate(d):
        fn = os.path.join(KC, 'pg', '%s_p%02d.png' % (e['tag'], i + 1))
        if not os.path.exists(fn):
            p.get_pixmap(matrix=pymupdf.Matrix(2.2, 2.2)).save(fn)
    e['scanned'] = (e.get('hangul') or 0) < 200
    keep.append(e)
json.dump(keep, open(os.path.join(KC, 'keep.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(keep), sum(1 for e in keep if e['scanned']))
