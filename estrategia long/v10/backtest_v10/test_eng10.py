"""Test: con las palancas nuevas apagadas, eng10 reproduce al bit la V8 de eng8 (curva de equity y operaciones) en las 9 series."""
import numpy as np, exp9, eng8
import exp10
S = exp10.load(True)
ok = True
for a in exp9.ASSETS:
    for tf in exp9.TFS:
        s = S[(a, tf)]
        d, q = exp9.gen9(s, exp9.V8)
        eq8, ex8, tr8 = eng8.run8(s, d, q["kI"], q["kT"], risk=q["risk"], mlev=q["mlev"], tp=q["tp"], be=q["be"], tron=q["tron"], ext={})
        eq10, ex10, tr10 = exp10.run10v(s, exp9.V8)
        same = np.array_equal(np.nan_to_num(eq8, nan=-1), np.nan_to_num(eq10, nan=-1)) and tr8.shape == tr10.shape and np.array_equal(tr8[:, :9], tr10[:, :9])
        print(a, tf, "operaciones", len(tr8), len(tr10), "IDENTICO" if same else "DIFERENTE", "" if same else f"max|d eq|={np.nanmax(np.abs(eq8-eq10)):.3e}")
        ok &= same
print("TEST", "OK" if ok else "FALLA")
