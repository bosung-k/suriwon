"""원문(부교재·교과서·기출·타교) 문항 정답의 독립 재계산 (전수 탐색·수치 계산).  python verify_sources.py"""
import itertools, math
from fractions import Fraction as F

R = {}
def subsets(s):
    s = list(s)
    for r in range(len(s) + 1):
        for c in itertools.combinations(s, r):
            yield set(c)

U = {1, 2, 3, 4, 6, 8, 12, 24}; A = {1, 2, 4}; B = {1, 2, 3, 4, 6, 12}
R['JD-04A30 (28)'] = sum(1 for X in subsets(U) if A & X == A and not B <= X)
U = set(range(1, 11)); A = {2, 5, 8}; B = {1, 3, 5, 7, 9}
R['JD-04B15 (256)'] = sum(1 for C in subsets(U) if (C & A) <= (C & B))
A = {1, 2, 3, 4, 5, 6}; B = {1, 3, 5, 7, 9}
R['JD-04B18 (32)'] = sum(1 for X in subsets(A) if len(A & B & X) >= 2)
R['TB2-Q72 (5)'] = sum(1 for k in range(2, 200) if all(n % k == 0 for n in range(12, 500, 12)))
R['F25-11 (6)'] = sum(1 for n in range(1, 201) if n % 30 == 0)
R['JD-04B12 (33)'] = sum(1 for n in range(1, 101) if n % 2 == 0 and (n % 3 == 0 or n % 4 == 0))
def maxfree(N, m):
    cnt = [sum(1 for n in range(1, N + 1) if n % m == r) for r in range(m)]
    tot = min(cnt[0], 1) + (min(cnt[m // 2], 1) if m % 2 == 0 else 0)
    for r in range(1, (m + 1) // 2):
        tot += max(cnt[r], cnt[m - r])
    return tot
R['JD-04B31 (83)'] = maxfree(202, 5); R['OT25 (23)'] = maxfree(50, 7)
R['TB2-Q73 (59)'] = 60 - (25 - (40 - 16))
# 명제
def interval_sub(p, q):  # closed intervals
    return q[0] <= p[0] and p[1] <= q[1]
cnt = 0
for a in range(-50, 51):
    lo, hi = min(a, 2 * a), max(a, 2 * a)
    pq = interval_sub((lo, hi), (-2, 5)); meet = not (hi < -2 or lo > 5)
    if not pq and meet: cnt += 1
R['JD-05B04 (4)'] = cnt
R['F25-12 (5)'] = sum(1 for k in range(-100, 0) if (k * k - k > 2) and (7 >= 1 - k))
R['JD-05B14 (9)'] = sum(1 for a in range(-50, 51) if -3 <= min(2, a) and max(2, a) <= 5)
R['TB2-Q69 (7)'] = sum(k for k in range(1, 50) if k - 1 >= 2 and k + 2 < 7)
# F25-서2
def ok(n):
    s = math.sqrt(n + 1) - 1; t = 24 / (n + 3)
    if abs(s - 1) < 1e-12: return True
    P = (min(1, s), max(1, s)); Q = (min(4, t), max(4, t))
    if abs(t - 4) < 1e-12: return False
    return Q[0] <= P[0] and P[1] <= Q[1]
R['F25-S2 (93)'] = sum(n for n in range(1, 3000) if ok(n))
# 함수
def is_inv_count(n, pred):
    return sum(1 for p in itertools.permutations(range(1, n + 1)) if pred(dict(zip(range(1, n + 1), p))))
R['JD-06A20 (4)'] = sum(1 for p in itertools.product([1, 2, 3], repeat=3)
                        if all(p[p[i] - 1] == i + 1 for i in range(3)))
R['JD-06B19 (4)'] = is_inv_count(4, lambda f: all(f[f[x]] == x for x in f) and any(f[x] == 2 * x for x in f))
def power_id(f, k):
    return all(_it(f, x, k) == x for x in f)
def _it(f, x, k):
    for _ in range(k): x = f[x]
    return x
R['F25-S4 (40)'] = is_inv_count(5, lambda f: f[5] != 5 and power_id(f, 4))
R['JD-06A07 (6)'] = sum(1 for a in range(1, 50) for b in range(1, 50) if -a + 7 > 0 and a - 7 + b == 2)
def f25(x): return x - 2 if x >= 0 else x + 2
def it(f, x, n):
    for _ in range(n): x = f(x)
    return x
R['JD-06A25 (0)'] = it(f25, 9, 2030) + it(f25, 11, 2030)
def fh(x): return -2 * x + 6 if x < 3 else 2 * x - 6
R['OT24-HY (13)'] = sum(it(fh, F(1, 2), n) for n in (1, 2, 4, 8))
# 유리·무리
R['TB3-Q48 (3)'] = sum(1 for x in range(1, 100) if 18 % (2 * x - 1) == 0)
R['JD-07A14 (6)'] = sum(1 for x in range(1, 4) for y in range(1, 4) if y <= F(1, 2 * x - 8) + 3)
def no_q2(a):
    # y = (-2x-2a+7)/(x-2): sample x<0 densely
    for i in range(1, 4000):
        x = -i / 20
        if (-2 * x - 2 * a + 7) / (x - 2) > 0: return False
    return True
R['JD-07A15 (6)'] = sum(a for a in range(1, 30) if no_q2(a))
R['JD-08B11 (11/2)'] = [k for k in [F(3, 2), F(5, 2), F(7, 2), F(9, 2), F(11, 2)] if (k >= 3 and 2 + 7 / (k - 2) == 4)]
def meets(m):
    for i in range(0, 200000):
        x = 3 + i / 1000
        if abs((-math.sqrt(x - 3) + 1) - (m * x - 2)) < 2e-3 or (-math.sqrt(x - 3) + 1) > m * x - 2 and i == 0: return True
    return False
R['TB3-Q53 (2)'] = min(m for m in range(1, 10) if not meets(m))
for k, v in R.items():
    print(k, '=>', v)
