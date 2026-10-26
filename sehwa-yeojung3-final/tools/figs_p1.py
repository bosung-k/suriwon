from draw import *
import os
os.makedirs('re', exist_ok=True)

# ---- 1번: ∠A=90°, ∠ADE=∠C, AD=9, DE=12
def f1():
    fig, ax = new(4, 2.4)
    B, C = P(0, 0), P(10, 0)
    A = P(3.6, 4.8)                      # AB=6, AC=8 (∠A=90°)
    D = A + (B - A) * 0.72               # AD
    ad = np.linalg.norm(D - A)
    E = A + unit(C - A) * ad * 0.75      # AE/AD = tan C = 3/4 → ∠ADE=∠C
    for a, b in [(A, B), (B, C), (C, A), (D, E)]:
        seg(ax, a, b)
    right_angle(ax, A, B, C, s=0.42)
    # ∠ADE, ∠C 표시 (원본: 점)
    angle_arc(ax, D, A, E, r=0.75)
    dot(ax, D + unit(unit(A - D) + unit(E - D)) * 0.45, r=0.07)
    dot(ax, C + unit(unit(A - C) + unit(B - C)) * 0.8, r=0.07)
    dim_arc(ax, D, A, bulge=0.16, side=1, label='9', lo=0.55)
    dim_arc(ax, D, E, bulge=0.12, side=-1, label='12', lo=0.5)
    lab(ax, A, 'A', dy=0.45); lab(ax, B, 'B', dx=-0.45, dy=-0.05); lab(ax, C, 'C', dx=0.45, dy=-0.05)
    lab(ax, D, 'D', dx=-0.5, dy=0.05); lab(ax, E, 'E', dx=0.45, dy=0.25)
    save(fig, 're/01번.png')

# ---- 2번: tan15°
def f2():
    fig, ax = new(4.4, 1.6)
    k = 2.2
    C = P((2 + 3 ** .5) * k, 0); A = P(C[0], 1 * k); D = P(2 * k, 0); B = P(0, 0)
    for a, b in [(B, C), (C, A), (A, B), (A, D)]:
        seg(ax, a, b)
    right_angle(ax, C, B, A, s=0.28)
    angle_arc(ax, B, C, A, r=1.6)
    angle_arc(ax, D, C, A, r=0.55, label='30°', lr=1.15)
    angle_arc(ax, A, B, D, r=0.9)
    lab(ax, B + P(1.45, 0.75), '15°', fs=FS - 1)
    lab(ax, A + P(-1.15, 0.45), '15°', fs=FS - 1)
    lab(ax, A, 'A', dy=0.35); lab(ax, B, 'B', dx=-0.35); lab(ax, C, 'C', dx=0.35, dy=-0.05); lab(ax, D, 'D', dy=-0.38)
    save(fig, 're/02번.png')

# ---- 4번: M은 BC의 중점, ∠BMA=45°, ∠MAB=90°
def f4():
    fig, ax = new(3.6, 1.4)
    B, M, C = P(0, 0), P(2, 0), P(4, 0)
    A = P(1, 1)
    for a, b in [(B, C), (A, B), (A, C), (A, M)]:
        seg(ax, a, b)
    right_angle(ax, A, B, M, s=0.15)
    ticks(ax, B, M, n=2, s=0.07, gap=0.06); ticks(ax, M, C, n=2, s=0.07, gap=0.06)
    lab(ax, A, 'A', dy=0.18); lab(ax, B, 'B', dx=-0.18); lab(ax, C, 'C', dx=0.18); lab(ax, M, 'M', dy=-0.2)
    save(fig, 're/04번.png')

# ---- 5번: 정삼각형 ABC, D는 AC 위, ∠ADB=105°, DC=10√3
def f5():
    fig, ax = new(3.2, 2.9)
    s = 15 + 5 * 3 ** .5
    B, C = P(0, 0), P(s, 0); A = P(s / 2, s * 3 ** .5 / 2)
    D = C + unit(A - C) * 10 * 3 ** .5
    poly(ax, [A, B, D], fc=GRAY)
    for a, b in [(A, B), (B, C), (C, A), (B, D)]:
        seg(ax, a, b)
    angle_arc(ax, D, A, B, r=2.2)
    lab(ax, D + P(-4.6, -1.2), '105°', fs=FS - 1)
    dim_arc(ax, D, C, bulge=0.16, side=1, label=r'10\sqrt{3}', it=True, lo=5.5)
    lab(ax, A, 'A', dy=1.5); lab(ax, B, 'B', dx=-1.5); lab(ax, C, 'C', dx=1.5); lab(ax, D, 'D', dx=1.4, dy=0.6)
    save(fig, 're/05번.png')

for f in (f1, f2, f4, f5):
    f()
