"""Ronda 8B: lógica específica 1D con escala de tiempo NATIVA (barras diarias), cuadrícula completa. Selección con TRAIN/VAL (post 2017-08). PRE solo como diagnóstico posterior."""
import exp8, data8, pandas as pd, numpy as np, itertools, time, json
SP=data8.load_all(False,pre=True)
ASS=("ETH","BTC","DOGE")
def stat3(a,v,wins):
    s=SP[(a,"1d")]; eq,ex,trd=exp8.run_variant(s,v); return {w:s.stat(eq,trd,w) for w in wins}
base={a:stat3(a,{},("TRAIN","VAL","DEV","PRE","OOS1")) for a in ASS}
cal=lambda m: np.nan if (m is None or m["calmar"]!=m["calmar"]) else m["calmar"]
t0=time.time(); rows=[]
for N,L,A,k,tp in itertools.product((4,6,10,15,20,30,40,55),(20,33,50,75,100,150,200),(10,14,20),(1.5,2.0,2.5,3.0,4.0),(0,6,8,12)):
    v=dict(p=dict(N_b=N,L_b=L,A_b=A,atr_scale=1.0,kI=k,kT=k,tp=tp))
    r=dict(N=N,L=L,A=A,k=k,tp=tp)
    for a in ASS:
        st=stat3(a,v,("TRAIN","VAL","DEV"))
        for w in ("TRAIN","VAL","DEV"):
            r[f"{a}_{w}_cal"]=cal(st[w]); r[f"{a}_{w}_d"]=cal(st[w])-cal(base[a][w])
        r[f"{a}_mdd"]=st["DEV"]["mdd"]; r[f"{a}_cagr"]=st["DEV"]["cagr"]; r[f"{a}_n"]=st["DEV"]["trades"]
    rows.append(r)
G=pd.DataFrame(rows); G.to_pickle("round8b_dev.pkl"); print(len(G),"combinaciones",round(time.time()-t0,1),"s")
# criterio pre-registrado 1D: ETH dCal>0 en TRAIN y VAL; BTC y DOGE dCal(DEV)>=0; ETH mdd no peor de 1pp que base
bm=base["ETH"]["DEV"]["mdd"]
ok=(G.ETH_TRAIN_d>0)&(G.ETH_VAL_d>0)&(G.BTC_DEV_d>=0)&(G.DOGE_DEV_d>=0)&(G.ETH_mdd>bm-0.01)
print("pasan criterio:",int(ok.sum()),"de",len(G),f"({ok.mean()*100:.1f}%)")
print("base DEV Calmar ETH/BTC/DOGE:",{a:round(cal(base[a]["DEV"]),2) for a in ASS})
# suavizado de vecindad: media del score en vecinos (+-1 paso por parametro) -> meseta
G["score"]=(G.ETH_DEV_d*2+G.BTC_DEV_d+G.DOGE_DEV_d)/4
ax={"N":sorted(G.N.unique()),"L":sorted(G.L.unique()),"A":sorted(G.A.unique()),"k":sorted(G.k.unique()),"tp":sorted(G.tp.unique())}
idx={tuple(r[c] for c in ("N","L","A","k","tp")):r.score for _,r in G.iterrows()}
def neigh(key):
    vals=[]
    for j,c in enumerate(("N","L","A","k","tp")):
        i=ax[c].index(key[j])
        for d in (-1,1):
            if 0<=i+d<len(ax[c]):
                kk=list(key); kk[j]=ax[c][i+d]; vals.append(idx[tuple(kk)])
    return np.nanmean(vals)
G["sm"]=[neigh((r.N,r.L,r.A,r.k,r.tp)) for r in G.itertuples()]
G["plateau"]=(G.score+G.sm)/2
G.to_pickle("round8b_dev.pkl")
pd.set_option("display.width",250)
cols=["N","L","A","k","tp","ETH_TRAIN_d","ETH_VAL_d","BTC_DEV_d","DOGE_DEV_d","ETH_mdd","ETH_n","score","sm","plateau"]
print("TOP 12 por meseta (score propio + vecinos):"); print(G.sort_values("plateau",ascending=False)[cols].head(12).round(2).to_string(index=False))
print("TOP 8 de los que pasan el criterio:"); print(G[ok].sort_values("plateau",ascending=False)[cols].head(8).round(2).to_string(index=False))
