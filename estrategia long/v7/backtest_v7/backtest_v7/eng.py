import numpy as np, pandas as pd
from numba import njit
import data as DT
FEE=0.0006
SLIP={"BTC":0.0004,"ETH":0.0006,"DOGE":0.0010}
FUND8H_LONG=0.00005
TFH={"1h":1.0,"4h":4.0,"1d":24.0}
TRAIN_END=pd.Timestamp("2021-12-31 23:59:59"); VAL_END=pd.Timestamp("2023-12-31 23:59:59")

@njit(cache=True)
def ema_nb(x,n):
    out=np.full(len(x),np.nan); a=2.0/(n+1)
    if len(x)<n: return out
    s=0.0
    for i in range(n): s+=x[i]
    v=s/n; out[n-1]=v
    for i in range(n,len(x)):
        v=a*x[i]+(1-a)*v; out[i]=v
    return out
@njit(cache=True)
def atr_nb(h,l,c,n):
    m=len(c); out=np.full(m,np.nan)
    if m<=n: return out
    tr=np.empty(m); tr[0]=h[0]-l[0]
    for i in range(1,m): tr[i]=max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1]))
    s=0.0
    for i in range(1,n+1): s+=tr[i]
    v=s/n; out[n]=v
    for i in range(n+1,m):
        v=(v*(n-1)+tr[i])/n; out[i]=v
    return out
@njit(cache=True)
def rmax_prev(x,n):
    m=len(x); out=np.full(m,np.nan)
    for i in range(n,m):
        v=x[i-n]
        for j in range(i-n+1,i):
            if x[j]>v: v=x[j]
        out[i]=v
    return out
@njit(cache=True)
def rmin_prev(x,n):
    m=len(x); out=np.full(m,np.nan)
    for i in range(n,m):
        v=x[i-n]
        for j in range(i-n+1,i):
            if x[j]<v: v=x[j]
        out[i]=v
    return out
@njit(cache=True)
def adx_nb(h,l,c,n):
    m=len(c); out=np.full(m,np.nan)
    if m<2*n+2: return out
    tr=np.zeros(m); pdm=np.zeros(m); mdm=np.zeros(m)
    for i in range(1,m):
        up=h[i]-h[i-1]; dn=l[i-1]-l[i]
        pdm[i]=up if (up>dn and up>0) else 0.0
        mdm[i]=dn if (dn>up and dn>0) else 0.0
        tr[i]=max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1]))
    st=0.0; sp=0.0; sm=0.0
    for i in range(1,n+1): st+=tr[i]; sp+=pdm[i]; sm+=mdm[i]
    dx=np.full(m,np.nan)
    for i in range(n,m):
        if i>n:
            st=st-st/n+tr[i]; sp=sp-sp/n+pdm[i]; sm=sm-sm/n+mdm[i]
        pdi=100*sp/st if st>0 else 0.0; mdi=100*sm/st if st>0 else 0.0
        dx[i]=100*abs(pdi-mdi)/(pdi+mdi) if (pdi+mdi)>0 else 0.0
    s=0.0
    for i in range(n,2*n): s+=dx[i]
    v=s/n; out[2*n-1]=v
    for i in range(2*n,m):
        v=(v*(n-1)+dx[i])/n; out[i]=v
    return out

# P: 0 k_init,1 k_trail,2 risk,3 max_lev,4 fee,5 slip,6 stop_extra,7 fund_bar_long,8 tp_atr,9 be_atr,10 max_bars,11 trail_on_atr
@njit(cache=True)
def engine(o,h,l,c,atr,le,se,lx,sx,szm,P,warm,maxt):
    n=len(c); eqc=np.full(n,np.nan); expo=np.zeros(n)
    tr=np.zeros((maxt,9)); nt=0
    k_init=P[0]; k_tr=P[1]; risk=P[2]; mlev=P[3]; fee=P[4]; slip=P[5]; sx_=P[6]; fund=P[7]
    tp_atr=P[8]; be_atr=P[9]; maxb=int(P[10]); tr_on=P[11]
    eq=1.0; pos=0; units=0.0; ef=0.0; stop=0.0; ext=0.0; eqb=1.0; ei=0; szf=0.0; sd=0.0; atr_e=0.0; tp=0.0; trailing=True
    for i in range(n):
        if i<warm:
            eqc[i]=eq; continue
        if pos!=0:
            ex=False; fill=0.0; rs_=1
            if pos==1 and o[i]<=stop:
                fill=o[i]*(1-slip-sx_); ex=True; rs_=0
            elif pos==-1 and o[i]>=stop:
                fill=o[i]*(1+slip+sx_); ex=True; rs_=0
            elif pos==1 and tp>0 and i>ei and c[i-1]>=tp:
                fill=o[i]*(1-slip); ex=True; rs_=3
            elif pos==-1 and tp>0 and i>ei and c[i-1]<=tp:
                fill=o[i]*(1+slip); ex=True; rs_=3
            elif (pos==1 and lx[i-1]) or (pos==-1 and sx[i-1]):
                fill=o[i]*(1-slip) if pos==1 else o[i]*(1+slip); ex=True; rs_=1
            elif maxb>0 and (i-ei)>=maxb:
                fill=o[i]*(1-slip) if pos==1 else o[i]*(1+slip); ex=True; rs_=4
            if ex:
                pnl=pos*units*(fill-ef); eq=eq+pnl-units*fill*fee
                ra=szf*sd*eqb
                tr[nt,0]=ei;tr[nt,1]=i;tr[nt,2]=pos;tr[nt,3]=ef;tr[nt,4]=fill;tr[nt,5]=eq/eqb-1.0
                tr[nt,6]=(eq-eqb)/ra if ra>0 else 0.0; tr[nt,7]=szf; tr[nt,8]=rs_; nt+=1
                pos=0; units=0.0
        if pos==0 and not np.isnan(atr[i-1]) and atr[i-1]>0:
            go=0
            if le[i-1]: go=1
            elif se[i-1]: go=-1
            if go!=0:
                sdv=k_init*atr[i-1]/o[i]
                sz=risk*szm[i-1]/sdv
                if sz>mlev: sz=mlev
                if sz>0 and eq>0:
                    pos=go; szf=sz; sd=sdv; eqb=eq; ei=i
                    ef=o[i]*(1+slip) if pos==1 else o[i]*(1-slip)
                    notional=sz*eq; units=notional/ef; eq=eq-notional*fee
                    stop=ef-pos*k_init*atr[i-1]; ext=ef; atr_e=atr[i-1]
                    tp=(ef+pos*tp_atr*atr[i-1]) if tp_atr>0 else 0.0
                    trailing=(tr_on<=0)
        if pos!=0:
            hit=False
            if pos==1 and l[i]<=stop:
                fill=min(stop,o[i])*(1-slip-sx_); hit=True
            elif pos==-1 and h[i]>=stop:
                fill=max(stop,o[i])*(1+slip+sx_); hit=True
            if hit:
                pnl=pos*units*(fill-ef); eq=eq+pnl-units*fill*fee
                ra=szf*sd*eqb
                tr[nt,0]=ei;tr[nt,1]=i;tr[nt,2]=pos;tr[nt,3]=ef;tr[nt,4]=fill;tr[nt,5]=eq/eqb-1.0
                tr[nt,6]=(eq-eqb)/ra if ra>0 else 0.0; tr[nt,7]=szf; tr[nt,8]=0; nt+=1
                pos=0; units=0.0
        if pos!=0:
            if pos==1:
                eq-=fund*units*c[i]
                if h[i]>ext: ext=h[i]
                if (not trailing) and (ext-ef)>=tr_on*atr_e: trailing=True
                if be_atr>0 and (ext-ef)>=be_atr*atr_e and ef>stop: stop=ef
                if trailing and not np.isnan(atr[i]):
                    ns=ext-k_tr*atr[i]
                    if ns>stop: stop=ns
            else:
                if l[i]<ext: ext=l[i]
                if (not trailing) and (ef-ext)>=tr_on*atr_e: trailing=True
                if be_atr>0 and (ef-ext)>=be_atr*atr_e and ef<stop: stop=ef
                if trailing and not np.isnan(atr[i]):
                    ns=ext+k_tr*atr[i]
                    if ns<stop: stop=ns
            mtm=eq+pos*units*(c[i]-ef); eqc[i]=mtm
            expo[i]=pos*units*c[i]/mtm if mtm>0 else 0.0
        else:
            eqc[i]=eq
    if pos!=0:
        fill=c[n-1]*(1-slip) if pos==1 else c[n-1]*(1+slip)
        pnl=pos*units*(fill-ef); eq=eq+pnl-units*fill*fee; ra=szf*sd*eqb
        tr[nt,0]=ei;tr[nt,1]=n-1;tr[nt,2]=pos;tr[nt,3]=ef;tr[nt,4]=fill;tr[nt,5]=eq/eqb-1.0
        tr[nt,6]=(eq-eqb)/ra if ra>0 else 0.0; tr[nt,7]=szf; tr[nt,8]=2; nt+=1
        eqc[n-1]=eq
    return eqc,expo,tr[:nt]

@njit(cache=True)
def stats_nb(eq,dend,i0,i1,tri,trn):
    base=eq[i0-1] if i0>0 else 1.0
    if np.isnan(base) or base<=0: base=1.0
    mx=1.0; mdd=0.0
    for i in range(i0,i1):
        v=eq[i]/base
        if v>mx: mx=v
        d=v/mx-1.0
        if d<mdd: mdd=d
    total=eq[i1-1]/base-1.0
    s=0.0; s2=0.0; sn=0.0; cnt=0; prev=base
    for k in range(len(dend)):
        j=dend[k]
        if j<i0 or j>=i1: continue
        r=eq[j]/prev-1.0; prev=eq[j]
        s+=r; s2+=r*r; cnt+=1
        if r<0: sn+=r*r
    sh=np.nan; so=np.nan
    if cnt>30:
        m=s/cnt; var=s2/cnt-m*m
        if var>0: sh=m/np.sqrt(var*cnt/(cnt-1))*np.sqrt(365.25)
        if sn>0: so=m/np.sqrt(sn/cnt)*np.sqrt(365.25)
    gp=0.0; gl=0.0; nw=0; ntt=0
    for k in range(trn):
        xi=tri[k,1]
        if xi>=i0 and xi<i1:
            ntt+=1; r=tri[k,5]
            if r>0: gp+=r; nw+=1
            else: gl-=r
    return total,mdd,sh,so,ntt,nw,gp,gl

class Series:
    def __init__(self,asset,tf,df):
        self.a=asset; self.tf=tf; self.df=df
        self.o=df.open.values.astype(np.float64); self.h=df.high.values.astype(np.float64)
        self.l=df.low.values.astype(np.float64); self.c=df.close.values.astype(np.float64)
        self.idx=df.index; self.n=len(df)
        day=(df.index.values.astype("datetime64[D]")).astype(np.int64)
        self.dend=np.flatnonzero(np.r_[day[1:]!=day[:-1],True]).astype(np.int64)
        self.i_tr=int(df.index.searchsorted(TRAIN_END,side="right")); self.i_va=int(df.index.searchsorted(VAL_END,side="right"))
        self.cache={}
    def ind(self,kind,n):
        k=(kind,n)
        if k not in self.cache:
            f={"ema":lambda:ema_nb(self.c,n),"atr":lambda:atr_nb(self.h,self.l,self.c,n),
               "hh":lambda:rmax_prev(self.h,n),"ll":lambda:rmin_prev(self.l,n),
               "hc":lambda:rmax_prev(self.c,n),"lc":lambda:rmin_prev(self.c,n),
               "adx":lambda:adx_nb(self.h,self.l,self.c,n)}[kind]
            self.cache[k]=f()
        return self.cache[k]
    def run(self,sig,k_init,k_trail=None,risk=0.02,mlev=1.0,cost=1.0,tp=0.0,be=0.0,maxb=0,tron=0.0,warm=None,fee=None,slip=None,stopx=None,fund=None):
        n=self.n; z=np.zeros(n,dtype=np.bool_)
        fe=FEE*cost if fee is None else fee; sl=SLIP[self.a]*cost if slip is None else slip
        sxx=sl if stopx is None else stopx; fu=FUND8H_LONG*TFH[self.tf]/8.0*cost if fund is None else fund
        P=np.array([k_init,k_init if k_trail is None else k_trail,risk,mlev,fe,sl,sxx,fu,tp,be,maxb,tron],dtype=np.float64)
        szm=sig.get("szm",np.ones(n))
        return engine(self.o,self.h,self.l,self.c,np.asarray(sig["atr"],dtype=np.float64),
                      np.asarray(sig.get("le",z),dtype=np.bool_),np.asarray(sig.get("se",z),dtype=np.bool_),
                      np.asarray(sig.get("lx",z),dtype=np.bool_),np.asarray(sig.get("sx",z),dtype=np.bool_),
                      np.asarray(szm,dtype=np.float64),P,int(sig.get("warm",250) if warm is None else warm),n//2+10)
    def win(self,w):
        return {"TRAIN":(0,self.i_tr),"VAL":(self.i_tr,self.i_va),"DEV":(0,self.i_va),"OOS":(self.i_va,self.n),"FULL":(0,self.n)}[w]
    def stat(self,eq,trd,w):
        i0,i1=self.win(w)
        if i1-i0<5: return None
        tot,mdd,sh,so,nt,nw,gp,gl=stats_nb(eq,self.dend,i0,i1,trd,len(trd))
        yrs=(self.idx[i1-1]-self.idx[i0]).total_seconds()/86400/365.25
        cagr=(1+tot)**(1/yrs)-1 if (yrs>0.5 and tot>-1) else np.nan
        return dict(ret=tot,cagr=cagr,mdd=mdd,sharpe=sh,sortino=so,trades=nt,win=(nw/nt if nt else np.nan),
                    pf=(gp/gl if gl>0 else (np.inf if gp>0 else np.nan)),calmar=(cagr/abs(mdd) if (mdd<0 and cagr==cagr) else np.nan),yrs=yrs,net=None)

def load_series():
    D,e15=DT.load()
    return {k:Series(k[0],k[1],v) for k,v in D.items()}
