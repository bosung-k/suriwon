import cv2, numpy as np
def base_clean(path):
    img=cv2.imread(path)
    b,g,r=[img[:,:,i] for i in range(3)]
    # red crayon vanishes in the red channel, black print stays dark
    gray=r.copy()
    # remaining crayon tint: reddish and not black underneath
    tint=((r.astype(int)-g.astype(int)>22)&(r>165)).astype(np.uint8)
    tint=cv2.dilate(tint,np.ones((3,3),np.uint8))
    gray[tint>0]=255
    bg=cv2.morphologyEx(gray,cv2.MORPH_CLOSE,np.ones((17,17),np.uint8))
    bg=cv2.GaussianBlur(bg,(0,0),9)
    flat=np.clip(gray.astype(np.float32)/np.maximum(bg,1)*255,0,255)
    return flat.astype(np.uint8)
def levels(a,lo=120,hi=225):
    x=(a.astype(np.float32)-lo)/(hi-lo); return (np.clip(x,0,1)*255).astype(np.uint8)
def grid_view(a,scale=3,step=20):
    big=cv2.resize(a,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    big=cv2.cvtColor(big,cv2.COLOR_GRAY2BGR)
    h,w=a.shape
    for x in range(0,w,step):
        c=(0,0,255) if x%100==0 else (255,180,0)
        cv2.line(big,(x*scale,0),(x*scale,h*scale),c,1)
        if x%40==0: cv2.putText(big,str(x),(x*scale+2,10),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    for y in range(0,h,step):
        c=(0,0,255) if y%100==0 else (255,180,0)
        cv2.line(big,(0,y*scale),(w*scale,y*scale),c,1)
        if y%40==0: cv2.putText(big,str(y),(2,y*scale-2),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    return big
if __name__=='__main__':
    import glob
    for f in sorted(glob.glob('raw_*.png')):
        a=levels(base_clean(f)); k=f[4:-4]
        cv2.imwrite('c1_%s.png'%k,a); cv2.imwrite('g_%s.png'%k,grid_view(a))
