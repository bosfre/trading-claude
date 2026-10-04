import pandas as pd,numpy as np,eng,gen
pd.set_option("display.width",300); pd.set_option("display.max_columns",50)
SER=eng.load_series()
V3=dict(N_h=140,L_h=800,A_h=56,kI=5.0,kT=5.0,minN=5,minL=20,minA=10,ent="hh")
rows=[]
for name,ch in (("V3",{}),("V3+TP20",dict(tp=20))):
    for rk in (0.02,0.03,0.04,0.05,0.06,0.08,0.10):
        for tf in ("1h","4h","1d"):
            for a in ("ETH","BTC","DOGE"):
                m,eq,ex,trd=gen.run(SER[(a,tf)],dict(V3,**ch,risk=rk,mlev=2.0),wins=("DEV","OOS","FULL"))
                e=ex.copy(); lev=np.nanmean(np.abs(e[e!=0])) if (e!=0).any() else np.nan
                for w in ("DEV","OOS","FULL"): rows.append(dict(ver=name,risk=rk,tf=tf,asset=a,w=w,lev=lev,**m[w]))
R=pd.DataFrame(rows); R.to_pickle("risk.pkl")
for w in ("DEV","OOS"):
    t=R[(R.w==w)&(R.asset=="ETH")].copy()
    for c in ("ret","cagr","mdd"): t[c]=(t[c]*100).round(1)
    print(f"\n##### ETH {w}: CAGR% / MDD% por riesgo por operación")
    print(t.pivot_table(index=["ver","risk"],columns="tf",values=["cagr","mdd"]).round(1).to_string())
t=R[(R.w=="DEV")&(R.asset=="ETH")&(R.ver=="V3+TP20")].copy(); print("\napalancamiento medio (nocional/equity cuando hay posición), V3+TP20 ETH:"); print(t.pivot_table(index="risk",columns="tf",values="lev").round(2).to_string())
