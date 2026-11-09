# content_NN.py 점검: 문항 수, ID 존재(교재 DB / 기출 시작 문단), 출처 표기, 개념 상자에서 버려지는 줄
# 사용: python check_content.py content_02.py srcdb.json gichul.json
import sys, json, runpy, collections
C = runpy.run_path(sys.argv[1])
db = {p['id'] for p in json.load(open(sys.argv[2]))}
gi = json.load(open(sys.argv[3]))
starts = {f'x:{s}:{p["b0"]}' for s, ps in gi.items() for p in ps}
n = 0; src = collections.Counter(); bad = []; seen = set()
for S in C['SECTIONS']:
    print(f"[{S['title']}] {len(S['probs'])}문항  {n+1}–{n+len(S['probs'])}번")
    n += len(S['probs'])
    for lab, pid in S['probs']:
        if pid in seen: bad.append('중복 ' + pid)
        seen.add(pid)
        if pid.startswith('x:'):
            src['x'] += 1
            if pid not in starts: bad.append('기출 시작 문단 아님 ' + pid)
            if pid not in C['GICHUL']: bad.append('GICHUL 표기 없음 ' + pid)
        elif pid.startswith('c:'):
            src['c'] += 1
            if pid[2:] not in C['CUSTOM']: bad.append('CUSTOM 없음 ' + pid)
        else:
            src[pid.split('-')[0].rstrip('0123456789')] += 1
            if pid not in db: bad.append('DB에 없음 ' + pid)
    # lesson_tpl 개념 상자 규칙: 표 뒤 '## ' 없이 오는 줄은 버려진다
    title = None
    for it in S['concept']:
        if isinstance(it, str) and it.startswith('## '): title = it
        elif isinstance(it, str):
            if title is None: bad.append(f"버려지는 줄({S['title']}): {it[:30]}")
        else: title = None
    if S['concept'] and isinstance(S['concept'][0], str) and not S['concept'][0].startswith('## '):
        bad.append(f"첫 줄이 상자 제목 아님({S['title']})")
for k in C['GICHUL']:
    if k not in seen: bad.append('GICHUL에만 있고 안 쓰임 ' + k)
print('총', n, '문항', dict(src))
print('문제:', bad or '없음')
