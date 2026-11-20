# V11 (filtros macro sobre V10) — informe

## 1. Conclusión

**V11 = V10 en lógica. Ningún filtro macro mejora la estrategia, y todos la empeoran.** Probé 7 variantes (21 pruebas = variantes × 3 temporalidades) con el Nasdaq y el índice del dólar, con las reglas fijadas por escrito **antes** de ejecutarlas (`v11_prereg.txt`) y evaluadas contra V10 solo con TRAIN y VAL en ETH + BTC + DOGE. **0 de 21 pasaron el criterio.** No se abrió ningún holdout y no se cambia nada en el Pine.

- **En VAL (2022-23) las 21 pruebas empeoran el Calmar de ETH** (entre −0,44 y −1,92). En TRAIN solo 4 de 21 mejoran, y ninguna de esas cuatro mejora a la vez BTC y DOGE.
- **El filtro actúa mucho** (bloquea entre el 20 % y el 63 % de las barras, según la variante), así que no es que no funcione: es que quita entradas buenas.
- Sobre la ventana completa (2017-08 → 2026-10, descriptivo) el Calmar baja en todas las temporalidades y variantes: 1H de 1,60 a 0,33-1,13; 4H de 1,72 a 0,27-1,15; 1D de 0,91 a 0,40-0,75.
- **Opción 3 (funding, diagnóstico):** no hay ninguna relación fiable entre el funding previo a la entrada y el resultado. Con 27-38 operaciones por temporalidad y p-valores de 0,12 a 0,93, no se puede concluir nada, y además el funding de este periodo casi no tuvo valores altos positivos (ver sección 5).

Esto no cambia lo que ya sabíamos: V10 está en un óptimo local y la información extra de precios o macro que he probado no lo mejora. Es un resultado útil: con las pruebas hechas, esta línea queda descartada.

## 2. Datos usados y cómo se evitó mirar al futuro

- **Nasdaq Composite** diario (2017-01-03 → 2026-11-19), de tu CSV. Los cierres coinciden con los que consulté de FMP, y el archivo pasó la comprobación de integridad (2.485 filas, sin huecos ni duplicados).
- **Dólar**: no usé el ETF UUP de tu CSV porque viene **sin ajustar por los repartos del fondo** y tiene caídas artificiales del −1,5 % al −6 % en diciembre (2018, 2019, 2023, 2024 y 2025). Construí en su lugar un **DXY sintético** con los pesos oficiales del DXY (euro 57,6 %, yen 13,6 %, libra 11,9 %, dólar canadiense 9,1 %, corona sueca 4,2 %, franco suizo 3,6 %) a partir de tipos de cambio diarios de Alpha Vantage. Correlación de retornos diarios con el UUP (sin los días de reparto): 0,957. Nivel el 27/09/2022: 114,2, coherente con el máximo de ese año (~114). Es una aproximación: no pude obtener el DXY oficial con las herramientas disponibles.
- **Sin mirar al futuro:** el dato macro de un día solo se considera conocido a partir de las 00:00 UTC del día siguiente (la bolsa de EE. UU. cierra sobre las 21:00 UTC). Cada barra cripto usa el último dato disponible en su hora de cierre. Comprobado en `test11.py` (60 barras al azar recalculadas con datos truncados, 0 discrepancias) y en `verify11.py` (4.198 operaciones revisadas, 0 abiertas con el filtro en contra).
- Donde falta historia para la media (por ejemplo la SMA 200 del Nasdaq antes de octubre de 2017), el filtro no actúa. Afecta a unos 2 meses de 2017.

## 3. Qué se probó (`experimentos_V11.csv`)

Filtros de entrada sobre V10 (que ya incluye el filtro BTC > EMA 800 h). Parámetros de 100 y 200 días por convención, sin optimizar:
- **M1** Nasdaq por encima de su SMA de L días.
- **M2** DXY por debajo de su SMA de L días.
- **M3** las dos condiciones a la vez.
- **M4** en vez de bloquear, riesgo × 0,5 cuando no se cumple M3 (L = 200).

Criterio por temporalidad, igual que en V9/V10: ΔCalmar de ETH > 0 en TRAIN y VAL; BTC y DOGE ≥ 0; ΔDD de ETH mejor que −1 pp; ΔR/operación de ETH > 0. Reglas anti-falso-positivo R1-R3 de V10.

| Variante | TF | ΔCalmar ETH TRAIN | ΔCalmar ETH VAL | ΔCalmar BTC | ΔCalmar DOGE | ΔDD ETH (pp) | ΔR/op ETH | ¿Pasa? |
|---|---|---|---|---|---|---|---|---|
| NQ>SMA100 | 1H | -0,15 | -1,12 | -0,66 | -0,44 | -4,1 | -0,047 | no |
| NQ>SMA100 | 4H | +0,05 | -1,74 | -0,25 | -0,49 | +1,2 | -0,061 | no |
| NQ>SMA100 | 1D | -0,27 | -0,98 | +0,04 | +0,10 | -0,4 | -0,034 | no |
| NQ>SMA200 | 1H | -0,11 | -0,86 | -0,32 | -0,18 | -1,8 | -0,009 | no |
| NQ>SMA200 | 4H | +0,47 | -1,37 | +0,11 | -0,27 | +1,7 | +0,017 | no |
| NQ>SMA200 | 1D | +0,23 | -0,56 | -0,06 | +0,06 | +0,1 | +0,047 | no |
| USD<SMA100 | 1H | -1,19 | -0,71 | -0,72 | -0,20 | -1,3 | -0,059 | no |
| USD<SMA100 | 4H | -1,55 | -1,06 | -0,50 | -0,09 | +1,7 | -0,129 | no |
| USD<SMA100 | 1D | -0,54 | -0,44 | -0,12 | -0,09 | +3,0 | +0,106 | no |
| USD<SMA200 | 1H | -0,55 | -0,76 | -0,70 | +0,56 | -3,0 | -0,018 | no |
| USD<SMA200 | 4H | -1,41 | -1,27 | -0,55 | +0,60 | +1,2 | -0,126 | no |
| USD<SMA200 | 1D | -0,26 | -0,63 | -0,23 | +0,57 | -0,4 | +0,111 | no |
| NQ&USD 100 | 1H | -1,19 | -1,13 | -0,94 | -0,27 | -3,9 | -0,118 | no |
| NQ&USD 100 | 4H | -1,55 | -1,60 | -0,66 | -0,36 | +1,7 | -0,176 | no |
| NQ&USD 100 | 1D | -0,43 | -0,78 | -0,30 | -0,12 | +3,0 | +0,067 | no |
| NQ&USD 200 | 1H | -0,55 | -1,22 | -1,05 | +0,41 | -9,3 | -0,084 | no |
| NQ&USD 200 | 4H | -1,41 | -1,92 | -0,85 | +0,55 | -5,3 | -0,194 | no |
| NQ&USD 200 | 1D | -0,26 | -1,06 | -0,51 | +0,55 | -0,3 | +0,069 | no |
| tamano x0,5 NQ&USD200 | 1H | +0,08 | -0,66 | -0,58 | +0,36 | +0,7 | -0,000 | no |
| tamano x0,5 NQ&USD200 | 4H | -0,75 | -0,96 | -0,40 | +0,61 | +1,7 | -0,000 | no |
| tamano x0,5 NQ&USD200 | 1D | -0,09 | -0,62 | -0,17 | +0,17 | +1,4 | -0,000 | no |

Lectura:
- **Nasdaq (M1):** mejora algo TRAIN en 4H (+0,05 y +0,47) y en 1D con L = 200 (+0,23), pero hunde VAL (−0,56 a −1,74) y empeora BTC o DOGE. Posible explicación, no comprobada: la SMA 200 del Nasdaq reacciona tarde y bloquea el rebote de ETH de principios de 2023.
- **Dólar (M2):** empeora TRAIN y VAL en 1H y 4H. En 1D mejora el R por operación (+0,11) y, con L = 100, el DD (+3,0 pp), pero a costa del Calmar en TRAIN (−0,26 a −0,54).
- **Ambos (M3):** es lo peor, porque bloquea entre el 58 % y el 63 % de las barras y deja 56-75 operaciones en vez de 105-143.
- **Tamaño en vez de filtro (M4):** es la versión más suave y tampoco pasa. Reduce algo el DD (de 1,3 a 3,5 pp, según la temporalidad), pero el Calmar cae (1H 1,09; 4H 1,11; 1D 0,73, frente a 1,60; 1,72 y 0,91).
- **Con 21 pruebas se esperarían 1-2 aprobadas por azar; salieron 0.** No hay ni siquiera un falso positivo que descartar.

## 4. Comparación descriptiva sobre la ventana completa (ETH, 2017-08-17 → 2026-10-03, riesgo 5 %)

No se usó para elegir nada (se hizo después de ver que 0 de 21 pasaban) e incluye 2024-2026, ya conocido de V8-V10.

| TF | Variante | Rentabilidad | CAGR | DD | Calmar | Operaciones | Win rate | PF | Barras bloqueadas |
|---|---|---|---|---|---|---|---|---|---|
| 1H | V10 (sin macro) | 1.431 % | 34,8 % | -21,8 % | 1,60 | 143 | 42,7 % | 2,41 | 0 % |
| 1H | NQ>SMA100 | 664 % | 25,0 % | -24,5 % | 1,02 | 126 | 40,5 % | 2,13 | 25 % |
| 1H | NQ>SMA200 | 771 % | 26,8 % | -23,7 % | 1,13 | 128 | 40,6 % | 2,21 | 20 % |
| 1H | USD<SMA100 | 481 % | 21,3 % | -21,0 % | 1,01 | 77 | 45,5 % | 2,91 | 55 % |
| 1H | USD<SMA200 | 296 % | 16,3 % | -27,7 % | 0,59 | 79 | 43,0 % | 2,37 | 54 % |
| 1H | NQ&USD 100 | 302 % | 16,5 % | -23,5 % | 0,70 | 74 | 44,6 % | 2,56 | 63 % |
| 1H | NQ&USD 200 | 161 % | 11,1 % | -33,5 % | 0,33 | 75 | 40,0 % | 1,98 | 58 % |
| 1H | tamano x0,5 NQ&USD200 | 519 % | 22,1 % | -20,2 % | 1,09 | 143 | 42,7 % | 2,23 | 58 % |
| 4H | V10 (sin macro) | 1.011 % | 30,2 % | -17,6 % | 1,72 | 126 | 43,7 % | 2,54 | 0 % |
| 4H | NQ>SMA100 | 473 % | 21,1 % | -24,9 % | 0,85 | 110 | 43,6 % | 2,20 | 25 % |
| 4H | NQ>SMA200 | 616 % | 24,1 % | -24,9 % | 0,97 | 111 | 43,2 % | 2,39 | 20 % |
| 4H | USD<SMA100 | 283 % | 15,8 % | -13,8 % | 1,15 | 73 | 42,5 % | 2,55 | 55 % |
| 4H | USD<SMA200 | 189 % | 12,3 % | -21,7 % | 0,57 | 75 | 41,3 % | 2,15 | 54 % |
| 4H | NQ&USD 100 | 180 % | 11,9 % | -17,8 % | 0,67 | 69 | 43,5 % | 2,23 | 63 % |
| 4H | NQ&USD 200 | 97 % | 7,7 % | -28,3 % | 0,27 | 70 | 40,0 % | 1,76 | 58 % |
| 4H | tamano x0,5 NQ&USD200 | 354 % | 18,0 % | -16,3 % | 1,11 | 126 | 43,7 % | 2,22 | 58 % |
| 1D | V10 (sin macro) | 483 % | 21,3 % | -23,4 % | 0,91 | 105 | 44,8 % | 2,15 | 0 % |
| 1D | NQ>SMA100 | 252 % | 14,8 % | -21,9 % | 0,67 | 91 | 44,0 % | 1,96 | 25 % |
| 1D | NQ>SMA200 | 315 % | 16,9 % | -25,4 % | 0,66 | 92 | 44,6 % | 2,07 | 20 % |
| 1D | USD<SMA100 | 239 % | 14,3 % | -19,2 % | 0,75 | 59 | 47,5 % | 2,51 | 55 % |
| 1D | USD<SMA200 | 236 % | 14,2 % | -20,2 % | 0,70 | 61 | 44,3 % | 2,38 | 54 % |
| 1D | NQ&USD 100 | 153 % | 10,7 % | -26,8 % | 0,40 | 56 | 48,2 % | 2,21 | 63 % |
| 1D | NQ&USD 200 | 141 % | 10,1 % | -23,8 % | 0,43 | 57 | 43,9 % | 2,06 | 58 % |
| 1D | tamano x0,5 NQ&USD200 | 242 % | 14,4 % | -19,9 % | 0,73 | 105 | 44,8 % | 2,04 | 58 % |

En la variante de tamaño, "barras bloqueadas" son las barras con riesgo × 0,5 (no se bloquea ninguna entrada, por eso mantiene las mismas operaciones que V10).

## 5. Opción 3: funding de ETH (diagnóstico, no selecciona reglas)

Archivo del usuario: 5.197 registros de 4 horas entre 2024-03-18 y 2026-10-31. **Faltan tres meses completos (abril 2024, julio 2024 y abril 2025) y un registro en junio de 2026**, y no hay nada anterior a marzo de 2024. Por eso solo cubre ~2,6 años, y estos años ya no son vírgenes (se usaron en V8-V10).

Para cada operación de V10 en el periodo, miré el funding medio de las 24 horas previas a la entrada (se descartaron 3 operaciones por TF sin al menos 4 registros previos) y comparé "funding alto" (cuartil superior) con el resto:

| TF | Operaciones | Win rate | Win rate con funding alto (cuartil superior) | Win rate resto | Retorno medio funding alto | Retorno medio resto | Correlación (Spearman) | p |
|---|---|---|---|---|---|---|---|---|
| 1D | 27 | 29,6 % | 16,7 % (n=12) | 40,0 % | -1,36 % | +0,78 % | -0,23 | 0,26 |
| 1H | 38 | 39,5 % | 41,7 % (n=12) | 38,5 % | +0,35 % | +0,79 % | -0,02 | 0,93 |
| 4H | 33 | 42,4 % | 36,4 % (n=11) | 45,5 % | -0,24 % | +1,96 % | -0,28 | 0,12 |

Lectura:
- **No hay relación detectable.** Las diferencias van en sentidos distintos según la temporalidad y ningún p-valor baja de 0,12. Con 27-38 operaciones, una diferencia real pequeña no se vería.
- **Limitación importante:** en este periodo el funding estuvo casi siempre en su suelo (mediana y percentil 90: 0,005 % por 4 h) y los valores altos positivos son raros (máximo +0,078 %). Los extremos que hay son más bien negativos (mínimo −0,16 %). La hipótesis de partida ("funding muy alto = ruptura trampa") no se puede poner a prueba con estos datos porque casi no ocurrió.
- **Conclusión:** no hay base para añadir una regla de funding. Para probarla de verdad harían falta años con funding alto (2020-2021), que este archivo no tiene.

## 6. Qué NO puedo afirmar

- **No hay OOS virgen:** 2024-2026 se conocía de V8-V10. Por eso todas las decisiones se tomaron solo con TRAIN/VAL y los holdouts no se abrieron (`oos_access_log11.txt`).
- Probé un conjunto pequeño de filtros macro (Nasdaq y dólar, medias de 100 y 200 días). Otras formas de usar la misma información (momentum, volatilidad macro, tipos de interés, VIX) no se probaron y no se pueden descartar; pero se pre-registraron solo estas para no multiplicar pruebas.
- El DXY sintético es una aproximación. Con el DXY oficial los resultados serían casi idénticos (correlación 0,957 con el UUP limpio), pero no puedo asegurar cada decimal.
- El resultado del funding depende de un archivo incompleto.
- No se ha tocado el Pine, así que sigue sin compilarse en TradingView desde aquí.

## 7. Siguientes pasos razonables

1. **Verificar en TradingView el filtro BTC con el panel de V10** (pendiente de V10): es lo que explicaría la diferencia de tu +366 % en 1D frente a mi +483 %. Si no puedes exportar la lista de operaciones, copia las primeras 15-20 filas de "Lista de operaciones" del 1D como texto o captura.
2. **Probar la misma lógica en otros activos líquidos** (SOL, BNB, LINK, XRP, ADA, LTC) como validación independiente. Dices que en otros activos unas veces gana y otras pierde; tiene sentido medirlo bien con el mismo método para calibrar qué esperar de ETH.
3. **Decidir el riesgo operativo.** Si el objetivo es un DD de 10-15 %, el preset de riesgo de V10 (1H 3,3 %, 4H 4,2 %, 1D 3,0 %) es la vía honesta; no mejora el Calmar, pero fija el DD.
4. **Repetir en 6-12 meses** cuando haya un OOS genuino.

## 8. Archivos
`informe_V11.md`, `v11_prereg.txt`, `experimentos_V11.csv`, `descriptivo_V11_ETH.csv`, `diagnostico_funding_V11.csv`, `funding_por_operacion_V11.csv`, `oos_access_log11.txt`, `macro_daily.csv` (Nasdaq, UUP y DXY sintético), y el código: `mk_macro.py` (construye el DXY), `exp11.py` (arnés), `round11a.py` (ronda), `test11.py` y `verify11.py` (comprobaciones), `desc11.py`, `funding11.py`. Se ejecutan sobre `backtest_v10/` del repo (motor `eng10.py` y arnés `exp9.py`/`exp10.py` sin cambios).
