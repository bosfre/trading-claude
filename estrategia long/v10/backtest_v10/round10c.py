import exp10, exp9, numpy as np, pandas as pd, sys
S = exp10.load(True)
rows=[]
for C in (50,75,100,125,150,200):
    v=dict(name=f"enfria {C}h",fam="G3",p=dict(xref=exp10.B800),x={},y=dict(cool_h=C))
    sm,D,res=exp9.trial9(S,v); sm["C"]=C; rows.append(sm)
    print(f"C={C:<4}", {tf:(sm[f'E{tf}_tr'],sm[f'E{tf}_va'],sm[f'B{tf}'],sm[f'D{tf}'],sm[f'dMDD_{tf}'],sm[f'dR_{tf}']) for tf in exp9.TFS}, {k:bool(x) for k,x in sm['acc'].items()}); sys.stdout.flush()
pd.DataFrame(rows).to_pickle("round10c.pkl")
n1=sum(r["acc"]["1h"] and r["acc"]["4h"] for r in rows); n1h=sum(r["acc"]["1h"] for r in rows); n4h=sum(r["acc"]["4h"] for r in rows)
print(f"\nvalores de C que pasan: 1H {n1h}/6 | 4H {n4h}/6 | ambas a la vez {n1}/6  -> regla: >=4 en ambas")
