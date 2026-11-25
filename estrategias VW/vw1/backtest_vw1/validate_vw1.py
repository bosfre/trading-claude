"""Validación del motor conjunto: con un solo lado activo y las convenciones del motor original debe reproducir a V10 y a W10.
  1) LONG solo, costes 'orig', strict=0, fbL=1  vs  exp10/eng10 (motor V10)  en 2017-08 -> 2026-10 (serie extendida).
  2) SHORT solo, costes 'orig', strict=1          vs  backtest_w11.run_cfg (config W10) en los CSV 2017-08 -> 2026-01-06.
Salida: validacion_motor.csv"""
import numpy as np, pandas as pd, os
import prep_vw as P
from prep_vw import exp9, exp10, W, TFS

rows = []
S = P.series()
print("== 1) LONG solo (V10) ==")
for tf in TFS:
    s = S[("ETH", tf)]
    eq0, ex0, trd0 = exp9.run9(s, exp10.V9)
    m0 = exp9.wstat(s, eq0, ex0, trd0, "2017-08-17", None)
    R = P.run(tf, enL=True, enS=False, model="orig", strict=False, fbL=1.0)
    m1 = P.stats(R, "FULL")
    d_eq = float(np.nanmax(np.abs(R["eq"] / eq0 - 1)))
    print(f"{tf}: legacy ret {m0['ret']*100:9.2f}% mdd {m0['mdd']*100:6.2f}% n {m0['n']:3d} | motor VW ret {m1['ret']*100:9.2f}% mdd {m1['mdd']*100:6.2f}% n {m1['n']:3d} | max|eq/eq0-1| = {d_eq:.2e}")
    rows.append(dict(lado="LONG V10", tf=tf, ref_ret=m0["ret"], ref_mdd=m0["mdd"], ref_n=m0["n"], vw_ret=m1["ret"], vw_mdd=m1["mdd"], vw_n=m1["n"], max_dif_equity=d_eq))

print("\n== 2) SHORT solo (W10) en los CSV (hasta 2026-01-06) ==")
csv_end = {"1h": "2026-01-06 09:00:00", "4h": "2026-01-06 12:00:00", "1d": "2026-01-06"}
for tf in TFS:
    A = P.arrays(tf); idx = A["idx"]; n_end = int(idx.searchsorted(pd.Timestamp(csv_end[tf]), side="right"))
    # referencia: el motor de W sobre exactamente esas filas
    df = pd.read_csv(os.path.join(P.ROOT, "csvs", f"ETHUSDT_{tf}.csv"), parse_dates=["timestamp"]).set_index("timestamp")
    assert len(df) == n_end and (df.index == idx[:n_end]).all(), (len(df), n_end)
    T = W.TF(df, tf); out, eqw, trw = W.run_cfg(T, W.W10[tf], W.RISK10[tf])
    ref = out["TOTAL"]
    R = P.run(tf, enL=False, enS=True, model="orig", strict=True, n_end=n_end)
    m1 = P.stats(R, "FULL")
    d_eq = float(np.nanmax(np.abs(R["eq"][W.bounds(T, "TOTAL")[0]:] / eqw - 1)))
    print(f"{tf}: legacy W10 ret {ref['ret']:8.2f}% dd {ref['dd']:6.2f}% n {ref['n']:3d} pf {ref['pf']:.2f} | motor VW ret {m1['ret']*100:8.2f}% dd {m1['mdd']*100:6.2f}% n {m1['n']:3d} pf {m1['pf']:.2f} | max|eq/eq0-1| = {d_eq:.2e}")
    rows.append(dict(lado="SHORT W10", tf=tf, ref_ret=ref["ret"] / 100, ref_mdd=ref["dd"] / 100, ref_n=ref["n"], vw_ret=m1["ret"], vw_mdd=m1["mdd"], vw_n=m1["n"], max_dif_equity=d_eq))

pd.DataFrame(rows).to_csv(os.path.join(P.HERE, "validacion_motor.csv"), index=False)
