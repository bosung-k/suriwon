import sys, zlib, struct, olefile
from hwpbuild import recs
EXT = {1,2,3,11,12,14,15,16,17,18,21,22,23}  # extended (8-wchar) ctrl codes with CTRL records
INL = {4,5,6,7,8,9,19,20}
def check(path):
    o=olefile.OleFileIO(path)
    R=recs(zlib.decompress(o.openstream('BodyText/Section0').read(),-15))
    errs=[]
    n=len(R)
    for i,(t,l,d) in enumerate(R):
        if t!=66: continue
        nch,mask=struct.unpack_from('<II',d,0); last=nch>>31; nch&=0x7fffffff
        ncs,nrt,nls=struct.unpack_from('<HHH',d,12)
        # children
        j=i+1; txt=None; pcs=None; pls=None; ctrls=0
        while j<n and R[j][1]>l:
            if R[j][1]==l+1:
                if R[j][0]==67: txt=R[j][2]
                elif R[j][0]==68: pcs=R[j][2]
                elif R[j][0]==69: pls=R[j][2]
                elif R[j][0]==71: ctrls+=1
            j+=1
        if txt is None:
            if nch!=1: errs.append((i,'no text but nch',nch))
            exp_ctrl=0
        else:
            w=struct.unpack('<%dH'%(len(txt)//2),txt)
            if len(w)!=nch: errs.append((i,'nch mismatch',nch,len(w)))
            k=0; exp_ctrl=0; m=0
            while k<len(w):
                c=w[k]
                if c<32:
                    m|=1<<c
                    if c in EXT:
                        exp_ctrl+=1
                        if w[k+7]!=c: errs.append((i,'ctrl not closed',k))
                        k+=8; continue
                    if c in INL:
                        if w[k+7]!=c: errs.append((i,'inline not closed',k))
                        k+=8; continue
                k+=1
            # ids of extended ctrl chars must match the CTRL records, in order
            ids=[]
            kk=0
            while kk<len(w):
                c=w[kk]
                if c<32 and (c in EXT or c in INL):
                    if c in EXT: ids.append(struct.pack('<HH',w[kk+1],w[kk+2]))
                    kk+=8; continue
                kk+=1
            recids=[]
            jj=i+1
            while jj<n and R[jj][1]>l:
                if R[jj][1]==l+1 and R[jj][0]==71: recids.append(R[jj][2][:4])
                jj+=1
            if ids!=recids: errs.append((i,'ctrl id mismatch',ids,recids))
            if (m & ~(1<<13)) != (mask & ~(1<<13)) and (m|(1<<13))!=(mask|(1<<13)): errs.append((i,'mask',hex(m),hex(mask)))
        if ctrls!=exp_ctrl: errs.append((i,'ctrl count',ctrls,exp_ctrl))
        if pcs is None or len(pcs)//8!=ncs: errs.append((i,'pcs count'))
        if pls is None or len(pls)//36!=nls: errs.append((i,'pls count',nls, None if pls is None else len(pls)//36))
    # list headers: paragraph count & last flag
    for i,(t,l,d) in enumerate(R):
        if t==72:
            np_=struct.unpack_from('<h',d,0)[0]
            j=i+1; cnt=0; lastflags=[]
            while j<n and R[j][1]>=l:
                if R[j][1]==l and R[j][0]==66:
                    cnt+=1; lastflags.append(R[j][2][3]>>7)
                elif R[j][1]==l and R[j][0]!=66: break
                j+=1
            if cnt!=np_: errs.append((i,'list para count',np_,cnt))
            if lastflags and (lastflags[-1]!=1 or any(lastflags[:-1])): errs.append((i,'last flags',lastflags))
    return len(R),errs
for p in sys.argv[1:]:
    n,e=check(p); print(p,n,'errors',len(e)); [print('  ',x) for x in e[:20]]
