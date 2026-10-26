"""세화여중3 기말 HWP에 정리한 그림을 문항 위치에 삽입한다 (글자처럼 취급, 가운데 정렬)."""
import sys, zlib, struct, io, random
import olefile, numpy as np, cv2
from PIL import Image
sys.path.insert(0, '.'); sys.path.insert(0, 'mk')
from hwpx import recs
from inl import para_text
from hwpbuild import enc, ctrlchar
from cfb import clone_tree, write_cfb, Node

SRC, OUT = sys.argv[1], sys.argv[2]
FIG = 'fig/'
MM = 7200 / 25.4

# (찾을 문단 앞부분, 그림 파일, 폭 mm, 이후 문단 n개 건너뛰고 삽입)
PLAN = [
    ('$angle rm A = 90 DEG$', 're/01번.png', 34, 0),
    ('그림을 이용하여', 're/02번.png', 46, 0),
    ('삼각형  $rm {ABC}$ 에서 변  $rm {BC}$', 're/04번.png', 40, 0),
    ('정삼각형  $rm {ABC}$', 're/05번.png', 34, 0),
    ('직사각형 모양의 종이', 'o_p6.png', None, 0),
    ('다음 그림과 같이 근총안', 'o_p8.png', None, 1),
    ('원  $rm O$ 의 지름  $rm {AB}$', 'o_p10.png', None, 0),
    ('원 모양의 색종이', 'o_p11.png', None, 0),
    ('$overline {rm {AB}}$ 는 원  $rm O$ 의 지름이고', 'o_p12.png', None, 0),
    ('중심이  $rm O$ 로 같고', 'o_p13.png', None, 0),
    ('원  $rm O$ 에 내접하는 삼각형', 'o_p14.png', None, 0),
    ('직선  $rm {TT}', 'o_p15.png', None, 0),
    ('직각삼각형  $rm {ABC}$ 에서  $overline {rm {AB}}$ 의 길이는', 'o_p16.png', None, 0),
    ('<보기>의 각 도형', 'o_p17.png', 72, 0),
    ('그림은 한 변의 길이가', 're/18번.png', 62, 0),
    ('직사각형  $rm {ABCD}$ 의 둘레', 're/19번.png', 46, 0),
    ('그림과 같이 큰 반원', 're/서답형1.png', 44, 0),
    ('점  $rm O$ 가 중심이고', 're/서답형2.png', 38, 1),
    ('$( 1 )$  [3점]', 're/서답형2_1.png', 27, 0),
    ('$( 2 )$  [3점]', 're/서답형2_2.png', 21, 0),
    ('한 쌍의 대각의 크기의 합', 're/서답형3.png', 30, 0),
    ('직육면체에서', 're/서답형4.png', 36, 0),
]
PHOTO_MM = 0.125   # 사진 1px ≈ 0.125mm (시험지 사진 기준)


def tight(img, pad=4):
    a = np.array(img.convert('L'))
    ys, xs = np.where(a < 200)
    return img.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad + 1, a.shape[1]), min(ys.max() + pad + 1, a.shape[0])))


def load_png(path, width_mm):
    im = Image.open(FIG + path).convert('L')
    im = tight(im)
    if width_mm is None:
        width_mm = im.width * PHOTO_MM
    px = int(round(width_mm / 25.4 * 300))          # 300dpi
    im = im.resize((px, int(round(im.height * px / im.width))), Image.LANCZOS)
    im = im.quantize(6, dither=Image.Dither.NONE)
    bio = io.BytesIO(); im.save(bio, 'PNG', optimize=True)
    return bio.getvalue(), width_mm, width_mm * im.height / im.width


# ---------------------------------------------------------------- template picture records (마플시너지 HWP에서)
def template():
    t = olefile.OleFileIO('src/n05.hwp')
    R = list(recs(t.openstream('BodyText/Section0').read()))
    for i, (tg, l, d) in enumerate(R):
        if tg == 76 and d[:4] == b'cip$' and R[i - 1][0] == 71 and R[i - 1][1] == 1:
            return R[i - 1][2], R[i][2], R[i + 1][2]


T_CTRL, T_SC, T_PIC = template()


def pic_records(bin_id, w, h, inst):
    c = bytearray(T_CTRL[:46])
    attr = 0x042a2311                                      # 글자처럼 취급 (원본 문서의 인라인 그림 속성)
    struct.pack_into('<I', c, 4, attr)
    struct.pack_into('<ii', c, 8, 0, 0)
    struct.pack_into('<ii', c, 16, w, h)
    struct.pack_into('<I', c, 36, inst)
    struct.pack_into('<H', c, 44, 0)
    s = bytearray(T_SC)
    iw, ih = struct.unpack_from('<ii', s, 20)
    struct.pack_into('<iiii', s, 20, w, h, w, h)
    struct.pack_into('<ii', s, 42, w // 2, h // 2)
    struct.pack_into('<6d', s, 100, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0)   # 축소 행렬 → 1
    p = bytearray(T_PIC)
    for off in range(0, len(p) - 3):
        v = struct.unpack_from('<i', p, off)[0]
        if v == iw: struct.pack_into('<i', p, off, w)
        elif v == ih: struct.pack_into('<i', p, off, h)
    # BinData ID: 원본 ID 위치 찾기 (밝기/명암/효과 뒤 2바이트)
    struct.pack_into('<H', p, 71, bin_id)
    return [(71, 1, bytes(c)), (76, 2, bytes(s)), (85, 3, bytes(p))]




def blank_hdr():
    return None


# ---------------------------------------------------------------- main
o = olefile.OleFileIO(SRC)
R = [list(r) for r in recs(zlib.decompress(o.openstream('BodyText/Section0').read(), -15))]
D = [list(r) for r in recs(zlib.decompress(o.openstream('DocInfo').read(), -15))]

# 문단 목록
paras = []
i = 0
while i < len(R):
    if R[i][0] == 66 and R[i][1] == 0:
        t, j = para_text(R, i); paras.append((i, j, t.strip())); i = j
    else:
        i += 1

def is_blank(k):
    i, j, t = paras[k]
    return t == '' and (j - i) <= 3

bins = []
inserts = {}     # para index → (records to insert after, n blanks to delete)
used = set()
start = 0
for key, path, wmm, skip in PLAN:
    k = next(k for k in range(start if key.startswith('$(') else 0, len(paras)) if k not in used and paras[k][2].startswith(key))
    used.add(k)
    if key.startswith('점  $rm O$ 가'):
        start = k
    data, wmm, hmm = load_png(path, wmm)
    bins.append(data)
    bid = len(bins)
    w, h = int(round(wmm * MM)), int(round(hmm * MM))
    hdr = bytearray(R[paras[k][0]][2])
    nh = bytearray(24)
    struct.pack_into('<IIHBBHHHI', nh, 0, 9, 1 << 11, 16, 0, 0, 1, 0, 0, 0)
    txt = struct.pack('<9H', *ctrlchar(11, 'gso '), 13)
    cs = struct.pack('<II', 0, 17)
    ls = struct.pack('<iiiiiiiiI', 0, 0, h, h, int(h * 0.85), 600, 0, 29000, 0x60000)
    recs_new = [(66, 0, bytes(nh)), (67, 1, txt), (68, 1, cs), (69, 1, ls)] + pic_records(bid, w, h, random.randint(1 << 20, 1 << 30))
    pos = k + skip
    # 그림 높이만큼 뒤따르는 빈 줄 삭제
    nblank = int(hmm / 6.2)
    inserts[pos] = (recs_new, nblank)
    print('%-28s → para %d  %.0fx%.0fmm  bin %d  del %d' % (path, pos, wmm, hmm, bid, nblank))

out = []
pending_del = 0
for k, (i, j, t) in enumerate(paras):
    if pending_del and is_blank(k):
        pending_del -= 1
        continue
    if not is_blank(k):
        pass
    out.extend(R[i:j])
    if k in inserts:
        rn, nb = inserts[k]
        out.extend([list(r) for r in rn])
        # 같은 문항의 선택지 뒤 빈 줄부터 지운다
        pending_del = nb
# 문단 밖 레코드(문서 끝) 보존
last_j = paras[-1][1]
out.extend(R[last_j:])
# 마지막 문단 표시 유지
for idx in range(len(out) - 1, -1, -1):
    if out[idx][0] == 66 and out[idx][1] == 0:
        d = bytearray(out[idx][2]); struct.pack_into('<I', d, 0, struct.unpack_from('<I', d, 0)[0] | 0x80000000); out[idx][2] = bytes(d); break
for idx in range(len(out)):
    if out[idx][0] == 66 and out[idx][1] == 0 and idx != max(q for q in range(len(out)) if out[q][0] == 66 and out[q][1] == 0):
        d = bytearray(out[idx][2]); struct.pack_into('<I', d, 0, struct.unpack_from('<I', d, 0)[0] & 0x7fffffff); out[idx][2] = bytes(d)

# DocInfo: BIN_DATA 레코드 + ID_MAPPINGS
im_idx = next(k for k, r in enumerate(D) if r[0] == 17)
d = bytearray(D[im_idx][2]); struct.pack_into('<i', d, 0, len(bins)); D[im_idx][2] = bytes(d)
bd = [[18, 1, struct.pack('<HHH', 0x0021, n + 1, 3) + 'png'.encode('utf-16le')] for n in range(len(bins))]
D = D[:im_idx + 1] + bd + D[im_idx + 1:]


def deflate(b):
    c = zlib.compressobj(9, zlib.DEFLATED, -15); return c.compress(b) + c.flush()


root = clone_tree(o, {('BodyText', 'Section0'): deflate(enc(out)), ('DocInfo',): deflate(enc(D))})
bs = Node('BinData', 1)
for n, data in enumerate(bins):
    bs.children.append(Node('BIN%04X.png' % (n + 1), 2, data))
root.children.append(bs)
write_cfb(OUT, root)
print('written', OUT, 'pictures', len(bins))
