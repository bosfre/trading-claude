import eng,gen,pandas as pd,numpy as np,sys,time,random
from search import G,GR,conv
TF=sys.argv[1]; NC=int(sys.argv[2]); seed=int(sys.argv[3])
S=eng.load_series()
MDD_ETH=-0.18; MDD_OTH=-0.30
def obj(res):
    """res[a][w] -> stats. Peor ventana (TRAIN/VAL) de CAGR/|MDD|; tope de MDD en DEV; ETH pesa 50%."""
    tot=0.0; info={}
    for a,wt in (("ETH",.5),("BTC",.25),("DOGE",.25)):
        cs=[]
        for w in ("TRAIN","VAL"):
            m=res[a][w]
            c=m["calmar"] if m["calmar"]==m["calmar"] else (m["ret"]/max(abs(m["mdd"]),1e-3)/max(m["yrs"],1))
            cs.append(c)
        v=min(cs)
        lim=MDD_ETH if a=="ETH" else MDD_OTH
        dd=res[a]["DEV"]["mdd"]
        if dd<lim: v-= (lim-dd)*20          # penalización dura por salirse del presupuesto de drawdown
        if res[a]["DEV"]["trades"]<30: v-=1.0
        tot+=wt*v
    return tot
def evaluate(p):
    q=conv(p); return {a:gen.run(S[(a,TF)],q,wins=("TRAIN","VAL","DEV"))[0] for a in ("ETH","BTC","DOGE")}
if __name__=="__main__":
    rng=random.Random(seed); out=[]; t=time.time()
    for i in range(NC):
        p={k:rng.choice(v) for k,v in GR.items()}
        for k,g in (("N_b","N"),("L_b","L"),("A_b","A"),("sN_b","N"),("sL_b","L")): p[k]=rng.choice(G[g])
        r=evaluate(p); sc=obj(r); e=r["ETH"]
        out.append(dict(tf=TF,score=sc,**{k:(v.item() if hasattr(v,'item') else v) for k,v in p.items()},
            ethRet=e["DEV"]["ret"],ethMdd=e["DEV"]["mdd"],ethCagr=e["DEV"]["cagr"],ethSh=e["DEV"]["sharpe"],ethN=e["DEV"]["trades"],
            ethTr=e["TRAIN"]["ret"],ethVa=e["VAL"]["ret"],btcRet=r["BTC"]["DEV"]["ret"],btcMdd=r["BTC"]["DEV"]["mdd"],
            dogeRet=r["DOGE"]["DEV"]["ret"],dogeMdd=r["DOGE"]["DEV"]["mdd"],btcVa=r["BTC"]["VAL"]["ret"],dogeVa=r["DOGE"]["VAL"]["ret"]))
        if (i+1)%5000==0: print(TF,i+1,round(time.time()-t),"s",flush=True)
    pd.DataFrame(out).to_csv(f"search2_{TF}.csv",index=False); print("FIN",TF,len(out),flush=True)
