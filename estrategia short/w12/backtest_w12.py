"""
w12 - Motor de backtest ETHUSDT SHORT-only en 1H / 4H / 1D. Es el motor de backtest_w11.py (reproduce W8/W10/W11) con:
  - costes parametrizables: set_costs(fee, slip, size)  size='entry' (motor antiguo: cantidad = nominal/entrada)
                                                        size='close' (TradingView: cantidad = nominal/cierre de la senal)
  - datos extendidos hasta nov-2026: load(d, ext=True) concatena Binance + csvs/ext2026/ (ver build_ext_data.py)
  - tramo HOLDOUT26 (2026-01-07 -> fin): W10/W11 se disenaron con datos hasta 2026-01-06, asi que es un test fuera de muestra
  - ganchos para W12: cooldown tras perdida, filtro de eficiencia (ER, lateralidad), filtro de pendiente de la EMA de regimen
Uso: python backtest_w12.py [carpeta csvs] [--fee 0.0006] [--slip 0.0006]   -> calibracion contra W11 + W10/W11 con costes de TradingView
"""
import numpy as np, pandas as pd, bisect, os, sys

FEE = 0.0005; SLIP = 0.0003; SIZE = 'entry'; MAXLEV = 2.0
SPLITS = {'TRAIN': ('2017-08-17', '2021-12-31 23:59:59'), 'VALIDATION': ('2022-01-01', '2023-12-31 23:59:59'),
          'OOS': ('2024-01-01', '2026-01-10 23:59:59'), 'IS': ('2017-08-17', '2023-12-31 23:59:59'),
          'TOTAL': ('2017-08-17', '2026-01-10 23:59:59'), 'HOLDOUT26': ('2026-01-07', '2030-01-01'),
          'ALL': ('2017-08-17', '2030-01-01')}
FAC = {'1h': 4, '4h': 1, '1d': 1 / 6}
RD = lambda x: int(np.floor(x + 0.5))


def cli_costs():
    """--fee y --slip (fraccion por lado). Por defecto las condiciones de TradingView del usuario: 0,06 % + 0,06 %."""
    g = lambda k, dflt: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else dflt
    return g('--fee', 0.0006), g('--slip', 0.0006)


def cli_dir(default):
    return sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else default


def set_costs(fee, slip, size='entry'):
    global FEE, SLIP, SIZE
    FEE, SLIP, SIZE = fee, slip, size


def load(d, ext=False):
    D = {}
    for tf in ('1h', '4h', '1d'):
        df = pd.read_csv(f'{d}/ETHUSDT_{tf}.csv', parse_dates=['timestamp']).set_index('timestamp')
        if ext:
            x = pd.read_csv(f'{d}/ext2026/ETHUSD_{tf}_ext2026.csv', parse_dates=['timestamp']).set_index('timestamp')
            df = pd.concat([df[df.index < x.index[0]], x])
        D[tf] = df
    return D


def atr_rma(h, l, c, n):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    a = np.full(len(tr), np.nan); a[n - 1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i - 1] * (n - 1) + tr[i]) / n
    return a


class TF:
    """Datos y series cacheadas de una temporalidad."""
    def __init__(self, df, tf):
        self.df = df; self.tf = tf; self.f = FAC[tf]; f = self.f
        self.o, self.h, self.l, self.c = [df[k].values.astype(float) for k in ('open', 'high', 'low', 'close')]
        self.idx = df.index
        na = max(RD(14 * f), 14)
        self.atr = atr_rma(self.h, self.l, self.c, na) * np.sqrt(f)
        self._ema = {}; self._ll = {}; self._vol = {}; self._er = {}

    def ema(self, base_len):
        n = RD(base_len * self.f)
        if n not in self._ema: self._ema[n] = self.df.close.ewm(span=n, adjust=False).mean().values
        return self._ema[n]

    def ll(self, base_len):
        n = RD(base_len * self.f)
        if n not in self._ll: self._ll[n] = self.df.low.rolling(n).min().shift(1).values
        return self._ll[n]

    def volthr(self, W, q):
        key = (W, q)
        if key not in self._vol:
            ap = pd.Series(self.atr / self.c); w = RD(W * self.f)
            self._vol[key] = ap.rolling(w, min_periods=w).quantile(q).shift(1).values
        return self._vol[key]

    def er(self, base_len):
        """Ratio de eficiencia de Kaufman: |cambio neto| / recorrido total en n barras (bajo = lateral)."""
        n = RD(base_len * self.f)
        if n not in self._er:
            c = self.df.close
            self._er[n] = ((c - c.shift(n)).abs() / c.diff().abs().rolling(n).sum()).values
        return self._er[n]

    def slope(self, trend_len, base_len):
        """Variacion relativa de la EMA de regimen en n barras (negativa = cayendo)."""
        e = pd.Series(self.ema(trend_len)); n = RD(base_len * self.f)
        return ((e - e.shift(n)) / e).values


def build_signal(T, cfg):
    """cfg: trend, look, pb (None|int), vol (None|(W,q)), ext (None|float), er (None|(n,thr)), slope (None|(n,thr))"""
    c, atr = T.c, T.atr
    nt = RD(cfg.get('trend', 600) * T.f)
    ema = T.ema(cfg.get('trend', 600))
    ok = ~np.isnan(atr)
    ll = T.ll(cfg.get('look', 45))
    brk = (c < ema) & (c < ll) & ok & ~np.isnan(ll)
    s = brk.copy()
    if cfg.get('pb'):
        ef = T.ema(cfg['pb'])
        cross = (c < ef) & (np.roll(c, 1) >= np.roll(ef, 1))
        pbs = cross & (c < ema) & (ef < ema) & ok
        pbs[:nt] = False
        s = s | pbs
    s[:nt] = False
    if cfg.get('vol'):
        W, q = cfg['vol']
        s = s & ~((T.atr / T.c) > T.volthr(W, q))
    if cfg.get('ext'):
        s = s & (((ema - c) / atr) <= cfg['ext'])
    if cfg.get('er'):
        n, thr = cfg['er']; s = s & (T.er(n) >= thr)
    if cfg.get('slope'):
        n, thr = cfg['slope']; s = s & (T.slope(cfg.get('trend', 600), n) <= -thr)
    return s


def bounds(T, seg):
    a, b = SPLITS[seg]
    return T.idx.searchsorted(pd.Timestamp(a)), T.idx.searchsorted(pd.Timestamp(b), side='right')


def backtest(T, sig, i0, i1, m=3.0, risk=0.04, marr=None, tp=None, cool=0, cool_k=1):
    """marr[j]: multiplicador del stop segun el tipo de entrada (W11). tp=(pct, mult_atr): toma parcial.
    cool: barras (de esta TF) sin nuevas entradas tras una perdida; cool_k: perdidas seguidas necesarias para activarlo."""
    o, h, l, c, atr = T.o, T.h, T.l, T.c, T.atr
    sidx = np.flatnonzero(sig).tolist(); n = i1 - i0
    eq_bar = np.ones(n); eq = 1.0; trades = []; i = i0; last = i0; losses = 0
    while i < i1 - 1:
        p = bisect.bisect_left(sidx, i)
        if p >= len(sidx): break
        j = sidx[p]; e = j + 1
        if e >= i1: break
        eq_bar[last - i0:e - i0] = eq
        mi = m if marr is None else marr[j]
        er = o[e]; entry = er * (1 - SLIP); a0 = atr[j]
        stp = c[j] + mi * a0; dist = mi * a0 / c[j]
        notional = min(MAXLEV * eq, risk * eq / dist)
        if SIZE == 'close': qty = notional / c[j]; fee_in = FEE * qty * entry
        else: qty = notional / entry; fee_in = FEE * notional
        qrem = qty; realized = 0.0; tpl = None; tpq = 0.0
        if tp is not None and tp[0] > 0:
            tpl = c[j] - tp[1] * a0; tpq = qty * tp[0] / 100.0
        lo = er; k = e; partial = False
        while True:
            ok_ = o[k]
            if ok_ >= stp: xr = ok_; why = 'gap'; break
            if h[k] >= stp: xr = stp; why = 'stop'; break
            if tpl is not None and not partial:
                px = o[k] if o[k] <= tpl else (tpl if l[k] <= tpl else None)
                if px is not None:
                    xf_p = px * (1 + SLIP)
                    realized += tpq * (entry - xf_p) - FEE * tpq * xf_p
                    qrem -= tpq; partial = True
            if k == i1 - 1: xr = c[k]; why = 'eos'; break
            if l[k] < lo: lo = l[k]
            ns = lo + mi * atr[k]
            if ns < stp: stp = ns
            eq_bar[k - i0] = eq + realized - fee_in + qrem * (entry - c[k])
            k += 1
        xf = xr * (1 + SLIP)
        pnl = realized + qrem * (entry - xf) - fee_in - FEE * qrem * xf
        en = eq + pnl; eq_bar[k - i0] = en
        trades.append((e, k, pnl, pnl / eq, why, k - e + 1))
        eq = en; last = k + 1; i = k
        losses = losses + 1 if pnl < 0 else 0
        if cool and losses >= cool_k: i = k + cool; losses = 0
    if last - i0 < n: eq_bar[last - i0:] = eq
    return eq_bar, pd.DataFrame(trades, columns=['ei', 'xi', 'pnl', 'ret', 'why', 'bars'])


def seg_metrics(T, eq, T_, i0f, seg):
    i0, i1 = bounds(T, seg); a = i0 - i0f; b = i1 - i0f
    start = eq[a - 1] if a > 0 else 1.0; sub = eq[a:b] / start
    ret = sub[-1] - 1
    dd = (sub / np.maximum.accumulate(np.concatenate([[1.0], sub]))[1:] - 1).min()
    t = T_[(T_.xi >= i0) & (T_.xi < i1)]
    w = t.pnl > 0; gl = -t.pnl[~w].sum()
    yrs = (T.idx[min(i1, len(T.idx)) - 1] - T.idx[i0]).days / 365.25
    cagr = ((1 + ret) ** (1 / yrs) - 1) * 100 if yrs > 0 and ret > -1 else np.nan
    return dict(ret=ret * 100, dd=dd * 100, pf=(t.pnl[w].sum() / gl if gl > 0 else np.nan),
                wr=(w.mean() * 100 if len(t) else np.nan), n=len(t),
                apt=(t.ret.mean() * 100 if len(t) else np.nan), cagr=cagr)


SEGS = ['TRAIN', 'VALIDATION', 'OOS', 'TOTAL']


def marr_for(T, cfg):
    """Multiplicador por tipo de entrada: cfg['ms'] = (mult ruptura, mult pullback)."""
    if not cfg.get('ms'): return None
    ema = T.ema(cfg.get('trend', 600)); ll = T.ll(cfg.get('look', 45))
    return np.where((T.c < ema) & (T.c < ll), cfg['ms'][0], cfg['ms'][1])


def run_cfg(T, cfg, risk, segs=SEGS, whole='TOTAL'):
    s = build_signal(T, cfg); i0f, i1f = bounds(T, whole)
    eq, tr = backtest(T, s, i0f, i1f, m=cfg['m'], risk=risk, marr=marr_for(T, cfg), tp=cfg.get('tp'),
                      cool=cfg.get('cool', 0), cool_k=cfg.get('cool_k', 1))
    return {seg: seg_metrics(T, eq, tr, i0f, seg) for seg in segs}, eq, tr


def yearly(T, eq, whole='TOTAL'):
    i0f, _ = bounds(T, whole)
    s = pd.Series(eq, index=T.idx[i0f:i0f + len(eq)])
    ye = s.resample('YE').last(); prev = ye.shift(1).fillna(1.0)
    return (ye / prev - 1) * 100


# ---------------------------------------------------------------- configuraciones (iguales a backtest_w11.py)
M0 = {'1d': 2.0, '4h': 3.0, '1h': 3.0}
RHO = 0.70
W10 = {'1d': dict(trend=600, look=45, pb=55, vol=(750, .70), m=2.0),
       '4h': dict(trend=600, look=45, pb=40, vol=(750, .75), m=3.0),
       '1h': dict(trend=600, look=45, pb=40, vol=(750, .65), m=3.0, ext=9, tp=(25, 1.5))}
W11 = {'1d': dict(W10['1d'], ms=(round(M0['1d'] * RHO, 3), M0['1d'])),
       '4h': dict(W10['4h'], ms=(round(M0['4h'] * RHO, 3), M0['4h'])),
       '1h': dict(trend=600, look=45, pb=40, vol=(750, .65), m=3.0, ext=9)}
RISK10 = {'1d': .05, '4h': .04, '1h': .06}
RISK11 = {'1d': .05, '4h': .04, '1h': .055}
BASE = (('W10', W10, RISK10), ('W11', W11, RISK11))


def table(D, cfgs_risks, segs, whole, label):
    TS = {tf: TF(D[tf], tf) for tf in D}; rows = []
    for name, cfgs, rks in cfgs_risks:
        for tf in ('1d', '4h', '1h'):
            out, eq, tr = run_cfg(TS[tf], cfgs[tf], rks[tf], segs, whole)
            for seg in segs:
                r = dict(out[seg]); r.update(ver=name, tf=tf, riesgo=rks[tf] * 100, seg=seg, costes=label); rows.append(r)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    d = cli_dir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'csvs'))
    fee, slip = cli_costs(); label = f'slip{slip * 100:g}'
    pd.set_option('display.width', 220); cols = ['tf', 'ver', 'riesgo', 'seg', 'ret', 'dd', 'pf', 'wr', 'n', 'apt', 'cagr']
    print('=== 1) CALIBRACION: costes antiguos (0,05 % + 0,03 %), datos Binance hasta 2026-01-06; debe coincidir con W11_resultados.md ===')
    set_costs(0.0005, 0.0003, 'entry')
    print(table(load(d), BASE, SEGS, 'TOTAL', 'old')[cols].round(2).to_string(index=False))
    print(f'\n=== 2) W10/W11 con condiciones de TradingView (comision {fee*100:g} %, slippage {slip*100:g} %, cantidad al cierre), datos extendidos; HOLDOUT26 = test limpio ===')
    set_costs(fee, slip, 'close')
    R = table(load(d, ext=True), BASE, SEGS + ['HOLDOUT26', 'ALL'], 'ALL', 'tv')
    print(R[cols].round(2).to_string(index=False))
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados'), exist_ok=True)
    R.round(4).to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados', f'baseline_W10_W11_tv_{label}.csv'), index=False)
