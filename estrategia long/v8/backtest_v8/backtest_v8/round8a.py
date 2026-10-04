"""Ronda 8A: palancas estructurales de V8 sobre la base V7, solo DEV (TRAIN/VAL), ETH+BTC+DOGE, 1H/4H/1D. Pre-registrado antes de ver resultados."""
import exp8, data8, pandas as pd, numpy as np
S=data8.load_all(False,pre=False)
V=[]
for kT in (4,5):
    for kH in (0,7,10):
        V.append(dict(name=f"F1 stop al cierre kT={kT} duro={kH}",fam="F1_cstop",p=dict(kT=kT),ext=dict(cstop=1,kH=kH)))
for at in (6,10):
    for fr in (0.33,0.5):
        V.append(dict(name=f"F2 salida parcial {fr:.2f} a +{at}ATR",fam="F2_partial",ext=dict(ptp_at=at,ptp_frac=fr)))
for rN in (35,70):
    for rb in (70,140,280):
        V.append(dict(name=f"F3 reentrada canal {rN}h ventana {rb}h",fam="F3_reentry",p=dict(reN_h=rN),ext=dict(reent_h=rb)))
for m in (0,0.5):
    V.append(dict(name=f"F4 entrada buy-stop margen {m}ATR",fam="F4_entstop",p=dict(ent="lvl",brk_m=m)))
for xN in (35,70,140):
    V.append(dict(name=f"F5 salida por minimo {xN}h",fam="F5_donchlow",p=dict(xN_h=xN)))
for m in (0.25,0.5,1.0):
    V.append(dict(name=f"F6 margen de ruptura {m}ATR",fam="F6_brkmargin",p=dict(brk_m=m)))
rows=[]
for v in V:
    sm,D,res=exp8.trial(S,v)
    sm["acc"]="".join(tf[:2] if a else "--" for tf,a in sm["acc"].items()); rows.append(sm)
R=pd.DataFrame(rows); R.to_pickle("round8a.pkl")
pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
cols=["name","E1h_tr","E1h_va","E4h_tr","E4h_va","E1d_tr","E1d_va","B1h","B4h","B1d","D1h","D4h","D1d","dMDD_1h","dMDD_4h","dMDD_1d","acc"]
print(R[cols].to_string(index=False))
