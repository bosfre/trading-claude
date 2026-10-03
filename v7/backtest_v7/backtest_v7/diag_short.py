import pandas as pd, numpy as np, pickle, eng, exp, lab, v7cfg
pd.set_option("display.width",250); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",200)
S=eng.load_series()
print("=== Contribución de los cortos por año (ETH): suma de retornos de operación (%) y nº; V7 - V6 en retorno anual del equity")
for tf in lab.TFS:
    s=S[("ETH",tf)]
    eq7,ex7,tr7=exp.run_variant(s,v7cfg.V7); eq6,ex6,tr6=exp.run_variant(s,v7cfg.V6)
    T=lab.trade_table(s,dict(lab.V6P,short=1,sN_h=270,sL_h=1800),tr7)
    T["year"]=T.t1.dt.year
    sh=T[T.pos==-1]; lg=T[T.pos==1]
    g=sh.groupby("year").agg(n=("ret","size"),win=("ret",lambda x:(x>0).mean()),sum_ret=("ret",lambda x:x.sum()*100),meanR=("R","mean"))
    y7=exp.yearly(s,eq7); y6=exp.yearly(s,eq6)
    out=pd.concat([g,(y7-y6).rename("dEquity_anual")*100],axis=1).round(2)
    print(f"\n-- ETH {tf}  (cortos: {len(sh)} operaciones totales, win {(sh.ret>0).mean():.0%}, meanR {sh.R.mean():.2f})"); print(out.to_string())
# Detalle de cortos en OOS 1H y 4H
for tf in ("1h","4h"):
    s=S[("ETH",tf)]; eq7,ex7,tr7=exp.run_variant(s,v7cfg.V7)
    T=lab.trade_table(s,dict(lab.V6P,short=1,sN_h=270,sL_h=1800),tr7); sh=T[(T.pos==-1)&(T.xi>=s.i_va)]
    print(f"\n=== Cortos OOS ETH {tf}: {len(sh)} ops")
    print(sh[["t0","t1","ret","R","reason","bars","mfe_atr","mae_atr"]].assign(ret=lambda d:(d.ret*100).round(1),R=lambda d:d.R.round(2),mfe_atr=lambda d:d.mfe_atr.round(1),mae_atr=lambda d:d.mae_atr.round(1)).to_string(index=False))
