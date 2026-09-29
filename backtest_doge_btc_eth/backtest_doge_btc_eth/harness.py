"""harness.py - ejecuta una estrategia en los 9 activos/timeframes (+ETC 1h/4h extra) y resume por split."""
import os, json, time
import numpy as np
import pandas as pd
import bt

_TRIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trials_log.csv")

def log_trial(version, params, note=""):
    """Cada configuracion evaluada se registra (control de comparaciones multiples)."""
    new = not os.path.exists(_TRIALS_FILE)
    with open(_TRIALS_FILE, "a") as f:
        if new:
            f.write("ts,version,params,note\n")
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{version},\"{json.dumps(params, sort_keys=True)}\",{note}\n")

MAIN = [(a, tf) for a in bt.ASSETS for tf in bt.TFS]
EXTRA = [("ETC", "1h"), ("ETC", "4h")]

_CACHE = {}
def series(a, tf, oos=False):
    key = (a, tf, oos)
    if key not in _CACHE:
        _CACHE[key] = bt.get_series(a, tf, oos=oos)
    return _CACHE[key]

def run_one(strat_fn, params, a, tf, oos=False, cost_mult=1.0, k_stop=None, risk_frac=0.02, max_lev=1.0):
    df = series(a, tf, oos)
    sig = strat_fn(df, dict(params, tf=tf))
    k = params["k"] if k_stop is None else k_stop
    eq, ex, trd = bt.backtest(df, a, tf, sig, k_stop=k, risk_frac=risk_frac, max_lev=max_lev, cost_mult=cost_mult)
    return df, eq, ex, trd

def _agg_portfolio(eqs, t0, t1):
    """Cartera equiponderada (rebalanceo diario) de las curvas de equity de las series activas en la ventana."""
    rets = []
    for name, eq in eqs.items():
        e = eq.dropna().loc[:t1]
        prev = e.loc[:t0]
        w = e.loc[t0:t1]
        if len(w) < 30:
            continue
        d = w.resample("1D").last().dropna()
        rets.append(d.pct_change().rename(name))
    if not rets:
        return None
    R = pd.concat(rets, axis=1).iloc[1:]
    pr = R.mean(axis=1, skipna=True).dropna()
    eqp = (1 + pr).cumprod()
    days = (pr.index[-1] - pr.index[0]).days
    total = eqp.iloc[-1] - 1
    ann = eqp.iloc[-1] ** (365.25 / days) - 1 if days > 30 else np.nan
    mdd = (eqp / eqp.cummax() - 1).min()
    sh = pr.mean() / pr.std() * np.sqrt(365.25) if pr.std() > 0 else np.nan
    return dict(ret=total, ann=ann, mdd=mdd, sharpe=sh, calmar=ann / abs(mdd) if mdd < 0 else np.nan)

def evaluate(version, strat_fn, params, splits=("TRAIN", "VAL"), extras=True, cost_mult=1.0,
             k_stop=None, risk_frac=0.02, max_lev=1.0, oos=False, note="", log=True):
    if log:
        log_trial(version, dict(params, cost_mult=cost_mult, risk_frac=risk_frac, max_lev=max_lev), note)
    rows, eqs = [], {}
    combos = MAIN + (EXTRA if extras else [])
    for a, tf in combos:
        df, eq, ex, trd = run_one(strat_fn, params, a, tf, oos=oos, cost_mult=cost_mult, k_stop=k_stop,
                                  risk_frac=risk_frac, max_lev=max_lev)
        eqs[(a, tf)] = eq
        for sp in splits:
            if sp == "OOS":
                t0, t1 = bt.oos_window(df)
            else:
                t0, t1 = bt.SPLITS[sp]
            m = bt.metrics(eq, trd, t0, t1, close=df.close)
            if m is None:
                continue
            expo = ex.loc[t0:t1]
            m.update(dict(version=version, asset=a, tf=tf, split=sp, extra=(a, tf) in EXTRA,
                          exposure=float((expo.abs() > 0).mean())))
            rows.append(m)
    res = pd.DataFrame(rows)
    aggs = []
    for sp in splits:
        for grp, cs in (("MAIN9", MAIN), ("ALL", MAIN + EXTRA)):
            if not extras and grp == "ALL":
                continue
            sub = {k: v for k, v in eqs.items() if k in cs}
            t0, t1 = (bt.oos_window(list(sub.values())[0]) if sp == "OOS" else bt.SPLITS[sp])
            p = _agg_portfolio(sub, t0, t1)
            if p:
                p.update(dict(version=version, split=sp, group=grp))
                aggs.append(p)
    return res, pd.DataFrame(aggs), eqs

# ---------------------------------------------------------------- impresion
def fmt_table(res, split, cols=("ret", "ann", "mdd", "sharpe", "pf", "trades", "win", "avg_win", "avg_loss", "expect", "expect_R", "payoff", "bh")):
    r = res[res.split == split].copy()
    r["serie"] = r.asset + " " + r.tf
    r = r.set_index("serie")[list(cols)]
    pct = ["ret", "ann", "mdd", "win", "avg_win", "avg_loss", "expect", "bh"]
    out = r.copy()
    for c in pct:
        if c in out:
            out[c] = (out[c] * 100).round(2)
    for c in ("sharpe", "pf", "expect_R", "payoff"):
        if c in out:
            out[c] = out[c].round(2)
    out["trades"] = out["trades"].astype(int)
    return out

def summary_line(res, aggs, split):
    r = res[(res.split == split) & (~res.extra)]
    a = aggs[(aggs.split == split) & (aggs.group == "MAIN9")]
    a = a.iloc[0] if len(a) else None
    s = (f"{split}: series+ {int((r.ret>0).sum())}/{len(r)} | mediana ret {r.ret.median()*100:.1f}% | mediana Sharpe {r.sharpe.median():.2f} "
         f"| mediana PF {r.pf.replace(np.inf,np.nan).median():.2f} | mediana MDD {r.mdd.median()*100:.1f}% | trades tot {int(r.trades.sum())}")
    if a is not None:
        s += f" || CARTERA 9: ret {a.ret*100:.1f}% ann {a.ann*100:.1f}% Sharpe {a.sharpe:.2f} MDD {a.mdd*100:.1f}%"
    return s
