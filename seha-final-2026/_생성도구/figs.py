"""Draw the problem figures (PNG) used by the 서초고 book.  python figs.py"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch, Circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
DPI = 220


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=DPI, bbox_inches='tight', pad_inches=0.04, facecolor='white')
    plt.close(fig)


# ------------------------------------------------------------ arrow diagrams
def arrow_panel(ax, x0, left, right, mapping, lname='X', rname='Y', title=None, gap=1.6, tag=None):
    n = max(len(left), len(right))
    h = 0.55 * n + 0.5
    for xc, items, nm in ((x0, left, lname), (x0 + gap, right, rname)):
        ax.add_patch(Ellipse((xc, 0), 0.75, h, fill=False, lw=1.1))
        ax.text(xc, h / 2 + 0.12, '$%s$' % nm, ha='center', va='bottom', fontsize=13)
        for i, it in enumerate(items):
            y = (len(items) - 1) / 2 * 0.55 - i * 0.55
            ax.text(xc, y, '$%s$' % it, ha='center', va='center', fontsize=12)
    ax.annotate('', xy=(x0 + gap - 0.35, h / 2 + 0.3), xytext=(x0 + 0.35, h / 2 + 0.3),
                arrowprops=dict(arrowstyle='->', lw=1.0))
    if tag:
        ax.text(x0 - 0.8, h / 2 + 0.2, tag, ha='left', va='bottom', fontsize=12)
    if title:
        ax.text(x0 + gap / 2, h / 2 + 0.38, '$%s$' % title, ha='center', va='bottom', fontsize=12)

    def ypos(items, it):
        i = items.index(it)
        return (len(items) - 1) / 2 * 0.55 - i * 0.55
    for a, bs in mapping.items():
        for b in (bs if isinstance(bs, (list, tuple)) else [bs]):
            ax.annotate('', xy=(x0 + gap - 0.17, ypos(right, b)), xytext=(x0 + 0.17, ypos(left, a)),
                        arrowprops=dict(arrowstyle='-|>', lw=0.9, mutation_scale=9, shrinkA=2, shrinkB=2))
    return h


def arrows(name, panels, width_per=2.6):
    fig, ax = plt.subplots(figsize=(width_per * len(panels), 2.7))
    x = 0
    hmax = 0
    for p in panels:
        h = arrow_panel(ax, x, **p)
        if p.get('label'):
            pass
        hmax = max(hmax, h)
        x += p.get('gap', 1.6) + 1.3
    ax.set_xlim(-0.9, x - 0.7)
    ax.set_ylim(-hmax / 2 - 0.2, hmax / 2 + 0.75)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, name)


def arrows_chain(name, sets, maps, titles):
    """three columns X->X->X"""
    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    xs = [0, 1.7, 3.4]
    n = len(sets[0])
    h = 0.55 * n + 0.5
    for xc in xs:
        ax.add_patch(Ellipse((xc, 0), 0.75, h, fill=False, lw=1.1))
        ax.text(xc, h / 2 + 0.12, '$X$', ha='center', va='bottom', fontsize=13)
        for i, it in enumerate(sets[0]):
            ax.text(xc, (n - 1) / 2 * 0.55 - i * 0.55, '$%s$' % it, ha='center', va='center', fontsize=12)
    yp = lambda v: (n - 1) / 2 * 0.55 - sets[0].index(v) * 0.55
    for k, (m, t) in enumerate(zip(maps, titles)):
        a0, a1 = xs[k], xs[k + 1]
        ax.annotate('', xy=(a1 - 0.35, h / 2 + 0.3), xytext=(a0 + 0.35, h / 2 + 0.3), arrowprops=dict(arrowstyle='->', lw=1.0))
        ax.text((a0 + a1) / 2, h / 2 + 0.38, '$%s$' % t, ha='center', va='bottom', fontsize=12)
        for a, b in m.items():
            ax.annotate('', xy=(a1 - 0.17, yp(b)), xytext=(a0 + 0.17, yp(a)),
                        arrowprops=dict(arrowstyle='-|>', lw=0.9, mutation_scale=9, shrinkA=2, shrinkB=2))
    ax.set_xlim(-0.6, 4.0)
    ax.set_ylim(-h / 2 - 0.2, h / 2 + 0.8)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, name)


# ------------------------------------------------------------ venn diagrams
def venn3(name, region):
    """region(a,b,c)->bool : shade where True"""
    fig, ax = plt.subplots(figsize=(3.0, 2.5))
    ca, cb, cc = (0, 0.55), (-0.5, -0.3), (0.5, -0.3)
    r = 0.85
    xs, ys = np.meshgrid(np.linspace(-2, 2, 700), np.linspace(-1.7, 1.9, 700))
    ina = (xs - ca[0]) ** 2 + (ys - ca[1]) ** 2 < r * r
    inb = (xs - cb[0]) ** 2 + (ys - cb[1]) ** 2 < r * r
    inc = (xs - cc[0]) ** 2 + (ys - cc[1]) ** 2 < r * r
    m = region(ina, inb, inc)
    ax.contourf(xs, ys, m.astype(float), levels=[0.5, 1.5], colors=['#bdbdbd'])
    for c, nm, off in ((ca, 'A', (0, r + 0.12)), (cb, 'B', (-r - 0.05, -0.55)), (cc, 'C', (r + 0.05, -0.55))):
        ax.add_patch(Circle(c, r, fill=False, lw=1.1))
        ax.text(c[0] + off[0], c[1] + off[1], '$%s$' % nm, ha='center', va='center', fontsize=13)
    ax.add_patch(Rectangle((-1.95, -1.55), 3.9, 3.35, fill=False, lw=1.1))
    ax.text(-1.8, 1.62, '$U$', fontsize=13)
    ax.set_xlim(-2, 2); ax.set_ylim(-1.6, 1.85); ax.set_aspect('equal'); ax.axis('off')
    save(fig, name)


def venn2(name, region):
    fig, ax = plt.subplots(figsize=(2.8, 1.8))
    ca, cb, r = (-0.45, 0), (0.45, 0), 0.75
    xs, ys = np.meshgrid(np.linspace(-1.55, 1.55, 700), np.linspace(-1.0, 1.0, 500))
    ina = (xs - ca[0]) ** 2 + (ys - ca[1]) ** 2 < r * r
    inb = (xs - cb[0]) ** 2 + (ys - cb[1]) ** 2 < r * r
    ax.contourf(xs, ys, region(ina, inb).astype(float), levels=[0.5, 1.5], colors=['#bdbdbd'])
    for c, nm, dx in ((ca, 'A', -0.35), (cb, 'B', 0.35)):
        ax.add_patch(Circle(c, r, fill=False, lw=1.1))
        ax.text(c[0] + dx, 0.5, '$%s$' % nm, ha='center', fontsize=13)
    ax.add_patch(Rectangle((-1.55, -1.0), 3.1, 2.0, fill=False, lw=1.1))
    ax.text(-1.45, 0.78, '$U$', fontsize=13)
    ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.05, 1.05); ax.set_aspect('equal'); ax.axis('off')
    save(fig, name)


# ------------------------------------------------------------ graphs
def axes(ax, xl, yl):
    ax.annotate('', xy=(xl[1], 0), xytext=(xl[0], 0), arrowprops=dict(arrowstyle='-|>', lw=0.9, mutation_scale=9))
    ax.annotate('', xy=(0, yl[1]), xytext=(0, yl[0]), arrowprops=dict(arrowstyle='-|>', lw=0.9, mutation_scale=9))
    ax.text(xl[1], -0.08 * (yl[1] - yl[0]) / 4, '$x$', fontsize=12, va='top', ha='right')
    ax.text(0.04 * (xl[1] - xl[0]) / 4, yl[1], '$y$', fontsize=12, va='top', ha='left')
    ax.set_xlim(xl); ax.set_ylim(yl); ax.set_aspect('equal'); ax.axis('off')


def points_graph(name, pts, label, ymax=4):
    fig, ax = plt.subplots(figsize=(2.6, 2.6))
    for x in range(1, 5):
        ax.plot([x, x], [0, ymax + 0.3], ls=':', lw=0.7, color='gray')
        ax.text(x, -0.15, '$%d$' % x, ha='center', va='top', fontsize=11)
    for y in range(1, ymax + 1):
        ax.plot([0, 4.3], [y, y], ls=':', lw=0.7, color='gray')
        ax.text(-0.12, y, '$%d$' % y, ha='right', va='center', fontsize=11)
    ax.text(-0.12, -0.12, '$O$', ha='right', va='top', fontsize=11)
    for x, y in pts:
        ax.plot(x, y, 'o', color='black', ms=6)
    ax.text(4.3, ymax + 0.25, '$%s$' % label, ha='right', va='bottom', fontsize=11)
    axes(ax, (-0.3, 4.7), (-0.3, ymax + 0.8))
    save(fig, name)


def fig_parabola61():
    fig, ax = plt.subplots(figsize=(2.6, 2.4))
    t = np.linspace(-2.6, 1.6, 400)
    y = 8 / 9 * (t + 0.5) ** 2 - 2
    ax.plot(t, y, color='black', lw=1.3)
    ax.plot([-0.5, -0.5], [0, -2], ls='--', lw=0.7, color='black')
    ax.plot([-0.5, 0], [-2, -2], ls='--', lw=0.7, color='black')
    ax.text(-2, 0.1, '$-2$', ha='center', va='bottom', fontsize=11)
    ax.text(1.05, 0.1, '$1$', ha='center', va='bottom', fontsize=11)
    ax.text(-0.5, 0.1, r'$-\frac{1}{2}$', ha='center', va='bottom', fontsize=11)
    ax.text(0.08, -2.05, '$-2$', ha='left', va='top', fontsize=11)
    ax.text(0.05, 0.05, '$O$', ha='left', va='bottom', fontsize=10)
    ax.text(1.2, 1.4, '$y=f(x)$', fontsize=11)
    axes(ax, (-2.8, 1.9), (-2.5, 2.0))
    save(fig, 'q_sw061')


def fig_hyper_f25_4():
    fig, ax = plt.subplots(figsize=(2.9, 2.5))
    for rng in (np.linspace(-1.5, 2.9, 300), np.linspace(3.12, 6.5, 300)):
        ax.plot(rng, 2 / (rng - 3) + 2, color='black', lw=1.3)
    ax.plot([3, 3], [-1.6, 5], ls=':', color='black', lw=0.8)
    ax.plot([-1.5, 6.5], [2, 2], ls=':', color='black', lw=0.8)
    ax.text(-0.1, 2.05, '$2$', ha='right', va='bottom', fontsize=11)
    ax.text(3.05, -0.1, '$3$', ha='left', va='top', fontsize=11)
    ax.text(2.0, 0.1, '$2$', ha='center', va='bottom', fontsize=11)
    ax.text(-0.08, -0.08, '$O$', ha='right', va='top', fontsize=10)
    axes(ax, (-1.6, 6.7), (-1.7, 5.2))
    save(fig, 'q_f25_04')


def fig_hyper_sw093():
    fig, ax = plt.subplots(figsize=(2.6, 2.4))
    for rng in (np.linspace(-1.5, 3.75, 300), np.linspace(4.3, 8, 300)):
        ax.plot(rng, (rng - 8) / (rng - 4), color='black', lw=1.3)
    ax.plot([4, 4], [-3, 5.5], ls=':', color='black', lw=0.8)
    ax.plot([-1.5, 8], [1, 1], ls=':', color='black', lw=0.8)
    ax.text(-0.1, 2, '$2$', ha='right', va='center', fontsize=11)
    ax.text(4.05, -0.1, '$4$', ha='left', va='top', fontsize=11)
    ax.text(-0.08, -0.08, '$O$', ha='right', va='top', fontsize=10)
    axes(ax, (-1.6, 8.3), (-3.0, 5.7))
    save(fig, 'q_sw093')


def fig_sqrt_sw106():
    fig, ax = plt.subplots(figsize=(2.6, 1.8))
    t = np.linspace(-4, 0, 300)
    ax.plot(t, np.sqrt(-t) * 1.0, color='black', lw=1.3)
    ax.text(-3.9, 2.15, r'$y=-a\sqrt{bx}$', fontsize=11)
    ax.text(0.08, -0.08, '$O$', ha='left', va='top', fontsize=10)
    axes(ax, (-4.2, 1.2), (-0.6, 2.6))
    save(fig, 'q_sw106')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # 2025 기말 2번 : 대응 네 개
    L4, L3 = ['1', '2', '3', '4'], ['1', '2', '3']
    arrows('q_f25_02a', [dict(left=L4, right=['a', 'b', 'c'], mapping={'1': 'b', '2': 'b', '3': 'a', '4': 'c'}, tag='ㄱ.'),
                         dict(left=L4, right=['a', 'b', 'c'], mapping={'1': 'a', '2': 'b', '3': 'b'}, tag='ㄴ.')])
    arrows('q_f25_02b', [dict(left=L3, right=['a', 'b', 'c', 'd'], mapping={'1': 'a', '2': 'b', '3': 'c'}, tag='ㄷ.'),
                         dict(left=L3, right=['a', 'b', 'c'], mapping={'1': 'a', '2': 'c', '3': ['b', 'c']}, tag='ㄹ.')])
    venn3('q_f25_06', lambda a, b, c: c & ~(a & b))
    venn3('q_sw030', lambda a, b, c: b & c & ~a)
    venn2('q_sw032', lambda a, b: (a & b) | (~a & ~b))
    points_graph('q_sw053', [(1, 2), (2, 1), (3, 3), (4, 3)], 'y=g(x)')
    points_graph('q_f25_14', [(1, 4), (2, 1), (3, 4), (4, 3)], 'y=f(x)')
    points_graph('q_new_f1', [(1, 3), (2, 4), (3, 1), (4, 4)], 'y=f(x)')
    fig_parabola61()
    N4 = ['1', '2', '3', '4']
    arrows_chain('q_sw064', [N4], [{'1': '2', '2': '3', '3': '4', '4': '1'}, {'1': '2', '2': '1', '3': '4', '4': '3'}], ['f', 'g'])
    arrows('q_sw067', [dict(left=['1', '2', '3'], right=['1', '2', '3'], mapping={'1': '2', '2': '3', '3': '1'}, lname='X', rname='X', title='f')])
    N5 = ['1', '2', '3', '4', '5']
    arrows('q_sw070', [dict(left=N5, right=N5, mapping={'1': '3', '2': '5', '3': '2', '4': '1', '5': '4'}, lname='X', rname='X', title='f'),
                       dict(left=N5, right=N5, mapping={'1': '5', '2': '3', '3': '1', '4': '2', '5': '4'}, lname='X', rname='X', title='g')])
    arrows('q_sw071', [dict(left=['7', '8', '9'], right=['1', '2', '3'], mapping={'7': '3', '8': '1', '9': '2'}, lname='C', rname='A', title='(g \\circ f)^{-1}')])
    arrows('q_sw077', [dict(left=N4, right=N4, mapping={'1': '2', '2': '1', '3': '3', '4': '4'}, lname='X', rname='X', title='f')])
    fig_hyper_f25_4()
    fig_hyper_sw093()
    fig_sqrt_sw106()
    print('figs:', sorted(os.listdir(OUT)))


