import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=eng.load_series(); base=exp.eval_variant(S,{})
rows=[]
for n,l in itertools.product((100,120,140,170,200),(600,700,800,900,1000)):
    v=dict(p=dict(N_h=float(n),L_h=float(l)))
    r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(f"core N={n} L={l}",d); sm["N"]=n; sm["L"]=l; rows.append(sm); exp.log_trial(sm["variante"],sm)
T=pd.DataFrame(rows)
for col in ("ETH_trn","ETH_val","c1h","c4h","c1d","BTC","DOGE","dCAGR_ETH"):
    print(f"\n{col}  (filas N, columnas L)"); print(T.pivot(index="N",columns="L",values=col).round(2).to_string())
rows=[]
for a_h in (28,42,84,112,168):
    v=dict(p=dict(A_h=float(a_h)));r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(f"ATR {a_h}h",d); rows.append(sm); exp.log_trial(sm["variante"],sm)
print("\n=== ventana ATR"); print(pd.DataFrame(rows).to_string(index=False))
