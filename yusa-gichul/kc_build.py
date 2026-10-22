# -*- coding: utf-8 -*-
"""Build '유사 기출' HWPX from E1 template.  kc_build.py T|C"""
import os, re, sys, itertools, json
from xml.sax.saxutils import escape
from PIL import Image
from hx import *
from scan import top_paras, plain
import kcx
from kc_ans import ANS, DROP

ENDNOTE = True
NOTE_GAP = int(os.environ.get('NOTE_GAP', '300'))
_id = itertools.count(1960000001)
_z = itertools.count(3000)

TAGINFO = {
    'K00': '2015 반포중 2학기 중간', 'K01': '2015 반포중 2학기 기말', 'K02': '2016 반포중 2학기 기말', 'K03': '2017 반포중 2학기 기말', 'K04': '2017 반포중 2학기 중간',
    'K05': '2022 방배중 2학기 기말', 'K06': '2022 방배중 2학기 중간', 'K07': '2023 방배중 2학기 기말', 'K08': '2024 방배중 2학기 기말', 'K09': '2025 방배중 2학기 기말',
    'K10': '2016 서문여중 2학기 중간', 'K11': '2017 서문여중 2학기 기말', 'K12': '2017 서문여중 2학기 중간', 'K13': '2018 서문여중 2학기 기말', 'K14': '2018 서문여중 2학기 중간',
    'K15': '2019 서문여중 2학기 기말', 'K16': '2019 서문여중 2학기 중간', 'K17': '2020 서문여중 2학기 기말',
    'K22': '2017 세화여중 2학기 기말', 'K23': '2017 세화여중 2학기 중간', 'K24': '2018 세화여중 2학기 기말', 'K25': '2018 세화여중 2학기 중간', 'K26': '2019 세화여중 2학기 기말',
    'K27': '2019 세화여중 2학기 중간', 'K28': '2020 세화여중 2학기 기말', 'K29': '2020 세화여중 2학기 중간', 'K30': '2021 세화여중 2학기 기말', 'K31': '2021 세화여중 2학기 중간',
    'K32': '2022 세화여중 2학기 기말', 'K33': '2022 세화여중 2학기 중간', 'K34': '2023 세화여중 2학기 기말', 'K35': '2024 세화여중 2학기 기말', 'K36': '2025 세화여중 2학기 기말',
    'K39': '2017 신반포중 2학기 기말', 'K40': '2017 신반포중 2학기 중간', 'K41': '2018 신반포중 2학기 기말', 'K42': '2018 신반포중 2학기 중간', 'K43': '2019 신반포중 2학기 기말',
    'K44': '2020 신반포중 2학기 기말', 'K45': '2021 신반포중 2학기 기말', 'K47': '2021 신반포중 2학기 중간', 'K48': '2022 신반포중 2학기 기말', 'K49': '2022 신반포중 2학기 중간',
    'K50': '2023 신반포중 2학기 기말', 'K51': '2023 신반포중 2학기 중간', 'K52': '2024 신반포중 2학기 기말', 'K53': '2024 신반포중 2학기 중간', 'K54': '2025 신반포중 2학기 지필',
    'K59': '2022 옥정중 2학기 기말', 'K60': '2022 옥정중 2학기 중간', 'K61': '2023 옥정중 2학기 기말', 'K62': '2023 옥정중 2학기 중간', 'K63': '2024 옥정중 2학기 기말', 'K64': '2025 옥정중 2학기 기말',
}


def label(key):
    tag, rest = key.split('-', 1)
    rest = rest.split('@')[0]
    num = ('서술형 %s번' % rest[1:]) if rest.startswith('S') else ('%s번' % rest)
    if '@' in key:   # essay numbered without S
        num = '서술형 %s번' % rest
    return '[%s %s]' % (TAGINFO[tag], num)


EQ = ('<hp:equation id="%d" zOrder="%d" numberingType="EQUATION" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
      'dropcapstyle="None" version="Equation Version 60" baseLine="86" textColor="#000000" baseUnit="1100" lineMode="CHAR" font="HYhwpEQ">'
      '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="1125" heightRelTo="ABSOLUTE" protect="0"/>'
      '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" '
      'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="56" right="56" top="0" bottom="0"/>'
      '<hp:shapeComment>수식입니다.</hp:shapeComment><hp:script>%s</hp:script></hp:equation>')


KW = {'DEG', 'TRIANGLE', 'TIMES', 'DIV', 'LEFT', 'RIGHT', 'PI', 'LEQ', 'GEQ', 'BOT', 'CDOT', 'ANGLE', 'PM', 'MP', 'NEQ', 'RM', 'IT', 'SMALLSUM', 'PARALLEL', 'SIM', 'CONG', 'OVER', 'SQRT', 'BAR', 'ARCH', 'PRIME'}


def eq(script):
    # split point-name letter runs so they are not parsed as keywords (e.g. GE -> ≥)
    script = re.sub(r'\b[A-Z]{2,}\b', lambda m: m.group(0) if m.group(0) in KW else ' '.join(m.group(0)), script)
    vis = re.sub(r'\b(rm|it|over|sqrt|bar|DEG|angle|bot|TRIANGLE|arch|LEFT|RIGHT)\b|[{}~` ]', '', script)
    return EQ % (next(_id), next(_z), max(600, 520 * len(vis)), escape(script))


def content(markup):
    out = []
    for i, part in enumerate(markup.split('$')):
        if i % 2 == 0:
            if part:
                out.append('<hp:t>%s</hp:t>' % escape(part))
        else:
            out.append(eq(part))
    return ''.join(out)


def strip_ls(s):
    return re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', s, flags=re.S)


def ptag(s, pb=False, cb=False):
    t = re.match(r'<hp:p [^>]*>', s).group(0)
    t = re.sub(r'pageBreak="\d"', 'pageBreak="%d"' % pb, t)
    t = re.sub(r'columnBreak="\d"', 'columnBreak="%d"' % cb, t)
    return t


class Doc:
    def __init__(self, tmpl):
        self.files, self.order = read_hwpx(tmpl)
        x = self.files['Contents/section0.xml'].decode('utf-8')
        self.pr = top_paras(x); self.x = x
        P = lambda k: strip_ls(x[self.pr[min(k, len(self.pr) - 1)][0]:self.pr[min(k, len(self.pr) - 1)][1]])
        self.p0 = x[self.pr[0][0]:self.pr[0][1]]
        self.T_HEAD, self.T_LABEL, self.T_PROB, self.T_CH, self.T_PIC, self.T_BLANK = P(1), P(40), P(41), P(42), P(414), P(3)
        hpf = self.files['Contents/content.hpf'].decode('utf-8')
        # drop template images
        for n in [n for n in self.files if n.startswith('BinData/')]:
            del self.files[n]
        self.order = [n for n in self.order if not n.startswith('BinData/')]
        hpf = re.sub(r'<opf:item id="image\d+"[^>]*/>', '', hpf)
        self.hpf = hpf
        self.nimg = 0; self.en = 0; self.body = []
        hdr = self.files['Contents/header.xml'].decode('utf-8')
        self.bf = None
        for m in re.finditer(r'<hh:borderFill id="(\d+)".*?</hh:borderFill>', hdr, re.S):
            b = m.group(0)
            if all(re.search(r'<hh:%sBorder type="SOLID"' % s, b) for s in ('left', 'right', 'top', 'bottom')) and 'fillBrush' not in b:
                self.bf = m.group(1); break
        assert self.bf

    def head(self, text, cb=False, pb=False):
        s = self.T_HEAD.replace('세화여중3 학교프린트 III. 이차방정식 1번', escape(text))
        s = re.sub(r'<hp:tbl id="\d+" zOrder="\d+"', lambda m: '<hp:tbl id="%d" zOrder="%d"' % (next(_id), next(_z)), s)
        self.body.append(ptag(s, cb=cb, pb=pb) + s[len(re.match(r'<hp:p [^>]*>', s).group(0)):])

    def line(self, markup, cp='23'):
        self.body.append(ptag(self.T_BLANK) + '<hp:run charPrIDRef="%s">%s</hp:run></hp:p>' % (cp, content(markup) or '<hp:t/>'))

    def blank(self, n=1):
        for _ in range(n):
            self.body.append(ptag(self.T_BLANK) + '<hp:run charPrIDRef="23"/></hp:p>')

    def label(self, text, cb=False):
        self.body.append(ptag(self.T_LABEL, cb=cb) + '<hp:run charPrIDRef="21"><hp:t>%s</hp:t></hp:run></hp:p>' % escape(text))

    def problem(self, markup, ans=' '):
        self.en += 1
        if not ENDNOTE:
            self.body.append(ptag(self.T_BLANK) + '<hp:run charPrIDRef="23"><hp:t>%d) </hp:t>%s</hp:run></hp:p>' % (self.en, content(markup)))
            return
        s = self.T_PROB
        e = s.find('</hp:endNote></hp:ctrl>')
        head = s[:s.find('</hp:run>', e) + len('</hp:run>')]
        k1 = head.find('</hp:autoNum></hp:ctrl>') + len('</hp:autoNum></hp:ctrl>')
        k2 = head.rfind('</hp:run>', 0, head.find('</hp:subList>'))
        head = head[:k1] + (content(ans) if ans.strip() else '<hp:t> </hp:t>') + head[k2:]
        head = re.sub(r'<hp:endNote number="\d+"', '<hp:endNote number="%d"' % self.en, head)
        head = re.sub(r'<hp:autoNum num="\d+"', '<hp:autoNum num="%d"' % self.en, head)
        head = re.sub(r'instId="\d+"', 'instId="%d"' % next(_id), head)
        head = head.replace('<hp:run charPrIDRef="21"><hp:ctrl><hp:endNote', '<hp:run charPrIDRef="23"><hp:ctrl><hp:endNote', 1)
        self.body.append(head + '<hp:run charPrIDRef="23">%s</hp:run></hp:p>' % content(markup))

    def choices(self, ch):
        assert len(ch) == 5, ch
        mk = [c if ('$' in c or re.search(r'[가-힣ㄱ-ㅎ]', c)) else '$%s$' % c for c in ch]
        def wid(c):
            v = re.sub(r'\b(rm|it|sqrt|bar|DEG|angle|TIMES|DIV)\b|[{}~` $]', '', c)
            w = sum(2 if re.match(r'[가-힣ㄱ-ㅎ]', t) else 1 for t in v.replace('over', ''))
            return w * 0.6 if 'over' in c else w
        ws = [wid(c) for c in ch]
        nums = '①②③④⑤'
        SP = '          '
        if max(ws) > 7 or any('over' in c for c in ch):
            if max(ws) <= 7:
                self.line(SP.join('%s %s' % (n, c) for n, c in zip(nums[:3], mk[:3])))
                self.line(SP.join('%s %s' % (n, c) for n, c in zip(nums[3:], mk[3:])))
            else:
                for n, c in zip(nums, mk):
                    self.line('%s %s' % (n, c))
            return
        s = self.T_CH
        s = re.sub(r'<hp:tbl id="\d+" zOrder="\d+"', lambda m: '<hp:tbl id="%d" zOrder="%d"' % (next(_id), next(_z)), s)
        cells = list(re.finditer(r'(<hp:tc .*?<hp:subList[^>]*>)(.*?)(</hp:subList>)', s, re.S))
        assert len(cells) == 5
        out = []; last = 0
        for n, c, m in zip(nums, mk, cells):
            inner = m.group(2)
            pt = re.match(r'<hp:p [^>]*>', inner).group(0)
            new_inner = pt + '<hp:run charPrIDRef="3"><hp:t>%s </hp:t>%s</hp:run></hp:p>' % (n, content(c))
            out.append(s[last:m.start(2)] + new_inner); last = m.end(2)
        out.append(s[last:])
        self.body.append(''.join(out))

    def box(self, lines, title=None, width=27000):
        inner = ''.join('<hp:p id="0" paraPrIDRef="23" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="23">%s</hp:run></hp:p>'
                        % (content(l) or '<hp:t/>') for l in ([('<%s>' % title)] if title else []) + lines)
        tbl = ('<hp:tbl id="%d" zOrder="%d" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" '
               'pageBreak="CELL" repeatHeader="1" rowCnt="1" colCnt="1" cellSpacing="0" borderFillIDRef="%s" noAdjust="0">'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="2000" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" '
               'vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="140" right="140" top="140" bottom="140"/>'
               '<hp:inMargin left="510" right="510" top="141" bottom="141"/><hp:tr><hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" '
               'dirty="0" borderFillIDRef="%s"><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP" linkListIDRef="0" '
               'linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList><hp:cellAddr colAddr="0" rowAddr="0"/>'
               '<hp:cellSpan colSpan="1" rowSpan="1"/><hp:cellSz width="%d" height="2000"/><hp:cellMargin left="700" right="700" top="300" bottom="300"/>'
               '</hp:tc></hp:tr></hp:tbl>') % (next(_id), next(_z), self.bf, width, self.bf, inner, width)
        self.body.append(ptag(self.T_BLANK) + '<hp:run charPrIDRef="23">%s<hp:t/></hp:run></hp:p>' % tbl)

    def pic(self, path, maxw=27500, size=None):
        self.nimg += 1; iid = 'image%d' % self.nimg
        self.files['BinData/%s.png' % iid] = open(path, 'rb').read()
        self.order.append('BinData/%s.png' % iid)
        self.hpf = self.hpf.replace('</opf:manifest>', '<opf:item id="%s" href="BinData/%s.png" media-type="image/png" isEmbeded="1"/></opf:manifest>' % (iid, iid))
        w, h = Image.open(path).size
        sc = 45.5 * 0.78
        cw = int(w * sc); chh = int(h * sc)
        if size:
            cw, chh = size
        if cw > maxw:
            chh = int(chh * maxw / cw); cw = maxw
        ow, oh = w * 75, h * 75
        s = self.T_PIC
        s = re.sub(r'<hp:pic id="\d+" zOrder="\d+"', '<hp:pic id="%d" zOrder="%d"' % (next(_id), next(_z)), s)
        s = re.sub(r'instid="\d+"', 'instid="%d"' % next(_id), s)
        s = re.sub(r'<hp:orgSz width="\d+" height="\d+"/>', '<hp:orgSz width="%d" height="%d"/>' % (ow, oh), s)
        s = re.sub(r'<hp:curSz width="\d+" height="\d+"/>', '<hp:curSz width="%d" height="%d"/>' % (cw, chh), s)
        s = re.sub(r'centerX="\d+" centerY="\d+"', 'centerX="%d" centerY="%d"' % (cw // 2, chh // 2), s)
        s = re.sub(r'<hc:scaMatrix e1="[\d.]+" e2="0" e3="0" e4="0" e5="[\d.]+" e6="0"/>',
                   '<hc:scaMatrix e1="%.6f" e2="0" e3="0" e4="0" e5="%.6f" e6="0"/>' % (cw / ow, chh / oh), s)
        s = re.sub(r'binaryItemIDRef="\w+"', 'binaryItemIDRef="%s"' % iid, s)
        s = s.replace('effect="BLACK_WHITE"', 'effect="REAL_PIC"')
        s = re.sub(r'<hp:imgRect>.*?</hp:imgRect>', '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/><hc:pt3 x="0" y="%d"/></hp:imgRect>' % (ow, ow, oh, oh), s, flags=re.S)
        s = re.sub(r'<hp:imgClip left="0" right="\d+" top="0" bottom="\d+"/>', '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/>' % (ow, oh), s)
        s = re.sub(r'<hp:imgDim dimwidth="\d+" dimheight="\d+"/>', '<hp:imgDim dimwidth="%d" dimheight="%d"/>' % (ow, oh), s)
        s = re.sub(r'<hp:sz width="\d+" widthRelTo="ABSOLUTE" height="\d+"', '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d"' % (cw, chh), s)
        s = re.sub(r'<hp:shapeComment>.*?</hp:shapeComment>', '<hp:shapeComment>그림입니다.</hp:shapeComment>', s, flags=re.S)
        self.body.append(ptag(s) + s[len(re.match(r'<hp:p [^>]*>', s).group(0)):])

    def save(self, out, title):
        p0 = self.p0
        for a, b in (('2026학년도  제1학기', '2026학년도  제2학기'), ('기말고사 대비', '중간고사 대비'), ('학교프린트 분석문제', '학교프린트 유사 기출'), ('이차방정식', title)):
            p0 = p0.replace('<hp:t>%s</hp:t>' % a, '<hp:t>%s</hp:t>' % b)
        # tighter endnote list so answers fit on one page
        p0 = re.sub(r'(<hp:endNotePr>.*?<hp:noteSpacing betweenNotes=")\d+(")', r'\g<1>%d\2' % NOTE_GAP, p0, flags=re.S)
        x = self.x
        # endnotes start on their own page
        self.body.append(ptag(self.T_BLANK, pb=True) + '<hp:run charPrIDRef="23"/></hp:p>')
        body = p0 + ''.join(self.body)
        self.files['Contents/section0.xml'] = (x[:self.pr[0][0]] + body + x[self.pr[-1][1]:]).encode('utf-8')
        self.files['Contents/content.hpf'] = self.hpf.encode('utf-8')
        write_hwpx(out, self.files, self.order)
        return out


MULTI = {'K10-14', 'K14-S3', 'K06-21', 'K60-S3', 'K59-S2'}
SEL = {'K61-10': [2], 'K51-9': [1, 2], 'K36-12': [], 'K17-9': [2]}


W_EX_TEMPLATE = os.path.join(W, 'ex', 'E1.hwpx')
PR = {k: json.load(open(os.path.join(W, 'pr', ('%s_probs_fixed.json' if os.path.exists(os.path.join(W, 'pr', '%s_probs_fixed.json' % k)) else '%s_probs.json') % k), encoding='utf-8')) for k in 'TC'}


def figpaths(key):
    fs, names = kcx.save(key)
    return names


def build(kind):
    if kind == 'T':
        import kc_spec_t as S
        spec, none, title, nmax, unit = S.T, S.NONE_T, '삼각비', 29, '삼각비'
    else:
        import kc_spec_c as S
        spec, none, title, nmax, unit = S.C, S.NONE_C, '원의 성질', 33, '원과 직선, 원주각'
    d = Doc(W_EX_TEMPLATE)
    first = True
    for n in range(1, nmax + 1):
        if n not in spec and n not in none:
            continue
        d.head('세화여중3 학교프린트 %s %d번' % (unit, n), pb=not first); first = False
        # original print problem (left column)
        pp = PR[kind][n - 1]
        ptxt = [it for it in pp['items'] if it[0] == 'txt']
        d.problem(ptxt[0][1], ' ' + pp['ans'].replace('$$', '$, $'))
        for it in pp['items']:
            if it[0] == 'txt' and it is not ptxt[0]:
                d.line(it[1])
            elif it[0] == 'pic':
                w, h = Image.open(it[1]).size
                size = (it[2], it[3]) if it[2] else (int(w * 60), int(h * 60))
                if size[0] > 27500:
                    size = (27500, int(size[1] * 27500 / size[0]))
                d.pic(it[1], size=size)
            elif it[0] == 'tbl':
                d.pic(os.path.join(W, 'pr', 'T_tbl8.png'), size=(21000, int(21000 * Image.open(os.path.join(W, 'pr', 'T_tbl8.png')).size[1] / Image.open(os.path.join(W, 'pr', 'T_tbl8.png')).size[0])))
        d.label('[유사 기출문제]', cb=True)
        if n in none:
            d.line('※ 유사 기출 없음 ― %s' % none[n], cp='21'); d.blank(1)
            continue
        items = [it for it in spec[n] if it['k'] not in DROP]
        for it in items:
            d.label(label(it['k']))
            d.problem(it['q'], ' ' + ANS[it['k']])
            figs = it.get('figs_paths') or figpaths(it['k'])
            sel = SEL.get(it['k'], it.get('figs'))
            if sel is None and it['k'] not in MULTI:
                sel = [1] if figs else []
            if sel is not None:
                figs = [figs[i - 1] for i in sel]
            body = it['body']
            if body is None:
                body = ['F%d' % (i + 1) for i in range(len(figs))] + ([('C', it['ch'])] if it['ch'] else [])
            for b in body:
                if isinstance(b, str):
                    d.pic(figs[int(b[1:]) - 1])
                elif b[0] == 'S':
                    d.line(b[1])
                elif b[0] == 'C':
                    d.choices(b[1])
                elif b[0] == 'B':
                    d.box(b[1], b[2] if len(b) > 2 else None)
            if it is not items[-1]:
                d.blank(2)
    out = os.path.join(W, 'kc_%s.hwpx' % kind)
    return d.save(out, title)


if __name__ == '__main__':
    k = sys.argv[1]
    t = build(k)
    conv((t, os.path.join(W, 'kc_%s.pdf' % k), 'PDF'))
    print(render(os.path.join(W, 'kc_%s.pdf' % k), os.path.join(W, 'kc_%s' % k), zoom=1.1))
