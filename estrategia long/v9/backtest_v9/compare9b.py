import exp9, numpy as np, pandas as pd, json
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=exp9.load(True); V8=exp9.V8; T0="2017-08-17"
# ---------- 1) frontera riesgo/DD ----------
rows=[]
for tf in exp9.TFS:
    s=S[("ETH",tf)]
    for m in (0.5,0.6,0.7,0.8,0.9,1.0,1.2):
        eq,ex,trd=exp9.run9(s,exp9.scale_risk(V8,m))
        for wn,(a,b) in {"COMUN 2017-08→2026-10":(T0,None),"OOS1+OOS2 2024→2026-10":("2024-01-01",None),"DEV 2017-08→2023":(T0,"2024-01-01")}.items():
            w=exp9.wstat(s,eq,ex,trd,a,b); rows.append(dict(tf=tf,riesgo_pct=5*m,ventana=wn,ret=w["ret"],cagr=w["cagr"],mdd=w["mdd"],calmar=w["calmar"],n=w["n"],avgR=w["avgR"]))
F=pd.DataFrame(rows); F.to_csv("frontera_riesgo_V8.csv",index=False)
print(F[F.ventana=="COMUN 2017-08→2026-10"].pivot_table(index="riesgo_pct",columns="tf",values=["cagr","mdd","calmar"]).round(3).to_string())
# ---------- 2) series diarias, mezcla de TF, bootstrap ----------
def daily(tf,v=V8):
    s=S[("ETH",tf)]; eq,ex,trd=exp9.run9(s,v); e=pd.Series(eq[s.dend],index=s.idx[s.dend].normalize()); return e[~e.index.duplicated()]
D=pd.concat({tf:daily(tf) for tf in exp9.TFS},axis=1).ffill().dropna(); R=D.pct_change().fillna(0.0)
R=R[R.index>=pd.Timestamp(T0)]
def met(r):
    e=(1+r).cumprod(); yrs=len(r)/365.25; tot=e.iloc[-1]-1; cagr=(1+tot)**(1/yrs)-1 if tot>-1 else np.nan
    pk=np.maximum.accumulate(np.r_[1.0,e.values])[1:]; mdd=(e.values/pk-1).min(); sh=r.mean()/r.std()*np.sqrt(365.25) if r.std()>0 else np.nan
    return dict(ret=tot,cagr=cagr,mdd=mdd,calmar=cagr/abs(mdd) if mdd<0 else np.nan,sharpe=sh)
BL={"1H":R["1h"],"4H":R["4h"],"1D":R["1d"],"4H+1D (50/50)":(R["4h"]+R["1d"])/2,"1H+4H (50/50)":(R["1h"]+R["4h"])/2,"1H+4H+1D (1/3 c/u)":(R["1h"]+R["4h"]+R["1d"])/3}
WIN={"COMUN 2017-08→2026-10":(T0,None),"TRAIN":(T0,"2022-01-01"),"VAL":("2022-01-01","2024-01-01"),"OOS1+OOS2 2024→2026-10":("2024-01-01",None)}
rows=[]
for wn,(a,b) in WIN.items():
    for k,r in BL.items():
        x=r[(r.index>=pd.Timestamp(a))&((r.index<pd.Timestamp(b)) if b else True)]; rows.append(dict(ventana=wn,cartera=k,**met(x)))
B=pd.DataFrame(rows); B.to_csv("mezcla_temporalidades_V8.csv",index=False)
print(B.pivot_table(index="cartera",columns="ventana",values="calmar").round(2).to_string()); print(B[B.ventana=="COMUN 2017-08→2026-10"].round(3).to_string())
print("correlación de retornos diarios:\n",R.corr().round(2).to_string())
# bootstrap por bloques (30 días, circular), pares conjuntos
rng=np.random.default_rng(7); n=len(R); blk=30; nb=int(np.ceil(n/blk)); NB=3000; arr=R[["1h","4h","1d"]].values
res=[]
for _ in range(NB):
    st=rng.integers(0,n,nb); idx=(st[:,None]+np.arange(blk)[None,:])%n; idx=idx.reshape(-1)[:n]; x=arr[idx]; row=[]
    for j in range(3):
        e=np.cumprod(1+x[:,j]); yrs=n/365.25; cagr=e[-1]**(1/yrs)-1; pk=np.maximum.accumulate(np.r_[1.0,e])[1:]; mdd=(e/pk-1).min(); row+= [cagr,mdd,cagr/abs(mdd)]
    res.append(row)
res=np.array(res); names=["1h","4h","1d"]; out=[]
for j,tf in enumerate(names):
    c=res[:,3*j:3*j+3]; out.append(dict(tf=tf,cagr_p5=np.percentile(c[:,0],5),cagr_med=np.median(c[:,0]),cagr_p95=np.percentile(c[:,0],95),mdd_p5=np.percentile(c[:,1],5),mdd_med=np.median(c[:,1]),calmar_p5=np.percentile(c[:,2],5),calmar_med=np.median(c[:,2]),calmar_p95=np.percentile(c[:,2],95)))
O=pd.DataFrame(out); print(O.round(3).to_string()); O.to_csv("bootstrap_bloques_TF_V8.csv",index=False)
pairs=[("4h","1d",1,2),("1h","1d",0,2),("1h","4h",0,1)]
for a,b,i,j in pairs:
    print(f"P(Calmar {a} > {b}) = {np.mean(res[:,3*i+2]>res[:,3*j+2]):.2f} | P(CAGR {a} > {b}) = {np.mean(res[:,3*i]>res[:,3*j]):.2f} | P(MDD {a} menor que {b}) = {np.mean(res[:,3*i+1]>res[:,3*j+1]):.2f}")
# ---------- 3) retorno por año ----------
E=pd.concat({tf:daily(tf) for tf in exp9.TFS},axis=1).ffill().dropna(); ye=E.resample("YE").last(); yr=ye/ye.shift(1)-1; yr.iloc[0]=ye.iloc[0]/E.iloc[0]-1; yr.index=yr.index.year
print((yr*100).round(1).to_string()); yr.to_csv("retorno_anual_ETH_V8_por_TF.csv")
