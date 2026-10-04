import exp8, data8, pandas as pd, numpy as np, json
S=data8.load_all(False,pre=False); exp8.set_refs(S)
pd.set_option("display.width",250)
def v7(L,mode="filter",w=0.5): return dict(name=f"H7 BTC>EMA{L}h {mode}",fam="H7_btcreg",p=dict(xref=dict(type="btc",mode=mode,L_h=L,w=w)))
# 1) meseta en L (solo DEV)
rows=[]
for L in (200,300,400,500,600,700,800,900,1000,1200,1600):
    for mode in ("filter","size"):
        sm,D,res=exp8.trial(S,v7(L,mode),assets=("ETH","DOGE"),do_log=True)
        rows.append(dict(L=L,mode=mode,**{k:sm[k] for k in ("E1h_tr","E1h_va","E4h_tr","E4h_va","E1d_tr","E1d_va","D1h","D4h","D1d","dMDD_1h","dMDD_4h","dMDD_1d")}))
R=pd.DataFrame(rows); print(R.to_string(index=False))
R.to_pickle("h7_plateau.pkl")
