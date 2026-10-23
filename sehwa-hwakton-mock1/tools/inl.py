import olefile, zlib, struct, sys
sys.path.insert(0,'/tmp/claude-0/-home-user/3d130f6b-3a8a-5690-ab57-9e65f259b155/scratchpad')
from hwpx import recs
EXT={1,2,3,11,12,14,15,16,17,18,21,22,23}; INL={4,5,6,7,8,9,19,20}
def load(p):
    o=olefile.OleFileIO(p)
    secs=sorted([e for e in o.listdir() if e[0]=='BodyText'])
    R=[]
    for e in secs:
        b=o.openstream('/'.join(e)).read()
        try: b=zlib.decompress(b,-15)
        except Exception: pass
        R+=list(recs(b))
    return R
def para_text(R,i):
    l=R[i][1]; j=i+1; txt=None; ctrls=[]
    while j<len(R) and R[j][1]>l:
        if R[j][1]==l+1 and R[j][0]==67: txt=R[j][2]
        if R[j][1]==l+1 and R[j][0]==71: ctrls.append(j)
        j+=1
    out=[]; ci=0
    if txt:
        w=struct.unpack('<%dH'%(len(txt)//2),txt); k=0
        while k<len(w):
            c=w[k]
            if c<32:
                if c in EXT:
                    if ci<len(ctrls): out.append(ctrl_text(R,ctrls[ci]))
                    ci+=1; k+=8; continue
                if c in INL: out.append(' ' if c==9 else ''); k+=8; continue
                if c in (10,13): out.append('\n')
                k+=1; continue
            out.append(chr(c)); k+=1
    return ''.join(out), j
def ctrl_text(R,j):
    cid=R[j][2][:4][::-1].decode('latin1'); l=R[j][1]
    if cid=='eqed':
        d=R[j+1][2]; n=struct.unpack_from('<H',d,4)[0]; return ' $'+d[6:6+2*n].decode('utf-16le','replace')+'$ '
    if cid in ('tbl ','gso '):
        # collect nested paragraphs
        parts=[]; k=j+1
        while k<len(R) and R[k][1]>l:
            if R[k][0]==66:
                t,_=para_text(R,k); parts.append(t.strip())
            k+=1
        inner=' | '.join(p for p in parts if p)
        return '\n[%s: %s]\n'%('표' if cid=='tbl ' else '그림/상자',inner) if inner else '[그림]'
    if cid in ('fn  ','en  '): return ''
    return ''
def dump(p):
    R=load(p); out=[]; i=0
    while i<len(R):
        if R[i][0]==66 and R[i][1]==0:
            t,j=para_text(R,i); out.append(t.rstrip('\n')); i=j
        else: i+=1
    return '\n'.join(out)
if __name__=='__main__':
    print(dump(sys.argv[1]))
