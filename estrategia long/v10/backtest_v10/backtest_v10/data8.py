"""V8: datos extendidos. Base = CSV del repo/usuario (hasta 2026-01-10 ETH, 2026-01-06 BTC/DOGE) + tramo nuevo
2026-01-06 -> 2026-10-03 de Twelve Data (1h, mismo UTC; en ETH coincide con Binance al 0,02 % en el solapamiento).
El tramo nuevo (OOS2, desde 2026-01-11) queda SELLADO: load_series8(ext=False) devuelve exactamente la serie de V6/V7."""
import numpy as np, pandas as pd, data as DT, eng
from eng import Series
import os
W=os.path.join(os.path.dirname(os.path.abspath(__file__)),"datos_nuevos")+"/"
TDF={"ETH":W+"td_eth_1h_raw.csv","BTC":W+"td_btc_1h_raw.csv","DOGE":W+"td_doge_1h_raw.csv"}
OOS2_START=pd.Timestamp("2026-01-11")
AGG={"open":"first","high":"max","low":"min","close":"last","volume":"sum"}

def td_1h(a):
    d=pd.read_csv(TDF[a],parse_dates=["datetime"]).rename(columns={"datetime":"timestamp"}).set_index("timestamp").sort_index()
    d["volume"]=0.0
    return d[["open","high","low","close","volume"]]

def _agg(h,rule,nexp,start):
    h=h[h.index>=start]
    d=h.resample(rule,label="left",closed="left").agg(AGG); n=h.close.resample(rule,label="left",closed="left").count()
    return d[n>=nexp].dropna()

def load8(ext=True):
    D,e15=DT.load()
    if not ext: return D
    out={}
    for a in ("ETH","BTC","DOGE"):
        h=D[(a,"1h")]; t=td_1h(a); t=t[t.index>h.index.max()]
        H=pd.concat([h,t]); H=H[~H.index.duplicated()]
        out[(a,"1h")]=H
        f=D[(a,"4h")]; c4=f.index.max()+pd.Timedelta(hours=4)
        out[(a,"4h")]=pd.concat([f,_agg(H,"4h",4,c4)])
        d=D[(a,"1d")]; c1=d.index.max()+pd.Timedelta(days=1)
        out[(a,"1d")]=pd.concat([d,_agg(H,"1D",24,c1)])
    return out

class Series8(Series):
    def __init__(self,asset,tf,df):
        super().__init__(asset,tf,df)
        self.i_o2=int(df.index.searchsorted(OOS2_START,side="left"))
    def win(self,w):
        if w=="OOS1": return (self.i_va,self.i_o2)
        if w=="OOS2": return (self.i_o2,self.n)
        if w=="ALL": return (0,self.n)
        if w=="OOSX": return (self.i_va,self.n)       # OOS1+OOS2
        return super().win(w)

def load_series8(ext=False):
    D=load8(ext)
    return {k:Series8(k[0],k[1],v) for k,v in D.items()}

# ---------------- 1D con histórico previo a 2017-08 (FMP, compuesto USD; solo 1D) ----------------
FMPF={"ETH":W+"fmp_eth_1d_old.csv","BTC":W+"fmp_btc_1d_old.csv","DOGE":W+"fmp_doge_1d_old.csv"}
PRE_START={"ETH":"2015-08-07","BTC":"2013-01-01","DOGE":"2017-09-01"}

class Series8P(Series8):
    """Ventanas con PRE: PRE=(0,i_pre) = datos previos a Binance (solo 1D). TRAIN/DEV empiezan en i_pre (= mismas ventanas que V6/V7)."""
    def __init__(self,asset,tf,df,pre_end=None):
        super().__init__(asset,tf,df)
        self.i_pre=int(df.index.searchsorted(pre_end)) if pre_end is not None else 0
    def win(self,w):
        ip=self.i_pre
        if w=="PRE": return (0,ip)
        if w=="TRAIN": return (ip,self.i_tr)
        if w=="DEV": return (ip,self.i_va)
        if w=="FULL": return (ip,self.n)          # 2017-08 -> fin de los datos cargados
        if w=="FULL0": return (ip,self.i_o2)      # 2017-08 -> 2026-01-10 (igual que los informes de V6/V7)
        if w=="ALL17": return (ip,self.n)
        if w=="ALL": return (0,self.n)
        if w=="OOS": return (self.i_va,self.i_o2)  # OOS1 (sin OOS2)
        if w in ("OOS1",): return (self.i_va,self.i_o2)
        if w=="OOS2": return (self.i_o2,self.n)
        if w=="OOSX": return (self.i_va,self.n)
        return super().win(w)

def load_etc():
    """ETC (nunca usado en V6/V7): 1h y 4h del repo hasta 2026-01-06; 1D agregado desde 1h."""
    h=DT.rd(f"{DT.C}/ETCUSDT_1h.csv"); f=DT.rd(f"{DT.C}/ETCUSDT_4h.csv")
    return {("ETC","1h"):h,("ETC","4h"):f,("ETC","1d"):DT.rs(h,"1D",24,0.75)}

def load_all(ext=False,pre=True,etc=False):
    """Dict (activo,tf)->Series8P. ext=False -> OOS2 sellado. pre=True -> 1D con PRE (FMP). etc=True -> añade ETC."""
    D=load8(ext); out={}
    if etc: D.update(load_etc())
    for k,v in D.items():
        pe=None
        if pre and k[1]=="1d" and k[0] in FMPF:
            f=pd.read_csv(FMPF[k[0]],parse_dates=["date"]).rename(columns={"date":"timestamp"}).set_index("timestamp").sort_index()
            f=f[["open","high","low","close","volume"]]; f=f[(f.index>=pd.Timestamp(PRE_START[k[0]]))&(f.index<v.index.min())]
            pe=v.index.min(); v=pd.concat([f,v])
        out[k]=Series8P(k[0],k[1],v,pe)
    return out
