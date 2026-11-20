"""Opcion 3 (DIAGNOSTICO, no selecciona reglas): funding medio de las 24 h previas a cada entrada de V10 (ETH, 2024-03-18 -> 2026-10-03) vs resultado."""
import numpy as np, pandas as pd, exp11, exp9
from scipy.stats import spearmanr, mannwhitneyu
f = pd.read_csv("funding_eth.csv"); f["t"] = pd.to_datetime(f.calc_time, unit="ms"); f = f.set_index("t").sort_index().last_funding_rate
S = exp11.load(True); out = []
for tf in exp9.TFS:
    s = S[("ETH", tf)]; eq, ex, trd = exp9.run9(s, exp9.V8)
    for t in trd:
        et = s.idx[int(t[0])]
        if et < f.index.min() + pd.Timedelta(hours=24) or et > f.index.max(): continue
        w = f[(f.index >= et - pd.Timedelta(hours=24)) & (f.index < et)]
        out.append(dict(tf=tf, entrada=et, n_reg=len(w), fund_24h=w.mean() if len(w) >= 4 else np.nan, ret=t[5], R=t[6]))
D = pd.DataFrame(out)
print("operaciones en el periodo del funding:", D.groupby("tf").size().to_dict(), "| sin funding fiable (<4 registros previos):", D[D.fund_24h.isna()].groupby("tf").size().to_dict())
D = D.dropna(subset=["fund_24h"]); D["gana"] = D.ret > 0
res = []
for tf, g in D.groupby("tf"):
    q = g.fund_24h.quantile(0.75); hi = g[g.fund_24h >= q]; lo = g[g.fund_24h < q]
    rho, p = spearmanr(g.fund_24h, g.ret) if len(g) > 5 else (np.nan, np.nan)
    res.append(dict(tf=tf, n=len(g), win_pct=round(g.gana.mean()*100, 1), fund_medio_gana_pct4h=round(g[g.gana].fund_24h.mean()*100, 4), fund_medio_pierde_pct4h=round(g[~g.gana].fund_24h.mean()*100, 4),
                    n_fund_alto=len(hi), win_fund_alto=round(hi.gana.mean()*100, 1), win_resto=round(lo.gana.mean()*100, 1), ret_medio_alto=round(hi.ret.mean()*100, 2), ret_medio_resto=round(lo.ret.mean()*100, 2),
                    spearman_rho=round(rho, 2), p=round(p, 2)))
R = pd.DataFrame(res); pd.set_option("display.width", 250); print(R.to_string(index=False)); R.to_csv("diagnostico_funding_V11.csv", index=False); D.to_csv("funding_por_operacion_V11.csv", index=False)
print("\nfunding global (por 4h): mediana", round(f.median()*100, 4), "% | p90", round(f.quantile(.9)*100, 4), "% | min", round(f.min()*100, 4), "% | max", round(f.max()*100, 4), "%")
