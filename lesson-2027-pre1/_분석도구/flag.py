# 시험지 머리표(학년도·코드번호 표)가 문항 범위에 섞인 문항을 찾는다.
# 사용: python flag.py <기출 HWP 폴더> <out.json>
import sys, os, re, json
sys.path.insert(0, os.path.dirname(__file__))
from seg import parse
G = sys.argv[1]
res = {}
for f in sorted(os.listdir(G)):
    sch = f[:-4]; byb = {}
    for x in parse(f'{G}/{f}'):
        if x['sec'] == 0: byb.setdefault(x['b'], []).append(x)
    starts = [b for b in sorted(byb) if any('en  ' in y['c'] for y in byb[b] if y['lv'] == 0)]
    for i, b0 in enumerate(starts):
        rng = [b0]; b = b0 + 1
        while b in byb and not any('en  ' in y['c'] for y in byb[b] if y['lv'] == 0):
            rng.append(b); b += 1
        nested = ' '.join(y['t'] for k in rng for y in byb[k] if y['lv'] > 0)
        hdr = bool(re.search(r'학년도|코드번호|선택형 \(', nested))
        m = re.search(r'[➀➁➂➃➄①②③④⑤]', nested)
        res[f'{sch}:{b0}'] = dict(n=i+1, hdr=hdr)
json.dump(res, open(sys.argv[2], 'w'), ensure_ascii=False)
bad = [k for k, v in res.items() if v['hdr']]
print(len(res), 'problems; header-mixed:', len(bad)); print(bad)
