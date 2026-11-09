# 오답DB _제작도구\seg.py와 같은 HWP(BodyText) 파서. 문단 번호(b)가 기출 문항 ID(x:학교:b)의 기준이다.
import olefile,zlib,struct,sys
EXT=(1,2,3,11,12,14,15,16,17,18,21,22,23); INL=(4,5,6,7,8,9,19,20)
def parse(path):
    f=olefile.OleFileIO(path)
    comp=f.openstream('FileHeader').read()[36]&1
    paras=[]
    i=0
    while f.exists(f'BodyText/Section{i}'):
        d=f.openstream(f'BodyText/Section{i}').read()
        if comp:d=zlib.decompress(d,-15)
        p=0; bidx=-1; top=None
        while p<len(d):
            h=struct.unpack('<I',d[p:p+4])[0];tag=h&0x3ff;lv=(h>>10)&0x3ff;sz=h>>20;p+=4
            if sz==0xfff:sz=struct.unpack('<I',d[p:p+4])[0];p+=4
            r=d[p:p+sz];p+=sz
            if tag==66:
                if lv==0: bidx+=1; top=len(paras)
                paras.append(dict(sec=i,lv=lv,b=bidx,t='',c=[],top=top))
            elif tag==67:
                s='';q=0
                while q<len(r):
                    c=struct.unpack('<H',r[q:q+2])[0]
                    if c<32:
                        if c in EXT: s+='\x01';q+=16
                        elif c in INL: q+=16
                        else:
                            if c in(10,13):s+='\n'
                            q+=2
                    else:s+=chr(c);q+=2
                paras[-1]['t']=s
            elif tag==71:
                cid=r[0:4][::-1].decode('latin1')
                for k in range(len(paras)-1,-1,-1):
                    if paras[k]['lv']==lv-1 and '\x01' in paras[k]['t']:
                        s=paras[k]['t'];j=s.index('\x01')
                        paras[k]['t']=s[:j]+('\x02' if cid=='eqed' else '')+s[j+1:]
                        paras[k]['c'].append(cid);break
            elif tag==88:
                n=struct.unpack('<H',r[4:6])[0]
                sc=r[6:6+2*n].decode('utf-16le','ignore').strip()
                for k in range(len(paras)-1,-1,-1):
                    if '\x02' in paras[k]['t']:
                        s=paras[k]['t'];j=s.index('\x02')
                        paras[k]['t']=s[:j]+'$'+sc+'$'+s[j+1:];break
        i+=1
    return paras
