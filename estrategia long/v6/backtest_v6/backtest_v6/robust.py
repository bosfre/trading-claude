import pandas as pd,numpy as np,sys,eng,gen
import core
from core import GR
TF=sys.argv[1]; TOP=int(sys.argv[2]); G=core.GALL[TF]; SER=eng.load_series()
grids={"N_b":G["N"],"L_b":G["L"],"A_b":G["A"],"sN_b":G["N"],"sL_b":G["L"],"kI":GR["kI"],"kT":GR["kT"],"tp":sorted(set(GR["tp"])),
       "xf":sorted(set(GR["xf"])),"tron":sorted(set(GR["tron"])),"be":sorted(set(GR["be"])),"adx":sorted(set(GR["adx"]))}
d=pd.read_csv(f"search2_{TF}.csv").sort_values("score",ascending=False).head(TOP)
KEYS=["N_b","L_b","A_b","sN_b","sL_b","kI","kT","tp","xf","tron","be","adx","ent","short","slope"]
rows=[]
for _,r in d.iterrows():
    p={k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in KEYS}
    if not p["short"]: p["sN_b"]=G["N"][0]; p["sL_b"]=G["L"][0]    # irrelevantes si no hay cortos
    ns=[]
    for k,g in grids.items():
        if not p["short"] and k in ("sN_b","sL_b"): continue
        if p[k] not in g: continue
        i=g.index(p[k])
        for j in (i-1,i+1):
            if 0<=j<len(g):
                q=dict(p); q[k]=g[j]; ns.append(core.obj(core.evaluate(SER,TF,q)))
    ns=np.array(ns); rows.append(dict(p,score=r.score,nb_med=np.median(ns),nb_p25=np.quantile(ns,.25),nb_min=ns.min(),n_nb=len(ns),
        ethCagr=r.ethCagr,ethMdd=r.ethMdd,ethSh=r.ethSh,ethN=r.ethN,ethTr=r.ethTr,ethVa=r.ethVa))
o=pd.DataFrame(rows); o["robust"]=0.5*o.score+0.5*o.nb_p25
o=o.sort_values("robust",ascending=False); o.to_csv(f"robust_{TF}.csv",index=False)
pd.set_option("display.width",300); pd.set_option("display.max_columns",40)
t=o.head(6).copy()
for k in ("ethCagr","ethMdd","ethTr","ethVa"): t[k]=(t[k]*100).round(1)
print(TF); print(t.round(2).to_string(index=False))
