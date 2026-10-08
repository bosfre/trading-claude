"""Arnes V10: reutiliza exp9 (metricas, criterio accept9, igual-DD) y sustituye run9 por run10v (motor eng10).
Variante v = dict(name, fam, p=params gen8, x=filtros de senal, y=palancas del motor eng10).
 x: vol_min  (volumen de la vela de ruptura >= vol_min * media de las N velas previas; sin dato de volumen -> no filtra)
    confirm  (n de cierres consecutivos por encima del canal exigidos antes de entrar)
 y: st_h/st_k (estancamiento), cool_h, fb_h/fb_m (ruptura fallida), anc_c (ancla del trailing en cierres)."""
import numpy as np, pandas as pd
import exp9, eng, eng10
from sigs import hb

B800 = exp9.B800
V9 = exp9.V8          # V9 = V8 sin cambios de logica
V9["name"] = "V9"

def gen10(s, v):
    d, q = exp9.gen9(s, v)
    x = v.get("x", {}); tf = s.tf
    N = int(q["N_b"]) if q.get("N_b") else hb(q["N_h"], tf, q["minN"])
    hi = s.ind("hh", N)
    le = d["le"]
    if "vol_min" in x:
        vol = s.df.volume.values.astype(float)
        vma = pd.Series(vol).rolling(N).mean().shift(1).values
        ok = np.isnan(vma) | (vma <= 0) | (vol <= 0) | (vol >= x["vol_min"] * vma)
        le = le & ok
    if x.get("confirm", 1) > 1:
        raw = le.copy()
        for k in range(1, int(x["confirm"])):
            raw = raw & np.r_[np.zeros(k, dtype=bool), le[:-k]]
        le = raw
    d["le"] = le
    return d, q, hi

def run10v(s, v, cost=1.0):
    d, q, hi = gen10(s, v)
    y = dict(v.get("y") or {}); tfh = eng.TFH[s.tf]
    for hk, bk in (("st_h", "st_bars"), ("cool_h", "cool"), ("fb_h", "fb_bars")):
        if hk in y: y[bk] = max(1, int(round(y.pop(hk) / tfh)))
    return eng10.run10(s, d, q["kI"], q["kT"], risk=q["risk"], mlev=q["mlev"], tp=q["tp"], be=q["be"], tron=q["tron"],
                       cost=cost * v.get("cost", 1.0), y=y, brk=hi)

exp9.run9 = run10v      # todo el arnes (base_res, eval9, matched_dd9, ...) usa ahora el motor V10
load = exp9.load
