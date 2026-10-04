import numpy as np, pandas as pd
import eng
from sigs import hb
DEF=dict(N_h=140,L_h=800,A_h=56,kI=5.0,kT=5.0,short=0,sN_h=None,sL_h=None,xN_h=0,xmode="ll",adx=0,adx_h=14,htf=0,tp=0.0,be=0.0,tron=0.0,
         risk=0.02,mlev=1.0,slope=0,ent="hh",maxb=0,minN=2,minL=2,minA=2)
_HT={}
def htf_ema(S,days):
    key=(S.a,S.tf,days)
    if key in _HT: return _HT[key]
    d=S.df.close.resample("1D").last().dropna()
    e=d.ewm(span=days,adjust=False,min_periods=days).mean(); e.index=e.index+pd.Timedelta(days=1)
    dc=d.copy(); dc.index=dc.index+pd.Timedelta(days=1)
    _HT[key]=(e.reindex(S.idx,method="ffill").values,dc.reindex(S.idx,method="ffill").values); return _HT[key]
def gen(S,p):
    q=dict(DEF); q.update(p); tf=S.tf
    N=hb(q["N_h"],tf,q["minN"]); L=hb(q["L_h"],tf,q["minL"]); A=hb(q["A_h"],tf,q["minA"])
    atr=S.ind("atr",A)*np.sqrt(4.0/eng.TFH[tf]); em=S.ind("ema",L)
    hi=S.ind("hh",N) if q["ent"]=="hh" else S.ind("hc",N)
    le=(S.c>hi)&(S.c>em)
    if q["slope"]:
        k=max(1,L//10); sl=np.r_[np.full(k,np.nan),em[k:]-em[:-k]]; le&=(sl>0)
    warm=max(N,L,A)+5
    if q["adx"]>0: le&=(S.ind("adx",hb(q["adx_h"],tf,2))>q["adx"])
    if q["htf"]>0:
        he,dcl=htf_ema(S,int(q["htf"])); le&=(dcl>he)
    d=dict(atr=atr,le=le,warm=warm)
    if q["short"]:
        sN=hb(q["sN_h"] or q["N_h"],tf,q["minN"]); sL=hb(q["sL_h"] or q["L_h"],tf,q["minL"])
        lo=S.ind("ll",sN) if q["ent"]=="hh" else S.ind("lc",sN); sem=S.ind("ema",sL)
        se=(S.c<lo)&(S.c<sem)
        if q["adx"]>0: se&=(S.ind("adx",hb(q["adx_h"],tf,2))>q["adx"])
        if q["htf"]>0:
            he,dcl=htf_ema(S,int(q["htf"])); se&=(dcl<he)
        d["se"]=se; d["warm"]=max(warm,sN,sL)+5
    if q["xN_h"]>0:
        xN=hb(q["xN_h"],tf,2)
        d["lx"]=(S.c<S.ind("ll" if q["xmode"]=="ll" else "lc",xN))
        if q["short"]: d["sx"]=(S.c>S.ind("hh" if q["xmode"]=="ll" else "hc",xN))
    return d,q
def run(S,p,wins=("TRAIN","VAL","DEV"),cost=1.0):
    d,q=gen(S,p)
    eq,ex,trd=S.run(d,q["kI"],q["kT"],risk=q["risk"],mlev=q["mlev"],cost=cost,tp=q["tp"],be=q["be"],maxb=q["maxb"],tron=q["tron"])
    return {w:S.stat(eq,trd,w) for w in wins},eq,ex,trd
