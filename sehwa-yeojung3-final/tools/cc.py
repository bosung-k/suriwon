import cv2, numpy as np, sys
sys.path.insert(0,'.')
from clean import levels, base_clean
def components(k, thr=150, minarea=6):
    a=levels(base_clean('raw_%s.png'%k))
    bw=(a<thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(bw,connectivity=8)
    return a,lab,st,cen,n
def show(k,scale=4,thr=150):
    a,lab,st,cen,n=components(k,thr)
    big=cv2.cvtColor(cv2.resize(a,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC),cv2.COLOR_GRAY2BGR)
    rng=np.random.RandomState(1)
    for i in range(1,n):
        if st[i,4]<6: continue
        col=tuple(int(c) for c in rng.randint(60,255,3)); col=(col[0]//2,col[1],col[2]) 
        x,y,w,h,ar=st[i]
        cv2.rectangle(big,(x*scale,y*scale),((x+w)*scale,(y+h)*scale),(0,160,255),1)
        cv2.putText(big,str(i),(x*scale,y*scale-2),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
    cv2.imwrite('cc_%s.png'%k,big)
    print(k,'components',n-1)
if __name__=='__main__':
    for k in sys.argv[1:]: show(k)
