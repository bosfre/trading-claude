# W5 — ETH SHORT: resultados de backtest

**Datos:** ETHUSDT Binance, 2017-08-17 → 2026-01-06 (1H: 73.414 velas · 4H: 18.371 · 1D: 3.065).  
**Motor:** short-only, señal al cierre y entrada en la apertura siguiente, stops intrabarra (gap incluido), riesgo 3 % por operación, tope 10x, costes 0,05 % comisión + 0,02 % slippage por lado, capital 10.000 reiniciado en cada tramo.  
**Tramos:** TRAIN 2017-08→2020-12 · VALID 2021-01→2023-06 · OOS 2023-07→2026-01.  
**W4~** = reconstrucción de la lógica w1/W4 (EMA200 + breakdown 75 barras + ATR14 + Chandelier 3,5) en este mismo motor; no es el código real de W4, por lo que las cifras absolutas no coinciden con TradingView, pero la comparación W4~ vs W5 es homogénea.

> **Aviso de integridad:** la selección final de W5 usó los tres tramos (el OOS dejó de ser limpio tras la primera evaluación del candidato inicial, que lo suspendió). La evidencia de robustez es la meseta de parámetros, el rendimiento año a año y el estrés de costes, no un OOS puro. El test limpio es el periodo ene–oct 2026 de TradingView, que no está en estos CSV.


## 1H

| Tramo | Versión | Rentab. | DD máx | PF | Win rate | Nº ops | Ret/DD | Sharpe | Sortino |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | W4~ | 53.3% | 29.4% | 1.22 | 34% | 173 | 1.81 | 0.61 | 1.07 |
| TRAIN | **W5** | 294.3% | 31.1% | 3.88 | 34% | 38 | 9.47 | 1.20 | 1.08 |
| VALID | W4~ | -8.5% | 30.0% | 0.93 | 32% | 133 | -0.28 | -0.06 | -0.08 |
| VALID | **W5** | 50.9% | 28.2% | 1.67 | 21% | 24 | 1.81 | 0.69 | 0.52 |
| OOS | W4~ | 58.0% | 23.2% | 1.36 | 40% | 124 | 2.50 | 0.85 | 1.48 |
| OOS | **W5** | 76.8% | 30.3% | 2.05 | 39% | 23 | 2.53 | 0.93 | 0.55 |
| FULL | W4~ | 121.5% | 45.2% | 1.18 | 35% | 430 | 2.69 | 0.50 | 0.82 |
| FULL | **W5** | 951.8% | 31.1% | 2.14 | 32% | 85 | 30.62 | 0.98 | 0.76 |

**Año a año (capital reiniciado cada año):**

| Año | ETH | W4~ | W5 | W5 DD | W5 ops |
|---|---:|---:|---:|---:|---:|
| 2018 | -82% | 117.2% | 159.1% | 31.1% | 22 |
| 2019 | -2% | -3.3% | 41.7% | 18.2% | 10 |
| 2020 | 471% | -10.8% | 21.7% | 14.5% | 2 |
| 2021 | 401% | -22.7% | -13.7% | 14.7% | 6 |
| 2022 | -68% | 23.2% | 86.8% | 27.1% | 16 |
| 2023 | 91% | -0.7% | 12.3% | 17.6% | 6 |
| 2024 | 45% | 35.9% | 31.2% | 18.2% | 5 |
| 2025 | -12% | 12.4% | 12.4% | 30.3% | 14 |

**Estrés de costes (FULL):** ×1: 952% (DD 31%) · ×2: 801% (DD 33%) · ×3: 671% (DD 34%)

**Perturbación ±1 paso en L, ks, kt (27 vecinos):** TRAIN: mín 55%, mediana 268%, 100% positivos · VALID: mín 31%, mediana 66%, 100% positivos · OOS: mín -4%, mediana 46%, 96% positivos

## 4H

| Tramo | Versión | Rentab. | DD máx | PF | Win rate | Nº ops | Ret/DD | Sharpe | Sortino |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | W4~ | 40.4% | 10.5% | 2.18 | 44% | 36 | 3.84 | 0.91 | 0.80 |
| TRAIN | **W5** | 105.6% | 14.6% | 3.74 | 48% | 29 | 7.23 | 1.15 | 0.85 |
| VALID | W4~ | 20.4% | 7.4% | 2.24 | 41% | 27 | 2.76 | 0.77 | 0.65 |
| VALID | **W5** | 3.0% | 20.1% | 1.07 | 27% | 22 | 0.15 | 0.15 | 0.09 |
| OOS | W4~ | -8.8% | 13.9% | 0.73 | 37% | 35 | -0.63 | -0.40 | -0.27 |
| OOS | **W5** | 26.8% | 12.1% | 1.92 | 41% | 17 | 2.21 | 0.81 | 0.55 |
| FULL | W4~ | 54.2% | 14.5% | 1.48 | 41% | 98 | 3.74 | 0.55 | 0.45 |
| FULL | **W5** | 168.3% | 21.2% | 1.88 | 40% | 68 | 7.93 | 0.77 | 0.51 |

**Año a año (capital reiniciado cada año):**

| Año | ETH | W4~ | W5 | W5 DD | W5 ops |
|---|---:|---:|---:|---:|---:|
| 2018 | -82% | 46.3% | 78.0% | 14.6% | 16 |
| 2019 | -2% | 0.8% | 12.2% | 10.8% | 9 |
| 2020 | 466% | 1.2% | 12.9% | 7.0% | 1 |
| 2021 | 394% | 0.3% | -10.4% | 10.4% | 5 |
| 2022 | -68% | 19.3% | 22.5% | 20.1% | 15 |
| 2023 | 91% | 0.4% | -5.5% | 8.5% | 5 |
| 2024 | 47% | -8.1% | 14.3% | 9.2% | 4 |
| 2025 | -11% | 0.9% | 10.1% | 12.1% | 10 |

**Estrés de costes (FULL):** ×1: 168% (DD 21%) · ×2: 151% (DD 22%) · ×3: 134% (DD 24%)

**Perturbación ±1 paso en L, ks, kt (27 vecinos):** TRAIN: mín 34%, mediana 92%, 100% positivos · VALID: mín -14%, mediana 11%, 85% positivos · OOS: mín -19%, mediana 1%, 56% positivos

## 1D

| Tramo | Versión | Rentab. | DD máx | PF | Win rate | Nº ops | Ret/DD | Sharpe | Sortino |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | W4~ | 7.5% | 3.4% | 5.12 | 67% | 6 | 2.22 | 0.67 | 0.45 |
| TRAIN | **W5** | 16.6% | 7.2% | 5.12 | 67% | 6 | 2.30 | 0.75 | 0.63 |
| VALID | W4~ | 2.9% | 5.2% | 1.69 | 50% | 4 | 0.57 | 0.38 | 0.23 |
| VALID | **W5** | 2.5% | 10.2% | 1.31 | 40% | 5 | 0.24 | 0.20 | 0.12 |
| OOS | W4~ | 0.5% | 2.9% | 1.95 | 75% | 4 | 0.16 | 0.08 | 0.04 |
| OOS | **W5** | 4.2% | 5.2% | 2.50 | 50% | 4 | 0.81 | 0.29 | 0.18 |
| FULL | W4~ | 11.2% | 6.2% | 2.62 | 64% | 14 | 1.79 | 0.42 | 0.25 |
| FULL | **W5** | 24.5% | 13.0% | 2.48 | 53% | 15 | 1.89 | 0.45 | 0.31 |

**Año a año (capital reiniciado cada año):**

| Año | ETH | W4~ | W5 | W5 DD | W5 ops |
|---|---:|---:|---:|---:|---:|
| 2018 | -83% | 8.2% | 19.8% | 5.7% | 3 |
| 2019 | -7% | 1.3% | 2.9% | 3.4% | 2 |
| 2020 | 463% | -1.2% | -3.0% | 3.0% | 1 |
| 2021 | 404% | 0.0% | 0.0% | 0.0% | 0 |
| 2022 | -68% | 5.7% | 5.7% | 7.4% | 4 |
| 2023 | 90% | -2.6% | -4.9% | 4.9% | 2 |
| 2024 | 42% | -0.5% | 0.3% | 4.2% | 1 |
| 2025 | -12% | 0.9% | 6.0% | 5.2% | 2 |

**Estrés de costes (FULL):** ×1: 25% (DD 13%) · ×2: 24% (DD 13%) · ×3: 23% (DD 13%)

**Perturbación ±1 paso en L, ks, kt (27 vecinos):** TRAIN: mín 2%, mediana 10%, 100% positivos · VALID: mín -2%, mediana 5%, 93% positivos · OOS: mín -9%, mediana -1%, 37% positivos
