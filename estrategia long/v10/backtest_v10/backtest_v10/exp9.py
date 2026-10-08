"""Arnés V9. Baseline = V8 (V7 + confirmación BTC>EMA800h). Selección SOLO con TRAIN/VAL/DEV (ETH, BTC, DOGE; 1H/4H/1D).
Holdouts (PRE 1D, ETC, OOSX 2024-01 -> 2026-10-03) se abren por funciones explícitas y quedan en oos_access_log.txt.
Variante v = dict(p=params gen8, ext=palancas eng8, x=extras V9, name, fam)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, json, time, exp8, data8, eng, eng8, lab
from eng import ema_nb, stats_nb
from sigs import hb

B800 = dict(type="btc", mode="filter", L_h=800)
V8 = dict(name="V8", p=dict(xref=B800))
V7 = dict(name="V7")
TFS = ("1h", "4h", "1d"); ASSETS = ("ETH", "BTC", "DOGE"); SEL = ("TRAIN", "VAL", "DEV")
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trials10.jsonl")

def gen9(s, v):
    d, q = exp8.gen8(s, v.get("p", {}))
    x = v.get("x", {}); tf = s.tf
    L = int(q["L_b"]) if q.get("L_b") else hb(q["L_h"], tf, q["minL"])
    em = s.ind("ema", L); atr = d["atr"]
    ext = (s.c - em) / atr
    if "ext_max" in x:
        d["le"] = d["le"] & ~(ext > x["ext_max"])
    if "clv_min" in x:
        rng = s.h - s.l; clv = np.where(rng > 0, (s.c - s.l) / np.where(rng > 0, rng, 1), 0.5)
        d["le"] = d["le"] & (clv >= x["clv_min"])
    if "ext_size" in x:
        sz = np.where(ext > x["ext_size"][0], x["ext_size"][1], 1.0)
        d["szm"] = d.get("szm", np.ones(s.n)) * sz
    lx = d.get("lx", np.zeros(s.n, dtype=bool))
    if "trend_exit" in x:
        lx = lx | (s.c < em - x["trend_exit"] * atr)
    if "btc_exit" in x and s.a != "BTC":
        r = exp8.ref_close(s); Lr = hb(x["btc_exit"], tf, 2)
        er = ema_nb(np.nan_to_num(r, nan=np.nanmedian(r)), Lr)
        off = ~(np.isnan(r) | np.isnan(er) | (r > er))
        lx = lx | off
    d["lx"] = lx
    return d, q

def run9(s, v, cost=1.0):
    d, q = gen9(s, v)
    ext = dict(v.get("ext") or {})
    if q["ent"] == "lvl": ext["entstop"] = 1
    if "ts_h" in ext:
        ext["ts_bars"] = max(1, int(round(ext.pop("ts_h") / eng.TFH[s.tf])))
    return eng8.run8(s, d, q["kI"], q["kT"], risk=q["risk"], mlev=q["mlev"], tp=q["tp"], be=q["be"], tron=q["tron"], ext=ext, cost=cost * v.get("cost", 1.0))

# ---------------- métricas ampliadas ----------------
def widx(s, t0, t1=None):
    i0 = int(s.idx.searchsorted(pd.Timestamp(t0))) if isinstance(t0, str) else int(t0)
    i1 = s.n if t1 is None else (int(s.idx.searchsorted(pd.Timestamp(t1))) if isinstance(t1, str) else int(t1))
    return i0, i1

def wstat(s, eq, ex, trd, t0, t1=None, wn=None):
    """Métricas en [i0,i1). Operaciones = las que SALEN dentro de la ventana."""
    i0, i1 = (s.win(wn) if wn else widx(s, t0, t1))
    if i1 - i0 < 5: return None
    base = eq[i0 - 1] if i0 > 0 else 1.0
    if np.isnan(base) or base <= 0: base = 1.0
    e = eq[i0:i1] / base
    pk = np.maximum.accumulate(np.r_[1.0, e])[1:]; mdd = float((e / pk - 1).min()); ret = float(e[-1] - 1)
    yrs = (s.idx[i1 - 1] - s.idx[i0]).total_seconds() / 86400 / 365.25
    cagr = (1 + ret) ** (1 / yrs) - 1 if (yrs > 0.5 and ret > -1) else np.nan
    tot, mdd2, sh, so, nt, nw, gp, gl = stats_nb(eq, s.dend, i0, i1, trd, len(trd))
    sel = [t for t in trd if i0 <= t[1] < i1]
    out = dict(ret=ret, cagr=cagr, mdd=mdd, yrs=yrs, sharpe=sh, calmar=(cagr / abs(mdd) if (mdd < 0 and cagr == cagr) else np.nan), n=len(sel))
    if sel:
        r = np.array([t[5] for t in sel]); R = np.array([t[6] for t in sel]); bars = np.array([t[1] - t[0] for t in sel]) * eng.TFH[s.tf]
        E = base; pnl = []
        for x in r: pnl.append(E * x); E *= (1 + x)
        pnl = np.array(pnl)
        w = r > 0
        out.update(win=float(w.mean()), pf=float(r[r > 0].sum() / -r[r <= 0].sum()) if (r <= 0).any() and r[r <= 0].sum() < 0 else np.inf,
                   pf_usd=float(pnl[pnl > 0].sum() / -pnl[pnl <= 0].sum()) if (pnl <= 0).any() and pnl[pnl <= 0].sum() < 0 else np.inf,
                   avg_ret=float(r.mean()), med_ret=float(np.median(r)), avgR=float(R.mean()),
                   avg_win=float(r[w].mean()) if w.any() else np.nan, avg_loss=float(r[~w].mean()) if (~w).any() else np.nan,
                   avgR_win=float(R[w].mean()) if w.any() else np.nan, avgR_loss=float(R[~w].mean()) if (~w).any() else np.nan,
                   hours=float(bars.mean()), trades_yr=len(sel) / yrs, expo=float(np.mean(np.abs(ex[i0:i1]) > 0)))
        out["payoff"] = (out["avg_win"] / abs(out["avg_loss"])) if (w.any() and (~w).any()) else np.nan
    return out

def calm(m): return m["calmar"] if (m and m.get("calmar") == m.get("calmar")) else np.nan

# ---------------- evaluación contra V8 ----------------
_BASE = {}
def base_res(S, a, tf, v0=None):
    v0 = v0 or V8; k = (a, tf, id(S), v0["name"])
    if k not in _BASE:
        s = S[(a, tf)]; eq, ex, trd = run9(s, v0)
        _BASE[k] = {w: wstat(s, eq, ex, trd, None, None, w) for w in SEL}
    return _BASE[k]

def eval9(S, v, assets=ASSETS, tfs=TFS, cost=1.0):
    out = {}
    for a in assets:
        for tf in tfs:
            s = S[(a, tf)]; eq, ex, trd = run9(s, v, cost)
            out[(a, tf)] = {w: wstat(s, eq, ex, trd, None, None, w) for w in SEL}
    return out

def deltas9(S, res):
    rows = []
    for (a, tf), r in res.items():
        b = base_res(S, a, tf)
        for w in SEL:
            x, y = r[w], b[w]
            if x is None or y is None: continue
            rows.append(dict(a=a, tf=tf, w=w, cal=calm(x), b_cal=calm(y), mdd=x["mdd"], b_mdd=y["mdd"], cagr=x["cagr"], b_cagr=y["cagr"],
                             n=x["n"], b_n=y["n"], avgR=x.get("avgR", np.nan), b_avgR=y.get("avgR", np.nan), pf=x.get("pf", np.nan), b_pf=y.get("pf", np.nan)))
    D = pd.DataFrame(rows); D["dcal"] = D.cal - D.b_cal; D["dmdd"] = D.mdd - D.b_mdd; D["dcagr"] = D.cagr - D.b_cagr; D["dR"] = D.avgR - D.b_avgR
    return D

def summ9(D):
    out = {}
    def g(a, tf, w, col="dcal"):
        r = D[(D.a == a) & (D.tf == tf) & (D.w == w)]; return float(r[col].iloc[0]) if len(r) else np.nan
    for tf in TFS:
        out[f"E{tf}_tr"] = round(g("ETH", tf, "TRAIN"), 2); out[f"E{tf}_va"] = round(g("ETH", tf, "VAL"), 2); out[f"E{tf}_dev"] = round(g("ETH", tf, "DEV"), 2)
        out[f"B{tf}"] = round(g("BTC", tf, "DEV"), 2); out[f"D{tf}"] = round(g("DOGE", tf, "DEV"), 2)
        out[f"dMDD_{tf}"] = round(g("ETH", tf, "DEV", "dmdd") * 100, 1); out[f"dCAGR_{tf}"] = round(g("ETH", tf, "DEV", "dcagr") * 100, 1)
        out[f"dR_{tf}"] = round(g("ETH", tf, "DEV", "dR"), 3)
    return out

def accept9(sm, tf):
    """Criterio pre-registrado por temporalidad (vs V8): ETH dCalmar>0 en TRAIN y VAL; BTC y DOGE >= 0; dMDD ETH > -1 pp; dR/operación ETH DEV > 0."""
    return bool(sm[f"E{tf}_tr"] > 0 and sm[f"E{tf}_va"] > 0 and sm[f"B{tf}"] >= 0 and sm[f"D{tf}"] >= 0 and sm[f"dMDD_{tf}"] > -1.0 and sm[f"dR_{tf}"] > 0)

def log(v, res, stage="dev"):
    row = dict(t=time.strftime("%Y-%m-%d %H:%M:%S"), stage=stage, name=v.get("name", ""), fam=v.get("fam", ""), p=v.get("p", {}), ext=v.get("ext", {}), x=v.get("x", {}),
               res={f"{a}|{tf}|{w}": ({k: (None if (z is None or z != z) else float(z)) for k, z in m.items() if k in ("ret", "cagr", "mdd", "n", "calmar", "pf", "win", "avgR")} if m else None)
                    for (a, tf), r in res.items() for w, m in r.items()})
    with open(LOG, "a") as f: f.write(json.dumps(row) + "\n")

def trial9(S, v, do_log=True):
    res = eval9(S, v)
    if do_log: log(v, res)
    D = deltas9(S, res); sm = summ9(D); sm["name"] = v.get("name", ""); sm["acc"] = {tf: accept9(sm, tf) for tf in TFS}
    return sm, D, res

def scale_risk(v, m):
    w = json.loads(json.dumps(v)); w.setdefault("p", {}); w["p"]["risk"] = lab.V6P["risk"] * m; return w

def matched_dd9(S, v, a, tf, target_mdd, wn="DEV", lo=0.2, hi=4.0, it=22):
    s = S[(a, tf)]
    for _ in range(it):
        m = (lo + hi) / 2; eq, ex, trd = run9(s, scale_risk(v, m)); st = wstat(s, eq, ex, trd, None, None, wn)
        if st["mdd"] < target_mdd: hi = m
        else: lo = m
    return m, st

def load(ext=True, pre=False, etc=False):
    S = data8.load_all(ext, pre=pre, etc=etc); exp8.set_refs(S); return S
