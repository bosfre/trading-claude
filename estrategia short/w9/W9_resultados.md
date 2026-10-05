# W9 — ETH SHORT: resultados de backtest (W8 + mejoras de calidad por temporalidad)

**Motor:** el de tu `backtest_w4.py` (reproducción exacta de W4 y de W8), CSV de Binance 2017-08-17 → 2026-01-06. **Tramos (los tuyos):** TRAIN 2017-08→2021-12 · VALIDATION 2022-2023 · OOS 2024→2026-01. **Costes:** 0,05 % comisión + 0,03 % slippage por lado; tope de apalancamiento 2x.

## Veredicto (leer antes que las cifras)

W9 **no es una mejora uniforme sobre W8**. Es una mejora de *calidad* (win rate, PF, beneficio por operación, drawdown), y su valor depende de la temporalidad:

| TF | Qué cambia | Veredicto |
|---|---|---|
| **1D** | EMA rápida del pullback 40 → 55 (≈ 9 días) | **Mejora pequeña pero consistente** en calidad: PF 1,79 → 1,99, win rate 45,6 → 48,2 %, +1,57 → +1,77 % por operación, DD −21,7 → −20,6 % (el DD del OOS casi se reduce a la mitad: −16,9 → −8,8 %). Rentabilidad total +449 % → +472 % (casi igual: en 2021-25 el walk-forward da +158 % frente a +153 %). |
| **1H** | + filtro de extensión ≤ 9 ATR + toma parcial 25 % a 1,5 ATR + riesgo 4 → 6 % | **Mejora clara a igual rentabilidad**: mismo total (+744 % frente a +746 %), DD −24,8 → −21,3 %, PF 1,58 → 1,87, win rate 44,6 → **53,4 %**, +1,13 → **+1,84 %** por operación, OOS +47 → +66 %. Coste: TRAIN baja (240 → 195 %) y hay menos operaciones (213 → 131). |
| **4H** | **Sin cambios por defecto** | Las mejoras (extensión + toma parcial) existen en backtest pero **el walk-forward nunca habría elegido el filtro en 4H**, y a igual riesgo la rentabilidad cae a la mitad. Quedan disponibles, desactivadas. |

**Win rate:** en mi reproducción W8 tiene 45,6 % en 1D, no el ~32 % que ves en TradingView. No puedo explicar la diferencia sin tu lista de operaciones; lo más probable es el tramo 2015-2017 y ene-oct 2026 de TradingView, que no está en mis CSV. La toma parcial sube el win rate en 1D hasta ~57 %, pero **a igual DD cuesta rentabilidad y OOS** (+580 % → +503 %, OOS +79 % → +64 %), por eso no está activada en 1D.

**El filtro de extensión es una apuesta de régimen**, no una mejora gratuita: descarta entradas «extendidas» que en el crash de 2018 fueron muy rentables (4H: +166 % → +113 % ese año) y evita las que fallaron en 2019, 2022, 2024 y 2025. En 1D el filtro **empeora** mucho (+580 % → +154 %), por eso está apagado ahí.


### Valores por defecto del Pine W9 frente a W8 (los que verás al cargar el script)

| TF | Versión | Riesgo | TRAIN | VALID | OOS | TOTAL | DD total | PF | Win rate | Beneficio/op | Ops | CAGR/DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | W8 | 5% | 102% | 64% | 66% | 449% | -21.7% | 1.79 | 45.6% | 1.57% | 125 | 1.04 |
| 1D | **W9** | 5% | 107% | 68% | 65% | 472% | -20.6% | 1.99 | 48.2% | 1.77% | 112 | 1.12 |
| 4H | W8 | 4% | 181% | 46% | 23% | 403% | -23.9% | 1.53 | 43.6% | 1.01% | 181 | 0.89 |
| 4H | W9 (= W8) | 4% | 181% | 46% | 23% | 403% | -23.9% | 1.53 | 43.6% | 1.01% | 181 | 0.89 |
| 1H | W8 | 4% | 240% | 70% | 47% | 746% | -24.8% | 1.58 | 44.6% | 1.13% | 213 | 1.17 |
| 1H | **W9** | 6% | 195% | 73% | 66% | 744% | -21.3% | 1.87 | 53.4% | 1.84% | 131 | 1.36 |


## Validación completa

### A. A riesgo idéntico al de W4/W8 (1H 4 % · 4H 4 % · 1D 5 %), con las mejoras activadas en las tres temporalidades

| TF | Tramo | Versión | Riesgo | Rentab. | DD | PF | Win rate | Beneficio/op | Ops | Sharpe |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | TRAIN | W8 | 5.00% | 102.4% | -21.2% | 1.64 | 50.0% | 1.43% | 56 | 0.77 |
| 1D | TRAIN | **W9** | 5.00% | 106.9% | -17.3% | 1.83 | 52.9% | 1.59% | 51 | 0.81 |
| 1D | VALIDATION | W8 | 5.00% | 63.8% | -19.8% | 1.63 | 37.8% | 1.31% | 45 | 0.98 |
| 1D | VALIDATION | **W9** | 5.00% | 67.7% | -20.6% | 1.70 | 39.0% | 1.49% | 41 | 1.04 |
| 1D | OOS | W8 | 5.00% | 65.7% | -16.9% | 2.08 | 50.0% | 2.35% | 24 | 1.22 |
| 1D | OOS | **W9** | 5.00% | 65.0% | -8.8% | 2.49 | 55.0% | 2.77% | 20 | 1.34 |
| 1D | TOTAL | W8 | 5.00% | 449.3% | -21.7% | 1.79 | 45.6% | 1.57% | 125 | 0.92 |
| 1D | TOTAL | **W9** | 5.00% | 472.3% | -20.6% | 1.99 | 48.2% | 1.77% | 112 | 0.97 |
| 4H | TRAIN | W8 | 4.00% | 180.7% | -20.6% | 2.15 | 48.6% | 1.53% | 74 | 1.31 |
| 4H | TRAIN | **W9** | 4.00% | 85.4% | -12.1% | 2.63 | 60.5% | 1.54% | 43 | 1.29 |
| 4H | VALIDATION | W8 | 4.00% | 46.3% | -15.2% | 1.51 | 45.0% | 0.73% | 60 | 0.93 |
| 4H | VALIDATION | **W9** | 4.00% | 28.3% | -10.4% | 1.59 | 45.2% | 0.65% | 42 | 0.83 |
| 4H | OOS | W8 | 4.00% | 22.5% | -23.9% | 1.26 | 34.0% | 0.55% | 47 | 0.62 |
| 4H | OOS | **W9** | 4.00% | 27.8% | -8.2% | 1.75 | 50.0% | 0.98% | 28 | 1.01 |
| 4H | TOTAL | W8 | 4.00% | 403.2% | -23.9% | 1.53 | 43.6% | 1.01% | 181 | 1.05 |
| 4H | TOTAL | **W9** | 4.00% | 204.1% | -12.1% | 1.89 | 52.2% | 1.07% | 113 | 1.07 |
| 1H | TRAIN | W8 | 4.00% | 240.0% | -24.2% | 2.13 | 50.0% | 1.56% | 86 | 1.46 |
| 1H | TRAIN | **W9** | 4.00% | 110.6% | -14.7% | 2.72 | 63.8% | 1.69% | 47 | 1.47 |
| 1H | VALIDATION | W8 | 4.00% | 69.7% | -24.8% | 1.52 | 42.0% | 0.89% | 69 | 1.10 |
| 1H | VALIDATION | **W9** | 4.00% | 50.6% | -14.5% | 1.81 | 46.8% | 0.96% | 47 | 1.13 |
| 1H | OOS | W8 | 4.00% | 46.5% | -24.1% | 1.43 | 39.7% | 0.79% | 58 | 0.97 |
| 1H | OOS | **W9** | 4.00% | 42.6% | -12.7% | 1.85 | 48.6% | 1.07% | 37 | 1.26 |
| 1H | TOTAL | W8 | 4.00% | 745.6% | -24.8% | 1.58 | 44.6% | 1.13% | 213 | 1.23 |
| 1H | TOTAL | **W9** | 4.00% | 352.3% | -14.7% | 1.99 | 53.4% | 1.25% | 131 | 1.28 |

### B. A igual presupuesto de drawdown in-sample ≤ 25 % (tu regla): cada versión con el riesgo que lo cumple

| TF | Tramo | Versión | Riesgo | Rentab. | DD | PF | Win rate | Beneficio/op | Ops | Sharpe |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | TRAIN | W8 | 5.75% | 121.5% | -24.0% | 1.60 | 50.0% | 1.65% | 56 | 0.78 |
| 1D | TRAIN | **W9** | 6.00% | 134.8% | -20.5% | 1.78 | 52.9% | 1.91% | 51 | 0.82 |
| 1D | VALIDATION | W8 | 5.75% | 68.8% | -22.6% | 1.58 | 37.8% | 1.44% | 45 | 0.96 |
| 1D | VALIDATION | **W9** | 6.00% | 76.6% | -24.2% | 1.65 | 39.0% | 1.70% | 41 | 1.02 |
| 1D | OOS | W8 | 5.75% | 77.1% | -19.2% | 2.03 | 50.0% | 2.70% | 24 | 1.22 |
| 1D | OOS | **W9** | 6.00% | 80.2% | -10.5% | 2.42 | 55.0% | 3.33% | 20 | 1.34 |
| 1D | TOTAL | W8 | 5.75% | 562.4% | -24.5% | 1.75 | 45.6% | 1.77% | 125 | 0.92 |
| 1D | TOTAL | **W9** | 6.00% | 647.1% | -24.2% | 1.95 | 48.2% | 2.09% | 112 | 0.97 |
| 4H | TRAIN | W8 | 4.75% | 233.7% | -24.0% | 2.07 | 48.6% | 1.82% | 74 | 1.31 |
| 4H | TRAIN | **W9** | 8.50% | 232.3% | -24.3% | 2.27 | 60.5% | 3.20% | 43 | 1.27 |
| 4H | VALIDATION | W8 | 4.75% | 51.8% | -17.7% | 1.46 | 45.0% | 0.82% | 60 | 0.91 |
| 4H | VALIDATION | **W9** | 8.50% | 49.4% | -21.5% | 1.46 | 45.2% | 1.15% | 42 | 0.80 |
| 4H | OOS | W8 | 4.75% | 25.9% | -27.7% | 1.24 | 34.0% | 0.66% | 47 | 0.61 |
| 4H | OOS | **W9** | 8.50% | 55.1% | -16.7% | 1.63 | 50.0% | 2.00% | 28 | 0.96 |
| 4H | TOTAL | W8 | 4.75% | 537.5% | -27.7% | 1.48 | 43.6% | 1.19% | 181 | 1.04 |
| 4H | TOTAL | **W9** | 8.50% | 670.3% | -24.3% | 1.69 | 52.2% | 2.14% | 113 | 1.05 |
| 1H | TRAIN | W8 | 4.00% | 240.0% | -24.2% | 2.13 | 50.0% | 1.56% | 86 | 1.46 |
| 1H | TRAIN | **W9** | 7.00% | 246.6% | -24.5% | 2.45 | 63.8% | 2.96% | 47 | 1.46 |
| 1H | VALIDATION | W8 | 4.00% | 69.7% | -24.8% | 1.52 | 42.0% | 0.89% | 69 | 1.10 |
| 1H | VALIDATION | **W9** | 7.00% | 84.4% | -19.6% | 1.69 | 46.8% | 1.50% | 47 | 1.16 |
| 1H | OOS | W8 | 4.00% | 46.5% | -24.1% | 1.43 | 39.7% | 0.79% | 58 | 0.97 |
| 1H | OOS | **W9** | 7.00% | 76.2% | -21.2% | 1.74 | 48.6% | 1.85% | 37 | 1.23 |
| 1H | TOTAL | W8 | 4.00% | 745.6% | -24.8% | 1.58 | 44.6% | 1.13% | 213 | 1.23 |
| 1H | TOTAL | **W9** | 7.00% | 1026.0% | -24.5% | 1.82 | 53.4% | 2.13% | 131 | 1.30 |

### Año a año (equity continua, riesgo a igual DD)

| Año | 1D W8 | 1D W9 | 4H W8 | 4H W9 | 1H W8 | 1H W9 |
|---|---:|---:|---:|---:|---:|---:|
| 2018 | 114.5% | 134.9% | 165.9% | 113.3% | 142.0% | 101.2% |
| 2019 | 30.1% | 16.0% | 50.5% | 82.1% | 61.3% | 94.8% |
| 2020 | -14.0% | -6.3% | -11.7% | -8.9% | -14.2% | -14.3% |
| 2021 | -7.7% | -8.0% | -5.6% | -6.1% | 1.5% | 3.2% |
| 2022 | 53.0% | 59.1% | 30.1% | 28.0% | 49.3% | 64.9% |
| 2023 | 10.3% | 10.9% | 16.7% | 16.7% | 13.7% | 11.9% |
| 2024 | 90.1% | 88.4% | 32.9% | 40.3% | 31.6% | 46.9% |
| 2025 | -6.8% | -4.4% | -5.3% | 10.6% | 11.3% | 19.9% |

### Costes y slippage (TOTAL / OOS), riesgo a igual DD

| TF | Versión | costes ×1 | costes ×2 | costes ×3 | slippage ×4 |
|---|---|---:|---:|---:|---:|
| 1D | W8 | 562% / 77% (DD -25%) | 420% / 68% (DD -27%) | 309% / 60% (DD -30%) | 405% / 67% (DD -27%) |
| 1D | W9 | 647% / 80% (DD -24%) | 497% / 72% (DD -25%) | 377% / 65% (DD -26%) | 481% / 71% (DD -25%) |
| 4H | W8 | 537% / 26% (DD -28%) | 402% / 18% (DD -29%) | 296% / 10% (DD -31%) | 388% / 17% (DD -30%) |
| 4H | W9 | 670% / 55% (DD -24%) | 511% / 45% (DD -25%) | 384% / 36% (DD -29%) | 486% / 44% (DD -26%) |
| 1H | W8 | 746% / 47% (DD -25%) | 557% / 37% (DD -28%) | 411% / 27% (DD -32%) | 537% / 35% (DD -29%) |
| 1H | W9 | 1026% / 76% (DD -24%) | 784% / 64% (DD -25%) | 594% / 53% (DD -26%) | 746% / 62% (DD -26%) |

### Frontera de riesgo de W9 (TOTAL ret / DD total / OOS)

| Riesgo | 1D | 4H | 1H |
|---|---|---|---|
| 3% | 217% / -12.9% / 37% | 139% / -9.2% / 21% | 229% / -11.3% / 31% |
| 4% | 331% / -16.9% / 50% | 204% / -12.1% / 28% | 352% / -14.7% / 43% |
| 5% | 472% / -20.6% / 65% | 282% / -14.9% / 35% | 522% / -18.1% / 54% |
| 6% | 647% / -24.2% / 80% | 375% / -17.7% / 42% | 744% / -21.3% / 66% |
| 7% | 829% / -27.7% / 89% | 490% / -20.4% / 48% | 1026% / -24.5% / 76% |
| 8% | 1003% / -31.0% / 94% | 616% / -23.0% / 54% | 1323% / -27.5% / 84% |

### Sensibilidad: 81 variantes alrededor de W9 (régimen 450/600/800 · ruptura 30/45/60 · percentil de vol 65/75/85 · 4.º eje: extensión 7,5/9/10,5 en 1H-4H; pullback 45/55/75 en 1D), riesgo W8

| TF | Tramo | Mín | Mediana | Máx | % positivas | PF mediano | Win rate mediano |
|---|---|---:|---:|---:|---:|---:|---:|
| 1D | TRAIN | 59% | 102% | 181% | 100% | | |
| 1D | VALIDATION | 4% | 55% | 90% | 100% | | |
| 1D | OOS | 14% | 46% | 80% | 100% | | |
| 1D | TOTAL | 162% | 350% | 660% | 100% | 1.77 | 47.4% |
| 1D | (W8, mismas variantes de régimen/ruptura/vol) OOS mediano / PF / WR | | 38% | | | 1.59 | 44.5% |
| 4H | TRAIN | 22% | 73% | 131% | 100% | | |
| 4H | VALIDATION | -1% | 19% | 40% | 99% | | |
| 4H | OOS | -5% | 23% | 54% | 96% | | |
| 4H | TOTAL | 51% | 148% | 248% | 100% | 1.70 | 51.5% |
| 4H | (W8, mismas variantes de régimen/ruptura/vol) OOS mediano / PF / WR | | 23% | | | 1.47 | 42.6% |
| 1H | TRAIN | 37% | 96% | 140% | 100% | | |
| 1H | VALIDATION | 14% | 44% | 84% | 100% | | |
| 1H | OOS | 7% | 33% | 59% | 100% | | |
| 1H | TOTAL | 147% | 257% | 425% | 100% | 1.91 | 52.3% |
| 1H | (W8, mismas variantes de régimen/ruptura/vol) OOS mediano / PF / WR | | 36% | | | 1.54 | 44.3% |

### Walk-forward 2021-25 (parámetro elegido cada año solo con los años previos por CAGR/DD anual; resto de W9 fijo; riesgo W8)

| TF | Parámetro | Elegidos por año (2021→2025) | WFA pooled | W9 fijo | W8 |
|---|---|---|---:|---:|---:|
| 1H | ext | 9, 9, 9, None, 9 | 114% | 119% | 152% |
| 4H | ext | None, None, None, None, None | 62% | 59% | 71% |
| 1D | pb | 30, 30, 75, 75, 75 | 92% | 158% | 153% |


## Ideas probadas y descartadas

| Idea | Resultado |
|---|---|
| Stop inicial más ajustado (×0,75) | Sube el total pero con más DD y menor PF: es sobre todo más exposición. |
| Trailing más ancho (×1,25) | Mejora TRAIN en 1D pero baja VALID y OOS; daña 4H/1H. |
| Break-even a 1,5 ATR (1D) | Pico aislado: 1,25 y 1,75 ATR dan igual o menos que la base. Además hunde el win rate en 4H/1H (44 → 37 %). |
| Toma parcial en 1D | Sube el win rate (45 → 57 %) pero a igual DD baja rentabilidad (−13 %), PF y OOS. |
| Más riesgo a las rupturas (×1,5) | A igual DD no mejora (+580 % → +517 %). |
| Filtros de pendiente, RSI, posición del cierre | Sin efecto o inconsistentes entre tramos. |
| Filtro de volumen (≥ 0,6–0,8 × media) | Sube PF pero recorta TRAIN a la mitad en 1D; dependiente de régimen, no adoptado. |
| Parada por tiempo | No se activa nunca con el trailing actual. |
| Pullback con EMA distinta en 1H/4H | Ruidoso; la mejor zona sigue siendo 35–40. |

## Advertencias

- **No es una mejora uniforme:** 1H y 1D mejoran en calidad; 4H queda como W8.
- **Más riesgo por operación en 1H (6 %)**: se justifica por la reducción del DD, pero aumenta el daño por gap en un stop; el modelo incluye gaps al open pero no ejecución real ni funding.
- **Toma parcial en TradingView:** mi motor da prioridad al stop si coinciden stop y objetivo en la misma barra; el emulador de TradingView puede resolverlo distinto, y el objetivo se coloca sobre el cierre de la señal (no sobre la apertura de la entrada).
- **El OOS no es independiente:** parte de la elección (extensión 9, parcial 25 %/1,5 ATR) se apoya en haber visto el comportamiento en 2019-2025. La evidencia de robustez es la meseta (1H: extensión 7,5–10,5), la sensibilidad y el walk-forward.
- Los tests limpios siguen siendo tus datos de TradingView de 2015-2017 y ene-oct 2026.
