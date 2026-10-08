"""Arnés V8. Selección SOLO con TRAIN/VAL/DEV (ETH, BTC, DOGE; 1H/4H/1D). PRE/OOS1/OOS2 bloqueados salvo función explícita 'holdout'.
Variante v = dict(p=params de gen8, ext=palancas de eng8, name=..., fam=...). Baseline V7 = dict() (= V6 en Python)."""
import numpy as np, pandas as pd, json, os, time, eng, eng8, gen, lab, data8
from eng import ema_nb
from sigs import hb

eng.SLIP.setdefault("ETC", 0.0008)   # supuesto: ETC algo menos líquido que ETH (8 pb)
SEL = ("TRAIN", "VAL", "DEV")
LOG = "trials8.jsonl"
ASSETS = ("ETH", "BTC", "DOGE"); TFS = ("1h", "4h", "1d")

_REFS = {}
def set_refs(S):
    for tf in TFS: _REFS[tf] = S[("BTC", tf)]
def ref_close(s):
    key = (s.a, s.tf, id(s))
    if key not in _REFS:
        b = _REFS[s.tf]; _REFS[key] = pd.Series(b.c, index=b.idx).reindex(s.idx, method="ffill").values
    return _REFS[key]

def gen8(s, p):
    q = dict(gen.DEF); q.update(lab.V6P); q.update(p)
    tf = s.tf; tfh = eng.TFH[tf]
    N = int(q["N_b"]) if q.get("N_b") else hb(q["N_h"], tf, q["minN"])
    L = int(q["L_b"]) if q.get("L_b") else hb(q["L_h"], tf, q["minL"])
    A = int(q["A_b"]) if q.get("A_b") else hb(q["A_h"], tf, q["minA"])
    sc = q["atr_scale"] if q.get("atr_scale") else np.sqrt(4.0 / tfh)
    atr = s.ind("atr", A) * sc; em = s.ind("ema", L)
    hi = s.ind("hh", N) if q["ent"] in ("hh", "lvl") else s.ind("hc", N)
    d = dict(atr=atr, warm=max(N, L, A) + 5)
    m = q.get("brk_m", 0.0)
    if q["ent"] == "lvl":
        d["le"] = (s.c > em); d["lvl"] = hi + m * atr          # filtro de tendencia + buy-stop en el canal
    else:
        d["le"] = (s.c > hi + m * atr) & (s.c > em)
    xr = q.get("xref")
    if xr and s.a != "BTC":
        r = ref_close(s)
        if xr["type"] == "ratio": r = s.c / r
        Lr = hb(xr["L_h"], tf, 2); er = ema_nb(np.nan_to_num(r, nan=np.nanmedian(r)), Lr)
        okr = np.isnan(r) | np.isnan(er) | (r > er)   # sin dato de referencia -> no filtra
        if xr["mode"] == "filter": d["le"] = d["le"] & okr
        else: d["szm"] = np.where(okr, 1.0, xr.get("w", 0.5))
    if q.get("slope"):
        k = max(1, L // 10); sl = np.r_[np.full(k, np.nan), em[k:] - em[:-k]]; d["le"] = d["le"] & (sl > 0)
    if q.get("xN_b") or q.get("xN_h"):
        xN = int(q["xN_b"]) if q.get("xN_b") else hb(q["xN_h"], tf, 2)
        d["lx"] = (s.c < s.ind("ll", xN))
    if q.get("reN_b") or q.get("reN_h"):
        rN = int(q["reN_b"]) if q.get("reN_b") else hb(q["reN_h"], tf, 2)
        d["le2"] = (s.c > s.ind("hh", rN)) & (s.c > em)
    return d, q

def run_variant(s, v, cost=1.0):
    d, q = gen8(s, v.get("p", {}))
    ext = dict(v.get("ext") or {})
    if q["ent"] == "lvl": ext["entstop"] = 1
    if "reent_h" in ext: ext["reent"] = max(1, int(round(ext.pop("reent_h") / eng.TFH[s.tf])))
    return eng8.run8(s, d, q["kI"], q["kT"], risk=q["risk"], mlev=q["mlev"], tp=q["tp"], be=q["be"], tron=q["tron"], ext=ext, cost=cost * v.get("cost", 1.0))

def stats(s, eq, trd, wins):
    return {w: s.stat(eq, trd, w) for w in wins}

_BASE = {}
def base_stats(S, a, tf, wins):
    k = (a, tf, tuple(wins), id(S))
    if k not in _BASE:
        eq, ex, trd = run_variant(S[(a, tf)], {})
        _BASE[k] = stats(S[(a, tf)], eq, trd, wins)
    return _BASE[k]

def calm(m):
    return m["calmar"] if (m and m["calmar"] == m["calmar"]) else np.nan

def eval_variant(S, v, assets=ASSETS, tfs=TFS, wins=SEL):
    out = {}
    for a in assets:
        for tf in tfs:
            s = S[(a, tf)]; eq, ex, trd = run_variant(s, v)
            out[(a, tf)] = stats(s, eq, trd, wins)
    return out

def deltas(S, res, wins=SEL):
    rows = []
    for (a, tf), r in res.items():
        b = base_stats(S, a, tf, tuple(wins))
        for w in wins:
            x, y = r[w], b[w]
            if x is None or y is None: continue
            rows.append(dict(a=a, tf=tf, w=w, ret=x["ret"], cagr=x["cagr"], mdd=x["mdd"], n=x["trades"], cal=calm(x),
                             b_ret=y["ret"], b_cagr=y["cagr"], b_mdd=y["mdd"], b_n=y["trades"], b_cal=calm(y)))
    D = pd.DataFrame(rows); D["dcal"] = D.cal - D.b_cal; D["dmdd"] = D.mdd - D.b_mdd; D["dcagr"] = D.cagr - D.b_cagr
    return D

def summ(D, tfs_focus=TFS):
    out = {}
    def g(a, tf, w):
        r = D[(D.a == a) & (D.tf == tf) & (D.w == w)]; return float(r.dcal.iloc[0]) if len(r) else np.nan
    for tf in tfs_focus:
        out[f"E{tf}_tr"] = round(g("ETH", tf, "TRAIN"), 2); out[f"E{tf}_va"] = round(g("ETH", tf, "VAL"), 2)
        out[f"E{tf}_dev"] = round(g("ETH", tf, "DEV"), 2)
        out[f"B{tf}"] = round(g("BTC", tf, "DEV"), 2); out[f"D{tf}"] = round(g("DOGE", tf, "DEV"), 2)
        r = D[(D.a == "ETH") & (D.tf == tf) & (D.w == "DEV")]
        out[f"dMDD_{tf}"] = round(float(r.dmdd.iloc[0]) * 100, 1) if len(r) else np.nan
        out[f"dCAGR_{tf}"] = round(float(r.dcagr.iloc[0]) * 100, 1) if len(r) else np.nan
    return out

def accept(sm, tf):
    """Criterio pre-registrado POR TEMPORALIDAD: ETH dCalmar>0 en TRAIN y VAL; BTC y DOGE >= 0 (media DEV); dMDD ETH > -1 pp."""
    return bool(sm[f"E{tf}_tr"] > 0 and sm[f"E{tf}_va"] > 0 and sm[f"B{tf}"] >= 0 and sm[f"D{tf}"] >= 0 and sm[f"dMDD_{tf}"] > -1.0)

def log(v, res, stage="dev"):
    row = dict(t=time.strftime("%Y-%m-%d %H:%M:%S"), stage=stage, name=v.get("name", ""), fam=v.get("fam", ""), p=v.get("p", {}), ext=v.get("ext", {}),
               res={f"{a}|{tf}|{w}": ({k: (None if (x is None or x != x) else float(x)) for k, x in m.items() if k in ("ret", "cagr", "mdd", "trades", "calmar", "sharpe")} if m else None)
                    for (a, tf), r in res.items() for w, m in r.items()})
    with open(LOG, "a") as f: f.write(json.dumps(row) + "\n")

def trial(S, v, tfs=TFS, assets=ASSETS, wins=SEL, do_log=True, stage="dev"):
    res = eval_variant(S, v, assets, tfs, wins)
    if do_log: log(v, res, stage)
    D = deltas(S, res, wins); sm = summ(D, tfs)
    sm["name"] = v.get("name", ""); sm["acc"] = {tf: accept(sm, tf) for tf in tfs}
    return sm, D, res

def scale_risk(v, m):
    w = json.loads(json.dumps(v)); w.setdefault("p", {}); w["p"]["risk"] = lab.V6P["risk"] * m; return w

def matched_dd(S, v, a, tf, target_mdd, win="DEV", lo=0.2, hi=4.0, it=24):
    s = S[(a, tf)]
    for _ in range(it):
        m = (lo + hi) / 2
        eq, ex, trd = run_variant(s, scale_risk(v, m)); st = s.stat(eq, trd, win)
        if st["mdd"] < target_mdd: hi = m
        else: lo = m
    return m, st
