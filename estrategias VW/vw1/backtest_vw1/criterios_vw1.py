"""Evalúa los criterios C1-C5 y el de la variante D fijados en vw1_prereg.txt, a partir de los CSV de run_vw1.py."""
import pandas as pd, numpy as np, os
H = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(os.path.join(H, "resultados_VW1.csv")); O = pd.read_csv(os.path.join(H, "solapamiento_VW1.csv"))
TFS = ("1h", "4h", "1d")
def g(tf, model, cost, scen, seg, col):
    r = R[(R.tf == tf) & (R.modelo == model) & (R.costes == cost) & (R.escenario.str.startswith(scen + " ")) & (R.tramo == seg)]
    return float(r[col].iloc[0])
out = []
def rec(c, desc, ok, det): out.append(dict(criterio=c, descripcion=desc, cumple=bool(ok), detalle=det)); print(f"{c}: {'CUMPLE' if ok else 'NO CUMPLE'}  {det}")
def evaluate(model):
    print(f"\n######## modelo {model} ########")
    sfx = "" if model == "pine" else " (orig)"
    if model == "pine":
        ok = all((O.perdida_long < .20) & (O.perdida_short < .20))
        rec("C1" + sfx, "pérdida de operaciones por solapamiento < 20 % en cada lado", ok, "; ".join(f"{r.tf}: long {r.perdida_long*100:.1f} %, short {r.perdida_short*100:.1f} %" for r in O.itertuples()))
    n = 0; det = []
    for tf in TFS:
        c = g(tf, model, "x1", "C", "FULL", "calmar"); a = g(tf, model, "x1", "A", "FULL", "calmar"); b = g(tf, model, "x1", "B", "FULL", "calmar")
        n += (c > a and c > b); det.append(f"{tf}: VW1 {c:.2f} vs V10 {a:.2f} / W10 {b:.2f}")
    rec("C2" + sfx, "Calmar FULL de VW1 > el de A y B en >=2 de 3 TF", n >= 2, "; ".join(det))
    allok = True; det = []
    for seg in ("TRAIN", "VAL", "OOS1"):
        k = 0; parts = []
        for tf in TFS:
            c = g(tf, model, "x1", "C", seg, "ret"); m = max(g(tf, model, "x1", "A", seg, "ret"), g(tf, model, "x1", "B", seg, "ret"))
            k += (c >= m); parts.append(f"{tf} {c*100:.0f} % vs {m*100:.0f} %")
        allok &= (k >= 2); det.append(f"{seg}: {k}/3 ({'; '.join(parts)})")
    rec("C3" + sfx, "en TRAIN, VAL y OOS1, ret(VW1) >= mejor de A/B en >=2 de 3 TF", allok, " | ".join(det))
    if model == "pine":
        allok = True; det = []
        for cost in ("x2", "x3"):
            for tf in TFS:
                c = g(tf, model, cost, "C", "FULL", "calmar"); r = g(tf, model, cost, "C", "FULL", "ret")
                allok &= (c > 1 and r > 0); det.append(f"{cost} {tf}: Calmar {c:.2f}, ret {r*100:.0f} %")
        rec("C4", "con costes x2 y x3: Calmar > 1 y rentabilidad > 0 en las 3 TF", allok, "; ".join(det))
    allok = True; det = []
    for tf in TFS:
        c = abs(g(tf, model, "x1", "C", "FULL", "mdd")); m = max(abs(g(tf, model, "x1", "A", "FULL", "mdd")), abs(g(tf, model, "x1", "B", "FULL", "mdd")))
        allok &= (c - m <= 0.05); det.append(f"{tf}: VW1 {c*100:.1f} % vs max(A,B) {m*100:.1f} % (dif {100*(c-m):+.1f} pp)")
    rec("C5" + sfx, "DD de VW1 no supera el mayor de A/B en más de 5 pp", allok, "; ".join(det))
    k = 0; det = []
    for tf in TFS:
        wins = [g(tf, model, "x1", "D", s, "calmar") > g(tf, model, "x1", "C", s, "calmar") for s in ("TRAIN", "VAL", "OOS1")]
        k += all(wins); det.append(f"{tf}: D>C en " + ",".join(s for s, w in zip(("TRAIN", "VAL", "OOS1"), wins) if w) if any(wins) else f"{tf}: D>C en ninguno")
    rec("D" + sfx, "VW1-flip supera a VW1 en Calmar en TRAIN, VAL y OOS1 a la vez en >=2 de 3 TF (si no, se descarta)", k >= 2, "; ".join(det))
evaluate("pine"); evaluate("orig")
pd.DataFrame(out).to_csv(os.path.join(H, "criterios_VW1.csv"), index=False)
