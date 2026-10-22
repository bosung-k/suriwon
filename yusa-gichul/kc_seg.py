import os, json, re
from hx import W
KC = os.path.join(W, 'kc')
keep = json.load(open(os.path.join(KC, 'keep.json'), encoding='utf-8'))
L = json.load(open(os.path.join(KC, 'lines.json'), encoding='utf-8'))
OKP = {'K59': range(1, 7), 'K60': range(22, 28), 'K61': range(1, 7), 'K62': range(22, 28), 'K63': range(25, 31), 'K64': range(19, 25)}
START = re.compile(r'^\s*(?:\[?\s*(?:서\s*[술답논]\s*형|서·논술형)\s*\]?\s*\[?\s*(\d{1,2})|(\d{1,2})\s*[.)．]\s*\S|\[\s*(\d{1,2})\s*\]|(\d{1,2})\s{1,3}[가-힣그다(\[<])')
STAT = re.compile(r'평균|분산|표준편차|산점도|상관|중앙값|최빈값|도수|자료|변량|대푯값|이차함수|이차방정식|인수분해|제곱근|꼭짓점의 좌표|포물선')
probs = []
for e in keep:
    tag = e['tag']
    pages = sorted(k for k in L if k.startswith(tag + '_'))
    if tag in OKP:
        pages = [k for k in pages if int(k[-2:]) in OKP[tag]]
    cur = None; expect = 1
    for k in pages:
        for l in L[k]:
            t = l['t']
            m = START.match(t)
            num = None
            if m:
                num = next(g for g in m.groups() if g)
                num = int(num)
            essay = bool(re.match(r'^\s*\[?\s*(서\s*[술답논]\s*형|서·논술형)', t))
            if m and (essay or 1 <= num <= 30) and not re.match(r'^\s*\d{1,2}\s*[.)]\s*\d', t):
                if cur:
                    probs.append(cur)
                cur = dict(tag=tag, num=('S' if essay else '') + str(num), page=k, col=l['col'], y0=l['y0'], text=t, end=(k, l['col'], l['y1']))
            elif cur:
                cur['text'] += ' ' + t
                cur['end'] = (k, l['col'], l['y1'])
    if cur:
        probs.append(cur)
json.dump(probs, open(os.path.join(KC, 'probs.json'), 'w', encoding='utf-8'), ensure_ascii=False)
rel = {e['tag']: e['rel'] for e in keep}
out = []; last = None
n = 0
for p in probs:
    if STAT.search(p['text']) and not re.search(r'sin|cos|tan|원|접|삼각비', p['text']):
        continue
    if p['tag'] != last:
        out.append('#### %s %s' % (p['tag'], rel[p['tag']].split('\\')[-1])); last = p['tag']
    t = re.sub(r'\s+', ' ', p['text'])
    out.append('%s-%s|%s' % (p['tag'], p['num'], t[:230]))
    n += 1
open(os.path.join(KC, 'probs.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print(len(probs), n, sum(len(x) for x in out))
