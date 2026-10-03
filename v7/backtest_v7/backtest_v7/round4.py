import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=eng.load_series(); base=exp.eval_variant(S,{})
V={}
for L in (1200,1600,2400):
    V[f"L1 largos solo si c>EMA{L}h"]=dict(lreg=dict(L_h=L,mode="filter"))
    V[f"L1 largos x0.5 si c<EMA{L}h"]=dict(lreg=dict(L_h=L,mode="size",w=0.5))
for L in (400,800): V[f"I salida por régimen c<EMA{L}h"]=dict(rexit=L)
for tp in (0,15,30,40): V[f"T TP={tp} ATR"]=dict(p=dict(tp=float(tp)))
sh=lambda n,l:dict(short=1,sN_h=n,sL_h=l)
for n,l in ((250,2000),(280,1600),(210,1600),(250,1600),(280,2000)):
    V[f"S cortos {n}/{l} x0.5"]=dict(p=sh(n,l),ext=dict(fund_s=-1),sw=.5)
    V[f"S cortos {n}/{l} x0.75"]=dict(p=sh(n,l),ext=dict(fund_s=-1),sw=.75)
rows=[]
for name,v in V.items():
    r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(name,d); rows.append(sm); exp.log_trial(name,sm)
print(pd.DataFrame(rows).to_string(index=False))
