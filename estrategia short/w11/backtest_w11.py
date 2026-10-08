"""
w11 - Backtest reproducible: ETHUSDT SHORT-only en 1H / 4H / 1D (motor compatible con backtest_w4.py de W4/W8/W9).
Uso:  python backtest_w11.py [directorio con ETHUSDT_1h.csv, ETHUSDT_4h.csv, ETHUSDT_1d.csv]

Calibración: este motor reproduce EXACTAMENTE W8 (1D +449,3 %, 4H +403,2 %, 1H +745,6 %) y W9 en 1D (+472,3 %) y 4H.
  En 1H con toma parcial, W9 no cobraba la comisión de salida de la parte parcial; aquí SÍ se cobra (más conservador:
  W10 1H sale +880 % en vez de +887 %).
W10 (reconstruido; no estaba en el repositorio accesible) = W9 + percentil de volatilidad por TF (1D 70 | 4H 75 | 1H 65),
  riesgo 1D 5 % | 4H 4 % | 1H 6 %. Cuadra con las cifras de referencia de W10 (1D +500,3 %, 103 ops, PF 2,20, OOS +76,6 %).
W11 = W10 + (1D y 4H) stop de las entradas por ruptura = 0,70 x stop del pullback + (1H) sin toma parcial, riesgo 5,5 %.
Tramos: TRAIN 2017-08-17..2021-12-31 | VALIDATION 2022..2023 | OOS 2024-01-01..2026-01-10. Costes: 0,05 % + 0,03 % por lado.
Las variantes tp/be/trail_fn/throttle/rwf del motor son pruebas DESCARTADAS (ver W11_resultados.md).
"""
import numpy as np, pandas as pd, bisect, os, pickle

FEE = 0.0005; SLIP = 0.0003; MAXLEV = 2.0
SPLITS = {'TRAIN': ('2017-08-17', '2021-12-31 23:59:59'), 'VALIDATION': ('2022-01-01', '2023-12-31 23:59:59'),
          'OOS': ('2024-01-01', '2026-01-10 23:59:59'), 'IS': ('2017-08-17', '2023-12-31 23:59:59'),
          'TOTAL': ('2017-08-17', '2026-01-10 23:59:59')}
FAC = {'1h': 4, '4h': 1, '1d': 1 / 6}
FILES = {'1h': 'ETHUSDT_1h.csv', '4h': 'ETHUSDT_4h.csv', '1d': 'ETHUSDT_1d.csv'}   # se sobreescribe con el directorio pasado por argumento
RD = lambda x: int(np.floor(x + 0.5))

def load():
    D = {}
    for tf, p in FILES.items():
        D[tf] = pd.read_csv(p, parse_dates=['timestamp']).set_index('timestamp')
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
        self._ema = {}; self._ll = {}; self._vol = {}; self._hh = {}

    def ema(self, base_len):
        n = RD(base_len * self.f)
        if n not in self._ema: self._ema[n] = self.df.close.ewm(span=n, adjust=False).mean().values
        return self._ema[n]

    def ll(self, base_len):
        n = RD(base_len * self.f)
        if n not in self._ll: self._ll[n] = self.df.low.rolling(n).min().shift(1).values
        return self._ll[n]

    def hh(self, base_len):
        n = RD(base_len * self.f)
        if n not in self._hh: self._hh[n] = self.df.high.rolling(n).max().shift(1).values
        return self._hh[n]

    def volthr(self, W, q):
        key = (W, q)
        if key not in self._vol:
            ap = pd.Series(self.atr / self.c); w = RD(W * self.f)
            self._vol[key] = ap.rolling(w, min_periods=w).quantile(q).shift(1).values
        return self._vol[key]

def build_signal(T, cfg):
    """cfg: trend, look, pb (None|int), vol (None|(W,q)), ext (None|float)"""
    c, atr = T.c, T.atr
    nt = RD(cfg.get('trend', 600) * T.f)
    ema = T.ema(cfg.get('trend', 600))
    ok = ~np.isnan(atr)
    ll = T.ll(cfg.get('look', 45))
    brk = (c < ema) & (c < ll) & ok & ~np.isnan(ll)
    s = brk.copy(); brk_arr = brk
    if cfg.get('pb'):
        ef = T.ema(cfg['pb'])
        cross = (c < ef) & (np.roll(c, 1) >= np.roll(ef, 1))
        pbs = cross & (c < ema) & (ef < ema) & ok
        pbs[:nt] = False
        s = s | pbs
    s[:nt] = False
    if cfg.get('vol'):
        W, q = cfg['vol']
        thr = T.volthr(W, q)
        ap = T.atr / T.c
        s = s & ~(ap > thr)
    if cfg.get('ext'):
        s = s & (((ema - c) / atr) <= cfg['ext'])
    return s

def bounds(T, seg):
    a, b = SPLITS[seg]
    return T.idx.searchsorted(pd.Timestamp(a)), T.idx.searchsorted(pd.Timestamp(b), side='right')

def backtest(T, sig, i0, i1, m=3.0, risk=0.04, minit=None, tp=None, be_after_tp=False, trail_fn=None, throttle=None, rw=None, marr=None):
    """tp = (pct, mult_atr) toma parcial. minit = multiplicador del stop inicial (por defecto m).
    trail_fn(k, e, lo, er, a0, m) -> multiplicador de trailing (opcional)."""
    o, h, l, c, atr = T.o, T.h, T.l, T.c, T.atr
    sidx = np.flatnonzero(sig).tolist(); n = i1 - i0
    eq_bar = np.ones(n); eq = 1.0; trades = []; i = i0; last = i0
    peak = 1.0
    m0 = m
    while i < i1 - 1:
        p = bisect.bisect_left(sidx, i)
        if p >= len(sidx): break
        j = sidx[p]; e = j + 1
        if e >= i1: break
        eq_bar[last - i0:e - i0] = eq
        m = m0 if marr is None else marr[j]
        mi = m if minit is None else minit
        er = o[e]; entry = er * (1 - SLIP); a0 = atr[j]
        stp = c[j] + mi * a0; dist = mi * a0 / c[j]
        rk = risk if rw is None else risk * rw[j]
        if throttle is not None and eq < peak * (1 - throttle[0]): rk = rk * throttle[1]
        notional = min(MAXLEV * eq, rk * eq / dist); qty = notional / entry; fee_in = FEE * notional
        qrem = qty; realized = 0.0; fee_open = fee_in
        tpl = None; tpq = 0.0
        if tp is not None and tp[0] > 0:
            tpl = c[j] - tp[1] * a0; tpq = qty * tp[0] / 100.0
        lo = er; k = e; mfe = 0.0; partial = False
        while True:
            ok_ = o[k]
            if ok_ >= stp: xr = ok_; why = 'gap'; break
            if h[k] >= stp: xr = stp; why = 'stop'; break
            if tpl is not None and not partial:
                if o[k] <= tpl: px = o[k]
                elif l[k] <= tpl: px = tpl
                else: px = None
                if px is not None:
                    xf_p = px * (1 + SLIP)
                    realized += tpq * (entry - xf_p) - FEE * tpq * xf_p
                    qrem -= tpq; partial = True
                    if be_after_tp and entry < stp: stp = entry
            if k == i1 - 1: xr = c[k]; why = 'eos'; break
            if l[k] < lo: lo = l[k]
            mm = m if trail_fn is None else trail_fn(k, e, lo, er, a0, m)
            ns = lo + mm * atr[k]
            if ns < stp: stp = ns
            eq_bar[k - i0] = eq + realized - fee_open + qrem * (entry - c[k])
            k += 1
        xf = xr * (1 + SLIP)
        pnl = realized + qrem * (entry - xf) - fee_open - FEE * qrem * xf
        en = eq + pnl; eq_bar[k - i0] = en
        trades.append((e, k, pnl, pnl / eq, why, k - e + 1, (er - lo) / a0))
        eq = en; last = k + 1; i = k
        if eq > peak: peak = eq
    if last - i0 < n: eq_bar[last - i0:] = eq
    return eq_bar, pd.DataFrame(trades, columns=['ei', 'xi', 'pnl', 'ret', 'why', 'bars', 'mfe'])

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

def run_cfg(T, cfg, risk, segs=SEGS):
    s = build_signal(T, cfg); i0f, i1f = bounds(T, 'TOTAL')
    rw, marr = aux(T, cfg)
    eq, tr = backtest(T, s, i0f, i1f, m=cfg['m'], risk=risk, rw=rw, marr=marr, minit=cfg.get('minit'), tp=cfg.get('tp'),
                      be_after_tp=cfg.get('be', False), trail_fn=cfg.get('trail_fn'), throttle=cfg.get('throttle'))
    out = {seg: seg_metrics(T, eq, tr, i0f, seg) for seg in segs}
    return out, eq, tr

def yearly(T, eq):
    i0f, _ = bounds(T, 'TOTAL')
    s = pd.Series(eq, index=T.idx[i0f:i0f + len(eq)])
    ye = s.resample('YE').last(); prev = ye.shift(1).fillna(1.0)
    return (ye / prev - 1) * 100


def aux(T, cfg):
    """Pesos de riesgo y multiplicador por tipo de entrada."""
    c, atr = T.c, T.atr; ema = T.ema(cfg.get('trend', 600)); rw = None; marr = None
    if cfg.get('rwf'):
        e1, p = cfg['rwf']; ext = np.maximum((ema - c) / atr, 1e-9)
        rw = np.minimum(1.0, (e1 / ext) ** p); rw = np.where(np.isnan(rw), 1.0, rw)
    if cfg.get('ms'):
        ll = T.ll(cfg.get('look', 45)); brk = (c < ema) & (c < ll)
        marr = np.where(brk, cfg['ms'][0], cfg['ms'][1])
    return rw, marr


# ---------------------------------------------------------------- configuraciones
M0 = {'1d': 2.0, '4h': 3.0, '1h': 3.0}          # multiplicador del stop del pullback (w8)
RHO = 0.70                                       # stop ruptura / stop pullback en 1D y 4H (w11)
W10 = {'1d': dict(trend=600, look=45, pb=55, vol=(750, .70), m=2.0),
       '4h': dict(trend=600, look=45, pb=40, vol=(750, .75), m=3.0),
       '1h': dict(trend=600, look=45, pb=40, vol=(750, .65), m=3.0, ext=9, tp=(25, 1.5))}
W11 = {'1d': dict(W10['1d'], ms=(round(M0['1d'] * RHO, 3), M0['1d'])),
       '4h': dict(W10['4h'], ms=(round(M0['4h'] * RHO, 3), M0['4h'])),
       '1h': dict(trend=600, look=45, pb=40, vol=(750, .65), m=3.0, ext=9)}
RISK10 = {'1d': .05, '4h': .04, '1h': .06}
RISK11 = {'1d': .05, '4h': .04, '1h': .055}

if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    for k in FILES: FILES[k] = os.path.join(d, os.path.basename(FILES[k]))
    D = load(); TS = {tf: TF(D[tf], tf) for tf in D}
    rows = []
    for name, cfgs, rks in (('W10', W10, RISK10), ('W11', W11, RISK11)):
        for tf in ('1d', '4h', '1h'):
            out, eq, tr = run_cfg(TS[tf], cfgs[tf], rks[tf])
            for seg in SEGS:
                r = out[seg]; r.update(ver=name, tf=tf, riesgo=rks[tf] * 100, seg=seg); rows.append(r)
    pd.set_option('display.width', 220)
    print(pd.DataFrame(rows)[['tf', 'ver', 'riesgo', 'seg', 'ret', 'dd', 'pf', 'wr', 'n', 'apt', 'cagr']].round(2).to_string(index=False))
