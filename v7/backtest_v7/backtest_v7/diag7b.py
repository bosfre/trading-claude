import numpy as np, pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
A=pd.read_pickle("A_v6_trades_dev.pkl")
A["half"]=np.where(A.t0<pd.Timestamp("2021-01-01"),"TRAIN(<=2020)","2021-2023")
# percentil dentro de (asset,tf)
for col in ("ext","brk","volr","er","vrel","slope","atrpct"):
    A[col+"_p"]=A.groupby(["asset","tf"])[col].rank(pct=True)
def show(col):
    print(f"\n=== {col}: meanR por tercil DENTRO de cada (activo,tf); columnas = activo/periodo")
    A["t"]=pd.cut(A[col+"_p"],[0,1/3,2/3,1.0001],labels=["bajo","medio","alto"])
    tabs=[]
    for a in ("ETH","BTC","DOGE"):
        g=A[A.asset==a].groupby("t",observed=True).R.mean(); tabs.append(g.rename(a))
    for h in ("TRAIN(<=2020)","2021-2023"):
        g=A[A.half==h].groupby("t",observed=True).R.mean(); tabs.append(g.rename(h))
    g=A.groupby("t",observed=True).R.mean().rename("TODO"); tabs.append(g)
    n=A.groupby("t",observed=True).R.size().rename("n"); tabs.append(n)
    print(pd.concat(tabs,axis=1).round(2).to_string())
for col in ("volr","atrpct","ext","brk","er","slope","vrel"): show(col)
