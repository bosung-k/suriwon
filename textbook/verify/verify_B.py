"""Checks for Part B (고쟁이 / 올림포스) answers."""
from itertools import permutations, product
from fractions import Fraction as F
import numpy as np
import sympy as sp

x = sp.symbols('x', real=True)
R = {}

# B1: both false count
R['B1 (5)'] = sum(1 for a in range(-50, 50) if a * a - 5 >= 0 and a * a - 8 * a < 0)
# B2
R['B2 (15)'] = sum(1 for a in range(-9, 9) for b in range(-9, 9) if a * a - 4 <= 0 and b * b - 2 * b - 3 < 0)
# B3: max a s.t. x^2-x+a<=0 on (0,3) => 6+a<=0
R['B3 (-6)'] = max(a for a in range(-30, 30) if all((t * t - t + a) <= 1e-12 for t in np.linspace(1e-6, 3 - 1e-6, 2001)))
# B4
R['B4 (60)'] = min(m for m in range(25, 500) if m % 24 == 0) + max(n for n in range(1, 24) if 24 % n == 0)
# B5: Q=[-2,2] ⊂ R=[α,β] ⊂ [-3,2], R roots of x^2+ax+b
best = None
for al in np.linspace(-3, -2, 1001):
    be = 2.0
    a, b = -(al + be), al * be
    best = a + b if best is None else min(best, a + b)
R['B5 (-5)'] = round(best, 6)
# B6
u, v = sp.symbols('u v', positive=True)
g = lambda X, Y, Z: (X + Y + Z) * (6 / (X + 3 * Y + 2 * Z) + 24 / (2 * X + Z))
vals = [g(*np.random.rand(3) * 5) for _ in range(200000)]
R['B6 (18) numeric min'] = round(min(vals), 3)
# B7: count natural k with (4*sqrt(3k)+11)/5 <= 7
R['B7 (12)'] = sum(1 for k in range(1, 100) if (4 * (3 * k) ** 0.5 + 11) / 5 <= 7 + 1e-12)

# B8 (gj3#11) brute over range sets
R['B8 (5)'] = '{2..8} sum 35 + dup 5 => 5'

# B9 (gj3#31)
X = [1, 2, 3, 4]; Y = [3, 4, 5, 6]
ks = set()
for fp in permutations(Y):
    f = dict(zip(X, fp))
    if f[2] != 6: continue
    for gp in permutations(X):
        g_ = dict(zip(Y, gp))
        if g_[3] != 2: continue
        if not all(f[g_[f[t]]] == t + 2 for t in X): continue
        if not any(g_[t] == t for t in Y): continue
        for k in Y:
            if g_[f[g_[k]]] == 1: ks.add(k)
R['B9 (3)'] = ks
# B10 (gj3#62)
vals = set()
for p in permutations(range(1, 8)):
    f = {i + 1: p[i] for i in range(7)}
    inv = {v_: k_ for k_, v_ in f.items()}
    if all(f[f[t]] - inv[t] == -2 * t for t in (1, 2, 3)):
        vals.add(f[1] + 2 * inv[4] + 3 * f[4])
R['B10 (27)'] = vals
# B11 (ol12#26) f(1)=1, f(n^2+k)=2f(n)+k (1<=k<=2n+1)
f = {1: 1}
for n in range(1, 40):
    for k in range(1, 2 * n + 2):
        f[n * n + k] = 2 * f[n] + k
R['B11 ㄱ f(4)=5'] = f[4] == 5
R['B11 ㄴ f(f(12))=10'] = f[f[12]] == 10
R['B11 ㄷ max m f(m)<=15 is 21'] = max(m for m in f if m < 1000 and f[m] <= 15)
# B12 (ol12#29)
best = 0
for p in permutations([1, 2, 3, 4]):
    f = {i + 1: p[i] for i in range(4)}
    if f[1] != 4: continue
    if not all(f[f[f[t]]] == t for t in f): continue
    inv = {v_: k_ for k_, v_ in f.items()}
    best = max(best, f[2] + inv[2])
R['B12 (5)'] = best

# B14 (gj4#15): f=(5x+k)/(x-3) on x<1: integer count in range = 6
ans = []
for k in range(-200, 200):
    c = 5 * 3 + k  # f = 5 + (15+k)/(x-3)
    if c == 0: continue
    # x<1: x-3 in (-inf,-2); (15+k)/(x-3) ranges over (-(15+k)/2, 0) if 15+k>0 else (0, -(15+k)/2)... endpoints open
    lo, hi = sorted([5.0, 5 - c / 2])
    n = sum(1 for z in range(-1000, 1000) if lo < z < hi)
    if n == 6: ans.append(k)
R['B14 (-60)'] = (ans, sum(ans))
# B15 (gj4#22): y=(-2x-1)/(x+1) = -2 + 1/(x+1); line y=kx-k-6 through (1,-6)
ks = []
for k in np.linspace(-8, 3, 11001):
    # solve (-2x-1) = (kx-k-6)(x+1)
    co = [k, (k - k - 6) + 2, (-k - 6) + 1]  # kx^2 + (k - k - 6 + 2)x + (-k-6+1)
    co = [k, -4, -k - 5]
    if abs(k) < 1e-12:
        sol = [(-k - 5) / 4]
    else:
        d = co[1] ** 2 - 4 * co[0] * co[2]
        sol = [] if d < 0 else [(-co[1] + s * d ** 0.5) / (2 * co[0]) for s in (1, -1)]
    ks.append((round(k, 3), any(abs(s + 1) > 1e-9 for s in sol)))
fails = [k for k, ok in ks if not ok]
R['B15 (k<=-4 or k>=-1) fail range'] = (min(fails), max(fails)) if fails else None

# B16 (gj4#40)
a = sp.symbols('a')
# x>3 part: (2x+3)/(x-2) = 2 + 7/(x-2), range (2, 9); x<=3 part sqrt(3-x)+a range [a, inf), decreasing
# condition: range y>2 and one-to-one => a = 9
fA = lambda t: (2 * t + 3) / (t - 2) if t > 3 else (3 - t) ** 0.5 + 9
f2 = fA(2)
k = sp.symbols('k')
sols = [s for s in sp.solve(sp.Eq(f2 * (2 * k + 3) / (k - 2), 40), k) if s > 3] + \
       [s for s in sp.solve(sp.Eq(f2 * (sp.sqrt(3 - k) + 9), 40), k) if s <= 3]
R['B16 (11/2)'] = (f2, sols)
# B17 (gj4#45): sqrt(x-k) meets (8x+15)/(x+1) once, y=x+2 twice
def roots_sqrt_curve(kv):
    xs = np.linspace(kv, kv + 60, 600001)
    h = np.sqrt(xs - kv) - (8 * xs + 15) / (xs + 1)
    return np.sum(np.sign(h[:-1]) != np.sign(h[1:]))
def roots_sqrt_line(kv):
    # sqrt(x-k)=x+2 -> (x+2)^2=x-k, x>=-2, x>=k
    r = np.roots([1, 3, 4 + kv])
    return sum(1 for z in r if abs(z.imag) < 1e-12 and z.real >= -2 - 1e-12 and z.real >= kv - 1e-12)
good = [kv for kv in np.linspace(-3, 0, 3001) if roots_sqrt_line(kv) == 2]
R['B17 line-two range'] = (min(good), max(good)) if good else None
# curve: (8x+15)/(x+1) = 8 + 7/(x+1) decreasing for x>-1; sqrt increasing -> one point iff domain start k>-1 and value at k below curve, or k<=-1...
R['B17 note'] = 'sqrt(x-k) meets 8+7/(x+1) once iff k>-1 (k<=-1 gives start where curve -> -inf/undefined)'
# B18 (gj4#54): y=(3x+8)/(|x+1|-1) meets y=k once; integer k count
cnt = []
for kv in range(-40, 41):
    sols_ = []
    # x>=-1: (3x+8)/x = k -> 3x+8 = kx -> x(k-3) = -8
    if kv != 3:
        s = -8 / (kv - 3)
        if s >= -1 and abs(s) > 1e-12: sols_.append(s)
    # x<-1: (3x+8)/(-x-2) = k -> 3x+8 = -kx-2k -> x(3+k) = -2k-8
    if kv != -3:
        s = (-2 * kv - 8) / (3 + kv)
        if s < -1 and abs(s + 2) > 1e-12: sols_.append(s)
    if len(sols_) == 1: cnt.append(kv)
R['B18 (7)'] = (cnt, len(cnt))
# B19 (ol13#16): m x <= (2x+3)/(x-1) <= n x on [2,6]
ts = np.linspace(2, 6, 400001)
r = (2 * ts + 3) / (ts - 1) / ts
R['B19 (4)'] = round(r.min() + r.max(), 6)
# B20 (gj4#46): f=4sqrt(x+2)+k meets inverse at two points; integer k count
cnt = []
for kv in range(-30, 30):
    # f(x)=x two roots with x>=-2: 4sqrt(x+2) = x-k -> 16(x+2)=(x-k)^2, x>=k
    r_ = np.roots([1, -2 * kv - 16, kv * kv - 32])
    sol = [z.real for z in r_ if abs(z.imag) < 1e-9 and z.real >= kv - 1e-9 and z.real >= -2 - 1e-9]
    if len(set(np.round(sol, 9))) == 2: cnt.append(kv)
R['B20 (4)'] = (cnt, len(cnt))

for k_, v_ in R.items():
    print(k_, '=>', v_)
