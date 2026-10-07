# W10 — ETH SHORT: resultados de backtest (W9 + percentil de volatilidad por temporalidad)

**Motor:** el de tu `backtest_w4.py` (calibrado: reproduce W4 y W8 exactos, W9 exacto en 1D y 4H y con un 0,5 % de diferencia en 1H). CSV de Binance 2017-08-17 → 2026-01-06 (1H 73.414 · 4H 18.371 · 1D 3.065 velas). **Tramos:** TRAIN 2017-08→2021-12 · VALIDATION 2022-2023 · OOS 2024→2026-01. **Costes:** 0,05 % comisión + 0,03 % slippage por lado, tope 2x.

> **Corrección:** en una respuesta anterior de esta sesión dije que no tenía el código de W8/W9. Era falso: estaba en los documentos del proyecto y no lo había mirado. Todo lo anterior hecho con una base reconstruida queda descartado; lo de abajo usa tu motor real.

## Veredicto

- **Un solo cambio respecto a W9:** percentil máximo del filtro de volatilidad **1D 0,75 → 0,70**, **1H 0,75 → 0,65**, **4H sin cambios (0,75)**.
- **No es una mejora «grande» por temporalidad.** A igual riesgo: 1D +472 % → +500 % (PF 1,99 → 2,20, OOS +65 % → +77 %); 1H +740 % → +887 % (PF 1,87 → 2,21, DD −21,3 % → −17,6 %, OOS +65 % → +80 %); 4H igual que W9. La rejilla, el walk-forward y las salidas alternativas indican que dentro de esta familia de reglas no queda más ganancia robusta.
- **La mejora grande está en combinar las tres temporalidades** (sin parámetros nuevos): a igual DD in-sample (~24 %), cartera W10 **+1.807 % / OOS +94 %** frente a **+1.126 % / OOS +70 %** de la cartera W9.

## A) Mismo riesgo (1D 5 % · 4H 4 % · 1H 6 %; W8 con su riesgo base 5/4/4)

| TF | Versión | Riesgo | TRAIN | VALID | OOS (DD) | TOTAL | DD | PF | WR | Ops | Med/op |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | W8 | 5 % | 102,4 % | 63,8 % | 65,7 % (−16,9) | 449,3 % | −21,7 % | 1,79 | 45,6 % | 125 | 1,57 % |
| 1D | W9 | 5 % | 106,9 % | 67,7 % | 65,0 % (−8,8) | 472,3 % | −20,6 % | 1,99 | 48,2 % | 112 | 1,77 % |
| 1D | **W10** | 5 % | 96,8 % | 72,8 % | **76,6 %** (−8,8) | **500,3 %** | −20,6 % | **2,20** | 49,5 % | 103 | **1,97 %** |
| 4H | W8 = W9 = W10 | 4 % | 180,7 % | 46,3 % | 22,5 % (−23,9) | 403,2 % | −23,9 % | 1,53 | 43,6 % | 181 | 1,01 % |
| 1H | W8 | 4 % | 240,0 % | 69,7 % | 46,5 % (−24,1) | 745,6 % | −24,8 % | 1,58 | 44,6 % | 213 | 1,13 % |
| 1H | W9 | 6 % | 194,6 % | 72,4 % | 65,5 % (−18,4) | 740,3 % | −21,3 % | 1,87 | 53,4 % | 131 | 1,83 % |
| 1H | **W10** | 6 % | 219,4 % | 71,6 % | **80,0 %** (−13,8) | **886,8 %** | **−17,6 %** | **2,21** | **56,5 %** | 115 | **2,22 %** |

Coste de W10 en 1D: TRAIN baja de 106,9 % a 96,8 % (se evitan entradas de alta volatilidad que en 2018 eran rentables). Menos operaciones (112 → 103 en 1D; 131 → 115 en 1H), pero de más calidad.

## B) Mismo presupuesto de DD (DD in-sample ≤ 25 %, riesgo en pasos de 0,25 %)

| TF | Versión | Riesgo | TRAIN | VALID | OOS (DD) | TOTAL | DD | PF | WR | Ops |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1D | W9 | 6,00 % | 134,8 % | 76,6 % | 80,2 % (−10,5) | 647,1 % | −24,2 % | 1,95 | 48,2 % | 112 |
| 1D | **W10** | 6,00 % | 121,2 % | 83,0 % | **95,6 %** (−10,5) | **691,6 %** | −24,2 % | 2,17 | 49,5 % | 103 |
| 1H | W9 | 7,00 % | 245,9 % | 84,0 % | 75,9 % (−21,2) | 1.019,6 % | −24,5 % | 1,82 | 53,4 % | 131 |
| 1H | W10 | 10,00 %* | 479,5 % | 120,1 % | 122,7 % (−22,0) | 2.740,4 % | −24,9 % | 2,01 | 56,5 % | 115 |

\* **No compares el 2.740 % con el 1.020 % como si fuera pura mejora de edge:** a riesgo nominal 10 % el tope de 2x limita el 33 % de las operaciones y el apalancamiento medio sube a ~1,65x (W9 ~1,25x). La comparación limpia en 1H es la de la tabla A (mismo riesgo, apalancamiento medio ~1,1x en ambas) o W10 a 7 %: **+1.258 % con DD −19,0 %** frente a +1.020 % con DD −24,5 %.

## Qué se probó y qué se descartó

| Idea | Resultado |
|---|---|
| Rejilla completa de ejes (régimen, ruptura, pullback, m, percentil, extensión, salida por régimen) | La correlación de rangos IS→OOS entre configuraciones es +0,33 en 1D, +0,07 en 4H y **−0,44 en 1H**: afinar parámetros en 1H es sobreajuste. |
| Walk-forward 2021-25 eligiendo cada año con datos previos | **Todos los ejes a la vez empeora a W9 fijo en las tres TF** (1D 86 % vs 158 %, 4H 59 % vs 71 %, 1H 95 % vs 119 %). Solo cambios de un eje y estables año a año aportan. |
| m más bajo en 1D (1,5) | IS muy mejor, OOS igual (66 % vs 65 %) con DD OOS −19 % vs −9 % y más apalancamiento: **solo mejora histórica, descartado**. |
| Percentil 0,70 en 4H | Acantilado en 0,65; vecindario de 81 variantes **peor** que el de W9 (mediana 290 % vs 349 %): **descartado**. |
| EMA de régimen 450–800 | 600 está en el pico en 4H y 1H; en 1D las diferencias son ruido. |
| Salida por cierre sobre la EMA de régimen | Mejora pequeña y del mismo signo en las tres TF (+4 %, +9 %, +30 % a igual presupuesto), pero añade un grado de libertad; no incluida. |
| Stop tipo Donchian, trailing adaptativo, cooldown, ruptura ≥ x ATR, vela bajista, TP parcial en 1D/4H, tope de apalancamiento 3x | Sin mejora robusta: la estructura de salida está agotada. |
| Condicionar por pendiente de la EMA, edad del régimen o extensión | Casi todos los buckets se comportan al revés en IS y en OOS (p. ej. EMA subiendo: peor en IS, mejor en OOS): sería sobreajuste. |

## Estrés de W10

- **Costes y slippage:** W10 ≥ W9 en 1D y 1H en todos los escenarios (×1, ×2, ×3 y slippage ×4). Por ejemplo, costes ×3 en 1D: ~319 % vs ~290 %; en 1H: ~570 % vs ~445 %.
- **Vecindario de 81 variantes** (régimen 450/600/800 × ruptura 30/45/60 × percentil ±0,05 × m ±0,25, a riesgo W9): 1D OOS mediano 46 % vs 39 % y mínimo 18 % vs 2 %; 1H TOTAL mediano 572 % vs 500 %, PF mediano 2,08 vs 1,85, DD mediano −20,9 % vs −22,3 %.
- **Config fija en 2021-25 (riesgo 5/4/4):** 1D 185 % (W9 158 %, W8 153 %); 1H 130 % (W9 119 %, **W8 152 %**).
- **Año a año:** las mejoras vienen de años malos (1H 2020 −3,7 % vs −12,3 %; 1D 2025 +1,2 % vs −3,6 %; 1H 2024 +58 % vs +41 %) a costa de algo menos en 2018.

## Cartera 1D + 4H + 1H (1/3 del capital por temporalidad, cada subcuenta compone la suya)

Correlación de retornos diarios entre temporalidades: 0,47–0,71. Riesgo por operación = el de cada versión × λ.

| Cartera | λ | Riesgos (1D / 4H / 1H) | TOTAL | DD IS | OOS (DD) |
|---|---:|---|---:|---:|---:|
| W9 | 1,5 | 7,5 % / 6 % / 9 % | 1.126 % | −24,2 % | +70 % |
| W10 | 1,5 | 7,5 % / 6 % / 9 % | 1.330 % | −20,3 % | **+89 %** (−14,8 %) |
| W10 | 1,75 | 8,75 % / 7 % / 10,5 % | 1.807 % | −23,7 % | +94 % |
| W10 | 2,0 | 10 % / 8 % / 12 % | 2.220 % | −26,9 % | — |

Recomendación: **λ = 1,5**, que deja margen frente al 25 %. Medido con equity de cierre diario (el DD intradía de 1H/4H puede ser algo mayor). Cada gráfico necesita su propia instancia con su capital inicial.

## Advertencias

- **Evidencia 1D débil:** el OOS de 1D tiene ~20 operaciones y no discrimina entre W9 y W10 por sí solo. El respaldo es la meseta (0,65–0,75), la coherencia con 1H y el walk-forward con config fija. El walk-forward que *elige* el percentil en 1D dio 125 % < 158 %, es decir, la selección automática no lo respalda.
- **1H reciente:** en los últimos 12 meses del CSV W10 hace +13,9 % (DD −11,4 %) frente a +17,4 % (DD −15,7 %) de W9, y −2,3 % frente a +1,1 % en 6 meses. **W10 no mejora el rendimiento reciente de 1H** en el tramo visible. El −21 % de W9 que ves en TradingView cae en ene–oct 2026, fuera de mis CSV (terminan el 6 ene 2026), así que no puedo diagnosticarlo.
- **Test limpio pendiente:** corre W10 en TradingView sobre ene–oct 2026 sin tocar nada; es el único OOS que ni tú ni yo hemos usado para elegir.
- **No verificado en TradingView:** el Pine es W9 con tres inputs nuevos y no lo he podido compilar aquí. El backtest tampoco modela funding ni ejecución real; el emulador de TradingView puede resolver distinto la toma parcial de 1H.
- **Más trades bajos en volatilidad = posiciones más grandes:** el filtro más estricto selecciona entradas con stop corto en %, lo que sube el apalancamiento medio a igual riesgo nominal.
