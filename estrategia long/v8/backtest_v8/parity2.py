import numpy as np, pandas as pd, data8, engtv
S=data8.load_series8(False); TFH={"1h":1.0,"4h":4.0,"1d":24.0}
TV=dict(comm=0.0006,slip_abs=0.02); REPO=dict(comm=0.0006,slip_frac=0.0006,stop_extra=0.0006,fund8h=0.00005)
pd.set_option("display.width",220)
# --- 1D estilo TradingView: FMP 2015-08 -> 2017-08-16 + Binance
f=pd.read_csv("fmp_eth_1d_old.csv",parse_dates=["date"]).set_index("date")[["open","high","low","close","volume"]]
b=S[("ETH","1d")].df
tv1d=pd.concat([f[f.index<b.index.min()],b])
print("1D TV-like:",tv1d.index.min().date(),"->",tv1d.index.max().date(),len(tv1d),"barras; años",round((tv1d.index.max()-tv1d.index.min()).days/365.25,2))
rows=[]
def go(name,df,tfh,costs,cn,period):
    for mode in ("v6pine","v6_floor","v7pine","py_notp","pyref"):
        e,t=engtv.run_tv(df,tfh,mode,**costs)
        i0=0
        if period is not None: i0=int(df.index.searchsorted(pd.Timestamp(period)))
        st=engtv.tv_stats(df,e,t,i0,len(df)); 
        rows.append(dict(serie=name,costes=cn,desde=str(df.index[i0].date()),modo=mode,ret=st["ret"],cagr=st["cagr"],mdd=st["mdd"],n=st["trades"],calmar=st["calmar"]))
for cn,cc in (("TV",TV),("REPO",REPO)):
    go("ETH 1D 2015-08..2026-01",tv1d,24.0,cc,cn,None)
    go("ETH 1D 2017-08..2026-01",b,24.0,cc,cn,None)
    go("ETH 1D desde 2016-01 (FMP+Binance)",tv1d,24.0,cc,cn,"2016-01-01")
    for tf in ("1h","4h"):
        go(f"ETH {tf.upper()} 2017-08..2026-01",S[("ETH",tf)].df,TFH[tf],cc,cn,None)
R=pd.DataFrame(rows); R.to_csv("parity2_decomp.csv",index=False)
print(R.round(3).to_string(index=False))
