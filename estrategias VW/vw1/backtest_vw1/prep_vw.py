"""Datos, señales y métricas del backtest conjunto VW1.
Las señales se generan con el CÓDIGO ORIGINAL de cada versión (sin reescribirlas):
  LONG  : estrategia long/v10/backtest_v10  (exp10.gen10 sobre la variante V9 = V10: Donchian 140 h, EMA 800 h, filtro BTC > EMA 800 h, k 5, TP 20 ATR, riesgo 5 %, mlev 2x)
  SHORT : estrategia short/w11/backtest_w11.py  (build_signal con la configuración W10: EMA 600, ruptura 45, pullback 40/55, percentil de volatilidad 70/75/65, mult 2/3/3)
Datos: ETH y BTC 1h/4h/1d de csvs/ (2017-08-17 -> 2026-01-06) + tramo 2026-01 -> 2026-10-03 de Twelve Data (el mismo que usó V10; ver data8.py).
Todos los indicadores son causales, así que calcularlos sobre la serie completa y recortar equivale a calcularlos sobre la serie recortada."""
import os, sys, importlib.util
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
V10 = os.path.join(ROOT, "estrategia long", "v10", "backtest_v10")
W11 = os.path.join(ROOT, "estrategia short", "w11")
sys.path.insert(0, V10); sys.path.insert(0, HERE)
import exp10, exp9                       # noqa: E402  (motor y señales de V10)
import eng_vw                            # noqa: E402

_spec = importlib.util.spec_from_file_location("backtest_w11", os.path.join(W11, "backtest_w11.py"))
W = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(W)

TFS = ("1h", "4h", "1d")
RISK_L = 0.05                            # V10 estándar (se lee de la variante V9; solo documental)
RISK_S = W.RISK10                        # {'1d': .05, '4h': .04, '1h': .06}
CUTS = {"TRAIN": ("2017-08-17", "2022-01-01"), "VAL": ("2022-01-01", "2024-01-01"), "OOS1": ("2024-01-01", "2026-01-11"),
        "OOS2": ("2026-01-11", None), "ORIG": ("2017-08-17", "2026-01-11"), "FULL": ("2017-08-17", None)}

_S = None; _CACHE = {}
def series():
    global _S
    if _S is None: _S = exp10.load(True)
    return _S

def arrays(tf):
    """o,h,l,c, (atrL, leL, warmL), (atrS, sS) y el índice temporal de ETH en la temporalidad tf."""
    if tf in _CACHE: return _CACHE[tf]
    S = series(); s = S[("ETH", tf)]
    d, q, hi = exp10.gen10(s, exp10.V9)
    assert abs(q["risk"] - RISK_L) < 1e-12 and q["mlev"] == 2.0 and q["kI"] == 5.0 and q["kT"] == 5.0 and q["tp"] == 20, q
    T = W.TF(s.df, tf); cfg = W.W10[tf]
    sS = W.build_signal(T, cfg)
    assert np.array_equal(T.c, s.c) and np.array_equal(T.o, s.o)
    out = dict(o=s.o, h=s.h, l=s.l, c=s.c, idx=s.idx, atrL=np.asarray(d["atr"], dtype=np.float64), leL=np.asarray(d["le"], dtype=np.bool_), warmL=int(d["warm"]),
               atrS=np.asarray(T.atr, dtype=np.float64), sS=np.asarray(sS, dtype=np.bool_), mS=float(cfg["m"]), tpS=cfg.get("tp"), riskS=RISK_S[tf], riskL=q["risk"])
    _CACHE[tf] = out; return out

def run(tf, enL=True, enS=True, model="pine", cm=1.0, strict=True, fbL=None, flip=False, n_end=None, riskL=None, riskS=None):
    """Una pasada del motor conjunto. fbL por defecto: 1 con costes 'orig' (motor V10), 0 con costes 'pine' (Pine de V10)."""
    A = arrays(tf)
    if fbL is None: fbL = 1.0 if model == "orig" else 0.0
    (fL, sL, sxL, fuL), (fS, slS, fuS) = eng_vw.costs(model, tf, cm)
    tpS = A["tpS"]
    PL = np.array([5.0, 5.0, A["riskL"] if riskL is None else riskL, 2.0, 20.0, fL, sL, sxL, fuL], dtype=np.float64)
    PS = np.array([A["mS"], A["riskS"] if riskS is None else riskS, 2.0, (tpS[0] / 100.0 if tpS else 0.0), (tpS[1] if tpS else 0.0), fS, slS, fuS], dtype=np.float64)
    F = np.array([float(enL), float(enS), float(strict), float(fbL), float(flip)], dtype=np.float64)
    n = len(A["c"]) if n_end is None else int(n_end)
    eq, pos, tr, cnt = eng_vw.joint(A["o"][:n], A["h"][:n], A["l"][:n], A["c"][:n], A["atrL"][:n], A["leL"][:n], A["warmL"], A["atrS"][:n], A["sS"][:n], PL, PS, F)
    return dict(eq=eq, pos=pos, tr=tr, cnt=cnt, idx=A["idx"][:n], n=n)

def seg_idx(idx, seg):
    a, b = CUTS[seg]
    i0 = int(idx.searchsorted(pd.Timestamp(a))); i1 = len(idx) if b is None else int(idx.searchsorted(pd.Timestamp(b)))
    return i0, min(i1, len(idx))

def stats(R, seg="FULL", eq=None):
    """Métricas de una ventana. Operaciones = las que SALEN dentro de la ventana (criterio de V10/W)."""
    idx = R["idx"]; e = R["eq"] if eq is None else eq
    i0, i1 = seg_idx(idx, seg)
    if i1 - i0 < 5: return None
    base = e[i0 - 1] if i0 > 0 else 1.0
    x = e[i0:i1] / base
    pk = np.maximum.accumulate(np.r_[1.0, x])[1:]
    mdd = float((x / pk - 1).min()); ret = float(x[-1] - 1)
    yrs = (idx[i1 - 1] - idx[i0]).total_seconds() / 86400 / 365.25
    cagr = (1 + ret) ** (1 / yrs) - 1 if (yrs > 0.5 and ret > -1) else np.nan
    out = dict(ret=ret, cagr=cagr, mdd=mdd, calmar=(cagr / abs(mdd) if (mdd < 0 and cagr == cagr) else np.nan), yrs=yrs)
    tr = R["tr"]
    if len(tr):
        t = tr[(tr[:, 1] >= i0) & (tr[:, 1] < i1)]
    else:
        t = tr
    out["n"] = len(t)
    if len(t):
        pnl = t[:, 6]; r = t[:, 5]
        out.update(win=float((r > 0).mean()), pf=(float(pnl[pnl > 0].sum() / -pnl[pnl <= 0].sum()) if (pnl <= 0).any() and pnl[pnl <= 0].sum() < 0 else np.inf),
                   avg_ret=float(r.mean()), n_long=int((t[:, 2] == 1).sum()), n_short=int((t[:, 2] == -1).sum()),
                   pnl_long=float(pnl[t[:, 2] == 1].sum()), pnl_short=float(pnl[t[:, 2] == -1].sum()))
    else:
        out.update(win=np.nan, pf=np.nan, avg_ret=np.nan, n_long=0, n_short=0, pnl_long=0.0, pnl_short=0.0)
    out["expo"] = float((R["pos"][i0:i1] != 0).mean())
    return out

def yearly(R, eq=None):
    e = pd.Series(R["eq"] if eq is None else eq, index=R["idx"]).ffill()
    ye = e.resample("YE").last(); prev = ye.shift(1).fillna(1.0)
    r = ye / prev - 1; r.index = r.index.year
    return r

def blend(Ra, Rb, wa=0.5):
    """Equity de dos cuentas independientes (capital repartido wa / 1-wa, cada una compone la suya, sin reequilibrar)."""
    return wa * Ra["eq"] + (1 - wa) * Rb["eq"]
