import sys,struct,olefile,zlib,json,re
sys.path.insert(0,'/tmp/claude-0/-home-user/3d130f6b-3a8a-5690-ab57-9e65f259b155/scratchpad')
from inl import load, para_text
from hwpx import recs
def numbered_ps(path):
    o=olefile.OleFileIO(path); R=list(recs(zlib.decompress(o.openstream('DocInfo').read(),-15)))
    ps=[d for t,l,d in R if t==25]; out=set()
    for i,d in enumerate(ps):
        a1=struct.unpack_from('<I',d,0)[0]; head=(a1>>23)&3
        if head==2: out.add(i)
    return out
def segment(path, tag):
    nps=numbered_ps(path); R=load(path)
    probs=[]; cur=None; section=''
    i=0
    while i<len(R):
        if R[i][0]==66 and R[i][1]==0:
            t,j=para_text(R,i); ps=struct.unpack_from('<H',R[i][2],8)[0]
            m=re.search(r'\[그림/상자: ([^\]]*?) \| (\d\d)\]',t)
            if m: section=m.group(2)+' '+m.group(1).replace(' | ',' ')
            if ps in nps:
                cur={'id':'%s-%03d'%(tag,len(probs)+1),'sec':section,'start':i,'text':t.strip()}; probs.append(cur)
            elif cur is not None and t.strip() and not t.strip().startswith('[그림/상자:'):
                if t.strip()!='[그림]': cur['text']+='\n'+t.strip()
            i=j
        else: i+=1
    return nps,probs
if __name__=='__main__':
    allp=[]
    for f,tag in [('src/s2_02.hwp','조건부'),('src/s3_01.hwp','확률분포'),('src/s3_02.hwp','추정')]:
        nps,P=segment(f,tag); print(f,'numbered ps',sorted(nps),'problems',len(P))
        allp+=P
    json.dump(allp,open('src/probs.json','w'),ensure_ascii=False,indent=0)
