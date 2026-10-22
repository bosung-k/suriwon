"""변형·신작 문항의 정답을 계산으로 재확인 (첫 풀이와 별도 경로).  python verify_variants.py"""
import itertools, math
from fractions import Fraction as F
import sympy as sp

R = {}
x = sp.symbols('x', real=True)

# V1-1  F25-서5 변형: (가) x notin X => x^2 != x+2, (나) x in X => 4x^4-11x^3 = ax^2+bx+c, sum(X)=2
a, b, c = sp.symbols('a b c')
poly = sp.expand(4 * (x + 1) * (x - 2) * (x - 1) * (x - F(3, 4)))
# 4x^4-11x^3 - (a x^2 + b x + c) = poly  ->  match
sol = sp.solve(sp.Poly(4 * x**4 - 11 * x**3 - a * x**2 - b * x - c - poly, x).all_coeffs(), [a, b, c])
R['V1-1 a+b+c'] = sol[a] + sol[b] + sol[c]
# uniqueness: X must contain -1,2 ; roots of quartic have sum 11/4 ; X subset of roots, sum 2
# brute: 3rd root t with -1+2+t=2 -> t=1 ; 4 roots sum 11/4 -> X cannot be all 4 roots.
R['V1-1 roots'] = sp.solve(poly, x)

# V1-2  U={1..300}: n((A4 ∪ A6) - A9)
R['V1-2'] = sum(1 for n in range(1, 301) if (n % 4 == 0 or n % 6 == 0) and n % 9 != 0)

# V1-3  (m,n): A_m∩A_n = A_36 and A_m∪A_n ⊂ A_6
R['V1-3'] = sum(1 for m in range(1, 200) for n in range(1, 200)
               if math.lcm(m, n) == 36 and m % 6 == 0 and n % 6 == 0)

# V1-4  U={1..9}, A={1..5}, B={4,5,6,7}: X∪A=A∪B, X∩(A-B)≠∅, n(X) even
U = range(1, 10); A = {1, 2, 3, 4, 5}; B = {4, 5, 6, 7}
cnt = 0
for r in range(10):
    for X in itertools.combinations(U, r):
        X = set(X)
        if X | A == A | B and X & (A - B) and len(X) % 2 == 0:
            cnt += 1
R['V1-4'] = cnt

# V1-5  A△B={1,3,5,7}, B△C={2,3,6,7} -> sum(A△C)
R['V1-5'] = sum({1, 3, 5, 7} ^ {2, 3, 6, 7})

# V2-1  p:-1<=x<=4, q:x>=k^2+k-4, r:x>2k+10 ; p->q false and ~r->~p false ; integer k<=10
def false_pq(k):  # exists x in [-1,4] with x < k^2+k-4
    return -1 < k * k + k - 4
def false_pr(k):  # p->r false: exists x in [-1,4] with x <= 2k+10
    return -1 <= 2 * k + 10
R['V2-1'] = [k for k in range(-100, 11) if false_pq(k) and false_pr(k)]

# V2-2  p:(x-2)(x-(sqrt(n+5)-1))<0  q:(x-5)(x-30/(n+1))<0 ; P⊂Q true ; natural n
def P_sub_Q(n):
    s = math.sqrt(n + 5) - 1; t = 30 / (n + 1)
    p = (min(2, s), max(2, s)); q = (min(5, t), max(5, t))
    if abs(p[0] - p[1]) < 1e-12:
        return True
    if abs(q[0] - q[1]) < 1e-12:
        return False
    return q[0] <= p[0] + 1e-12 and p[1] <= q[1] + 1e-12
ns = [n for n in range(1, 2000) if P_sub_Q(n)]
R['V2-2 n'] = ns; R['V2-2 sum'] = sum(ns)

# V2-4  빈칸: m=2k-1,n=2l -> m^2+mn+n^2=2f+1 ; m=2k-1,n=2l-1 -> 2g+1 ; f(2,3)+g(2,3)
k, l = sp.symbols('k l')
f1 = sp.expand(((2*k-1)**2 + (2*k-1)*(2*l) + (2*l)**2 - 1) / 2)
g1 = sp.expand(((2*k-1)**2 + (2*k-1)*(2*l-1) + (2*l-1)**2 - 1) / 2)
R['V2-4 f'] = f1; R['V2-4 g'] = g1; R['V2-4'] = f1.subs({k: 2, l: 3}) + g1.subs({k: 2, l: 3})

# V2-6  x>3: x+25/(x-3) min m at x=a -> m+a
t = sp.symbols('t', positive=True)
expr = x + 25 / (x - 3)
crit = [r for r in sp.solve(sp.diff(expr, x), x) if r > 3]
R['V2-6'] = (crit, expr.subs(x, crit[0]) + crit[0])

# V2-7  '어떤 실수 x, x^2-ax+a+3<=0' 거짓 -> 정수 a 개수
R['V2-7'] = [aa for aa in range(-50, 50) if aa * aa - 4 * (aa + 3) < 0]

# V2-8  p:[2,4], q:|x-a|<=3, r:|x-b|<=5 ; P⊂Q and Q⊂R ; integer pairs (a,b)
R['V2-8'] = sum(1 for aa in range(-30, 30) for bb in range(-30, 30)
                if aa - 3 <= 2 and aa + 3 >= 4 and bb - 5 <= aa - 3 and aa + 3 <= bb + 5)

# V3-1  X={1..5} bijections with f^6=I and f(5)!=5
def compose_pow(p, e):
    q = list(range(len(p)))
    for _ in range(e):
        q = [p[i] for i in q]
    return q
cnt = 0
for p in itertools.permutations(range(5)):
    if compose_pow(p, 6) == list(range(5)) and p[4] != 4:
        cnt += 1
R['V3-1'] = cnt

# V3-2  f=ax+b, g=2x-1, f∘g=g∘f, f(3)=7 -> f(10)
aa, bb = sp.symbols('aa bb')
s2 = sp.solve([sp.Eq(-aa + bb, 2 * bb - 1), sp.Eq(3 * aa + bb, 7)], [aa, bb])
R['V3-2'] = 10 * s2[aa] + s2[bb]

# V3-6  f=|2x-4|+ax+3 bijection R->R ; integer |a|<=10
R['V3-6'] = [aa for aa in range(-10, 11) if (2 + aa) * (aa - 2) > 0]

# V4-1  y=2500/(x-7)+5 (x>7): PQ+PR min -> y of P
expr = x + 2500 / (x - 7) + 5
crit = [r for r in sp.solve(sp.diff(expr, x), x) if r > 7]
R['V4-1'] = (crit, 2500 / (crit[0] - 7) + 5)

# V4-3  y=(kx+2)/(x-1), y=(3x-1)/(x+k): asymptote rectangle area 21, k>0
kk = sp.symbols('kk', positive=True)
R['V4-3'] = sp.solve(sp.Eq((1 + kk) * sp.Abs(kk - 3), 21), kk)

# V4-4  f(x)=90-2400/(x+20) on (10,60): #natural x with f^2(x)<=50<=f^3(x)
fF = lambda v: F(90) - F(2400) / (v + 20)
cnt = 0
for n in range(11, 60):
    v = F(n); v1 = fF(v); v2 = fF(v1); v3 = fF(v2)
    if v2 <= 50 <= v3:
        cnt += 1
R['V4-4'] = (fF(F(10)), fF(F(60)), cnt)

# V5-1  f = sqrt(8-4x)+a (x<=2), 1/(2-x)+a^2-2 (x>2) bijection R->R, a>0 ; b=a ; g(y),h(y) inverse branches
R['V5-1 a'] = [r for r in sp.solve(sp.Eq(t**2 - 2, t), t)]
y = sp.symbols('y')
g_y = sp.solve(sp.Eq(sp.sqrt(8 - 4 * x) + 2, y), x)       # branch x<=2 (y>=2)
h_y = sp.solve(sp.Eq(1 / (2 - x) + 2, y), x)              # branch x>2 (y<2)
R['V5-1 g,h'] = (g_y, h_y)
R['V5-1'] = 2 + (2 - (4 - 2)**2 / 4) + (2 + 1 / (2 - 1))

# V5-2  f(x)=max{ sqrt(kx-k^2)+4k/3 | 0<k<=x } ; n < f(30)+f^-1(60)
def fmax(X, N=200000):
    best = -1
    for i in range(1, N + 1):
        kv = X * i / N
        v = math.sqrt(max(kv * X - kv * kv, 0)) + 4 * kv / 3
        best = max(best, v)
    return best
R['V5-2 f(30)'] = fmax(30)          # expect 45
R['V5-2 f(40)'] = fmax(40)          # expect 60 -> f^-1(60)=40
R['V5-2 n'] = math.ceil(45 + 40) - 1

# V5-3  y=-sqrt(2x-4)+3 inverse
R['V5-3 inverse'] = sp.solve(sp.Eq(-sp.sqrt(2 * y - 4) + 3, x), y)

# V5-5  f=sqrt(4x-8)+2 and inverse : distance^2 of intersection points
pts = sp.solve(sp.Eq(sp.sqrt(4 * x - 8) + 2, x), x)
R['V5-5'] = (pts, 2 * (pts[1] - pts[0])**2)

# V5-6  sqrt(x+4) = x/2 + k two distinct points : [alpha, beta)
def nsol(kv):
    # solve sqrt(x+4)=x/2+kv  <->  x+4=(x/2+kv)^2, x/2+kv>=0, x>=-4
    sols = sp.solve(sp.Eq(x + 4, (x / 2 + kv)**2), x)
    return len([s for s in sols if s.is_real and s >= -4 and s / 2 + kv >= 0])
R['V5-6'] = [(kv, nsol(kv)) for kv in [F(19, 10), 2, F(21, 10), F(12, 5), F(5, 2), F(26, 10)]]

# external checks
# OT23M 함수: f=4x-x^2, f^4=f^3, x!=0 -> product of solutions
fx = 4 * x - x**2
f3 = fx.subs(x, fx); f3 = fx.subs(x, f3)
f4 = fx.subs(x, f3)
solset = set(sp.solve(sp.Eq(f4, f3), x)) - {0}
R['OT23M f4=f3 product'] = sp.nsimplify(sp.prod(list(solset)))
R['OT23M count'] = len(solset)

for kk_, vv in R.items():
    print(kk_, '=>', vv)
