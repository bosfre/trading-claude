"""Paridad Pine: V6.pine (tal cual) vs V7.pine, mismas ventanas y costes. Solo datos <= 2026-01-10 (OOS2 sellado)."""
import numpy as np, pandas as pd, data8, engtv, itertools, pickle
S=data8.load_series8(False)
TFH={"1h":1.0,"4h":4.0,"1d":24.0}
COSTS={"TV":dict(comm=0.0006,slip_abs=0.02,slip_frac=0.0,stop_extra=0.0,fund8h=0.0),
       "REPO":dict(comm=0.0006,slip_frac=0.0006,stop_extra=0.0006,fund8h=0.00005,slip_abs=0.0)}
def get_df(tf):
    df=S[("ETH",tf)].df
    return df
def windows(tf,df):
    s=S[("ETH",tf)]
    W={"FULL":(0,len(df)),"TRAIN":(0,s.i_tr),"VAL":(s.i_tr,s.i_va),"OOS1":(s.i_va,len(df))}
    n5=min(5000,len(df)); W["TV5000"]=(len(df)-n5,len(df))
    return W
rows=[]
for tf in ("1h","4h","1d"):
    df=get_df(tf)
    for cn,cc in COSTS.items():
        for mm,mmn in ((0,"2x"),(1,"1x-clip"),(2,"1x-rechaza")):
            for mode in ("v6pine","v7pine"):
                e,t=engtv.run_tv(df,TFH[tf],mode,margin_mode=mm,**cc)
                for wn,(i0,i1) in windows(tf,df).items():
                    # ventanas parciales: re-simular desde i0 con indicadores desde cero (como TradingView) en TV5000; resto = recorte de la corrida completa
                    if wn=="TV5000":
                        sub=df.iloc[i0:i1]; e2,t2=engtv.run_tv(sub,TFH[tf],mode,margin_mode=mm,**cc); st=engtv.tv_stats(sub,e2,t2)
                    else:
                        st=engtv.tv_stats(df,e,t,i0,i1)
                    rows.append(dict(tf=tf,costes=cn,margen=mmn,modo=mode,ventana=wn,**{k:st[k] for k in ("ret","cagr","mdd","trades","calmar","yrs")}))
R=pd.DataFrame(rows); R.to_csv("parity_v6pine_vs_v7pine.csv",index=False)
pd.set_option("display.width",200); pd.set_option("display.max_rows",500)
P=R.pivot_table(index=["tf","costes","margen","ventana"],columns="modo",values=["ret","mdd","trades"])
P.columns=[f"{a}_{b}" for a,b in P.columns]; P["d_ret"]=P.ret_v7pine-P.ret_v6pine
print(P.round(3).to_string())
