import eng,gen,pandas as pd,numpy as np,sys,time,random
TF=sys.argv[1]; NC=int(sys.argv[2]); seed=int(sys.argv[3])
S=eng.load_series(); tfh=eng.TFH[TF]
G={"1h":dict(N=[12,24,36,48,72,96,120,168],L=[100,200,400,600,800,1200,1600],A=[14,28,56,84]),
   "4h":dict(N=[6,10,15,20,30,40,60],L=[50,100,150,200,300,400],A=[10,14,21,28]),
   "1d":dict(N=[3,5,10,15,20,30,50],L=[20,30,50,100,150,200],A=[10,14,20])}[TF]
GR=dict(kI=[2,2.5,3,4,5,6],kT=[3,4,5,6,8,10,12,15],ent=["hh","hc"],tp=[0,0,10,15,20,30],short=[0,1],xf=[0,0,0.5,1.0],tron=[0,0,2,4],be=[0,0,4],slope=[0,1],adx=[0,0,15,20])
def sample(r):
    p={k:r.choice(v) for k,v in GR.items()}
    for k,g in (("N_b","N"),("L_b","L"),("A_b","A"),("sN_b","N"),("sL_b","L")): p[k]=r.choice(G[g])
    return p
def conv(p):
    return dict(kI=p["kI"],kT=p["kT"],ent=p["ent"],tp=p["tp"],short=p["short"],tron=p["tron"],be=p["be"],slope=p["slope"],adx=p["adx"],
        N_h=p["N_b"]*tfh,L_h=p["L_b"]*tfh,A_h=p["A_b"]*tfh,sN_h=p["sN_b"]*tfh,sL_h=p["sL_b"]*tfh,xN_h=p["xf"]*p["N_b"]*tfh,xmode="lc" if p["ent"]=="hc" else "ll")
def evaluate(p,cost=1.0):
    q=conv(p); return {a:gen.run(S[(a,TF)],q,wins=("TRAIN","VAL","DEV"),cost=cost)[0] for a in ("ETH","BTC","DOGE")}
def score(res,minn):
    cal=[res[a]["DEV"]["calmar"] for a in ("ETH","BTC","DOGE")]
    if any(c!=c for c in cal): return -9
    sc=(2*cal[0]+cal[1]+cal[2])/4
    neg=sum(1 for a in res for w in ("TRAIN","VAL") if res[a][w]["ret"]<=0)
    if res["ETH"]["DEV"]["trades"]<minn: sc-=2
    return sc-0.5*neg
if __name__=="__main__":
    rng=random.Random(seed); out=[]; t=time.time(); minn=60 if TF!="1d" else 40
    for i in range(NC):
        p=sample(rng); r=evaluate(p); sc=score(r,minn); e=r["ETH"]["DEV"]
        out.append(dict(tf=TF,score=sc,**{k:(v.item() if hasattr(v,'item') else v) for k,v in p.items()},
            ethRet=e["ret"],ethMdd=e["mdd"],ethSh=e["sharpe"],ethN=e["trades"],ethCal=e["calmar"],
            btcCal=r["BTC"]["DEV"]["calmar"],dogeCal=r["DOGE"]["DEV"]["calmar"],
            ethTrRet=r["ETH"]["TRAIN"]["ret"],ethVaRet=r["ETH"]["VAL"]["ret"]))
        if (i+1)%100==0:
            pd.DataFrame(out).to_csv(f"search_{TF}.csv",index=False); print(TF,i+1,round(time.time()-t),"s mejor",round(max(o['score'] for o in out),2),flush=True)
    pd.DataFrame(out).to_csv(f"search_{TF}.csv",index=False); print("FIN",TF,flush=True)
