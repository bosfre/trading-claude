# W11 — ETH SHORT: resultados de backtest (W10 como baseline + stop por tipo de entrada)

**Motor:** el de tu `backtest_w4.py` (reproduce exactamente W8: 1D +449,3 %, 4H +403,2 %, 1H +745,6 %), CSV de Binance 2017-08-17 → 2026-01-06 (1H 73.414 · 4H 18.371 · 1D 3.065 velas). **Tramos:** TRAIN 2017-08→2021-12 · VALIDATION 2022-2023 · OOS 2024→2026-01. **Costes:** 0,05 % comisión + 0,03 % slippage por lado, tope 2x. Equity continua; los tramos se miden sobre esa curva.

## Veredicto: **W11** (confianza moderada; ver «Qué no está probado»)

W11 mejora a W10 en las tres temporalidades y en la cartera, **con el mismo riesgo (1D, 4H) o menor (1H 6 % → 5,5 %)**, y mejora el OOS en las tres. Son **dos cambios** y nada más:

1. **1D y 4H: stop distinto según el tipo de entrada.** Las entradas por **ruptura** usan un multiplicador de stop = **0,70 × el del pullback** (1D: 1,4 frente a 2,0 ATR; 4H: 2,1 frente a 3,0). Se aplica al stop inicial, a la distancia con que se dimensiona el riesgo y al trailing de esa operación. El pullback queda exactamente como en W10.
2. **1H: se elimina la toma parcial** (25 % a 1,5 ATR) y el riesgo baja de 6 % a 5,5 %. La toma parcial solo compraba win rate: a igual DD recortaba ~1/6 de la rentabilidad.

| TF (riesgo) | Métrica | W10 | W11 | Cambio |
|---|---|---:|---:|---|
| **1D** (5 %) | Rentab. total / OOS | +500 % / +76,6 % | **+818 % / +104,7 %** | +64 % / +28 pts |
| | DD · PF · WR · ops | −20,6 % · 2,20 · 49,5 % · 103 | −20,5 % · 2,50 · 52,4 % · 105 | DD igual, PF +0,30 |
| | Beneficio/op · CAGR/DD | 1,97 % · 1,15 | 2,38 % · 1,48 | |
| **4H** (4 %) | Rentab. total / OOS | +403 % / +22,5 % | **+504 % / +43,9 %** | +25 % / +21 pts |
| | DD · PF · WR · ops | −23,9 % · 1,53 · 43,6 % · 181 | **−20,5 %** · 1,60 · 43,9 % · 187 | DD −3,4 pts |
| | Beneficio/op · CAGR/DD | 1,01 % · 0,89 | 1,08 % · 1,16 | |
| **1H** (6 → 5,5 %) | Rentab. total / OOS | +880 % / +79,7 % | **+1.134 % / +92,8 %** | +29 % / +13 pts |
| | DD · PF · WR · ops | −17,6 % · 2,21 · 56,5 % · 115 | −17,9 % · 2,25 · **49,6 %** · 115 | DD +0,3 pts, WR −7 pts |
| | Beneficio/op · CAGR/DD | 2,21 % · 1,77 | 2,47 % · 1,95 | |
| **Cartera** 1D+4H+1H (1/3 c/u, reb. diario) | Total / DD / OOS | +600 % / −13,0 % / +59 % | **+833 % / −12,7 % / +80 %** | Sharpe 1,34 → 1,43 |
| Cartera con pesos 1,4/3 (≈ tu +1.330 %) | Total / DD / OOS | +1.312 % / −17,9 % / +88 % | **+1.988 % / −17,7 % / +124 %** | |

## Nota sobre W10: reconstrucción, no el archivo original

**W10 no estaba en los archivos del proyecto** (solo W1–W9 y los CSV; no tengo acceso a GitHub desde aquí). Lo reconstruí a partir de tus cifras de referencia buscando la variante de W9 que las reproduce, y cuadra casi exacta: **W10 = W9 con el percentil del filtro de volatilidad por temporalidad (1D 70 · 4H 75 · 1H 65) y riesgo 5/4/6 %**.

| | Referencia que me diste | Mi reconstrucción |
|---|---|---|
| 1D | +500 % · DD −20,6 % · PF 2,20 · WR 49,5 % · 103 ops · OOS +76,6 % | +500,3 % · −20,6 % · 2,20 · 49,5 % · 103 · +76,6 % |
| 4H | +403 % · DD −23,9 % · PF 1,53 · WR 43,6 % · 181 ops · OOS +22,5 % | +403,2 % · −23,9 % · 1,53 · 43,6 % · 181 · +22,5 % |
| 1H | +887 % · DD −17,6 % · PF 2,21 · WR 56,5 % · 115 ops · OOS +80,0 % | +880 % · −17,6 % · 2,21 · 56,5 % · 115 · +79,7 % |

La diferencia del 1H (+880 % frente a +887 %) es que el motor de W9 no cobraba la comisión de salida de la parte parcial; el mío sí. **Compara siempre con el Pine real de W10**: si tu W10 difiere de esta reconstrucción en algo que yo no vea, las mejoras podrían cambiar.

## Por qué funciona

Una entrada por ruptura se produce **en un cierre ya en mínimos**: el riesgo principal es el rebote inmediato, y un stop más corto lo recorta; si la ruptura continúa, el trailing sigue pegado al mínimo. Un **pullback fallido** entra en un rebote hacia la EMA rápida y necesita más aire para no ser expulsado por el ruido. W10 trataba las dos entradas con el mismo stop, y ese era un compromiso. La mejora aparece de forma consistente y en el mismo sentido en 1D y 4H (el ratio óptimo ronda 0,6–0,8 en las dos).

Qué mejora: **PF, beneficio medio por operación y OOS** en 1D y 4H; DD −3,4 pts en 4H. En 1D el DD no baja (−20,5 %), y no se alcanza la zona 10–20 % en 4H ni en 1D.

## Comparación completa con W10 (mismo riesgo; 1H W11 a 5,5 % y a 6 % para comparar a igual riesgo)

| TF | Versión | Riesgo | Tramo | Rentab. | DD | PF | WR | Ops | Benef./op | CAGR | CAGR/DD |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | W10 | 5.00% | TRAIN | 96.8% | -15.9% | 1.79 | 52.1% | 48 | 1.59% | 16.8% | 1.05 |
| 1D | W10 | 5.00% | VALIDATION | 72.8% | -20.6% | 1.76 | 41.0% | 39 | 1.65% | 31.5% | 1.53 |
| 1D | W10 | 5.00% | OOS | 76.6% | -8.8% | 3.42 | 62.5% | 16 | 3.88% | 32.6% | 3.70 |
| 1D | W10 | 5.00% | TOTAL | 500.3% | -20.6% | 2.20 | 49.5% | 103 | 1.97% | 23.8% | 1.15 |
| 1D | W11 | 5.00% | TRAIN | 152.0% | -14.5% | 2.09 | 55.1% | 49 | 2.09% | 23.5% | 1.63 |
| 1D | W11 | 5.00% | VALIDATION | 78.0% | -20.5% | 1.81 | 45.0% | 40 | 1.70% | 33.5% | 1.63 |
| 1D | W11 | 5.00% | OOS | 104.7% | -8.9% | 3.86 | 62.5% | 16 | 4.99% | 42.7% | 4.77 |
| 1D | W11 | 5.00% | TOTAL | 818.0% | -20.5% | 2.50 | 52.4% | 105 | 2.38% | 30.3% | 1.48 |
| 4H | W10 | 4.00% | TRAIN | 180.7% | -20.6% | 2.15 | 48.6% | 74 | 1.53% | 26.6% | 1.29 |
| 4H | W10 | 4.00% | VALIDATION | 46.3% | -15.2% | 1.51 | 45.0% | 60 | 0.73% | 21.0% | 1.39 |
| 4H | W10 | 4.00% | OOS | 22.5% | -23.9% | 1.26 | 34.0% | 47 | 0.55% | 10.6% | 0.44 |
| 4H | W10 | 4.00% | TOTAL | 403.2% | -23.9% | 1.53 | 43.6% | 181 | 1.01% | 21.2% | 0.89 |
| 4H | W11 | 4.00% | TRAIN | 218.2% | -17.6% | 2.30 | 50.0% | 78 | 1.62% | 30.3% | 1.72 |
| 4H | W11 | 4.00% | VALIDATION | 31.8% | -17.2% | 1.35 | 41.9% | 62 | 0.52% | 14.9% | 0.86 |
| 4H | W11 | 4.00% | OOS | 43.9% | -20.5% | 1.47 | 36.2% | 47 | 0.91% | 19.8% | 0.96 |
| 4H | W11 | 4.00% | TOTAL | 503.5% | -20.5% | 1.60 | 43.9% | 187 | 1.08% | 23.9% | 1.16 |
| 1H | W10 | 6.00% | TRAIN | 218.7% | -13.7% | 3.17 | 67.4% | 43 | 2.95% | 30.4% | 2.21 |
| 1H | W10 | 6.00% | VALIDATION | 71.2% | -17.6% | 1.75 | 46.7% | 45 | 1.36% | 30.9% | 1.75 |
| 1H | W10 | 6.00% | OOS | 79.7% | -13.8% | 2.34 | 55.6% | 27 | 2.46% | 33.8% | 2.44 |
| 1H | W10 | 6.00% | TOTAL | 880.5% | -17.6% | 2.21 | 56.5% | 115 | 2.21% | 31.3% | 1.77 |
| 1H | W11 | 5.50% | TRAIN | 258.3% | -15.1% | 3.28 | 55.8% | 43 | 3.29% | 33.9% | 2.24 |
| 1H | W11 | 5.50% | VALIDATION | 78.6% | -17.9% | 1.73 | 42.2% | 45 | 1.50% | 33.7% | 1.88 |
| 1H | W11 | 5.50% | OOS | 92.8% | -14.3% | 2.44 | 51.9% | 27 | 2.80% | 38.5% | 2.69 |
| 1H | W11 | 5.50% | TOTAL | 1133.9% | -17.9% | 2.25 | 49.6% | 115 | 2.47% | 34.9% | 1.95 |
| 1H | W11 @riesgo W10 | 6.00% | TRAIN | 297.5% | -16.3% | 3.23 | 55.8% | 43 | 3.59% | 37.1% | 2.27 |
| 1H | W11 @riesgo W10 | 6.00% | VALIDATION | 84.5% | -18.8% | 1.71 | 42.2% | 45 | 1.60% | 35.9% | 1.91 |
| 1H | W11 @riesgo W10 | 6.00% | OOS | 103.0% | -15.5% | 2.40 | 51.9% | 27 | 3.05% | 42.1% | 2.72 |
| 1H | W11 @riesgo W10 | 6.00% | TOTAL | 1388.9% | -18.8% | 2.21 | 49.6% | 115 | 2.68% | 38.0% | 2.02 |

## Año a año (equity continua, mismo riesgo)

| Año | 1D W10 | 1D W11 | 4H W10 | 4H W11 | 1H W10 | 1H W11 |
|---|---:|---:|---:|---:|---:|---:|
| 2018 | 98.1% | 125.1% | 130.9% | 128.3% | 83.6% | 103.2% |
| 2019 | 12.4% | 26.1% | 41.6% | 55.6% | 75.3% | 80.5% |
| 2020 | -5.3% | -5.3% | -9.9% | -9.9% | -3.7% | -4.2% |
| 2021 | -6.7% | -6.3% | -4.7% | -0.6% | 2.8% | 2.0% |
| 2022 | 53.9% | 53.8% | 25.7% | 16.5% | 53.2% | 53.9% |
| 2023 | 12.3% | 15.7% | 16.4% | 13.2% | 11.7% | 16.0% |
| 2024 | 74.4% | 99.5% | 27.7% | 41.6% | 57.8% | 67.6% |
| 2025 | 1.2% | 2.6% | -4.1% | 1.6% | 13.9% | 15.0% |

W11 ≥ W10 en 1D en todos los años menos 2022 (igual); en 1H en 6 de 8; en 4H empeora en 2022 (+25,7 % → +16,5 %) y 2023 (+16,4 % → +13,2 %), mejora en 2019, 2021, 2024 y 2025. **La mejora no depende de un solo año** (1D: 2018, 2019, 2024 y 2023 aportan; 4H: 2019, 2024, 2025).

## A igual drawdown (control del efecto riesgo)

| TF | Versión | Riesgo | Rentab. total | DD | PF | OOS |
|---|---|---:|---:|---:|---:|---:|
| 1D | W10 | 4,99 % | +499 % | −20,6 % | 2,20 | +76 % |
| 1D | W11 | 5,03 % | **+827 %** | −20,6 % | 2,50 | +105 % |
| 4H | W10 | 4,00 % | +404 % | −23,9 % | 1,53 | +23 % |
| 4H | W11 | 4,76 % | **+694 %** | −23,9 % | 1,55 | +52 % |
| 1H | W10 | 5,97 % | +872 % | −17,6 % | 2,21 | +79 % |
| 1H | W11 | 5,31 % | **+1.047 %** | −17,6 % | 2,26 | +89 % |

En 1D el riesgo necesario es prácticamente el mismo: la mejora **no** viene de apalancar. En 4H parte de la ganancia a igual DD sí requiere más riesgo (4,76 %), por eso la tabla principal compara a riesgo igual (4 %).

## Robustez

**Vecindario pareado** (108 variantes por TF: régimen EMA 450/600/800 × ruptura 30/45/60 × percentil de vol 65/70/75/80 × pullback 3 valores; mismo riesgo; W11 frente a W10 con los mismos ajustes del resto):

| TF | TRAIN mejora | VALID mejora | OOS mejora | TOTAL mejora | CAGR/DD mejora | PF mejora | DD menor | Mediana TOTAL W10 → W11 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1D | 100 % | 75 % | 100 % | 100 % | 100 % | 94 % | 68 % | +367 % → +613 % |
| 4H | 86 % | **31 %** | 89 % | 87 % | 79 % | 83 % | 60 % | +388 % → +425 % |
| 1H (sin TP, riesgo 6 %) | 100 % | 81 % | 100 % | 100 % | 80 % | 66 % | **0 %** | +436 % → +638 % |

**Walk-forward 2021-25** (rho elegido cada año solo con años previos por CAGR/DD, rejilla {1; 0,85; 0,75; 0,70}): en 1D y 4H eligió 0,70 los cinco años (WFA +241 % y +89 % frente a +185 % y +71 % con rho = 1). En 1H eligió rho = 1 cuatro de cinco años, por eso 1H no lleva el cambio.

**Costes y slippage (TOTAL / OOS / DD):**

| Escenario | 1D W10 | 1D W11 | 4H W10 | 4H W11 | 1H W10 (6 %) | 1H W11 (5,5 %) |
|---|---:|---:|---:|---:|---:|---:|
| x1 | 500% / 77% / -20.6% | 818% / 105% / -20.5% | 403% / 23% / -23.9% | 504% / 44% / -20.5% | 880% / 80% / -17.6% | 1134% / 93% / -17.9% |
| x2 | 402% / 71% / -21.4% | 651% / 98% / -21.7% | 312% / 16% / -25.3% | 383% / 35% / -22.1% | 703% / 71% / -19.1% | 927% / 84% / -19.4% |
| x3 | 319% / 66% / -22.3% | 514% / 91% / -22.8% | 237% / 10% / -26.7% | 286% / 27% / -23.7% | 557% / 63% / -20.6% | 754% / 76% / -20.8% |
| slip x4 | 391% / 71% / -21.6% | 633% / 97% / -21.8% | 302% / 15% / -25.5% | 370% / 34% / -22.3% | 684% / 70% / -19.3% | 904% / 83% / -19.6% |

W11 sigue por encima de W10 en todos los escenarios, y aguanta costes ×3 y slippage ×4.

**Sensibilidad del ratio (igual riesgo que W10):** 1D rho 0,85 → +646 % · 0,80 → +716 % · 0,75 → +720 % · **0,70 → +818 %** · 0,67 → +887 % · **0,65 → +689 % con DD −26,4 %** · 0,60 → +581 % con DD −25,5 %. Es decir, mejora en todo el rango 0,6–0,85, pero **por debajo de 0,67 el DD de 1D se dispara**: por eso no uso 0,67 (el máximo del barrido, que daría +887 %) y dejo margen en 0,70. Cifra prudente: espera algo más cerca de +720–820 % en 1D que de +887 %. En 4H la curva es suave (0,60 → +655 %, 0,70 → +504 %, 0,80 → +445 %, 1,0 → +403 %).

## Qué se probó y se descartó (mismo riesgo, sobre W9/W10)

| Idea | Resultado |
|---|---|
| Toma parcial en 1D/4H (25–50 % a 1–3 ATR) | Recorta rentabilidad y OOS en todas las variantes; CAGR/DD sin mejora. En 1H, quitarla mejora (la razón del cambio 2). |
| Filtro de extensión en 4H (7,5–9) | Mejora PF, DD y OOS (4H +266 % y DD −16 % con ext 9) pero **TRAIN cae de +181 % a +108 %** y el total ~−35 %; no cumple «mejorar TRAIN». En 1D hunde (+472 % → +176 %). Queda como input desactivado (`extH4 = 0`) por si quieres un perfil prudente. |
| Tamaño de riesgo graduado por extensión (en vez de filtro binario) | 1D: peor (CAGR/DD 0,73–1,00 frente a 1,12). 4H: mejora CAGR/DD pero con −30 % de rentabilidad. |
| Reducir riesgo tras un DD del 8–12 % (probado sobre la base W8/W9 sin ext/TP) | 1H baja el DD pero el OOS empeora (+46 % → +38–42 %); 1D empeora CAGR/DD. |
| Trailing que se aprieta tras X ATR de beneficio | Solo ayuda en 4H con X = 6 y x0,65, con acantilado en X = 4: no es robusto. |
| Ratio ruptura/pullback también en 1H | Sube rentabilidad y DD en proporción: a igual DD **peor** (+730 % frente a +1.047 % sin TP y rho = 1). |
| Stop de la ruptura más ancho que el del pullback (rho > 1) | Peor en las tres. Pullback +0,5 ATR más ancho: sin mejora consistente (solo ayuda en 1D, junto a la ruptura más corta). |

Ronda de exploración: unas 15 hipótesis y ~400 evaluaciones para decidir W11 (sin contar las búsquedas para reconstruir W10). La decisión final descansa en **un solo mecanismo nuevo** (el ratio) más la retirada de la toma parcial en 1H.

## Qué no está probado / advertencias

- **El OOS no es limpio**: el ratio 0,70 y la retirada de la toma parcial se eligieron viendo toda la muestra. La evidencia es el vecindario, el walk-forward, el año a año y los costes, no un OOS puro. **El test limpio sigue siendo tus datos de TradingView 2015-2017 y ene–oct 2026.**
- **4H sigue siendo la temporalidad más débil**: PF 1,60, CAGR/DD 1,16 y **VALIDATION peor que W10** (+46,3 % → +31,8 %; solo mejora en el 31 % del vecindario). La mejora de 4H viene de TRAIN y OOS.
- **1H**: el win rate baja de 56,5 % a 49,6 % (la toma parcial era cosmética para el WR) y el DD sube 0,3 pts a riesgo 5,5 % (1,2 pts a riesgo 6 %). A riesgo 5,5 % los DD son comparables, no menores.
- En 1D el OOS son solo 16 operaciones (47 en 4H, 27 en 1H): los resultados OOS tienen mucha varianza.
- **El Pine W11 no se ha compilado en TradingView** (no hay acceso desde aquí). Cambia la gestión del stop por tipo de entrada, que el emulador de TradingView puede resolver distinto de mi motor en barras con stop y gap. Verifica número de operaciones y rentabilidad en 1D/4H/1H frente a W10.
- Funding de perpetuos y ejecución real no están modelados. La definición de cartera la reconstruí a ojo (pesos 1,4/3 reproducen tu +1.330 % y OOS +89 % de W10, pero mi DD no coincide con tu −20,3 %): la comparación W10-W11 usa la misma definición para ambos.
- Tus cifras de TradingView de W10 (1H ene–oct 2026 −21,6 %, 1D +451 % con DD −24,9 %) son sobre ETHUSD y otro periodo y no las puedo contrastar con mis CSV.
