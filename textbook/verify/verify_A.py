"""Brute-force / symbolic checks for Part A (직렬·병렬 융합) answers."""
from itertools import combinations, product, permutations
from fractions import Fraction as F
import sympy as sp

x = sp.symbols('x', real=True)
R = {}

# ---- S1: q->p, q->~p both false; p: x^2-2x-8<=0 ([-2,4]), q: |x-k|<=2
ks = [k for k in range(-20, 21) if (k - 2 < -2 or k + 2 > 4) and (k + 2 >= -2 and k - 2 <= 4)]
m = sum(ks); R['S1-1'] = (ks, m)
N = 2 * m + 4
best = None
for a in range(1, N + 1):
    for b in range(1, N + 1):
        U = range(1, N + 1)
        A = {u for u in U if u % a == 0}
        B = {u for u in U if b % u == 0}
        if {3, 6} <= (A & B) and len(B - A) == 2:
            s = sum(A - B)
            best = s if best is None else min(best, s)
R['S1-2 (P2, expect 27)'] = best

# ---- S2: x>1, 2x+8/(x-1) min
v = sp.minimum(2 * x + 8 / (x - 1), x, sp.Interval.open(1, sp.oo)); R['S2-1'] = v
N = int(v) + 5
P = {p for p in range(2, N + 1) if all(p % d for d in range(2, p))}
U = set(range(1, N + 1))
cnt = 0
for mask in range(1 << N):
    X = {i + 1 for i in range(N) if mask >> i & 1}
    if len(X - P) * len(X | (U - P)) != 11:
        continue
    M = 1
    for e in X: M *= e
    nd = 1
    for pr, ex in sp.factorint(M).items(): nd *= ex + 1
    if nd == 16:
        cnt += 1
R['S2-2 (P10, expect 38)'] = cnt

# ---- S3: y=(ax+1)/(x+b) symmetric w.r.t. y=x+2 and y=-x+6 -> center (2,4)
a, b = 4, -2
R['S3-1 ab'] = a * b

# ---- S4: p: |x-1|<=a, q: -1<=x<=5, p sufficient for q, natural a count
R['S4-1'] = sum(1 for a_ in range(1, 50) if 1 - a_ >= -1 and 1 + a_ <= 5)
k = R['S4-1']
def f4(t): return 2 * t + k if t < k else t * t - 7 * t + 8 * k
sols = set()
# f(f(a)) = f(a): let b=f(a), need f(b)=b
fixed = []
for expr, cond in [(2 * x + k - x, lambda r: r < k), (x * x - 7 * x + 8 * k - x, lambda r: r >= k)]:
    for r in sp.solve(expr, x):
        if r.is_real and cond(float(r)): fixed.append(r)
for bval in fixed:
    for expr, cond in [(2 * x + k - bval, lambda r: r < k), (x * x - 7 * x + 8 * k - bval, lambda r: r >= k)]:
        for r in sp.solve(expr, x):
            if r.is_real and cond(float(r)): sols.add(sp.nsimplify(r))
R['S4-2 (P20, expect 6)'] = (sorted(sols, key=float), sum(sols))

# ---- S5: f(2x+1)=6x+1 -> f^{-1}(19)
t = sp.symbols('t')
ft = sp.expand((6 * ((t - 1) / 2) + 1))
kk = int(sp.solve(ft - 19, t)[0]); R['S5-1'] = kk
cnt = 0
for A_ in range(-100, 100):
    s1, s2 = A_ + kk, -A_ + 5
    # increasing or decreasing on both pieces with matching jump
    l1 = s1 * 1 - 1          # left limit at 1
    r1 = s2 * 1 + 2 * A_ + 1  # value at 1
    ok = (s1 > 0 and s2 > 0 and l1 <= r1) or (s1 < 0 and s2 < 0 and l1 >= r1)
    cnt += ok
R['S5-2 (P22, expect 11)'] = cnt

# ---- S6: exists x: x^2-(a-3)x+4<0, natural a min
R['S6-1'] = min(a_ for a_ in range(1, 50) if (a_ - 3) ** 2 - 16 > 0)
A_, B_ = sp.symbols('A B', real=True)
# P29: f=a/x+b, |f| meets y=2 at exactly one point; f^{-1}(2)=f(2)-1
sol = []
for bb in [2, -2]:   # |f|=2 one point => asymptote y=b is y=2 or y=-2 (one branch hits other level once)
    # f(x) = 2 has x = a/(2-b); f^{-1}(2) = a/(2-b) must equal f(2)-1 = a/2+b-1
    if bb == 2:
        continue  # f=2 impossible, then f^{-1}(2) undefined
    aa = sp.symbols('aa')
    for r in sp.solve(sp.Eq(aa / (2 - bb), aa / 2 + bb - 1), aa):
        sol.append((r, bb, sp.nsimplify(r / R['S6-1'] + bb)))
R['S6-2 (P29, expect -1/2)'] = sol

# ---- S7: x>1, x+49/(x-1) min
v = sp.minimum(x + 49 / (x - 1), x, sp.Interval.open(1, sp.oo)); R['S7-1'] = v
res = []
for K in range(2, 200):
    A = [e for e in range(1, K + 1) if e % 2 == 0]
    B = [e for e in range(1, K + 1) if K % e == 0]
    C = [e for e in range(1, K + 1) if e not in A and e not in B]
    if len(A) * len(C) == int(v):
        p_ = 1
        for e in C: p_ *= e
        res.append((K, C, p_))
R['S7-2 (P9, expect 189)'] = res

# ---- S8: x>0, (x+3)^2/x min
v = sp.minimum((x + 3) ** 2 / x, x, sp.Interval.open(0, sp.oo)); R['S8-1'] = v
aa = sp.symbols('aa', positive=True)
# f=4/(x-a)-4: A=(a+1,0), B=(0,-4/a-4), C=(a,-4), O
Ox, Oy = 0, 0
pts = [(0, 0), (0, -4 / aa - 4), (aa, -4), (aa + 1, 0)]
area = sp.Rational(1, 2) * sp.Abs(sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4)))
R['S8-2 (P26, expect 5)'] = sp.solve(sp.Eq(sp.simplify(area), 2 * v), aa)

# ---- S9: p: x^2-6x+8<=0 ([2,4]) , q: x>=m, p->q true; max m
R['S9-1'] = 2
# ---- S10: (a+b)(4/a+9/b) min = 13 + 2*sqrt(36)
R['S10-1'] = 13 + 2 * 6
# ---- S11: 2x+3y=12 max xy
y = sp.symbols('y')
R['S11-1'] = sp.maximum(x * (12 - 2 * x) / 3, x, sp.Interval.open(0, 6))
# ---- S12: {1,2}⊂X⊂{1..6}, n(X)<=5
R['S12-1'] = sum(1 for r in range(0, 4) for _ in combinations(range(4), r))
# ---- S13: p: x^2-6x+5<=0 [1,5]; q: |x-a|<=4 ; p sufficient for q -> sum integer a
R['S13-1'] = sum(a_ for a_ in range(-20, 20) if a_ - 4 <= 1 and a_ + 4 >= 5)
# ---- S14: all x: x^2+2(k-1)x+k+5>0 -> integer k max
R['S14-1'] = max(k_ for k_ in range(-50, 50) if (k_ - 1) ** 2 - (k_ + 5) < 0)
# ---- S15: p: |x-2|<k, q: -3<x<9, p sufficient -> natural k max
R['S15-1'] = max(k_ for k_ in range(1, 50) if 2 - k_ >= -3 and 2 + k_ <= 9)
K = R['S15-1']
fs = []
for f in product(range(1, 5), repeat=4):
    ff = lambda v: f[v - 1]
    if all(xx + ff(ff(xx)) <= K for xx in range(1, 5)) and set(f) == {1, 2, 4}:
        fs.append(f)
R['S15-2 (P19, expect ㄱ,ㄴ true, ㄷ false)'] = (fs, all(f[f[3] - 1] == 1 for f in fs), all(f[2] == 4 for f in fs), len(fs))

# ---- S16: sqrt(ax+b) through (1,2),(5,4) -> f(21)
sa = sp.solve([sp.Eq(A_ + B_, 4), sp.Eq(5 * A_ + B_, 16)], [A_, B_])
R['S16-1'] = sp.sqrt(21 * sa[A_] + sa[B_])

# ---- S17: f=2x+1, g(f(x))=4x+5 -> g(3/2)
R['S17-1'] = 2 * F(3, 2) + 3
U = [1, 2, 4, 8, 16, 32]
best = None
for A in range(64):
    for B in range(64):
        As = {U[i] for i in range(6) if A >> i & 1}
        Bs = {U[i] for i in range(6) if B >> i & 1}
        BmA = Bs - As
        if not (2 <= len(BmA) <= 4): continue
        if len(As | Bs) != 5: continue
        if sum(As | (set(U) - Bs)) != int(R['S17-1']) * sum(BmA): continue
        s = sum(As)
        best = s if best is None else min(best, s)
R['S17-2 (P3, expect 22)'] = best

# ---- S18: (ax+b)/(x+c) asymptotes x=-1,y=3 through (1,9) -> a+b+c
kk = 2 * (9 - 3)  # k/(1+1)+3=9
R['S18-1'] = 3 + (3 + kk) + 1   # y=(3x+3+k)/(x+1)

# ---- S19 parallel: P17 and P18
best = set()
X = [-3, -2, -1, 0, 1, 2]
for choice in product([0, 1], repeat=6):
    vals = [(5 - v * v) if c == 0 else (-4 * v) for v, c in zip(X, choice)]
    if len(set(vals)) < 6: continue
    if vals[3] * vals[4] * vals[5] < 0:
        best.add(sum(vals))
R['S19-a (P17, expect 26)'] = best
f = {k_: pow(3, k_, 10) for k_ in range(1, 10)}
bestA = 0
for r in range(2, 10):
    for A in combinations(range(1, 10), r):
        As = set(A)
        if all(f[a_] in As and f[f[a_]] == 7 for a_ in A) and all(f[p_] <= f[q_] for p_, q_ in combinations(sorted(A), 2)):
            bestA = max(bestA, sum(A))
R['S19-b (P18, expect 11)'] = bestA

# ---- S20 parallel: P12 (16) and P24 (13)
ks = [k_ for k_ in range(-20, 21) if (k_ - 2 < -1 or k_ + 2 > 5) and (k_ + 2 >= -1 and k_ - 2 <= 5)]
R['S20-a (P12, expect 16)'] = sum(ks)
Xs = [-2, -1, 0, 1, 2]
vals = set()
for perm in permutations(Xs):
    fm = dict(zip(Xs, perm)); inv = {v: k_ for k_, v in fm.items()}
    if fm[fm[-1]] + inv[-2] != 4: continue
    if not all(fm[k_] * fm[k_ - 2] <= 0 for k_ in (0, 1)): continue
    vals.add(6 * fm[0] + 5 * fm[1] + 2 * fm[2])
R['S20-b (P24, expect 13)'] = vals

for k_, v_ in R.items():
    print(k_, '=>', v_)
