"""시험지 원본 그림 양식으로 재구성: 검은 실선, 세리프 글자, 점선 치수 호, 회색 음영."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Arc, Wedge
from matplotlib import rcParams

rcParams['font.family'] = 'Liberation Serif'
rcParams['mathtext.fontset'] = 'stix'
LW = 1.3          # 원본 굵은 선
THIN = 0.8
FS = 13
GRAY = '#b8b8b8'
DGRAY = '#8c8c8c'

P = lambda x, y: np.array([x, y], float)


def new(w=4, h=3):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_aspect('equal'); ax.axis('off')
    return fig, ax


def seg(ax, a, b, lw=LW, ls='-', c='k'):
    ax.plot([a[0], b[0]], [a[1], b[1]], color=c, lw=lw, ls=ls, solid_capstyle='round')


def poly(ax, pts, fc=GRAY, ec='none', lw=0, z=0):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, zorder=z))


def lab(ax, p, s, dx=0, dy=0, fs=FS, it=False, ha='center', va='center'):
    t = r'$%s$' % s if it else s
    ax.text(p[0] + dx, p[1] + dy, t, fontsize=fs, ha=ha, va=va)


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


def right_angle(ax, v, a, b, s=0.25, lw=THIN):
    u1, u2 = unit(a - v) * s, unit(b - v) * s
    ax.plot(*zip(v + u1, v + u1 + u2, v + u2), color='k', lw=lw)


def angle_arc(ax, v, a, b, r=0.35, lw=THIN, label=None, lr=None, fs=FS - 2, it=False):
    t1 = np.degrees(np.arctan2(*(a - v)[::-1])); t2 = np.degrees(np.arctan2(*(b - v)[::-1]))
    if (t2 - t1) % 360 > 180: t1, t2 = t2, t1
    ax.add_patch(Arc(v, 2 * r, 2 * r, theta1=t1, theta2=t2, lw=lw, color='k'))
    if label:
        m = np.radians(t1 + ((t2 - t1) % 360) / 2)
        q = v + (lr or r * 1.9) * np.array([np.cos(m), np.sin(m)])
        lab(ax, q, label, fs=fs, it=it)


def dim_arc(ax, a, b, bulge=0.25, label=None, side=1, fs=FS - 1, lpos=0.5, lo=0.18, it=False, ls=(0, (1.2, 2.2))):
    """두 점 사이 점선 치수 호(원본처럼 바깥으로 볼록)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a; n = np.array([-d[1], d[0]]) / np.linalg.norm(d) * side
    t = np.linspace(0, 1, 60)
    h = bulge * np.linalg.norm(d)
    pts = a[None] + t[:, None] * d[None] + (4 * t * (1 - t) * h)[:, None] * n[None]
    ax.plot(pts[:, 0], pts[:, 1], color='k', lw=THIN, ls=ls)
    if label:
        q = a + lpos * d + (4 * lpos * (1 - lpos) * h + lo * np.linalg.norm(d) ** 0 * 0.6) * n
        lab(ax, q, label, fs=fs, it=it)


def ticks(ax, a, b, n=2, s=0.12, gap=0.07, lw=THIN):
    m = (a + b) / 2; d = unit(b - a); nv = np.array([-d[1], d[0]])
    for k in range(n):
        c = m + d * gap * (k - (n - 1) / 2)
        seg(ax, c - nv * s + d * 0.03, c + nv * s - d * 0.03, lw=lw)


def dot(ax, p, r=0.045):
    ax.add_patch(Circle(p, r, color='k', zorder=5))


def save(fig, name, pad=0.06):
    fig.savefig(name, dpi=400, bbox_inches='tight', pad_inches=pad, facecolor='white')
    plt.close(fig)
