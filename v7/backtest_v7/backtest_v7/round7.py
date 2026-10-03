import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40)
S=eng.load_series(); base=exp.eval_variant(S,{})
rows=[]
for rm,rk in itertools.product((6,8,10),(6,7,8)):
    v=dict(ext=dict(rat_m=rm,rat_k=rk)); r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(f"C' ensanchar trailing MFE>={rm} -> kT={rk}",d); rows.append(sm); exp.log_trial(sm["variante"],sm)
print(pd.DataFrame(rows).to_string(index=False))
t=pd.read_csv("trials_log.csv"); print("\nTOTAL de hipótesis/variantes probadas y registradas hasta ahora:",len(t),"| aceptadas por el criterio pre-registrado:",int(t.ACEPTA.sum()))
