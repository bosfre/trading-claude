"""Utilidades de laboratorio para V7 (diagnóstico de operaciones y comparativas).
Todo el análisis exploratorio usa SOLO DEV (<=2023-12-31). El OOS no se toca hasta la evaluación final."""
import numpy as np, pandas as pd, eng, gen

V3P = dict(N_h=140, L_h=800, A_h=56, kI=5.0, kT=5.0, minN=5, minL=20, minA=10, ent="hh")
V6P = dict(V3P, tp=20, risk=0.05, mlev=2.0)
TFS = ("1h", "4h", "1d")
ASSETS = ("ETH", "BTC", "DOGE")
WINS = ("TRAIN", "VAL", "OOS", "FULL")


def hb(h, tf, mn=2):
    return gen.hb(h, tf, mn)


def run_v(s, p, wins=WINS, cost=1.0):
    return gen.run(s, p, wins=wins, cost=cost)


def trade_table(s, p, trd):
    """Tabla de operaciones con MFE/MAE y características en la barra de señal (i-1)."""
    d, q = gen.gen(s, p)
    c, h, l, o = s.c, s.h, s.l, s.o
    tf = s.tf
    atr = d["atr"]
    N = hb(q["N_h"], tf, q["minN"]); L = hb(q["L_h"], tf, q["minL"])
    em = s.ind("ema", L); hh = s.ind("hh", N)
    atr_f = s.ind("atr", hb(56, tf, 3)); atr_s = s.ind("atr", hb(560, tf, 3))
    vol = s.df.volume.values.astype(float)
    vma = pd.Series(vol).rolling(N).mean().shift(1).values
    # eficiencia de Kaufman sobre N barras
    dc = np.abs(np.diff(c, prepend=c[0]))
    er = np.abs(c - np.r_[np.full(N, np.nan), c[:-N]]) / pd.Series(dc).rolling(N).sum().values
    k = max(1, L // 10)
    slope = (em - np.r_[np.full(k, np.nan), em[:-k]]) / atr
    rows = []
    for t in trd:
        ei, xi, pos = int(t[0]), int(t[1]), int(t[2])
        j = ei - 1
        seg_h = h[ei:xi + 1]; seg_l = l[ei:xi + 1]
        ef = t[3]
        a0 = atr[j]
        mfe = (seg_h.max() - ef) / a0 if pos == 1 else (ef - seg_l.min()) / a0
        mae = (ef - seg_l.min()) / a0 if pos == 1 else (seg_h.max() - ef) / a0
        rows.append(dict(ei=ei, xi=xi, pos=pos, t0=s.idx[ei], t1=s.idx[xi], ret=t[5], R=t[6], size=t[7], reason=int(t[8]),
                         bars=xi - ei, mfe_atr=mfe, mae_atr=mae,
                         ext=(c[j] - em[j]) / atr[j], brk=(c[j] - hh[j]) / atr[j], volr=atr_f[j] / atr_s[j],
                         er=er[j], vrel=vol[j] / vma[j] if vma[j] > 0 else np.nan, slope=slope[j],
                         atrpct=atr[j] / c[j]))
    return pd.DataFrame(rows)


def dev_mask(s, df):
    return df.xi < s.i_va


def stat_line(x):
    if len(x) == 0:
        return dict(n=0)
    r = x["ret"].values
    gp = r[r > 0].sum(); gl = -r[r <= 0].sum()
    return dict(n=len(x), win=(r > 0).mean(), meanR=x["R"].mean(), medR=x["R"].median(), pf=(gp / gl if gl > 0 else np.inf),
                avg_ret=r.mean())
