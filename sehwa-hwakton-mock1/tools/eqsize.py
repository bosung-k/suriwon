import re
# widths in HWPUNIT for 11pt equation font (calibrated on 2026 midterm)
IT={'a':525,'b':525,'c':500,'d':525,'e':480,'f':600,'g':525,'h':550,'i':330,'j':330,'k':525,'l':330,'m':900,'n':600,'o':525,'p':525,'q':450,'r':450,'s':420,'t':330,'u':600,'v':525,'w':750,'x':600,'y':525,'z':450,
    'A':825,'B':750,'C':780,'D':830,'E':720,'F':720,'G':830,'H':900,'I':400,'J':480,'K':830,'L':680,'M':975,'N':830,'O':830,'P':700,'Q':830,'R':720,'S':600,'T':650,'U':830,'V':720,'W':1000,'X':825,'Y':825,'Z':680}
RM={'P':640,'E':670,'V':790,'N':790,'C':730,'H':850,'g':550,'A':790,'B':730,'O':790,'k':550,'m':860,'%':900}
SYM={'+':1133,'-':1133,'=':1430,'<':1460,'>':1460,'(':417,')':417,',':375,'.':300,'|':300,'%':900,'∪':1133,'∩':1133,'≤':1133,'≥':1133,'[':417,']':417,'/':500,'!':330,':':400,'×':1133}
KW={'cap':1133,'cup':1133,'le':1510,'leq':1510,'ge':1510,'geq':1510,'times':1133,'cdots':1100,'smallinter':1133,'sigma':650,'alpha':650,'mu':600,'emptyset':824,'subset':1450,'neq':1450,'rarrow':1412,'in':1133,'notin':1133,'pm':1133,'cdot':500,'smallprod':900,'lbrace':602,'rbrace':602,'it':0,'rm':0,'LEFT':0,'RIGHT':0,'``':0}
def tok(s):
    return re.findall(r'[A-Za-z]+|\d+(?:\.\d+)?|\S',s)
class Box:
    def __init__(s,w,up=0,dn=0,sub=False,sup=False,frac=False): s.w=w;s.sup=sup;s.sub=sub;s.frac=frac
def parse(ts,i=0,scale=1.0,rm=False,stop=None):
    items=[]  # list of (w,flags)
    w=0; flags=set()
    while i<len(ts):
        t=ts[i]
        if t=='}':
            return w,flags,i+1
        if t=='{':
            cw,cf,i=parse(ts,i+1,scale,rm); last=('grp',cw,cf); w+=cw; flags|=cf; items.append(last); continue
        if t in('^','_'):
            # script: next group or token
            if i+1<len(ts) and ts[i+1]=='{':
                cw,cf,i=parse(ts,i+2,scale*0.7,rm)
            else:
                cw,cf,i=atom(ts[i+1],scale*0.7,rm),set(),i+2
            w+=cw; flags.add('sup' if t=='^' else 'sub'); flags|=cf; continue
        if t=='over':
            # numerator is last group
            num=items.pop() if items else ('grp',0,set())
            w-=num[1]
            if i+1<len(ts) and ts[i+1]=='{':
                dw,df,i=parse(ts,i+2,scale,rm)
            else:
                dw,df,i=atom(ts[i+1],scale,rm),set(),i+2
            fw=max(num[1],dw)+575*scale
            w+=fw; flags.add('frac'); flags|=num[2]|df; items.append(('grp',fw,set())); continue
        if t=='rm': rm=True; i+=1; continue
        if t=='it': rm=False; i+=1; continue
        if t in ('LEFT','RIGHT'):
            if i+1<len(ts) and ts[i+1] in '{}':
                w+=602*scale; i+=2; continue
            i+=1; continue
        if t=='bar':
            i+=1; continue
        if t=='cases':
            flags.add('cases'); i+=1; continue
        if t=='#':
            flags.add('row'); i+=1; continue
        if t=='&': i+=1; continue
        aw=atom(t,scale,rm); w+=aw; items.append(('a',aw,set())); i+=1
    return w,flags,i
def atom(t,scale,rm):
    if t=='~': return 552*scale
    if t=='`': return 137*scale
    if t in KW: return KW[t]*scale
    if re.fullmatch(r'\d+(\.\d+)?',t):
        return (525*sum(c.isdigit() for c in t)+300*t.count('.'))*scale
    if re.fullmatch(r'[A-Za-z]+',t):
        return sum((RM.get(c,IT.get(c,600)*0.95) if rm else IT.get(c,600)) for c in t)*scale
    return SYM.get(t,600)*scale
def est(s):
    if 'cases' in s:
        pre,body=s.split('cases',1)
        body=body.strip()[1:].rsplit('}',1)[0]
        rows=[r.replace('&',' ') for r in body.split('#')]
        pw=parse(tok(pre))[0] if pre.strip() else 0
        rw=max(parse(tok(r))[0] for r in rows)
        return int(pw+700+rw), 3000*len(rows), 58
    ts=tok(s)
    w,fl,_=parse(ts)
    if 'cases' in fl:
        h,b=4800,60
    elif 'frac' in fl:
        h,b=(2768,68) if ('sup' in fl or 'LEFT (' in s) else (2580,65)
    elif 'sup' in fl and 'sub' in fl: h,b=1538,74
    elif 'sub' in fl: h,b=1350,71
    elif 'sup' in fl: h,b=1313,87
    else: h,b=1125,85
    return int(round(w)),h,b
if __name__=='__main__':
    import json
    E=json.load(open('../w/eqs.json'))
    errs=[]
    for f,s,w,h,fs,b,_ in E:
        if f!='y2026': continue
        ew,eh,eb=est(s)
        errs.append((abs(ew-w)/w,s,w,ew,h,eh))
    errs.sort(reverse=True)
    for e in errs[:25]: print('%.2f'%e[0],e[2],e[3],e[4],e[5],e[1])
    import statistics; print('median',statistics.median(e[0] for e in errs),'mean',statistics.mean(e[0] for e in errs))
