# W6 — ETH SHORT: resultados de backtest

**Datos:** ETHUSDT Binance 2017-08-17 → 2026-01-06 (1H 73.414 velas · 4H 18.371 · 1D 3.065). **Tramos:** TRAIN 2017-08→2020-12 · VALID 2021-01→2023-06 · OOS 2023-07→2026-01.  
**Motor:** short-only, riesgo 3 %, tope 10x, comisión 0,05 % + slippage 0,02 % por lado (en entradas stop el slippage es el doble), stops intrabarra con gap, DD mark-to-market con el HIGH de la barra (conservador), capital 10.000 reiniciado por tramo. Calibración: mi motor dio +24,5 % para W5 en 1D y TradingView +24,55 %.

## Veredicto

- **1H y 4H: mejora real y robusta.** W6 = W5 + entrada por orden stop en el nivel de ruptura, **sin reoptimizar ningún parámetro**.
- **1D: objetivo +500 % NO alcanzado, y no es alcanzable con esta familia.** En 1D W6 = W5 (la entrada stop no ayuda ahí). Ver sección 1D.

> **Integridad:** los parámetros de W5 se eligieron mirando los tres tramos, así que el OOS no es limpio. W6 no añade ningún parámetro nuevo ajustado: el cambio es de ejecución y se valida con comparación pareada sobre toda la rejilla de parámetros. Los tests limpios son los datos de TradingView que no están en mis CSV (2015-2017 y ene-oct 2026).


## 1H

| Tramo | Versión | Rentab. | CAGR | DD máx | PF | Win rate | Ops | CAGR/DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | W5 | 294.3% | 50.2% | 31.1% | 3.88 | 34% | 38 | 1.61 |
| TRAIN | **W6** | 615.4% | 79.2% | 35.2% | 4.48 | 36% | 45 | 2.25 |
| VALID | W5 | 50.9% | 18.0% | 28.2% | 1.67 | 21% | 24 | 0.64 |
| VALID | **W6** | 75.5% | 25.3% | 38.5% | 1.69 | 18% | 33 | 0.66 |
| OOS | W5 | 76.8% | 25.4% | 30.3% | 2.05 | 39% | 23 | 0.84 |
| OOS | **W6** | 91.6% | 29.5% | 32.3% | 1.77 | 30% | 33 | 0.91 |
| FULL | W5 | 951.8% | 32.4% | 31.1% | 2.14 | 32% | 85 | 1.04 |
| FULL | **W6** | 2306.4% | 46.1% | 38.5% | 1.94 | 29% | 111 | 1.20 |

**Año a año (capital reiniciado):**

| Año | ETH | W5 | W6 | W6 DD | W6 ops |
|---|---:|---:|---:|---:|---:|
| 2018 | -82% | 159.1% | 264.8% | 35.2% | 25 |
| 2019 | -2% | 41.7% | 89.3% | 25.9% | 13 |
| 2020 | 471% | 21.7% | 21.2% | 14.3% | 2 |
| 2021 | 401% | -13.7% | -12.5% | 17.8% | 6 |
| 2022 | -68% | 86.8% | 95.9% | 38.5% | 25 |
| 2023 | 91% | 12.3% | 8.9% | 25.8% | 11 |
| 2024 | 45% | 31.2% | 39.4% | 20.5% | 7 |
| 2025 | -12% | 12.4% | 29.3% | 27.4% | 17 |

**Estrés de costes y de fill (FULL / OOS):**

| Escenario | W6 FULL | W6 DD | W6 OOS |
|---|---:|---:|---:|
| slippage entrada 0.02% | 2335% | 38.4% | 92.3% |
| slippage entrada 0.04% | 2306% | 38.5% | 91.6% |
| slippage entrada 0.08% | 2249% | 38.5% | 90.2% |
| slippage entrada 0.16% | 2139% | 38.7% | 87.4% |
| TODOS los costes ×2 | 1731% | 40.1% | 72.5% |
| TODOS los costes ×3 | 1292% | 41.8% | 55.2% |

**Perturbación ±1 paso en L, ks, kt (27 vecinos):** TRAIN: mín 155%, mediana 744%, 100% positivos · VALID: mín 28%, mediana 113%, 100% positivos · OOS: mín 12%, mediana 55%, 100% positivos

**Frontera riesgo → CAGR/DD (W6, FULL):**

| Riesgo/op | CAGR | DD | CAGR/DD |
|---|---:|---:|---:|
| 2% | 31.8% | 27.9% | 1.14 |
| 3% | 46.1% | 38.5% | 1.20 |
| 4% | 59.2% | 47.3% | 1.25 |
| 5% | 71.2% | 54.9% | 1.30 |

## 4H

| Tramo | Versión | Rentab. | CAGR | DD máx | PF | Win rate | Ops | CAGR/DD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | W5 | 105.6% | 23.8% | 14.6% | 3.74 | 48% | 29 | 1.63 |
| TRAIN | **W6** | 205.7% | 39.3% | 20.3% | 4.20 | 48% | 33 | 1.93 |
| VALID | W5 | 3.0% | 1.2% | 20.1% | 1.07 | 27% | 22 | 0.06 |
| VALID | **W6** | 4.5% | 1.8% | 24.7% | 1.08 | 28% | 29 | 0.07 |
| OOS | W5 | 26.8% | 9.9% | 12.1% | 1.92 | 41% | 17 | 0.82 |
| OOS | **W6** | 48.4% | 17.0% | 20.7% | 1.77 | 38% | 26 | 0.82 |
| FULL | W5 | 168.3% | 12.5% | 21.2% | 1.88 | 40% | 68 | 0.59 |
| FULL | **W6** | 374.0% | 20.4% | 24.7% | 1.84 | 39% | 88 | 0.82 |

**Año a año (capital reiniciado):**

| Año | ETH | W5 | W6 | W6 DD | W6 ops |
|---|---:|---:|---:|---:|---:|
| 2018 | -82% | 78.0% | 114.0% | 17.4% | 18 |
| 2019 | -2% | 12.2% | 32.3% | 14.2% | 12 |
| 2020 | 466% | 12.9% | 13.8% | 7.3% | 1 |
| 2021 | 394% | -10.4% | -8.3% | 8.9% | 5 |
| 2022 | -68% | 22.5% | 15.3% | 24.7% | 22 |
| 2023 | 91% | -5.5% | 1.4% | 15.3% | 9 |
| 2024 | 47% | 14.3% | 17.5% | 11.5% | 7 |
| 2025 | -11% | 10.1% | 23.1% | 12.4% | 12 |

**Estrés de costes y de fill (FULL / OOS):**

| Escenario | W6 FULL | W6 DD | W6 OOS |
|---|---:|---:|---:|
| slippage entrada 0.02% | 378% | 24.7% | 48.8% |
| slippage entrada 0.04% | 374% | 24.7% | 48.4% |
| slippage entrada 0.08% | 359% | 24.8% | 45.4% |
| slippage entrada 0.16% | 344% | 25.1% | 43.9% |
| TODOS los costes ×2 | 316% | 25.8% | 39.7% |
| TODOS los costes ×3 | 270% | 27.3% | 33.5% |

**Perturbación ±1 paso en L, ks, kt (27 vecinos):** TRAIN: mín 59%, mediana 182%, 100% positivos · VALID: mín -2%, mediana 16%, 96% positivos · OOS: mín 12%, mediana 41%, 100% positivos

**Frontera riesgo → CAGR/DD (W6, FULL):**

| Riesgo/op | CAGR | DD | CAGR/DD |
|---|---:|---:|---:|
| 2% | 13.9% | 17.3% | 0.80 |
| 3% | 20.4% | 24.7% | 0.82 |
| 4% | 26.5% | 31.4% | 0.84 |
| 5% | 32.2% | 37.5% | 0.86 |

## 1D — objetivo +500 %: no alcanzado

| Tramo | W5 = W6 (1D) | Rentab. | CAGR | DD | PF | Ops |
|---|---|---:|---:|---:|---:|---:|
| TRAIN | W5/W6 | 16.6% | 4.7% | 7.2% | 5.12 | 6 |
| VALID | W5/W6 | 2.5% | 1.0% | 10.2% | 1.31 | 5 |
| OOS | W5/W6 | 4.2% | 1.7% | 5.2% | 2.50 | 4 |
| FULL | W5/W6 | 24.5% | 2.7% | 13.0% | 2.48 | 15 |

**Frontera riesgo → CAGR (1D, FULL):** 3%: CAGR 2.7% / DD 13% · 5%: CAGR 4.3% / DD 21% · 8%: CAGR 6.4% / DD 31% · 10%: CAGR 7.8% / DD 37%

**Qué se probó para llegar a +500 % y por qué no funciona:**

1. *Exposición pasiva en régimen bajista* (short con nocional fijo cuando cierre < EMA 50/100/200): **pierde en todos los tramos** (hasta −96 % a 1x). No existe un beta bajista gratuito que apalancar.
2. *Escaneo de señales* (RSI2, Bollinger, días extremos, rebotes a EMA…): ETH tiene deriva alcista fuerte y los sobrecomprados **siguen subiendo** (RSI2>95: +6 % a 10 días). Vender fuerza/reversión a la media está contraindicado. Lo único con signo bajista es la ruptura de mínimos largos, con muy pocas muestras y desvaneciéndose en OOS.
3. *Pyramiding* (hasta 5 unidades): sube TRAIN/VALID pero **suspende el OOS** (−4 % a −8 %) y, a igual DD, queda en la misma frontera que subir el riesgo.
4. *Entrada por orden stop en 1D*: no mejora (FULL +24,5 % → +17 %, OOS negativo).
5. *Búsqueda aleatoria de 5.000 configuraciones* (cruces de EMAs, pendiente, RSI, ROC, TP, salida por momentum/tiempo, pyramiding): **la mejor rentabilidad total, mirando TODO el histórico, fue +200 % (DD 34 %, OOS ≈ 0 %)**. Las 8 mejores por TRAIN/VALID cayeron todas en OOS (−4 % a −23 %).
6. *Walk-forward* (ver W5): re-optimizar cada año con solo datos pasados da −16 % en 1D (2021-25).

**Conclusión:** con riesgo 3 % el edge robusto en 1D es ≈ 3 % anual (CAGR/DD ≈ 0,2 a cualquier nivel de riesgo). Llegar a +500 % exigiría sobreajustar o asumir un riesgo que destruiría el drawdown. Para entender el +250 % de W4 hace falta su código.

