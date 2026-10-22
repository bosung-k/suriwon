"""Build an HWPX book from the 수리원 template + content modules.

Usage: python gen.py <kind: lesson|workbook> <out.hwpx> <content_dir>
Text markup: $...$ = Hangul equation script.
"""
import sys, os, re, copy, zipfile, importlib.util, glob
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'yx')
NS_HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
NS_HC = 'http://www.hancom.co.kr/hwpml/2011/core'
HP = '{%s}' % NS_HP
ns = {'hp': NS_HP}

_id = [2000000000]


def nid():
    _id[0] += 1
    return str(_id[0])


def E(tag, attrib=None, parent=None, text=None):
    attrib = {k: str(v) for k, v in (attrib or {}).items()}
    e = etree.SubElement(parent, HP + tag, attrib) if parent is not None else etree.Element(HP + tag, attrib, nsmap={'hp': NS_HP})
    if text is not None:
        e.text = text
    return e


# ---------------------------------------------------------------- equations
def eq_size(script, base=1000):
    s = re.sub(r'\b(LEFT|RIGHT|rm|it|bold)\b', '', script)
    s = re.sub(r'[{}`~ ]', '', s)
    s = re.sub(r'\b(over|sqrt|SUBSET|cap|cup|sim|times|leq|geq|LEQ|GEQ|RARROW|LRARROW|rarrow|lrarrow|SMALLINTER|CUP|SIM|TIMES|CDOTS|cdots|EMPTYSET|in|IN|notin|NOTIN|neq|NEQ|alpha|beta|circ|CIRC|prime)\b', 'X', s)
    n = max(1, len(s))
    frac = ' over ' in script or 'over{' in script.replace(' ', '') or 'cases' in script
    w = int(n * base * 0.52) + 200
    if frac:
        num = script.count('over')
        w = int(w * 0.75)
        return w, int(base * 2.35), 65
    if 'sqrt' in script or '^' in script:
        return w, int(base * 1.25), 80
    return w, int(base * 1.125), 85


def add_eq(run, script, color='#000000', base=1000):
    # set-builder bar: add thin spaces around '|' (but keep LEFT | ... RIGHT | absolute values)
    script = re.sub(r'(?<!LEFT)(?<!RIGHT) \| ', ' `|` ', script)
    w, h, bl = eq_size(script, base)
    e = E('equation', {'id': nid(), 'zOrder': '0', 'numberingType': 'EQUATION', 'textWrap': 'TOP_AND_BOTTOM', 'textFlow': 'BOTH_SIDES',
                       'lock': '0', 'dropcapstyle': 'None', 'version': 'Equation Version 60', 'baseLine': bl, 'textColor': color,
                       'baseUnit': base, 'lineMode': 'CHAR', 'font': 'HYhwpEQ'}, run)
    E('sz', {'width': w, 'widthRelTo': 'ABSOLUTE', 'height': h, 'heightRelTo': 'ABSOLUTE', 'protect': 0}, e)
    E('pos', {'treatAsChar': 1, 'affectLSpacing': 0, 'flowWithText': 1, 'allowOverlap': 0, 'holdAnchorAndSO': 0, 'vertRelTo': 'PARA',
              'horzRelTo': 'PARA', 'vertAlign': 'TOP', 'horzAlign': 'LEFT', 'vertOffset': 0, 'horzOffset': 0}, e)
    E('outMargin', {'left': 56, 'right': 56, 'top': 0, 'bottom': 0}, e)
    E('shapeComment', None, e, '수식입니다.')
    E('script', None, e, script)
    return e


def add_text(run, s):
    """plain text; '\t' becomes a tab element"""
    t = E('t', None, run)
    parts = s.split('\t')
    t.text = parts[0]
    for p in parts[1:]:
        tab = E('tab', {'width': 4000, 'leader': 0, 'type': 1}, t)
        tab.tail = p
    return t


def fill_run(run, text, eqcolor='#000000'):
    parts = re.split(r'\$(.*?)\$', text)
    for i, part in enumerate(parts):
        if i % 2:
            add_eq(run, part.strip(), eqcolor)
        elif part:
            add_text(run, part)
    if len(parts) == 1 and not parts[0]:
        E('t', None, run)


def para(parent, text='', paraPr=0, style=0, charPr=6, pageBreak=0, eqcolor='#000000'):
    p = E('p', {'id': 0, 'paraPrIDRef': paraPr, 'styleIDRef': style, 'pageBreak': pageBreak, 'columnBreak': 0, 'merged': 0}, parent)
    run = E('run', {'charPrIDRef': charPr}, p)
    if isinstance(text, list):          # list of (charPr, text) runs
        p.remove(run)
        for cp, tx in text:
            r = E('run', {'charPrIDRef': cp}, p)
            fill_run(r, tx, eqcolor)
    else:
        fill_run(run, text, eqcolor)
    return p


# ---------------------------------------------------------------- tables
def sublist(parent, valign='TOP'):
    return E('subList', {'id': '', 'textDirection': 'HORIZONTAL', 'lineWrap': 'BREAK', 'vertAlign': valign, 'linkListIDRef': 0,
                         'linkListNextIDRef': 0, 'textWidth': 0, 'textHeight': 0, 'hasTextRef': 0, 'hasNumRef': 0}, parent)


def table(run, rows, cols, width, height, bf, inmargin=(510, 510, 141, 141), horzRel='COLUMN'):
    t = E('tbl', {'id': nid(), 'zOrder': 0, 'numberingType': 'TABLE', 'textWrap': 'TOP_AND_BOTTOM', 'textFlow': 'BOTH_SIDES', 'lock': 0,
                  'dropcapstyle': 'None', 'pageBreak': 'CELL', 'repeatHeader': 0, 'rowCnt': rows, 'colCnt': cols, 'cellSpacing': 0,
                  'borderFillIDRef': bf, 'noAdjust': 0}, run)
    E('sz', {'width': width, 'widthRelTo': 'ABSOLUTE', 'height': height, 'heightRelTo': 'ABSOLUTE', 'protect': 0}, t)
    E('pos', {'treatAsChar': 1, 'affectLSpacing': 0, 'flowWithText': 1, 'allowOverlap': 0, 'holdAnchorAndSO': 0, 'vertRelTo': 'PARA',
              'horzRelTo': horzRel, 'vertAlign': 'TOP', 'horzAlign': 'LEFT', 'vertOffset': 0, 'horzOffset': 0}, t)
    E('outMargin', {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}, t)
    l, r, tp, b = inmargin
    E('inMargin', {'left': l, 'right': r, 'top': tp, 'bottom': b}, t)
    return t


def cell(tr, col, row, w, h, bf, colspan=1, rowspan=1, valign='TOP', margin=(454, 454, 454, 454), hasMargin=0):
    tc = E('tc', {'name': '', 'header': 0, 'hasMargin': hasMargin, 'protect': 0, 'editable': 0, 'dirty': 1, 'borderFillIDRef': bf}, tr)
    sl = sublist(tc, valign)
    return tc, sl


def cell_tail(tc, col, row, w, h, colspan=1, rowspan=1, margin=(454, 454, 454, 454)):
    E('cellAddr', {'colAddr': col, 'rowAddr': row}, tc)
    E('cellSpan', {'colSpan': colspan, 'rowSpan': rowspan}, tc)
    E('cellSz', {'width': w, 'height': h}, tc)
    l, r, t, b = margin
    E('cellMargin', {'left': l, 'right': r, 'top': t, 'bottom': b}, tc)


# ---------------------------------------------------------------- blocks
def concept_box(parent, title, lines):
    p = E('p', {'id': 0, 'paraPrIDRef': 42, 'styleIDRef': 13, 'pageBreak': 0, 'columnBreak': 0, 'merged': 0}, parent)
    run = E('run', {'charPrIDRef': 6}, p)
    t = table(run, 1, 1, 59000, 5000, 21, (1200, 1200, 800, 800))
    tr = E('tr', None, t)
    tc, sl = cell(tr, 0, 0, 59000, 5000, 21, valign='CENTER', hasMargin=1)
    para(sl, title, 43, 13, 32, eqcolor='#300101')
    for ln in lines:
        para(sl, ln, 44, 13, 6)
    cell_tail(tc, 0, 0, 59000, 5000, margin=(1200, 1200, 800, 800))
    E('t', None, run)
    return p


def item_height(items, per_line=46):
    h = 0
    for it in items:
        tall = (' over ' in it) or ('cases' in it)
        lines = max(1, int(vis_len(it) / per_line + 0.999))
        h += (2700 if tall else 1700) + (lines - 1) * 1800
    return h + 1000


def bogi_box(parent, items, width=42000, title='<보 기>'):
    """template-style box: title sits in a gap of the top border"""
    p = para(parent, '', 19, 1, 6)
    run = p.find('hp:run', ns)
    run.remove(run.find('hp:t', ns))
    side = (width - 5000) // 2
    t = table(run, 3, 3, width, 3000, 5, horzRel='PARA')
    tr = E('tr', None, t)
    m = (510, 510, 141, 141)
    tc, sl = cell(tr, 0, 0, side, 625, 6, valign='CENTER'); para(sl, '', 9, 4, 29); cell_tail(tc, 0, 0, side, 625, margin=m)
    tc, sl = cell(tr, 1, 0, 5000, 1282, 1, valign='CENTER'); para(sl, title, 18, 4, 6); cell_tail(tc, 1, 0, 5000, 1282, 1, 2, margin=m)
    tc, sl = cell(tr, 2, 0, side, 625, 6, valign='CENTER'); para(sl, '', 9, 4, 29); cell_tail(tc, 2, 0, side, 625, margin=m)
    tr = E('tr', None, t)
    tc, sl = cell(tr, 0, 1, side, 657, 7, valign='CENTER'); para(sl, '', 9, 4, 29); cell_tail(tc, 0, 1, side, 657, margin=m)
    tc, sl = cell(tr, 2, 1, side, 657, 8, valign='CENTER'); para(sl, '', 9, 4, 29); cell_tail(tc, 2, 1, side, 657, margin=m)
    tr = E('tr', None, t)
    hh = item_height(items)
    tc, sl = cell(tr, 0, 2, width, hh, 9, colspan=3, valign='CENTER')
    for it in items:
        para(sl, it, 7, 0, 29)
    cell_tail(tc, 0, 2, width, hh, 3, 1, margin=(1200, 1200, 300, 700))
    t.find('hp:sz', ns).set('height', str(hh + 1300))
    E('t', None, run)
    return p


def cond_box(parent, items, width=46000):
    p = para(parent, '', 19, 1, 6)
    run = p.find('hp:run', ns)
    run.remove(run.find('hp:t', ns))
    hh = item_height(items) + 200
    t = table(run, 1, 1, width, hh, 5, horzRel='PARA')
    tr = E('tr', None, t)
    tc, sl = cell(tr, 0, 0, width, hh, 5, valign='CENTER')
    for it in items:
        para(sl, it, 7, 0, 29)
    cell_tail(tc, 0, 0, width, hh, margin=(1200, 1200, 500, 500))
    E('t', None, run)
    return p


def grid_table(parent, rows, widths, header=True):
    """plain table (lesson plan etc.). rows: list of list of str"""
    p = para(parent, '', 42, 0, 6)
    run = p.find('hp:run', ns)
    run.remove(run.find('hp:t', ns))
    W = sum(widths)
    t = table(run, len(rows), len(widths), W, 2000 * len(rows), 5)
    for ri, row in enumerate(rows):
        tr = E('tr', None, t)
        for ci, txt in enumerate(row):
            tc, sl = cell(tr, ci, ri, widths[ci], 2000, 5, valign='CENTER')
            for k, line in enumerate(str(txt).split('\n')):
                if ri == 0 and header:
                    para(sl, line, 2, 0, 32)
                else:
                    para(sl, line, 9, 0, 6)
            cell_tail(tc, ci, ri, widths[ci], 2000, margin=(500, 500, 300, 300))
    E('t', None, run)
    return p


_en = [0]


def endnote(run, ans, sol):
    _en[0] += 1
    ctrl = E('ctrl', None, run)
    en = E('endNote', {'number': _en[0], 'instId': nid()}, ctrl)
    sl = sublist(en)
    p = E('p', {'id': 0, 'paraPrIDRef': 10, 'styleIDRef': 10, 'pageBreak': 0, 'columnBreak': 0, 'merged': 0}, sl)
    r = E('run', {'charPrIDRef': 20}, p)
    c2 = E('ctrl', None, r)
    an = E('autoNum', {'num': _en[0], 'numType': 'ENDNOTE'}, c2)
    E('autoNumFormat', {'type': 'DIGIT', 'userChar': '', 'prefixChar': '', 'suffixChar': '', 'supscript': 0}, an)
    fill_run(r, ') [정답] ' + ans)
    for ln in sol or []:
        para(sl, ln, 10, 10, 6)


def vis_len(s):
    """approximate printed width in 'Korean character' units"""
    n = 0.0
    for i, part in enumerate(re.split(r'\$(.*?)\$', s)):
        if i % 2:
            sc = re.sub(r'\b(LEFT|RIGHT|rm|it|bold)\b|[{}`~ ]', '', part)
            sc = re.sub(r'<=|>=|!=|->|\+-', 'X', sc)
            sc = re.sub(r'\b(over|sqrt|SUBSET|cap|cup|sim|times|cdots|EMPTYSET|in|RARROW|LRARROW|CIRC|not)\b', 'X', sc)
            k = 0.68 if ' over ' in part else 0.85
            n += len(sc) * k + 0.3
        else:
            n += sum(1.0 if ord(c) > 0x1100 else 0.55 for c in part)
    return n


def choices_para(sl, ch):
    n = len(ch)
    marks = '①②③④⑤'
    longest = max(vis_len(c) for c in ch)
    if longest <= 6.5:
        cols = 5
    elif longest <= 12.5:
        cols = 3
    elif longest <= 20:
        cols = 2
    else:
        cols = 1
    if cols == 1:
        for i in range(n):
            para(sl, marks[i] + ' ' + ch[i], 37, 9, 6)
        return
    # invisible table keeps the columns aligned
    p = para(sl, '', 9, 0, 6)
    run = p.find('hp:run', ns)
    run.remove(run.find('hp:t', ns))
    W = 49000
    cw = W // cols
    rows = (n + cols - 1) // cols
    tall = any((' over ' in c) or ('sqrt' in c) for c in ch)
    rh = 2300 if tall else 1500
    t = table(run, rows, cols, W, rh * rows, 1, inmargin=(0, 0, 0, 0), horzRel='PARA')
    for r in range(rows):
        tr = E('tr', None, t)
        for c in range(cols):
            i = r * cols + c
            tc, cl = cell(tr, c, r, cw, rh, 1, valign='CENTER')
            para(cl, (marks[i] + ' ' + ch[i]) if i < n else '', 9, 0, 6)
            cell_tail(tc, c, r, cw, rh, margin=(400, 100, 60, 60))
    E('t', None, run)


def problem_cell(tr, row, rowspan, height, prob):
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
    if prob.get('tag'):
        para(sl, prob['tag'], 8, 1, 32, eqcolor='#300101')
    q = prob['q'] if isinstance(prob['q'], list) else [prob['q']]
    for ln in q:
        para(sl, ln, 8, 1, 6)
    if prob.get('cond'):
        cond_box(sl, prob['cond'])
    if prob.get('after_cond'):
        for ln in prob['after_cond']:
            para(sl, ln, 8, 1, 6)
    if prob.get('bogi'):
        bogi_box(sl, prob['bogi'])
    if prob.get('note'):
        para(sl, prob['note'], 17, 1, 6)
    if prob.get('choices'):
        choices_para(sl, prob['choices'])
    cell_tail(tc, 2, row, W2, height, margin=m)


def problem_page(parent, probs):
    para(parent, '', 23, 0, 6, pageBreak=1)
    p = E('p', {'id': 0, 'paraPrIDRef': 23, 'styleIDRef': 0, 'pageBreak': 0, 'columnBreak': 0, 'merged': 0}, parent)
    run = E('run', {'charPrIDRef': 9}, p)
    H = 81620
    h = H // len(probs)
    t = table(run, len(probs), 3, 60360, H, 20)
    for i, pr in enumerate(probs):
        tr = E('tr', None, t)
        problem_cell(tr, i, 1, h, pr)
    E('t', None, run)


# ---------------------------------------------------------------- template pieces
def load_tpl():
    sec = etree.parse(os.path.join(TPL, 'Contents', 'section0.xml'))
    root = sec.getroot()
    ps = root.findall('hp:p', ns)
    return sec, root, ps


def set_texts(p, texts):
    ts = [t for t in p.iter(HP + 't') if t.text and t.text.strip()]
    for t, new in zip(ts, texts):
        t.text = new


def section_header(parent, tpl_head, num, title):
    h = copy.deepcopy(tpl_head)
    ts = [t for t in h.iter(HP + 't') if t.text and t.text.strip()]
    ts[0].text = num
    ts[1].text = title
    for e in h.iter():
        if e.get('instid'):
            e.set('instid', str(int(nid()) % 2000000000 + 300000000))
        if etree.QName(e).localname in ('container', 'rect') and e.get('id') not in (None, '0'):
            e.set('id', nid())
    parent.append(h)


def build(kind, out, content_dir):
    sys.path.insert(0, content_dir)
    sessions = []
    for f in sorted(glob.glob(os.path.join(content_dir, 's?.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        sessions.append(m.S)
    meta = importlib.util.spec_from_file_location('meta', os.path.join(content_dir, 'meta.py'))
    M = importlib.util.module_from_spec(meta)
    meta.loader.exec_module(M)

    sec, root, ps = load_tpl()
    head_tpl = ps[26]
    toc_tpl = ps[18]
    keep = ps[:18]  # secPr + cover up to toc
    tail_cover = ps[21:26]
    for p in ps:
        root.remove(p)
    for p in keep:
        root.append(p)
    # cover texts
    book = M.BOOK[kind]
    set_texts(keep[10], ['공통수학2'])
    set_texts(keep[11], [book['title']])
    set_texts(keep[12], [book['sub']])
    set_texts(keep[14], ['2026년 1학년 2학기 기말고사 대비'])
    key = 'examples' if kind == 'lesson' else 'workbook'
    start = 1
    for s in sessions:
        n = len(s[key])
        toc = copy.deepcopy(toc_tpl)
        set_texts(toc, ['%s   ' % s['no'], '%s     ' % s['title'], '%d – %d번' % (start, start + n - 1)])
        root.append(toc)
        start += n
    for p in tail_cover:
        root.append(p)

    # number ranges + type tags
    ranges = {}
    for k in ('examples', 'workbook'):
        st = 1
        for s in sessions:
            ranges[(s['no'], k)] = (st, st + len(s[k]) - 1)
            st += len(s[k])
    for s in sessions:
        for k in ('examples', 'workbook'):
            for pr in s[k]:
                if 't' in pr and 'tag' not in pr:
                    tag = '유형 %02d  %s' % (pr['t'], s['types'][pr['t'] - 1])
                    if pr.get('src'):
                        tag += '   |   ' + pr['src']
                    pr['tag'] = tag

    # lesson plan page (both books)
    para(root, [(21, M.PLAN_TITLE)], 38, 11, 21, pageBreak=1)
    for ln in M.PLAN_INTRO:
        para(root, ln, 40, 12, 6)
    if hasattr(M, 'PLAN_ROWS'):
        grid_table(root, M.PLAN_ROWS(sessions, ranges), M.PLAN_WIDTHS)
    else:
        rows = [['회차', '수업 내용', '교과서', '교재 예제', '워크북 과제']]
        for s in sessions:
            a, b = ranges[(s['no'], 'examples')]
            c, d = ranges[(s['no'], 'workbook')]
            rows.append(['%d회' % int(s['no']), s['plan'], s['pages'], '%d ~ %d번' % (a, b), '%d ~ %d번\n(%d문항)' % (c, d, d - c + 1)])
        grid_table(root, rows, [5200, 27000, 8000, 8800, 10000])
    for ln in M.PLAN_NOTES:
        para(root, ln, 40, 12, 6)

    per_page = 2 if kind == 'lesson' else 3
    for s in sessions:
        section_header(root, head_tpl, s['no'], s['title'] + ('' if kind == 'lesson' else '  워크북'))
        first = True
        if kind == 'lesson':
            for item in s['concepts']:
                if item[0] == 'h':
                    para(root, item[1], 38 if first else 39, 11, 21)
                    first = False
                elif item[0] == 'p':
                    para(root, item[1], 40, 12, 6)
                elif item[0] == 'pi':
                    para(root, item[1], 41, 12, 6)
                elif item[0] == 'box':
                    concept_box(root, item[1], item[2])
                elif item[0] == 'pb':
                    para(root, '', 23, 0, 6, pageBreak=1)
                    first = True
        else:
            a, b = ranges[(s['no'], 'workbook')]
            ea, eb = ranges[(s['no'], 'examples')]
            para(root, [(21, '%d회 과제  |  워크북 %d ~ %d번 (%d문항)' % (int(s['no']), a, b, b - a + 1))], 38, 11, 21)
            para(root, '(1) 수업 교재 %d ~ %d번 예제를 다시 확인한 뒤 풀어요. 유형 순서대로 배열되어 있습니다.' % (ea, eb), 40, 12, 6)
            para(root, '(2) 채점 후 틀린 문제는 같은 유형의 교재 예제를 보고 다시 풀어 봅니다.', 40, 12, 6)
            rows = [['유형', '내용', '교재 예제', '워크북']]
            for ti, tname in enumerate(s['types'], 1):
                wn = [a + j for j, pr in enumerate(s['workbook']) if pr.get('t') == ti]
                en = [ea + j for j, pr in enumerate(s['examples']) if pr.get('t') == ti]
                fmt = lambda L: ('%d ~ %d번' % (L[0], L[-1]) if len(L) > 1 else '%d번' % L[0]) if L else '-'
                rows.append(['유형 %02d' % ti, tname, fmt(en), fmt(wn)])
            grid_table(root, rows, [7000, 30000, 11000, 11000])
        probs = s[key]
        i = 0
        while i < len(probs):
            n = per_page
            if probs[i].get('full'):
                n = 1
            chunk = []
            while i < len(probs) and len(chunk) < n:
                if chunk and probs[i].get('full'):
                    break
                chunk.append(probs[i]); i += 1
            problem_page(root, chunk)

    # write package
    tmp = out + '.dir'
    import shutil
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(TPL, tmp)
    sec.write(os.path.join(tmp, 'Contents', 'section0.xml'), xml_declaration=True, encoding='UTF-8', standalone=True)
    for mp, reps in M.MASTER[kind].items():
        f = os.path.join(tmp, 'Contents', mp)
        s = open(f, encoding='utf-8').read()
        for a, b in reps:
            s = s.replace(a, b)
        open(f, 'w', encoding='utf-8').write(s)
    f = os.path.join(tmp, 'Contents', 'content.hpf')
    s = open(f, encoding='utf-8').read().replace('공통수학2 III. 유리함수와 무리함수 50제', '공통수학2 ' + book['title'] + ' ' + book['sub'])
    open(f, 'w', encoding='utf-8').write(s)
    # drop unused images? keep all (masterpage may reference)
    with zipfile.ZipFile(out, 'w') as z:
        z.write(os.path.join(tmp, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
        for dp, dn, fn in os.walk(tmp):
            for name in fn:
                full = os.path.join(dp, name)
                arc = os.path.relpath(full, tmp).replace('\\', '/')
                if arc == 'mimetype':
                    continue
                z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)
    print('written', out, 'endnotes', _en[0])


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3])
