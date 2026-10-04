# W8 — ETH SHORT: resultados de backtest (base W4 + stop más ajustado)

> **Nota de versiones:** este informe sustituye al «W7» entregado antes (rechazo de la EMA20), que queda **descartado**: con los supuestos de tu W4 rinde bastante menos en 1D (+121 % frente a +449 % de W8) y no mejora 1H/4H.

## Veredicto

- **1D: mejora clara y robusta frente a W4.** +250 % → **+449 %** a tu mismo riesgo (5 %) y con el mismo DD (−21,7 % frente a −22,0 %); OOS +38 % → **+66 %**; VALIDATION +25 % → +64 %. A **igual presupuesto de DD in-sample ≤ 25 %** (tu regla): W4 +290 % (riesgo 5,5 %) → W8 **+562 %** (riesgo 5,75 %, DD −24,5 %, OOS +77 %).
- **1H y 4H: mejora moderada.** 1H +517 % → +746 % (OOS +33 % → +47 %); 4H +320 % → +403 % (OOS **−2,6 % → +22,5 %**, DD −26,7 % → −23,9 %). Pero 4H baja en TRAIN (201 % → 181 %) y 1H en VALIDATION (76 % → 70 %), y en 1H/4H la elección de m = 3,0 está parcialmente informada por el OOS.
- El único cambio es el multiplicador `mult` del stop: **3,5 → 2,0 en 1D, 3,0 en 1H y 4H**. Todo lo demás es W4.

## Qué cambia respecto a W4

Un solo parámetro: el multiplicador del stop Chandelier (`mult`, en ATR equivalentes de 4h). **W4 usa 3,5 en todas las temporalidades; W8 usa 2,0 en 1D y 3,0 en 1H y 4H.** Todo lo demás es idéntico a W4.

Elegido como centro de la meseta de cada temporalidad (no el máximo ni el borde de la rejilla).

## Comparación W4 → W8

| TF | Tramo | W4 ret | W8 ret | W4 DD | W8 DD | W8 PF | W8 WR | W8 ops | W8 Sharpe |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | TRAIN | 102.7% | **102.4%** | -18.4% | -21.2% | 1.64 | 50% | 56 | 0.77 |
| 1D | VALIDATION | 25.3% | **63.8%** | -22.0% | -19.8% | 1.63 | 38% | 45 | 0.98 |
| 1D | OOS | 37.9% | **65.7%** | -10.7% | -16.9% | 2.08 | 50% | 24 | 1.22 |
| 1D | TOTAL | 250.2% | **449.3%** | -22.0% | -21.7% | 1.79 | 46% | 125 | 0.92 |
| 4H | TRAIN | 201.3% | **180.7%** | -14.3% | -20.6% | 2.15 | 49% | 74 | 1.31 |
| 4H | VALIDATION | 43.0% | **46.3%** | -23.8% | -15.2% | 1.51 | 45% | 60 | 0.93 |
| 4H | OOS | -2.6% | **22.5%** | -26.7% | -23.9% | 1.26 | 34% | 47 | 0.62 |
| 4H | TOTAL | 319.6% | **403.2%** | -26.7% | -23.9% | 1.53 | 44% | 181 | 1.05 |
| 1H | TRAIN | 164.9% | **240.0%** | -21.1% | -24.2% | 2.13 | 50% | 86 | 1.46 |
| 1H | VALIDATION | 75.7% | **69.7%** | -22.2% | -24.8% | 1.52 | 42% | 69 | 1.10 |
| 1H | OOS | 32.6% | **46.5%** | -23.8% | -24.1% | 1.43 | 40% | 58 | 0.97 |
| 1H | TOTAL | 517.3% | **745.6%** | -23.8% | -24.8% | 1.58 | 45% | 213 | 1.23 |

## Año a año (equity continua)

| Año | ETH 1D | 1D W4 | 1D W8 | 4H W4 | 4H W8 | 1H W4 | 1H W8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | -83% | 84.0% | 95.6% | 120.7% | 130.9% | 94.2% | 142.0% |
| 2019 | -7% | 28.4% | 26.4% | 39.9% | 41.6% | 51.5% | 61.3% |
| 2020 | 463% | -11.9% | -12.3% | -6.0% | -9.9% | -11.3% | -14.2% |
| 2021 | 404% | -2.6% | -6.7% | 3.8% | -4.7% | 1.6% | 1.5% |
| 2022 | -68% | 14.4% | 46.4% | 29.6% | 25.7% | 53.8% | 49.3% |
| 2023 | 90% | 9.5% | 11.9% | 10.3% | 16.4% | 14.3% | 13.7% |
| 2024 | 42% | 43.2% | 76.0% | 14.6% | 27.7% | 28.1% | 31.6% |
| 2025 | -12% | -1.8% | -5.8% | -13.7% | -4.1% | 5.1% | 11.3% |

## Costes y slippage (TOTAL / OOS)

| TF | Versión | costes ×1 | costes ×2 | costes ×3 | slippage ×4 |
|---|---|---:|---:|---:|---:|
| 1D | W4 | 250% / 38% | 221% / 35% | 194% / 33% | 217% / 35% |
| 1D | W8 | 449% / 66% | 344% / 58% | 259% / 51% | 333% / 57% |
| 4H | W4 | 320% / -3% | 258% / -7% | 206% / -12% | 251% / -8% |
| 4H | W8 | 403% / 23% | 312% / 16% | 237% / 10% | 302% / 15% |
| 1H | W4 | 517% / 33% | 412% / 26% | 324% / 19% | 400% / 25% |
| 1H | W8 | 746% / 47% | 557% / 37% | 411% / 27% | 537% / 35% |

## Sensibilidad: 243 variantes alrededor de W8 (régimen 450/600/800, ruptura 30/45/60, pullback 30/40/60, percentil de vol 65/75/85, m ±0,25)

| TF | Tramo | Mín | Mediana | Máx | % positivas |
|---|---|---:|---:|---:|---:|
| 1D | TRAIN | 49% | 108% | 217% | 100% |
| 1D | VALIDATION | 11% | 66% | 151% | 100% |
| 1D | OOS | -11% | 37% | 77% | 98% |
| 1D | TOTAL | 160% | 385% | 753% | 100% |
| 4H | TRAIN | 76% | 165% | 267% | 100% |
| 4H | VALIDATION | -11% | 40% | 104% | 96% |
| 4H | OOS | -21% | 24% | 82% | 86% |
| 4H | TOTAL | 117% | 337% | 606% | 100% |
| 1H | TRAIN | 105% | 207% | 313% | 100% |
| 1H | VALIDATION | 20% | 65% | 130% | 100% |
| 1H | OOS | -12% | 35% | 85% | 96% |
| 1H | TOTAL | 272% | 565% | 1028% | 100% |

## Walk-forward del multiplicador m (2021-25; m elegido cada año solo con años previos por CAGR/DD anual; resto de W4 fijo)

| TF | WFA pooled | W8 fijo | W4 fijo |
|---|---:|---:|---:|
| 1D | 177% | 153% | 72% |
| 4H | 36% | 71% | 47% |
| 1H | 133% | 152% | 140% |

## Frontera de riesgo en 1D (W8, m=2,0)

| Riesgo/op | TOTAL | DD | OOS |
|---|---:|---:|---:|
| 3% | 210% | -13.6% | 37% |
| 4% | 317% | -17.7% | 51% |
| 5% | 449% | -21.7% | 66% |
| 6% | 605% | -25.5% | 81% |
| 7% | 765% | -29.1% | 89% |

## A igual presupuesto de drawdown (riesgo máximo con DD in-sample ≤ 25 %)

| TF | Versión | Riesgo | TRAIN | VALID | OOS | TOTAL | DD total |
|---|---|---:|---:|---:|---:|---:|---:|
| 1D | W4 | 5,5 % | 116,0 % | 27,1 % | 41,9 % | 289,7 % | −24,0 % |
| 1D | **W8 (m=2,0)** | 5,75 % | 121,5 % | 68,8 % | **77,1 %** | **562,4 %** | −24,5 % |

## Contraste con las versiones anteriores (mismos supuestos de W4: riesgo 4/4/5 %, tope 2x, 0,08 %/lado)

| TF | W6 | W7 anterior (rechazo EMA20) | W4 | **W8** |
|---|---:|---:|---:|---:|
| 1H TOTAL (DD) | +1.185 % (DD 40,8 %*) | — | +517 % (−23,8 %) | +746 % (−24,8 %) |
| 4H TOTAL (DD) | +510 % (DD 33,9 %*) | — | +320 % (−26,7 %) | +403 % (−23,9 %) |
| 1D TOTAL (DD) | +42 % (DD 20,6 %*) | +121 % (DD 19,2 %*) | +250 % (−22,0 %) | +449 % (−21,7 %) |

\* DD medido con mi motor (máximo de la barra, más conservador que el cierre del tuyo): no es directamente comparable. W6 da más rentabilidad bruta en 1H/4H, pero con más drawdown; no la he normalizado a igual presupuesto, así que no afirmo que sea peor ni mejor que W8 en esas dos temporalidades.

## Qué se probó sobre W4 y se descartó

Con riesgo fijo, ninguna de estas variantes mejoró los tres tramos a la vez (solo m = 2,5 lo hizo en 1D): régimen EMA 300/450/800, ruptura 30/60/90, pullback EMA 20/30/60, sin filtro de volatilidad / percentil 65 / 85 / ventana 375 / 1500, cooldown tras stop, y añadir el rechazo EMA20 como tercera entrada. Ruptura 30, ventana de volatilidad 375 y el rechazo EMA20 suben el total (hasta +1.132 % a riesgo 6,5 %) pero **empeoran el OOS** (+31 % frente a +42 % de W4): son sobreajuste a 2018.

## Advertencias

- **Stops más ajustados = más operaciones** (1D: 90 → 125) y más exposición a gaps y fallos de stop en mercados rápidos. Aguanta costes ×3 y slippage ×4, pero no modelo funding ni ejecución real.
- La elección de m en 1H/4H se apoya en una meseta amplia (2,75–3,25), pero la mejora del OOS de 4H solo existe en el OOS.
- El walk-forward de m en 4H queda por debajo del m fijo (+36 % frente a +71 %): la elección anual con datos pasados es ruidosa ahí.
- Los tests limpios siguen siendo tus datos de TradingView de 2015-2017 y ene-oct 2026.
