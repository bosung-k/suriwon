import re,json,sys
def seg(path,tag):
    L=open(path).read().split('\n'); P=[]; sec=''; step=''; blank=99; cur=None
    for ln in L:
        s=ln.strip()
        m=re.match(r'\[그림/상자: (\d\d) \| (.*)\]$',s)
        if m: sec=m.group(1)+' '+m.group(2).replace(' | ',' '); cur=None; blank=99; continue
        m=re.match(r'\[그림/상자: (STEP.*)\]$',s)
        if m: step=m.group(1); sec=step; cur=None; blank=99; continue
        if re.match(r'\[그림/상자: \d\d [^|]*\]$',s): blank=99; continue
        if not s: blank+=1; continue
        if blank>=2 or cur is None:
            cur={'id':'%s-%03d'%(tag,len(P)+1),'sec':sec,'text':s}; P.append(cur)
        else: cur['text']+='\n'+s
        blank=0
    return P
allp=[]
for n in ['03','05','06']:
    P=seg('src/n%s.txt'%n,'시너지'+n); print(n,len(P)); allp+=P
json.dump(allp,open('src/newprobs.json','w'),ensure_ascii=False)
with open('src/newcompact.txt','w') as f:
    for p in allp:
        t=re.sub(r'\$\s*','$',p['text']); t=re.sub(r'\s+',' ',t)
        f.write('[%s] (%s) %s\n'%(p['id'],p['sec'],t[:420]))
