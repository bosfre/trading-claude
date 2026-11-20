import numpy as np, pandas as pd, data8, engtv
from engtv import pine_signals, pine_rma, run_tv
SX=data8.load_all(True,pre=True,etc=False); TFH={"1h":1.0,"4h":4.0,"1d":24.0}
TV=dict(comm=0.0006,slip_abs=0.02)
def btc_ok(sub,tf,L_h=800.0):
    b=SX[("BTC",tf)]; r=pd.Series(b.c,index=b.idx).reindex(sub.index,method="ffill").values.astype(float)
    n=int(max(20,round(L_h/TFH[tf]))); e=pine_rma(np.nan_to_num(r,nan=np.nanmedian(r)),n,True); return np.isnan(e)|(r>e)
def sig(sub,tf,v8=True):
    atr,lc=pine_signals(sub,TFH[tf]); 
    if v8: lc=lc&btc_ok(sub,tf)
    return atr,lc
def full(eq,tr,i0,i1,cash0=10000.0):
    base=eq[i0-1] if i0>0 else cash0
    e=eq[i0:i1]/base; pk=np.maximum.accumulate(np.r_[1.0,e])[1:]; mdd=float((e/pk-1).min()); ret=float(e[-1]-1)
    sel=[t for t in tr if i0<=t[1]<i1]; r=np.array([t[5] for t in sel]); E=base; pnl=[]
    for x in r: pnl.append(E*x); E*=(1+x)
    pnl=np.array(pnl); gp=pnl[pnl>0].sum(); gl=-pnl[pnl<=0].sum()
    return dict(ret=ret*100,mdd=mdd*100,n=len(sel),win=100*float((r>0).mean()) if len(r) else np.nan,pf=gp/gl if gl>0 else np.nan,gp=gp,gl=gl)
def go(df,tf,i0,fresh,v8=True,mode="v7pine"):
    if fresh:
        sub=df.iloc[i0:]; sg=sig(sub,tf,v8); eq,tr=run_tv(sub,TFH[tf],mode,margin_mode=0,sig=sg,**TV); return full(eq,tr,1,len(sub)),sub
    sg=sig(df,tf,v8); eq,tr=run_tv(df,TFH[tf],mode,margin_mode=0,sig=sg,**TV); return full(eq,tr,i0,len(df)),df
rows=[]
def rec(name,tf,desde,modo,v8,m): rows.append(dict(caso=name,tf=tf,desde=desde,modo=modo,version="V8" if v8 else "V7",**m))
d1=SX[("ETH","1d")].df; d4=SX[("ETH","4h")].df; d1h=SX[("ETH","1h")].df
for v8 in (True,False):
    m,_=go(d1,"1d",0,True,v8); rec("1D histórico completo (2015-08→)","1d","2015-08","arranque limpio",v8,m)
    i17=int(d1.index.searchsorted(pd.Timestamp("2017-08-17"))); m,_=go(d1,"1d",i17,True,v8); rec("1D desde Binance 2017-08","1d","2017-08","arranque limpio",v8,m)
    i=int(d4.index.searchsorted(pd.Timestamp("2024-01-01")))
    m,_=go(d4,"4h",i,False,v8); rec("4H últimos 2 años","4h","2024-01-01","corrida continua recortada",v8,m)
    m,_=go(d4,"4h",i,True,v8); rec("4H últimos 2 años","4h","2024-01-01","arranque limpio",v8,m)
    i=int(d1h.index.searchsorted(pd.Timestamp("2026-01-04")))
    m,_=go(d1h,"1h",i,False,v8); rec("1H últimos 9 meses","1h","2026-01-04","corrida continua recortada",v8,m)
    m,_=go(d1h,"1h",i,True,v8); rec("1H últimos 9 meses","1h","2026-01-04","arranque limpio",v8,m)
R=pd.DataFrame(rows); R.to_csv("emulacion_TV_V8_vs_tus_numeros.csv",index=False)
pd.set_option("display.width",250); print(R.round(2).to_string())
print("\nTUS NÚMEROS TV (V8): 1D completo +2491.84% DD 18% WR 46% PF 1.929 (GP 526424 / GL 272840) | 4H 2024-01→2026-10 +42% DD 14% PF 2.17 | 1H 9 meses +36% DD 12% PF 1.46 n=11")
