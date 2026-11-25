"""Backtest conjunto VW1 vs V10 sola vs W10 sola (ver vw1_prereg.txt). Escribe CSV en esta carpeta."""
import os, numpy as np, pandas as pd
import prep_vw as P
from prep_vw import TFS

SEGS = ("TRAIN", "VAL", "OOS1", "OOS2", "ORIG", "FULL")
OUT = P.HERE
rows = []; ov_rows = []; ann = {}; boot_rows = []

def add(tf, model, cm, scen, R, eq=None, segs=SEGS):
    for seg in segs:
        m = P.stats(R, seg, eq=eq)
        if m and eq is not None:      # curva de equity ajena (50/50): solo valen las métricas de equity, no las de operaciones
            m = {k: (v if k in ("ret", "cagr", "mdd", "calmar", "yrs") else np.nan) for k, v in m.items()}
        if m: rows.append(dict(tf=tf, modelo=model, costes=f"x{cm:g}", escenario=scen, tramo=seg, **m))

def boot(tr, seg_end, n_res=5000, seed=7):
    """Remuestreo de operaciones (con reemplazo) de la ventana ORIG: DD máximo y rentabilidad final por orden de operaciones aleatorio."""
    r = tr[tr[:, 1] < seg_end, 5]
    if len(r) < 10: return None
    rng = np.random.default_rng(seed); k = len(r)
    draws = rng.choice(r, size=(n_res, k), replace=True)
    path = np.cumprod(1 + draws, axis=1)
    pk = np.maximum.accumulate(np.concatenate([np.ones((n_res, 1)), path], axis=1), axis=1)[:, 1:]
    mdd = (path / pk - 1).min(axis=1)
    return dict(n=k, dd_p50=float(np.percentile(mdd, 50)), dd_p5=float(np.percentile(mdd, 5)), ret_p5=float(np.percentile(path[:, -1] - 1, 5)), ret_p50=float(np.percentile(path[:, -1] - 1, 50)),
                p_loss=float((path[:, -1] < 1).mean()))

for tf in TFS:
    A = P.arrays(tf); idx = A["idx"]
    orig_end = int(idx.searchsorted(pd.Timestamp("2026-01-11")))
    for model, cms in (("pine", (1.0, 2.0, 3.0)), ("orig", (1.0,))):
        for cm in cms:
            Ra = P.run(tf, True, False, model, cm)                 # V10 sola
            Rb = P.run(tf, False, True, model, cm)                 # W10 sola
            Rc = P.run(tf, True, True, model, cm)                  # VW1
            Rd = P.run(tf, True, True, model, cm, flip=True)       # VW1-flip (variante única)
            Re_eq = P.blend(Ra, Rb, 0.5)                           # 50/50 cuentas independientes
            add(tf, model, cm, "A  V10 sola", Ra); add(tf, model, cm, "B  W10 sola", Rb); add(tf, model, cm, "C  VW1", Rc)
            add(tf, model, cm, "D  VW1-flip", Rd); add(tf, model, cm, "E  50/50 cuentas separadas", Ra, eq=Re_eq)
            if model == "pine" and cm == 1.0:
                # ---- solapamiento ----
                pa, pb = Ra["pos"], Rb["pos"]
                ta, tb = Ra["tr"], Rb["tr"]
                # entradas de A cuya señal cae con B abierta (barra ei-1) y viceversa: pérdida de primer orden
                blkA = int(sum(1 for t in ta if pb[int(t[0]) - 1] != 0)); blkB = int(sum(1 for t in tb if pa[int(t[0]) - 1] != 0))
                both = float(((pa != 0) & (pb != 0)).mean()); inA = float((pa != 0).mean()); inB = float((pb != 0).mean())
                tc = Rc["tr"]; nL = int((tc[:, 2] == 1).sum()); nS = int((tc[:, 2] == -1).sum())
                ov_rows.append(dict(tf=tf, n_V10_sola=len(ta), n_long_VW1=nL, perdida_long=1 - nL / len(ta), n_W10_sola=len(tb), n_short_VW1=nS, perdida_short=1 - nS / len(tb),
                                    entradas_V10_con_W10_abierta=blkA, entradas_W10_con_V10_abierta=blkB, conflictos_misma_barra=int(Rc["cnt"][0]),
                                    barras_senal_long_ignorada=int(Rc["cnt"][1]), barras_senal_short_ignorada=int(Rc["cnt"][2]),
                                    t_en_mercado_V10=inA, t_en_mercado_W10=inB, t_solapado_si_fueran_cuentas_separadas=both, t_en_mercado_VW1=float((Rc["pos"] != 0).mean())))
                ann[(tf, "V10 sola")] = P.yearly(Ra); ann[(tf, "W10 sola")] = P.yearly(Rb); ann[(tf, "VW1")] = P.yearly(Rc)
                ann[(tf, "50/50 separadas")] = P.yearly(Ra, eq=Re_eq)
                for nm, Rx in (("V10 sola", Ra), ("W10 sola", Rb), ("VW1", Rc)):
                    b = boot(Rx["tr"], orig_end)
                    if b: boot_rows.append(dict(tf=tf, escenario=nm, **b))
        print(tf, "ok", flush=True)

R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "resultados_VW1.csv"), index=False)
pd.DataFrame(ov_rows).to_csv(os.path.join(OUT, "solapamiento_VW1.csv"), index=False)
pd.DataFrame(boot_rows).to_csv(os.path.join(OUT, "bootstrap_VW1.csv"), index=False)
Y = pd.DataFrame({f"{k[0]} | {k[1]}": v for k, v in ann.items()}).sort_index(); Y.to_csv(os.path.join(OUT, "retorno_anual_VW1.csv"))
print("escritos: resultados_VW1.csv, solapamiento_VW1.csv, bootstrap_VW1.csv, retorno_anual_VW1.csv")
