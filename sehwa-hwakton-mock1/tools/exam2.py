import struct, zlib, io, sys
import olefile
import hwpbuild
from hwpbuild import (Para, TableSpec, parse_inline, build_para, recs, enc, ENNO, CFG, PS_SEG,
                      T_PHDR, T_PTXT, T_PCS, T_PLS, T_CTRL, T_EQ)
from cfb import clone_tree, write_cfb

FORM = '../w/form.hwp'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out2.hwp'

# ---- form style ids
P_Q, P_BLANK, P_DISP, P_CONT, P_RIGHT, P_CH, P_HDR, P_LABEL = 17, 1, 4, 18, 7, 19, 2, 13
C_BODY, C_NUM, C_CH = 7, 21, 22
WHITE = 24  # appended char shape (white copy of body text)
CFG.update({'en_ps': 17, 'en_st': 0, 'suffix': 0x2e})
PS_SEG.clear()
PS_SEG.update({0: (500, 29612), 1: (500, 29612), 2: (1000, 29312), 4: (0, 30612), 7: (500, 29612),
               10: (0, 26928), 13: (500, 29812), 17: (500, 29612), 18: (1500, 28612), 19: (1500, 29112)})


def Q(text, ans):
    return Para(P_Q, [('en', [('t', ans)], None), ('t', ' ')] + parse_inline(text), cs=C_BODY, cs_first=C_NUM, st=1)


def SQ(text, ans_eq):
    return Para(P_Q, [('en', [('eq', ans_eq)], None), ('t', ' ')] + parse_inline(text), cs=C_BODY, cs_first=C_NUM, st=1)


def EQ_(text, ans_eq):
    return Para(P_BLANK, [('en', [('eq', ans_eq)], None)] + parse_inline(text), cs=C_BODY, cs_first=WHITE, st=0)


def D(eq):
    return Para(P_DISP, [('eq', eq)], st=0)


def C(text, ps=None):
    return Para(P_CONT, parse_inline(text), st=0)


def RT(text, ps=None):
    return Para(P_RIGHT, parse_inline(text), st=0)


def BOX(lines):
    t = TableSpec([[[parse_inline(l) for l in lines]]], [27949], cell_ps=10, cell_cs=C_BODY)
    return Para(P_CONT, [('tbl', t)], st=0)


ZROWS = {0.5: '0.1915', 1.0: '0.3413', 1.5: '0.4332', 2.0: '0.4772', 2.5: '0.4938', 3.0: '0.4987'}


def ZTABLE(zs):
    rows = [[[('eq', 'z')], [('eq', 'rm P it (0 le Z le z)')]]]
    for z in zs:
        rows.append(['%.1f' % z, ZROWS[z]])
    t = TableSpec(rows, [4000, 8000], row_h=1300, cell_ps=4, cell_cs=C_BODY)
    return Para(P_DISP, [('tbl', t)], st=0)


def CH(a, b, c, d, e):
    l1 = [('t', '① '), ('eq', a), ('t', ' '), ('tab',), ('t', '② '), ('eq', b), ('t', ' '), ('tab',),
          ('t', '③ '), ('eq', c)]
    l2 = [('t', '④ '), ('eq', d), ('t', ' '), ('tab',), ('t', '⑤ '), ('eq', e)]
    return [Para(P_CH, l1, cs=C_CH, st=4), Para(P_CH, l2, cs=C_CH, st=4)]


def SC(x):
    return '[$%s$점]' % x


# ------------------------------------------------------------------ items
F = lambda a, b: '{%s} over {%s}' % (a, b)
items = []

# 1 (3.7) 교과서 조건부확률 중단원 5 변형
items.append([
    Q('두 사건 $A,~B$에 대하여', '④'),
    D('rm P it (A)= %s ,~ rm P it (B)= %s ,~ rm P it (A ^{C} cap B ^{C} )= %s' % (F(2, 3), F(1, 2), F(1, 6))),
    C('일 때, $rm P it (A|B)$의 값은? (단, $A ^{C}$은 $A$의 여사건이다.)'),
    RT(SC('3.7'), 28),
] + CH(F(1, 3), F(1, 2), F(3, 5), F(2, 3), F(3, 4)))

# 2 (3.7) 추정 중단원 1 변형
items.append([
    Q('숫자 $1,~1,~3,~3,~3,~3,~5,~5$가 하나씩 적힌 공 $8$개로 이루어진 모집단에서 크기가 $4$인 표본을 임의추출할 때, 표본평균 $bar X$에 대하여 $rm E it ( bar X )+ rm V it ( bar X )$의 값은? ' + SC('3.7'), '②'),
] + CH('3', F(7, 2), '4', F(9, 2), '5'))

# 3 (3.8) 추정 125쪽 (2) 변형 - 모비율 신뢰구간
items.append([
    Q('어느 도시의 고등학생 중에서 $400$명을 임의추출하여 조사하였더니 $80$명이 일주일에 세 번 이상 운동을 한다고 답하였다. 이 결과를 이용하여 구한 이 도시 고등학생 중 일주일에 세 번 이상 운동을 하는 학생의 비율 $p$에 대한 신뢰도 $99`%$의 신뢰구간이 $a le p le b$일 때, $b-a$의 값은? (단, $Z$가 표준정규분포를 따르는 확률변수일 때, $rm P it ( LEFT | Z RIGHT | le 2.58)=0.99$로 계산한다.) ' + SC('3.8'), '④'),
] + CH('0.0392', '0.0516', '0.0784', '0.1032', '0.2064'))

# 4 (3.9) 조건부확률 중단원 9 변형
items.append([
    Q('서로 독립인 두 사건 $A,~B$에 대하여 현수는 두 사건이 서로 독립임을 이용하여 $rm P it (A cup B)=0.76$을 얻었고, 은서는 두 사건이 서로 배반사건이라고 잘못 생각하여 $rm P it (A cup B)=0.9$를 얻었다. $rm P it (A)> rm P it (B)$일 때, $rm P it (A)- rm P it (B)$의 값은? ' + SC('3.9'), '⑤'),
] + CH('0.1', '0.2', '0.3', '0.4', '0.5'))

# 5 (4.0) 확률분포 중단원 7 변형
items.append([
    Q('확률변수 $X$에 대하여 확률변수 $Y=- %s X+4$라 할 때, $rm E it (Y)=-1$이고 $rm E it (Y ^{2} )=5$이다. $rm E it (X)+ rm V it (X)$의 값은? ' % F(1, 2) + SC('4.0'), '①'),
] + CH('26', '28', '30', '32', '34'))

# 6 (4.1) 조건부확률 중단원 7 변형
items.append([
    Q('상자 안에 크기와 모양이 같은 빨간색 볼펜 $n$자루와 파란색 볼펜 $3$자루가 들어 있다. 이 상자에서 수영이와 나은이가 차례대로 볼펜을 임의로 $1$자루씩 꺼낸다. 나은이가 꺼낸 볼펜이 파란색일 때, 수영이가 꺼낸 볼펜이 빨간색일 확률이 $%s$이다. 자연수 $n$의 값은? (단, 꺼낸 볼펜은 다시 넣지 않는다.) ' % F(5, 7) + SC('4.1'), '②'),
] + CH('4', '5', '6', '7', '8'))

# 7 (4.2) 확률분포 중단원 11 변형 - 이항분포의 정규근사
items.append([
    Q('확률변수 $X$의 확률질량함수가', '③'),
    D('rm P it (X=x)= {} _{400} rm C it _{x} LEFT ( %s RIGHT ) ^{x} LEFT ( %s RIGHT ) ^{400-x}' % (F(1, 5), F(4, 5))),
    RT('$(x=0,~1,~2,~ cdots ,~400)$', 28),
    C('일 때, $rm P it (72 le X le 92)$의 값을 아래 표준정규분포표를 이용하여 구한 것은? ' + SC('4.2')),
    ZTABLE([0.5, 1.0, 1.5, 2.0]),
] + CH('0.6247', '0.6826', '0.7745', '0.8185', '0.9104'))

# 8 (4.3) 확률분포 83쪽 생각 열기 변형 - 연속확률변수
items.append([
    Q('어느 식당에서 손님이 음식을 주문한 후 음식이 나올 때까지 걸리는 시간(단위: 분)을 확률변수 $X$라 할 때, $X$의 확률밀도함수 $f(x)$가 다음과 같다.', '③'),
    D('f(x)= cases{ %s x ~&(0 le x<10)# %s (40-x)~&(10 le x le 40)}' % (F(1, 200), F(1, 600))),
    Para(P_BLANK, [], st=0),
    C('음식이 나올 때까지 걸리는 시간이 $5$분 이상 $25$분 이하일 확률은? ' + SC('4.3')),
] + CH(F(5, 8), F(11, 16), F(3, 4), F(13, 16), F(7, 8)))

# 9 (4.5) 조건부확률 중단원 11 변형 - 독립시행 + 조건부확률
items.append([
    Q('수직선 위의 원점에 점 $rm P$가 있다. 동전 한 개를 던져서 앞면이 나오면 점 $rm P$를 양의 방향으로 $2$만큼, 뒷면이 나오면 음의 방향으로 $1$만큼 이동시킨다. 동전을 $6$번 던진 후 점 $rm P$의 좌표가 $6$ 이상이었을 때, 동전을 처음 던져서 앞면이 나왔을 확률은? ' + SC('4.5'), '①'),
] + CH(F(8, 11), F(17, 22), F(9, 11), F(19, 22), F(10, 11)))

# 10 (4.5) 확률 대단원 10 변형 - 표 + 조건부확률
survey = TableSpec([
    ['', '만족함', '만족하지 않음'],
    ['1학년', [('eq', 'a+20')], [('eq', '2b+10')]],
    ['2학년', [('eq', '3a-20')], [('eq', 'b+10')]],
], [5600, 7600, 9400], row_h=1400, cell_ps=4, cell_cs=C_BODY)
items.append([
    Q('다음 표는 어느 고등학교 $1$학년과 $2$학년 학생 $300$명을 대상으로 동아리 활동에 대한 만족도를 조사한 것이다. 이때 조사에 참여하지 않은 학생은 없다.', '②'),
    RT('(단위: 명)', 28),
    Para(P_DISP, [('tbl', survey)], st=0),
    C('이 조사에 참여한 학생 중에서 임의로 택한 한 명이 동아리 활동에 만족한 학생일 때, 이 학생이 $2$학년 학생일 확률은 $%s$이다. 이 조사에 참여한 학생 중에서 임의로 택한 한 명이 동아리 활동에 만족하지 않은 학생일 때, 이 학생이 $1$학년 학생일 확률은? (단, $a,~b$는 상수이다.) ' % F(5, 8) + SC('4.5'), 29),
] + CH(F(4, 7), F(9, 14), F(5, 7), F(11, 14), F(6, 7)))

# 11 (4.6) 추정 중단원 12 변형 - 표본평균의 분포 활용
items.append([
    Q('어느 공장에서 생산하는 쿠키 $1$개의 무게는 평균이 $20` rm g$, 표준편차가 $2` rm g$인 정규분포를 따른다고 한다. 이 공장에서는 쿠키를 $16$개씩 임의추출하여 한 상자에 담는데, 한 상자에 담긴 쿠키 $16$개의 무게의 합이 $308` rm g$ 미만이거나 $336` rm g$ 초과이면 불량품으로 판정한다. 이 공장에서 포장한 $10000$개의 상자 중 불량품으로 판정되는 상자의 개수의 기댓값을 아래 표준정규분포표를 이용하여 구한 것은? (단, 상자의 무게는 고려하지 않는다.) ' + SC('4.6'), '③'),
    ZTABLE([1.0, 1.5, 2.0, 2.5]),
] + CH('456', '668', '896', '1056', '1587'))

# 12 (4.7) 확률분포 중단원 12 변형 - 규칙에 따른 점수
items.append([
    Q('동전 한 개를 $4$번 던져서 나온 결과에 대하여 다음 규칙에 따라 얻은 점수를 확률변수 $X$라 할 때, $rm E it (X)+ rm V it (X)$의 값은? ' + SC('4.7'), '⑤'),
    BOX(['(가) 같은 면이 연속하여 나오지 않으면 $0$점으로 한다.',
         '(나) 같은 면이 연속하여 나오는 최대 횟수가 $2$이면 $1$점으로 한다.',
         '(다) 같은 면이 연속하여 나오는 최대 횟수가 $3$이면 $2$점으로 한다.',
         '(라) 같은 면이 연속하여 $4$번 나오면 $4$점으로 한다.']),
] + CH(F(7, 4), '2', F(9, 4), F(5, 2), F(11, 4)))

# 13 (4.8) 추정 119쪽 생각 열기 변형 - 신뢰구간의 길이
items.append([
    Q('정규분포 $rm N it (m,~4 ^{2} )$을 따르는 모집단에서 크기가 $n$인 표본을 임의추출하여 구한 표본평균이 $bar x _{1}$일 때, 모평균 $m$에 대한 신뢰도 $95`%$의 신뢰구간은 $a le m le b$이다. 같은 모집단에서 크기가 $4n$인 표본을 임의추출하여 구한 표본평균이 $bar x _{2}$일 때, 모평균 $m$에 대한 신뢰도 $99`%$의 신뢰구간은 $c le m le d$이다. $b-a=3.92$, $a=c$일 때, $bar x _{2} - bar x _{1}$의 값은? (단, $Z$가 표준정규분포를 따르는 확률변수일 때, $rm P it ( LEFT | Z RIGHT | le 1.96)=0.95,~ rm P it ( LEFT | Z RIGHT | le 2.58)=0.99$로 계산한다.) ' + SC('4.8'), '①'),
] + CH('0.67', '0.77', '0.87', '0.97', '1.07'))

# 14 (4.9) 확률분포 중단원 13 변형 - 두 정규분포
items.append([
    Q('두 확률변수 $X,~Y$는 각각 정규분포 $rm N it (16,~4 ^{2} )$, $rm N it (m,~4 ^{2} )$을 따르고, 두 확률변수 $X,~Y$의 확률밀도함수를 각각 $f(x),~g(x)$라 할 때, 다음 조건을 만족시킨다.', '④'),
    BOX(['(가) $f(24)=g(32)$', '(나) $rm P it (X ge 20)< rm P it (Y le 28)$']),
    C('$rm P it (18 le Y le 34)$의 값을 아래 표준정규분포표를 이용하여 구한 것은? ' + SC('4.9'), 29),
    ZTABLE([1.0, 1.5, 2.0, 2.5]),
] + CH('0.7745', '0.8351', '0.9104', '0.9270', '0.9772'))

# 15 (5.1) 조건부확률 중단원 14 변형 - 대진 + 조건부확률
items.append([
    Q('$1$반과 $2$반을 포함한 $6$개 반이 다음과 같은 방법으로 피구 경기를 한다.', '③'),
    BOX(['(가) $6$개 반을 임의로 $2$개 반씩 세 조로 나누어 조별로 $1$차 경기를 한다.',
         '(나) $1$차 경기에서 이긴 세 반 중 임의로 택한 한 반은 부전승으로 결승 경기에 오르고, 나머지 두 반이 $2$차 경기를 한다.',
         '(다) $2$차 경기에서 이긴 반과 부전승으로 오른 반이 결승 경기를 한다.']),
    C('$1$반과 $2$반이 경기를 하였을 때, 그 경기가 결승 경기였을 확률은? (단, 한 경기에서 각 반이 이길 확률은 서로 같고, 비기는 경우는 없다.) ' + SC('5.1'), 29),
] + CH(F(1, 10), F(1, 6), F(1, 5), F(1, 4), F(1, 3)))

# 16 (5.2) 2025 세화여고 기말 11번 변형 - 함수 + 조건부확률
items.append([
    Q('집합 $X= LEFT { 1,~2,~3,~4,~5 RIGHT }$에 대하여 $X$에서 $X$로의 모든 함수 중에서 임의로 선택한 한 함수를 $f$라 하자. $f(1)+f(2)=f(3)$일 때, 집합 $X$의 어떤 원소 $a$에 대하여 $f(a)=4$일 확률은 $%s$이다. $p+q$의 값은? (단, $p$와 $q$는 서로소인 자연수이다.) ' % F('q', 'p') + SC('5.2'), '⑤'),
] + CH('34', '36', '38', '40', '42'))

# ---- short answers
short = []
# 단답1 (3.8) 추정 중단원 13 변형
short.append([
    SQ('표준편차가 $sigma$인 정규분포를 따르는 모집단에서 크기가 $n$인 표본을 임의추출하여 구한 모평균 $m$에 대한 신뢰도 $95`%$의 신뢰구간이 $90.2 le m le 109.8$이었다. 같은 표본을 이용하여 구한 모평균 $m$에 대한 신뢰도 $99`%$의 신뢰구간에 속하는 자연수의 개수를 구하시오. (단, $Z$가 표준정규분포를 따르는 확률변수일 때, $rm P it ( LEFT | Z RIGHT | le 1.96)=0.95,~ rm P it ( LEFT | Z RIGHT | le 2.58)=0.99$로 계산한다.) ' + SC('3.8'), '25'),
])
# 단답2 (4.0) 2025 세화여고 기말 13번 변형 - 표본평균의 분포
short.append([
    SQ('모집단의 확률변수 $X$가 갖는 값은 $0,~1,~2$이다. 이 모집단에서 크기가 $2$인 표본을 임의추출하여 구한 표본평균을 $bar X$라 할 때, $rm P it ( bar X =2)= %s$, $rm E it (4 bar X )=3$이다. $rm P it ( bar X =1)= %s$일 때, $p+q$의 값을 구하시오. ' % (F(1, 16), F('q', 'p')), '21'),
    RT('(단, $p$와 $q$는 서로소인 자연수이다.) ' + SC('4.0'), 33),
])
# 단답3 (4.4) 추정 대단원 14 변형 - 모비율 신뢰구간의 길이
short.append([
    SQ('어느 지역에서 공원 조성을 희망하는 주민의 비율을 알아보기 위하여 이 지역 주민 중에서 $900$명을 임의추출하여 조사하였더니 $n$명이 공원 조성을 희망하였다. 이 결과를 이용하여 구한 모비율 $p$에 대한 신뢰도 $99`%$의 신뢰구간이 $a le p le b$일 때, $b-a ge 0.0688$을 만족시키는 자연수 $n$의 개수를 구하시오. (단, $Z$가 표준정규분포를 따르는 확률변수일 때, $rm P it ( LEFT | Z RIGHT | le 2.58)=0.99$로 계산한다.) ' + SC('4.4'), '541'),
])
# 단답4 (4.6) 2025 세화여고 기말 서답형 7번 변형 - 독립
short.append([
    SQ('어느 대학교 면접장에 모인 $n$명의 학생들의 수험번호를 확인해 보니 수험번호가 $20$ 이하인 학생이 $16$명이고, 수험번호가 $4$의 배수인 학생이 $8$명이었다. 이 $n$명의 학생 중에서 임의로 한 명을 택할 때, 택한 학생의 수험번호가 $20$ 이하인 사건과 $4$의 배수인 사건이 서로 독립인 경우가 존재하도록 하는 모든 자연수 $n$의 값의 합을 구하시오. ', '224'),
    RT('(단, 학생들의 수험번호는 서로 다른 자연수이다.) ' + SC('4.6'), 33),
])
# 단답5 (5.2) 2025 세화여고 기말 서답형 8번 변형 - 독립시행
short.append([
    SQ('한 변의 길이가 $1$인 정육각형 $rm ABCDEF$의 꼭짓점 $rm A,~B,~C,~D,~E,~F$가 시계 방향으로 차례로 놓여 있고, 점 $rm P$는 이 정육각형의 변을 따라 움직인다. 한 개의 주사위를 한 번 던져 홀수의 눈이 나오면 점 $rm P$를 시계 방향으로 $3$만큼, 짝수의 눈이 나오면 시계 반대 방향으로 $2$만큼 이동시키는 시행을 한다. 꼭짓점 $rm A$에 있던 점 $rm P$가 이 시행을 $10$번 반복한 후 꼭짓점 $rm B$에 있을 확률이 $p times LEFT ( %s RIGHT ) ^{10}$일 때, 자연수 $p$의 값을 구하시오. ' % F(1, 2) + SC('5.2'), '130'),
])
# 서술형1 (8) 추정 대단원 11 변형 - 두 표본평균
essay = [
    EQ_('어느 공장에서 생산되는 $rm A$ 제품의 무게는 정규분포 $rm N it (m,~3 ^{2} )$을 따르고, $rm B$ 제품의 무게는 정규분포 $rm N it (2m,~6 ^{2} )$을 따른다고 한다. 이 공장에서 생산된 $rm A$ 제품 중에서 임의추출한 $9$개의 무게의 표본평균을 $bar X$, $rm B$ 제품 중에서 임의추출한 $16$개의 무게의 표본평균을 $bar Y$라 하자.', '12'),
    D('rm P it ( bar X ge k)= rm P it ( bar Y le k)=0.0228'),
    C('일 때, $m+k$의 값을 구하는 풀이 과정과 답을 쓰시오. (단, $Z$가 표준정규분포를 따르는 확률변수일 때, $rm P it (0 le Z le 2)=0.4772$로 계산한다.) [$8$점]', 34),
]



# ------------------------------------------------------------------ assemble on the form
o = olefile.OleFileIO(FORM)
R = [list(r) for r in recs(zlib.decompress(o.openstream('BodyText/Section0').read(), -15))]


def find_para(text, start=0):
    for i in range(start, len(R)):
        if R[i][0] == T_PTXT and R[i][1] == 1:
            from hwpx_text import plain
            if plain(R[i][2]).lstrip().startswith(text):
                return i - 1  # PHDR index
    raise KeyError(text)


def para_end(i):
    lvl = R[i][1]
    j = i + 1
    while j < len(R) and R[j][1] > lvl:
        j += 1
    return j


i_start = find_para('[시작]')
i_hdr = find_para('‣ 서술형')
i_label = find_para('서술형1.')
i_sd = find_para('[서답형]')
i_end = find_para('※ 답안지')

prefix = R[:i_start]
seo_label = R[i_label:para_end(i_label)]
tail_blanks = R[para_end(i_sd):i_end]
suffix = R[i_end:]
hdr_orig = R[i_hdr]


def retext(records, mapping, black=None):
    """exact-text replacement in PTXT records; fixes nch and optionally char shapes."""
    for k, (t, l, d) in enumerate(records):
        if t != T_PTXT:
            continue
        s = d.decode('utf-16le', 'ignore')[:-1]
        if s in mapping:
            new = mapping[s]
            records[k][2] = (new + '\r').encode('utf-16le')
            h = bytearray(records[k - 1][2])
            flag = struct.unpack_from('<I', h, 0)[0] & 0x80000000
            struct.pack_into('<I', h, 0, (len(new) + 1) | flag)
            # make the paragraph a single black run
            pcs = records[k + 1][2]
            runs = [struct.unpack_from('<II', pcs, x) for x in range(0, len(pcs), 8)]
            cs = runs[-1][1]
            if black and any(r[1] in black for r in runs):
                cs = black.get(runs[0][1], runs[-1][1])
            records[k + 1][2] = struct.pack('<II', 0, cs)
            struct.pack_into('<H', h, 12, 1)
            records[k - 1][2] = bytes(h)


NPAGES = '7'
retext(prefix, {'2026학년도-1학년-공통수학2': '2026학년도-1학년-확률과통계', '공통수학2': '확률과통계', '03': '06',
                '14문항': '16문항', '67점': '70점', '4문항': '5문항', '21점': '22점', '2문항': '1문항',
                '12점': '8점', '8': NPAGES}, black={17: 4, 18: 0})
retext(suffix, {'8': NPAGES}, black={17: 4, 18: 0})

body = []
v = [0]


def emit(p, split=0):
    if split:
        p.split = split
    p.vpos = v[0]
    body.extend(build_para(p, 0))
    v[0] += p.height()


def blank():
    emit(Para(P_BLANK, [], st=0))


def emit_item(paras, split=0):
    for k, p in enumerate(paras):
        emit(p, split if k == 0 else 0)


def fill_to(y):
    while v[0] + 1600 <= y:
        blank()


MID = 45300
starts = [14067, 4533]
for k in range(0, 16, 2):
    col = k // 2
    v[0] = starts[col] if col < 2 else 0
    emit_item(items[k], 0 if col == 0 else 8)
    fill_to(MID - 200)
    v[0] = MID
    emit_item(items[k + 1])

# short-answer block: header like the form's section header, numbers continue by endnote
v[0] = 0
h = Para(P_HDR, [('t', '‣ 단답형 '), ('eq', '17`'), ('t', '번부터 '), ('eq', '21`'),
                 ('t', '번까지는 OMR 카드에 답을 표기하시오.')], st=0)
h.pcs = [(0, 13), (1, 2)]
emit(h, 8)
blank()
emit_item(short[0])
fill_to(MID - 200)
v[0] = MID
emit_item(short[1])
v[0] = 0
emit_item(short[2], 8)
fill_to(MID - 200)
v[0] = MID
emit_item(short[3])
v[0] = 0
emit_item(short[4], 8)

# essay page: form header (page break kept), label, question at [서답형]
v[0] = 0
sh = Para(P_HDR, [('t', '‣ 서술형 '), ('eq', '1`'), ('t', '번은 풀이 과정과 답을 모두 쓰시오.')], st=0)
sh.pcs = [(0, 13), (1, 2)]
emit(sh, 4)
blank()
body.extend(seo_label)
v[0] = 4000
emit_item(essay)
# drop as many of the form's trailing blank lines as the question is taller than one line
extra = max(0, int((v[0] - 4000) / 1600) - 1)
blank_groups = []
j = 0
while j < len(tail_blanks):
    k = j + 1
    while k < len(tail_blanks) and tail_blanks[k][1] > 0:
        k += 1
    blank_groups.append(tail_blanks[j:k])
    j = k
for g in blank_groups[extra:]:
    body.extend(g)

out_body = prefix + body + suffix
# answer key (endnotes) on its own page, as in the real exam: page break on the last paragraph
last = max(k for k, r in enumerate(out_body) if r[0] == T_PHDR and r[1] == 0)
d = bytearray(out_body[last][2]); d[11] = 4; out_body[last][2] = bytes(d)
sec = enc(out_body)

# DocInfo: white char shape, endnote suffix '.', caret reset
di = [list(r) for r in recs(zlib.decompress(o.openstream('DocInfo').read(), -15))]
cs_idx = [k for k, r in enumerate(di) if r[0] == 21]
white = bytearray(di[cs_idx[7]][2])
white[52:56] = bytes.fromhex('ffffff00')
di.insert(cs_idx[-1] + 1, [21, di[cs_idx[-1]][1], bytes(white)])
assert len(cs_idx) == WHITE
for r in di:
    if r[0] == 17:
        d = bytearray(r[2]); n = struct.unpack_from('<i', d, 36)[0]; struct.pack_into('<i', d, 36, n + 1); r[2] = bytes(d)
    if r[0] == 16:
        d = bytearray(r[2]); d[14:26] = b'\0' * 12; r[2] = bytes(d)
# endnote shape in the section definition (2nd FOOTNOTE_SHAPE record)
fn = [k for k, r in enumerate(out_body) if r[0] == 74]
d = bytearray(out_body[fn[1]][2]); struct.pack_into('<H', d, 8, 0x2e); out_body[fn[1]][2] = bytes(d)
sec = enc(out_body)


def deflate(b):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return c.compress(b) + c.flush()


prv = []
for t, l, d in out_body:
    if t == T_PTXT:
        s = ''.join(ch for ch in d.decode('utf-16le', 'ignore') if ord(ch) >= 32 or ch == '\r')
        prv.append(s.replace('\r', '\r\n'))
prvtext = ''.join(prv)[:1000].encode('utf-16le')
from PIL import Image
im = Image.new('RGB', (248, 350), 'white'); bio = io.BytesIO(); im.save(bio, 'PNG')
root = clone_tree(o, {('BodyText', 'Section0'): deflate(sec), ('DocInfo',): deflate(enc(di)),
                      ('PrvText',): prvtext, ('PrvImage',): bio.getvalue()})
write_cfb(OUT, root)
print('written', OUT, 'records', len(out_body), 'endnotes', ENNO[0], 'dropped blanks', extra)
