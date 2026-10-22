# -*- coding: utf-8 -*-
"""Extract print problems (text markup, answer, extra lines, pictures) from print HWPX.
pr_extract.py T|C -> work/pr/<k>_probs.json, images work/pr/<k>_img/*.png"""
import os, re, sys, json, io, html
from PIL import Image
from hx import *
from scan import top_paras, plain

k = sys.argv[1]
files, order = read_hwpx(os.path.join(W, 'pr', k + '.hwpx'))
x = files['Contents/section0.xml'].decode('utf-8')
hpf = files['Contents/content.hpf'].decode('utf-8')
href = dict(re.findall(r'<opf:item id="(\w+)" href="([^"]+)"', hpf))
pr = top_paras(x)
ps = [x[a:b] for a, b in pr]
OUT = os.path.join(W, 'pr', k + '_img'); os.makedirs(OUT, exist_ok=True)


def clean(t):
    t = t.replace('\r', '').replace('\n', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    t = html.unescape(t)
    return t.strip()


starts = [i for i, s in enumerate(ps) if '<hp:endNote' in s and i > 0]
probs = []
for n, i in enumerate(starts):
    j = starts[n + 1] if n + 1 < len(starts) else len(ps)
    blk = ps[i:j]
    s0 = blk[0]
    ans = ''
    m = re.search(r'<hp:endNote.*?</hp:endNote>', s0, re.S)
    if m:
        e = m.group(0)
        e = re.sub(r'<hp:autoNum.*?</hp:autoNum>', '', e, flags=re.S)
        e = re.sub(r'<hp:shapeComment>.*?</hp:shapeComment>', '', e, flags=re.S)
        ans = clean(re.sub(r'<[^>]+>', '', re.sub(r'<hp:script>(.*?)</hp:script>', r'$\1$', e, flags=re.S)))
    items = []
    for t, s in enumerate(blk):
        body = re.sub(r'<hp:endNote.*?</hp:endNote>', '', s, flags=re.S)
        # pictures (skip pictures nested inside tables)
        nt = re.sub(r'<hp:tbl .*?</hp:tbl>', '', body, flags=re.S)
        for pm in re.finditer(r'<hp:pic .*?</hp:pic>', nt, re.S):
            pic = pm.group(0)
            bid = re.search(r'binaryItemIDRef="(\w+)"', pic).group(1)
            cw, ch = map(int, re.search(r'<hp:curSz width="(\d+)" height="(\d+)"', pic).groups())
            data = files[href[bid]]
            im = Image.open(io.BytesIO(data)).convert('RGB')
            fn = os.path.join(OUT, 'p%02d_%s.png' % (n + 1, bid))
            im.save(fn)
            items.append(('pic', fn, cw, ch))
        if '<hp:tbl ' in body:
            items.append(('tbl', plain(re.search(r'<hp:tbl .*?</hp:tbl>', body, re.S).group(0))[:80]))
            body = re.sub(r'<hp:tbl .*?</hp:tbl>', '', body, flags=re.S)
        body = re.sub(r'<hp:pic .*?</hp:pic>', '', body, flags=re.S)
        txt = clean(plain(body))
        if txt:
            items.append(('txt', txt))
    probs.append(dict(n=n + 1, ans=ans, items=items))
json.dump(probs, open(os.path.join(W, 'pr', k + '_probs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for p in probs:
    print(p['n'], 'ANS:', p['ans'][:60])
    for it in p['items']:
        print('   ', it[0], (it[1] if it[0] != 'pic' else os.path.basename(it[1]) + ' %dx%d' % (it[2], it[3]))[:150])
