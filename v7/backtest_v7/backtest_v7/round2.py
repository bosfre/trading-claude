import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=eng.load_series(); base=exp.eval_variant(S,{})
V={}
# H: vecindad de cortos selectivos (largo ya validado como V6)
for sN,sL in itertools.product((140,210,280,420,560),(800,1200,1600,2400)):
    for sw in (1.0,0.5):
        V[f"H cortos N={sN}h EMA={sL}h riesgoC x{sw}"]=dict(p=dict(short=1,sN_h=sN,sL_h=sL),ext=dict(fund_s=-1),sw=sw)
# D: pirámide, vecindad y 'free-roll'
for pa,pf,pn in itertools.product((3,4,5,6,8),(0.25,0.5),(1,2)):
    V[f"D pirámide +{pa}ATR x{pf} n={pn}"]=dict(ext=dict(pyr_at=pa,pyr_frac=pf,pyr_n=pn))
rows=[]
for name,v in V.items():
    r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(name,d); rows.append(sm); exp.log_trial(name,sm)
T=pd.DataFrame(rows); T.to_pickle("round2.pkl")
print("=== CORTOS (selectivos) ===")
print(T[T.variante.str.startswith("H")].to_string(index=False))
print("\n=== PIRÁMIDE ===")
print(T[T.variante.str.startswith("D")].to_string(index=False))
