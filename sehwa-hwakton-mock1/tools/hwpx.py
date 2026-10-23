import olefile, zlib, struct, sys
def recs(b):
    i=0
    while i<len(b):
        h=struct.unpack_from('<I',b,i); h=h[0]; i+=4
        tag=h&0x3ff; lvl=(h>>10)&0x3ff; sz=h>>20
        if sz==0xfff: sz=struct.unpack_from('<I',b,i)[0]; i+=4
        yield tag,lvl,b[i:i+sz]; i+=sz
def ptext(d):
    s=d.decode('utf-16le','replace'); out=[]; i=0
    while i<len(s):
        c=ord(s[i])
        if c<32:
            if c in (0,10,13,24,25,26,27,28,29,30,31):
                out.append('\n' if c in (10,13) else ''); i+=1
            else:
                ctrl=s[i+1:i+3][::-1] if False else ''
                out.append('⟦%d⟧'%c if c==11 else ('\t' if c==9 else '')); i+=8
        else: out.append(s[i]); i+=1
    return ''.join(out)
if __name__=="__main__":
  o=olefile.OleFileIO(sys.argv[1])
  secs=sorted([e for e in o.listdir() if e[0]=='BodyText'])
  for e in secs:
      b=zlib.decompress(o.openstream('/'.join(e)).read(),-15)
      pending=[]; buf=None
      for tag,lvl,d in recs(b):
          if tag==67:
              t=ptext(d); print(t.rstrip('\n'))
          elif tag==88:
              n=struct.unpack_from('<H',d,4)[0]; scr=d[6:6+2*n].decode('utf-16le','replace')
              print('   $'+scr+'$')
          elif tag==71:
              cid=d[:4][::-1].decode('latin1')
              if cid in('tbl ','gso '): print('   <%s>'%cid.strip())
  