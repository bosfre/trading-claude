"""Reproduce la linea base V9(=V8) en ETH 1H/4H/1D sobre la ventana comun 2017-08-17 -> fin de datos.
Referencia informe V9: 1H +1429.1% DD -21.8% | 4H +1009.5% DD -17.3% | 1D +463.9% DD -23.2%"""
import exp9, numpy as np, pandas as pd, time
pd.set_option("display.width", 250)
t0 = time.time()
S = exp9.load(True)
print("carga", round(time.time() - t0, 1), "s")
for a in ("ETH", "BTC", "DOGE"):
    for tf in exp9.TFS:
        s = S[(a, tf)]
        print(a, tf, s.n, s.idx[0], s.idx[-1])
print()
ref = {"1h": (1429.1, -21.8, 143), "4h": (1009.5, -17.3, 126), "1d": (463.9, -23.2, 105)}
for tf in exp9.TFS:
    s = S[("ETH", tf)]
    t1 = time.time(); eq, ex, trd = exp9.run9(s, exp9.V8)
    m = exp9.wstat(s, eq, ex, trd, "2017-08-17", None)
    print(f"ETH {tf}: ret {m['ret']*100:8.1f}%  DD {m['mdd']*100:6.1f}%  CAGR {m['cagr']*100:5.1f}%  n {m['n']:4d}  win {m['win']*100:4.1f}%  PF% {m['pf']:.2f}  PF$ {m['pf_usd']:.2f}"
          f"  | informe V9: {ref[tf]}   ({time.time()-t1:.1f}s)")
