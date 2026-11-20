"""Motor V10 = motor V8 (solo largos) + 4 palancas nuevas. Con las palancas apagadas reproduce engine8 al bit (test_eng10.py).
Palancas nuevas (vector Y):
 0 st_bars  parada por estancamiento: si pasan >= st_bars barras sin nuevo maximo, el multiplicador del trailing baja a st_k
 1 st_k     multiplicador del trailing en estancamiento (solo si < kT)
 2 cool     enfriamiento: tras una operacion perdedora no se abre otra durante 'cool' barras
 3 fb_bars  ruptura fallida: durante las primeras fb_bars barras, si el cierre cae por debajo del nivel del canal roto - fb_m*ATR, salida en la apertura siguiente
 4 fb_m     margen (en ATR) de la ruptura fallida
 5 anc_c    ancla del trailing = maximo de CIERRES (en vez de maximos intrabarra)
"""
import numpy as np
from numba import njit
from eng import FEE, SLIP, FUND8H_LONG, TFH

@njit(cache=True)
def engine10(o, h, l, c, atr, le, lx, szm, brk, P, Y, warm, maxt):
    n = len(c); eqc = np.full(n, np.nan); expo = np.zeros(n)
    tr = np.zeros((maxt, 10)); nt = 0
    k_init = P[0]; k_tr = P[1]; risk = P[2]; mlev = P[3]; fee = P[4]; slip = P[5]; sx_ = P[6]; fund = P[7]
    tp_atr = P[8]; be_atr = P[9]; maxb = int(P[10]); tr_on = P[11]
    st_bars = int(Y[0]); st_k = Y[1]; cool = int(Y[2]); fb_bars = int(Y[3]); fb_m = Y[4]; anc_c = Y[5] > 0
    eq = 1.0; pos = 0; units = 0.0; ef = 0.0; ef0 = 0.0; stop = 0.0; ext = 0.0; eqb = 1.0; ei = 0; szf = 0.0; sd = 0.0
    atr_e = 0.0; tp = 0.0; trailing = True; last_hi = 0; last_loss = -1000000000; flvl = 0.0; fbx = False
    for i in range(n):
        if i < warm:
            eqc[i] = eq; continue
        if pos != 0:
            ex = False; fill = 0.0; rs_ = 1
            if o[i] <= stop:
                fill = o[i] * (1 - slip - sx_); ex = True; rs_ = 0
            elif tp > 0 and i > ei and c[i - 1] >= tp:
                fill = o[i] * (1 - slip); ex = True; rs_ = 3
            elif fbx:
                fill = o[i] * (1 - slip); ex = True; rs_ = 7
            elif lx[i - 1]:
                fill = o[i] * (1 - slip); ex = True; rs_ = 1
            elif maxb > 0 and (i - ei) >= maxb:
                fill = o[i] * (1 - slip); ex = True; rs_ = 4
            fbx = False
            if ex:
                pnl = units * (fill - ef); eq = eq + pnl - units * fill * fee
                ra = szf * sd * eqb
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = 1; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = (eq - eqb) / ra if ra > 0 else 0.0; tr[nt, 7] = szf; tr[nt, 8] = rs_; tr[nt, 9] = 0; nt += 1
                if eq / eqb - 1.0 < 0: last_loss = i
                pos = 0; units = 0.0
        if pos == 0 and not np.isnan(atr[i - 1]) and atr[i - 1] > 0:
            go = 0
            if le[i - 1]: go = 1
            if go != 0 and cool > 0 and (i - last_loss) < cool: go = 0
            if go != 0:
                epx = o[i]
                sdv = k_init * atr[i - 1] / epx
                sz = risk * szm[i - 1] / sdv
                if sz > mlev: sz = mlev
                if sz > 0 and eq > 0:
                    pos = 1; szf = sz; sd = sdv; eqb = eq; ei = i; fbx = False
                    ef = epx * (1 + slip)
                    notional = sz * eq; units = notional / ef; eq = eq - notional * fee
                    stop = ef - k_init * atr[i - 1]; ext = ef; ef0 = ef; atr_e = atr[i - 1]
                    tp = (ef + tp_atr * atr[i - 1]) if tp_atr > 0 else 0.0
                    trailing = (tr_on <= 0); last_hi = i; flvl = brk[i - 1]
        if pos != 0:
            if l[i] <= stop:
                fill = min(stop, o[i]) * (1 - slip - sx_)
                pnl = units * (fill - ef); eq = eq + pnl - units * fill * fee
                ra = szf * sd * eqb
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = 1; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = (eq - eqb) / ra if ra > 0 else 0.0; tr[nt, 7] = szf; tr[nt, 8] = 0; tr[nt, 9] = 0; nt += 1
                if eq / eqb - 1.0 < 0: last_loss = i
                pos = 0; units = 0.0
        if pos != 0:
            eq -= fund * units * c[i]
            src = c[i] if anc_c else h[i]
            if src > ext:
                ext = src; last_hi = i
            if (not trailing) and (ext - ef0) >= tr_on * atr_e: trailing = True
            if be_atr > 0 and (ext - ef0) >= be_atr * atr_e and ef0 > stop: stop = ef0
            if trailing and not np.isnan(atr[i]):
                kk = k_tr
                if st_bars > 0 and (i - last_hi) >= st_bars and st_k < kk: kk = st_k
                ns = ext - kk * atr[i]
                if ns > stop: stop = ns
            if fb_bars > 0 and (i - ei) < fb_bars and c[i] < flvl - fb_m * atr_e: fbx = True
            mtm = eq + units * (c[i] - ef); eqc[i] = mtm
            expo[i] = units * c[i] / mtm if mtm > 0 else 0.0
        else:
            eqc[i] = eq
    if pos != 0:
        fill = c[n - 1] * (1 - slip)
        pnl = units * (fill - ef); eq = eq + pnl - units * fill * fee; ra = szf * sd * eqb
        tr[nt, 0] = ei; tr[nt, 1] = n - 1; tr[nt, 2] = 1; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
        tr[nt, 6] = (eq - eqb) / ra if ra > 0 else 0.0; tr[nt, 7] = szf; tr[nt, 8] = 2; tr[nt, 9] = 0; nt += 1
        eqc[n - 1] = eq
    return eqc, expo, tr[:nt]

YK = ("st_bars", "st_k", "cool", "fb_bars", "fb_m", "anc_c")

def run10(s, sig, k_init, k_trail=None, risk=0.02, mlev=1.0, cost=1.0, tp=0.0, be=0.0, maxb=0, tron=0.0, y=None, brk=None):
    n = s.n; z = np.zeros(n, dtype=np.bool_)
    fe = FEE * cost; sl = SLIP[s.a] * cost; fu = FUND8H_LONG * TFH[s.tf] / 8.0 * cost
    P = np.array([k_init, k_init if k_trail is None else k_trail, risk, mlev, fe, sl, sl, fu, tp, be, maxb, tron], dtype=np.float64)
    Y = np.zeros(len(YK))
    if y:
        for kk, v in y.items(): Y[YK.index(kk)] = v
    szm = sig.get("szm", np.ones(n))
    b = np.full(n, np.nan) if brk is None else np.asarray(brk, dtype=np.float64)
    return engine10(s.o, s.h, s.l, s.c, np.asarray(sig["atr"], dtype=np.float64), np.asarray(sig.get("le", z), dtype=np.bool_),
                    np.asarray(sig.get("lx", z), dtype=np.bool_), np.asarray(szm, dtype=np.float64), b, P, Y, int(sig.get("warm", 250)), n // 2 + 10)
