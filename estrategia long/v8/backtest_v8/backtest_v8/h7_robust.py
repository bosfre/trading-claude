import exp8, data8, eng, pandas as pd, numpy as np, json
S=data8.load_all(False,pre=False,etc=True); exp8.set_refs(S)
pd.set_option("display.width",250)
V=dict(name="V8-A",p=dict(xref=dict(type="btc",mode="filter",L_h=800)))
def yearly(s,eq):
    e=pd.Series(eq,index=s.idx).ffill(); ye=e.resample("YE").last(); r=ye/ye.shift(1)-1; r.iloc[0]=ye.iloc[0]/e.dropna().iloc[0]-1; r.index=r.index.year; return r
print("== R3: a igual drawdown (ETH, DEV) ==")
for tf in exp8.TFS:
    s=S[("ETH",tf)]; eqb,_,tb=exp8.run_variant(s,{}); b=s.stat(eqb,tb,"DEV")
    m,x=exp8.matched_dd(S,V,"ETH",tf,b["mdd"],"DEV")
    print(tf,"V7 CAGR %.1f%% MDD %.1f%% | V8 mismo riesgo CAGR %.1f%%  | V8 a igual DD (riesgo x%.2f) CAGR %.1f%% MDD %.1f%%  -> ganancia a igual DD %+.1f pp"%(b["cagr"]*100,b["mdd"]*100,s.stat(exp8.run_variant(s,V)[0],exp8.run_variant(s,V)[2],"DEV")["cagr"]*100,m,x["cagr"]*100,x["mdd"]*100,(x["cagr"]-b["cagr"])*100))
print("== R4: costes x1/x2/x3 (ETH) dCalmar DEV y FULL ==")
for c in (1,2,3):
    out=[]
    for tf in exp8.TFS:
        s=S[("ETH",tf)]
        for w in ("DEV","FULL"):
            eb,_,tb=exp8.run_variant(s,{},cost=c); ev,_,tv=exp8.run_variant(s,V,cost=c)
            b=s.stat(eb,tb,w); x=s.stat(ev,tv,w); out.append(f"{tf}/{w}: {b['calmar']:.2f}->{x['calmar']:.2f} (CAGR {b['cagr']*100:.0f}->{x['cagr']*100:.0f}%)")
    print("x%d  "%c," | ".join(out))
print("== Retorno por año ETH (V7 -> V8), % ==")
Y={}
for tf in exp8.TFS:
    s=S[("ETH",tf)]; yb=yearly(s,exp8.run_variant(s,{})[0]); yv=yearly(s,exp8.run_variant(s,V)[0]); Y[tf]=(yb*100).round(1).astype(str)+" -> "+(yv*100).round(1).astype(str)
print(pd.DataFrame(Y).to_string())
print("== Operaciones eliminadas/añadidas por el filtro (ETH, FULL) ==")
for tf in exp8.TFS:
    s=S[("ETH",tf)]; _,_,tb=exp8.run_variant(s,{}); _,_,tv=exp8.run_variant(s,V)
    kb={int(t[0]):t for t in tb}; kv={int(t[0]):t for t in tv}
    rem=[kb[k] for k in kb if k not in kv]; add=[kv[k] for k in kv if k not in kb]; com=[kb[k] for k in kb if k in kv]
    f=lambda L: (len(L), np.mean([t[5] for t in L])*100 if L else np.nan, np.mean([t[5]>0 for t in L])*100 if L else np.nan, np.mean([t[6] for t in L]) if L else np.nan)
    print(tf,"eliminadas n=%d ret medio %.2f%% win %.0f%% R medio %.2f | añadidas n=%d ret medio %.2f%% win %.0f%% R medio %.2f | comunes n=%d ret medio %.2f%% win %.0f%% R %.2f"%(*f(rem),*f(add),*f(com)))
