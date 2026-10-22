"""Shared helpers: hwpx read/write, pdf render."""
import zipfile, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, 'work')


def read_hwpx(path):
    z = zipfile.ZipFile(path)
    return {i.filename: z.read(i.filename) for i in z.infolist()}, [i.filename for i in z.infolist()]


def write_hwpx(path, files, order):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        names = list(order) + [n for n in files if n not in order]
        for n in names:
            if n not in files:
                continue
            if n == 'mimetype':
                z.writestr(zipfile.ZipInfo(n), files[n], compress_type=zipfile.ZIP_STORED)
            else:
                z.writestr(n, files[n])


def conv(*triples):
    args = [sys.executable, os.path.join(HERE, 'conv.py')]
    for t in triples:
        args += list(t)
    r = subprocess.run(args, capture_output=True, text=True, timeout=600)
    print(r.stdout[-3000:], r.stderr[-3000:])


def render(pdf, prefix, pages=None, zoom=1.6):
    import pymupdf
    d = pymupdf.open(pdf)
    out = []
    for i, p in enumerate(d):
        if pages and (i + 1) not in pages:
            continue
        pix = p.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        f = '%s_p%d.png' % (prefix, i + 1)
        pix.save(f)
        out.append(f)
    return out
