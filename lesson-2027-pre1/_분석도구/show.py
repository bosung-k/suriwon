# 기출 문항의 본문·조건 상자·미주(정답)를 그대로 본다.
# 사용: python show.py <기출 HWP 폴더> 상문고:37 서초고:196 ...
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
from seg import parse
G = sys.argv[1]
cache = {}
for arg in sys.argv[2:]:
    sch, b0 = arg.split(':'); b0 = int(b0)
    if sch not in cache:
        byb = {}
        for x in parse(f'{G}/{sch}.hwp'):
            if x['sec'] == 0: byb.setdefault(x['b'], []).append(x)
        cache[sch] = byb
    byb = cache[sch]
    rng = [b0]; b = b0 + 1
    while b in byb and not any('en  ' in y['c'] for y in byb[b] if y['lv'] == 0):
        rng.append(b); b += 1
    out = []
    for k in rng:
        for y in byb[k]:
            t = y['t'].replace('\x01', '').replace('\x02', '').strip()
            if t: out.append(('  ' * y['lv']) + t)
    print(f'===== {sch}:{b0}')
    print(re.sub(r'\n+', ' ', '\n'.join(out))[:1500])
