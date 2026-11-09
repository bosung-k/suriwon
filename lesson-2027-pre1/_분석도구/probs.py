# 기출 HWP 폴더의 모든 문항 시작 문단(미주 위치)과 본문을 JSON으로 뽑는다. lesson.py ext_range와 같은 규칙.
# 사용: python probs.py <기출 HWP 폴더(학교명.hwp)> <out.json>
import sys, re, json, glob, os
sys.path.insert(0, os.path.dirname(__file__))
from seg import parse
INSTR = re.compile(r'답안지|서답형|※|\[서울고/|답만|풀이과정|서술형 답안')
def problems(path):
    byb = {}
    for x in parse(path):
        if x['sec'] == 0: byb.setdefault(x['b'], []).append(x)
    txt = lambda k: ' '.join(y['t'] for y in byb[k]).replace('\x01','').replace('\x02','').strip()
    ctl = lambda k: [c for y in byb[k] for c in y['c']]
    starts = [b for b in sorted(byb) if any('en  ' in y['c'] for y in byb[b] if y['lv'] == 0)]
    out = []
    for b0 in starts:
        rng = [b0]; b = b0 + 1
        while b in byb and not any('en  ' in y['c'] for y in byb[b] if y['lv'] == 0):
            rng.append(b); b += 1
        while len(rng) > 1 and ((not txt(rng[-1]) and not any(c in ('tbl ', 'gso ') for c in ctl(rng[-1]))) or INSTR.search(txt(rng[-1]))):
            rng.pop()
        # main text only of top-level paras (exclude endnote content which is nested at lv>0 in same b)
        main = ' '.join(' '.join(y['t'] for y in byb[k] if y['lv']==0) for k in rng)
        main = main.replace('\x01','').replace('\x02','')
        out.append(dict(b0=b0, b1=rng[-1], text=re.sub(r'\s+',' ',main).strip(), figs=sum(c in('gso ','tbl ') for k in rng for c in ctl(k))))
    return out
if __name__ == '__main__':
    res = {}
    for f in sorted(glob.glob(sys.argv[1] + '/*.hwp')):
        sch = os.path.basename(f)[:-4]
        res[sch] = problems(f)
    json.dump(res, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
    for s, ps in res.items(): print(s, len(ps), [p['b0'] for p in ps])
