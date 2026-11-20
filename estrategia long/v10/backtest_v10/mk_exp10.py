import pandas as pd, numpy as np
A = pd.read_pickle("round10a.pkl"); A["ronda"] = "10a"
Bb = pd.read_pickle("round10b.pkl"); Bb["ronda"] = "10b (enmienda 1)"
Cc = pd.read_pickle("round10c.pkl"); Cc["name"] = Cc["C"].map(lambda c: f"enfria {c}h"); Cc["fam"] = "G3"; Cc["ronda"] = "10c (enmienda 2)"
Cc = Cc[Cc.C != 100]                       # C=100 ya esta en la ronda 10a (mismo resultado)
R = pd.concat([A, Bb, Cc], ignore_index=True)
fam = {"G1": "G1 volumen", "G2": "G2 estancamiento", "G2b": "G2b estancamiento (umbrales alcanzables)", "G3": "G3 enfriamiento tras perdida", "G4": "G4 ruptura fallida", "G5": "G5 ancla del trailing en cierres", "G6": "G6 confirmacion 2 cierres"}
what = {"vol>=1.0x": "Entrar solo si volumen de la vela de ruptura >= 1,0 x media de las N velas previas", "vol>=1.5x": "... >= 1,5 x la media",
        "estanc 280h->3.5": "Sin nuevo maximo en 280 h: trailing 5 -> 3,5 ATR (nunca se activa: estancamiento max. 248 h)", "estanc 560h->3.5": "560 h -> 3,5 ATR (nunca se activa)", "estanc 560h->4.0": "560 h -> 4,0 ATR (nunca se activa)",
        "estanc 100h->3.0": "Sin nuevo maximo en 100 h: trailing 5 -> 3,0 ATR", "estanc 150h->3.5": "150 h -> 3,5 ATR", "estanc 200h->4.0": "200 h -> 4,0 ATR",
        "fallida 50h/1ATR": "Salir si en las 50 h iniciales el cierre cae 1 ATR bajo el nivel del canal roto", "fallida 150h/1ATR": "150 h / 1 ATR", "fallida 150h/2ATR": "150 h / 2 ATR",
        "ancla cierres": "El trailing sigue al maximo de cierres, no al maximo intrabarra", "confirma 2 cierres": "Entrar solo tras 2 cierres consecutivos sobre el canal"}
rows = []
for _, r in R.iterrows():
    for tf in ("1h", "4h", "1d"):
        fails = []
        if not r[f"E{tf}_tr"] > 0: fails.append("ETH TRAIN")
        if not r[f"E{tf}_va"] > 0: fails.append("ETH VAL")
        if not r[f"B{tf}"] >= 0: fails.append("BTC")
        if not r[f"D{tf}"] >= 0: fails.append("DOGE")
        if not r[f"dMDD_{tf}"] > -1.0: fails.append("DD")
        if not r[f"dR_{tf}"] > 0: fails.append("R/op")
        nm = r["name"]; d = what[nm] if nm in what else f"Enfriamiento: no abrir otra operacion durante {nm.split()[1]} tras una perdedora"
        rows.append(dict(ronda=r["ronda"], familia=fam[r["fam"]], variante=nm, descripcion=d, tf=tf, dCalmar_ETH_TRAIN=r[f"E{tf}_tr"], dCalmar_ETH_VAL=r[f"E{tf}_va"], dCalmar_BTC_DEV=r[f"B{tf}"],
                         dCalmar_DOGE_DEV=r[f"D{tf}"], dMDD_ETH_pp=r[f"dMDD_{tf}"], dR_por_op_ETH=r[f"dR_{tf}"], pasa_criterio=bool(r["acc"][tf]), falla_en=", ".join(fails) if fails else "-"))
E = pd.DataFrame(rows)
E["decision"] = "Descartada"
E.loc[E.pasa_criterio, "decision"] = "Pasa el criterio basico en esta TF pero NO la regla R1/R2 (una sola TF, efecto pequeno o vecinos que fallan) -> descartada"
E.loc[E.variante.str.startswith("estanc 280") | E.variante.str.startswith("estanc 560"), "decision"] = "Prueba nula por construccion (umbral mayor que cualquier estancamiento real); sustituida por G2b"
E.to_csv("experimentos_V10.csv", index=False)
print(len(E), "filas |", E.variante.nunique(), "variantes | pasan criterio basico:", int(E.pasa_criterio.sum()))
print(E[E.pasa_criterio][["ronda", "variante", "tf"]].to_string(index=False))
