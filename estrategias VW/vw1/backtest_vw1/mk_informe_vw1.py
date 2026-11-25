"""Genera ../informe_VW1_backtest.md a partir de los CSV (las tablas se escriben desde los datos, no a mano)."""
import pandas as pd, numpy as np, os
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "..", "informe_VW1_backtest.md")
R = pd.read_csv(os.path.join(H, "resultados_VW1.csv")); O = pd.read_csv(os.path.join(H, "solapamiento_VW1.csv"))
B = pd.read_csv(os.path.join(H, "bootstrap_VW1.csv")); Y = pd.read_csv(os.path.join(H, "retorno_anual_VW1.csv"), index_col=0)
C = pd.read_csv(os.path.join(H, "criterios_VW1.csv")); V = pd.read_csv(os.path.join(H, "validacion_motor.csv"))
TFS = ("1h", "4h", "1d"); TFN = {"1h": "1H", "4h": "4H", "1d": "1D"}
SEGN = {"TRAIN": "TRAIN 2017-08→2021", "VAL": "VAL 2022-23", "OOS1": "OOS1 2024→2026-01-10", "OOS2": "OOS2 2026-01-11→10-03", "ORIG": "ORIG (TRAIN+VAL+OOS1)", "FULL": "FULL 2017-08→2026-10"}
SC = {"A": "V10 sola", "B": "W10 sola", "C": "**VW1**", "D": "VW1-flip (descartada)", "E": "50/50 en cuentas separadas"}
def g(tf, scen, seg, col, model="pine", cost="x1"):
    r = R[(R.tf == tf) & (R.modelo == model) & (R.costes == cost) & (R.escenario.str.startswith(scen + " ")) & (R.tramo == seg)]
    return float(r[col].iloc[0]) if len(r) else np.nan
def _es(t): return t.replace(",", "§").replace(".", ",").replace("§", ".")
def pct(x, d=0): return "—" if x != x else _es(f"{x*100:,.{d}f} %")
def num(x, d=2): return "—" if x != x else _es(f"{x:.{d}f}")
def table(head, rows): return "| " + " | ".join(head) + " |\n|" + "|".join(["---"] + ["---:"] * (len(head) - 1)) + "|\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows) + "\n"

def cal_wins(seg): return sum(g(tf, "C", seg, "calmar") > max(g(tf, "A", seg, "calmar"), g(tf, "B", seg, "calmar")) for tf in TFS)
CW = {seg: cal_wins(seg) for seg in ("TRAIN", "VAL", "OOS1", "OOS2")}
import re
L = []
L.append("# VW1 — backtest conjunto (LONG V10 + SHORT W10 en una sola cuenta)\n")
L.append("Fecha: 2026-11-24. Código y CSV: [`backtest_vw1/`](backtest_vw1/). Pre-registro (escrito antes de ejecutar): [`backtest_vw1/vw1_prereg.txt`](backtest_vw1/vw1_prereg.txt).\n")
f = lambda tf, k, **kw: g(tf, "C", "FULL", k, **kw)
L.append("## Veredicto\n")
L.append(f"""**Los dos perfiles casi no se estorban y, en la ventana completa, VW1 tiene mejor Calmar que cada uno por separado en las tres temporalidades. Pero esa ventaja está concentrada en 2017-2021 (TRAIN): fuera de muestra (2024-26) la rentabilidad es mayor, el Calmar no lo es siempre. Todo es simulación en Python; el test que falta es el de TradingView.**

- **V10 y W10 casi nunca están dentro a la vez** (con cuentas separadas coincidirían en {pct(O.t_solapado_si_fueran_cuentas_separadas.min(),1)}–{pct(O.t_solapado_si_fueran_cuentas_separadas.max(),1)} de las barras). Por eso la regla «una sola posición, sin invertir» cuesta poco: **0 entradas LONG perdidas** y **{pct(O.perdida_short.min(),1)}–{pct(O.perdida_short.max(),1)} de las SHORT** (según temporalidad).
- Al usar el mismo capital en momentos distintos, **las tasas de crecimiento se suman** y el drawdown apenas sube. Con costes 0,08 % por lado, 2017-08 → 2026-10: **1H {pct(f('1h','ret'))} / DD {pct(f('1h','mdd'),1)}; 4H {pct(f('4h','ret'))} / DD {pct(f('4h','mdd'),1)}; 1D {pct(f('1d','ret'))} / DD {pct(f('1d','mdd'),1)}.** Calmar de VW1 {num(f('1h','calmar'))} / {num(f('4h','calmar'))} / {num(f('1d','calmar'))} (V10 sola {num(g('1h','A','FULL','calmar'))} / {num(g('4h','A','FULL','calmar'))} / {num(g('1d','A','FULL','calmar'))}; W10 sola {num(g('1h','B','FULL','calmar'))} / {num(g('4h','B','FULL','calmar'))} / {num(g('1d','B','FULL','calmar'))}).
- **Los cinco criterios pre-registrados (C1–C5) se cumplen** en las tres temporalidades, también con costes ×2 y ×3. La variante con inversión de posición (VW1-flip) **no** supera el criterio y se descarta.
- **Tres matices que no se deben perder:** (1) **por tramos, el Calmar de VW1 supera al del mejor componente en {CW['TRAIN']}/3 temporalidades en TRAIN, {CW['VAL']}/3 en VAL, {CW['OOS1']}/3 en OOS1 y {CW['OOS2']}/3 en OOS2** (OOS1: 1H {num(g('1h','C','OOS1','calmar'))} vs {num(max(g('1h','A','OOS1','calmar'),g('1h','B','OOS1','calmar')))}; 4H {num(g('4h','C','OOS1','calmar'))} vs {num(max(g('4h','A','OOS1','calmar'),g('4h','B','OOS1','calmar')))}; 1D {num(g('1d','C','OOS1','calmar'))} vs {num(max(g('1d','A','OOS1','calmar'),g('1d','B','OOS1','calmar')))}). Este análisis por tramo no estaba en el pre-registro: se informa como hallazgo, no como criterio superado ni fallado. Fuera de muestra VW1 gana en rentabilidad (porque suma los dos lados) pero también sube el DD; por eso la mejora de calidad no está demostrada de forma independiente del periodo. (2) en **4H** el SHORT es el eslabón débil (W10 sola: Calmar {num(g('4h','B','FULL','calmar'))}, PF 1,5) y en OOS1 (2024→2026-01) VW1 4H rinde {pct(g('4h','C','OOS1','ret'),1)} frente a {pct(g('4h','A','OOS1','ret'),1)} de V10 sola, con DD {pct(g('4h','C','OOS1','mdd'),1)} frente a {pct(g('4h','A','OOS1','mdd'),1)}: casi no aporta ahí. (3) **El DD de VW1 es algo mayor que el de sus componentes** (entre {num(100*(-g('4h','C','FULL','mdd')-max(-g('4h','A','FULL','mdd'),-g('4h','B','FULL','mdd'))),1)} y {num(100*(-g('1d','C','FULL','mdd')-max(-g('1d','A','FULL','mdd'),-g('1d','B','FULL','mdd'))),1)} puntos porcentuales por encima del peor de los dos), y el remuestreo de operaciones sitúa el DD mediano en −26 % y el 5 % peor en −39 % / −41 %: planifica drawdowns de 35-45 %.
""")
L.append("## 1. Qué se ha medido\n")
L.append("""- **VW1** = LONG V10 (Donchian 140 h + EMA 800 h + filtro BTC > EMA 800 h, stop/trailing 5 ATR, TP 20 ATR, riesgo 5 %) + SHORT W10 (régimen EMA 600, ruptura de mínimos | pullback fallido, filtro de volatilidad, stop Chandelier; riesgo 1D 5 % / 4H 4 % / 1H 6 %). Mismos parámetros que sus versiones por separado; **no se ha tocado nada**.
- **Reglas del conjunto** (las del Pine VW1): una sola cuenta y una sola posición; con una posición abierta se ignoran las señales del lado contrario; si coinciden señal LONG y SHORT en la misma barra estando plano, no se opera.
- **Se compara con:** A = V10 sola, B = W10 sola (mismo motor, mismos costes), E = reparto 50/50 en dos cuentas independientes (referencia teórica: no es ejecutable en un solo gráfico) y D = VW1-flip (una única variante alternativa).
- **Datos:** ETH 1H/4H/1D de Binance (`csvs/`) 2017-08-17 → 2026-01-06 + tramo 2026-01 → 2026-10-03 de Twelve Data (el mismo que usó V10). **Tramos:** TRAIN 2017-08→2021-12, VAL 2022-23, OOS1 2024-01→2026-01-10, OOS2 2026-01-11→2026-10-03. Para el LONG no existe OOS virgen (V10 ya los había visto como descripción); para el SHORT, OOS2 no se había abierto antes y aquí solo se describe, no se ha usado para elegir nada.
- **Costes principales («pine»):** comisión 0,08 % por lado y slippage 0, sin funding: lo que declara el `strategy()` de VW1. Se repite con los costes originales de cada motor («orig») y con costes ×2 y ×3.
""")
L.append("## 2. Validación del motor\n")
L.append("Antes de medir nada conjunto, el motor se comprobó con un solo lado activo y las convenciones de cada motor original:\n")
rows = []
for r in V.itertuples():
    rows.append([r.lado, TFN[r.tf], pct(r.ref_ret, 2), pct(r.ref_mdd, 2), str(int(r.ref_n)), pct(r.vw_ret, 2), pct(r.vw_mdd, 2), str(int(r.vw_n)), f"{r.max_dif_equity:.0e}"])
L.append(table(["Lado", "TF", "Original: rent.", "DD", "ops", "Motor VW: rent.", "DD", "ops", "dif. máx. equity"], rows))
L.append("La curva de equity coincide a precisión de máquina con los motores `eng10` (V10) y `backtest_w11` (W10). Además, en las pruebas conjuntas: ninguna operación se solapa con otra, la equity final es el producto de los retornos de las operaciones (diferencia < 1e-14) y el tamaño nunca supera 2x.\n")

L.append("## 3. Resultados con costes 0,08 % por lado (modelo «pine»)\n")
L.append("Rentabilidad / drawdown máximo por tramo. Cada tramo se mide sobre la misma curva continua de equity.\n")
for tf in TFS:
    L.append(f"### {TFN[tf]}\n")
    rows = []
    for sc in ("A", "B", "C", "E"):
        rows.append([SC[sc]] + [f"{pct(g(tf, sc, s, 'ret'))} / {pct(g(tf, sc, s, 'mdd'), 1)}" for s in ("TRAIN", "VAL", "OOS1", "OOS2", "FULL")])
    L.append(table(["Escenario"] + [SEGN[s] for s in ("TRAIN", "VAL", "OOS1", "OOS2", "FULL")], rows))
L.append("**Calidad (ventana FULL 2017-08 → 2026-10, costes ×1):**\n")
rows = []
for tf in TFS:
    for sc in ("A", "B", "C", "E"):
        rows.append([TFN[tf], SC[sc], pct(g(tf, sc, "FULL", "cagr"), 1), pct(g(tf, sc, "FULL", "mdd"), 1), num(g(tf, sc, "FULL", "calmar")), num(g(tf, sc, "FULL", "pf")),
                     pct(g(tf, sc, "FULL", "win")), "—" if g(tf, sc, "FULL", "n") != g(tf, sc, "FULL", "n") else str(int(g(tf, sc, "FULL", "n"))), pct(g(tf, sc, "FULL", "expo"))])
L.append(table(["TF", "Escenario", "CAGR", "DD", "Calmar", "PF ($)", "Acierto", "Operaciones", "Tiempo en mercado"], rows))
L.append("(El 50/50 no tiene operaciones propias en una sola lista, de ahí los guiones.)\n")
L.append("**Calmar por tramo (VW1 frente a la mejor de las dos por separado):**\n")
rows = []
for tf in TFS:
    row = [TFN[tf]]
    for s in ("TRAIN", "VAL", "OOS1", "OOS2"):
        row.append(f"{num(g(tf,'C',s,'calmar'))} vs {num(max(g(tf,'A',s,'calmar'), g(tf,'B',s,'calmar')))}")
    rows.append(row)
L.append(table(["TF", "TRAIN", "VAL", "OOS1", "OOS2"], rows))
L.append(f"""OOS2 son solo ~9 meses: el Calmar anualizado de un tramo tan corto es indicativo, no concluyente. **Lectura:** el Calmar de VW1 supera al del mejor componente en {CW['TRAIN']}/3 TF en TRAIN, {CW['VAL']}/3 en VAL, {CW['OOS1']}/3 en OOS1 y {CW['OOS2']}/3 en OOS2. En 2024→2026-01 VW1 rinde más que cualquiera de los dos por separado en las tres TF, pero con un DD mayor (1H {pct(g('1h','C','OOS1','mdd'),1)}, 4H {pct(g('4h','C','OOS1','mdd'),1)}, 1D {pct(g('1d','C','OOS1','mdd'),1)}), y en 4H y 1D la rentabilidad extra no compensa ese DD. Es exactamente el tipo de mejora que la regla del proyecto manda no dar por buena sin más: la ventaja de Calmar de la ventana FULL viene sobre todo del TRAIN.\n""")

L.append("## 4. Solapamiento: qué cuesta la regla «una posición, sin invertir»\n")
rows = []
for r in O.itertuples():
    rows.append([TFN[r.tf], f"{r.n_V10_sola} → {r.n_long_VW1}", pct(r.perdida_long, 1), f"{r.n_W10_sola} → {r.n_short_VW1}", pct(r.perdida_short, 1), str(r.entradas_W10_con_V10_abierta), str(r.conflictos_misma_barra),
                 pct(r.t_en_mercado_V10, 0), pct(r.t_en_mercado_W10, 0), pct(r.t_solapado_si_fueran_cuentas_separadas, 1), pct(r.t_en_mercado_VW1, 0)])
L.append(table(["TF", "Ops LONG (sola → VW1)", "Pérdida", "Ops SHORT (sola → VW1)", "Pérdida", "Entradas SHORT con LONG abierto", "Conflictos misma barra", "Tiempo V10", "Tiempo W10", "Solape si fueran cuentas separadas", "Tiempo VW1"], rows))
L.append("""Todo el coste lo paga el SHORT. Explicación probable (no comprobada): una ruptura alcista de 140 h sobre la EMA 800 h suele llegar cuando un SHORT ya habría sido sacado por su stop, mientras que un SHORT nuevo sí puede aparecer con un LONG todavía abierto. De las operaciones de W10 sola, VW1 deja de tomar 24 / 26 / 17 (1H / 4H / 1D) y toma 11 / 12 / 7 que W10 sola no habría tomado (al estar plana antes, entra en señales que W10 sola no podía aprovechar): el saldo neto es el de la tabla.

**Eficiencia de la combinación:** si V10 y W10 corrieran en el mismo capital sin estorbarse, el resultado sería el producto de los dos multiplicadores. VW1 conserva """ + f"""{pct((1+g('1h','C','FULL','ret'))/((1+g('1h','A','FULL','ret'))*(1+g('1h','B','FULL','ret'))))} (1H), {pct((1+g('4h','C','FULL','ret'))/((1+g('4h','A','FULL','ret'))*(1+g('4h','B','FULL','ret'))))} (4H) y {pct((1+g('1d','C','FULL','ret'))/((1+g('1d','A','FULL','ret'))*(1+g('1d','B','FULL','ret'))))} (1D) de ese producto.
""")

L.append("## 5. Criterios pre-registrados\n")
rows = [[r.criterio, r.descripcion, "CUMPLE" if r.cumple else "NO CUMPLE", re.sub(r"(\d)\.(\d)", r"\1,\2", r.detalle)] for r in C.itertuples()]
L.append("| Criterio | Qué exige | Resultado | Detalle |\n|---|---|---|---|\n" + "\n".join("| " + " | ".join(x) + " |" for x in rows) + "\n")
L.append("""**Lectura honesta de C2 y C3:** son criterios laxos por construcción (dos estrategias que operan en momentos distintos casi siempre suman más que cada una por separado). C2 usa la ventana FULL, dominada por TRAIN (ver el Calmar por tramo del apartado 3). Lo que de verdad dicen algo es C1 (el solapamiento cuesta poco), C4 (aguanta costes ×3) y C5 (el DD no se dispara). Con 4H en OOS1 el criterio C3 se cumple por muy poco (+77,5 % frente a +72,3 %).
""")

L.append("## 6. Robustez adicional\n")
L.append("**Costes (modelo «pine», ventana FULL): rentabilidad / DD / Calmar**\n")
rows = []
for tf in TFS:
    for sc in ("A", "B", "C"):
        rows.append([TFN[tf], SC[sc]] + [f"{pct(g(tf, sc, 'FULL', 'ret', cost=c))} / {pct(g(tf, sc, 'FULL', 'mdd', cost=c), 1)} / {num(g(tf, sc, 'FULL', 'calmar', cost=c))}" for c in ("x1", "x2", "x3")])
L.append(table(["TF", "Escenario", "Costes ×1 (0,08 %)", "×2 (0,16 %)", "×3 (0,24 %)"], rows))
L.append("**Costes originales de cada motor («orig»: LONG 6 pb + 6 pb con stop de slippage doble y funding; SHORT 5 pb + 3 pb) — rentabilidad / DD / Calmar, ventana FULL:**\n")
rows = []
for tf in TFS:
    rows.append([TFN[tf]] + [f"{pct(g(tf, sc, 'FULL', 'ret', model='orig'))} / {pct(g(tf, sc, 'FULL', 'mdd', model='orig'), 1)} / {num(g(tf, sc, 'FULL', 'calmar', model='orig'))}" for sc in ("A", "B", "C")])
L.append(table(["TF", "V10 sola", "W10 sola", "VW1"], rows))
L.append("**Remuestreo de operaciones** (5.000 reordenaciones con reemplazo de las operaciones de la ventana ORIG; asume operaciones independientes, que es una simplificación):\n")
rows = [[TFN[r.tf], r.escenario, str(r.n), pct(r.dd_p50, 1), pct(r.dd_p5, 1), pct(r.ret_p5), pct(r.ret_p50)] for r in B.itertuples()]
L.append(table(["TF", "Escenario", "Ops", "DD mediano", "DD (percentil 5 % peor)", "Rent. (percentil 5 %)", "Rent. mediana"], rows))
L.append("**Retorno por año (modelo «pine», costes ×1):**\n")
rows = []
for yr in Y.index:
    row = [str(yr)]
    for tf in TFS:
        row += [pct(Y.loc[yr, f"{tf} | V10 sola"]), pct(Y.loc[yr, f"{tf} | W10 sola"]), pct(Y.loc[yr, f"{tf} | VW1"])]
    rows.append(row)
L.append(table(["Año"] + [f"{TFN[tf]} {n}" for tf in TFS for n in ("V10", "W10", "VW1")], rows))
L.append("2017 es parcial (desde agosto) y 2026 llega hasta el 3 de octubre. En varios años alcistas VW1 rinde algo menos que V10 sola (4H 2020-21 y 2025; 1D 2020-21; 1H 2025): es el precio de incluir los SHORT perdedores de esos años.\n")

L.append("## 7. Variante VW1-flip (descartada)\n")
L.append("Invierte la posición cuando aparece la señal contraria con una posición abierta. Era una única variante, sin parámetros nuevos, con el criterio fijado de antemano: superar a VW1 en Calmar en TRAIN, VAL y OOS1 a la vez en ≥2 de 3 TF. " + C[C.criterio == "D"].detalle.iloc[0] + ". **No lo cumple**; además empeora el DD en FULL (1H −27,8 % vs −24,8 %, 4H −27,0 % vs −26,6 %, 1D −33,9 % vs −27,5 %) y el Calmar FULL en 1H y 1D. Se descarta y no se reabre. Esto no dice que invertir sea malo en general, solo que con las reglas actuales no aporta de forma consistente.\n")

L.append("## 8. Cifras para comparar con TradingView\n")
L.append("Resultado esperado del Python para VW1 (modelo «pine»: comisión 0,08 %, slippage 0). **No esperes que TradingView dé exactamente lo mismo**: otros datos de velas, otro emulador de órdenes (p. ej. el stop del LONG no vale en la barra de relleno, la toma parcial del SHORT en 1H) e indicadores con semilla ligeramente distinta. Sí deberías ver el mismo orden de magnitud de operaciones y de DD. Pon el rango del gráfico en 2017-08-17 en adelante (VW1 ya filtra por ese inicio, así que en 1D no entrarán las operaciones de 2015-2017 que sí aparecen en V10 sola).\n")
rows = []
for tf in TFS:
    for seg in ("ORIG", "FULL"):
        rows.append([TFN[tf], "2017-08-17 → 2026-01-10" if seg == "ORIG" else "2017-08-17 → 2026-10-03", pct(g(tf, "C", seg, "ret")), pct(g(tf, "C", seg, "mdd"), 1), f"{int(g(tf,'C',seg,'n'))} ({int(g(tf,'C',seg,'n_long'))} L / {int(g(tf,'C',seg,'n_short'))} S)", num(g(tf, "C", seg, "pf")), pct(g(tf, "C", seg, "win"))])
L.append(table(["TF", "Ventana", "Rentabilidad", "DD máx.", "Operaciones", "PF ($)", "Acierto"], rows))
L.append("Con los costes de cada motor original («orig»), que incluyen funding en el LONG y slippage, el resultado FULL baja a " + ", ".join(f"{TFN[tf]} {pct(g(tf,'C','FULL','ret',model='orig'))}" for tf in TFS) + ".\n")

L.append("## 9. Limitaciones\n")
L.append("""- **Todo es simulación en Python con las convenciones de los motores originales.** El Pine VW1 no se ha compilado ni ejecutado en TradingView; la comparación del apartado 8 es justamente el test que falta.
- **Los parámetros de V10 y W10 se eligieron con datos de TRAIN/VAL (y, en el caso del LONG, el OOS ya se había visto).** Que VW1 sume los dos no elimina ese sesgo; solo los junta. La parte de la rentabilidad que viene de 2017-2021 (TRAIN) es la menos creíble como expectativa futura: en OOS1 VW1 hace +157 % (1H), +77 % (4H) y +113 % (1D), y en OOS2 +31 % / +21 % / −4 %.
- **La rentabilidad total mostrada es enorme porque compone dos ventajas en la misma cuenta durante 9 años con riesgo por operación del 4-6 %.** No la tomes como expectativa: usa Calmar, DD y los tramos OOS. El 5 % peor del remuestreo de DD es −39 % a −41 %.
- **4H:** el SHORT de 4H es el más débil de W10 (PF 1,5, evidencia no robusta al cambiar el percentil); en 2024-2026 VW1 4H apenas mejora a V10 sola. **1D:** pocas operaciones por tramo (el OOS1 de 1D tiene 27 operaciones LONG y 15 SHORT) y V10 1D depende del ancla del día; W10 1D con evidencia débil.
- **Costes:** sin funding en el SHORT (los dos motores originales no lo modelan) ni deslizamiento realista en capitulaciones; con costes ×3 VW1 sigue con Calmar > 1, pero eso no sustituye a datos reales.
- **Posición única:** si algún día se quiere que el SHORT pueda entrar con el LONG abierto (hoy cuesta 6,5-9 % de sus entradas), hace falta una cuenta/estrategia separada o cubrir en otro instrumento; en un solo gráfico de TradingView la posición es neta.
- **El 2026 de W10 es coherente con lo que viste en TradingView:** W10 sola en 1H hace −22,9 % de DD en 2026-01→10, parecido al −21 % de W9 que mencionaste.
""")
L.append("## 10. Archivos\n")
L.append("""- `backtest_vw1/eng_vw.py` (motor conjunto), `prep_vw.py` (señales con el código original de V10 y W10, métricas), `validate_vw1.py`, `run_vw1.py`, `criterios_vw1.py`, `mk_informe_vw1.py`, `vw1_prereg.txt`, `oos_access_log.txt`.
- CSV: `resultados_VW1.csv` (todos los escenarios × tramos × costes), `solapamiento_VW1.csv`, `bootstrap_VW1.csv`, `retorno_anual_VW1.csv`, `criterios_VW1.csv`, `validacion_motor.csv`.
- Reproducir: `pip install numba pandas numpy scipy` y, desde `backtest_vw1/`, `python validate_vw1.py && python run_vw1.py && python criterios_vw1.py && python mk_informe_vw1.py`. Las rutas se calculan desde la ubicación del script.
""")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
print("OK", OUT)
