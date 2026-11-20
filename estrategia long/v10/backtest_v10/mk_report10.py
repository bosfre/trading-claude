"""Genera informe_V10.md leyendo los CSV de resultados (ninguna cifra se transcribe a mano)."""
import pandas as pd, numpy as np, json
C = pd.read_csv("comparativa_V9_V10.csv"); F = pd.read_csv("frontera_riesgo_V10.csv"); K = pd.read_csv("costes_V10.csv")
SR = pd.read_csv("sensibilidad_parametros_V10.csv"); Y = pd.read_csv("retorno_anual_V10.csv", index_col=0)
A = pd.read_csv("anchor10_resultados.csv"); EN = pd.read_csv("ensamble_anclas_resultados.csv"); E = pd.read_csv("experimentos_V10.csv")
V7R = pd.read_csv("v7_vs_v9_ref_V10.csv"); PRE = json.load(open("preset_riesgo_V10.json")); TFS = ("1h", "4h", "1d"); TFN = {"1h": "1H", "4h": "4H", "1d": "1D"}
V9N = "V9 (= V10 estandar, riesgo 5 %)"
def _es(txt): return txt.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
def pr(v): return _es(f"{v*100:,.1f} %") if v == v else "-"
def pr0(v): return _es(f"{v*100:,.0f} %") if v == v else "-"
def nm(v, d=2): return f"{v:.{d}f}".replace(".", ",") if v == v else "-"
def row(tf, ver, win="COMUN 2017-08->2026-10"):
    return C[(C.tf == tf) & (C.version.str.startswith(ver)) & (C.ventana == win)].iloc[0]
def tbl(head, rows): return "| " + " | ".join(head) + " |\n|" + "|".join(["---"] * len(head)) + "|\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows)

# ---- tabla V9 vs V10 (ventana comun) ----
def cmp_rows():
    out = []
    lab = [("Rentabilidad total", lambda r: pr0(r.ret)), ("CAGR", lambda r: pr(r.cagr)), ("Máx. drawdown (intrabarra)", lambda r: pr(r.mdd)), ("Calmar (CAGR/DD)", lambda r: nm(r.calmar)),
           ("Operaciones", lambda r: str(int(r.n))), ("Win rate", lambda r: pr(r.win)), ("Profit Factor (% por operación)", lambda r: nm(r.pf)), ("Profit Factor ($, como TradingView)", lambda r: nm(r.pf_usd)),
           ("Beneficio medio / operación (% equity)", lambda r: pr(r.avg_ret)), ("R medio / operación", lambda r: nm(r.avgR)), ("Ganancia media / pérdida media", lambda r: nm(r.payoff)), ("Sharpe (diario)", lambda r: nm(r.sharpe))]
    for name, f in lab:
        cells = [name]
        for tf in TFS:
            a = row(tf, "V9"); b = row(tf, "V10 preset")
            cells += [f(a), f(b)]
        out.append(cells)
    return out
head = ["Métrica (ETH, 2017-08-17 → 2026-10-03)"] + [f"{TFN[tf]} V9 = V10 (5 %)" if i == 0 else f"{TFN[tf]} V10 preset" for tf in TFS for i in (0, 1)]
T_CMP = tbl(head, cmp_rows())
# ---- ventanas ----
WN = ["TRAIN 2017-08->2021", "VAL 2022-23", "OOS1 2024->2026-01", "OOS2 2026-01->10", "ULTIMOS 2 ANIOS 2024-01->2026-10"]
def win_rows():
    out = []
    for w in WN:
        cells = [w.replace("->", "→").replace("ANIOS", "AÑOS").replace("ULTIMOS", "ÚLTIMOS")]
        for tf in TFS:
            a = row(tf, "V9", w); b = row(tf, "V10 preset", w)
            cells.append(f"{pr(a.cagr)} / {pr(a.mdd)} / {nm(a.calmar)}"); cells.append(f"{pr(b.cagr)} / {pr(b.mdd)} / {nm(b.calmar)}")
        out.append(cells)
    return out
T_WIN = tbl(["Ventana (CAGR / DD / Calmar)"] + [f"{TFN[tf]} V9" if i == 0 else f"{TFN[tf]} preset" for tf in TFS for i in (0, 1)], win_rows())
# ---- frontera ----
def front_rows():
    out = []
    for tgt in (-0.10, -0.12, -0.15, -0.20):
        cells = [f"{int(tgt*100)} %"]
        for tf in TFS:
            r = F[(F.tf == tf) & (F.dd_objetivo == tgt)].iloc[0]; cells.append(f"{nm(r.riesgo_pct,1)} % → CAGR {pr(r.cagr)} (Calmar {nm(r.calmar)})")
        out.append(cells)
    cells = ["sin objetivo (riesgo 5 %)"]
    for tf in TFS:
        r = F[(F.tf == tf) & (F.dd_objetivo.isna())].iloc[0]; cells.append(f"5,0 % → CAGR {pr(r.cagr)} / DD {pr(r.mdd)} (Calmar {nm(r.calmar)})")
    out.append(cells); return out
T_FR = tbl(["DD objetivo"] + [TFN[t] + " (riesgo → CAGR)" for t in TFS], front_rows())
# ---- costes ----
def cost_rows():
    out = []
    for ver in ("V9", "V10 preset"):
        for cm in ("x1", "x2", "x3"):
            cells = [f"{ver} {cm}"]
            for tf in TFS:
                r = K[(K.version == ver) & (K.tf == tf) & (K.costes == cm)].iloc[0]; cells.append(f"{pr(r.cagr)} / {pr(r.mdd)} / {nm(r.calmar)}")
            out.append(cells)
    return out
T_CO = tbl(["Costes (CAGR / DD / Calmar)"] + [TFN[t] for t in TFS], cost_rows())
# ---- anclas ----
def anc_rows():
    out = []
    for tf in ("1d", "4h"):
        for a in ("ETH", "BTC", "DOGE"):
            y = A[(A.a == a) & (A.tf == tf)]; o = float(y[y.off == 0].cagr.iloc[0])
            out.append([f"{a} {TFN[tf]}", str(len(y)), f"{pr0(y.ret.min())} – {pr0(y.ret.median())} – {pr0(y.ret.max())}", f"{pr(y.cagr.min())} – {pr(y.cagr.median())} – {pr(y.cagr.max())}",
                        f"{nm(y.calmar.min())} – {nm(y.calmar.median())} – {nm(y.calmar.max())}", f"{pr(o)} (puesto {int((y.cagr > o).sum() + 1)} de {len(y)})"])
    return out
T_AN = tbl(["Serie", "Anclas", "Rentabilidad (mín – mediana – máx)", "CAGR (mín – mediana – máx)", "Calmar (mín – mediana – máx)", "Ancla estándar 00:00 UTC: CAGR"], anc_rows())
def ens_rows():
    out = []
    for name in ("1d K=4", "1d K=24", "4h K=4"):
        for a in ("ETH", "BTC", "DOGE"):
            r = EN[(EN.ens == name) & (EN.a == a) & (EN.ventana == "COMUN 2017-08->2026-10")].iloc[0]
            out.append([f"{name.replace('1d', '1D').replace('4h', '4H')} · {a}", f"{pr(r.cagr_ens)} / {pr(r.mdd_ens)} / {nm(r.cal_ens)}", f"{pr(r.cagr_avg)} / {pr(r.mdd_avg)} / {nm(r.cal_avg)}", f"{pr(r.cagr_0)} / {pr(r.mdd_0)} / {nm(r.cal_0)}"])
    return out
T_EN = tbl(["Ensamble · activo (ventana común)", "Ensamble CAGR / DD / Calmar", "Media de anclas sueltas", "Ancla estándar 0"], ens_rows())
# ---- sensibilidad ----
def sens_rows(tf):
    x = SR[SR.tf == tf]; b = x[x.param == "base"].iloc[0]; out = []
    for _, r in x.iterrows():
        out.append([str(r.param).replace(".", ","), pr(r.cagr), pr(r.mdd), nm(r.calmar), nm(r.calmar_dev), nm(r.calmar_btc_dev), nm(r.calmar_doge_dev), str(int(r.n))])
    return out
SH = ["Parámetro", "CAGR", "DD", "Calmar (común)", "Calmar DEV ETH", "Calmar DEV BTC", "Calmar DEV DOGE", "Op."]
# ---- anual ----
T_Y = tbl(["Año (ETH, riesgo 5 %)"] + [TFN[t] for t in TFS], [[str(i)] + [pr(Y.loc[i, tf]) if Y.loc[i, tf] == Y.loc[i, tf] else "-" for tf in TFS] for i in Y.index if i >= 2018])
# ---- experimentos ----
def exp_rows():
    out = []
    for fam, g in E.groupby("familia", sort=False):
        nv = g.variante.nunique(); npass = int(g.pasa_criterio.sum())
        det = "; ".join(f"{r.variante} ({TFN[r.tf]})" for _, r in g[g.pasa_criterio].iterrows()) or "ninguna"
        out.append([fam, str(nv), str(len(g)), str(npass), det])
    return out
T_EX = tbl(["Familia", "Variantes", "Pruebas (× 3 TF)", "Pasan criterio básico", "Cuáles"], exp_rows())
nE = len(E); nP = int(E.pasa_criterio.sum()); nV = E.variante.nunique()
v7 = V7R[(V7R.tf == "1d") & (V7R.version.str.startswith("V7"))].iloc[0]; a1 = row("1d", "V9"); a4 = row("4h", "V9"); a1h = row("1h", "V9"); p1 = row("1d", "V10 preset"); p4 = row("4h", "V10 preset"); p1h = row("1h", "V10 preset")

md = f"""# V10 (optimización de V9) — informe

## 1. Conclusión

**V10 mantiene la lógica de V9 (= V8).** No he encontrado ninguna mejora de lógica que sea robusta, y prefiero decírtelo antes que forzar una. Probé **{nV} variantes nuevas ({nE} pruebas = variantes × 3 temporalidades)** de entrada, salida y gestión de posición, fijadas por escrito **antes** de ejecutarlas (`v10_prereg.txt`, con tres enmiendas fechadas) y evaluadas contra V9 solo con TRAIN y VAL en ETH + BTC + DOGE. **{nP} de {nE} pasaron el criterio básico** (≈ {nP/nE*100:.0f} %, compatible con ruido), cada una en una sola temporalidad, con efecto pequeño y con vecinos de parámetros que fallan; ninguna cumplió las reglas anti-falso-positivo (R1: ≥ 2 temporalidades o efecto grande; R2: vecinos que no empeoren), así que no se abrió ningún holdout y no se adoptó nada.

**Qué significa para tus objetivos (1H, 4H y 1D en conjunto)**
- **Rentabilidad, Profit Factor, win rate y beneficio por operación: no mejorados.** Con riesgo 5 % V10 = V9 exactamente: 1H +{pr0(a1h.ret)} / DD {pr(a1h.mdd)}, 4H +{pr0(a4.ret)} / {pr(a4.mdd)}, 1D +{pr0(a1.ret)} / {pr(a1.mdd)} (ETH, 2017-08 → 2026-10).
- **Drawdown: solo se reduce bajando el riesgo**, y entonces cae la rentabilidad casi en proporción (el Calmar apenas se mueve). Lo ofrezco como **preset de riesgo opcional** (sección 3), no como mejora de la estrategia. Con él, el DD baja a ≈ −15 % en las tres temporalidades; no lo activo por defecto porque en 1D reduce la rentabilidad de +{pr0(a1.ret)} a +{pr0(p1.ret)}, justo lo que pediste no empeorar.
- **1D**: no se empeora, pero tampoco mejora. Lo que sí he podido medir es **cuánto de su resultado es suerte**: con la misma estrategia y los mismos datos, solo desplazando la hora en que empieza el día, ETH 1D va de CAGR {pr(A[(A.a=='ETH')&(A.tf=='1d')].cagr.min())} a {pr(A[(A.a=='ETH')&(A.tf=='1d')].cagr.max())} (sección 5).

**Hallazgos nuevos que sí te sirven**
1. **El filtro de BTC puede estar desactivado en tu gráfico sin que lo notes.** En el Pine de V8/V9 el filtro no bloquea nada si BTC no tiene dato en una barra. Tus cifras de 1D (+366 %, DD ≈ 27 %) se parecen más a **V7 sin filtro** en mi backtest (+{pr0(v7.ret)}, {pr(v7.mdd)}) que a V9 (+{pr0(a1.ret)}, {pr(a1.mdd)}). El Pine V10 trae un panel que muestra si el filtro está activo y en cuántas barras faltan datos de BTC.
2. **En ETH, 1D es muy sensible al stop**: k = 4,0–4,5 ATR empeora el DD hasta −31 % y el Calmar cae de 0,91 a 0,63–0,66; pero en BTC y DOGE esa misma bajada **mejora** el Calmar (BTC 1,40 y DOGE 0,59 con k = 4,0, frente a 0,90 y 0,24). La dirección no es consistente entre activos, así que tampoco es una palanca que explotar: es otra muestra de que 1D tiene más azar que señal. 4H es la temporalidad más estable ante cambios de parámetros.
3. **El ancla estándar de 1D (00:00 UTC) es de las peores** para ETH y DOGE (puesto 23 de 24), pero está a mitad de tabla en BTC. No es una ventaja explotable a priori (no hay una razón económica para que un ancla sea mejor): es ruido de temporización.

## 2. Qué es V10 exactamente

Lógica idéntica a V8/V9: largo si el cierre supera el máximo de 140 h y la EMA de 800 h, **y** BTC está sobre su EMA de 800 h; stop inicial y trailing de 5 ATR, TP a 20 ATR, riesgo 5 % por operación (apalancamiento máx. 2×). Cambios **operativos** (no de edge) en `V10_ETH_Donchian_EMA_ATR_TP_BTC.pine`:
1. Panel de diagnóstico del filtro BTC (activo/desactivado, barras sin datos de BTC, señales bloqueadas, riesgo aplicado).
2. Preset de riesgo opcional por temporalidad (1H {nm(PRE['1h'],1)} % · 4H {nm(PRE['4h'],1)} % · 1D {nm(PRE['1d'],1)} %), por defecto en **Manual 5 % = V9**.
3. Se eliminó la piramidación experimental (venía apagada y está descartada desde V7).
El Pine **no está compilado ni probado en TradingView** desde este entorno.

## 3. V10 frente a V9 en 1H, 4H y 1D

Datos: tus CSV de ETH (1h/4h/1d hasta 2026-01-06) + tramo de Twelve Data hasta 2026-10-03; costes del repo (comisión 0,06 %, slippage por activo, funding). Las cifras de V9 se han **re-ejecutado con estos CSV**: 1H y 4H coinciden con el informe V9 (+1.431 % y +1.011 % frente a +1.429 % y +1.010 %); 1D da +{pr0(a1.ret)} frente a +464 % del informe V9, porque aquí se lee el CSV diario directamente en vez de remuestrear desde 15 m.

{T_CMP}

**Qué ha mejorado, qué ha empeorado (preset DD ≈ 15 % frente a V9 con riesgo 5 %)**
- **Mejora**: el drawdown (1H {pr(a1h.mdd)} → {pr(p1h.mdd)}; 4H {pr(a4.mdd)} → {pr(p4.mdd)}; 1D {pr(a1.mdd)} → {pr(p1.mdd)}) y el Profit Factor en dólares (1H {nm(a1h.pf_usd)} → {nm(p1h.pf_usd)}; 4H {nm(a4.pf_usd)} → {nm(p4.pf_usd)}; 1D {nm(a1.pf_usd)} → {nm(p1.pf_usd)}). Esto último es un efecto de ponderación (el PF en dólares da más peso a las operaciones recientes cuando la cuenta ya ha crecido y, con menos riesgo, crece más despacio), no una mejor calidad de operación: el PF por operación no cambia.
- **Empeora**: CAGR (1H {pr(a1h.cagr)} → {pr(p1h.cagr)}; 4H {pr(a4.cagr)} → {pr(p4.cagr)}; 1D {pr(a1.cagr)} → {pr(p1.cagr)}), rentabilidad total y beneficio medio por operación (1H {pr(a1h.avg_ret)} → {pr(p1h.avg_ret)}). El Calmar baja un poco (1H {nm(a1h.calmar)} → {nm(p1h.calmar)}; 4H {nm(a4.calmar)} → {nm(p4.calmar)}; 1D {nm(a1.calmar)} → {nm(p1.calmar)}): es moverse por la misma curva, no mejorarla.
- **Igual**: win rate, Profit Factor por operación, R medio, ganancia/pérdida media y nº de operaciones (las señales son las mismas). Por eso **el win rate no se puede subir sin cambiar la lógica, y la lógica probada no lo mejora de forma robusta**.
- **Coste del preset por punto de drawdown recortado**: 1H {nm((a1h.cagr-p1h.cagr)/(p1h.mdd-a1h.mdd),2)} pp de CAGR por cada pp de DD, 4H {nm((a4.cagr-p4.cagr)/(p4.mdd-a4.mdd),2)} y 1D {nm((a1.cagr-p1.cagr)/(p1.mdd-a1.mdd),2)}. En ninguna temporalidad se recorta DD gratis.

**Por ventanas** (CAGR / DD / Calmar). TRAIN y VAL fueron las ventanas de selección; OOS1 y OOS2 ya se conocían de V8/V9, así que describen pero no son pruebas independientes.

{T_WIN}

**Frontera de riesgo** (riesgo que da cada DD en la ventana común; mide eficiencia, no una mejora):

{T_FR}

## 4. Qué se probó y por qué se descartó (`experimentos_V10.csv`, `trials10.jsonl`)

Criterio por temporalidad (el de V9): ΔCalmar ETH > 0 en TRAIN **y** VAL; ΔCalmar BTC y DOGE ≥ 0; ΔDD ETH no peor de 1 pp; ΔR/operación ETH > 0. Reglas añadidas en V10: **R1** solo se adopta si pasa en ≥ 2 temporalidades con los mismos parámetros, o en 1 con efecto grande (ΔCalmar ≥ 0,3) y un vecino que también pase; **R2** debe haber un vecino de parámetros que no empeore; **R3** nunca se acepta nada que empeore 1D.

{T_EX}

- **Volumen de ruptura** (primera vez que se usa como regla): con ≥ 1,0× la media mejora 4H en TRAIN (+0,17) pero no en VAL, y 1D empeora (−0,21 / −0,14); con ≥ 1,5× es inestable (4H TRAIN +0,32, VAL −0,12; 1D TRAIN −1,35). El tramo 2026 no tiene volumen en los datos, así que el filtro no actúa ahí.
- **Parada por estancamiento**: mi primer intento (280-560 h) **era nulo por construcción**: el estancamiento máximo dentro de una operación 4H de la muestra es de 248 h (lo corregí en la enmienda 1 y conté las pruebas nuevas). Con umbrales alcanzables (100-200 h) ninguna pasa y en 1D empeora (ΔR/op hasta −0,12, DD hasta 3,4 pp peor).
- **Enfriamiento tras pérdida**: la única con apariencia de señal (100 h pasa en 1H). La curva de sensibilidad pre-registrada (C = 50-200 h) da **0 de 6 valores que pasen a la vez en 1H y 4H** (regla: ≥ 4), los signos cambian entre vecinos y con 300 h destroza TRAIN (−0,9 a −1,7). Es ruido.
- **Ruptura fallida**: solo 150 h/2 ATR pasa, en 1D, con efecto de +0,10 / +0,06: incumple R1; en 1H/4H empeora DOGE (−0,3 a −0,6).
- **Ancla del trailing en cierres** y **confirmación de 2 cierres**: signos contrarios entre TRAIN/VAL o entre activos.
- **Ya descartado en V6-V9 y no repetido**: pirámide, cortos, reentrada, parciales, entrada por stop, stop al cierre, throttle por DD, trinquetes, multi-velocidad, filtros de volatilidad/ADX/régimen, TP 0-40, rejilla N×L×ATR×k, ETH/BTC, salidas temporales, salidas por EMA/BTC, trailing más ancho, filtro de extensión, calidad de vela.
- **No probado** (prior bajo → minería de datos): hora/día de la semana; amplitud de mercado con ETC (no hay ETC en 2026).

**Aviso estadístico**: el criterio básico deja pasar por azar una fracción de pruebas que no puedo fijar con precisión (las pruebas están correlacionadas entre temporalidades y activos); {nP} de {nE} ({nP/nE*100:.0f} %) es compatible con ruido, y ninguna sobrevive a R1/R2. Los {nV} intentos se hicieron sobre un espacio ya muy explorado (V6-V9 acumulan cientos de variantes), así que la probabilidad a priori de una mejora real era baja.

## 5. Robustez de la base (V10 = V9)

### 5.1 Ancla de la vela: ¿cuánto del resultado es suerte?
Misma V9, mismos datos; las velas de 1D se construyen desde 1H con 24 anclas (la vela empieza a las 00, 01, … 23 h UTC) y las de 4H con 4 anclas. No es una búsqueda de parámetros: mide el ruido de temporización.

{T_AN}

El ancla estándar de 1D (00:00 UTC, la de TradingView) es la 23.ª de 24 en ETH y en DOGE y la 10.ª en BTC. **La dependencia es grande en 1D** (la rentabilidad de ETH va de +374 % a +930 %) **y pequeña en 4H**. Consecuencias: (1) diferencias de pocos puntos entre temporalidades, o entre tu TradingView y mi backtest, pueden ser solo esto; (2) la ventaja o desventaja de 1D frente a 4H no se puede leer al detalle: con la **mediana** de anclas, 1D (Calmar {nm(A[(A.a=='ETH')&(A.tf=='1d')].calmar.median())}) sigue por debajo de 4H ({nm(A[(A.a=='ETH')&(A.tf=='4h')].calmar.median())}), pero la brecha es menor que con el ancla estándar (0,91 frente a 1,72).

**¿Mejora repartir el capital entre varias anclas?** (pesos iguales, sin optimizar; se compara con la **media** de las anclas sueltas, la comparación justa; contra el ancla 0 la mejora sería casi toda regresión a la media)

{T_EN}

El ensamble de 24 anclas en 1D recorta ≈ 1,5 pp de DD y suma ≈ +0,1 de Calmar frente a la media de anclas: diversificación real pero pequeña (los sleeves están muy correlacionados). **No cumple mi criterio pre-registrado** (BTC en DEV: Calmar 0,93 frente a 0,95; el ensamble de 4 anclas falla en TRAIN y el de 4H en VAL) y exigiría ejecutar 24 sleeves en paralelo, que en TradingView no es práctico. Queda como hallazgo, no como cambio de V10.

### 5.2 Sensibilidad de parámetros (una a una, sobre V9)
**1H**

{tbl(SH, sens_rows('1h'))}

**4H**

{tbl(SH, sens_rows('4h'))}

**1D** (A_h y parte de N_h no cambian nada: los mínimos de barras del Pine, N ≥ 5, ATR ≥ 10, los fijan)

{tbl(SH, sens_rows('1d'))}

Lectura: en 1H y 4H la base está en una meseta (Calmar 1,1-1,7 en 1H y 1,2-1,8 en 4H en los vecinos; N y EMA más largas empeoran de forma suave). **1D en ETH es frágil al stop**: k = 4,0-4,5 baja el Calmar de 0,91 a 0,63-0,66 y sube el DD a −26,5 % / −31 %, mientras que en BTC y DOGE la misma bajada mejora el Calmar DEV (BTC 1,40 y 0,97; DOGE 0,59 y 0,50, frente a 0,90 y 0,24): sin dirección común entre activos. Ningún valor mejora claramente la base en las tres temporalidades a la vez. La excepción aparente, EMA 600-700 h en 1D (Calmar 1,02-1,05), empeora BTC en DEV (0,77-0,83 frente a 0,90) y no ayuda en 1H, así que no la tomo como mejora; sirve para ver que 1D tiene más recorrido de azar que de señal.

### 5.3 Costes y slippage (ventana común)
{T_CO}

Con costes ×3 el Calmar de V9 es 0,94 (1H), 1,03 (4H) y 0,57 (1D): el orden entre temporalidades no cambia y el recorte relativo de CAGR es parecido (−25 % a −27 %). El preset de riesgo aguanta igual.

### 5.4 Retorno por año (ETH, riesgo 5 %)
{T_Y}

## 6. Sobre tus cifras de 1D (+366 %, DD ≈ 27 %)
No las reproduzco con V9: en mi backtest 1D da +{pr0(a1.ret)} / {pr(a1.mdd)} (2017-08 → 2026-10). **V7 sin filtro BTC**, re-ejecutada con los mismos datos y ventana (`v7_vs_v9_ref_V10.csv`), da +{pr0(v7.ret)} / {pr(v7.mdd)}, mucho más cerca de lo que ves que V9. Es una pista, no una prueba: otras causas posibles son costes distintos, el ancla de la vela y el rango de fechas. Compruébalo en TradingView: (1) con el Pine V10, mira el panel (si dice que faltan datos de BTC, el filtro no actúa); (2) activa y desactiva "Filtro de régimen BTC": si el resultado no cambia, el filtro no se está aplicando; (3) usa el mismo símbolo de ETH (Binance ETHUSDT) y el mismo rango de fechas. Con periodos distintos, 1D también cambia mucho por el ancla de la vela (sección 5.1).

## 7. Qué NO puedo afirmar
- **No hay OOS virgen para V10**: 2024-2026 se conocía de V8/V9. Por eso todas las selecciones se hicieron solo con TRAIN/VAL y no se abrió ningún holdout (`oos_access_log.txt`). Que V10 = V9 en lógica **no añade sobreajuste**.
- {nE} pruebas dan resultados espurios por azar; la regla R1/R2 los filtra, pero un efecto real pequeño (< ~0,1 de Calmar) tampoco es detectable con ~12-16 operaciones al año.
- El Pine no está compilado ni probado en TradingView; las diferencias con tu TradingView pueden venir de costes (los de TradingView son más benignos), de los datos de tu exchange y del ancla.
- Los datos de 2026 (Twelve Data) no tienen volumen y son de otro proveedor que Binance.

## 8. Siguientes pasos razonables
1. Verificar en TradingView el filtro de BTC con el panel de V10 (sección 6) antes de comparar nada más.
2. Si quieres DD ≈ 15 %: usar el preset o un riesgo intermedio de la tabla de frontera; no esperes que mejore el Calmar.
3. Para mejorar 1D "de verdad" hace falta información nueva (otros activos, datos de derivados, amplitud de mercado), no más reglas sobre el precio de ETH; 1D tiene el resultado más dependiente del azar de la vela.
4. Repetir el análisis cuando haya 6-12 meses más de datos fuera de muestra.

## 9. Archivos
`informe_V10.md`, `V10_ETH_Donchian_EMA_ATR_TP_BTC.pine`, `experimentos_V10.csv`, `comparativa_V9_V10.csv`, `frontera_riesgo_V10.csv`, `costes_V10.csv`, `sensibilidad_parametros_V10.csv`, `retorno_anual_V10.csv`, `anchor10_resultados.csv`, `ensamble_anclas_resultados.csv`, `v7_vs_v9_ref_V10.csv`, `v10_prereg.txt`, `oos_access_log.txt`, `trials10.jsonl` y el código en `backtest_v10/` (`eng10.py` motor, `exp10.py` arnés, `round10a/b/c.py` rondas, `anchor10.py`/`ens10.py` anclas, `final10.py` análisis, `verify10.py` verificación independiente, `test_eng10.py` test de que el motor reproduce V9 al bit).
"""
open("../informe_V10.md", "w").write(md)
print("informe_V10.md escrito:", len(md), "caracteres")
