"""Sensibilidad al ANCLA de las velas: misma V9, mismos datos, velas 1D (24 desfases de 1 h) y 4H (4 desfases), construidas desde 1H.
No es una busqueda de parametros: mide cuanto del resultado es suerte del limite de vela. Ventana comun 2017-08-17 -> 2026-10-03.
Despues evalua el CONJUNTO de anclas con pesos iguales (sin optimizar): cada ancla con 1/K del capital."""
import exp10, exp9, exp8, data8, numpy as np, pandas as pd, sys
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
S = exp10.load(True)
H = {a: S[(a, "1h")].df for a in ("ETH", "BTC", "DOGE")}
AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}

def build(a, tf, off):
    rule = "24h" if tf == "1d" else "4h"; per = 24 if tf == "1d" else 4
    h = H[a]
    d = h.resample(rule, offset=pd.Timedelta(hours=off), label="left", closed="left").agg(AGG)
    n = h.close.resample(rule, offset=pd.Timedelta(hours=off), label="left", closed="left").count()
    d = d[n >= 0.75 * per].dropna()
    return data8.Series8(a, tf, d)

def run_anchor(tf, off, assets=("ETH", "BTC", "DOGE")):
    for k in [k for k in exp8._REFS if not isinstance(k, str)]: del exp8._REFS[k]   # la cache usa id(): se reutiliza tras liberar series
    ser = {a: build(a, tf, off) for a in assets}
    exp8._REFS[tf] = ser["BTC"] if "BTC" in ser else build("BTC", tf, off)
    out = {}
    for a in assets:
        s = ser[a]; eq, ex, trd = exp9.run9(s, exp9.V8)
        out[a] = (s, eq, ex, trd)
    return out

def daily_equity(s, eq):
    e = pd.Series(eq, index=s.idx).ffill()
    return e.resample("1D").last().dropna()

def dstats(e, t0, t1=None):
    """CAGR/MDD/Calmar con equity de cierre diario en [t0,t1)."""
    e = e[(e.index >= pd.Timestamp(t0)) & ((e.index < pd.Timestamp(t1)) if t1 else True)]
    if len(e) < 30: return None
    r = e.iloc[-1] / e.iloc[0] - 1; yrs = (e.index[-1] - e.index[0]).days / 365.25
    cagr = (1 + r) ** (1 / yrs) - 1 if (yrs > 0.5 and r > -1) else np.nan
    mdd = float((e / e.cummax() - 1).min())
    return dict(ret=r, cagr=cagr, mdd=mdd, calmar=(cagr / abs(mdd) if mdd < 0 else np.nan), yrs=yrs)

WIN = {"COMUN": ("2017-08-17", None), "TRAIN": ("2017-08-17", "2022-01-01"), "VAL": ("2022-01-01", "2024-01-01"), "2024->": ("2024-01-01", None)}
if __name__ == "__main__":
    allrows = []; EQ = {}
    for tf, offs in (("1d", range(0, 24)), ("4h", range(0, 4))):
        for off in offs:
            r = run_anchor(tf, off)
            for a, (s, eq, ex, trd) in r.items():
                de = daily_equity(s, eq); EQ[(a, tf, off)] = de
                m = exp9.wstat(s, eq, ex, trd, "2017-08-17", None)
                allrows.append(dict(a=a, tf=tf, off=off, ret=m["ret"], cagr=m["cagr"], mdd=m["mdd"], calmar=m["calmar"], n=m["n"], win=m["win"], pf=m["pf"], avgR=m["avgR"]))
            sys.stdout.flush()
    T = pd.DataFrame(allrows); T.to_csv("anchor10_resultados.csv", index=False)
    for tf in ("1d", "4h"):
        print(f"\n===== ETH {tf}: V9 con el ancla desplazada (ventana comun) =====")
        x = T[(T.a == "ETH") & (T.tf == tf)].copy()
        for c in ("ret", "cagr", "mdd", "win"): x[c] = (x[c] * 100).round(1)
        print(x[["off", "ret", "cagr", "mdd", "calmar", "n", "win", "pf", "avgR"]].round(2).to_string(index=False))
        for a in ("ETH", "BTC", "DOGE"):
            y = T[(T.a == a) & (T.tf == tf)]
            print(f"{a} {tf}: CAGR min/mediana/max = {y.cagr.min()*100:.1f} / {y.cagr.median()*100:.1f} / {y.cagr.max()*100:.1f} %   Calmar min/med/max = {y.calmar.min():.2f} / {y.calmar.median():.2f} / {y.calmar.max():.2f}   DD peor/mejor = {y.mdd.min()*100:.1f} / {y.mdd.max()*100:.1f} %")
    pd.to_pickle(EQ, "anchor10_eq.pkl")
