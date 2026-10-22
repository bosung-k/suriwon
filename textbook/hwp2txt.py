"""Extract text (with equation scripts) from HWP 5.0 files.
Usage: python hwp2txt.py in.hwp out.txt
Equations are emitted as ⟦script⟧, tables/boxes as nested blocks.
"""
import sys, zlib, struct, olefile

PARA_HEADER, PARA_TEXT, CTRL_HEADER, LIST_HEADER, EQEDIT = 66, 67, 71, 72, 88
EXT = {1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23}
INL = {4, 5, 6, 7, 8, 9, 19, 20}


def records(data):
    i, out = 0, []
    while i + 4 <= len(data):
        h = struct.unpack_from('<I', data, i)[0]
        tag, lvl, size = h & 0x3FF, (h >> 10) & 0x3FF, h >> 20
        i += 4
        if size == 0xFFF:
            size = struct.unpack_from('<I', data, i)[0]
            i += 4
        out.append([tag, lvl, data[i:i + size], []])
        i += size
    return out


def tree(recs):
    root, stack = [None, -1, b'', []], []
    stack.append(root)
    for r in recs:
        while stack[-1][1] >= r[1]:
            stack.pop()
        stack[-1][3].append(r)
        stack.append(r)
    return root[3]


def find(node, tag):
    for c in node[3]:
        if c[0] == tag:
            return c
        f = find(c, tag)
        if f:
            return f
    return None


def render_ctrl(c):
    cid = c[2][:4][::-1].decode('latin1', 'replace')
    if cid == 'eqed':
        e = find(c, EQEDIT)
        if e:
            n = struct.unpack_from('<H', e[2], 4)[0]
            s = e[2][6:6 + 2 * n].decode('utf-16le', 'replace')
            return '⟦' + s.strip() + '⟧'
        return '⟦?⟧'
    # nested paragraphs (tables, text boxes, footnotes...)
    paras = []
    collect_paras(c, paras)
    if not paras:
        return ''
    body = ' | '.join(p for p in paras if p.strip())
    if cid == 'tbl ':
        return '\n[표: ' + body + ']\n'
    if cid in ('gso ',):
        return '\n[박스: ' + body + ']\n' if body.strip() else ''
    return ' {' + body + '} '


def collect_paras(node, out):
    for c in node[3]:
        if c[0] == PARA_HEADER:
            out.append(render_para(c))
        else:
            collect_paras(c, out)


def render_para(p):
    text = b''
    ctrls = []
    for c in p[3]:
        if c[0] == PARA_TEXT:
            text = c[2]
        elif c[0] == CTRL_HEADER:
            ctrls.append(c)
    s, i, k = [], 0, 0
    n = len(text) // 2
    while i < n:
        ch = struct.unpack_from('<H', text, i * 2)[0]
        if ch in EXT:
            if k < len(ctrls):
                s.append(render_ctrl(ctrls[k]))
                k += 1
            i += 8
        elif ch in INL:
            i += 8
        elif ch == 9:
            s.append('\t'); i += 8
        elif ch in (10, 13):
            i += 1
        elif ch < 32:
            i += 1
        else:
            s.append(chr(ch)); i += 1
    while k < len(ctrls):
        s.append(render_ctrl(ctrls[k])); k += 1
    return ''.join(s)


def main(src, dst):
    ole = olefile.OleFileIO(src)
    hdr = ole.openstream('FileHeader').read()
    compressed = hdr[36] & 1
    secs = sorted([e for e in ole.listdir() if e[0] == 'BodyText'],
                  key=lambda e: int(e[1][7:]))
    lines = []
    for e in secs:
        d = ole.openstream(e).read()
        if compressed:
            d = zlib.decompress(d, -15)
        for node in tree(records(d)):
            if node[0] == PARA_HEADER:
                t = render_para(node)
                if t.strip():
                    lines.append(t)
    with open(dst, 'w', encoding='utf-8', errors='replace') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

