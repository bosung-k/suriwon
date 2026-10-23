from fractions import Fraction as F
from itertools import product, permutations
def pairings(L):
    if not L: yield []; return
    a=L[0]
    for i in range(1,len(L)):
        rest=L[1:i]+L[i+1:]
        for p in pairings(rest): yield [(a,L[i])]+p
def wins(pairs):  # all win combos, equal prob
    for bits in product([0,1],repeat=len(pairs)):
        yield [p[b] for p,b in zip(pairs,bits)]
def cond(trials):  # trials: list of (prob, met12, final12)
    met=sum(p for p,m,f in trials if m); fin=sum(p for p,m,f in trials if m and f)
    return fin/met
# original 15: 6 teams
def orig15():
    T=[];P=list(pairings(list(range(6))))
    for pr in P:
        for w in wins(pr):
            for bye in w:
                o=[x for x in w if x!=bye]
                for w2 in o:
                    p=F(1,len(P))*F(1,8)*F(1,3)*F(1,2)
                    games=[set(x) for x in pr]+[set(o),{w2,bye}]
                    T.append((p,{0,1} in games,{w2,bye}=={0,1}))
    return cond(T)
# 15-A: 8 teams, random pairing, then winners randomly re-paired, final
def v15a():
    T=[];P=list(pairings(list(range(8))))
    for pr in P:
        for w in wins(pr):
            P2=list(pairings(w))
            for pr2 in P2:
                for w2 in wins(pr2):
                    p=F(1,len(P))*F(1,16)*F(1,len(P2))*F(1,4)
                    games=[set(x) for x in pr+pr2]+[set(w2)]
                    T.append((p,{0,1} in games,set(w2)=={0,1}))
    return cond(T)
# 15-B: 5 teams. (가) random 1 team bye, others 2 pairs. (나) 2 winners play 2nd game. (다) 2nd winner vs bye in final
def v15b():
    T=[]
    for bye in range(5):
        rest=[x for x in range(5) if x!=bye]; P=list(pairings(rest))
        for pr in P:
            for w in wins(pr):
                for w2 in w:
                    p=F(1,5)*F(1,len(P))*F(1,4)*F(1,2)
                    games=[set(x) for x in pr]+[set(w),{w2,bye}]
                    T.append((p,{0,1} in games,{w2,bye}=={0,1}))
    return cond(T)
print('orig15',orig15(),'15A',v15a(),'15B',v15b())
# 16
def fcond(n,given,event,dom=None):
    X=range(1,n+1); g=e=0
    for f in product(X,repeat=n):
        f=(None,)+f
        if given(f):
            g+=1; e+=event(f)
    return F(e,g),g,e
print('orig16',fcond(5,lambda f:f[1]+f[2]==f[3],lambda f:4 in f[1:]))
print('16A',fcond(5,lambda f:f[1]+f[2]+f[3]==f[4],lambda f:2 in f[1:]))
print('16B',fcond(5,lambda f:f[1]*f[2]==f[3],lambda f:5 in f[1:]))
print('16B2',fcond(5,lambda f:f[1]*f[2]==f[3],lambda f:len(set(f[1:]))==5 ))
print('16A2',fcond(5,lambda f:f[1]+f[2]+f[3]==f[4],lambda f:3 in f[1:]))
