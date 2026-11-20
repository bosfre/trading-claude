import exp9, numpy as np, pandas as pd
pd.set_option("display.width",260); pd.set_option("display.max_columns",40)
S=exp9.load(True); V8=exp9.V8; T0="2017-08-17"
def wst(s,v,m,cost=1.0,a=T0,b=None):
    eq,ex,trd=exp9.run9(s,exp9.scale_risk(v,m),cost); return exp9.wstat(s,eq,ex,trd,a,b)
def match(s,target,a=T0,b=None):
    lo,hi=0.1,4.0
    for _ in range(24):
        m=(lo+hi)/2; w=wst(s,V8,m,1.0,a,b)
        if w["mdd"]<target: hi=m
        else: lo=m
    return m,w
rows=[]
for tgt in ():
    for tf in exp9.TFS:
        s=S[("ETH",tf)]; m,w=match(s,tgt)
        o=wst(s,V8,m,1.0,"2024-01-01",None)
        rows.append(dict(dd_objetivo=tgt,tf=tf,riesgo_pct=round(5*m,2),cagr=w["cagr"],ret=w["ret"],mdd=w["mdd"],calmar=w["calmar"],cagr_2024_26=o["cagr"],mdd_2024_26=o["mdd"]))

# costes y apalancamiento (riesgo 5 %)
rows=[]
for tf in exp9.TFS:
    s=S[("ETH",tf)]
    for c in (1.0,2.0,3.0):
        w=wst(s,V8,1.0,c); rows.append(dict(tf=tf,coste=c,cagr=w["cagr"],mdd=w["mdd"],calmar=w["calmar"],pf=w["pf"],avg_ret=w["avg_ret"]))
    eq,ex,trd=exp9.run9(s,V8); sz=np.array([t[7] for t in trd]); print(tf,"tamaño medio %.2fx, pct de operaciones >1x: %.0f%%, máx %.2fx, exposición media cuando hay posición %.2f"%(sz.mean(),100*(sz>1.0001).mean(),sz.max(),np.mean(np.abs(ex)[np.abs(ex)>0])))
C=pd.DataFrame(rows); C.to_csv("costes_V8_por_TF.csv",index=False); print(C.round(3).to_string())
# tus números de TradingView normalizados a anual
for nm,ret,yrs,dd in (("1D completo (2015-08→2026-10)",24.9184,(pd.Timestamp("2026-10-04")-pd.Timestamp("2015-08-07")).days/365.25,0.18),("4H 2024-01-01→2026-10-04",0.42,(pd.Timestamp("2026-10-04")-pd.Timestamp("2024-01-01")).days/365.25,0.14),("1H 9 meses (~2026-01-04→10-04)",0.36,(pd.Timestamp("2026-10-04")-pd.Timestamp("2026-01-04")).days/365.25,0.12)):
    cg=(1+ret)**(1/yrs)-1; print(f"{nm}: {yrs:.2f} años, CAGR {cg*100:.1f}%, Calmar(CAGR/DD) {cg/dd:.2f}")
