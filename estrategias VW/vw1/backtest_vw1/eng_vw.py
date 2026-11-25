"""Motor conjunto VW1 = LONG V10 + SHORT W10 con UNA equity y UNA posición neta (como la estrategia Pine VW1).

Cada lado conserva EXACTAMENTE la mecánica de su motor original:
  LONG  (eng10.py / V10): señal al cierre i-1 -> entrada en la apertura de i; stop inicial entrada - k*ATR(i-1); trailing = máx - k*ATR(i);
        TP a +20 ATR evaluado al cierre y ejecutado en la apertura siguiente; stop duro con gap a la apertura; riesgo/ATR con tope de apalancamiento;
        costes: comisión + slippage (el stop paga slippage doble) + funding.
  SHORT (backtest_w4/w11.py / W10): señal al cierre j -> entrada en la apertura j+1; stop = close_j + m*ATR_eq(j); trailing = mín desde entrada + m*ATR_eq(k);
        toma parcial opcional (1H: 25 % a 1,5 ATR_eq); el stop manda sobre el objetivo si coinciden en la barra; comisión + slippage por lado, sin funding.
Reglas del conjunto (iguales a las del Pine VW1):
  * Solo una posición a la vez; con una posición abierta se ignoran las señales del lado contrario (no se invierte).
  * Si coinciden señal LONG y señal SHORT en la misma barra y se está plano, no se opera (conflicto).
  * 'strict' (por defecto): solo se entra con la cuenta plana AL CIERRE de la barra anterior (semántica Pine: la señal se evalúa al cierre y no puede
    haber orden si la posición seguía abierta). strict=0 reproduce el motor de V10 (permite reentrada en la misma apertura tras un TP o un gap).
  * fbL: 1 = el stop del LONG ya vale en la barra de relleno (motor de V10); 0 = no vale (así lo hace el Pine de V10: el strategy.exit se envía al cierre de la barra de relleno).
  * flip (variante opcional, NO es VW1): con una posición abierta, una señal del lado contrario cierra en la apertura siguiente y abre la contraria.
"""
import numpy as np
from numba import njit

# F: 0 enL, 1 enS, 2 strict, 3 fbL, 4 flip
# PL: 0 k_init, 1 k_trail, 2 risk, 3 mlev, 4 tp_atr, 5 fee, 6 slip, 7 stop_extra_slip, 8 funding_por_barra
# PS: 0 mult, 1 risk, 2 mlev, 3 tp_frac (0..1), 4 tp_mult_atr, 5 fee, 6 slip, 7 funding_por_barra
# trades: 0 ei, 1 xi, 2 lado, 3 precio entrada, 4 precio salida, 5 ret (eq_after/eq_before-1), 6 pnl (en equity inicial=1), 7 motivo, 8 eq_before, 9 tamano (nocional/equity)
# motivo: 0 stop, 1 salida a mercado, 2 fin de datos, 3 TP, 8 flip
@njit(cache=True)
def joint(o, h, l, c, atrL, leL, warmL, atrS, sS, PL, PS, F):
    n = len(c)
    eqc = np.ones(n); posa = np.zeros(n, dtype=np.int8)
    tr = np.zeros((n // 2 + 10, 10)); nt = 0
    k_init = PL[0]; k_tr = PL[1]; riskL = PL[2]; mlevL = PL[3]; tp_atr = PL[4]; feeL = PL[5]; slipL = PL[6]; sxL = PL[7]; fundL = PL[8]
    mS = PS[0]; riskS = PS[1]; mlevS = PS[2]; tpf = PS[3]; tpm = PS[4]; feeS = PS[5]; slipS = PS[6]; fundS = PS[7]
    enL = F[0] > 0; enS = F[1] > 0; strict = F[2] > 0; fbL = F[3] > 0; flip = F[4] > 0
    eq = 1.0; pos = 0
    units = 0.0; ef = 0.0; stop = 0.0; ext = 0.0; tp = 0.0
    qrem = 0.0; entry = 0.0; stp = 0.0; lo = 0.0; tpl = 0.0; tpq = 0.0; partial = False
    eqb = 1.0; ei = 0; szf = 0.0
    nconf = 0; ignL = 0; ignS = 0
    for i in range(n):
        pos_prev = pos; flipped = False
        sigL = False; sigS = False
        if i >= 1:
            sigL = enL and i >= warmL and leL[i - 1] and (not np.isnan(atrL[i - 1])) and atrL[i - 1] > 0
            sigS = enS and sS[i - 1] and (not np.isnan(atrS[i - 1])) and atrS[i - 1] > 0
        # ---- (a) salidas del LONG en la apertura: stop con gap, objetivo TP ----
        if pos == 1:
            ex = False; fill = 0.0; rs = 1
            if o[i] <= stop:
                fill = o[i] * (1 - slipL - sxL); ex = True; rs = 0
            elif tp > 0 and i > ei and c[i - 1] >= tp:
                fill = o[i] * (1 - slipL); ex = True; rs = 3
            elif flip and sigS and (not sigL):
                fill = o[i] * (1 - slipL); ex = True; rs = 8
            if ex:
                eq = eq + units * (fill - ef) - units * fill * feeL
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = 1; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = eq - eqb; tr[nt, 7] = rs; tr[nt, 8] = eqb; tr[nt, 9] = szf; nt += 1
                pos = 0; units = 0.0
                if rs == 8: flipped = True
        elif pos == -1 and flip and sigL and (not sigS):
            xf = o[i] * (1 + slipS)
            eq = eq + qrem * (entry - xf) - feeS * qrem * xf
            tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = -1; tr[nt, 3] = entry; tr[nt, 4] = xf; tr[nt, 5] = eq / eqb - 1.0
            tr[nt, 6] = eq - eqb; tr[nt, 7] = 8; tr[nt, 8] = eqb; tr[nt, 9] = szf; nt += 1
            pos = 0; qrem = 0.0; flipped = True
        # ---- (b) entradas (solo plano) ----
        if pos == 0:
            allow = (pos_prev == 0) or (not strict) or flipped
            if allow:
                if sigL and sigS:
                    nconf += 1
                elif sigL:
                    epx = o[i]; sdv = k_init * atrL[i - 1] / epx
                    sz = riskL / sdv
                    if sz > mlevL: sz = mlevL
                    if sz > 0 and eq > 0:
                        pos = 1; szf = sz; eqb = eq; ei = i
                        ef = epx * (1 + slipL)
                        notional = sz * eq; units = notional / ef; eq = eq - notional * feeL
                        stop = ef - k_init * atrL[i - 1]; ext = ef
                        tp = (ef + tp_atr * atrL[i - 1]) if tp_atr > 0 else 0.0
                elif sigS:
                    j = i - 1; a0 = atrS[j]
                    entry = o[i] * (1 - slipS); stp = c[j] + mS * a0; dist = mS * a0 / c[j]
                    notional = min(mlevS * eq, riskS * eq / dist)
                    if notional > 0 and eq > 0:
                        pos = -1; szf = notional / eq; eqb = eq; ei = i
                        qrem = notional / entry; eq = eq - feeS * notional
                        lo = o[i]; partial = False
                        if tpf > 0:
                            tpl = c[j] - tpm * a0; tpq = qrem * tpf
                        else:
                            tpl = 0.0; tpq = 0.0
            else:
                if pos_prev == 1 and sigS and (not flip): ignS += 1
                if pos_prev == -1 and sigL and (not flip): ignL += 1
        if pos != 0 and pos_prev == pos:
            # señales ignoradas por posición contraria (cuenta de barras con señal)
            if pos == 1 and sigS: ignS += 1
            if pos == -1 and sigL: ignL += 1
        # ---- (c)+(d) gestión intrabarra de la posición abierta ----
        if pos == 1:
            if (i > ei or fbL) and l[i] <= stop:
                fill = min(stop, o[i]) * (1 - slipL - sxL)
                eq = eq + units * (fill - ef) - units * fill * feeL
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = 1; tr[nt, 3] = ef; tr[nt, 4] = fill; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = eq - eqb; tr[nt, 7] = 0; tr[nt, 8] = eqb; tr[nt, 9] = szf; nt += 1
                pos = 0; units = 0.0
                eqc[i] = eq
            else:
                eq -= fundL * units * c[i]
                if h[i] > ext: ext = h[i]
                if not np.isnan(atrL[i]):
                    ns = ext - k_tr * atrL[i]
                    if ns > stop: stop = ns
                eqc[i] = eq + units * (c[i] - ef)
        elif pos == -1:
            hit = False; xr = 0.0
            if o[i] >= stp:
                xr = o[i]; hit = True
            elif h[i] >= stp:
                xr = stp; hit = True
            if hit:
                xf = xr * (1 + slipS)
                eq = eq + qrem * (entry - xf) - feeS * qrem * xf
                tr[nt, 0] = ei; tr[nt, 1] = i; tr[nt, 2] = -1; tr[nt, 3] = entry; tr[nt, 4] = xf; tr[nt, 5] = eq / eqb - 1.0
                tr[nt, 6] = eq - eqb; tr[nt, 7] = 0; tr[nt, 8] = eqb; tr[nt, 9] = szf; nt += 1
                pos = 0; qrem = 0.0
                eqc[i] = eq
            else:
                if tpq > 0 and (not partial):
                    px = -1.0
                    if o[i] <= tpl: px = o[i]
                    elif l[i] <= tpl: px = tpl
                    if px > 0:
                        xfp = px * (1 + slipS)
                        eq = eq + tpq * (entry - xfp) - feeS * tpq * xfp
                        qrem -= tpq; partial = True
                eq -= fundS * qrem * c[i]
                if l[i] < lo: lo = l[i]
                ns = lo + mS * atrS[i]
                if ns < stp: stp = ns
                eqc[i] = eq + qrem * (entry - c[i])
        else:
            eqc[i] = eq
        posa[i] = pos
    # ---- fin de datos: cierra lo abierto al cierre de la última barra ----
    if pos != 0:
        if pos == 1:
            fill = c[n - 1] * (1 - slipL)
            eq = eq + units * (fill - ef) - units * fill * feeL
            tr[nt, 0] = ei; tr[nt, 1] = n - 1; tr[nt, 2] = 1; tr[nt, 3] = ef; tr[nt, 4] = fill
        else:
            xf = c[n - 1] * (1 + slipS)
            eq = eq + qrem * (entry - xf) - feeS * qrem * xf
            tr[nt, 0] = ei; tr[nt, 1] = n - 1; tr[nt, 2] = -1; tr[nt, 3] = entry; tr[nt, 4] = xf
        tr[nt, 5] = eq / eqb - 1.0; tr[nt, 6] = eq - eqb; tr[nt, 7] = 2; tr[nt, 8] = eqb; tr[nt, 9] = szf; nt += 1
        eqc[n - 1] = eq
    return eqc, posa, tr[:nt], np.array([nconf, ignL, ignS])


def costs(model, tf, cm=1.0):
    """Devuelve (fee, slip, stop_extra, fund_por_barra) del LONG y (fee, slip, fund) del SHORT para un modelo de costes.
    'orig'  : los de cada motor original (LONG 6 pb + 6 pb slippage, stop con slippage doble, funding 0,005 %/8h; SHORT 5 pb + 3 pb, sin funding).
    'pine'  : comisión 0,08 % por lado y slippage 0 para los dos lados, sin funding (lo que declara el strategy() de VW1)."""
    tfh = {"1h": 1.0, "4h": 4.0, "1d": 24.0}[tf]
    if model == "orig":
        L = (0.0006 * cm, 0.0006 * cm, 0.0006 * cm, 0.00005 * tfh / 8.0 * cm); S = (0.0005 * cm, 0.0003 * cm, 0.0)
    elif model == "pine":
        L = (0.0008 * cm, 0.0, 0.0, 0.0); S = (0.0008 * cm, 0.0, 0.0)
    else:
        raise ValueError(model)
    return L, S
