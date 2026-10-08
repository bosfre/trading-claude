"""Emulador de la semántica de TradingView para los Pine V6 / V7 (orden de ejecución y estado del script).
 - El script corre al CIERRE de cada barra; las órdenes enviadas se ejecutan en la apertura siguiente.
 - strategy.exit(stop) enviado en el cierre de la barra i solo puede saltar desde la barra i+1 (la barra de relleno NO tiene stop).
 - Indicadores 'exactos de Pine': EMA con semilla SMA, ATR = RMA(TR) con semilla SMA y TR[0]=high-low, Donchian = highest(high,N)[1].
Modos:
   v6pine : V6.pine tal cual (atrEntry se borra en la barra de señal -> TP inactivo; stop inicial = max(high de la barra de relleno) - k*ATR)
   v7pine : V7.pine (TP activo, entryRef = precio real de entrada, stop inicial = entryRef - k*ATR de la señal)
   pyref  : lógica del backtest de Python (stop activo ya en la barra de relleno) -> sirve para validar el emulador
"""
import numpy as np, pandas as pd
from numba import njit
from eng import stats_nb

@njit(cache=True)
def pine_rma(x, n, ema):
    m = len(x); out = np.full(m, np.nan)
    if m < n: return out
    s = 0.0
    for i in range(n): s += x[i]
    v = s / n; out[n - 1] = v
    a = 2.0 / (n + 1) if ema else 1.0 / n
    for i in range(n, m):
        v = a * x[i] + (1 - a) * v; out[i] = v
    return out

@njit(cache=True)
def pine_atr(h, l, c, n):
    m = len(c); tr = np.empty(m); tr[0] = h[0] - l[0]
    for i in range(1, m): tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    return pine_rma(tr, n, False)

@njit(cache=True)
def pine_highest_prev(x, n):
    m = len(x); out = np.full(m, np.nan)
    for i in range(n, m):
        v = x[i - n]
        for j in range(i - n + 1, i):
            if x[j] > v: v = x[j]
        out[i] = v
    return out

def pine_signals(df, tf_hours, N_h=140.0, L_h=800.0, A_h=56.0, ref=4.0):
    tfm = tf_hours * 60.0
    bN = int(max(5, round(N_h * 60 / tfm))); bL = int(max(20, round(L_h * 60 / tfm))); bA = int(max(10, round(A_h * 60 / tfm)))
    h = df.high.values.astype(np.float64); l = df.low.values.astype(np.float64); c = df.close.values.astype(np.float64)
    atr = pine_atr(h, l, c, bA) * np.sqrt(ref / tf_hours)
    dh = pine_highest_prev(h, bN); em = pine_rma(c, bL, True)
    ok = ~np.isnan(dh) & ~np.isnan(em) & ~np.isnan(atr) & (atr > 0)
    lc = ok & (c > np.nan_to_num(dh, nan=1e18)) & (c > np.nan_to_num(em, nan=1e18))
    return atr, lc

# P: 0 k,1 tp_mult,2 risk,3 mlev,4 comm,5 slip_frac,6 slip_abs,7 stop_extra,8 fund_bar,9 cash0
# F: 0 tp_on,1 floor_on,2 stop_fill_bar,3 margin_mode (0 ideal / 1 clip a 1x / 2 rechazar si >1x)
@njit(cache=True)
def tv_engine(o, h, l, c, atr, lc, P, F):
    n = len(c); eq = np.full(n, np.nan); tr = np.zeros((n // 2 + 10, 10)); nt = 0
    k = P[0]; tpm = P[1]; risk = P[2]; mlev = P[3]; comm = P[4]; sf = P[5]; sa = P[6]; sxe = P[7]; fund = P[8]; cash = P[9]
    tp_on = F[0] > 0; floor_on = F[1] > 0; sfb = F[2] > 0; mm = int(F[3])
    q = 0.0; epx = 0.0; stop = np.nan; stop_act = False; hse = 0.0; atr_e = 0.0; eref = 0.0; fresh = False
    pend_q = 0.0; pend_atr = 0.0; pend_close = False; ei = 0; cash_b = 0.0; szf = 0.0; sdist = 0.0
    for i in range(n):
        o_ = o[i]
        ex = False; fill = 0.0; rs = 0
        # 1) en la apertura: stop con gap, o cierre a mercado pendiente
        if q > 0 and stop_act and o_ <= stop:
            fill = (o_ * (1 - sf) - sa) * (1 - sxe); ex = True; rs = 0
        elif q > 0 and pend_close:
            fill = o_ * (1 - sf) - sa; ex = True; rs = 3
        pend_close = False
        # 2) entrada pendiente
        if (not ex) and q == 0 and pend_q > 0:
            fp = o_ * (1 + sf) + sa
            cash_b = cash; cash -= comm * pend_q * fp
            q = pend_q; epx = fp; ei = i; fresh = True; stop = np.nan; stop_act = False; atr_e = pend_atr
            szf = q * fp / cash_b
            pend_q = 0.0
            if sfb:
                stop = epx - k * atr_e; stop_act = True
        # 3) stop intrabarra
        if (not ex) and q > 0 and stop_act and l[i] <= stop:
            fill = (min(stop, o_) * (1 - sf) - sa) * (1 - sxe); ex = True; rs = 0
        if ex:
            cash += q * (fill - epx) - comm * q * fill
            tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = 1; tr[nt, 3] = epx; tr[nt, 4] = fill; tr[nt, 5] = cash / cash_b - 1.0
            tr[nt, 6] = 0.0; tr[nt, 7] = szf; tr[nt, 8] = rs; nt += 1
            q = 0.0; stop_act = False; stop = np.nan; fresh = False
        # 4) funding
        if q > 0: cash -= fund * q * c[i]
        # 5) equity al cierre
        eqn = cash + (q * (c[i] - epx) if q > 0 else 0.0)
        eq[i] = eqn
        # 6) script al cierre
        if q > 0:
            if fresh:
                if floor_on:
                    eref = epx; stop = eref - k * atr_e; hse = eref
                else:
                    hse = h[i]; stop = np.nan
                fresh = False
            if h[i] > hse: hse = h[i]
            cand = hse - k * atr[i]
            if np.isnan(stop) or cand > stop: stop = cand
            stop_act = True
            if tp_on and floor_on and c[i] >= eref + tpm * atr_e: pend_close = True
        else:
            if pend_q == 0 and lc[i] and (not np.isnan(atr[i])) and atr[i] > 0:
                spct = k * atr[i] / c[i]
                if spct > 0.0005:
                    sz = risk / spct
                    if sz > mlev: sz = mlev
                    ok = True
                    if mm == 1 and sz > 1.0: sz = 1.0
                    if mm == 2 and sz > 1.0: ok = False
                    if ok and eqn > 0:
                        pend_q = eqn * sz / c[i]; pend_atr = atr[i]
    return eq, tr[:nt]

MODES = {"v6pine": (0, 0, 0), "v7pine": (1, 1, 0), "pyref": (1, 1, 1), "v6_floor": (0, 1, 0), "py_notp": (0, 1, 1)}

def run_tv(df, tf_hours, mode="v7pine", k=5.0, tp=20.0, risk=0.05, mlev=2.0, comm=0.0006, slip_frac=0.0, slip_abs=0.0, stop_extra=0.0,
           fund8h=0.0, margin_mode=0, cash0=10000.0, sig=None, **kw):
    tp_on, floor_on, sfb = MODES[mode]
    atr, lc = pine_signals(df, tf_hours, **kw) if sig is None else sig
    P = np.array([k, tp, risk, mlev, comm, slip_frac, slip_abs, stop_extra, fund8h * tf_hours / 8.0, cash0], dtype=np.float64)
    F = np.array([tp_on, floor_on, sfb, margin_mode], dtype=np.float64)
    return tv_engine(df.open.values.astype(np.float64), df.high.values.astype(np.float64), df.low.values.astype(np.float64),
                     df.close.values.astype(np.float64), atr, lc, P, F)

def tv_stats(df, eq, tr, i0=0, i1=None):
    """Métricas sobre [i0,i1) con la misma función que el resto del proyecto."""
    i1 = len(df) if i1 is None else i1
    day = (df.index.values.astype("datetime64[D]")).astype(np.int64)
    dend = np.flatnonzero(np.r_[day[1:] != day[:-1], True]).astype(np.int64)
    e = eq.copy() / eq[0] if False else eq.copy()
    # normaliza a base 1 en i0-1 para tot/mdd (stats_nb ya usa eq[i0-1] como base)
    tot, mdd, sh, so, nt, nw, gp, gl = stats_nb(e / 1.0, dend, max(i0, 1), i1, tr[:, :] if len(tr) else np.zeros((0, 10)), len(tr))
    yrs = (df.index[i1 - 1] - df.index[i0]).total_seconds() / 86400 / 365.25
    cagr = (1 + tot) ** (1 / yrs) - 1 if (yrs > 0.5 and tot > -1) else np.nan
    return dict(ret=tot, cagr=cagr, mdd=mdd, trades=nt, win=(nw / nt if nt else np.nan), pf=(gp / gl if gl > 0 else np.nan), yrs=yrs,
                calmar=(cagr / abs(mdd) if (mdd < 0 and cagr == cagr) else np.nan))
