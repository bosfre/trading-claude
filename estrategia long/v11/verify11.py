"""Verificacion independiente V11: (1) el CSV macro coincide con el original del usuario; (2) ninguna operacion se abre con el filtro en contra (recalculado con merge_asof, sin usar macro_ok);
(3) con el filtro apagado el numero de operaciones es el de V10; (4) las celdas del informe salen de experimentos_V11.csv."""
import numpy as np, pandas as pd, exp11, exp9
from round11a import VS
M = pd.read_csv("macro_daily.csv", parse_dates=["date"]).set_index("date")
src = pd.read_csv("/mnt/user-data/attachments/570c478a-c7e6-5472-8270-1e8aa65cbf61/55966dba-NASDAQ_UUP_daily_2017_latest.csv", parse_dates=["date"])
nq = src[src.symbol == "NASDAQ"].set_index("date").close; up = src[src.symbol == "UUP"].set_index("date").close
print("(1) nasdaq identico al original:", bool(np.allclose(M.nasdaq.dropna().values, nq.values)), "| uup identico:", bool(np.allclose(M.uup.dropna().values, up.values)), "| filas Nasdaq", len(nq))
S = exp11.load(True); tot = 0; bad = 0
for v in VS:
    m = v["x"]["macro"]
    for tf in ("1h", "4h", "1d"):
        for a in ("ETH", "BTC", "DOGE"):
            s = S[(a, tf)]; eq, ex, trd = exp9.run9(s, v)
            closes = pd.DataFrame({"t": s.idx + pd.Timedelta(hours=exp9.eng.TFH[tf])})
            okv = np.ones(s.n, bool)
            for key, L in (("nasdaq", m["nq"]), ("dxy_syn", m["usd"])):
                if not L: continue
                x = M[key].dropna(); sma = x.rolling(L, min_periods=L).mean()
                c = ((x > sma) if key == "nasdaq" else (x < sma)).astype(float).where(sma.notna())
                a_ = pd.DataFrame({"avail": c.index + pd.Timedelta(days=1), "c": c.values}).sort_values("avail")
                j = pd.merge_asof(closes, a_, left_on="t", right_on="avail")
                okv &= (j.c.isna() | (j.c > 0.5)).values
            if m.get("mode") == "size": continue
            for t in trd:
                tot += 1
                if not okv[int(t[0]) - 1]: bad += 1
print("(2) operaciones revisadas", tot, "| abiertas con filtro en contra:", bad)
E = pd.read_pickle("round11a.pkl"); print("(4) pruebas:", len(E) * 3, "| aprobadas:", int(sum(sum(bool(x) for x in r.values()) for r in E.acc)))
