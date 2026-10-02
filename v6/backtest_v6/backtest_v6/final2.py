import pandas as pd,numpy as np,json,eng,core,gen,sigs
pd.set_option("display.width",300); pd.set_option("display.max_columns",60)
SER=eng.load_series(); CFG=json.load(open("final_cfg.json"))
V3P=dict(N_h=140,L_h=800,A_h=56,kI=5.0,kT=5.0,minN=5,minL=20,minA=10,ent="hh")
WINS=("TRAIN","VAL","OOS","FULL")
def run_cfg(name,tf,asset,cost=1.0):
    s=SER[(asset,tf)]
    if name in ("V3","V4","V3@5%","V6","V6@2%","V6@3%","V6@4%","V6@6%"):
        p=dict(V3P)
        if name=="V4": p["A_h"]=200
        if name.startswith("V6"): p["tp"]=20
        rk={"V3":.02,"V4":.02,"V3@5%":.05,"V6":.05,"V6@2%":.02,"V6@3%":.03,"V6@4%":.04,"V6@6%":.06}[name]
        ml=1.0 if name in ("V3","V4") else 2.0
        m,eq,ex,trd=gen.run(s,dict(p,risk=rk,mlev=ml),wins=WINS,cost=cost)
    elif name=="V5":
        sig=sigs.v5(s); eq,ex,trd=s.run(sig,3.5,risk=.03,mlev=2.0,cost=cost); m={w:s.stat(eq,trd,w) for w in WINS}
    elif name=="BUSCADA":      # mejor config encontrada en la búsqueda (solo datos <=2023): ver informe
        q=core.conv(CFG[tf]["lean"],tf); m,eq,ex,trd=gen.run(s,q,wins=WINS,cost=cost)
    return m,eq,ex,trd
VERS=["V3","V4","V5","V3@5%","V6","BUSCADA"]
rows=[]; EQ={}
for v in VERS:
    for tf in ("1h","4h","1d"):
        for a in ("ETH","BTC","DOGE"):
            m,eq,ex,trd=run_cfg(v,tf,a); EQ[(v,tf,a)]=(eq,ex,trd)
            for w in WINS: rows.append(dict(ver=v,tf=tf,asset=a,w=w,**m[w]))
R=pd.DataFrame(rows); R["net_usd_10k"]=R.ret*10000; R.to_csv("resultados_completos.csv",index=False); R.to_pickle("R2.pkl")
def tab(win,asset="ETH",vers=VERS,cols=("ret","cagr","net_usd_10k","mdd","sharpe","sortino","win","pf","trades")):
    t=R[(R.w==win)&(R.asset==asset)&(R.ver.isin(vers))].copy()
    for c in ("ret","cagr","mdd","win"): t[c]=(t[c]*100).round(1)
    t["net_usd_10k"]=t.net_usd_10k.round(0)
    for c in ("sharpe","sortino","pf"): t[c]=t[c].round(2)
    t["o"]=t.ver.map({v:i for i,v in enumerate(VERS)}); t=t.sort_values(["tf","o"])
    return t.set_index(["tf","ver"])[list(cols)]
if __name__=="__main__":
    for w in ("FULL","OOS","TRAIN","VAL"): print(f"\n########## ETH {w}"); print(tab(w).to_string())
    for a in ("BTC","DOGE"):
        for w in ("FULL","OOS"): print(f"\n########## {a} {w}"); print(tab(w,a,["V3","V4","V5","V6","BUSCADA"],("ret","cagr","mdd","sharpe","pf","trades")).to_string())
