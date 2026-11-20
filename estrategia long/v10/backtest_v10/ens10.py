import pandas as pd, numpy as np
import anchor10 as A
EQ = pd.read_pickle("anchor10_eq.pkl")
OFFS = {"1d": list(range(24)), "4h": [0, 1, 2, 3]}
ENS = {"1d K=4": ("1d", [0, 6, 12, 18]), "1d K=24": ("1d", list(range(24))), "4h K=4": ("4h", [0, 1, 2, 3])}
WIN = {"COMUN 2017-08->2026-10": ("2017-08-17", None), "TRAIN 2017-08->2021": ("2017-08-17", "2022-01-01"), "VAL 2022-23": ("2022-01-01", "2024-01-01"),
       "DEV 2017-08->2023": ("2017-08-17", "2024-01-01"), "2024->2026-10": ("2024-01-01", None)}
def ensemble(a, tf, offs):
    df = pd.concat([EQ[(a, tf, o)] for o in offs], axis=1).sort_index().ffill().bfill()
    return df.mean(axis=1)
rows = []
for name, (tf, offs) in ENS.items():
    for a in ("ETH", "BTC", "DOGE"):
        e_ens = ensemble(a, tf, offs)
        for wn, (t0, t1) in WIN.items():
            singles = [A.dstats(EQ[(a, tf, o)], t0, t1) for o in OFFS[tf]]
            singles = [s for s in singles if s]
            if not singles: continue
            m_ens = A.dstats(e_ens, t0, t1); m0 = A.dstats(EQ[(a, tf, 0)], t0, t1)
            avg = {k: float(np.nanmean([s[k] for s in singles])) for k in ("cagr", "mdd", "calmar")}
            med = {k: float(np.nanmedian([s[k] for s in singles])) for k in ("cagr", "mdd", "calmar")}
            rows.append(dict(ens=name, a=a, ventana=wn, cagr_ens=m_ens["cagr"], mdd_ens=m_ens["mdd"], cal_ens=m_ens["calmar"],
                             cagr_avg=avg["cagr"], mdd_avg=avg["mdd"], cal_avg=avg["calmar"], cagr_med=med["cagr"], cal_med=med["calmar"],
                             cagr_0=m0["cagr"], mdd_0=m0["mdd"], cal_0=m0["calmar"], cagr_min=min(s["cagr"] for s in singles), cagr_max=max(s["cagr"] for s in singles)))
R = pd.DataFrame(rows); R.to_csv("ensamble_anclas_resultados.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
for name in ENS:
    x = R[R.ens == name].copy()
    for c in ("cagr_ens", "mdd_ens", "cagr_avg", "mdd_avg", "cagr_med", "cagr_0", "mdd_0", "cagr_min", "cagr_max"): x[c] = (x[c] * 100).round(1)
    print(f"\n=== Ensamble {name}: ensamble | media de anclas | ancla 0 ===")
    print(x[["a", "ventana", "cagr_ens", "mdd_ens", "cal_ens", "cagr_avg", "mdd_avg", "cal_avg", "cagr_0", "mdd_0", "cal_0"]].round(2).to_string(index=False))
