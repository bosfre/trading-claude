"""Verificacion independiente: rentabilidad = producto de (1+r_i) de las operaciones; win rate y PF desde la lista de operaciones;
DD desde la equity compuesta SOLO por cierres de operaciones (por eso es algo menor que el DD intrabarra del CSV)."""
import exp10, exp9, numpy as np, pandas as pd
S = exp10.load(True); B = exp10.B800
def V(risk): return dict(name="v", p=dict(xref=B, risk=risk / 100), x={}, y={})
CSV = pd.read_csv("comparativa_V9_V10.csv"); ok = True
CASES = (("1h", 5.0, "V9 (= V10 estandar, riesgo 5 %)"), ("4h", 5.0, "V9 (= V10 estandar, riesgo 5 %)"), ("1d", 5.0, "V9 (= V10 estandar, riesgo 5 %)"),
         ("1h", 3.3, "V10 preset DD~15 % (riesgo 3.3 %)"), ("4h", 4.2, "V10 preset DD~15 % (riesgo 4.2 %)"), ("1d", 3.0, "V10 preset DD~15 % (riesgo 3.0 %)"))
for tf, risk, ver in CASES:
    s = S[("ETH", tf)]; eq, ex, trd = exp9.run9(s, V(risk)); t0 = s.idx.searchsorted(pd.Timestamp("2017-08-17"))
    T = trd[trd[:, 1] >= t0]; r = T[:, 5]
    ret = np.prod(1 + r) - 1; win = (r > 0).mean(); pf = r[r > 0].sum() / -r[r <= 0].sum()
    curve = np.cumprod(1 + r); dd = (curve / np.maximum.accumulate(np.r_[1.0, curve])[1:] - 1).min()
    row = CSV[(CSV.tf == tf) & (CSV.version == ver) & (CSV.ventana == "COMUN 2017-08->2026-10")].iloc[0]
    good = abs(ret - row.ret) / row.ret < 0.01 and abs(win - row.win) < 1e-9 and abs(pf - row.pf) < 0.01 and int(row.n) == len(T)
    ok &= bool(good)
    print(f"{tf} riesgo {risk}: ops {len(T)} (CSV {int(row.n)}) | rent. {ret*100:8.1f}% (CSV {row.ret*100:8.1f}%) | win {win*100:.1f}% (CSV {row.win*100:.1f}%) | PF {pf:.2f} (CSV {row.pf:.2f}) | DD solo-cierres {dd*100:.1f}% (CSV intrabarra {row.mdd*100:.1f}%)  {'OK' if good else 'REVISAR'}")
print("VERIFICACION", "OK" if ok else "CON DIFERENCIAS")
