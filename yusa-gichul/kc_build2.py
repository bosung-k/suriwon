# -*- coding: utf-8 -*-
"""Same content as kc_build, laid out with the '03-1. 세화여중 양식' exam form (template: G = exam made with that form).
kc_build2.py T|C [total_pages]"""
import os, re, sys
from xml.sax.saxutils import escape
from PIL import Image
import kc_build as KB
from kc_build import content, strip_ls, ptag, _id, _z, Doc
from hx import *
from scan import top_paras

TPL = os.path.join(W, 'ex', 'G.hwpx')
TAB = '<hp:tab width="6049" leader="0" type="1"/>'
CP_BODY, CP_CH, CP_NUM = '17', '12', '15'
CP_HEAD, CP_SRC = '19', '21'          # 12pt bold, 11pt bold
PP_PROB, PP_IND, PP_CH, PP_CH1, PP_PIC, PP_HEAD = '8', '11', '10', '12', '27', '3'


def para(pp, cp, inner, pb=False, cb=False):
    return ('<hp:p id="0" paraPrIDRef="%s" styleIDRef="0" pageBreak="%d" columnBreak="%d" merged="0">'
            '<hp:run charPrIDRef="%s">%s</hp:run></hp:p>') % (pp, pb, cb, cp, inner)


class Doc2(Doc):
    def __init__(self, tmpl):
        super().__init__(tmpl)
        x = self.x
        P = lambda k: strip_ls(x[self.pr[k][0]:self.pr[k][1]])
        self.T_PROB, self.T_PIC = P(5), P(7)
        self.T_BLANK = P(10)
        self.HDR = re.search(r'<hp:ctrl><hp:header .*?</hp:header></hp:ctrl>', x[self.pr[45][0]:self.pr[45][1]], re.S).group(0)
        self.heads = 0

    def head(self, text, cb=False, pb=False):
        self.heads += 1
        hdr = self.HDR.replace('2026학년도-2학년-2학기-중간-수학', '2026학년도-3학년-2학기-중간-수학') if self.heads == 2 else ''
        self.body.append(('<hp:p id="0" paraPrIDRef="%s" styleIDRef="0" pageBreak="%d" columnBreak="%d" merged="0">'
                          '<hp:run charPrIDRef="%s">%s<hp:t>%s</hp:t></hp:run></hp:p>') % (PP_HEAD, pb, cb, CP_HEAD, hdr, escape('[' + text + ']')))

    def label(self, text, cb=False):
        cp = CP_HEAD if text.startswith('[유사') else CP_SRC
        if cb and self.heads == 1:
            self.body.append(para('17', '10', '', cb=True)); self.body.append(para('17', '10', '')); self.body.append(para('17', '10', ''))
            cb = False
        self.body.append(para(PP_HEAD, cp, '<hp:t>%s</hp:t>' % escape(text), cb=cb))

    def line(self, markup, cp=None):
        self.body.append(para(PP_IND, cp or CP_BODY, content(markup) or '<hp:t/>'))

    def blank(self, n=1):
        for _ in range(n):
            self.body.append(para(PP_PROB, CP_BODY, ''))

    def problem(self, markup, ans=' '):
        self.en += 1
        s = self.T_PROB
        e = s.find('</hp:endNote></hp:ctrl>')
        head = s[:s.find('</hp:run>', e) + len('</hp:run>')]
        k1 = head.find('</hp:autoNum></hp:ctrl>') + len('</hp:autoNum></hp:ctrl>')
        k2 = head.rfind('</hp:run>', 0, head.find('</hp:subList>'))
        head = head[:k1] + (content(ans) if ans.strip() else '<hp:t> </hp:t>') + head[k2:]
        head = re.sub(r'<hp:endNote number="\d+"', '<hp:endNote number="%d"' % self.en, head)
        head = re.sub(r'<hp:autoNum num="\d+"', '<hp:autoNum num="%d"' % self.en, head)
        head = re.sub(r'instId="\d+"', 'instId="%d"' % next(_id), head)
        self.body.append(head + '<hp:run charPrIDRef="%s"><hp:t> </hp:t>%s</hp:run></hp:p>' % (CP_BODY, content(markup)))

    def choices(self, ch):
        assert len(ch) == 5, ch
        mk = [c if ('$' in c or re.search(r'[가-힣ㄱ-ㅎ]', c)) else '$%s$' % c for c in ch]

        def wid(c):
            v = re.sub(r'\b(rm|it|sqrt|bar|DEG|angle|TIMES|DIV)\b|[{}~` $]', '', c)
            w = sum(2 if re.match(r'[가-힣ㄱ-ㅎ]', t) else 1 for t in v.replace('over', ''))
            return w * 0.6 if 'over' in c else w
        nums = '①②③④⑤'
        if max(wid(c) for c in ch) > 9 or any('=' in c for c in ch):
            for n, c in zip(nums, mk):
                self.body.append(para(PP_CH1, CP_CH, content('%s %s' % (n, c))))
            return
        for grp in ((0, 1, 2), (3, 4)):
            inner = ('<hp:t> ' + TAB + '</hp:t>').join(content('%s %s' % (nums[i], mk[i])) for i in grp)
            self.body.append(para(PP_CH, CP_CH, inner))

    def box(self, lines, title=None, width=26000):
        inner = ''.join(para('6', CP_BODY, content(l) or '<hp:t/>') for l in ([('<%s>' % title)] if title else []) + lines)
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
        self.body.append(para(PP_IND, CP_BODY, tbl + '<hp:t/>'))

    def pic(self, path, maxw=26500, size=None):
        super().pic(path, maxw=maxw, size=size)
        s = self.body[-1]
        self.body[-1] = re.sub(r'^<hp:p [^>]*>', '<hp:p id="0" paraPrIDRef="%s" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">' % PP_PIC, s)

    def save(self, out, info):
        p0 = self.p0
        for a, b in info:
            p0 = p0.replace('<hp:t>%s</hp:t>' % a, '<hp:t>%s</hp:t>' % b)
        x = self.x
        # instruction line from template (para 3), replaced text
        instr = para('17', '32', '<hp:t>%s</hp:t>' % escape('※ 왼쪽 단은 세화여중3 학교프린트 문항, 오른쪽 단은 같은 유형의 기출문제입니다. 문항 번호를 따라 함께 풀어 보세요. (정답은 맨 뒤)'))
        self.body.insert(0, para('17', '10', ''))
        self.body.insert(1, para('17', '10', ''))
        self.body.insert(2, instr)
        self.body.insert(3, para(PP_PROB, CP_BODY, ''))
        self.body.append(para(PP_PROB, CP_BODY, '', pb=True))
        body = p0 + ''.join(self.body)
        self.files['Contents/section0.xml'] = (x[:self.pr[0][0]] + body + x[self.pr[-1][1]:]).encode('utf-8')
        self.files['Contents/content.hpf'] = self.hpf.encode('utf-8')
        write_hwpx(out, self.files, self.order)
        return out


def build(kind, total):
    KB.Doc = Doc2
    orig_save = Doc2.save
    nprint = 29 if kind == 'T' else 33
    import kc_spec_t, kc_spec_c
    spec = kc_spec_t.T if kind == 'T' else kc_spec_c.C
    nsim = sum(len([i for i in v if i['k'] not in KB.DROP]) for v in spec.values())
    title = '삼각비' if kind == 'T' else '원과 직선, 원주각'
    info = [('2026학년도 제2학기 중간고사', '2026학년도 제2학기 중간고사 대비'), ('시행일', '자료'), ('2026년 10월 1일 2교시', '학교프린트 유사 기출'),
            ('과목명', '단원'), ('(코드)', ''), ('수학(05)', title), ('2학년 1반 ~ 9반', '세화여중 3학년'),
            ('선택형 20문항/서답형 4문항', '프린트 %d문항/기출 %d문항' % (nprint, nsim)), (' / 6 &gt;', ' / %d &gt;' % total)]
    Doc2.save = lambda self, out, _t: orig_save(self, out, info)
    try:
        t = KB.build(kind)
    finally:
        KB.Doc = Doc; Doc2.save = orig_save
    return t


if __name__ == '__main__':
    k = sys.argv[1]
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    # kc_build.build creates Doc(E1) -> patch template path
    KB.W_EX_TEMPLATE = TPL
    t = build(k, total)
    out = os.path.join(W, 'kf_%s.hwpx' % k)
    os.replace(t, out)
    conv((out, os.path.join(W, 'kf_%s.pdf' % k), 'PDF'))
