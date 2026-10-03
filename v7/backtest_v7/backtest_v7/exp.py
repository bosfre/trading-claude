"""Arnés de experimentos V7. SOLO ventanas de selección (TRAIN, VAL, DEV). El OOS está bloqueado hasta la evaluación final.
Un 'variant' es un dict:
  p     : parámetros de gen.gen (se mezclan sobre V6P)
  ext   : palancas extra del motor eng7
  vr    : dict(span_h=..., mode='filter'|'size', thr=..., w_lo=.., w_hi=..)  (régimen de volatilidad, causal)
  kw    : kwargs de run7 (kI/kT salen de p; risk, mlev, tp salen de p)
"""
import numpy as np, pandas as pd, eng, eng7, gen, lab, json, os, time
from eng import ema_nb

SEL = ("TRAIN", "VAL", "DEV")           # ventanas permitidas en selección
_LOG = "trials_log.csv"
_cache = {}


def vol_ratio(s, d, span_h):
    key = (s.a, s.tf, span_h)
    if key not in _cache:
        atrp = d["atr"] / s.c
        n = max(5, int(round(span_h / eng.TFH[s.tf])))
        slow = ema_nb(np.nan_to_num(atrp, nan=np.nanmedian(atrp)), n)
        _cache[key] = atrp / slow
    return _cache[key]


def build(s, v):
    q = dict(lab.V6P); q.update(v.get("p", {}))
    d, q = gen.gen(s, q)
    vr = v.get("vr")
    if vr:
        r = vol_ratio(s, d, vr["span_h"])
        ok = np.isnan(r)
        if vr["mode"] == "filter":
            d["le"] = d["le"] & (ok | (r <= vr["thr"]))
        elif vr["mode"] == "size":
            szm = np.where(ok, 1.0, np.where(r <= vr["thr"], vr["w_lo"], vr["w_hi"]))
            d["szm"] = szm
    lm = v.get("lreg")
    if lm:
        Lb = gen.hb(lm["L_h"], s.tf, 2); em2 = s.ind("ema", Lb); okm = np.isnan(em2)
        if lm["mode"] == "filter":
            d["le"] = d["le"] & (okm | (s.c > em2))
        else:
            d["szm"] = np.where(okm | (s.c > em2), 1.0, lm["w"])
    if v.get("rexit"):
        Lb = gen.hb(v["rexit"], s.tf, 2); em3 = s.ind("ema", Lb)
        d["lx"] = np.nan_to_num(s.c < em3, nan=0).astype(bool)
    if v.get("sw") is not None and "se" in d:
        d["szm"] = np.where(d["se"] & ~d["le"], v["sw"], d.get("szm", np.ones(len(d["le"]))))
    return d, q


def run_variant(s, v):
    d, q = build(s, v)
    ext = dict(v.get("ext") or {})
    if "ts_h" in ext:
        ext["ts_bars"] = max(1, int(round(ext.pop("ts_h") / eng.TFH[s.tf])))
    return eng7.run7(s, d, q["kI"], q["kT"], risk=q["risk"], mlev=q["mlev"], tp=q["tp"], be=q["be"], tron=q["tron"], ext=ext,
                     cost=v.get("cost", 1.0))


def metrics(s, eq, trd, wins=SEL):
    return {w: s.stat(eq, trd, w) for w in wins}


def eval_variant(S, v, assets=lab.ASSETS, tfs=lab.TFS, wins=SEL):
    out = {}
    for a in assets:
        for tf in tfs:
            s = S[(a, tf)]
            eq, ex, trd = run_variant(s, v)
            out[(a, tf)] = metrics(s, eq, trd, wins)
    return out


def calm(m):
    c = m["calmar"]
    return c if c == c else np.nan


def delta_table(base, var, wins=SEL):
    """Filas por (activo,tf,ventana): métricas base, variante y delta."""
    rows = []
    for k in base:
        for w in wins:
            b, x = base[k][w], var[k][w]
            rows.append(dict(asset=k[0], tf=k[1], w=w, b_ret=b["ret"], v_ret=x["ret"], b_cagr=b["cagr"], v_cagr=x["cagr"], b_mdd=b["mdd"],
                             v_mdd=x["mdd"], b_cal=calm(b), v_cal=calm(x), b_n=b["trades"], v_n=x["trades"], b_sh=b["sharpe"], v_sh=x["sharpe"]))
    d = pd.DataFrame(rows)
    d["d_cal"] = d.v_cal - d.b_cal
    d["d_mdd"] = d.v_mdd - d.b_mdd
    d["d_cagr"] = d.v_cagr - d.b_cagr
    d["d_sh"] = d.v_sh - d.b_sh
    return d


def summarize(name, d):
    """Resumen de una variante frente a la base: criterios de aceptación pre-registrados."""
    e = d[d.asset == "ETH"]
    tr = e[e.w == "TRAIN"].d_cal.mean(); va = e[e.w == "VAL"].d_cal.mean()
    dev = e[e.w == "DEV"]
    per_tf = {r.tf: r.d_cal for r in dev.itertuples()}
    btc = d[(d.asset == "BTC") & (d.w == "DEV")].d_cal.mean(); doge = d[(d.asset == "DOGE") & (d.w == "DEV")].d_cal.mean()
    mdd = dev.d_mdd.mean()
    cells = d[d.w.isin(["TRAIN", "VAL"])]
    frac = (cells.d_cal > 0).mean()
    npos_tf = sum(1 for v in per_tf.values() if v > 0)
    acc = (tr > 0) and (va > 0) and npos_tf >= 2 and (btc > -0.05) and (doge > -0.05) and (mdd > -0.01)
    return dict(variante=name, ETH_trn=round(tr, 2), ETH_val=round(va, 2), c1h=round(per_tf["1h"], 2), c4h=round(per_tf["4h"], 2), c1d=round(per_tf["1d"], 2),
                BTC=round(btc, 2), DOGE=round(doge, 2), dMDD_ETH=round(mdd * 100, 1), dCAGR_ETH=round(dev.d_cagr.mean() * 100, 1),
                celdas_mejoran=round(frac, 2), ACEPTA=bool(acc))


def log_trial(name, summ):
    row = dict(summ); row["variante"] = name
    hdr = not os.path.exists(_LOG)
    pd.DataFrame([row]).to_csv(_LOG, mode="a", header=hdr, index=False)


# ---------------- utilidades adicionales ----------------
def yearly(s, eq, years=None):
    e = pd.Series(eq, index=s.idx).ffill()
    ye = e.resample("YE").last()
    r = (ye / ye.shift(1) - 1)
    r.iloc[0] = ye.iloc[0] / e.dropna().iloc[0] - 1
    r.index = r.index.year
    return r if years is None else r.loc[[y for y in r.index if y in years]]


def ens_run(s, sleeves, base_v=None):
    """Conjunto de sleeves (lista de variants). Equity combinada = media de retornos por barra (cuenta compartida rebalanceada)."""
    eqs, trs = [], []
    for v in sleeves:
        eq, ex, trd = run_variant(s, v)
        eqs.append(eq); trs.append(trd)
    E = np.vstack(eqs)
    r = np.vstack([np.r_[0.0, np.diff(e) / e[:-1]] for e in E])
    r = np.nan_to_num(r)
    comb = np.cumprod(1 + r.mean(axis=0))
    tr = np.vstack(trs)
    return comb, tr


def scale_risk(v, m):
    w = dict(v); p = dict(w.get("p", {})); p["risk"] = lab.V6P["risk"] * m; w["p"] = p; return w


def matched_dd(S, v, a, tf, target_mdd, win="DEV", lo=0.3, hi=3.0, it=22):
    """Escala el riesgo de la variante v (multiplicador m) hasta que el MDD de 'win' coincida con target_mdd. Devuelve (m, stats)."""
    s = S[(a, tf)]
    for _ in range(it):
        m = (lo + hi) / 2
        eq, ex, trd = run_variant(s, scale_risk(v, m))
        st = s.stat(eq, trd, win)
        if st["mdd"] < target_mdd: hi = m      # demasiado DD -> menos riesgo
        else: lo = m
    return m, st
