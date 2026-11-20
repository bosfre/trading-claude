"""Arnes V11: filtros macro (Nasdaq, DXY sintetico) sobre V10. Reutiliza exp10/exp9 (metricas, criterio accept9) y sustituye run9 por run11v.
x = dict(macro=dict(nq=L|None, usd=L|None, mode='filter'|'size', w=0.5)).
Sin look-ahead: el dato macro del dia D se conoce desde D+1 00:00 UTC; cada barra usa el ultimo dato disponible en su hora de CIERRE."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v10", "backtest_v10"))  # motor y arnes de V10 (sin cambios)
import exp9, eng, eng10, exp10
exp9.LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trials11.jsonl")
HERE = os.path.dirname(os.path.abspath(__file__))
MAC = pd.read_csv(f"{HERE}/macro_daily.csv", parse_dates=["date"]).set_index("date")
_C = {}
def cond(key, L):
    """Serie diaria de condicion (1.0 cumple / 0.0 no / NaN sin dato) indexada por la fecha en que el dato YA es conocido (D + 1 dia)."""
    k = (key, L)
    if k not in _C:
        x = MAC[key].dropna()
        sma = x.rolling(L, min_periods=L).mean()
        c = (x > sma) if key == "nasdaq" else (x < sma)
        c = c.astype(float).where(sma.notna())
        c.index = c.index + pd.Timedelta(days=1)
        _C[k] = c
    return _C[k]
_O = {}
def macro_ok(s, nq, usd):
    """Array bool por barra: True si se cumplen las condiciones pedidas (o si no hay dato -> no filtra)."""
    k = (id(s), nq, usd)
    if k not in _O:
        closes = s.idx + pd.Timedelta(hours=eng.TFH[s.tf])
        ok = np.ones(s.n, dtype=bool)
        for key, L in (("nasdaq", nq), ("dxy_syn", usd)):
            if not L: continue
            c = cond(key, L)
            v = c.reindex(c.index.union(closes)).ffill().reindex(closes).values
            ok &= np.isnan(v) | (v > 0.5)
        _O[k] = ok
    return _O[k]

def gen11(s, v):
    d, q, hi = exp10.gen10(s, v)
    m = (v.get("x") or {}).get("macro")
    if m:
        ok = macro_ok(s, m.get("nq"), m.get("usd"))
        if m.get("mode", "filter") == "filter": d["le"] = d["le"] & ok
        else: d["szm"] = d.get("szm", np.ones(s.n)) * np.where(ok, 1.0, m.get("w", 0.5))
    return d, q, hi

def run11v(s, v, cost=1.0):
    d, q, hi = gen11(s, v)
    y = dict(v.get("y") or {})
    return eng10.run10(s, d, q["kI"], q["kT"], risk=q["risk"], mlev=q["mlev"], tp=q["tp"], be=q["be"], tron=q["tron"],
                       cost=cost * v.get("cost", 1.0), y=y, brk=hi)
exp9.run9 = run11v
load = exp9.load
