"""Ronda 11a: 7 hipotesis pre-registradas (v11_prereg.txt), SOLO TRAIN/VAL/DEV, ETH+BTC+DOGE x 1H/4H/1D, contra V10 (= V9)."""
import exp11, exp9, numpy as np, pandas as pd, sys
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
S = exp11.load(True)
def V(name, fam, nq=None, usd=None, mode="filter", w=0.5):
    return dict(name=name, fam=fam, p=dict(xref=exp9.B800), x=dict(macro=dict(nq=nq, usd=usd, mode=mode, w=w)), y={})
VS = [V("NQ>SMA100", "M1", nq=100), V("NQ>SMA200", "M1", nq=200),
      V("USD<SMA100", "M2", usd=100), V("USD<SMA200", "M2", usd=200),
      V("NQ&USD 100", "M3", nq=100, usd=100), V("NQ&USD 200", "M3", nq=200, usd=200),
      V("tamano x0.5 NQ&USD200", "M4", nq=200, usd=200, mode="size")]
rows = []
for v in VS:
    sm, D, res = exp9.trial9(S, v); sm["fam"] = v["fam"]; rows.append(sm)
    print(f"{v['name']:<24}", {tf: (sm[f'E{tf}_tr'], sm[f'E{tf}_va'], sm[f'B{tf}'], sm[f'D{tf}'], sm[f'dMDD_{tf}'], sm[f'dR_{tf}']) for tf in exp9.TFS},
          {k: bool(x) for k, x in sm['acc'].items()}); sys.stdout.flush()
pd.DataFrame(rows).to_pickle("round11a.pkl")
print("\ncolumnas por TF: (dCalmar ETH TRAIN, ETH VAL, BTC DEV, DOGE DEV, dMDD ETH pp, dR/op ETH)")
