"""
bt.py - Motor de backtest cuantitativo (BTC/ETH/DOGE [+ETC extra]) con:
  * separacion temporal Train / Validation / OOS con BLOQUEO del OOS por codigo
  * indicadores causales (sin lookahead): senal en el cierre de la barra t, ejecucion en la apertura de t+1
  * costes: comision + spread + slippage (+ slippage extra en stops) + funding en largos
  * sizing por riesgo con tope de apalancamiento, sin piramidar, una posicion por serie
"""
import os, time
import numpy as np
import pandas as pd
from numba import njit

UP = "/mnt/user-data/uploads"

# ---------------------------------------------------------------- split temporal (fijado ANTES de ver resultados)
TRAIN_END = pd.Timestamp("2021-12-31 23:59:59")   # Train:      inicio  -> 2021-12-31
VAL_END   = pd.Timestamp("2023-12-31 23:59:59")   # Validation: 2022-01 -> 2023-12
# OOS final:  2024-01-01 -> fin de datos  (BLOQUEADO durante el desarrollo)
DEV_END = VAL_END

_OOS_UNLOCKED = False
def unlock_oos(reason):
    """Unica via para acceder al OOS. Deja registro auditable."""
    global _OOS_UNLOCKED
    _OOS_UNLOCKED = True
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "oos_access_log.txt"), "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} OOS DESBLOQUEADO: {reason}\n")
    print(f"[!] OOS desbloqueado: {reason}")

# ---------------------------------------------------------------- costes por lado (fracciones del precio)
FEE_SIDE = 0.0006                     # 6 bps comision taker por lado
SLIP_SIDE = {"BTC": 0.0004, "ETH": 0.0006, "DOGE": 0.0010, "ETC": 0.0010}   # spread/2 + slippage por lado
STOP_EXTRA_MULT = 1.0                 # en salidas por stop, slippage adicional = 1x el slippage base
FUNDING_8H_LONG = 0.00005             # 0.005% / 8h solo en largos (supuesto conservador; cortos ni pagan ni cobran)

TF_HOURS = {"15m": 0.25, "1h": 1.0, "4h": 4.0}
BARS_PER_YEAR = {"15m": 365.25 * 96, "1h": 365.25 * 24, "4h": 365.25 * 6}

AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
_FREQ = {"15m": "15min", "1h": "1h", "4h": "4h"}

def _read(name):
    return pd.read_csv(f"{UP}/{name}.csv", parse_dates=["timestamp"]).set_index("timestamp").sort_index()

def get_series(asset, tf, oos=False):
    """Devuelve OHLCV. ETH 1h/4h se derivan del 15m (no hay ficheros nativos). oos=False trunca a DEV_END."""
    if asset == "ETH" and tf in ("1h", "4h"):
        b = _read("ETHUSDT_15m")
        df = b.resample(_FREQ[tf], label="left", closed="left").agg(AGG)
        df = df[b.close.resample(_FREQ[tf]).count() > 0]
    else:
        df = _read(f"{asset}USDT_{tf}")
    if oos:
        if not _OOS_UNLOCKED:
            raise PermissionError("OOS bloqueado. Usa unlock_oos(motivo) solo en la prueba final.")
        return df
    return df.loc[:DEV_END]

# ---------------------------------------------------------------- indicadores causales
def atr_wilder(df, n=14):
    pc = df.close.shift(1)
    tr = pd.concat([df.high - df.low, (df.high - pc).abs(), (df.low - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()

def ema(s, n):
    return s.ewm(span=n, adjust=False, min_periods=n).mean()

# ---------------------------------------------------------------- motor
@njit(cache=True)
def _engine(o, h, l, c, atr, long_entry, short_entry, long_exit, short_exit,
            k_stop, risk_frac, max_lev, fee, slip, stop_extra, fund_bar_long, warmup, max_trades):
    n = len(c)
    eq_curve = np.full(n, np.nan)
    expo = np.zeros(n)                       # exposicion firmada (notional/equity)
    # trades: entry_i, exit_i, dir, entry_fill, exit_fill, net_ret, R, size, reason
    tr = np.zeros((max_trades, 9))
    nt = 0
    eq = 1.0                                 # equity realizada (con posicion abierta: eq_base)
    pos = 0                                  # +1 long, -1 short
    units = 0.0; entry_fill = 0.0; stop = 0.0; extreme = 0.0
    eq_before = 1.0; e_i = 0; size_frac = 0.0; stopdist = 0.0
    for i in range(n):
        if i < warmup:
            eq_curve[i] = eq
            continue
        # ---------- 1) ejecucion en la APERTURA de la barra i de decisiones tomadas al cierre de i-1
        if pos != 0:
            exit_now = False; fill = 0.0; reason = 1
            # a) gap contra el stop en la apertura
            if pos == 1 and o[i] <= stop:
                fill = o[i] * (1 - slip - stop_extra); exit_now = True; reason = 0
            elif pos == -1 and o[i] >= stop:
                fill = o[i] * (1 + slip + stop_extra); exit_now = True; reason = 0
            # b) salida por senal discrecional (cierre anterior) -> apertura actual
            elif (pos == 1 and long_exit[i - 1]) or (pos == -1 and short_exit[i - 1]):
                fill = o[i] * (1 - slip) if pos == 1 else o[i] * (1 + slip)
                exit_now = True; reason = 1
            if exit_now:
                pnl = pos * units * (fill - entry_fill)
                fee_out = units * fill * fee
                eq = eq + pnl - fee_out
                risk_amt = size_frac * stopdist * eq_before
                tr[nt, 0] = e_i; tr[nt, 1] = i; tr[nt, 2] = pos; tr[nt, 3] = entry_fill; tr[nt, 4] = fill
                tr[nt, 5] = eq / eq_before - 1.0
                tr[nt, 6] = (eq - eq_before) / risk_amt if risk_amt > 0 else 0.0
                tr[nt, 7] = size_frac; tr[nt, 8] = reason
                nt += 1
                pos = 0; units = 0.0
        if pos == 0 and not np.isnan(atr[i - 1]) and atr[i - 1] > 0:
            go = 0
            if long_entry[i - 1]:
                go = 1
            elif short_entry[i - 1]:
                go = -1
            if go != 0:
                sd = k_stop * atr[i - 1] / o[i]
                sz = risk_frac / sd
                if sz > max_lev:
                    sz = max_lev
                if sz > 0 and eq > 0:
                    pos = go; size_frac = sz; stopdist = sd; eq_before = eq; e_i = i
                    entry_fill = o[i] * (1 + slip) if pos == 1 else o[i] * (1 - slip)
                    notional = sz * eq
                    units = notional / entry_fill
                    eq = eq - notional * fee
                    stop = entry_fill - pos * k_stop * atr[i - 1]
                    extreme = entry_fill
        # ---------- 2) dentro de la barra i: stop intrabarra (con el stop fijado al cierre anterior)
        if pos != 0:
            hit = False
            if pos == 1 and l[i] <= stop:
                fill = min(stop, o[i]) * (1 - slip - stop_extra); hit = True
            elif pos == -1 and h[i] >= stop:
                fill = max(stop, o[i]) * (1 + slip + stop_extra); hit = True
            if hit:
                pnl = pos * units * (fill - entry_fill)
                fee_out = units * fill * fee
                eq = eq + pnl - fee_out
                risk_amt = size_frac * stopdist * eq_before
                tr[nt, 0] = e_i; tr[nt, 1] = i; tr[nt, 2] = pos; tr[nt, 3] = entry_fill; tr[nt, 4] = fill
                tr[nt, 5] = eq / eq_before - 1.0
                tr[nt, 6] = (eq - eq_before) / risk_amt if risk_amt > 0 else 0.0
                tr[nt, 7] = size_frac; tr[nt, 8] = 0
                nt += 1
                pos = 0; units = 0.0
        # ---------- 3) cierre de barra: funding, trailing stop (aplica desde la barra siguiente), mark-to-market
        if pos != 0:
            if pos == 1:
                eq -= fund_bar_long * units * c[i]
                if h[i] > extreme:
                    extreme = h[i]
                if not np.isnan(atr[i]):
                    ns = extreme - k_stop * atr[i]
                    if ns > stop:
                        stop = ns
            else:
                if l[i] < extreme:
                    extreme = l[i]
                if not np.isnan(atr[i]):
                    ns = extreme + k_stop * atr[i]
                    if ns < stop:
                        stop = ns
            mtm = eq + pos * units * (c[i] - entry_fill)
            eq_curve[i] = mtm
            expo[i] = pos * units * c[i] / mtm if mtm > 0 else 0.0
        else:
            eq_curve[i] = eq
    # cierre forzado al final (sin coste de salida sobredimensionado)
    if pos != 0:
        fill = c[n - 1] * (1 - slip) if pos == 1 else c[n - 1] * (1 + slip)
        pnl = pos * units * (fill - entry_fill)
        eq = eq + pnl - units * fill * fee
        risk_amt = size_frac * stopdist * eq_before
        tr[nt, 0] = e_i; tr[nt, 1] = n - 1; tr[nt, 2] = pos; tr[nt, 3] = entry_fill; tr[nt, 4] = fill
        tr[nt, 5] = eq / eq_before - 1.0
        tr[nt, 6] = (eq - eq_before) / risk_amt if risk_amt > 0 else 0.0
        tr[nt, 7] = size_frac; tr[nt, 8] = 2
        nt += 1
        eq_curve[n - 1] = eq
    return eq_curve, expo, tr[:nt]

def backtest(df, asset, tf, sig, k_stop=3.0, risk_frac=0.02, max_lev=1.0, cost_mult=1.0, warmup=None):
    """sig: dict con 'atr', 'long_entry', 'short_entry', 'long_exit', 'short_exit' (arrays bool alineados con df)."""
    n = len(df)
    z = np.zeros(n, dtype=np.bool_)
    le = np.asarray(sig.get("long_entry", z), dtype=np.bool_)
    se = np.asarray(sig.get("short_entry", z), dtype=np.bool_)
    lx = np.asarray(sig.get("long_exit", z), dtype=np.bool_)
    sx = np.asarray(sig.get("short_exit", z), dtype=np.bool_)
    atr = np.asarray(sig["atr"], dtype=np.float64)
    fund_bar = FUNDING_8H_LONG * TF_HOURS[tf] / 8.0 * cost_mult
    slip = SLIP_SIDE[asset] * cost_mult
    fee = FEE_SIDE * cost_mult
    if warmup is None:
        warmup = int(sig.get("warmup", 250))
    eqc, expo, tr = _engine(df.open.values.astype(np.float64), df.high.values.astype(np.float64),
                            df.low.values.astype(np.float64), df.close.values.astype(np.float64), atr,
                            le, se, lx, sx, float(k_stop), float(risk_frac), float(max_lev),
                            fee, slip, slip * STOP_EXTRA_MULT, fund_bar, int(warmup), int(n // 2 + 10))
    idx = df.index
    eq = pd.Series(eqc, index=idx)
    ex = pd.Series(expo, index=idx)
    cols = ["entry_i", "exit_i", "dir", "entry_px", "exit_px", "net_ret", "R", "size", "reason"]
    trd = pd.DataFrame(tr, columns=cols)
    if len(trd):
        trd["entry_t"] = idx[trd.entry_i.astype(int).values]
        trd["exit_t"] = idx[trd.exit_i.astype(int).values]
        trd["bars"] = trd.exit_i - trd.entry_i
    else:
        trd["entry_t"] = pd.Series(dtype="datetime64[ns]"); trd["exit_t"] = pd.Series(dtype="datetime64[ns]"); trd["bars"] = 0
    return eq, ex, trd

# ---------------------------------------------------------------- metricas
def metrics(eq, trd, t0, t1, close=None):
    """Metricas sobre la ventana [t0, t1]. Base de equity = ultimo valor previo a t0 (o el primero valido)."""
    e = eq.dropna()
    prev = e.loc[:t0]
    base = prev.iloc[-1] if len(prev) else e.iloc[0]
    w = e.loc[t0:t1]
    if len(w) < 2:
        return None
    w = w / base
    total = w.iloc[-1] - 1.0
    days = (w.index[-1] - w.index[0]).total_seconds() / 86400.0
    ann = (w.iloc[-1]) ** (365.25 / days) - 1.0 if days > 30 and w.iloc[-1] > 0 else np.nan
    dd = (w / w.cummax() - 1.0).min()
    d = w.resample("1D").last().dropna()
    dr = d.pct_change().dropna()
    sharpe = dr.mean() / dr.std() * np.sqrt(365.25) if len(dr) > 30 and dr.std() > 0 else np.nan
    t = trd[(trd.exit_t >= t0) & (trd.exit_t <= t1)] if len(trd) else trd
    n = len(t)
    if n:
        wins = t[t.net_ret > 0]; loss = t[t.net_ret <= 0]
        gp, gl = wins.net_ret.sum(), -loss.net_ret.sum()
        pf = gp / gl if gl > 0 else np.inf
        avg_w = wins.net_ret.mean() if len(wins) else 0.0
        avg_l = loss.net_ret.mean() if len(loss) else 0.0
        out = dict(trades=n, win=len(wins) / n, avg_win=avg_w, avg_loss=avg_l, expect=t.net_ret.mean(),
                   expect_R=t.R.mean(), payoff=(avg_w / abs(avg_l)) if avg_l != 0 else np.inf, pf=pf)
    else:
        out = dict(trades=0, win=np.nan, avg_win=np.nan, avg_loss=np.nan, expect=np.nan, expect_R=np.nan, payoff=np.nan, pf=np.nan)
    out.update(ret=total, ann=ann, mdd=dd, sharpe=sharpe, calmar=(ann / abs(dd)) if (dd < 0 and ann == ann) else np.nan)
    if close is not None:
        c = close.loc[t0:t1]
        out["bh"] = c.iloc[-1] / c.iloc[0] - 1.0
    return out

SPLITS = {
    "TRAIN": (pd.Timestamp("1900-01-01"), TRAIN_END),
    "VAL":   (TRAIN_END + pd.Timedelta(seconds=1), VAL_END),
}
def oos_window(df):
    return (VAL_END + pd.Timedelta(seconds=1), df.index[-1])

ASSETS = ["BTC", "ETH", "DOGE"]
TFS = ["15m", "1h", "4h"]
