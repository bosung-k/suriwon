import os, re, json, shutil
import pymupdf
R = r'G:\.shortcut-targets-by-id\1zjN5lpDCrIJeCbtv_y7VKjTRs6xBCqhZ\01.수리원수학학원\200. 중등부\02. 중등 기출\001. 중등 기출(학교 배포)'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work', 'kc')
os.makedirs(OUT, exist_ok=True)
sel = []
for dp, dn, fn in os.walk(R):
    for f in fn:
        p = os.path.join(dp, f)
        rel = p[len(R) + 1:]
        if re.search(r'답안|모범|정답|해설|답지', f):
            continue
        if not f.lower().endswith(('.pdf', '.hwp')):
            continue
        is3 = re.search(r'3학년|3-2|중3|\\3학년\\', rel)
        sem2 = re.search(r'3-2|2학기|2 학기|지필', f)
        if is3 and sem2:
            sel.append(rel)
info = []
for i, rel in enumerate(sorted(sel)):
    tag = 'K%02d' % i
    src = os.path.join(R, rel)
    ext = os.path.splitext(rel)[1].lower()
    dst = os.path.join(OUT, tag + ext)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
    ent = dict(tag=tag, rel=rel)
    if ext == '.pdf':
        d = pymupdf.open(dst)
        txt = ''.join(p.get_text() for p in d)
        ent.update(pages=d.page_count, chars=len(txt), hangul=len(re.findall('[가-힣]', txt)))
        open(os.path.join(OUT, tag + '.txt'), 'w', encoding='utf-8').write(txt)
    info.append(ent)
    print(tag, ent.get('pages'), ent.get('hangul'), rel)
json.dump(info, open(os.path.join(OUT, 'info.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
