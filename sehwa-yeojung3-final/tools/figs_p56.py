from draw import *
from shapely.geometry import Polygon as SPoly
from shapely.ops import unary_union
from matplotlib.patches import FancyArrowPatch
import os
os.makedirs('re', exist_ok=True)


def rot(p, t):
    c, s = np.cos(t), np.sin(t)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1]])


# ---- 18번: 정사각형 OABC를 O 중심 30°씩 회전
def f18():
    fig, ax = new(4.6, 2.0)
    sq = [P(0, 0), P(2, 0), P(2, 2), P(0, 2)]
    polys = []
    for k in range(12):
        q = [rot(p, np.radians(30 * k)) for p in sq]
        polys.append(SPoly(q))
        ax.add_patch(Polygon(q, closed=True, fill=False, ec='k', lw=THIN))
    O = P(0, 0)
    A, B, C = sq[1], sq[2], sq[3]
    angle_arc(ax, O, A, rot(A, np.radians(30)), r=0.55, label='30°', lr=0.95, fs=FS - 3)
    dot(ax, O, r=0.05)
    lab(ax, O, 'O', dx=-0.25, dy=-0.2, fs=FS - 2); lab(ax, A, 'A', dx=0.2, dy=-0.15, fs=FS - 2)
    lab(ax, B, 'B', dx=0.2, dy=0.2, fs=FS - 2); lab(ax, C, 'C', dx=-0.2, dy=0.2, fs=FS - 2)
    u = unary_union(polys)
    off = P(6.4, 0)
    ax.add_patch(FancyArrowPatch((3.05, 0), (3.75, 0), arrowstyle='-|>', mutation_scale=9, lw=THIN, color='k'))
    xy = np.array(u.exterior.coords) + off
    ax.add_patch(Polygon(xy, closed=True, fc=GRAY, ec='k', lw=THIN))
    ax.set_xlim(-3.2, 9.4); ax.set_ylim(-3.0, 3.0)
    save(fig, 're/18번.png')


# ---- 19번: 직사각형 ABCD, AB=8, BC=15, 두 내접원(반지름 3)
def f19():
    fig, ax = new(3.6, 2.2)
    B, C, D, A = P(0, 0), P(15, 0), P(15, 8), P(0, 8)
    O, O2 = P(3, 3), P(12, 5)
    d = unit(C - A)
    G = A + d * (np.dot(O - A, d)); H = A + d * (np.dot(O2 - A, d))
    poly(ax, [G, O, H, O2], fc=DGRAY)
    ax.add_patch(Polygon([A, B, C, D], closed=True, fill=False, ec='k', lw=LW))
    seg(ax, A, C)
    ax.add_patch(Circle(O, 3, fill=False, ec='k', lw=THIN))
    ax.add_patch(Circle(O2, 3, fill=False, ec='k', lw=THIN))
    for a, b in [(G, O), (O, H), (H, O2), (O2, G)]:
        seg(ax, a, b, lw=THIN)
    dot(ax, O, 0.12); dot(ax, O2, 0.12)
    lab(ax, A, 'A', dx=-0.5, dy=0.3); lab(ax, B, 'B', dx=-0.5, dy=-0.3); lab(ax, C, 'C', dx=0.5, dy=-0.3)
    lab(ax, D, 'D', dx=0.5, dy=0.3); lab(ax, O, 'O', dx=-0.55, dy=-0.1); lab(ax, O2, "O'", dx=0.75, dy=0.15)
    lab(ax, G, 'G', dx=0.05, dy=0.6); lab(ax, H, 'H', dx=-0.1, dy=-0.65)
    save(fig, 're/19번.png')


# ---- 서답형1: 큰 반원 AB, 작은 두 반원 AC, CB
def s1():
    fig, ax = new(3.4, 1.9)
    A, B = P(0, 0), P(10, 0); C = P(3.4, 0)
    R, c0 = 5, P(5, 0); r1, c1 = 1.7, P(1.7, 0); r2, c2 = 3.3, P(6.7, 0)
    th = np.radians(62)
    Dp = c0 + R * np.array([np.cos(th), np.sin(th)])
    t = np.linspace(0, np.pi, 200)
    big = np.c_[c0[0] + R * np.cos(t), R * np.sin(t)]
    sm1 = np.c_[c1[0] + r1 * np.cos(t[::-1]), r1 * np.sin(t[::-1])]
    sm2 = np.c_[c2[0] + r2 * np.cos(t[::-1]), r2 * np.sin(t[::-1])]
    shade = np.vstack([big, sm1[::-1][::-1], sm2])  # 큰 반원(B→A) 후 작은 반원 A→C, C→B
    shade = np.vstack([big, np.c_[c1[0] - r1 * np.cos(t), r1 * np.sin(t)], np.c_[c2[0] - r2 * np.cos(t), r2 * np.sin(t)]])
    ax.add_patch(Polygon(shade, closed=True, fc=GRAY, ec='none'))
    ax.plot(big[:, 0], big[:, 1], 'k', lw=LW)
    ax.plot(c1[0] + r1 * np.cos(t), r1 * np.sin(t), 'k', lw=LW)
    ax.plot(c2[0] + r2 * np.cos(t), r2 * np.sin(t), 'k', lw=LW)
    seg(ax, A, B)
    # E: AD와 작은 반원(AC) 교점 = C에서 AD에 내린 수선의 발, F도 같은 방식
    E = A + unit(Dp - A) * np.dot(C - A, unit(Dp - A))
    F = B + unit(Dp - B) * np.dot(C - B, unit(Dp - B))
    for a, b in [(A, Dp), (Dp, B), (E, C), (C, F)]:
        seg(ax, a, b, lw=THIN)
    lab(ax, A, 'A', dx=-0.4, dy=-0.25); lab(ax, B, 'B', dx=0.4, dy=-0.25); lab(ax, C, 'C', dy=-0.5)
    lab(ax, Dp, 'D', dx=0.1, dy=0.4); lab(ax, E, 'E', dx=-0.05, dy=0.5); lab(ax, F, 'F', dx=0.35, dy=-0.35)
    save(fig, 're/서답형1.png')


# ---- 서답형2: 사분원과 삼각비 값
def s2():
    fig, ax = new(2.9, 2.6)
    for g in np.arange(0.1, 1.01, 0.1):
        ax.plot([g, g], [0, 1.05], color='#9a9a9a', lw=0.4, ls=(0, (1, 1.5)))
        ax.plot([0, 1.05], [g, g], color='#9a9a9a', lw=0.4, ls=(0, (1, 1.5)))
    ax.add_patch(Polygon([(0, 0), (1.05, 0), (1.05, 1.05), (0, 1.05)], closed=True, fill=False, ec='k', lw=THIN))
    th = np.radians(35)
    Pp = P(np.cos(th), np.sin(th)); Q = P(Pp[0], 0); S = P(1, 0); Rr = P(1, np.tan(th))
    poly(ax, [P(0, 0), Pp, Q], fc=GRAY)
    t = np.linspace(0, np.pi / 2, 100)
    ax.plot(np.cos(t), np.sin(t), 'k', lw=LW)
    for a, b in [(P(0, 0), Rr), (Pp, Q), (Rr, S), (P(0, 0), P(1.05, 0)), (P(0, 0), P(0, 1.05))]:
        seg(ax, a, b, lw=LW if b is not Q else LW)
    seg(ax, P(0, Rr[1]), Rr, lw=THIN, ls=(0, (2, 2)))
    seg(ax, P(0, Pp[1]), Pp, lw=THIN, ls=(0, (2, 2)))
    right_angle(ax, Q, Pp, P(0, 0), s=0.04); right_angle(ax, S, Rr, P(0, 0), s=0.04)
    angle_arc(ax, P(0, 0), S, Pp, r=0.12, label='35°', lr=0.2, fs=FS - 4)
    fs = FS - 3
    lab(ax, P(0, 1), '1', dx=-0.07, fs=fs); lab(ax, P(0, Rr[1]), '0.7002', dx=-0.2, fs=fs)
    lab(ax, P(0, Pp[1]), '0.5736', dx=-0.2, fs=fs); lab(ax, Q, '0.8192', dx=-0.06, dy=-0.07, fs=fs)
    lab(ax, S, '1', dx=0.03, dy=-0.07, fs=fs); lab(ax, P(0, 0), 'O', dx=-0.06, dy=-0.06, fs=fs)
    lab(ax, Pp, 'P', dx=0.06, dy=-0.03, fs=fs); lab(ax, Q, 'Q', dx=0.035, dy=0.04, fs=fs - 1)
    lab(ax, S, 'S', dx=0.07, dy=0.04, fs=fs - 1); lab(ax, Rr, 'R', dx=0.06, dy=0.03, fs=fs)
    save(fig, 're/서답형2.png')


def s2a():
    fig, ax = new(1.9, 1.3)
    th = np.radians(35)
    C = P(0, 0); B = P(-3 * np.cos(th), 0); A = P(B[0], 3 * np.sin(th))
    for a, b in [(A, B), (B, C), (C, A)]:
        seg(ax, a, b)
    right_angle(ax, B, A, C, s=0.15)
    angle_arc(ax, C, A, B, r=0.45, label='35°', lr=0.8, fs=FS - 2)
    dim_arc(ax, A, C, bulge=0.12, side=1, label='3', lo=0.45)
    dim_arc(ax, B, A, bulge=0.18, side=1, label='x', it=True, lo=0.35)
    lab(ax, A, 'A', dy=0.2); lab(ax, B, 'B', dx=-0.15, dy=-0.15); lab(ax, C, 'C', dx=0.2, dy=-0.1)
    save(fig, 're/서답형2_1.png')


def s2b():
    fig, ax = new(1.4, 1.7)
    th = np.radians(55)
    B = P(0, 0); C = P(4 * np.cos(th), 0); A = P(C[0], 4 * np.sin(th))
    for a, b in [(A, B), (B, C), (C, A)]:
        seg(ax, a, b)
    right_angle(ax, C, A, B, s=0.18)
    angle_arc(ax, B, C, A, r=0.45, label='55°', lr=0.85, fs=FS - 2)
    dim_arc(ax, B, A, bulge=0.1, side=1, label='4', lo=0.45)
    dim_arc(ax, B, C, bulge=0.18, side=-1, label='x', it=True, lo=0.35)
    lab(ax, A, 'A', dy=0.22); lab(ax, B, 'B', dx=-0.2, dy=-0.1); lab(ax, C, 'C', dx=0.2, dy=-0.1)
    save(fig, 're/서답형2_2.png')


# ---- 서답형3: 원 O, 사각형 ABCD, 호 AC 위의 점 E
def s3():
    fig, ax = new(2.1, 2.1)
    def on(t): return P(np.cos(np.radians(t)), np.sin(np.radians(t)))
    E, A, B, C = on(103), on(150), on(220), on(332)
    D = 0.97 * on(30)     # 원 위에 있음을 보이는 문제라 원 근처에 둔다
    t = np.radians(np.linspace(103, 332, 200))
    ax.plot(np.cos(t), np.sin(t), 'k', lw=LW)
    t2 = np.radians(np.linspace(332, 463, 120))
    ax.plot(np.cos(t2), np.sin(t2), 'k', lw=THIN, ls=(0, (1.5, 2)))
    for a, b in [(A, B), (B, C), (C, D), (D, A), (E, A), (E, C)]:
        seg(ax, a, b, lw=LW)
    angle_arc(ax, E, A, C, r=0.13)
    angle_arc(ax, D, A, C, r=0.13)
    dot(ax, P(0, 0), 0.03)
    lab(ax, P(0, 0), 'O', dy=-0.13, fs=FS - 2)
    for p, s, dx, dy in [(E, 'E', 0, 0.13), (A, 'A', -0.13, 0.03), (B, 'B', -0.1, -0.1), (C, 'C', 0.12, -0.03), (D, 'D', 0.13, 0.03)]:
        lab(ax, p, s, dx=dx, dy=dy, fs=FS - 2)
    save(fig, 're/서답형3.png')


# ---- 서답형4: 직육면체, EF=8, ∠AFE=60°, ∠CFG=45°
def s4():
    fig, ax = new(2.6, 2.6)
    w, h = 8 * 3 ** .5, 8 * 3 ** .5
    dv = np.array([-0.62, 0.5]) * 8     # 깊이 방향(앞→뒤): 왼쪽 위
    F = P(0, 0); G = F + P(w, 0); Bp = F + P(0, h); C = G + P(0, h)
    E = F + dv; H = G + dv; A = Bp + dv; D = C + dv
    poly(ax, [A, Bp, C, D], fc='#d9d9d9'); poly(ax, [Bp, F, G, C], fc='#d0d0d0'); poly(ax, [A, E, F, Bp], fc='#c4c4c4')
    poly(ax, [A, F, C], fc=DGRAY, z=1)
    for a, b in [(A, D), (D, C), (C, Bp), (Bp, A), (A, E), (E, F), (F, G), (G, C), (Bp, F), (A, F), (F, C), (A, C)]:
        seg(ax, a, b)
    for a, b in [(E, H), (H, G), (H, D)]:
        seg(ax, a, b, lw=THIN, ls=(0, (3, 2)))
    angle_arc(ax, F, E, A, r=1.6)
    angle_arc(ax, F, G, C, r=2.0, label='45°', lr=3.3, fs=FS - 2)
    angle_arc(ax, C, A, F, r=1.4, label='x°', lr=2.4, fs=FS - 2, it=False)
    lab(ax, E + P(-1.6, -1.6), '60°', fs=FS - 2)
    lab(ax, (E + F) / 2 + P(0.6, -0.6), '8', fs=FS - 2)
    for p, s, dx, dy in [(A, 'A', -0.7, 0.6), (D, 'D', 0.4, 0.7), (Bp, 'B', 0.7, -0.8), (C, 'C', 0.9, 0.2),
                         (E, 'E', -0.8, 0.1), (H, 'H', 0.8, 0.3), (F, 'F', -0.3, -0.9), (G, 'G', 0.8, -0.3)]:
        lab(ax, p, s, dx=dx, dy=dy, fs=FS - 1)
    save(fig, 're/서답형4.png')


for f in (f18, f19, s1, s2, s2a, s2b, s3, s4):
    f()
