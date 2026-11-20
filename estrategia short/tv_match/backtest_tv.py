"""
backtest_tv.py - Motor "TV" para ETHUSDT SHORT (W8 / W9), con modelo de costes IDENTICO al de los Pine:
  comision 0,06 % por lado sobre el nominal de cada fill, slippage 0, cantidad calculada con el cierre de la barra de senal,
  entrada en la apertura siguiente, stop intrabarra (gap al open), prioridad al stop si coincide con la toma parcial.
Libreria (no se ejecuta sola): usa run_final.py.
Fee y slippage se pasan a backtest(P, fee, slip, size_at). Modelo antiguo de los informes W4-W9: fee 0.0005, slip 0.0003, size_at="entry".
"""
import sys, numpy as np, pandas as pd

FAC = {'1h': 4, '4h': 1, '1d': 1 / 6}
SPLITS = {'TRAIN': ('2017-08-17', '2021-12-31 23:59:59'), 'VALIDATION': ('2022-01-01', '2023-12-31 23:59:59'),
          'OOS': ('2024-01-01', '2026-01-10 23:59:59'), 'TOTAL': ('2017-08-17', '2026-01-10 23:59:59')}
rd = lambda x: int(np.floor(x + 0.5))

W8 = {'1h': dict(m=3.0, risk=.04, fast=40, ext=0, tp_pct=0),
      '4h': dict(m=3.0, risk=.04, fast=40, ext=0, tp_pct=0),
      '1d': dict(m=2.0, risk=.05, fast=40, ext=0, tp_pct=0)}
W9 = {'1h': dict(m=3.0, risk=.06, fast=40, ext=9, tp_pct=25),
      '4h': dict(m=3.0, risk=.04, fast=40, ext=0, tp_pct=0),
      '1d': dict(m=2.0, risk=.05, fast=55, ext=0, tp_pct=0)}
COMMON = dict(ema=600, look=45, atrn=14, vol=750, volpct=75, tp_mult=1.5, maxlev=2.0)


def atr_rma(h, l, c, n):
    tr = np.empty(len(h)); tr[0] = h[0] - l[0]
    pc = c[:-1]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - pc), abs(l[1:] - pc)))
    a = np.full(len(tr), np.nan); a[n - 1] = tr[:n].mean()
    for i in range(n, len(tr)):
        a[i] = (a[i - 1] * (n - 1) + tr[i]) / n
    return a


def prep(df, tf, cfg):
    cfg = {**COMMON, **cfg}; f = FAC[tf]
    o, h, l, c = [df[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]
    emaLen = rd(cfg['ema'] * f); lookLen = rd(cfg['look'] * f); fastLen = rd(cfg['fast'] * f)
    atrLen = max(rd(cfg['atrn'] * f), 14); volLen = rd(cfg['vol'] * f)
    emaT = df.close.ewm(span=emaLen, adjust=False).mean().values
    emaF = df.close.ewm(span=fastLen, adjust=False).mean().values
    atr = atr_rma(h, l, c, atrLen) * np.sqrt(f)
    prevLow = df.low.rolling(lookLen).min().shift(1).values
    regime = c < emaT
    sigBreak = regime & (c < prevLow)
    cp = np.roll(c, 1); ep = np.roll(emaF, 1)
    sigPull = regime & (emaF < emaT) & (c < emaF) & (cp >= ep)
    atrPct = pd.Series(atr / c)
    thr = atrPct.rolling(volLen, min_periods=volLen).quantile(cfg['volpct'] / 100).shift(1).values
    volOk = ~(atrPct.values > thr)
    idx = np.arange(len(c))
    extOk = np.ones(len(c), bool) if cfg['ext'] <= 0 else ((emaT - c) / atr <= cfg['ext'])
    sig = (idx >= emaLen) & volOk & extOk & ~np.isnan(atr) & ~np.isnan(prevLow) & (sigBreak | sigPull)
    sig[0] = False
    return dict(o=o, h=h, l=l, c=c, atr=atr, sig=sig, idx=df.index, **cfg)


def backtest(P, fee, slip, size_at='close'):
    o, h, l, c, atr, sig = P['o'], P['h'], P['l'], P['c'], P['atr'], P['sig']
    m, risk, maxlev = P['m'], P['risk'], P['maxlev']
    n = len(c); sidx = np.flatnonzero(sig)
    eq = 1.0; eq_bar = np.ones(n); trades = []; i = 0; last = 0
    while True:
        p = np.searchsorted(sidx, i)
        if p >= len(sidx): break
        j = sidx[p]; e = j + 1
        if e >= n: break
        eq_bar[last:e] = eq
        er = o[e]; entry = er * (1 - slip); a0 = atr[j]
        stp = c[j] + m * a0; dist = m * a0 / c[j]
        notional = min(maxlev * eq, risk * eq / dist)
        qty = notional / (c[j] if size_at == 'close' else entry)
        fee_in = fee * qty * entry
        tpq = qty * P['tp_pct'] / 100 if P['tp_pct'] > 0 else 0.0
        tpl = c[j] - P['tp_mult'] * a0
        rem = qty; realized = 0.0; tp_done = False; lo = er; k = e
        while True:
            ok = o[k]
            if ok >= stp: xr = ok; why = 'gap'; break
            if h[k] >= stp: xr = stp; why = 'stop'; break
            if tpq > 0 and not tp_done:
                fx = ok if ok <= tpl else (tpl if l[k] <= tpl else None)
                if fx is not None:
                    xf = fx * (1 + slip)
                    realized += tpq * (entry - xf) - fee * tpq * xf
                    rem -= tpq; tp_done = True
            if k == n - 1: xr = c[k]; why = 'eos'; break
            if l[k] < lo: lo = l[k]
            ns = lo + m * atr[k]
            if ns < stp: stp = ns
            eq_bar[k] = eq - fee_in + realized + rem * (entry - c[k])
            k += 1
        xf = xr * (1 + slip)
        pnl = realized + rem * (entry - xf) - fee_in - fee * rem * xf
        en = eq + pnl; eq_bar[k] = en
        trades.append((e, k, entry, xf, pnl, pnl / eq, why, k - e + 1, tp_done))
        eq = en; last = k + 1; i = k
    if last < n: eq_bar[last:] = eq
    T = pd.DataFrame(trades, columns=['ei', 'xi', 'entry', 'exit', 'pnl', 'ret', 'why', 'bars', 'tp'])
    return eq_bar, T


def seg_metrics(P, eq, T, a_ts, b_ts):
    idx = P['idx']; a = idx.searchsorted(pd.Timestamp(a_ts)); b = idx.searchsorted(pd.Timestamp(b_ts), side='right')
    start = eq[a - 1] if a > 0 else 1.0; sub = eq[a:b] / start
    dd = (sub / np.maximum.accumulate(np.concatenate([[1.0], sub]))[1:] - 1).min()
    t = T[(T.xi >= a) & (T.xi < b)]; w = t.pnl > 0; gl = -t.pnl[~w].sum()
    return dict(ret=(sub[-1] - 1) * 100, dd=dd * 100, pf=(t.pnl[w].sum() / gl if gl > 0 else np.nan),
                wr=(w.mean() * 100 if len(t) else np.nan), n=len(t))
