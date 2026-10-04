import pandas as pd,numpy as np,eng,gen,sigs
import final2 as F
pd.set_option("display.width",300); pd.set_option("display.max_columns",60)
SER=F.SER
# ---------------- A) estrés de costes (V6 y V3 en ETH)
print("=== A) COSTES x1 / x2 / x3 (comisión+slippage+funding) — ETH")
rows=[]
for v in ("V3","V6"):
    for tf in ("1h","4h","1d"):
        for c in (1,2,3):
            m,_,_,_=F.run_cfg(v,tf,"ETH",cost=c)
            for w in ("FULL","OOS"): rows.append(dict(ver=v,tf=tf,costes=f"x{c}",w=w,cagr=m[w]["cagr"]*100,mdd=m[w]["mdd"]*100,pf=m[w]["pf"],sharpe=m[w]["sharpe"]))
T=pd.DataFrame(rows).round(2); print(T.pivot_table(index=["ver","tf","costes"],columns="w",values=["cagr","mdd","pf"]).round(1).to_string())
# ---------------- B) remuestreo de operaciones: distribución del MDD y del retorno (V6 ETH FULL)
print("\n=== B) REMUESTREO de operaciones (5.000 simulaciones, mismo nº de operaciones que el FULL) — V6 ETH")
rng=np.random.default_rng(0)
for tf in ("1h","4h","1d"):
    trd=F.EQ[("V6",tf,"ETH")][2]; r=trd[:,5]; n=len(r); yrs=SER[("ETH",tf)].win("FULL"); 
    s=SER[("ETH",tf)]; y=(s.idx[-1]-s.idx[0]).days/365.25
    tots=[];dds=[]
    for _ in range(5000):
        x=rng.choice(r,n,replace=True); e=np.cumprod(1+x); pk=np.maximum.accumulate(np.r_[1,e])[1:]
        tots.append(e[-1]-1); dds.append((e/pk-1).min())
    tots=np.array(tots); dds=np.array(dds)
    cg=(1+tots)**(1/y)-1
    print(f"{tf}: CAGR p5/p50/p95 = {np.percentile(cg,5)*100:.1f}/{np.percentile(cg,50)*100:.1f}/{np.percentile(cg,95)*100:.1f}% | MDD mediana {np.median(dds)*100:.1f}%  p95 (peor 5%) {np.percentile(dds,5)*100:.1f}%  p99 {np.percentile(dds,1)*100:.1f}% | P(CAGR<0)={np.mean(cg<0)*100:.1f}%  (backtest real: MDD {F.R[(F.R.ver=='V6')&(F.R.tf==tf)&(F.R.asset=='ETH')&(F.R.w=='FULL')].mdd.iloc[0]*100:.1f}%)")
# ---------------- C) mezcla de las 3 temporalidades en ETH (1/3 de capital en cada una, rebalanceo diario)
print("\n=== C) MEZCLA 1H+4H+1D (ETH, 1/3 cada una) vs cada TF sola")
def daily(eq,s): 
    e=pd.Series(eq,index=s.idx).dropna(); d=e.resample("1D").last().dropna(); return d.pct_change().dropna()
def pstats(r,t0=None,t1=None):
    r=r.loc[t0:t1] if t0 else r; e=(1+r).cumprod(); y=(r.index[-1]-r.index[0]).days/365.25
    return dict(cagr=e.iloc[-1]**(1/y)-1,mdd=(e/e.cummax()-1).min(),sharpe=r.mean()/r.std()*np.sqrt(365.25),ret=e.iloc[-1]-1)
for v in ("V3","V6"):
    D={tf:daily(F.EQ[(v,tf,"ETH")][0],SER[("ETH",tf)]) for tf in ("1h","4h","1d")}
    M=pd.concat(D,axis=1).dropna(); B=M.mean(axis=1)
    for nm,r,lab in [(k,M[k],k) for k in M]+[("MEZCLA",B,"MEZCLA")]:
        out=[]
        for w,(a,b) in {"DEV":("2017","2023-12-31"),"OOS":("2024-01-01",None),"FULL":(None,None)}.items():
            p=pstats(r,a,b) if a else pstats(r); out.append(f"{w}: CAGR {p['cagr']*100:5.1f}% MDD {p['mdd']*100:6.1f}% Sh {p['sharpe']:.2f}")
        print(f"{v:3s} {lab:7s} "+" | ".join(out))
    print("   correlación diaria entre TFs:",M.corr().round(2).values[np.triu_indices(3,1)])
# ---------------- D) rendimiento anual V6 vs V3 (ETH 4H)
print("\n=== D) RENDIMIENTO POR AÑO (ETH 4H)  —  V3 | V6 | Buy&Hold")
s=SER[("ETH","4h")]; bh=pd.Series(s.c,index=s.idx)
for v in ("V3","V6"):
    e=pd.Series(F.EQ[(v,"4h","ETH")][0],index=s.idx); ye=e.resample("YE").last(); 
    F.__dict__.setdefault("YR",{})[v]=(ye/ye.shift(1)-1).fillna(ye/e.iloc[0]-1)
yb=bh.resample("YE").last(); ybh=(yb/yb.shift(1)-1).fillna(yb/bh.iloc[0]-1)
print(pd.DataFrame({"V3":F.YR["V3"]*100,"V6":F.YR["V6"]*100,"B&H ETH":ybh*100}).round(1).set_axis(lambda i:None if False else i.year if hasattr(i,'year') else i,axis=0).to_string() if False else pd.DataFrame({"V3 %":F.YR["V3"]*100,"V6 %":F.YR["V6"]*100,"Buy&Hold %":ybh*100}).round(1).assign(año=lambda d:d.index.year).set_index("año").to_string())
