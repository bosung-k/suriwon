"""서초고 1학년 기말 대비 교재 생성 (수리원 HWPX 양식 + content/s*.py).

Usage: python gen_sc.py <out.hwpx>
content/sN.py : S = {'no','title','plan','bundles': [(학습 제목, [문항 dict, ...]), ...]}
문항 dict : id, src, q, cond, after_cond, bogi, choices, img, imgw, size, ans, sol
"""
import sys, os, re, copy, zipfile, importlib.util, glob, shutil
from lxml import etree
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen
from gen import E, para, table, cell, cell_tail, bogi_box, cond_box, choices_para, endnote, grid_table, \
    load_tpl, set_texts, section_header, nid, ns, HP, NS_HC

HC = '{%s}' % NS_HC
FIGS = os.path.join(HERE, 'figs')
_pics = []          # (binid, path)


def pic(sl, name, width=17000):
    path = os.path.join(FIGS, name + '.png')
    im = Image.open(path)
    wpx, hpx = im.size
    h = int(width * hpx / wpx)
    binid = 'scimg%d' % (len(_pics) + 1)
    _pics.append((binid, path))
    p = para(sl, '', 8, 1, 6)
    run = p.find('hp:run', ns)
    run.remove(run.find('hp:t', ns))
    e = E('pic', {'id': nid(), 'zOrder': 0, 'numberingType': 'PICTURE', 'textWrap': 'TOP_AND_BOTTOM', 'textFlow': 'BOTH_SIDES',
                  'lock': 0, 'dropcapstyle': 'None', 'href': '', 'groupLevel': 0, 'instid': int(nid()) % 2000000000 + 100000000,
                  'reverse': 0}, run)
    E('offset', {'x': 0, 'y': 0}, e)
    E('orgSz', {'width': width, 'height': h}, e)
    E('curSz', {'width': width, 'height': h}, e)
    E('flip', {'horizontal': 0, 'vertical': 0}, e)
    E('rotationInfo', {'angle': 0, 'centerX': width // 2, 'centerY': h // 2, 'rotateimage': 1}, e)
    ri = E('renderingInfo', None, e)
    for tag in ('transMatrix', 'scaMatrix', 'rotMatrix'):
        etree.SubElement(ri, HC + tag, {'e1': '1', 'e2': '0', 'e3': '0', 'e4': '0', 'e5': '1', 'e6': '0'})
    etree.SubElement(e, HC + 'img', {'binaryItemIDRef': binid, 'bright': '0', 'contrast': '0', 'effect': 'REAL_PIC', 'alpha': '0'})
    rect = E('imgRect', None, e)
    for i, (x, y) in enumerate(((0, 0), (width, 0), (width, h), (0, h))):
        etree.SubElement(rect, HC + 'pt%d' % i, {'x': str(x), 'y': str(y)})
    E('imgClip', {'left': 0, 'right': wpx * 75, 'top': 0, 'bottom': hpx * 75}, e)
    E('inMargin', {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}, e)
    E('imgDim', {'dimwidth': wpx * 75, 'dimheight': hpx * 75}, e)
    E('effects', None, e)
    E('sz', {'width': width, 'widthRelTo': 'ABSOLUTE', 'height': h, 'heightRelTo': 'ABSOLUTE', 'protect': 0}, e)
    E('pos', {'treatAsChar': 1, 'affectLSpacing': 0, 'flowWithText': 1, 'allowOverlap': 0, 'holdAnchorAndSO': 0, 'vertRelTo': 'PARA',
              'horzRelTo': 'COLUMN', 'vertAlign': 'TOP', 'horzAlign': 'LEFT', 'vertOffset': 0, 'horzOffset': 0}, e)
    E('outMargin', {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}, e)
    E('shapeComment', None, e, '그림입니다.')
    E('t', None, run)


def problem_cell(tr, row, height, prob):
    W0, W1, W2 = 7375, 1419, 51566
    m = (454, 454, 454, 454)
    tc, sl = cell(tr, 0, row, W0, height, 18)
    p = E('p', {'id': 0, 'paraPrIDRef': 30, 'styleIDRef': 2, 'pageBreak': 0, 'columnBreak': 0, 'merged': 0}, sl)
    r = E('run', {'charPrIDRef': 19}, p)
    endnote(r, prob['ans'], prob.get('sol'))
    E('t', None, r)
    cell_tail(tc, 0, row, W0, height, margin=m)
    tc, sl = cell(tr, 1, row, W1, height, 19)
    para(sl, '', 0, 0, 6)
    cell_tail(tc, 1, row, W1, height, margin=m)
    tc, sl = cell(tr, 2, row, W2, height, 20)
    para(sl, prob['tag'], 8, 1, 32, eqcolor='#300101')
    for ln in (prob['q'] if isinstance(prob['q'], list) else [prob['q']]):
        para(sl, ln, 8, 1, 6)
    if prob.get('cond'):
        cond_box(sl, prob['cond'])
    for ln in prob.get('after_cond', []):
        para(sl, ln, 8, 1, 6)
    if prob.get('img'):
        names = prob['img'] if isinstance(prob['img'], list) else [prob['img']]
        ws = prob.get('imgw', 17000)
        ws = ws if isinstance(ws, list) else [ws] * len(names)
        for nm, w in zip(names, ws):
            pic(sl, nm, w)
    if prob.get('bogi'):
        bogi_box(sl, prob['bogi'])
    if prob.get('choices'):
        choices_para(sl, prob['choices'])
    cell_tail(tc, 2, row, W2, height, margin=m)


def problem_page(parent, probs):
    para(parent, '', 23, 0, 6, pageBreak=1)
    p = E('p', {'id': 0, 'paraPrIDRef': 23, 'styleIDRef': 0, 'pageBreak': 0, 'columnBreak': 0, 'merged': 0}, parent)
    run = E('run', {'charPrIDRef': 9}, p)
    H = 81620
    t = table(run, len(probs), 3, 60360, H, 20)
    for i, pr in enumerate(probs):
        tr = E('tr', None, t)
        problem_cell(tr, i, H // 2, pr)
    E('t', None, run)


def load_sessions(cdir):
    out = []
    for f in sorted(glob.glob(os.path.join(cdir, 's?.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        out.append(m.S)
    return out


def show_src(src):
    """학생용에는 부교재 원문과 서초고 기출만 출처를 보인다."""
    return (src.startswith('부교재') or src.startswith('2025 기말')) and '변형' not in src


def number(sessions):
    n = 0
    for s in sessions:
        s['range'] = [n + 1, None]
        for bt, items in s['bundles']:
            for pr in items:
                n += 1
                pr['no'] = n
                pr['tag'] = ('%s   |   %s' % (bt, pr['src'])) if show_src(pr['src']) else bt
        s['range'][1] = n
    return n


def build(out):
    sessions = load_sessions(os.path.join(HERE, 'content'))
    total = number(sessions)
    sec, root, ps = load_tpl()
    head_tpl, toc_tpl = ps[26], ps[18]
    keep, tail_cover = ps[:18], ps[21:26]
    for p in ps:
        root.remove(p)
    for p in keep:
        root.append(p)
    set_texts(keep[10], ['공통수학2'])
    set_texts(keep[11], ['집합 ~ 무리함수'])
    set_texts(keep[12], ['서초고 기말고사 대비 (%d제)' % total])
    set_texts(keep[14], ['2026년 1학년 2학기 기말고사 대비'])
    for s in sessions:
        toc = copy.deepcopy(toc_tpl)
        set_texts(toc, ['%s   ' % s['no'], '%s     ' % s['title'], '%d – %d번' % tuple(s['range'])])
        root.append(toc)
    for p in tail_cover:
        root.append(p)

    # 구성 안내
    para(root, [(21, '교재 구성')], 38, 11, 21, pageBreak=1)
    para(root, '(1) 시험 범위(집합의 연산 ~ 무리함수)를 교과서 단원 순서로 배열하고, 단원 안에서는 풀이 아이디어가 비슷한 문항끼리 묶었다.', 40, 12, 6)
    para(root, '(2) 각 묶음은 기본 확인 → 부교재 문항 → 응용 → 기출 순서이다. 부교재와 서초고 기출 문항에만 문항 위에 출처를 적었다.', 40, 12, 6)
    rows = [['단원', '학습 묶음', '문항 번호']]
    for s in sessions:
        first = True
        for bt, items in s['bundles']:
            a, b = items[0]['no'], items[-1]['no']
            rows.append([('%s %s' % (s['no'], s['title'])) if first else '', bt, '%d ~ %d번' % (a, b) if a != b else '%d번' % a])
            first = False
    grid_table(root, rows, [13000, 33000, 13000])
    para(root, '(3) 출처: ‘부교재’는 서초고 공통수학2 워크북, ‘2025 기말’은 2025학년도 서초고 2학기 기말고사이다. 정답과 풀이는 책의 맨 뒤에 있다.', 40, 12, 6)

    for s in sessions:
        probs = [pr for _, items in s['bundles'] for pr in items]
        for i in range(0, len(probs), 2):
            problem_page(root, probs[i:i + 2])

    # 빠른 정답
    para(root, [(21, '빠른 정답')], 38, 11, 21, pageBreak=1)
    allp = [pr for s in sessions for _, items in s['bundles'] for pr in items]
    rows = [['번호', '정답'] * 5]
    per = (len(allp) + 4) // 5
    for r in range(per):
        row = []
        for c in range(5):
            k = c * per + r
            if k < len(allp):
                row += [str(allp[k]['no']), allp[k].get('quick', allp[k]['ans'])]
            else:
                row += ['', '']
        rows.append(row)
    grid_table(root, rows, [3400, 8400] * 5)

    tmp = out + '.dir'
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(gen.TPL, tmp)
    sec.write(os.path.join(tmp, 'Contents', 'section0.xml'), xml_declaration=True, encoding='UTF-8', standalone=True)
    reps = {'masterpage0.xml': [('III. 유리함수와 무리함수', '공통수학2  집합 ~ 무리함수')],
            'masterpage1.xml': [('>03<', '>기말<'), ('유리함수와 무리함수', '서초고 1학년')]}
    for mp, rr in reps.items():
        f = os.path.join(tmp, 'Contents', mp)
        s = open(f, encoding='utf-8').read()
        for a, b in rr:
            s = s.replace(a, b)
        open(f, 'w', encoding='utf-8').write(s)
    f = os.path.join(tmp, 'Contents', 'content.hpf')
    s = open(f, encoding='utf-8').read().replace('공통수학2 III. 유리함수와 무리함수 50제', '공통수학2 집합~무리함수 서초고 기말 대비')
    items = ''.join('<opf:item id="%s" href="BinData/%s.png" media-type="image/png" isEmbeded="1"/>' % (b, b) for b, _ in _pics)
    s = s.replace('<opf:item id="section0"', items + '<opf:item id="section0"')
    open(f, 'w', encoding='utf-8').write(s)
    for b, pth in _pics:
        shutil.copy(pth, os.path.join(tmp, 'BinData', b + '.png'))
    with zipfile.ZipFile(out, 'w') as z:
        z.write(os.path.join(tmp, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
        for dp, dn, fn in os.walk(tmp):
            for name in fn:
                full = os.path.join(dp, name)
                arc = os.path.relpath(full, tmp).replace('\\', '/')
                if arc != 'mimetype' and name != 'desktop.ini':
                    z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)
    print('written', out, 'problems', total, 'endnotes', gen._en[0], 'pics', len(_pics))


if __name__ == '__main__':
    build(sys.argv[1])

