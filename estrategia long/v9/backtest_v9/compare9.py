import exp9, data8, numpy as np, pandas as pd, eng, json
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=exp9.load(True); SP=data8.load_all(True,pre=True,etc=False)
V8=exp9.V8; V7=exp9.V7
WIN={"COMUN 2017-08→2026-10":("2017-08-17",None),"COMUN 2017-08→2026-01 (informe V8)":("2017-08-17","2026-01-11"),
     "TRAIN 2017-08→2021":("2017-08-17","2022-01-01"),"VAL 2022-23":("2022-01-01","2024-01-01"),"OOS1 2024→2026-01":("2024-01-01","2026-01-11"),
     "OOS2 2026-01→10":("2026-01-11",None),"ÚLTIMOS 2 AÑOS (2024-01→2026-10)":("2024-01-01",None),"ÚLTIMOS 9 MESES (2026-01-05→2026-10)":("2026-01-05",None)}
rows=[]
def add(tag,ver,tf,wn,m):
    if m is None: return
    rows.append(dict(version=ver,tf=tf,ventana=wn,**{k:m.get(k) for k in ("yrs","ret","cagr","mdd","calmar","sharpe","n","trades_yr","win","pf","pf_usd","avg_ret","med_ret","avgR","avg_win","avg_loss","payoff","hours","expo")}))
for ver,v in (("V7",V7),("V8",V8)):
    exp9.exp8.set_refs(S)
    for tf in exp9.TFS:
        s=S[("ETH",tf)]; eq,ex,trd=exp9.run9(s,v)
        for wn,(a,b) in WIN.items(): add("S",ver,tf,wn,exp9.wstat(s,eq,ex,trd,a,b))
exp9.exp8.set_refs(SP)
for ver,v in (("V7",V7),("V8",V8)):
    s=SP[("ETH","1d")]; eq,ex,trd=exp9.run9(s,v)
    add("P",ver,"1d","1D DESDE 2015-08 (histórico completo, FMP+Binance)",exp9.wstat(s,eq,ex,trd,"2015-08-07",None))
    add("P",ver,"1d","1D PRE 2015-08→2017-08",exp9.wstat(s,eq,ex,trd,"2015-08-07","2017-08-17"))
T=pd.DataFrame(rows); T.to_csv("tabla_TF_normalizada_V7_V8.csv",index=False)
cols=["yrs","ret","cagr","mdd","calmar","n","trades_yr","win","pf","pf_usd","avg_ret","avgR","payoff","hours","expo"]
V=T[T.version=="V8"]
for wn in list(WIN)+["1D DESDE 2015-08 (histórico completo, FMP+Binance)","1D PRE 2015-08→2017-08"]:
    x=V[V.ventana==wn].set_index("tf")[cols]
    print("\n##",wn); print(x.round(3).to_string())
