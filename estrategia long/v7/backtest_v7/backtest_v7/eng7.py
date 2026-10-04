"""Motor V7 = motor V6 (eng.py) + palancas opcionales. Con X=0 reproduce V6 al bit.
Convenciones idénticas: señal al cierre de i-1, entrada en apertura de i, stop intrabarra, gaps, TP al cierre (ejecuta en apertura siguiente).
X (parámetros extra):
 0 ddthr      umbral de drawdown (fracción, p.ej. 0.10) para throttle de riesgo (0 = off)
 1 ddmult     multiplicador de riesgo mientras DD > ddthr
 2 rat_m      trinquete: cuando MFE >= rat_m ATR_entrada, el trailing pasa a rat_k (0 = off)
 3 rat_k      multiplicador ATR del trailing tras el trinquete
 4 pyr_at     piramidación: añade cuando el cierre supera la entrada original + pyr_at ATR_entrada (0 = off)
 5 pyr_frac   tamaño del añadido como fracción de las unidades iniciales
 6 fund_s     funding por barra para cortos (coste, fracción del nocional)
 7 ts_bars    stop de tiempo: nº de barras
 8 ts_mfe     ...si el MFE (en ATR_entrada) aún no alcanzó este valor
 9 pyr_n      nº máximo de añadidos
"""
import numpy as np, pandas as pd
from numba import njit
import eng
from eng import Series, ema_nb, atr_nb, rmax_prev, rmin_prev, adx_nb, stats_nb, FEE, SLIP, FUND8H_LONG, TFH


@njit(cache=True)
def engine7(o, h, l, c, atr, le, se, lx, sx, szm, P, X, warm, maxt):
    n = len(c); eqc = np.full(n, np.nan); expo = np.zeros(n)
    tr = np.zeros((maxt, 10)); nt = 0
    k_init = P[0]; k_tr = P[1]; risk = P[2]; mlev = P[3]; fee = P[4]; slip = P[5]; sx_ = P[6]; fund = P[7]
    tp_atr = P[8]; be_atr = P[9]; maxb = int(P[10]); tr_on = P[11]
    ddthr = X[0]; ddmult = X[1]; rat_m = X[2]; rat_k = X[3]; pyr_at = X[4]; pyr_frac = X[5]; fund_s = X[6]
    ts_bars = int(X[7]); ts_mfe = X[8]; pyr_n = int(X[9])
    eq = 1.0; pos = 0; units = 0.0; ef = 0.0; ef0 = 0.0; stop = 0.0; ext = 0.0; eqb = 1.0; ei = 0; szf = 0.0; sd = 0.0
    atr_e = 0.0; tp = 0.0; trailing = True; units0 = 0.0; nadd = 0; peak = 1.0
    for i in range(n):
        if i < warm:
            eqc[i] = eq; continue
        if pos != 0:
            ex = False; fill = 0.0; rs_ = 1
            if pos == 1 and o[i] <= stop:
                fill = o[i] * (1 - slip - sx_); ex = True; rs_ = 0
            elif pos == -1 and o[i] >= stop:
                fill = o[i] * (1 + slip + sx_); ex = True; rs_ = 0
            elif pos == 1 and tp > 0 and i > ei and c[i - 1] >= tp:
                fill = o[i] * (1 - slip); ex = True; rs_ = 3
            elif pos == -1 and tp > 0 and i > ei and c[i - 1] <= tp:
                fill = o[i] * (1 + slip); ex = True; rs_ = 3
            elif (pos == 1 and lx[i - 1]) or (pos == -1 and sx[i - 1]):
                fill = o[i] * (1 - slip) if pos == 1 else o[i] * (1 + slip); ex = True; rs_ = 1
            elif maxb > 0 and (i - ei) >= maxb:
                fill = o[i] * (1 - slip) if pos == 1 else o[i] * (1 + slip); ex = True; rs_ = 4
            elif ts_bars > 0 and (i - ei) >= ts_bars and ((ext - ef0) if pos == 1 else (ef0 - ext)) < ts_mfe * atr_e:
                fill = o[i] * (1 - slip) if pos == 1 else o[i] * (1 + slip); ex = True; rs_ = 5
            if ex:
                pnl = pos * units * (fill - ef); eq = eq + pnl - units * fill * fee
                ra = szf * sd * eqb
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = pos; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = (eq - eqb) / ra if ra > 0 else 0.0; tr[nt, 7] = szf; tr[nt, 8] = rs_; tr[nt, 9] = nadd; nt += 1
                pos = 0; units = 0.0
            elif pyr_at > 0 and nadd < pyr_n and i > ei and pos == 1 and c[i - 1] >= ef0 + pyr_at * atr_e * (nadd + 1) and stop > 0:
                # añadido (solo largos): al abrir i, tras cierre de i-1 por encima del nivel
                fill = o[i] * (1 + slip)
                addu = pyr_frac * units0
                eqm = eq + units * (o[i] - ef)
                if (units + addu) * fill > mlev * eqm:
                    addu = max(0.0, mlev * eqm / fill - units)
                if addu > 0 and eqm > 0:
                    eq = eq - addu * fill * fee
                    ef = (units * ef + addu * fill) / (units + addu); units = units + addu; nadd += 1
        if pos == 0 and not np.isnan(atr[i - 1]) and atr[i - 1] > 0:
            go = 0
            if le[i - 1]: go = 1
            elif se[i - 1]: go = -1
            if go != 0:
                sdv = k_init * atr[i - 1] / o[i]
                rk = risk
                if ddthr > 0 and peak > 0 and (eq / peak - 1.0) < -ddthr: rk = risk * ddmult
                sz = rk * szm[i - 1] / sdv
                if sz > mlev: sz = mlev
                if sz > 0 and eq > 0:
                    pos = go; szf = sz; sd = sdv; eqb = eq; ei = i; nadd = 0
                    ef = o[i] * (1 + slip) if pos == 1 else o[i] * (1 - slip)
                    notional = sz * eq; units = notional / ef; units0 = units; eq = eq - notional * fee
                    stop = ef - pos * k_init * atr[i - 1]; ext = ef; ef0 = ef; atr_e = atr[i - 1]
                    tp = (ef + pos * tp_atr * atr[i - 1]) if tp_atr > 0 else 0.0
                    trailing = (tr_on <= 0)
        if pos != 0:
            hit = False
            if pos == 1 and l[i] <= stop:
                fill = min(stop, o[i]) * (1 - slip - sx_); hit = True
            elif pos == -1 and h[i] >= stop:
                fill = max(stop, o[i]) * (1 + slip + sx_); hit = True
            if hit:
                pnl = pos * units * (fill - ef); eq = eq + pnl - units * fill * fee
                ra = szf * sd * eqb
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = pos; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = (eq - eqb) / ra if ra > 0 else 0.0; tr[nt, 7] = szf; tr[nt, 8] = 0; tr[nt, 9] = nadd; nt += 1
                pos = 0; units = 0.0
        if pos != 0:
            if pos == 1:
                eq -= fund * units * c[i]
                if h[i] > ext: ext = h[i]
                if (not trailing) and (ext - ef0) >= tr_on * atr_e: trailing = True
                if be_atr > 0 and (ext - ef0) >= be_atr * atr_e and ef0 > stop: stop = ef0
                if trailing and not np.isnan(atr[i]):
                    kk = k_tr
                    if rat_m > 0 and (ext - ef0) >= rat_m * atr_e: kk = rat_k
                    ns = ext - kk * atr[i]
                    if ns > stop: stop = ns
            else:
                eq -= fund_s * units * c[i]
                if l[i] < ext: ext = l[i]
                if (not trailing) and (ef0 - ext) >= tr_on * atr_e: trailing = True
                if be_atr > 0 and (ef0 - ext) >= be_atr * atr_e and ef0 < stop: stop = ef0
                if trailing and not np.isnan(atr[i]):
                    kk = k_tr
                    if rat_m > 0 and (ef0 - ext) >= rat_m * atr_e: kk = rat_k
                    ns = ext + kk * atr[i]
                    if ns < stop: stop = ns
            mtm = eq + pos * units * (c[i] - ef); eqc[i] = mtm
            expo[i] = pos * units * c[i] / mtm if mtm > 0 else 0.0
        else:
            eqc[i] = eq
        if eqc[i] > peak: peak = eqc[i]
    if pos != 0:
        fill = c[n - 1] * (1 - slip) if pos == 1 else c[n - 1] * (1 + slip)
        pnl = pos * units * (fill - ef); eq = eq + pnl - units * fill * fee; ra = szf * sd * eqb
        tr[nt, 0] = ei; tr[nt, 1] = n - 1; tr[nt, 2] = pos; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
        tr[nt, 6] = (eq - eqb) / ra if ra > 0 else 0.0; tr[nt, 7] = szf; tr[nt, 8] = 2; tr[nt, 9] = nadd; nt += 1
        eqc[n - 1] = eq
    return eqc, expo, tr[:nt]


XK = ("ddthr", "ddmult", "rat_m", "rat_k", "pyr_at", "pyr_frac", "fund_s", "ts_bars", "ts_mfe", "pyr_n")


def run7(s, sig, k_init, k_trail=None, risk=0.02, mlev=1.0, cost=1.0, tp=0.0, be=0.0, maxb=0, tron=0.0, ext=None, fee=None, slip=None):
    """Igual que Series.run pero con X (palancas extra)."""
    n = s.n; z = np.zeros(n, dtype=np.bool_)
    fe = FEE * cost if fee is None else fee; sl = SLIP[s.a] * cost if slip is None else slip
    fu = FUND8H_LONG * TFH[s.tf] / 8.0 * cost
    P = np.array([k_init, k_init if k_trail is None else k_trail, risk, mlev, fe, sl, sl, fu, tp, be, maxb, tron], dtype=np.float64)
    X = np.zeros(10)
    if ext:
        for k, v in ext.items(): X[XK.index(k)] = v
    if X[9] == 0: X[9] = 1
    if X[6] < 0: X[6] = fu
    szm = sig.get("szm", np.ones(n))
    return engine7(s.o, s.h, s.l, s.c, np.asarray(sig["atr"], dtype=np.float64),
                   np.asarray(sig.get("le", z), dtype=np.bool_), np.asarray(sig.get("se", z), dtype=np.bool_),
                   np.asarray(sig.get("lx", z), dtype=np.bool_), np.asarray(sig.get("sx", z), dtype=np.bool_),
                   np.asarray(szm, dtype=np.float64), P, X, int(sig.get("warm", 250)), n // 2 + 10)
