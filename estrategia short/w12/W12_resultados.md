# W12 — intento de mejora sobre W11: **sin mejora robusta, no se crea Pine W12**

**Veredicto:** ninguna de las ideas probadas (enfriamiento tras pérdida, filtro de lateralidad, filtro de pendiente de la EMA de régimen) mejora a W10/W11 de forma robusta en los tramos de desarrollo, así que **W11 sigue siendo la versión vigente y no hay `W12_ETH_short.pine`**. Además, con datos nuevos (2026) **W11 no confirma su ventaja sobre W10** (ver más abajo): tratar W11 como «mejor que W10» con cautela.

## Datos y motor
- **Motor:** `backtest_w12.py` = el de `backtest_w11.py` + costes parametrizables + tramo `HOLDOUT26` + ganchos para las hipótesis. **Calibración exacta:** con costes antiguos (0,05 % + 0,03 %) y datos hasta 2026-01-06 reproduce todas las cifras de `W11_resultados.md` (p. ej. 1D W11 TOTAL +818,02 %, DD −20,50 %, PF 2,50, 105 ops).
- **Costes de las tablas de las secciones anteriores a «Con el slippage confirmado»:** comisión 0,06 % por lado, **slippage 0**, cantidad calculada al cierre de la señal. El usuario confirmó después **slippage 0,06 % por lado**; esa sección repite la línea base y la rejilla con los costes definitivos y **las conclusiones no cambian**.
- **Datos:** Binance ETHUSDT hasta 2026-01-06 + extensión hasta noviembre de 2026 en `csvs/ext2026/` (1H y 4H: Twelve Data ETH/USD; 1D: Alpha Vantage ETH/USD; ver `build_ext_data.py`). La última vela de Binance estaba incompleta y la sustituye la completa. Sin huecos.
- **`HOLDOUT26` (2026-01-07 → 2026-11-20):** W10 y W11 se diseñaron con datos hasta 2026-01-06, así que este tramo es un test fuera de muestra real para ellas. Entre 27 y 37 operaciones por temporalidad: poca muestra.

## Hallazgo 1 — W11 no mejora a W10 en datos nuevos
Costes TradingView, datos extendidos, equity continua. Desarrollo = hasta 2026-01-10.

| TF | Versión | Desarrollo: Rentab. · DD · PF | **2026 (holdout)**: Rentab. · DD · PF · WR · Ops | Todo 2017-08 → 2026-11: Rentab. · DD |
|---|---|---|---|---|
| 1D | W10 | +533,9 % · −20,4 % · 2,25 | **−8,7 %** · −24,4 % · 0,86 · 26,9 % · 26 | +472,9 % · −24,4 % |
| 1D | W11 | +874,4 % · −20,2 % · 2,56 | **−14,8 %** · −26,5 % · 0,75 · 29,6 % · 27 | +721,5 % · −26,5 % |
| 4H | W10 | +436,6 % · −24,0 % · 1,55 | **+13,1 %** · −21,9 % · 1,22 · 27,8 % · 36 | +498,2 % · −26,0 % |
| 4H | W11 | +547,1 % · −20,6 % · 1,63 | **+11,2 %** · −21,9 % · 1,19 · 27,0 % · 37 | +608,9 % · −22,7 % |
| 1H | W10 (riesgo 6 %) | +955,8 % · −17,3 % · 2,26 | **+22,2 %** · −24,5 % · 1,44 · 43,8 % · 32 | +1.158,5 % · −24,5 % |
| 1H | W11 (riesgo 5,5 %) | +1.219,4 % · −17,6 % · 2,29 | **+20,4 %** · −26,7 % · 1,37 · 37,5 % · 32 | +1.455,3 % · −26,7 % |

W11 queda por debajo de W10 en las tres temporalidades en 2026 (y con más DD en 1D y 1H). Con 27–37 operaciones la diferencia no es concluyente en ninguna dirección, pero **la mejora de W11 sobre W10 solo está confirmada en el periodo con el que se diseñó**. También: en 2026 las dos pierden en 1D y apenas ganan en 4H, aunque en 1H ganan.

## Hallazgo 2 — el problema de 2026 no son rachas, es el win rate
Win rate (%) de W11 en desarrollo frente a 2026, y tras una pérdida frente a tras una ganancia (CSV en `diag12.py`):

| TF | WR desarrollo → 2026 | Desarrollo: tras pérdida / tras ganancia | 2026: tras pérdida / tras ganancia | Pérdida media · ganancia media (desarrollo → 2026) |
|---|---|---|---|---|
| 1D | 54,3 → **29,6** | 57,4 / 50,9 | 31,6 / 25,0 | −3,2 % · +7,2 % → −3,1 % · +5,8 % |
| 4H | 43,9 → **27,0** | 46,2 / 40,2 | 25,9 / 30,0 | −2,0 % · +5,1 % → −1,9 % · +6,7 % |
| 1H | 50,4 → **37,5** | 47,4 / 52,6 | 40,0 / 33,3 | −2,7 % · +7,6 % → −2,4 % · +5,9 % |

Una pérdida **no** predice otra (el win rate tras pérdida es igual o mayor que tras ganancia, también en 2026). El tamaño de ganancias y pérdidas casi no cambia: lo que cae es la proporción de operaciones que funcionan. En 1D, el 66–79 % de las pérdidas se cierran en 2 barras o menos, tanto en desarrollo como en 2026. **La hipótesis del enfriamiento no tiene respaldo en los datos.**

## Rejilla de hipótesis (selección solo con TRAIN / VALIDATION / OOS)
Bases W10 y W11; 24 variantes por temporalidad y base; costes TradingView. Criterio de mejora: **CAGR/DD estrictamente mayor que la base en cada uno de los tres tramos**. El holdout de 2026 **no se midió** para ninguna variante.

| Hipótesis | Rejilla (longitudes en barras de 4H) | Variantes que mejoran 3/3 · 2/3 · total (1D · 4H · 1H, ambas bases) |
|---|---|---|
| Enfriamiento tras pérdida | 6, 12, 24, 48 barras × 1 o 2 pérdidas seguidas | 1D: 0 · 2 · 16 / 4H: 0 · 5 · 16 / 1H: 0 · 5 · 16 |
| Lateralidad (ER de Kaufman ≥ umbral) | n 45, 90 × umbral 0,10 / 0,15 / 0,20 / 0,30 | 1D: 0 · 4 · 16 / 4H: 0 · 3 · 16 / 1H: 0 · 0 · 16 |
| Pendiente de la EMA de régimen ≤ −X | n 90, 180 × X 0 / 0,02 / 0,05 / 0,10 | 1D: 0 · 3 · 16 / 4H: 0 · 0 · 16 / 1H: 0 · 0 · 16 |

**Ninguna variante mejora en los tres tramos.** Las que mejoran en 2 de 3 no forman un vecindario coherente (al variar el parámetro, el resultado salta o empeora). Ejemplo, el mejor caso aislado (1D, W11, enfriamiento de 2 días tras una pérdida) frente a sus vecinos:

| Enfriamiento (1D) | Rentab. total | DD | n ops | CAGR/DD TRAIN · VALID · OOS |
|---|---:|---:|---:|---|
| ninguno (W11) | +874 % | −20,2 % | 105 | 1,69 · 1,73 · 4,96 |
| 1 día | +942 % | −19,8 % | 104 | 1,69 · 1,99 · 4,96 |
| **2 días** | **+968 %** | **−16,0 %** | **100** | 1,72 · 2,49 · 4,96 |
| 4 días | +765 % | −14,9 % | 92 | 1,08 · 3,60 · 4,96 |
| 8 días | +548 % | −18,4 % | 85 | 1,68 · 2,26 · 2,72 |

La mejora de 2 días sale de **5 operaciones que se dejan de hacer**, no es monótona, el OOS no cambia y con 2 pérdidas seguidas empeora. No se adopta.

## Con el slippage confirmado (comisión 0,06 % + slippage 0,06 % por lado)
El usuario confirmó el slippage cuando las secciones anteriores ya estaban hechas (con slippage 0). Misma línea base y misma rejilla con los costes definitivos (`--slip 0.0006`, valor por defecto de los scripts; `--slip 0` reproduce las tablas anteriores).

| TF | Versión | Desarrollo: Rentab. · DD · PF | 2026 (holdout): Rentab. · DD · PF · WR · Ops |
|---|---|---|---|
| 1D | W10 | +453,4 % · −21,0 % · 2,09 | −12,8 % · −25,8 % · 0,80 · 26,9 % · 26 |
| 1D | W11 | +737,3 % · −21,1 % · 2,37 | −19,2 % · −29,3 % · 0,68 · 29,6 % · 27 |
| 4H | W10 | +361,3 % · −25,1 % · 1,48 | +8,9 % · −22,8 % · 1,15 · 25,0 % · 36 |
| 4H | W11 | +447,2 % · −21,8 % · 1,54 | +6,7 % · −22,8 % · 1,11 · 24,3 % · 37 |
| 1H | W10 (riesgo 6 %) | +807,8 % · −18,4 % · 2,12 | +15,5 % · −26,2 % · 1,29 · 43,8 % · 32 |
| 1H | W11 (riesgo 5,5 %) | +1.048,2 % · −18,7 % · 2,16 | +14,3 % · −29,4 % · 1,25 · 34,4 % · 32 |

- El slippage recorta la rentabilidad total de W11 de +874 % a +737 % en 1D, de +547 % a +447 % en 4H y de +1.219 % a +1.048 % en 1H.
- **W11 sigue por debajo de W10 en 2026 en las tres temporalidades.**
- **Rejilla:** 0 variantes mejoran en los tres tramos de desarrollo. Mejoran en 2 de 3 (de 16 por celda): enfriamiento 1D 2 · 1H 5 · 4H 7; lateralidad (ER) 1D 4 · 1H 0 · 4H 3; pendiente 1D 5 · 1H 0 · 4H 0. Misma conclusión que con slippage 0.

## Qué no está probado / advertencias
- **El holdout de 2026 no es virgen para el diseño de W12:** la idea de lateralidad/enfriamiento nació de ver cómo se comportaron W8/W9 en 2026. Por eso la selección se hizo solo con datos hasta 2026-01-10 y 2026 queda **sin tocar** para cualquier variante futura.
- **No he probado cambios estructurales de la entrada o la salida** (solo tres hipótesis). Una búsqueda más amplia (estructuras distintas de entrada, validación walk-forward con control de comparaciones múltiples) es trabajo pesado para Codex; ver más abajo.
- **1H en TradingView:** mi 1H en 2026 (W10 +22,2 %, 32 ops, PF 1,44) no cuadra con lo que el usuario ve en su TradingView (−21,6 %, 21 ops, 4 ganadoras, etiquetas «Margin call»). Posibles causas, sin verificar: la ventana de 2.500 velas (la EMA de régimen necesita ~2.400), ETH/USD frente a ETHUSDT, y la configuración de margen/apalancamiento del Pine. No es comparable sin la lista de operaciones.
- Datos 2026 = Twelve Data (1H/4H) y Alpha Vantage (1D), no Binance. En el solape 4H coincide con Binance; en 1H la diferencia máxima de cierre es 0,1 %.
- Los Pine W9–W11 siguen con comisión 0,08 % y `slippage=0`; no están alineados con las condiciones confirmadas (ver `../ENCARGO_CODEX.md`).

## Qué haría falta para seguir (tareas para Codex)
1. **Búsqueda sistemática con walk-forward** (reentrenar año a año con solo años previos) sobre estructuras de entrada alternativas, con control de comparaciones múltiples (p. ej. Sharpe deflactado) y lista de pruebas registrada.
2. **Comprobar en TradingView** que el Pine de W10/W11 reproduce el motor (número de operaciones y rentabilidad en 1D/4H) y revisar la configuración de margen del Pine de 1H.
3. Reservar `HOLDOUT26` como test final de cualquier candidata: se mide una sola vez.

## Archivos
`backtest_w12.py` (motor; `python backtest_w12.py ../../csvs`) · `exp12.py` (rejilla) · `diag12.py` (diagnóstico) · `build_ext_data.py` (extensión de datos) · `data_raw/` (descargas originales) · `resultados/exp_dev_slip0.csv`, `resultados/exp_dev_slip0.06.csv`, `resultados/baseline_W10_W11_tv_slip0.csv`, `resultados/baseline_W10_W11_tv_slip0.06.csv`.
