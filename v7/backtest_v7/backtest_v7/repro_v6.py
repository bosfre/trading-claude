import eng, gen, pandas as pd, numpy as np, time
t=time.time()
S=eng.load_series(); print("series cargadas", round(time.time()-t,1),"s")
for k,s in S.items(): print(k, len(s.df), s.df.index[0], s.df.index[-1])
V3P=dict(N_h=140,L_h=800,A_h=56,kI=5.0,kT=5.0,minN=5,minL=20,minA=10,ent="hh")
ref=pd.read_csv("/home/claude/bosfre/trading-claude/v6/resultados_completos.csv")
ref=ref[(ref.ver=="V6")]
rows=[]
for (a,tf),s in S.items():
    m,eq,ex,trd=gen.run(s,dict(V3P,tp=20,risk=0.05,mlev=2.0),wins=("TRAIN","VAL","OOS","FULL"))
    for w in ("TRAIN","VAL","OOS","FULL"):
        r=ref[(ref.asset==a)&(ref.tf==tf)&(ref.w==w)].iloc[0]
        rows.append(dict(asset=a,tf=tf,w=w,ret=m[w]["ret"],ref_ret=r.ret,mdd=m[w]["mdd"],ref_mdd=r.mdd,n=m[w]["trades"],ref_n=r.trades))
d=pd.DataFrame(rows); d["dret"]=d.ret-d.ref_ret; print(d[d.asset=="ETH"].round(4).to_string()); print("max |dret| all assets:", d.dret.abs().max())
