import exp10, exp9, numpy as np, pandas as pd, sys
S = exp10.load(True)
def V(name, fam, y): return dict(name=name, fam=fam, p=dict(xref=exp10.B800), x={}, y=y)
VS = [V("estanc 100h->3.0","G2b",dict(st_h=100,st_k=3.0)), V("estanc 150h->3.5","G2b",dict(st_h=150,st_k=3.5)), V("estanc 200h->4.0","G2b",dict(st_h=200,st_k=4.0))]
rows=[]
for v in VS:
    sm,D,res = exp9.trial9(S, v); sm["fam"]=v["fam"]; rows.append(sm)
    print(f"{v['name']:<20}", {tf:(sm[f'E{tf}_tr'],sm[f'E{tf}_va'],sm[f'B{tf}'],sm[f'D{tf}'],sm[f'dMDD_{tf}'],sm[f'dR_{tf}']) for tf in exp9.TFS}, {k:bool(x) for k,x in sm['acc'].items()}); sys.stdout.flush()
pd.DataFrame(rows).to_pickle("round10b.pkl")
