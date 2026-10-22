import os, re, sys
from hx import *

P_OPEN = re.compile(r'<hp:p[ >]')


def top_paras(x):
    """Return list of (start, end) of top-level <hp:p> elements in section xml."""
    out = []
    depth = 0
    i = 0
    tok = re.compile(r'<hp:p[ >]|</hp:p>')
    for m in tok.finditer(x):
        if m.group(0) != '</hp:p>':
            if depth == 0:
                st = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                out.append((st, m.end()))
    return out


def plain(s):
    s = re.sub(r'<hp:endNote.*?</hp:endNote>', '', s, flags=re.S)
    s = re.sub(r'<hp:shapeComment>.*?</hp:shapeComment>', '', s, flags=re.S)
    s = re.sub(r'<hp:script>(.*?)</hp:script>', r'$\1$', s, flags=re.S)
    return re.sub(r'<[^>]+>', '', s)


if __name__ == '__main__':
    names = sys.argv[1:]
    todo = [(os.path.join(W, n + '.hwp'), os.path.join(W, n + '.hwpx'), 'HWPX') for n in names if not os.path.exists(os.path.join(W, n + '.hwpx'))]
    if todo:
        conv(*todo)
    for n in names:
        files, order = read_hwpx(os.path.join(W, n + '.hwpx'))
        x = files['Contents/section0.xml'].decode('utf-8')
        ps = top_paras(x)
        print('=====', n, len(ps))
        show = False
        for k, (a, b) in enumerate(ps):
            s = x[a:b]
            en = re.search(r'<hp:endNote number="(\d+)"', s)
            if en and int(en.group(1)) >= 13:
                show = True
            if not show:
                continue
            tag = s[:s.find('>') + 1]
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag))
            cp = re.findall(r'<hp:run charPrIDRef="(\d+)"', s)
            print(k, 'pp=%s st=%s pb=%s cb=%s' % (attrs.get('paraPrIDRef'), attrs.get('styleIDRef'), attrs.get('pageBreak'), attrs.get('columnBreak')),
                  'EN' + en.group(1) if en else '', 'PIC' if '<hp:pic ' in s else '', 'TBL' if '<hp:tbl ' in s else '', 'cp=' + ','.join(cp[:3]), '|', plain(s)[:60].replace('\n', ' '))
