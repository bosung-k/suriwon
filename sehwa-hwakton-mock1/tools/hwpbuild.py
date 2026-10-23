"""Build HWP 5.0 body records by cloning the 2026 Sehwa exam template."""
import re
import struct
import zlib
import olefile
from eqsize import est

T_PHDR, T_PTXT, T_PCS, T_PLS, T_CTRL, T_LIST, T_TBL, T_EQ = 66, 67, 68, 69, 71, 72, 77, 88


def recs(b):
    i = 0
    out = []
    while i < len(b):
        h = struct.unpack_from('<I', b, i)[0]
        i += 4
        tag, lvl, sz = h & 0x3ff, (h >> 10) & 0x3ff, h >> 20
        if sz == 0xfff:
            sz = struct.unpack_from('<I', b, i)[0]
            i += 4
        out.append([tag, lvl, bytes(b[i:i + sz])])
        i += sz
    return out


def enc(R):
    out = bytearray()
    for tag, lvl, d in R:
        if len(d) >= 0xfff:
            out += struct.pack('<II', tag | (lvl << 10) | (0xfff << 20), len(d))
        else:
            out += struct.pack('<I', tag | (lvl << 10) | (len(d) << 20))
        out += d
    return bytes(out)


# ---------------------------------------------------------------- template bits
TAB_DATA = [0x1a52, 0x0000, 0x0100, 0x0020, 0x0020, 0x0020]
EQ_CTRL_T = bytes.fromhex('6465716511232a0c00000000000000000d02000065040000be00000038003800000000007442554800000000060018c2ddc285c7c8b2e4b22e00')
EQ_TAIL_T = bytes.fromhex('4c040000000000005500000013004500710075006100740069006f006e002000560065007200730069006f006e0020003600300007004800590068007700700045005100')
EN_CTRL_T = bytes.fromhex('20206e650b00000000002e0000000000df425548')
ATNO_T = bytes.fromhex('6f6e7461020000000b00000000002e00')
TBL_CTRL_T = bytes.fromhex('206c627411222a0800000000000000002d6d00008d100000710000001b011b011b011b01e6425548000000000000')
LIST_CELL_T = bytes.fromhex('010000002000000100000000010001002d6d00008d100000fe01fe018d008d0003002d6d0000000000000000000000')
LIST_EN = bytes.fromhex('01000000000000000000000000000000')
PLS_T = bytes.fromhex('00000000f3360000dc050000dc050000fb04000084030000f4010000ac73000000000600')


PS_SEG = {1: (500, 29612), 2: (1000, 29312), 4: (0, 30612), 12: (500, 29812), 15: (1000, 26612),
          16: (500, 29612), 18: (1500, 29112), 22: (0, 26928), 25: (500, 29612), 26: (500, 29612),
          27: (2000, 28112), 28: (2000, 28112), 29: (1500, 28612), 32: (500, 29612), 33: (500, 29612),
          34: (500, 30112)}


class IdGen:
    def __init__(self, start):
        self.n = start

    def __call__(self):
        self.n += 1
        return self.n


NEWID = IdGen(0x76100000)


def ctrlchar(code, cid):
    """8-wchar extended control: code, ctrl id (4 bytes), 4 zero wchars, code."""
    b = cid.encode('latin1')[::-1]
    w1, w2 = struct.unpack('<HH', b)
    return [code, w1, w2, 0, 0, 0, 0, code]


# ---------------------------------------------------------------- width model (for line-seg estimates)
def text_w(s):
    w = 0
    for c in s:
        o = ord(c)
        if 0xAC00 <= o <= 0xD7A3 or 0x3131 <= o <= 0x318E:
            w += 1000
        elif c == ' ':
            w += 520
        elif c in ',.:;\'"`':
            w += 300
        elif c in '()[]':
            w += 340
        elif c in '①②③④⑤':
            w += 1000
        else:
            w += 550
    return w


class Para:
    """A paragraph spec. items: list of ('t', str) | ('eq', script) | ('en', answer_items, numcs) |
    ('tbl', TableSpec) | ('tab',)"""

    def __init__(self, ps, items, cs=7, st=1, split=0, cs_first=None, extra_cs=None):
        self.ps, self.items, self.cs, self.st, self.split = ps, items, cs, st, split
        self.cs_first = cs_first  # char shape for the leading 8 wchars (endnote number)
        self.last = False
        self.indent_w = 29612
        self.vpos = 0
        self.seg = None  # (start, width) override

    # estimated layout --------------------------------------------------
    def layout(self, width=None):
        """Returns list of (textpos, line_height) for estimated lines."""
        if width is None:
            width = getattr(self, 'lay_w', None) or (self.seg or PS_SEG.get(self.ps, (500, 29612)))[1] - 1000
        first_cut = 3000 if self.cs_first is not None else 0
        lines = []
        pos = 0
        cur_w = first_cut
        cur_h = 1000
        start = 0
        base_h = 1000
        for it in self.items:
            if it[0] == 't':
                for c in it[1]:
                    cw = text_w(c)
                    if cur_w + cw > width and c != ' ':
                        lines.append((start, cur_h))
                        start, cur_w, cur_h = pos, 0, base_h
                    cur_w += cw
                    pos += 1
            elif it[0] == 'eq':
                w, h, b = est(it[1])
                if cur_w + w > width and cur_w > 0:
                    lines.append((start, cur_h))
                    start, cur_w, cur_h = pos, 0, base_h
                cur_w += w
                cur_h = max(cur_h, h)
                pos += 8
            elif it[0] == 'en':
                cur_h = max(cur_h, 1500)
                cur_w += 1800
                pos += 8
            elif it[0] == 'tbl':
                cur_h = max(cur_h, it[1].height())
                pos += 8
            elif it[0] == 'tab':
                cur_w = (cur_w // 9300 + 1) * 9300
                pos += 8
        lines.append((start, cur_h))
        return lines

    def height(self):
        tot = 0
        for _, h in self.layout():
            tot += h + (900 if h == 1500 else 600)
        return tot


class TableSpec:
    def __init__(self, rows, widths, row_h=1500, cell_ps=4, cell_cs=7, bf=3, row_bf=None):
        self.rows = rows  # list of list of cells; cell = list of items or str
        self.widths = widths
        self.row_h = row_h
        self.cell_ps = cell_ps
        self.cell_cs = cell_cs
        self.bf = bf
        self.row_bf = row_bf or {}

    def cell_paras(self, ri, ci):
        lines = cell_items(self.rows[ri][ci])
        out = []
        for li, line in enumerate(lines):
            p = Para(self.cell_ps, line, cs=self.cell_cs, st=0)
            p.last = (li == len(lines) - 1)
            p.seg = (0, self.widths[ci] - 1021)
            p.cell = True
            p.lay_w = self.widths[ci] - 1300
            out.append(p)
        return out

    def row_heights(self):
        hs = []
        for ri, r in enumerate(self.rows):
            h = self.row_h
            for ci in range(len(r)):
                v = 0
                for p in self.cell_paras(ri, ci):
                    v += p.height()
                h = max(h, v - 600 + 282 + 700)
            hs.append(h)
        return hs

    def height(self):
        return sum(self.row_heights()) + 900


# ---------------------------------------------------------------- record emission
def build_para(p, lvl=0):
    """Return list of records for paragraph p at level lvl."""
    wch = []
    kids = []
    mask = 0
    for it in p.items:
        if it[0] == 't':
            for c in it[1]:
                wch.append(ord(c))
        elif it[0] == 'tab':
            wch += [9] + TAB_DATA + [9]
            mask |= 1 << 9
        elif it[0] == 'eq':
            wch += ctrlchar(11, 'eqed')
            mask |= 1 << 11
            kids += eq_records(it[1], lvl + 1)
        elif it[0] == 'en':
            wch += ctrlchar(17, 'en  ')
            mask |= 1 << 17
            kids += endnote_records(it[1], it[2], lvl + 1)
        elif it[0] == 'tbl':
            wch += ctrlchar(11, 'tbl ')
            mask |= 1 << 11
            kids += table_records(it[1], lvl + 1)
    wch.append(13)
    nch = len(wch)
    ptxt = struct.pack('<%dH' % nch, *wch) if nch > 1 else b''
    # char shapes
    if getattr(p, 'pcs', None):
        pcs = p.pcs
    elif p.cs_first is not None and nch > 8:
        pcs = [(0, p.cs_first), (8, p.cs)]
    else:
        pcs = [(0, p.cs)]
    pcs_b = b''.join(struct.pack('<II', a, b) for a, b in pcs)
    # line segs
    st0, wid = p.seg or PS_SEG.get(p.ps, (500, 29612))
    lines = p.layout()
    segs = b''
    v = p.vpos
    for tp, h in lines:
        sp = 900 if h == 1500 else 600
        segs += struct.pack('<IiiiiiiiI', tp, v, h, h, int(h * 0.85), sp, st0, wid, 0x60000)
        v += h + sp
    hdr = struct.pack('<IIHBBHHHIH', nch | (0x80000000 if p.last else 0), mask, p.ps, p.st, p.split,
                      len(pcs), 0, len(lines), 0x80000000 if (lvl > 0 and not getattr(p, 'cell', False)) else 0, 0)
    out = [[T_PHDR, lvl, hdr]]
    if ptxt:
        out.append([T_PTXT, lvl + 1, ptxt])
    out.append([T_PCS, lvl + 1, pcs_b])
    out.append([T_PLS, lvl + 1, segs])
    out += kids
    return out


def eq_records(script, lvl):
    w, h, base = est(script)
    c = bytearray(EQ_CTRL_T)
    struct.pack_into('<II', c, 16, w, h)
    struct.pack_into('<I', c, 36, NEWID())
    s = script.encode('utf-16le')
    tail = bytearray(EQ_TAIL_T)
    struct.pack_into('<h', tail, 8, base)
    eq = struct.pack('<IH', 0, len(script)) + s + bytes(tail)
    return [[T_CTRL, lvl, bytes(c)], [T_EQ, lvl + 1, eq]]


ENNO = [0]
CFG = {'en_ps': 24, 'en_st': 7, 'suffix': 0x2e}
ZORD = [400]
CELL_H = 0


def endnote_records(ans_items, numcs, lvl):
    ENNO[0] += 1
    n = ENNO[0]
    c = bytearray(EN_CTRL_T)
    struct.pack_into('<I', c, 4, n)
    struct.pack_into('<H', c, 10, CFG['suffix'])
    struct.pack_into('<I', c, 16, NEWID())
    a = bytearray(ATNO_T)
    struct.pack_into('<I', a, 8, n)
    struct.pack_into('<H', a, 14, CFG['suffix'])
    # endnote paragraph: atno ctrl + ' ' + answer
    wch = [18, 0x6e6f, 0x6174, 0, 0, 0, 0, 18, ord(' ')]
    kids = [[T_CTRL, lvl + 2, bytes(a)]]
    mask = 1 << 18
    for it in ans_items:
        if it[0] == 't':
            wch += [ord(ch) for ch in it[1]]
        else:
            wch += ctrlchar(11, 'eqed')
            mask |= 1 << 11
            kids += eq_records(it[1], lvl + 2)
    wch.append(13)
    nch = len(wch)
    hdr = struct.pack('<IIHBBHHHIH', nch | 0x80000000, mask, CFG['en_ps'], CFG['en_st'], 0, 1, 0, 1, 0x80000000, 0)
    pls = bytes.fromhex('00000000000000006504000065040000bc03000058020000f4010000ac73000000000600')
    out = [[T_CTRL, lvl, bytes(c)], [T_LIST, lvl + 1, LIST_EN],
           [T_PHDR, lvl + 1, hdr], [T_PTXT, lvl + 2, struct.pack('<%dH' % nch, *wch)],
           [T_PCS, lvl + 2, struct.pack('<II', 0, 7)], [T_PLS, lvl + 2, pls]] + kids
    return out


def cell_items(c):
    """cell content -> list of lines(items)"""
    if isinstance(c, str):
        return [parse_inline(c)]
    if c and isinstance(c[0], list):
        return c
    return [c]


def table_records(t, lvl):
    nrows, ncols = len(t.rows), len(t.widths)
    W = sum(t.widths)
    row_heights = t.row_heights()
    H = sum(row_heights)
    c = bytearray(TBL_CTRL_T)
    struct.pack_into('<II', c, 16, W, H)
    ZORD[0] += 1
    struct.pack_into('<I', c, 24, ZORD[0])
    struct.pack_into('<I', c, 36, NEWID())
    tb = struct.pack('<IHHH', 6, nrows, ncols, 0) + bytes.fromhex('fe01fe018d008d00')
    tb += b''.join(struct.pack('<H', ncols) for _ in range(nrows))
    tb += struct.pack('<HH', t.bf, 0)
    out = [[T_CTRL, lvl, bytes(c)], [T_TBL, lvl + 1, tb]]
    for ri, r in enumerate(t.rows):
        for ci, cell in enumerate(r):
            paras = t.cell_paras(ri, ci)
            L = bytearray(LIST_CELL_T)
            struct.pack_into('<h', L, 0, len(paras))
            struct.pack_into('<HHHH', L, 8, ci, ri, 1, 1)
            struct.pack_into('<II', L, 16, t.widths[ci], CELL_H if CELL_H else row_heights[ri])
            bf = t.row_bf.get((ri, ci), t.bf)
            struct.pack_into('<H', L, 32, bf)
            struct.pack_into('<I', L, 34, t.widths[ci])
            out.append([T_LIST, lvl + 1, bytes(L)])
            vv = 0
            for p in paras:
                p.vpos = vv
                vv += p.height()
                out += build_para(p, lvl + 1)
    return out


# ---------------------------------------------------------------- inline parsing
def parse_inline(s):
    """'text $eq$ text' -> items"""
    items = []
    for i, part in enumerate(re.split(r'\$', s)):
        if i % 2 == 0:
            if part:
                items.append(('t', part))
        else:
            items.append(('eq', part))
    return items
