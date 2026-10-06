import pandas as pd, numpy as np, json
R=pd.read_pickle("round9a.pkl")
fam={"TS":"G1 salida temporal","salida":"G1 salida por tendencia","trail":"G2 trailing más ancho","TP20":"G2 TP→trailing","saltar":"G3 filtro de extensión","CLV":"G3 calidad de vela","tamaño":"G3 tamaño por extensión"}
def f(n):
    for k,v in fam.items():
        if n.startswith(k): return v
    return ""
what={"TS 140h MFE<1ATR":"Salir a las 140 h si el beneficio máximo aún no llegó a 1 ATR","TS 140h MFE<2ATR":"Salir a las 140 h si no llegó a 2 ATR","TS 280h MFE<1ATR":"Salir a las 280 h si no llegó a 1 ATR","TS 280h MFE<2ATR":"Salir a las 280 h si no llegó a 2 ATR",
"salida close<EMA":"Salir si el cierre cae bajo la EMA 800 h","salida close<EMA-1ATR":"Salir si el cierre cae 1 ATR bajo la EMA 800 h","salida BTC<EMA800h":"Salir si BTC pierde su EMA 800 h",
"trail 7 tras +8ATR":"Trailing 5→7 ATR tras +8 ATR de beneficio","trail 8 tras +12ATR":"Trailing 5→8 ATR tras +12 ATR","TP20->trail3.5":"Sin TP a 20 ATR; trailing 3,5 ATR tras +20 ATR",
"saltar si ext>6":"No entrar si el cierre está >6 ATR sobre la EMA","saltar si ext>8":"No entrar si >8 ATR sobre la EMA","CLV>=0.5":"Cierre de la vela en el 50 % superior","CLV>=0.7":"Cierre de la vela en el 30 % superior","tamaño x0.5 si ext>6":"Tamaño x0,5 si >6 ATR sobre la EMA"}
rows=[]
for _,r in R.iterrows():
    for tf in ("1h","4h","1d"):
        fails=[]
        if not r[f"E{tf}_tr"]>0: fails.append("ETH TRAIN")
        if not r[f"E{tf}_va"]>0: fails.append("ETH VAL")
        if not r[f"B{tf}"]>=0: fails.append("BTC")
        if not r[f"D{tf}"]>=0: fails.append("DOGE")
        if not r[f"dMDD_{tf}"]>-1.0: fails.append("DD")
        if not r[f"dR_{tf}"]>0: fails.append("R/op")
        rows.append(dict(familia=f(r["name"]),variante=r["name"],descripcion=what.get(r["name"],""),tf=tf,dCalmar_ETH_TRAIN=r[f"E{tf}_tr"],dCalmar_ETH_VAL=r[f"E{tf}_va"],dCalmar_BTC_DEV=r[f"B{tf}"],dCalmar_DOGE_DEV=r[f"D{tf}"],dMDD_ETH_pp=r[f"dMDD_{tf}"],dR_por_op_ETH=r[f"dR_{tf}"],
                         pasa_criterio=bool(r["acc"][tf]),falla_en=", ".join(fails) if fails else "—"))
E=pd.DataFrame(rows)
# resultado de holdouts (solo las dos que se abrieron)
E["holdouts"]=""
E.loc[(E.variante=="salida close<EMA-1ATR")&(E.tf=="1d"),"holdouts"]="PRE +0,07 ok | ETC −0,05 FALLA (umbral −0,02) | 2024-26 +0,11 ok (DD 1,5 pp menos profundo) | costes x2 +0,03 | a igual DD +0,6 pp CAGR | años 5/8 (+1,1 pp) → DESCARTADA (ETC; efecto mínimo)"
E.loc[(E.variante=="saltar si ext>6")&(E.tf=="1d"),"holdouts"]="No pasaba el criterio (BTC −0,02). Mirada exploratoria, no adoptable: PRE −6,29 Calmar (+96 % vs +306 %) | ETC −0,23 | 2024-26 +0,35 (DD 6,6 pp menos profundo) | años 6/8 → DESCARTADA (se hunde en 2015-17 y ETC)"
E.to_csv("experimentos_V9.csv",index=False)
print(E[E.pasa_criterio][["variante","tf","falla_en"]]); print(len(E),"filas; pasan:",int(E.pasa_criterio.sum()),"de",len(E))
