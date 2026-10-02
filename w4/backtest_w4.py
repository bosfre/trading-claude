"""
w4 - Backtest reproducible: ETHUSDT SHORT-only en 1H / 4H / 1D.
Uso:  python backtest_w4.py [ruta/ETHUSDT_15m.csv]
1h, 4h y 1d se construyen agregando el CSV de 15m. Longitudes en barras de 4h, escaladas por tiempo (x4 en 1h, x1/6 en 1d).
w4 = regimen EMA 600 + (ruptura de 45 barras | pullback bajo EMA 40) + filtro de volatilidad (ATR% <= percentil 75 de 750 barras)
     + stop Chandelier 3,5 ATR. Riesgo por operacion: 1H 4 %, 4H 4 %, 1D 5 % (presupuesto de DD <= 25 % en el in-sample).
Tramos (fijados a priori): TRAIN 2017-08-17..2021-12-31 | VALIDATION 2022-01-01..2023-12-31 | OOS 2024-01-01..2026-01-10.
Costes: 0,05 % comision + 0,03 % slippage por lado. Las variantes tp/tight/momx/be/tstop/pyr del motor son pruebas DESCARTADAS.
"""
import sys, json
"""Motor de backtest v2 (w2). Mismo modelo de ejecución que w1 + salidas/filtros opcionales.
Señal al cierre -> entrada en la apertura siguiente. Stop intrabarra (gap al open). Si SL y TP/otra salida
coinciden en la misma barra, manda el SL (conservador). Costes: 0,05 % comisión + 0,03 % slippage por lado."""
import numpy as np, pandas as pd, bisect
FEE=0.0005; SLIP=0.0003; RISK=0.03; MAXLEV=2.0
SPLITS={'TRAIN':('2017-08-17','2021-12-31 23:59:59'),'VALIDATION':('2022-01-01','2023-12-31 23:59:59'),
        'OOS':('2024-01-01','2026-01-10 23:59:59'),'TV':('2017-08-17','2023-12-31 23:59:59'),
        'FULL':('2017-08-17','2026-01-10 23:59:59')}
FAC={'1h':4,'4h':1,'1d':1/6}

def atr_rma(h,l,c,n):
    pc=np.roll(c,1); pc[0]=c[0]
    tr=np.maximum(h-l,np.maximum(abs(h-pc),abs(l-pc)))
    a=np.full(len(tr),np.nan); a[n-1]=tr[:n].mean()
    for i in range(n,len(tr)): a[i]=(a[i-1]*(n-1)+tr[i])/n
    return a

_C={}
def base(df,tf,trend=200,look=75,atr_n=14):
    key=(id(df),tf,trend,look,atr_n)
    if key in _C: return _C[key]
    f=FAC[tf]; rd=lambda x:int(np.floor(x+0.5)); nt=rd(trend*f); nl=rd(look*f); na=max(rd(atr_n*f),14)
    o,h,l,c=[df[k].values.astype(float) for k in ('open','high','low','close')]
    ema=df.close.ewm(span=nt,adjust=False).mean().values
    ll=df.low.rolling(nl).min().shift(1).values
    akey=('atr',id(df),na)
    if akey not in _C: _C[akey]=atr_rma(h,l,c,na)
    atr=_C[akey]*np.sqrt(f)
    B=dict(o=o,h=h,l=l,c=c,ema=ema,ll=ll,atr=atr,idx=df.index,nt=nt,f=f,df=df)
    _C[key]=B; return B

def signal(B,slope=False,ext=None):
    c,ema,ll,atr=B['c'],B['ema'],B['ll'],B['atr']
    s=(c<ema)&(c<ll)&~np.isnan(atr)&~np.isnan(ll)
    s[:B['nt']]=False          # calentamiento: sin senales hasta que la EMA lleve `emaLen` barras (igual que el Pine)
    if slope:
        k=max(1,B['nt']//10); s&=(ema<np.roll(ema,k))
    if ext is not None:
        s&=((ema-c)/atr<=ext)
    return s

def ema_f(B,length):
    return B['df'].close.ewm(span=int(np.floor(length*B['f']+0.5)),adjust=False).mean().values

def signal_dual(B,mid=200):
    s=signal(B); em=ema_f(B,mid); return s&(em<B['ema'])

def signal_pb(B,fast=50):
    c,ema,atr=B['c'],B['ema'],B['atr']; ef=ema_f(B,fast)
    cross=(c<ef)&(np.roll(c,1)>=np.roll(ef,1))
    s=cross&(c<ema)&(ef<ema)&~np.isnan(atr); s[:B['nt']]=False; return s

def mom_exit(B,hh=None,ema_len=None):
    f=B['f']; df=B['df']
    if hh is not None:
        n=int(np.floor(hh*f+0.5)); mx=df.high.rolling(n).max().shift(1).values
        return B['c']>mx
    if ema_len is not None:
        e=df.close.ewm(span=int(np.floor(ema_len*f+0.5)),adjust=False).mean().values
        return B['c']>e
    return None

def backtest(B,sig,i0,i1,m=3.5,tp=None,tight=None,momx=None,risk=None,be=None,tstop=None):
    o,h,l,c,atr=B['o'],B['h'],B['l'],B['c'],B['atr']
    risk=RISK if risk is None else risk
    sidx=np.flatnonzero(sig).tolist(); n=i1-i0
    eq_bar=np.ones(n); eq=1.0; trades=[]; i=i0; last=i0
    while i<i1-1:
        p=bisect.bisect_left(sidx,i)
        if p>=len(sidx): break
        j=sidx[p]; e=j+1
        if e>=i1: break
        eq_bar[last-i0:e-i0]=eq
        er=o[e]; entry=er*(1-SLIP); a0=atr[j]
        stp=c[j]+m*a0; dist=m*a0/c[j]
        notional=min(MAXLEV*eq,risk*eq/dist); qty=notional/entry; fee_in=FEE*notional
        lo=er; hi=er; tpl=(er-tp*a0) if tp else None
        k=e
        while True:
            ok=o[k]
            if ok>=stp: xr=ok; why='gap'; break
            if h[k]>=stp: xr=stp; why='stop'; break
            if tpl is not None:
                if ok<=tpl: xr=ok; why='tp'; break
                if l[k]<=tpl: xr=tpl; why='tp'; break
            if k==i1-1: xr=c[k]; why='eos'; break
            if l[k]<lo: lo=l[k]
            if h[k]>hi: hi=h[k]
            me=m
            if tight is not None and (er-lo)>=tight[0]*a0: me=tight[1]
            ns=lo+me*atr[k]
            if ns<stp: stp=ns
            if be is not None and (er-lo)>=be*a0 and er<stp: stp=er
            wx=None
            if momx is not None and k>e and momx[k]: wx='mom'
            if tstop is not None and (k-e+1)>=tstop[0] and (er-lo)<tstop[1]*a0: wx='time'
            if wx is not None:
                eq_bar[k-i0]=eq-fee_in+qty*(entry-c[k])
                xr=o[k+1]; why=wx; k+=1; break
            eq_bar[k-i0]=eq-fee_in+qty*(entry-c[k])
            k+=1
        lo=min(lo,l[k]); hi=max(hi,h[k])
        xf=xr*(1+SLIP)
        pnl=qty*(entry-xf)-fee_in-FEE*qty*xf
        en=eq+pnl; eq_bar[k-i0]=en
        trades.append((e,k,entry,xf,pnl,pnl/eq,why,k-e+1,(er-lo)/a0,(hi-er)/a0,a0/er))
        eq=en; last=k+1; i=k
    if last-i0<n: eq_bar[last-i0:]=eq
    T=pd.DataFrame(trades,columns=['ei','xi','entry','exit','pnl','ret','why','bars','mfe','mae','atrp'])
    return eq_bar,T

def metrics(eq,T,idx):
    ret=eq[-1]-1; dd=(eq/np.maximum.accumulate(eq)-1).min()
    s=pd.Series(eq,index=idx).resample('1D').last().dropna(); dr=s.pct_change().dropna()
    sh=dr.mean()/dr.std()*np.sqrt(365) if dr.std()>0 else 0
    dn=dr[dr<0]; so=dr.mean()/np.sqrt((dn**2).mean())*np.sqrt(365) if len(dn) else 0
    if len(T):
        w=T.pnl>0; gl=-T.pnl[~w].sum(); pf=T.pnl[w].sum()/gl if gl>0 else np.inf; wr=w.mean()*100
    else: pf=wr=0
    return dict(ret=ret*100,dd=dd*100,n=len(T),pf=pf,wr=wr,sharpe=sh,sortino=so)

def bounds(B,seg,custom=None):
    a,b=custom or SPLITS[seg]; idx=B['idx']
    return idx.searchsorted(pd.Timestamp(a)),idx.searchsorted(pd.Timestamp(b),side='right')

def run(B,sig,seg,**kw):
    i0,i1=bounds(B,seg); eq,T=backtest(B,sig,i0,i1,**kw)
    return metrics(eq,T,B['idx'][i0:i1]),eq,T


import numpy as np, pandas as pd, bisect


def backtest4(B,sig,i0,i1,m=3.5,risk=0.03,pyr=None,LL=None):
    """pyr=dict(A,maxu,radd): anade unidad si cierre < minimo de N barras previas (LL) y beneficio abierto >= A*ATR0."""

    o,h,l,c,atr=B['o'],B['h'],B['l'],B['c'],B['atr']
    sidx=np.flatnonzero(sig).tolist(); n=i1-i0
    eq_bar=np.ones(n); eq=1.0; trades=[]; i=i0; last=i0
    while i<i1-1:
        p=bisect.bisect_left(sidx,i)
        if p>=len(sidx): break
        j=sidx[p]; e=j+1
        if e>=i1: break
        eq_bar[last-i0:e-i0]=eq
        er=o[e]; entry=er*(1-SLIP); a0=atr[j]
        stp=c[j]+m*a0; dist=m*a0/c[j]
        notional=min(MAXLEV*eq,risk*eq/dist)
        units=[[entry,notional/entry,FEE*notional]]
        lo=er; pending=None; k=e
        while True:
            ok=o[k]
            if pending is not None:
                units.append([ok*(1-SLIP),pending[0],FEE*pending[1]]); pending=None
            if ok>=stp: xr=ok; why='gap'; break
            if h[k]>=stp: xr=stp; why='stop'; break
            if k==i1-1: xr=c[k]; why='eos'; break
            if l[k]<lo: lo=l[k]
            ns=lo+m*atr[k]
            if ns<stp: stp=ns
            mtm=eq+sum(u[1]*(u[0]-c[k])-u[2] for u in units)
            eq_bar[k-i0]=mtm
            if pyr is not None and len(units)<pyr['maxu'] and c[k]<LL[k] and (er-c[k])>=pyr['A']*a0:
                da=(stp-c[k])/c[k]
                if da>0:
                    cur=sum(u[1] for u in units)*c[k]; room=MAXLEV*mtm-cur
                    nota=min(pyr['radd']*mtm/da,room)
                    if nota>0: pending=(nota/c[k],nota)
            k+=1
        xf=xr*(1+SLIP)
        pnl=sum(u[1]*(u[0]-xf)-u[2]-FEE*u[1]*xf for u in units)
        en=eq+pnl; eq_bar[k-i0]=en
        trades.append((e,k,pnl,pnl/eq,why,k-e+1,len(units)))
        eq=en; last=k+1; i=k
    if last-i0<n: eq_bar[last-i0:]=eq
    return eq_bar,pd.DataFrame(trades,columns=['ei','xi','pnl','ret','why','bars','units'])

_LL={}
def LLarr(B,N):
    key=(id(B['df']),B['f'],N)
    if key not in _LL: _LL[key]=B['df'].low.rolling(int(np.floor(N*B['f']+0.5))).min().shift(1).values
    return _LL[key]

def make(D,tf,cfg):
    B=base(D[tf],tf,cfg['trend'],cfg['look'],cfg.get('atr_n',14))
    s=signal(B)
    if cfg.get('pb'): s=s|signal_pb(B,cfg['pb'])
    if cfg.get('vol'):                       # filtro de volatilidad: no entrar si ATR% > cuantil q de su historia reciente
        W,q=cfg['vol']; ap=pd.Series(B['atr']/B['c']); w=int(np.floor(W*B['f']+0.5))
        thr=ap.rolling(w,min_periods=w).quantile(q).shift(1).values
        s=s&~(ap.values>thr)
    return B,s

def run4(B,s,seg,cfg,custom=None):
    i0,i1=bounds(B,seg,custom)
    pyr=cfg.get('pyr'); LL=LLarr(B,pyr['N']) if pyr else None
    eq,T=backtest4(B,s,i0,i1,m=cfg.get('m',3.5),risk=cfg.get('risk',0.03),pyr=pyr,LL=LL)
    r=metrics(eq,T.rename(columns={}) if len(T) else T,B['idx'][i0:i1]); return r,eq,T

W3 = {"trend": 600, "look": 45, "pb": 40, "m": 3.5}
W4 = {"trend": 600, "look": 45, "pb": 40, "m": 3.5, "vol": (750, 0.75)}
RISK4 = {"1h": 0.04, "4h": 0.04, "1d": 0.05}
SEGS = {"TRAIN": "TRAIN", "VALIDATION": "VALIDATION", "IS": "TV", "OOS": "OOS", "TOTAL": "FULL"}

def seg_metrics(B, eq, T, i0f, seg):
    i0, i1 = bounds(B, SEGS[seg]); a = i0 - i0f; b = i1 - i0f
    start = eq[a - 1] if a > 0 else 1.0; sub = eq[a:b] / start
    ret = sub[-1] - 1; dd = (sub / np.maximum.accumulate(np.concatenate([[1.0], sub]))[1:] - 1).min()
    t = T[(T.xi >= i0) & (T.xi < i1)]
    w = t.pnl > 0; gl = -t.pnl[~w].sum()
    return dict(ret=ret * 100, dd=dd * 100, pf=(t.pnl[w].sum() / gl if gl > 0 else np.nan), wr=w.mean() * 100 if len(t) else np.nan, n=len(t))

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "ETHUSDT_15m.csv"
    b15 = pd.read_csv(path, parse_dates=["timestamp"]).set_index("timestamp")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    D = {}
    for tf, rule in (("1h", "1h"), ("4h", "4h"), ("1d", "1D")):
        r = b15.resample(rule, label="left", closed="left").agg(agg)
        D[tf] = r[b15.close.resample(rule, label="left", closed="left").count() > 0]
    rows = []
    for name, cfg, rk in (("w3 (riesgo 3 %)", W3, {"1h": .03, "4h": .03, "1d": .03}), ("w4 (riesgo presupuestado)", W4, RISK4)):
        for tf in ("1h", "4h", "1d"):
            B, s = make(D, tf, cfg); i0f, i1f = bounds(B, "FULL")
            eq, T = backtest4(B, s, i0f, i1f, m=cfg["m"], risk=rk[tf])
            for seg in SEGS:
                m = seg_metrics(B, eq, T, i0f, seg); m.update(est=name, tf=tf, seg=seg); rows.append(m)
    pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
    print(pd.DataFrame(rows)[["est", "tf", "seg", "ret", "dd", "pf", "wr", "n"]].round(2).to_string(index=False))
