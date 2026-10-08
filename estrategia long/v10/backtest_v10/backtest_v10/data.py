import pandas as pd, numpy as np, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))      # raiz del repo
C = f"{R}/csvs"; SH = C                                          # BTC/DOGE/ETC (1h, 4h) viven en csvs/
ETHD = f"{HERE}/datos"                                           # ETH 1h/4h/1d completos (2017-08 -> 2026-01-06)
AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
def rd(p): return pd.read_csv(p, parse_dates=["timestamp"]).set_index("timestamp").sort_index()
def rs(b, rule, expect, thr):
    d = b.resample(rule, label="left", closed="left").agg(AGG)
    n = b.close.resample(rule, label="left", closed="left").count()
    return d[n >= thr * expect].dropna()
def load():
    """V10: ETH se lee directamente de los CSV 1h/4h/1d (en V9 se remuestreaba desde 15m, que ya no esta en el repo)."""
    D = {}
    for tf in ("1h", "4h", "1d"):
        d = rd(f"{ETHD}/ETHUSDT_{tf}.csv"); d = d[~d.index.duplicated()]
        D[("ETH", tf)] = d
    for a in ("BTC", "DOGE"):
        h = rd(f"{C}/{a}USDT_1h.csv"); f = rd(f"{C}/{a}USDT_4h.csv")
        D[(a, "1h")] = h; D[(a, "4h")] = f; D[(a, "1d")] = rs(h, "1D", 24, 0.75)
    return D, None
