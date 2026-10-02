import numpy as np, eng, gen
GALL={"1h":dict(N=[12,24,36,48,72,96,120,168],L=[100,200,400,600,800,1200,1600],A=[14,28,56,84]),
      "4h":dict(N=[6,10,15,20,30,40,60],L=[50,100,150,200,300,400],A=[10,14,21,28]),
      "1d":dict(N=[3,5,10,15,20,30,50],L=[20,30,50,100,150,200],A=[10,14,20])}
GR=dict(kI=[2,2.5,3,4,5,6],kT=[3,4,5,6,8,10,12,15],ent=["hh","hc"],tp=[0,0,10,15,20,30],short=[0,1],xf=[0,0,0.5,1.0],tron=[0,0,2,4],be=[0,0,4],slope=[0,1],adx=[0,0,15,20])
def conv(p,tf):
    tfh=eng.TFH[tf]
    return dict(kI=p["kI"],kT=p["kT"],ent=p["ent"],tp=p["tp"],short=p["short"],tron=p["tron"],be=p["be"],slope=p["slope"],adx=p["adx"],
        N_h=p["N_b"]*tfh,L_h=p["L_b"]*tfh,A_h=p["A_b"]*tfh,sN_h=p["sN_b"]*tfh,sL_h=p["sL_b"]*tfh,xN_h=p["xf"]*p["N_b"]*tfh,xmode="lc" if p["ent"]=="hc" else "ll")
def evaluate(S,tf,p,cost=1.0,wins=("TRAIN","VAL","DEV"),assets=("ETH","BTC","DOGE")):
    q=conv(p,tf); return {a:gen.run(S[(a,tf)],q,wins=wins,cost=cost)[0] for a in assets}
MDD_ETH=-0.18; MDD_OTH=-0.30
def obj(res):
    tot=0.0
    for a,wt in (("ETH",.5),("BTC",.25),("DOGE",.25)):
        cs=[]
        for w in ("TRAIN","VAL"):
            m=res[a][w]
            cs.append(m["calmar"] if m["calmar"]==m["calmar"] else (m["ret"]/max(abs(m["mdd"]),1e-3)/max(m["yrs"],1)))
        v=min(cs); lim=MDD_ETH if a=="ETH" else MDD_OTH; dd=res[a]["DEV"]["mdd"]
        if dd<lim: v-=(lim-dd)*20
        if res[a]["DEV"]["trades"]<30: v-=1.0
        tot+=wt*v
    return tot
