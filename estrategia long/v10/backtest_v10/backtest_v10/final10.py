"""Analisis final V10 vs V9 (ETH 1H/4H/1D): ventanas, frontera de riesgo, costes, sensibilidad de parametros, retorno por ano.
V10 = V9 en logica (ninguna palanca nueva paso el pre-registro). Lo que cambia en V10 es el PRESET DE RIESGO opcional (desescalado de riesgo)."""
import exp10, exp9, numpy as np, pandas as pd, json, sys
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
S = exp10.load(True); B = exp10.B800; TFS = exp9.TFS
def V(risk=None, **p):
    pp = dict(xref=B); pp.update(p)
    if risk is not None: pp["risk"] = risk / 100
    return dict(name="v", p=pp, x={}, y={})
WIN = {"COMUN 2017-08->2026-10": ("2017-08-17", None), "TRAIN 2017-08->2021": ("2017-08-17", "2022-01-01"), "VAL 2022-23": ("2022-01-01", "2024-01-01"),
       "OOS1 2024->2026-01": ("2024-01-01", "2026-01-11"), "OOS2 2026-01->10": ("2026-01-11", None), "ULTIMOS 2 ANIOS 2024-01->2026-10": ("2024-01-01", None)}
KEYS = ("yrs", "ret", "cagr", "mdd", "calmar", "sharpe", "n", "trades_yr", "win", "pf", "pf_usd", "avg_ret", "med_ret", "avgR", "avg_win", "avg_loss", "payoff", "hours", "expo")
def metrics(tf, v, t0, t1, cost=1.0, a="ETH"):
    s = S[(a, tf)]; eq, ex, trd = exp9.run9(s, v, cost); return exp9.wstat(s, eq, ex, trd, t0, t1)

# 1) frontera de riesgo (a igual DD en la ventana comun; la ventana "ALL" de ETH = comun salvo el calentamiento)
def risk_for_dd(tf, target):
    lo, hi = 0.2, 4.0; s = S[("ETH", tf)]
    for _ in range(24):
        m = (lo + hi) / 2; eq, ex, trd = exp9.run9(s, exp9.scale_risk(V(), m)); st = exp9.wstat(s, eq, ex, trd, None, None, "ALL")
        if st["mdd"] < target: hi = m
        else: lo = m
    return 5.0 * m
front = []
for tf in TFS:
    for tgt in (-0.10, -0.12, -0.15, -0.20):
        r = round(risk_for_dd(tf, tgt), 1); m = metrics(tf, V(r), "2017-08-17", None)
        front.append(dict(tf=tf, dd_objetivo=tgt, riesgo_pct=r, **{k: m[k] for k in ("ret", "cagr", "mdd", "calmar", "n", "win", "pf", "pf_usd", "avg_ret", "avgR")}))
    m = metrics(tf, V(5.0), "2017-08-17", None)
    front.append(dict(tf=tf, dd_objetivo=np.nan, riesgo_pct=5.0, **{k: m[k] for k in ("ret", "cagr", "mdd", "calmar", "n", "win", "pf", "pf_usd", "avg_ret", "avgR")}))
F = pd.DataFrame(front); F.to_csv("frontera_riesgo_V10.csv", index=False)
print(F.assign(ret=F.ret * 100, cagr=F.cagr * 100, mdd=F.mdd * 100).round(2).to_string(index=False))
PRESET = {tf: float(F[(F.tf == tf) & (F.dd_objetivo == -0.15)].riesgo_pct.iloc[0]) for tf in TFS}
print("\nPRESET DD~15 %:", PRESET)

# 2) comparativa por ventana: V9 (riesgo 5 %) = V10 estandar | V10 preset DD~15 %
rows = []
for tf in TFS:
    for ver, v in (("V9 (= V10 estandar, riesgo 5 %)", V(5.0)), (f"V10 preset DD~15 % (riesgo {PRESET[tf]} %)", V(PRESET[tf]))):
        for wn, (t0, t1) in WIN.items():
            m = metrics(tf, v, t0, t1)
            if m: rows.append(dict(version=ver, tf=tf, ventana=wn, **{k: m.get(k) for k in KEYS}))
C = pd.DataFrame(rows); C.to_csv("comparativa_V9_V10.csv", index=False)

# 3) costes x1/x2/x3 en la ventana comun
cr = []
for tf in TFS:
    for ver, v in (("V9", V(5.0)), ("V10 preset", V(PRESET[tf]))):
        for cm in (1.0, 2.0, 3.0):
            m = metrics(tf, v, "2017-08-17", None, cost=cm)
            cr.append(dict(version=ver, tf=tf, costes=f"x{cm:g}", cagr=m["cagr"], mdd=m["mdd"], calmar=m["calmar"], pf=m["pf"], pf_usd=m["pf_usd"], win=m["win"], avg_ret=m["avg_ret"]))
pd.DataFrame(cr).to_csv("costes_V10.csv", index=False)

# 4) sensibilidad de parametros (una a una) sobre V9, ETH + media BTC/DOGE (Calmar, ventana DEV y comun ETH)
OAT = [("base", {})] + [(f"N {x} h", dict(N_h=x)) for x in (100, 120, 170, 200)] + [(f"EMA {x} h", dict(L_h=x)) for x in (600, 700, 900, 1000)] \
      + [(f"k {x}", dict(kI=x, kT=x)) for x in (4.0, 4.5, 5.5, 6.0)] + [(f"TP {x}", dict(tp=x)) for x in (0, 15, 25, 30)] + [(f"ATR {x} h", dict(A_h=x)) for x in (40, 72)]
sr = []
for name, p in OAT:
    v = V(5.0, **p)
    for tf in TFS:
        m = metrics(tf, v, "2017-08-17", None); d = metrics(tf, v, "2017-08-17", "2024-01-01")
        ob = [metrics(tf, v, "2017-08-17", "2024-01-01", a=a) for a in ("BTC", "DOGE")]
        sr.append(dict(param=name, tf=tf, cagr=m["cagr"], mdd=m["mdd"], calmar=m["calmar"], calmar_dev=d["calmar"], n=m["n"], calmar_btc_dev=ob[0]["calmar"], calmar_doge_dev=ob[1]["calmar"]))
    sys.stdout.flush()
SR = pd.DataFrame(sr); SR.to_csv("sensibilidad_parametros_V10.csv", index=False)

# 5) retorno por ano
yr = {}
for tf in TFS:
    s = S[("ETH", tf)]; eq, ex, trd = exp9.run9(s, V(5.0)); e = pd.Series(eq, index=s.idx).ffill(); ye = e.resample("YE").last(); r = ye / ye.shift(1) - 1; r.index = r.index.year
    yr[tf] = r
pd.DataFrame(yr).to_csv("retorno_anual_V10.csv")
json.dump(PRESET, open("preset_riesgo_V10.json", "w"))
print("\nOK: CSV escritos")
