import pandas as pd, numpy as np, datetime, json, eng, eng7, exp, lab, v7cfg
pd.set_option("display.width",270); pd.set_option("display.max_columns",60); pd.set_option("display.max_rows",300)
with open("oos_access_log.txt","a") as f:
    f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} OOS DESBLOQUEADO: evaluación única de V7 congelado (cortos selectivos N=270h, EMA=1800h, riesgo cortos x0.5; resto = V6); parámetros elegidos solo con datos <=2023\n")
S=eng.load_series()
V6,V7=v7cfg.V6,v7cfg.V7
V7r45=dict(V7,p=dict(V7["p"],risk=0.045))
VARS={"V6":V6,"V7":V7,"V7@4.5%":V7r45}
WS=("TRAIN","VAL","OOS","FULL")
rows=[]; EQ={}
for a in lab.ASSETS:
    for tf in lab.TFS:
        s=S[(a,tf)]
        for nm,v in VARS.items():
            eq,ex,trd=exp.run_variant(s,v); EQ[(nm,a,tf)]=(eq,ex,trd)
            for w in WS:
                m=s.stat(eq,trd,w); rows.append(dict(ver=nm,asset=a,tf=tf,w=w,ret=m["ret"],cagr=m["cagr"],mdd=m["mdd"],sharpe=m["sharpe"],pf=m["pf"],calmar=m["calmar"],trades=m["trades"],win=m["win"],yrs=m["yrs"]))
R=pd.DataFrame(rows); R.to_pickle("final_R.pkl"); R.to_csv("resultados_v6_vs_v7.csv",index=False)
import pickle; pickle.dump({k:(v[0],v[2]) for k,v in EQ.items()},open("final_EQ.pkl","wb"))
def show(asset,w):
    t=R[(R.asset==asset)&(R.w==w)].copy()
    for c in ("ret","cagr","mdd"): t[c]=(t[c]*100).round(1)
    t["sharpe"]=t.sharpe.round(2); t["pf"]=t.pf.round(2); t["calmar"]=t.calmar.round(2)
    t["o"]=t.ver.map({"V6":0,"V7":1,"V7@4.5%":2}); t=t.sort_values(["tf","o"])
    return t.set_index(["tf","ver"])[["ret","cagr","mdd","sharpe","pf","calmar","trades"]]
for a in ("ETH",):
    for w in ("OOS","FULL","TRAIN","VAL"): print(f"\n######## {a} {w}"); print(show(a,w).to_string())
for a in ("BTC","DOGE"):
    for w in ("OOS","FULL"): print(f"\n######## {a} {w}"); print(show(a,w).loc[(slice(None),["V6","V7"]),:].to_string())
