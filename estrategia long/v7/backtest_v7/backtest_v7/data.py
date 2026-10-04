import pandas as pd, numpy as np
R="/home/claude/bosfre/trading-claude"
C=f"{R}/csvs"; SH=f"{R}/estrategia short"
U="/root/.claude/uploads/27f45e02-c9e2-5e7f-a8e8-a96824476b24"
AGG={"open":"first","high":"max","low":"min","close":"last","volume":"sum"}
def rd(p): return pd.read_csv(p,parse_dates=["timestamp"]).set_index("timestamp").sort_index()
def rs(b,rule,expect,thr):
    d=b.resample(rule,label="left",closed="left").agg(AGG)
    n=b.close.resample(rule,label="left",closed="left").count()
    return d[n>=thr*expect].dropna()
def new_csv(name):
    d=pd.read_csv(f"{U}/{name}"); d["timestamp"]=pd.to_datetime(d.open_time,unit="ms")
    return d.set_index("timestamp")[["open","high","low","close","volume"]]
def load():
    D={}
    e15=rd(f"{SH}/ETHUSDT_15m.csv")
    D[("ETH","1h")]=rs(e15,"1h",4,1.0); D[("ETH","4h")]=rs(e15,"4h",16,0.75); D[("ETH","1d")]=rs(e15,"1D",96,0.75)
    for a in ("BTC","DOGE"):
        h=rd(f"{C}/{a}USDT_1h.csv"); f=rd(f"{C}/{a}USDT_4h.csv")
        D[(a,"1h")]=h; D[(a,"4h")]=f; D[(a,"1d")]=rs(h,"1D",24,0.75)
    return D,e15
