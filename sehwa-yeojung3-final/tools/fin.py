import cv2, numpy as np, sys
sys.path.insert(0,'.')
from clean import levels, base_clean
from cc import components
S={}   # k: dict(ids=[...], polys=[(4x coords)...], crop=(x0,y0,x1,y1) in crop coords or None)
exec(open('spec2.py').read())
def build(k, scale=4):
    a,lab,st,cen,n=components(k)
    sp=S[k]; out=a.copy()
    idm=np.isin(lab,sp.get('ids',[])).astype(np.uint8)
    idm=cv2.dilate(idm,np.ones((5,5),np.uint8))
    out[idm>0]=255
    m=np.zeros_like(a)
    for poly in sp.get('polys',[]):
        pts=(np.array(poly,np.float32)/scale).round().astype(np.int32)
        if len(pts)==2: cv2.rectangle(m,tuple(pts[0]),tuple(pts[1]),255,-1)
        else: cv2.fillPoly(m,[pts],255)
    for pl,wd in sp.get('strokes',[]):
        k=sp.get('dk',1.0)
        pts=(np.array(pl,np.float32)*k/scale).round().astype(np.int32)
        cv2.polylines(m,[pts],False,255,max(1,int(round(wd*k/scale))))
    m=cv2.dilate(m,np.ones((3,3),np.uint8)) if sp.get('dil',True) else m
    if sp.get('relines'):
        bw=(a<140).astype(np.uint8)*255
        geo=np.zeros_like(a)
        L=cv2.HoughLinesP(bw,1,np.pi/360,60,minLineLength=sp.get('minlen',45),maxLineGap=3)
        if L is not None:
            for x1,y1,x2,y2 in L.reshape(-1,4): cv2.line(geo,(x1,y1),(x2,y2),255,3)
        Cc=cv2.HoughCircles(cv2.GaussianBlur(a,(5,5),1.5),cv2.HOUGH_GRADIENT,1,60,param1=120,param2=40,minRadius=40,maxRadius=120)
        if Cc is not None:
            for x,y,r in Cc.reshape(-1,3)[:,:3] if Cc.shape[-1]>=3 else []: cv2.circle(geo,(int(round(x)),int(round(y))),int(round(r)),255,4)
        geo=cv2.dilate(geo,np.ones((2,2),np.uint8))
        cv2.imwrite('geo_%s.png'%k,geo)
        m[(geo>0)&(a<170)]=0
    out[m>0]=255
    if sp.get('crayon'):
        im=cv2.imread('raw_%s.png'%k).astype(np.int16)
        d=(im[:,:,2]-im[:,:,1])
        dloc=cv2.medianBlur(np.clip(d+50,0,255).astype(np.uint8),31).astype(np.int16)-50
        cm=((d-dloc)>sp.get('cthr',14))&(im[:,:,2]>sp.get('rmin',112))
        cm=cv2.morphologyEx(cm.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        cm=cv2.dilate(cm,np.ones((3,3),np.uint8))
        out[(cm>0)&(out>sp.get('keepdark',60))]=255
        strong=cv2.dilate(((d-dloc)>sp.get('sthr',24)).astype(np.uint8),np.ones((3,3),np.uint8))
        out[(strong>0)&(out>sp.get('sdark',45))]=255
    if sp.get('redall'):
        im=cv2.imread('raw_%s.png'%k).astype(int); d=(im[:,:,2]-im[:,:,1]).astype(np.uint8) if False else (im[:,:,2]-im[:,:,1])
        rm=(cv2.medianBlur(np.clip(d+20,0,255).astype(np.uint8),3).astype(int)-20>sp.get('rthr',7)).astype(np.uint8)
        rm=cv2.dilate(rm,np.ones((5,5),np.uint8))
        if sp.get('keepdark'): rm[out<sp['keepdark']]=0
        if sp.get('shade'):
            tri=np.zeros_like(a); cv2.fillPoly(tri,[np.array(sp['shade'],np.int32)],255)
            tri_in=cv2.erode(tri,np.ones((7,7),np.uint8))
            base=(tri_in>0)&(rm==0)&(out>110)&(out<235)
            med=np.median(out[base]); sd=out[base].std()
            sel=(rm>0)&(out>110)
            ins=sel&(tri_in>0); outs=(rm>0)&(tri_in==0)&(out>55)
            src=out.copy(); valid=(tri_in>0)&(rm==0)&(out>90)
            todo=ins.copy()
            for dy,dx in [(-28,0),(28,0),(0,-30),(0,30),(-22,22),(22,-22),(-45,10),(45,-10),(-60,0),(60,0),(0,-60),(0,60)]:
                M=np.float32([[1,0,-dx],[0,1,-dy]])  # value at (y,x) taken from (y+dy,x+dx)
                sh=cv2.warpAffine(src,M,(a.shape[1],a.shape[0]),flags=cv2.INTER_NEAREST,borderValue=255)
                shv=cv2.warpAffine(valid.astype(np.uint8),M,(a.shape[1],a.shape[0]),flags=cv2.INTER_NEAREST,borderValue=0)>0
                take=todo&shv
                out[take]=sh[take]; todo&=~take
            out[todo]=int(med)
            out[outs]=255
        elif sp.get('whiten'):
            out[rm>0]=255
        else:
            out=cv2.inpaint(out,rm*255,5,cv2.INPAINT_TELEA)
    tf=np.zeros_like(a)
    for poly in sp.get('texfill',[]):
        pts=(np.array(poly,np.float32)/scale).round().astype(np.int32)
        cv2.fillPoly(tf,[pts],255)
    if tf.any() and sp.get('shade'):
        tri=np.zeros_like(a); cv2.fillPoly(tri,[np.array(sp['shade'],np.int32)],255)
        tri_in=cv2.erode(tri,np.ones((7,7),np.uint8))
        valid=(tri_in>0)&(tf==0)&(out>90)&(out<235)
        todo=(tf>0)&(tri_in>0)
        for dy,dx in [(-26,0),(26,0),(0,-30),(0,30),(-22,22),(22,-22),(-45,10),(45,-10),(-60,0),(60,0)]:
            M=np.float32([[1,0,-dx],[0,1,-dy]])
            sh=cv2.warpAffine(out,M,(a.shape[1],a.shape[0]),flags=cv2.INTER_NEAREST,borderValue=255)
            shv=cv2.warpAffine(valid.astype(np.uint8),M,(a.shape[1],a.shape[0]),flags=cv2.INTER_NEAREST,borderValue=0)>0
            take=todo&shv; out[take]=sh[take]; todo&=~take
    for poly in sp.get('keep',[]):
        km=np.zeros_like(a); pts=(np.array(poly,np.float32)/scale).round().astype(np.int32)
        if len(pts)==2: cv2.rectangle(km,tuple(pts[0]),tuple(pts[1]),255,-1)
        else: cv2.fillPoly(km,[pts],255)
        out[km>0]=a[km>0]
    for poly in sp.get('post',[]):
        km=np.zeros_like(a); pts=(np.array(poly,np.float32)/scale).round().astype(np.int32)
        if len(pts)==2: cv2.rectangle(km,tuple(pts[0]),tuple(pts[1]),255,-1)
        else: cv2.fillPoly(km,[pts],255)
        out[km>0]=255
    if sp.get('binar'): out[out>sp['binar']]=255
    if sp.get('speck'):
        n,lab2,st2,_=cv2.connectedComponentsWithStats((out<150).astype(np.uint8),connectivity=8)
        small=np.isin(lab2,[i for i in range(1,n) if st2[i,4]<=sp['speck']])
        out[small]=255
    lm=np.zeros_like(a)
    for poly in sp.get('light',[]):
        pts=(np.array(poly,np.float32)/scale).round().astype(np.int32)
        if len(pts)==2: cv2.rectangle(lm,tuple(pts[0]),tuple(pts[1]),255,-1)
        else: cv2.fillPoly(lm,[pts],255)
    out[(lm>0)&(out>int(sp.get('lthr',90)))]=255
    ip=np.zeros_like(a)
    for poly in sp.get('inpaint',[]):
        pts=(np.array(poly,np.float32)/scale).round().astype(np.int32)
        if len(pts)==2: cv2.rectangle(ip,tuple(pts[0]),tuple(pts[1]),255,-1)
        else: cv2.fillPoly(ip,[pts],255)
    if ip.any():
        out=cv2.inpaint(out,cv2.dilate(ip,np.ones((3,3),np.uint8)),4,cv2.INPAINT_TELEA)
    # recover soft edges: keep original gray where not erased
    return out
def tight(out, pad=6):
    ys,xs=np.where(out<200); 
    return out[max(ys.min()-pad,0):ys.max()+pad+1, max(xs.min()-pad,0):xs.max()+pad+1]
if __name__=='__main__':
    for k in sys.argv[1:]:
        o=build(k); cv2.imwrite('o_%s.png'%k,o)
        cv2.imwrite('w_%s.png'%k,cv2.resize(o,None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC))
