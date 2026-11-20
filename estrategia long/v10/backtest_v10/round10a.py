"""Ronda 10a: 12 hipotesis pre-registradas (v10_prereg.txt), SOLO TRAIN/VAL/DEV, ETH+BTC+DOGE x 1H/4H/1D, contra V9."""
import exp10, exp9, numpy as np, pandas as pd, sys
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
S = exp10.load(True)
def V(name, fam, x=None, y=None, p=None):
    pp = dict(xref=exp10.B800); pp.update(p or {}); return dict(name=name, fam=fam, p=pp, x=x or {}, y=y or {})
VS = [V("vol>=1.0x", "G1", x=dict(vol_min=1.0)), V("vol>=1.5x", "G1", x=dict(vol_min=1.5)),
      V("estanc 280h->3.5", "G2", y=dict(st_h=280, st_k=3.5)), V("estanc 560h->3.5", "G2", y=dict(st_h=560, st_k=3.5)), V("estanc 560h->4.0", "G2", y=dict(st_h=560, st_k=4.0)),
      V("enfria 100h", "G3", y=dict(cool_h=100)), V("enfria 300h", "G3", y=dict(cool_h=300)),
      V("fallida 50h/1ATR", "G4", y=dict(fb_h=50, fb_m=1.0)), V("fallida 150h/1ATR", "G4", y=dict(fb_h=150, fb_m=1.0)), V("fallida 150h/2ATR", "G4", y=dict(fb_h=150, fb_m=2.0)),
      V("ancla cierres", "G5", y=dict(anc_c=1)), V("confirma 2 cierres", "G6", x=dict(confirm=2))]
rows = []
for v in VS:
    sm, D, res = exp9.trial9(S, v); sm["fam"] = v["fam"]; rows.append(sm)
    print(f"{v['name']:<20}", {tf: (sm[f'E{tf}_tr'], sm[f'E{tf}_va'], sm[f'B{tf}'], sm[f'D{tf}'], sm[f'dMDD_{tf}'], sm[f'dR_{tf}']) for tf in exp9.TFS},
          {k: bool(x) for k, x in sm['acc'].items()}); sys.stdout.flush()
pd.DataFrame(rows).to_pickle("round10a.pkl")
print("\ncolumnas por TF: (dCalmar ETH TRAIN, ETH VAL, BTC DEV, DOGE DEV, dMDD ETH pp, dR/op ETH)")
