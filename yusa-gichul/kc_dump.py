"""Make per-exam text dumps (page/column ordered) with line bboxes in page-image pixels (2.2x)."""
import os, json, re
import pymupdf
from hx import W
KC = os.path.join(W, 'kc'); Z = 2.2
keep = json.load(open(os.path.join(KC, 'keep.json'), encoding='utf-8'))
allines = {}
out = []
for e in keep:
    d = pymupdf.open(os.path.join(KC, e['tag'] + '.pdf'))
    out.append('\n######## %s  %s' % (e['tag'], e['rel']))
    for pi, p in enumerate(d):
        Wp = p.rect.width * Z
        lines = []
        if not e['scanned']:
            for b in p.get_text('dict')['blocks']:
                for l in b.get('lines', []):
                    t = ''.join(s['text'] for s in l['spans']).strip()
                    if t:
                        x0, y0, x1, y1 = [v * Z for v in l['bbox']]
                        lines.append(dict(t=t, x0=x0, y0=y0, x1=x1, y1=y1))
        else:
            fn = os.path.join(KC, 'ocr', '%s_p%02d.json' % (e['tag'], pi + 1))
            if os.path.exists(fn):
                raw = open(fn, encoding='utf-8-sig').read().strip()
                lines = json.loads(raw) if raw else []
                if isinstance(lines, dict):
                    lines = [lines]
        for l in lines:
            l['col'] = 0 if (l['x0'] + l['x1']) / 2 < Wp / 2 else 1
        lines.sort(key=lambda l: (l['col'], round(l['y0'] / 8), l['x0']))
        allines['%s_p%02d' % (e['tag'], pi + 1)] = lines
        out.append('--- p%d' % (pi + 1))
        cur = None
        for l in lines:
            if l['col'] != cur:
                out.append('  [col %d]' % l['col']); cur = l['col']
            out.append('  %4d| %s' % (l['y0'], l['t']))
open(os.path.join(KC, 'dump.txt'), 'w', encoding='utf-8').write('\n'.join(out))
json.dump(allines, open(os.path.join(KC, 'lines.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(out), sum(len(x) for x in out))
