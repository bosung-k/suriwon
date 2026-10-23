from fractions import Fraction as F
from itertools import product
import sympy as sp
# EBS07-02
a,b=sp.symbols('a b')
E=a+2*b; E2=a+4*b
print('EBS07-02',sp.solve([a+b-sp.Rational(2,3), E2-E**2-sp.Rational(17,36)],[a,b]))
# 조건부-100: P(A∪B)=1/3, P(Ac∪Bc)=5/6 -> P(AB)=1/6 ; pa+pb-papb=1/3 -> pa+pb=1/2, papb=1/6 ; roots of ax^2+bx+1: sum=-b/a, prod=1/a
print('조건부-100 a=6,b=-3 ->',6-3)
# EBS04-32
n=sp.symbols('n',positive=True,integer=True)
print('EBS04-32',sp.solve(sp.Eq(n*(n+4)*14,3*(2*n+4)*(2*n+3)),n))
# 조건부-140: A,B,C draw from 4W2B, P(A white | C white)
def draws(W,B,k):
    from itertools import permutations
    balls=['W']*W+['B']*B
    tot=0;out=[]
    for p in permutations(range(W+B),k): out.append(tuple(balls[i] for i in p))
    return out
D=draws(4,2,3)
cw=[d for d in D if d[2]=='W']; print('조건부-140',F(sum(1 for d in cw if d[0]=='W'),len(cw)))
# EBS06-02: f=-ax+3a on[0,3), a/3 x - a on [3,5]; total area: 9a/2 + (from 3 to5) a/3*(x-3) area = a/3*2*2/2=2a/3
x=sp.symbols('x');A=sp.symbols('A',positive=True)
tot=sp.integrate(-A*x+3*A,(x,0,3))+sp.integrate(A/3*x-A,(x,3,5)); Av=sp.solve(tot-1,A)[0]
p=sp.integrate(-Av*x+3*Av,(x,2,3))+sp.integrate(Av/3*x-Av,(x,3,4)); print('EBS06-02',p)
# 확률분포-124: a(1-x) on[0,1), b(x-1) on[1,2]; a/2+b/2=1, P(1..2)=b/2=a/6
aa,bb=sp.symbols('aa bb'); s=sp.solve([aa/2+bb/2-1,bb/2-aa/6],[aa,bb]); print('확률분포-124',s, s[aa]-s[bb])
# 조건부-127: +2/-1, 9 tosses, |pos|=3: 2h-(9-h)=3h-9 =±3 -> h=4 or 2
from math import comb
print('조건부-127',F(comb(9,4)+comb(9,2),512))
# 시너지05-045: stop when x or y first hits 3. Given y hits 3 first, P(x==1)
from functools import lru_cache
tot=F(0);good=F(0)
def walk(x,y,p):
    global tot,good
    if y==3:
        tot+=p; good+= p if x==1 else 0; return
    if x==3: return
    walk(x+1,y,p/2); walk(x,y+1,p/2)
walk(0,0,F(1)); print('시너지05-045',good/tot)
# 05-058: 6 throws ±1 p=1/2, at 2: 4 up
print('05-058',F(comb(6,4),64))
# 조건부-083: same color, white: a(100-2a)/[a(100-2a)+(100-a)2a]=2/9
for av in range(1,50):
    w=av*(100-2*av); bl=(100-av)*2*av
    if F(w,w+bl)==F(2,9): print('조건부-083 a=',av)
# 06-047
def score(seq):
    return sum(1 if seq[i]==seq[i-1] else 2 for i in range(1,len(seq)))
v=[score(s) for s in product('HT',repeat=4)]; print('06-047',F(sum(v),16))
# 확률분포-177: 6 throws, even count k, odd 6-k: X=k^2-(6-k)^2 = 12k-36 -> E=12*3-36=0?? "제곱의 차" maybe absolute
Ek=F(0);Ea=F(0)
for k in range(7):
    pr=F(comb(6,k),64); Ek+=pr*(k*k-(6-k)**2); Ea+=pr*abs(k*k-(6-k)**2)
print('177 signed',4*Ek,'abs',4*Ea)
# 193: f(12)=g(26): 12-10=±(26-m): m=24 or 28 ; P(Y>=26)>=0.5 -> m>=26 -> m=28; P(Y<=20)=P(Z<=-2)=0.0228
print('193 -> 0.0228 ②')
# 05-072: A wins set 2/3; wins match; P(win within 4 | win)
p=F(2,3);q=1-p
w3=p**3; w4=comb(3,2)*p**3*q; w5=comb(4,2)*p**3*q**2
print('05-072',(w3+w4)/(w3+w4+w5), 'P(win)',w3+w4+w5)
# 034: X 10,20,30 probs 1/2,a,1/2-a; E=18 -> 5+20a+15-30a=18 -> a=0.2 ; P(Xbar=20): (10,30),(30,10),(20,20)
a_=F(1,5); print('034',2*F(1,2)*(F(1,2)-a_)+a_*a_)
# 조건부-106: girls 20 (12 glasses), boys 18+x; total 38+x, glasses 30: indep: 12/(38+x) = 20/(38+x)*30/(38+x)
for xx in range(0,40):
    if F(12,38+xx)==F(20*30,(38+xx)**2): print('106 x=',xx)
# 조건부-144
tot=0
for nn in range(1,17):
    divs=[d for d in range(1,17) if nn%d==0]
    pa=F(8,16);pb=F(len(divs),16);pab=F(sum(1 for d in divs if d%2==0),16)
    if pab==pa*pb: tot+=nn
print('144',tot)
# EBS04-34: boys 1학년 x+2, 2학년 8; girls 1학년 10, 2학년 x
for xx in range(1,30):
    N=xx+2+8+10+xx; boys=xx+10; g2=8+xx
    if F(8,N)==F(boys*g2,N*N): print('EBS04-34 x=',xx)
# 05-065 square: even ccw2, odd cw1; 6 throws; A->B. positions mod4, A=0, B=1 clockwise? define cw +1. ccw2 = -2
def poly(n,steps,target,moves):
    c=F(0)
    for s in product(moves,repeat=steps):
        if sum(m for m,_ in s)%n==target: 
            pr=F(1)
            for _,p in s: pr*=p
            c+=pr
    return c
print('05-065 B cw',poly(4,6,1,[(-2,F(1,2)),(1,F(1,2))]),'B ccw',poly(4,6,3,[(-2,F(1,2)),(1,F(1,2))]))
print('05-067',poly(4,4,0,[(1,F(2,3)),(-1,F(1,3))]))
print('05-066',poly(5,10,0,[(2,F(1,2)),(1,F(1,2))]))
