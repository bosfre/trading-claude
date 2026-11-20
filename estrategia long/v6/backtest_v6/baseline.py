import eng,sigs,pandas as pd,numpy as np
pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
S=eng.load_series()
CFG={"V3":dict(f=sigs.v3,k=5.0,risk=0.02,mlev=1.0),"V4":dict(f=sigs.v4,k=5.0,risk=0.02,mlev=1.0),
     "V3+corto":dict(f=lambda s:sigs.v3(s,short=True),k=5.0,risk=0.02,mlev=1.0),
     "V5":dict(f=sigs.v5,k=3.5,risk=0.03,mlev=2.0)}
rows=[]
for ver,c in CFG.items():
    for (a,tf),s in S.items():
        eq,ex,trd=s.run(c["f"](s),c["k"],risk=c["risk"],mlev=c["mlev"])
        for w in ("TRAIN","VAL","OOS","FULL"):
            m=s.stat(eq,trd,w); m.update(ver=ver,asset=a,tf=tf,win=w); rows.append(m)
df=pd.DataFrame(rows); df.to_pickle("baseline.pkl")
for w in ("FULL","OOS"):
    t=df[(df.win==w)&(df.asset=="ETH")].copy()
    for c in ("ret","cagr","mdd","win"): t[c]=(t[c]*100).round(1)
    print("\n== ETH",w); print(t.pivot_table(index="tf",columns="ver",values=["ret","cagr","mdd","trades"]).to_string())
