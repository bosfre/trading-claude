"""Ronda 8C (H7/H8): información nueva = régimen de BTC (filtro/tamaño) y fuerza relativa ETH/BTC. Solo ETH y DOGE se ven afectados (BTC no cambia)."""
import exp8, data8, pandas as pd
S=data8.load_all(False,pre=False); exp8.set_refs(S)
V=[]
for L in (400,800,1600):
    V.append(dict(name=f"H7 largos solo si BTC>EMA{L}h",fam="H7_btcreg",p=dict(xref=dict(type="btc",mode="filter",L_h=L))))
    V.append(dict(name=f"H7 tamaño x0.5 si BTC<EMA{L}h",fam="H7_btcreg",p=dict(xref=dict(type="btc",mode="size",L_h=L,w=0.5))))
for L in (400,800,1600):
    V.append(dict(name=f"H8 largos solo si ETH/BTC>EMA{L}h",fam="H8_ratio",p=dict(xref=dict(type="ratio",mode="filter",L_h=L))))
    V.append(dict(name=f"H8 tamaño x0.5 si ETH/BTC<EMA{L}h",fam="H8_ratio",p=dict(xref=dict(type="ratio",mode="size",L_h=L,w=0.5))))
rows=[]
for v in V:
    sm,D,res=exp8.trial(S,v,assets=("ETH","DOGE","BTC"))
    sm["acc"]="".join(tf[:2] if a else "--" for tf,a in sm["acc"].items()); rows.append(sm)
R=pd.DataFrame(rows); R.to_pickle("round8c.pkl")
pd.set_option("display.width",250)
print(R[["name","E1h_tr","E1h_va","E4h_tr","E4h_va","E1d_tr","E1d_va","D1h","D4h","D1d","dMDD_1h","dMDD_4h","dMDD_1d","acc"]].to_string(index=False))
