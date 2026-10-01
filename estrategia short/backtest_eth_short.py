"""
Backtest reproducible: ETHUSDT SHORT-only (breakdown + chandelier), 15m / 1h / 4h.
Uso:  python backtest_eth_short.py [ruta/ETHUSDT_15m.csv]
Los TF de 1h y 4h se construyen agregando el CSV de 15m (open=primero, high=max, low=min, close=ultimo, volume=suma).
Parametros congelados: EMA 200, ruptura 75, ATR 14 (en barras de 4h, escalados por tiempo), stop 3.5 ATR, riesgo 3 %.
Tramos (fijados a priori): TRAIN 2017-08-17..2021-12-31 | VALIDATION 2022-01-01..2023-12-31 | OOS 2024-01-01..fin.
"""
import sys
import pandas as pd
import numpy as np, pandas as pd, bisect
FEE=0.0005      # 0.05% por lado (taker perps)
SLIP=0.0003     # 0.03% por lado (slippage conservador en ETH)
RISK=0.03       # riesgo por operacion (ver main: congelado por presupuesto de drawdown en TRAIN+VAL)
MAXLEV=2.0      # apalancamiento maximo nocional/equity (fijo a priori)
SPLITS={'TRAIN':('2017-08-17','2021-12-31 23:59:59'),
        'VALIDATION':('2022-01-01','2023-12-31 23:59:59'),
        'OOS':('2024-01-01','2026-01-10 23:59:59')}
BPD={'15m':96,'1h':24,'4h':6}

def atr_rma(h,l,c,n=14):
    pc=np.roll(c,1); pc[0]=c[0]
    tr=np.maximum(h-l,np.maximum(abs(h-pc),abs(l-pc)))
    a=np.empty_like(tr); a[:n]=np.nan; a[n-1]=tr[:n].mean()
    for i in range(n,len(tr)): a[i]=(a[i-1]*(n-1)+tr[i])/n
    return a

FAC={'4h':1,'1h':4,'15m':16}
_atrc={}
def prepare(df, trend_n, look, slope=False, atr_n=14, tf='4h', rx=False):
    f=FAC[tf]; trend_n=int(trend_n*f); look=int(look*f); atr_n=int(atr_n*f)
    o,h,l,c=[df[k].values.astype(float) for k in ('open','high','low','close')]
    ema=df.close.ewm(span=trend_n,adjust=False).mean().values
    ll=df.low.rolling(look).min().shift(1).values          # minimo de las `look` barras PREVIAS
    key=(id(df),atr_n)
    if key not in _atrc: _atrc[key]=atr_rma(h,l,c,atr_n)
    atr=_atrc[key]*np.sqrt(f)   # ATR de barras mas cortas x sqrt(f) = volatilidad equivalente a 4h (raiz del tiempo)
    sig=(c<ema)&(c<ll)
    if slope:
        k=max(1,trend_n//10)
        sig&=(ema<np.roll(ema,k))
    sig&=~np.isnan(atr)&~np.isnan(ll)
    rxa=(c>ema) if rx else np.zeros(len(c),bool)
    return dict(o=o,h=h,l=l,c=c,atr=atr,ema=ema,sig=sig,rx=rxa,idx=df.index)

def backtest(P, i0, i1, m, eq0=1.0):
    """Corto en apertura de la barra siguiente a la senal. Stop chandelier (minimo desde entrada + m*ATR), solo baja.
    Stop intrabarra con gap-through al open. Si SL y datos ambiguos -> SL primero (conservador)."""
    o,h,l,c,atr,sig,rx=P['o'],P['h'],P['l'],P['c'],P['atr'],P['sig'],P['rx']
    sidx=np.flatnonzero(sig).tolist()
    n=i1-i0
    eq_bar=np.full(n,eq0,dtype=float)
    eq=eq0; trades=[]; i=i0
    last_eq_i=i0
    while i<i1-1:
        p=bisect.bisect_left(sidx,i)
        if p>=len(sidx): break
        j=sidx[p]                       # barra de senal (cierre)
        e=j+1                           # barra de entrada (open)
        if e>=i1: break
        eq_bar[last_eq_i-i0:e-i0]=eq
        entry_raw=o[e]; entry=entry_raw*(1-SLIP)
        stp=c[j]+m*atr[j]              # stop inicial conocido al cierre de la senal (replicable en Pine)
        dist=m*atr[j]/c[j]
        notional=min(MAXLEV*eq, RISK*eq/dist)
        qty=notional/entry
        fee_in=FEE*notional
        lo=entry_raw
        k=e; exit_px=None; reason=None
        while True:
            if o[k]>=stp:
                exit_raw=o[k]; reason='gap'; break
            if h[k]>=stp:
                exit_raw=stp; reason='stop'; break
            if k==i1-1:
                exit_raw=c[k]; reason='eos'; break
            lo=min(lo,l[k])
            stp=min(stp,lo+m*atr[k])
            if rx[k]:
                exit_raw=o[k+1]; reason='regime'; k+=1; break
            eq_bar[k-i0]=eq-fee_in+qty*(entry-c[k])
            k+=1
        exit_fill=exit_raw*(1+SLIP)
        pnl=qty*(entry-exit_fill)-fee_in-FEE*qty*exit_fill
        eq_new=eq+pnl
        eq_bar[k-i0]=eq_new
        trades.append(dict(entry_i=e,exit_i=k,entry=entry,exit=exit_fill,pnl=pnl,ret=pnl/eq,reason=reason,bars=k-e+1,notional=notional))
        eq=eq_new; last_eq_i=k+1; i=k       # senal en la barra de salida permite reentrada en k+1
    if last_eq_i-i0<n: eq_bar[last_eq_i-i0:]=eq
    return eq_bar, pd.DataFrame(trades)

def metrics(eq_bar, trades, idx, tf, eq0=1.0):
    ret=eq_bar[-1]/eq0-1
    peak=np.maximum.accumulate(eq_bar); dd=(eq_bar/peak-1).min()
    s=pd.Series(eq_bar,index=idx).resample('1D').last().dropna()
    dr=s.pct_change().dropna()
    sharpe=dr.mean()/dr.std()*np.sqrt(365) if dr.std()>0 else 0
    dn=dr[dr<0]; sortino=dr.mean()/np.sqrt((dn**2).mean())*np.sqrt(365) if len(dn)>0 else 0
    nt=len(trades)
    if nt:
        w=trades.pnl>0; gp=trades.pnl[w].sum(); gl=-trades.pnl[~w].sum()
        pf=gp/gl if gl>0 else np.inf; wr=w.mean()
        exposure=trades.bars.sum()/len(eq_bar)
    else: pf=wr=exposure=0
    yrs=(idx[-1]-idx[0]).days/365.25
    return dict(ret=ret*100,cagr=((1+ret)**(1/yrs)-1)*100 if yrs>0 else 0,dd=dd*100,n=nt,pf=pf,wr=wr*100,sharpe=sharpe,sortino=sortino,expo=exposure*100)

def seg_bounds(P, name):
    a,b=SPLITS[name]; idx=P['idx']
    i0=idx.searchsorted(pd.Timestamp(a)); i1=idx.searchsorted(pd.Timestamp(b),side='right')
    return i0,i1

def run(P, m, name):
    i0,i1=seg_bounds(P,name)
    eq,tr=backtest(P,i0,i1,m)
    return metrics(eq,tr,P['idx'][i0:i1],None),eq,tr


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "ETHUSDT_15m.csv"
    RISK = 0.03                                   # riesgo por operacion congelado antes de mirar OOS
    base = pd.read_csv(path, parse_dates=["timestamp"]).set_index("timestamp")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    D = {"15m": base}
    for tf, rule in (("1h", "1h"), ("4h", "4h")):
        r = base.resample(rule, label="left", closed="left").agg(agg)
        D[tf] = r[base.close.resample(rule, label="left", closed="left").count() > 0]
    rows = []
    for tf in ("15m", "1h", "4h"):
        P = prepare(D[tf], 200, 75, False, 14, tf, False)
        for seg in ("TRAIN", "VALIDATION", "OOS"):
            r, eq, tr = run(P, 3.5, seg)
            r.update(tf=tf, seg=seg)
            rows.append(r)
    pd.set_option("display.width", 200)
    print(pd.DataFrame(rows)[["tf", "seg", "ret", "cagr", "dd", "n", "pf", "wr", "sharpe", "sortino", "expo"]].round(2).to_string(index=False))
