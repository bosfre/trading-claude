import exp9, numpy as np, pandas as pd, json, sys
pd.set_option("display.width",250); pd.set_option("display.max_columns",60)
S=exp9.load(True)
B=exp9.B800
def V(name,fam,p=None,ext=None,x=None):
    pp=dict(xref=B); pp.update(p or {}); return dict(name=name,fam=fam,p=pp,ext=ext or {},x=x or {})
VS=[V("TS 140h MFE<1ATR","G1",ext=dict(ts_h=140,ts_mfe=1.0)),V("TS 140h MFE<2ATR","G1",ext=dict(ts_h=140,ts_mfe=2.0)),
    V("TS 280h MFE<1ATR","G1",ext=dict(ts_h=280,ts_mfe=1.0)),V("TS 280h MFE<2ATR","G1",ext=dict(ts_h=280,ts_mfe=2.0)),
    V("salida close<EMA","G1",x=dict(trend_exit=0.0)),V("salida close<EMA-1ATR","G1",x=dict(trend_exit=1.0)),
    V("salida BTC<EMA800h","G1",x=dict(btc_exit=800)),
    V("trail 7 tras +8ATR","G2",ext=dict(rat_m=8,rat_k=7)),V("trail 8 tras +12ATR","G2",ext=dict(rat_m=12,rat_k=8)),
    V("TP20->trail3.5","G2",p=dict(tp=0),ext=dict(rat_m=20,rat_k=3.5)),
    V("saltar si ext>6","G3",x=dict(ext_max=6)),V("saltar si ext>8","G3",x=dict(ext_max=8)),
    V("CLV>=0.5","G3",x=dict(clv_min=0.5)),V("CLV>=0.7","G3",x=dict(clv_min=0.7)),
    V("tamaño x0.5 si ext>6","G3",x=dict(ext_size=(6,0.5)))]
rows=[]
for v in VS:
    sm,D,res=exp9.trial9(S,v); rows.append(sm)
    print(f"{v['name']:<24}",{tf:(sm[f'E{tf}_tr'],sm[f'E{tf}_va'],sm[f'B{tf}'],sm[f'D{tf}'],sm[f'dMDD_{tf}'],sm[f'dR_{tf}']) for tf in exp9.TFS},{k:bool(x) for k,x in sm['acc'].items()})
    sys.stdout.flush()
pd.DataFrame(rows).to_pickle("round9a.pkl")
