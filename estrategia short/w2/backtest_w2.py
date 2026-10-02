"""
w2 - Backtest reproducible: ETHUSDT SHORT-only (breakdown + regimen EMA 600 + chandelier), 15m / 1h / 4h.
Uso:  python backtest_w2.py [ruta/ETHUSDT_15m.csv]
1h y 4h se construyen agregando el CSV de 15m. Parametros en barras de 4h, escalados por tiempo (x4 en 1h, x16 en 15m).
w2 = w1 con una unica modificacion: EMA de tendencia 200 -> 600. Todo lo demas igual (ruptura 75, ATR 14, stop 3.5 ATR, riesgo 3 %).
Tramos (fijados a priori): TRAIN 2017-08-17..2021-12-31 | VALIDATION 2022-01-01..2023-12-31 | OOS 2024-01-01..2026-01-10.
Las funciones tp/tight/momx/ext del motor son variantes PROBADAS Y DESCARTADAS; w2 no las usa.
"""
import sys
import numpy as np, pandas as pd, bisect
FEE=0.0005; SLIP=0.0003; RISK=0.03; MAXLEV=2.0
SPLITS={'TRAIN':('2017-08-17','2021-12-31 23:59:59'),'VALIDATION':('2022-01-01','2023-12-31 23:59:59'),
        'OOS':('2024-01-01','2026-01-10 23:59:59'),'TV':('2017-08-17','2023-12-31 23:59:59'),
        'FULL':('2017-08-17','2026-01-10 23:59:59')}
FAC={'4h':1,'1h':4,'15m':16}

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
    f=FAC[tf]; nt=int(round(trend*f)); nl=int(round(look*f)); na=int(round(atr_n*f))
    o,h,l,c=[df[k].values.astype(float) for k in ('open','high','low','close')]
    ema=df.close.ewm(span=nt,adjust=False).mean().values
    ll=df.low.rolling(nl).min().shift(1).values
    akey=('atr',id(df),na)
    if akey not in _C: _C[akey]=atr_rma(h,l,c,na)
    atr=_C[akey]*np.sqrt(f)
    B=dict(o=o,h=h,l=l,c=c,ema=ema,ll=ll,atr=atr,idx=df.index,nt=nt,f=f,df=df)
    _C[key]=B; return B

def signal(B,slope=False,ext=None,warmup=True):
    c,ema,ll,atr=B['c'],B['ema'],B['ll'],B['atr']
    s=(c<ema)&(c<ll)&~np.isnan(atr)&~np.isnan(ll)
    if warmup: s[:B['nt']]=False          # sin senales hasta que la EMA lleve `emaLen` barras (igual que el Pine)
    if slope:
        k=max(1,B['nt']//10); s&=(ema<np.roll(ema,k))
    if ext is not None:
        s&=((ema-c)/atr<=ext)
    return s

def mom_exit(B,hh=None,ema_len=None):
    f=B['f']; df=B['df']
    if hh is not None:
        n=int(round(hh*f)); mx=df.high.rolling(n).max().shift(1).values
        return B['c']>mx
    if ema_len is not None:
        e=df.close.ewm(span=int(round(ema_len*f)),adjust=False).mean().values
        return B['c']>e
    return None

def backtest(B,sig,i0,i1,m=3.5,tp=None,tight=None,momx=None,risk=None):
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
            if momx is not None and k>e and momx[k]:
                eq_bar[k-i0]=eq-fee_in+qty*(entry-c[k])
                xr=o[k+1]; why='mom'; k+=1; break
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


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "ETHUSDT_15m.csv"
    b15 = pd.read_csv(path, parse_dates=["timestamp"]).set_index("timestamp")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    D = {"15m": b15}
    for tf in ("1h", "4h"):
        r = b15.resample(tf, label="left", closed="left").agg(agg)
        D[tf] = r[b15.close.resample(tf, label="left", closed="left").count() > 0]
    rows = []
    for name, trend in (("w1", 200), ("w2", 600)):
        for tf in ("15m", "1h", "4h"):
            B = base(D[tf], tf, trend, 75, 14); s = signal(B)
            for seg in ("TRAIN", "VALIDATION", "OOS"):
                r, eq, T = run(B, s, seg, m=3.5); r.update(est=name, tf=tf, seg=seg); rows.append(r)
    pd.set_option("display.width", 200)
    print(pd.DataFrame(rows)[["est", "tf", "seg", "ret", "dd", "n", "pf", "wr", "sharpe", "sortino"]].round(2).to_string(index=False))
