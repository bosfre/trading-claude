import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",200)
S=eng.load_series()
base=exp.eval_variant(S,{})
V={}
for sp in (4320,8760):
    for th in (0.9,1.0,1.1): V[f"A1 filtro vol<= {th} (EMA {sp}h)"]=dict(vr=dict(span_h=sp,mode="filter",thr=th))
    for lo,hi in ((1.25,0.75),(1.5,0.5)): V[f"A2 tamaño vol {lo}/{hi} (EMA {sp}h)"]=dict(vr=dict(span_h=sp,mode="size",thr=1.0,w_lo=lo,w_hi=hi))
for dt,dm in itertools.product((0.08,0.10,0.12),(0.5,0.67)): V[f"B throttle DD>{dt:.0%} x{dm}"]=dict(ext=dict(ddthr=dt,ddmult=dm))
for rm,rk in itertools.product((6,8,10),(3,4)): V[f"C trinquete MFE>={rm} -> kT={rk}"]=dict(ext=dict(rat_m=rm,rat_k=rk))
for pa,pf in itertools.product((2,3,4),(0.5,1.0)): V[f"D pirámide +{pa}ATR x{pf}"]=dict(ext=dict(pyr_at=pa,pyr_frac=pf,pyr_n=1))
for kI,kT in ((4,5),(4,4),(4,6),(5,4),(5,6),(6,6),(3,5)): V[f"E kI={kI} kT={kT}"]=dict(p=dict(kI=float(kI),kT=float(kT)))
V["F ruptura por cierre (hc)"]=dict(p=dict(ent="hc"))
for th in (70,140,280): V[f"G stop tiempo {th}h sin +1ATR"]=dict(ext=dict(ts_h=th,ts_mfe=1.0))
V["H cortos simétricos (funding pagado)"]=dict(p=dict(short=1,sN_h=140,sL_h=800),ext=dict(fund_s=-1))
V["H cortos selectivos (N=280h, EMA 1600h)"]=dict(p=dict(short=1,sN_h=280,sL_h=1600),ext=dict(fund_s=-1))
rows=[]
for name,v in V.items():
    r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(name,d); rows.append(sm); exp.log_trial(name,sm)
T=pd.DataFrame(rows)
print(T.to_string(index=False))
T.to_pickle("round1.pkl")
