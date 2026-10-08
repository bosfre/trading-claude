"""V7 (= V9 sin el filtro de regimen de BTC) re-ejecutada con los CSV actuales, ventana comun 2017-08-17 -> 2026-10-03, para el apartado 6 del informe."""
import exp10, exp9, pandas as pd
S = exp10.load(True); rows = []
for tf in exp9.TFS:
    s = S[("ETH", tf)]
    for name, v in (("V7 (sin filtro BTC)", dict(name="V7", p={}, x={}, y={})), ("V9 (con filtro BTC)", dict(name="V9", p=dict(xref=exp10.B800), x={}, y={}))):
        eq, ex, trd = exp9.run9(s, v); m = exp9.wstat(s, eq, ex, trd, "2017-08-17", None)
        rows.append(dict(version=name, tf=tf, ret=m["ret"], cagr=m["cagr"], mdd=m["mdd"], calmar=m["calmar"], n=m["n"], win=m["win"], pf=m["pf"]))
R = pd.DataFrame(rows); R.to_csv("v7_vs_v9_ref_V10.csv", index=False)
x = R.copy()
for c in ("ret", "cagr", "mdd", "win"): x[c] = (x[c] * 100).round(1)
print(x.round(2).to_string(index=False))
