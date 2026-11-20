import exp8, data8, eng, pandas as pd, numpy as np, json, os
V8=dict(name="V8",p=dict(xref=dict(type="btc",mode="filter",L_h=800)))
S0=data8.load_all(True,pre=False,etc=False); exp8.set_refs(S0)
SP=data8.load_all(True,pre=True,etc=False)
SE=data8.load_all(False,pre=False,etc=True)
rows=[]
def add(S,a,tf,w,ver,v,cost=1.0):
    s=S[(a,tf)]; eq,_,tr=exp8.run_variant(s,v,cost); m=s.stat(eq,tr,w)
    if m is None: return
    rows.append(dict(activo=a,tf=tf,ventana=w,version=ver,coste=cost,ret=m["ret"],cagr=m["cagr"],mdd=m["mdd"],sharpe=m["sharpe"],sortino=m["sortino"],operaciones=m["trades"],win=m["win"],pf=m["pf"],calmar=m["calmar"],anios=m["yrs"]))
for a in ("ETH","BTC","DOGE"):
    for tf in exp8.TFS:
        for w in ("TRAIN","VAL","DEV","OOS1","FULL0","OOS2","ALL17"):
            add(S0,a,tf,w,"V6=V7 (Python)",{}); add(S0,a,tf,w,"V8",V8)
exp8.set_refs(SP)
for a in ("ETH","BTC","DOGE"):
    for w in ("PRE",):
        add(SP,a,"1d",w,"V6=V7 (Python)",{}); add(SP,a,"1d",w,"V8",V8)
exp8.set_refs(SE)
for a in ("ETC",):
    for tf in exp8.TFS:
        for w in ("TRAIN","VAL","DEV","OOS1","FULL0"):
            s=SE[(a,tf)]
            for ver,v in (("V6=V7 (Python)",{}),("V8",V8)):
                eq,_,tr=exp8.run_variant(s,v); m=s.stat(eq,tr,"OOS" if w=="OOS1" else ("FULL" if w=="FULL0" else w))
                if m: rows.append(dict(activo=a,tf=tf,ventana=w,version=ver,coste=1.0,ret=m["ret"],cagr=m["cagr"],mdd=m["mdd"],sharpe=m["sharpe"],sortino=m["sortino"],operaciones=m["trades"],win=m["win"],pf=m["pf"],calmar=m["calmar"],anios=m["yrs"]))
exp8.set_refs(S0)
# costes x1/x2/x3 en ETH
for c in (1.0,2.0,3.0):
    for tf in exp8.TFS:
        for w in ("FULL0","OOS1","OOS2"):
            add(S0,"ETH",tf,w,"V6=V7 (Python) coste x%g"%c,{},c); add(S0,"ETH",tf,w,"V8 coste x%g"%c,V8,c)
R=pd.DataFrame(rows); R.to_csv("/home/claude/work/v7/comparativa_V6_V7_V8.csv",index=False)
pd.set_option("display.width",250); pd.set_option("display.max_rows",400)
P=R[(R.coste==1.0)&(R.activo=="ETH")&(~R.version.str.contains("coste"))].pivot_table(index=["tf","ventana"],columns="version",values=["ret","cagr","mdd","operaciones","calmar"],aggfunc="first")
print(P.round(3).to_string())
# retorno por año ETH
def yearly(s,eq):
    e=pd.Series(eq,index=s.idx).ffill(); ye=e.resample("YE").last(); r=ye/ye.shift(1)-1; r.iloc[0]=ye.iloc[0]/e.dropna().iloc[0]-1; r.index=r.index.year; return r
Y=[]
for tf in exp8.TFS:
    s=S0[("ETH",tf)]; yb=yearly(s,exp8.run_variant(s,{})[0]); yv=yearly(s,exp8.run_variant(s,V8)[0])
    for y in yb.index: Y.append(dict(tf=tf,anio=int(y),V7=yb[y],V8=yv[y]))
Y=pd.DataFrame(Y); Y["dif"]=Y.V8-Y.V7; Y.to_csv("/home/claude/work/v7/retorno_anual_ETH_V7_vs_V8.csv",index=False)
full=Y[Y.anio.between(2018,2025)]
for tf in exp8.TFS:
    z=full[full.tf==tf]; d=z.dif.values; print(tf,"años 2018-2025: V8>V7 en",int((d>0).sum()),"de",len(d),"| dif media %+.1f pp | t=%.2f"%(d.mean()*100,d.mean()/(d.std(ddof=1)/np.sqrt(len(d)))))
