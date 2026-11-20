"""Emulación de TradingView (semántica Pine) de V6.pine / V7.pine / V8.pine sobre las mismas ventanas y costes. Incluye OOS2 (ya abierto en v8_oos2.py)."""
import numpy as np, pandas as pd, data8, engtv, exp8
from engtv import pine_signals, pine_rma, run_tv, tv_stats
SX=data8.load_all(True,pre=True,etc=False)
TFH={"1h":1.0,"4h":4.0,"1d":24.0}
COSTS={"TV":dict(comm=0.0006,slip_abs=0.02),"REPO":dict(comm=0.0006,slip_frac=0.0006,stop_extra=0.0006,fund8h=0.00005)}
def ref_ok(df,tf,L_h=800.0):
    b=SX[("BTC",tf)]; r=pd.Series(b.c,index=b.idx).reindex(df.index,method="ffill").values.astype(float)
    n=int(max(20,round(L_h*60/(TFH[tf]*60)))); n=max(2,int(round(L_h/TFH[tf]))) if False else int(max(20,round(L_h/TFH[tf])))
    e=pine_rma(np.nan_to_num(r,nan=np.nanmedian(r)),n,True)
    return np.isnan(e)|(r>e)
def sig(df,tf,v8):
    atr,lc=pine_signals(df,TFH[tf])
    if v8: lc=lc&ref_ok(df,tf)
    return atr,lc
rows=[]
for tf in ("1h","4h","1d"):
    df=SX[("ETH",tf)].df; s=SX[("ETH",tf)]
    n5=min(5000,len(df)); i5=len(df)-n5
    i17=s.i_pre if tf=="1d" else 0; io2=s.i_o2
    wins={"TV5000":(i5,len(df)),"FULL17":(i17,len(df)),"OOS2":(io2,len(df))}
    if tf=="1d": wins["DESDE2015"]=(0,len(df))
    for cn,cc in COSTS.items():
        for mm,mmn in ((0,"2x"),(1,"1x-clip")):
            for ver,mode,v8 in (("V6.pine","v6pine",False),("V7.pine","v7pine",False),("V8.pine","v7pine",True)):
                for wn,(i0,i1) in wins.items():
                    sub=df.iloc[i0:i1]
                    if wn in ("TV5000","DESDE2015"):       # TradingView arranca con los indicadores desde cero en su primera barra
                        sg=sig(sub,tf,v8) if not v8 else None
                        if v8:
                            atr,lc=pine_signals(sub,TFH[tf]); lc=lc&ref_ok_sub if False else lc
                            # referencia BTC alineada a la ventana
                            b=SX[("BTC",tf)]; r=pd.Series(b.c,index=b.idx).reindex(sub.index,method="ffill").values.astype(float)
                            nL=int(max(20,round(800.0/TFH[tf]))); e=pine_rma(np.nan_to_num(r,nan=np.nanmedian(r)),nL,True); lc=lc&(np.isnan(e)|(r>e)); sg=(atr,lc)
                        e_,t_=run_tv(sub,TFH[tf],mode,margin_mode=mm,sig=sg,**cc); st=tv_stats(sub,e_,t_)
                    else:                                   # FULL17/OOS2: corrida continua desde el inicio, recorte de ventana
                        sg=sig(df,tf,v8); e_,t_=run_tv(df,TFH[tf],mode,margin_mode=mm,sig=sg,**cc); st=tv_stats(df,e_,t_,i0,i1)
                    rows.append(dict(tf=tf,costes=cn,margen=mmn,version=ver,ventana=wn,desde=str(df.index[i0].date()),hasta=str(df.index[i1-1].date()),**{k:st[k] for k in ("ret","cagr","mdd","trades","calmar","yrs")}))
R=pd.DataFrame(rows); R.to_csv("paridad_pine_V6_V7_V8.csv",index=False)
pd.set_option("display.width",250); pd.set_option("display.max_rows",500)
for cn in ("TV","REPO"):
    P=R[(R.costes==cn)&(R.margen=="2x")].pivot_table(index=["tf","ventana","desde"],columns="version",values=["ret","mdd","trades"],aggfunc="first")
    print("== costes",cn,"(margen 2x) =="); print(P.round(3).to_string())
