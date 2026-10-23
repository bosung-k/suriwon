"""오답노트 DB 빌드: 1쪽 목차 + 문항당 1쪽(본문항 + 동형 3문항, 2단 2x2 배치), 정답은 미주."""
import sys, json, struct, zlib, io
sys.argv = [sys.argv[0], '/dev/null'] + sys.argv[1:]
OUTP = sys.argv[2] if len(sys.argv) > 2 else 'db.hwp'

src = open('exam2.py', encoding='utf-8').read()
head = src.split('# ------------------------------------------------------------------ assemble on the form')[0]
G = {'__name__': 'exam2_head'}
exec(compile(head, 'exam2_head', 'exec'), G)
globals().update({k: v for k, v in G.items() if not k.startswith('__')})

rt = src[src.index('def retext'):src.index('NPAGES =')]
exec(rt, globals())
MID = 45300
import db_items
V = db_items.build_variants(G)

# ---------------------------------------------------------------- originals
orig = {i + 1: items[i] for i in range(16)}
for i in range(5):
    orig[17 + i] = short[i]
orig[22] = [SQ('어느 공장에서 생산되는 $rm A$ 제품의 무게는 정규분포 $rm N it (m,~3 ^{2} )$을 따르고, $rm B$ 제품의 무게는 정규분포 $rm N it (2m,~6 ^{2} )$을 따른다고 한다. 이 공장에서 생산된 $rm A$ 제품 중에서 임의추출한 $9$개의 무게의 표본평균을 $bar X$, $rm B$ 제품 중에서 임의추출한 $16$개의 무게의 표본평균을 $bar Y$라 하자.', '12')] + essay[1:]


def LBL(text):
    return Para(P_BLANK, parse_inline(text), st=0)


# ---------------------------------------------------------------- form pieces
o = olefile.OleFileIO(FORM)
R = [list(r) for r in recs(zlib.decompress(o.openstream('BodyText/Section0').read(), -15))]


def find_para(text, start=0):
    from hwpx_text import plain
    for i in range(start, len(R)):
        if R[i][0] == T_PTXT and R[i][1] == 1 and plain(R[i][2]).lstrip().startswith(text):
            return i - 1
    raise KeyError(text)


i_start = find_para('[시작]')
i_end = find_para('※ 답안지')
prefix = R[:i_start]
suffix = R[i_end:]
NP = str(1 + 22)
retext(prefix, {'2026학년도-1학년-공통수학2': '2026학년도-1학년-확률과통계', '공통수학2': '확률과통계', '03': '06',
                '기말고사': '오답노트', '12월 14일': '모의 1회', '1교시': 'DB', '제1학년 재원생 전체': '본문항 + 동형 3문항',
                '배점': '구성', '14문항': '16문항', '67점': '64문항', '계 100점': '총 88문항', '4문항': '5문항',
                '21점': '20문항', '2문항': '1문항', '12점': '4문항',
                '※ 문항별 배점은 각 문항 끝에 표시되어 있습니다.': '※ 한 쪽에 본문항 1개와 동형·유사 3문항, 정답은 미주에 있습니다.',
                '8': NP}, black={17: 4, 18: 0})
retext(suffix, {'8': NP, '※ 답안지와 OMR 카드의 해당란에 필요한 내용을 정확히 기입(표기)했는지 확인하시오.':
                '※ 문항 번호(미주 번호)는 DB 전체에서 이어집니다. 정답은 마지막 쪽 미주에 있습니다.'}, black={17: 4, 18: 0})

body = []
v = [0]
warn = []


def emit(p, split=0):
    if split:
        p.split = split
    p.vpos = v[0]
    body.extend(build_para(p, 0))
    v[0] += p.height()


def blank():
    emit(Para(P_BLANK, [], st=0))


def fill_to(y):
    while v[0] + 1600 <= y:
        blank()


def emit_block(paras, split, where):
    for k, p in enumerate(paras):
        emit(p, split if k == 0 else 0)
    if where == 'top' and v[0] > MID - 200:
        warn.append('overflow top %s: %d' % (paras[0], v[0]))
    if where == 'bot' and v[0] > 2 * MID - 400:
        warn.append('overflow bottom: %d' % v[0])


# ---------------------------------------------------------------- page 1: index
index_lines = []
for n in range(1, 23):
    srcs = ', '.join('%s%s' % (t, g) for t, g, a, ps in V[n])
    index_lines.append('%s %s : %s' % (db_items.LABEL[n], db_items.TYPES[n], srcs))
v[0] = 14067
emit(LBL('[목차] 문항 유형 : 동형·유사 출처 (◎ 동형, ○ 유사)'))
blank()
for k, line in enumerate(index_lines[:11]):
    emit(LBL(line))
v[0] = 9000
for k, line in enumerate(index_lines[11:]):
    emit(LBL(line), 8 if k == 0 else 0)

# ---------------------------------------------------------------- item pages
recs_json = []
for n in range(1, 23):
    lab = db_items.LABEL[n]
    blocks = [[LBL('[본문항 %s] %s' % (lab, db_items.TYPES[n]))] + orig[n]]
    for j, (tag, grade, ans, paras) in enumerate(V[n], 1):
        blocks.append([LBL('[%s-%d %s] %s' % (lab, j, '동형' if grade == '◎' else '유사', tag))] + paras)
    # col 0
    v[0] = 0
    emit_block(blocks[0], 8, 'top')
    fill_to(MID - 200)
    v[0] = MID
    emit_block(blocks[1], 0, 'bot')
    # col 1
    v[0] = 0
    emit_block(blocks[2], 8, 'top')
    fill_to(MID - 200)
    v[0] = MID
    emit_block(blocks[3], 0, 'bot')
    recs_json.append({'no': n, 'label': lab, 'type': db_items.TYPES[n],
                      'problems': [{'role': '본문항', 'source': '2026 세화여고 고1 확통 모의고사 1회 ' + lab,
                                    'answer': db_items.ORIG_ANS[n]}] +
                                  [{'role': '동형' if g == '◎' else '유사', 'source': t, 'answer': a}
                                   for t, g, a, ps in V[n]]})

out_body = prefix + body + suffix
last = max(k for k, r in enumerate(out_body) if r[0] == T_PHDR and r[1] == 0)
d = bytearray(out_body[last][2]); d[11] = 4; out_body[last][2] = bytes(d)

di = [list(r) for r in recs(zlib.decompress(o.openstream('DocInfo').read(), -15))]
cs_idx = [k for k, r in enumerate(di) if r[0] == 21]
white = bytearray(di[cs_idx[7]][2]); white[52:56] = bytes.fromhex('ffffff00')
di.insert(cs_idx[-1] + 1, [21, di[cs_idx[-1]][1], bytes(white)])
for r in di:
    if r[0] == 17:
        dd = bytearray(r[2]); nn = struct.unpack_from('<i', dd, 36)[0]; struct.pack_into('<i', dd, 36, nn + 1); r[2] = bytes(dd)
    if r[0] == 16:
        dd = bytearray(r[2]); dd[14:26] = b'\0' * 12; r[2] = bytes(dd)
fn = [k for k, r in enumerate(out_body) if r[0] == 74]
dd = bytearray(out_body[fn[1]][2]); struct.pack_into('<H', dd, 8, 0x2e); out_body[fn[1]][2] = bytes(dd)
sec = enc(out_body)


def deflate(b):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return c.compress(b) + c.flush()


prv = []
for t, l, dd in out_body:
    if t == T_PTXT:
        s = ''.join(ch for ch in dd.decode('utf-16le', 'ignore') if ord(ch) >= 32 or ch == '\r')
        prv.append(s.replace('\r', '\r\n'))
prvtext = ''.join(prv)[:1000].encode('utf-16le')
from PIL import Image
im = Image.new('RGB', (248, 350), 'white'); bio = io.BytesIO(); im.save(bio, 'PNG')
root = clone_tree(o, {('BodyText', 'Section0'): deflate(sec), ('DocInfo',): deflate(enc(di)),
                      ('PrvText',): prvtext, ('PrvImage',): bio.getvalue()})
write_cfb(OUTP, root)
json.dump(recs_json, open(OUTP.rsplit('.', 1)[0] + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', OUTP, 'endnotes', ENNO[0], 'warnings', len(warn))
for w in warn:
    print(' ', w)
