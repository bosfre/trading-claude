# VW1 — backtest conjunto (LONG V10 + SHORT W10 en una sola cuenta)

Fecha: 2026-11-24. Código y CSV: [`backtest_vw1/`](backtest_vw1/). Pre-registro (escrito antes de ejecutar): [`backtest_vw1/vw1_prereg.txt`](backtest_vw1/vw1_prereg.txt).

## Veredicto

**Los dos perfiles casi no se estorban y, en la ventana completa, VW1 tiene mejor Calmar que cada uno por separado en las tres temporalidades. Pero esa ventaja está concentrada en 2017-2021 (TRAIN): fuera de muestra (2024-26) la rentabilidad es mayor, el Calmar no lo es siempre. Todo es simulación en Python; el test que falta es el de TradingView.**

- **V10 y W10 casi nunca están dentro a la vez** (con cuentas separadas coincidirían en 0,5 %–0,7 % de las barras). Por eso la regla «una sola posición, sin invertir» cuesta poco: **0 entradas LONG perdidas** y **6,5 %–9,1 % de las SHORT** (según temporalidad).
- Al usar el mismo capital en momentos distintos, **las tasas de crecimiento se suman** y el drawdown apenas sube. Con costes 0,08 % por lado, 2017-08 → 2026-10: **1H 14.990 % / DD -24,8 %; 4H 6.026 % / DD -26,6 %; 1D 3.506 % / DD -27,5 %.** Calmar de VW1 2,96 / 2,14 / 1,75 (V10 sola 1,84 / 1,84 / 1,03; W10 sola 1,27 / 0,79 / 0,88).
- **Los cinco criterios pre-registrados (C1–C5) se cumplen** en las tres temporalidades, también con costes ×2 y ×3. La variante con inversión de posición (VW1-flip) **no** supera el criterio y se descarta.
- **Tres matices que no se deben perder:** (1) **por tramos, el Calmar de VW1 supera al del mejor componente en 3/3 temporalidades en TRAIN, 2/3 en VAL, 1/3 en OOS1 y 3/3 en OOS2** (OOS1: 1H 2,76 vs 2,54; 4H 1,23 vs 1,84; 1D 2,11 vs 3,74). Este análisis por tramo no estaba en el pre-registro: se informa como hallazgo, no como criterio superado ni fallado. Fuera de muestra VW1 gana en rentabilidad (porque suma los dos lados) pero también sube el DD; por eso la mejora de calidad no está demostrada de forma independiente del periodo. (2) en **4H** el SHORT es el eslabón débil (W10 sola: Calmar 0,79, PF 1,5) y en OOS1 (2024→2026-01) VW1 4H rinde 77,5 % frente a 72,3 % de V10 sola, con DD -26,6 % frente a -16,7 %: casi no aporta ahí. (3) **El DD de VW1 es algo mayor que el de sus componentes** (entre 0,2 y 4,1 puntos porcentuales por encima del peor de los dos), y el remuestreo de operaciones sitúa el DD mediano en −26 % y el 5 % peor en −39 % / −41 %: planifica drawdowns de 35-45 %.

## 1. Qué se ha medido

- **VW1** = LONG V10 (Donchian 140 h + EMA 800 h + filtro BTC > EMA 800 h, stop/trailing 5 ATR, TP 20 ATR, riesgo 5 %) + SHORT W10 (régimen EMA 600, ruptura de mínimos | pullback fallido, filtro de volatilidad, stop Chandelier; riesgo 1D 5 % / 4H 4 % / 1H 6 %). Mismos parámetros que sus versiones por separado; **no se ha tocado nada**.
- **Reglas del conjunto** (las del Pine VW1): una sola cuenta y una sola posición; con una posición abierta se ignoran las señales del lado contrario; si coinciden señal LONG y SHORT en la misma barra estando plano, no se opera.
- **Se compara con:** A = V10 sola, B = W10 sola (mismo motor, mismos costes), E = reparto 50/50 en dos cuentas independientes (referencia teórica: no es ejecutable en un solo gráfico) y D = VW1-flip (una única variante alternativa).
- **Datos:** ETH 1H/4H/1D de Binance (`csvs/`) 2017-08-17 → 2026-01-06 + tramo 2026-01 → 2026-10-03 de Twelve Data (el mismo que usó V10). **Tramos:** TRAIN 2017-08→2021-12, VAL 2022-23, OOS1 2024-01→2026-01-10, OOS2 2026-01-11→2026-10-03. Para el LONG no existe OOS virgen (V10 ya los había visto como descripción); para el SHORT, OOS2 no se había abierto antes y aquí solo se describe, no se ha usado para elegir nada.
- **Costes principales («pine»):** comisión 0,08 % por lado y slippage 0, sin funding: lo que declara el `strategy()` de VW1. Se repite con los costes originales de cada motor («orig») y con costes ×2 y ×3.

## 2. Validación del motor

Antes de medir nada conjunto, el motor se comprobó con un solo lado activo y las convenciones de cada motor original:

| Lado | TF | Original: rent. | DD | ops | Motor VW: rent. | DD | ops | dif. máx. equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LONG V10 | 1H | 1.431,08 % | -21,81 % | 143 | 1.431,08 % | -21,81 % | 143 | 0e+00 |
| LONG V10 | 4H | 1.010,59 % | -17,60 % | 126 | 1.010,59 % | -17,60 % | 126 | 0e+00 |
| LONG V10 | 1D | 483,23 % | -23,43 % | 105 | 483,23 % | -23,43 % | 105 | 0e+00 |
| SHORT W10 | 1H | 880,47 % | -17,65 % | 115 | 880,47 % | -17,65 % | 115 | 8e-16 |
| SHORT W10 | 4H | 403,21 % | -23,89 % | 181 | 403,21 % | -23,89 % | 181 | 1e-15 |
| SHORT W10 | 1D | 500,31 % | -20,63 % | 103 | 500,31 % | -20,63 % | 103 | 7e-16 |

La curva de equity coincide a precisión de máquina con los motores `eng10` (V10) y `backtest_w11` (W10). Además, en las pruebas conjuntas: ninguna operación se solapa con otra, la equity final es el producto de los retornos de las operaciones (diferencia < 1e-14) y el tamaño nunca supera 2x.

## 3. Resultados con costes 0,08 % por lado (modelo «pine»)

Rentabilidad / drawdown máximo por tramo. Cada tramo se mide sobre la misma curva continua de equity.

### 1H

| Escenario | TRAIN 2017-08→2021 | VAL 2022-23 | OOS1 2024→2026-01-10 | OOS2 2026-01-11→10-03 | FULL 2017-08→2026-10 |
|---|---:|---:|---:|---:|---:|
| V10 sola | 599 % / -17,1 % | 27 % / -16,2 % | 81 % / -16,5 % | 12 % / -11,5 % | 1.699 % / -20,2 % |
| W10 sola | 219 % / -13,7 % | 71 % / -17,6 % | 84 % / -13,8 % | 2 % / -22,9 % | 928 % / -22,9 % |
| **VW1** | 2.208 % / -17,1 % | 94 % / -24,8 % | 157 % / -21,5 % | 31 % / -21,1 % | 14.990 % / -24,8 % |
| 50/50 en cuentas separadas | 409 % / -8,7 % | 41 % / -14,1 % | 82 % / -11,3 % | 8 % / -11,9 % | 1.314 % / -14,1 % |

### 4H

| Escenario | TRAIN 2017-08→2021 | VAL 2022-23 | OOS1 2024→2026-01-10 | OOS2 2026-01-11→10-03 | FULL 2017-08→2026-10 |
|---|---:|---:|---:|---:|---:|
| V10 sola | 395 % / -15,0 % | 33 % / -10,7 % | 72 % / -16,7 % | 2 % / -10,6 % | 1.060 % / -16,7 % |
| W10 sola | 181 % / -20,6 % | 46 % / -15,2 % | 24 % / -24,4 % | 11 % / -22,2 % | 468 % / -26,4 % |
| **VW1** | 1.388 % / -15,0 % | 91 % / -23,7 % | 77 % / -26,6 % | 21 % / -24,4 % | 6.026 % / -26,6 % |
| 50/50 en cuentas separadas | 288 % / -7,9 % | 38 % / -11,0 % | 54 % / -12,0 % | 5 % / -11,3 % | 764 % / -12,6 % |

### 1D

| Escenario | TRAIN 2017-08→2021 | VAL 2022-23 | OOS1 2024→2026-01-10 | OOS2 2026-01-11→10-03 | FULL 2017-08→2026-10 |
|---|---:|---:|---:|---:|---:|
| V10 sola | 290 % / -13,5 % | 34 % / -16,2 % | 40 % / -17,1 % | -7 % / -8,9 % | 580 % / -22,7 % |
| W10 sola | 97 % / -15,9 % | 73 % / -20,6 % | 78 % / -8,8 % | -8 % / -23,4 % | 455 % / -23,4 % |
| **VW1** | 708 % / -19,4 % | 118 % / -21,7 % | 113 % / -21,4 % | -4 % / -17,5 % | 3.506 % / -27,5 % |
| 50/50 en cuentas separadas | 193 % / -11,0 % | 47 % / -12,2 % | 55 % / -13,0 % | -8 % / -12,4 % | 518 % / -18,8 % |

**Calidad (ventana FULL 2017-08 → 2026-10, costes ×1):**

| TF | Escenario | CAGR | DD | Calmar | PF ($) | Acierto | Operaciones | Tiempo en mercado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1H | V10 sola | 37,2 % | -20,2 % | 1,84 | 2,03 | 43 % | 141 | 29 % |
| 1H | W10 sola | 29,1 % | -22,9 % | 1,27 | 1,79 | 54 % | 143 | 14 % |
| 1H | **VW1** | 73,3 % | -24,8 % | 2,96 | 1,79 | 49 % | 271 | 42 % |
| 1H | 50/50 en cuentas separadas | 33,7 % | -14,1 % | 2,39 | — | — | — | — |
| 4H | V10 sola | 30,8 % | -16,7 % | 1,84 | 2,10 | 44 % | 126 | 29 % |
| 4H | W10 sola | 21,0 % | -26,4 % | 0,79 | 1,45 | 41 % | 214 | 21 % |
| 4H | **VW1** | 57,0 % | -26,6 % | 2,14 | 1,55 | 43 % | 326 | 48 % |
| 4H | 50/50 en cuentas separadas | 26,7 % | -12,6 % | 2,12 | — | — | — | — |
| 1D | V10 sola | 23,4 % | -22,7 % | 1,03 | 1,82 | 47 % | 101 | 28 % |
| 1D | W10 sola | 20,7 % | -23,4 % | 0,88 | 1,57 | 45 % | 128 | 8 % |
| 1D | **VW1** | 48,1 % | -27,5 % | 1,75 | 1,57 | 47 % | 219 | 36 % |
| 1D | 50/50 en cuentas separadas | 22,1 % | -18,8 % | 1,17 | — | — | — | — |

(El 50/50 no tiene operaciones propias en una sola lista, de ahí los guiones.)

**Calmar por tramo (VW1 frente a la mejor de las dos por separado):**

| TF | TRAIN | VAL | OOS1 | OOS2 |
|---|---:|---:|---:|---:|
| 1H | 6,15 vs 3,28 | 1,58 vs 1,75 | 2,76 vs 2,54 | 2,16 vs 1,45 |
| 4H | 5,71 vs 2,94 | 1,62 vs 1,43 | 1,23 vs 1,84 | 1,24 vs 0,71 |
| 1D | 3,16 vs 2,70 | 2,20 vs 1,53 | 2,11 vs 3,74 | -0,30 vs -0,48 |

OOS2 son solo ~9 meses: el Calmar anualizado de un tramo tan corto es indicativo, no concluyente. **Lectura:** el Calmar de VW1 supera al del mejor componente en 3/3 TF en TRAIN, 2/3 en VAL, 1/3 en OOS1 y 3/3 en OOS2. En 2024→2026-01 VW1 rinde más que cualquiera de los dos por separado en las tres TF, pero con un DD mayor (1H -21,5 %, 4H -26,6 %, 1D -21,4 %), y en 4H y 1D la rentabilidad extra no compensa ese DD. Es exactamente el tipo de mejora que la regla del proyecto manda no dar por buena sin más: la ventaja de Calmar de la ventana FULL viene sobre todo del TRAIN.

## 4. Solapamiento: qué cuesta la regla «una posición, sin invertir»

| TF | Ops LONG (sola → VW1) | Pérdida | Ops SHORT (sola → VW1) | Pérdida | Entradas SHORT con LONG abierto | Conflictos misma barra | Tiempo V10 | Tiempo W10 | Solape si fueran cuentas separadas | Tiempo VW1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1H | 141 → 141 | 0,0 % | 143 → 130 | 9,1 % | 22 | 0 | 29 % | 14 % | 0,7 % | 42 % |
| 4H | 126 → 126 | 0,0 % | 214 → 200 | 6,5 % | 24 | 0 | 29 % | 21 % | 0,7 % | 48 % |
| 1D | 101 → 101 | 0,0 % | 128 → 118 | 7,8 % | 16 | 0 | 28 % | 8 % | 0,5 % | 36 % |

Todo el coste lo paga el SHORT. Explicación probable (no comprobada): una ruptura alcista de 140 h sobre la EMA 800 h suele llegar cuando un SHORT ya habría sido sacado por su stop, mientras que un SHORT nuevo sí puede aparecer con un LONG todavía abierto. De las operaciones de W10 sola, VW1 deja de tomar 24 / 26 / 17 (1H / 4H / 1D) y toma 11 / 12 / 7 que W10 sola no habría tomado (al estar plana antes, entra en señales que W10 sola no podía aprovechar): el saldo neto es el de la tabla.

**Eficiencia de la combinación:** si V10 y W10 corrieran en el mismo capital sin estorbarse, el resultado sería el producto de los dos multiplicadores. VW1 conserva 82 % (1H), 93 % (4H) y 95 % (1D) de ese producto.

## 5. Criterios pre-registrados

| Criterio | Qué exige | Resultado | Detalle |
|---|---|---|---|
| C1 | pérdida de operaciones por solapamiento < 20 % en cada lado | CUMPLE | 1h: long 0,0 %, short 9,1 %; 4h: long 0,0 %, short 6,5 %; 1d: long 0,0 %, short 7,8 % |
| C2 | Calmar FULL de VW1 > el de A y B en >=2 de 3 TF | CUMPLE | 1h: VW1 2,96 vs V10 1,84 / W10 1,27; 4h: VW1 2,14 vs V10 1,84 / W10 0,79; 1d: VW1 1,75 vs V10 1,03 / W10 0,88 |
| C3 | en TRAIN, VAL y OOS1, ret(VW1) >= mejor de A/B en >=2 de 3 TF | CUMPLE | TRAIN: 3/3 (1h 2208 % vs 599 %; 4h 1388 % vs 395 %; 1d 708 % vs 290 %) | VAL: 3/3 (1h 94 % vs 71 %; 4h 91 % vs 46 %; 1d 118 % vs 73 %) | OOS1: 3/3 (1h 157 % vs 84 %; 4h 77 % vs 72 %; 1d 113 % vs 78 %) |
| C4 | con costes x2 y x3: Calmar > 1 y rentabilidad > 0 en las 3 TF | CUMPLE | x2 1h: Calmar 2,46, ret 10356 %; x2 4h: Calmar 1,88, ret 4276 %; x2 1d: Calmar 1,44, ret 2581 %; x3 1h: Calmar 1,90, ret 7141 %; x3 4h: Calmar 1,64, ret 3025 %; x3 1d: Calmar 1,16, ret 1892 % |
| C5 | DD de VW1 no supera el mayor de A/B en más de 5 pp | CUMPLE | 1h: VW1 24,8 % vs max(A,B) 22,9 % (dif +1,9 pp); 4h: VW1 26,6 % vs max(A,B) 26,4 % (dif +0,2 pp); 1d: VW1 27,5 % vs max(A,B) 23,4 % (dif +4,1 pp) |
| D | VW1-flip supera a VW1 en Calmar en TRAIN, VAL y OOS1 a la vez en >=2 de 3 TF (si no, se descarta) | NO CUMPLE | 1h: D>C en VAL,OOS1; 4h: D>C en VAL,OOS1; 1d: D>C en OOS1 |
| C2 (orig) | Calmar FULL de VW1 > el de A y B en >=2 de 3 TF | CUMPLE | 1h: VW1 2,68 vs V10 1,54 / W10 1,27; 4h: VW1 2,02 vs V10 1,62 / W10 0,79; 1d: VW1 1,64 vs V10 0,92 / W10 0,88 |
| C3 (orig) | en TRAIN, VAL y OOS1, ret(VW1) >= mejor de A/B en >=2 de 3 TF | CUMPLE | TRAIN: 3/3 (1h 2050 % vs 551 %; 4h 1295 % vs 363 %; 1d 664 % vs 268 %) | VAL: 3/3 (1h 85 % vs 71 %; 4h 84 % vs 46 %; 1d 111 % vs 73 %) | OOS1: 3/3 (1h 129 % vs 84 %; 4h 70 % vs 65 %; 1d 105 % vs 78 %) |
| C5 (orig) | DD de VW1 no supera el mayor de A/B en más de 5 pp | CUMPLE | 1h: VW1 25,6 % vs max(A,B) 22,9 % (dif +2,7 pp); 4h: VW1 26,9 % vs max(A,B) 26,4 % (dif +0,5 pp); 1d: VW1 28,1 % vs max(A,B) 23,4 % (dif +4,7 pp) |
| D (orig) | VW1-flip supera a VW1 en Calmar en TRAIN, VAL y OOS1 a la vez en >=2 de 3 TF (si no, se descarta) | NO CUMPLE | 1h: D>C en VAL,OOS1; 4h: D>C en VAL,OOS1; 1d: D>C en OOS1 |

**Lectura honesta de C2 y C3:** son criterios laxos por construcción (dos estrategias que operan en momentos distintos casi siempre suman más que cada una por separado). C2 usa la ventana FULL, dominada por TRAIN (ver el Calmar por tramo del apartado 3). Lo que de verdad dicen algo es C1 (el solapamiento cuesta poco), C4 (aguanta costes ×3) y C5 (el DD no se dispara). Con 4H en OOS1 el criterio C3 se cumple por muy poco (+77,5 % frente a +72,3 %).

## 6. Robustez adicional

**Costes (modelo «pine», ventana FULL): rentabilidad / DD / Calmar**

| TF | Escenario | Costes ×1 (0,08 %) | ×2 (0,16 %) | ×3 (0,24 %) |
|---|---:|---:|---:|---:|
| 1H | V10 sola | 1.699 % / -20,2 % / 1,84 | 1.486 % / -21,4 % / 1,65 | 1.297 % / -22,6 % / 1,48 |
| 1H | W10 sola | 928 % / -22,9 % / 1,27 | 688 % / -24,9 % / 1,02 | 503 % / -28,1 % / 0,77 |
| 1H | **VW1** | 14.990 % / -24,8 % / 2,96 | 10.356 % / -27,0 % / 2,46 | 7.141 % / -31,6 % / 1,90 |
| 4H | V10 sola | 1.060 % / -16,7 % / 1,84 | 944 % / -17,3 % / 1,70 | 839 % / -18,2 % / 1,53 |
| 4H | W10 sola | 468 % / -26,4 % / 0,79 | 343 % / -28,1 % / 0,63 | 246 % / -30,3 % / 0,48 |
| 4H | **VW1** | 6.026 % / -26,6 % / 2,14 | 4.276 % / -27,2 % / 1,88 | 3.025 % / -27,9 % / 1,64 |
| 1D | V10 sola | 580 % / -22,7 % / 1,03 | 529 % / -23,2 % / 0,96 | 482 % / -23,8 % / 0,89 |
| 1D | W10 sola | 455 % / -23,4 % / 0,88 | 337 % / -24,8 % / 0,71 | 244 % / -26,6 % / 0,54 |
| 1D | **VW1** | 3.506 % / -27,5 % / 1,75 | 2.581 % / -30,2 % / 1,44 | 1.892 % / -33,4 % / 1,16 |

**Costes originales de cada motor («orig»: LONG 6 pb + 6 pb con stop de slippage doble y funding; SHORT 5 pb + 3 pb) — rentabilidad / DD / Calmar, ventana FULL:**

| TF | V10 sola | W10 sola | VW1 |
|---|---:|---:|---:|
| 1H | 1.297 % / -21,8 % / 1,54 | 929 % / -22,9 % / 1,27 | 11.623 % / -25,6 % / 2,68 |
| 4H | 886 % / -17,6 % / 1,62 | 468 % / -26,4 % / 0,79 | 5.108 % / -26,9 % / 2,02 |
| 1D | 495 % / -23,4 % / 0,92 | 455 % / -23,4 % / 0,88 | 3.053 % / -28,1 % / 1,64 |

**Remuestreo de operaciones** (5.000 reordenaciones con reemplazo de las operaciones de la ventana ORIG; asume operaciones independientes, que es una simplificación):

| TF | Escenario | Ops | DD mediano | DD (percentil 5 % peor) | Rent. (percentil 5 %) | Rent. mediana |
|---|---:|---:|---:|---:|---:|---:|
| 1H | V10 sola | 129 | -24,2 % | -39,2 % | 310 % | 1.470 % |
| 1H | W10 sola | 115 | -19,2 % | -31,4 % | 232 % | 874 % |
| 1H | VW1 | 238 | -26,0 % | -39,3 % | 2.003 % | 11.520 % |
| 4H | V10 sola | 117 | -21,5 % | -35,0 % | 236 % | 1.033 % |
| 4H | W10 sola | 181 | -22,9 % | -37,9 % | 80 % | 400 % |
| 4H | VW1 | 288 | -26,5 % | -40,5 % | 906 % | 4.802 % |
| 1D | V10 sola | 95 | -22,3 % | -36,5 % | 138 % | 629 % |
| 1D | W10 sola | 103 | -21,4 % | -35,7 % | 111 % | 494 % |
| 1D | VW1 | 192 | -26,7 % | -41,1 % | 687 % | 3.515 % |

**Retorno por año (modelo «pine», costes ×1):**

| Año | 1H V10 | 1H W10 | 1H VW1 | 4H V10 | 4H W10 | 4H VW1 | 1D V10 | 1D W10 | 1D VW1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 17 % | 0 % | 17 % | 1 % | 0 % | 1 % | 19 % | 0 % | 19 % |
| 2018 | 1 % | 84 % | 86 % | -8 % | 131 % | 112 % | -7 % | 98 % | 86 % |
| 2019 | 53 % | 75 % | 167 % | 51 % | 42 % | 120 % | 21 % | 12 % | 42 % |
| 2020 | 114 % | -4 % | 115 % | 95 % | -10 % | 83 % | 88 % | -5 % | 79 % |
| 2021 | 80 % | 3 % | 85 % | 80 % | -5 % | 72 % | 54 % | -7 % | 44 % |
| 2022 | 4 % | 53 % | 41 % | 7 % | 26 % | 32 % | -0 % | 54 % | 44 % |
| 2023 | 23 % | 12 % | 37 % | 25 % | 16 % | 45 % | 35 % | 12 % | 51 % |
| 2024 | 44 % | 58 % | 109 % | 41 % | 28 % | 62 % | 20 % | 74 % | 79 % |
| 2025 | 27 % | 14 % | 24 % | 24 % | -4 % | 11 % | 18 % | 1 % | 19 % |
| 2026 | 11 % | 5 % | 30 % | 1 % | 13 % | 20 % | -8 % | -7 % | -4 % |

2017 es parcial (desde agosto) y 2026 llega hasta el 3 de octubre. En varios años alcistas VW1 rinde algo menos que V10 sola (4H 2020-21 y 2025; 1D 2020-21; 1H 2025): es el precio de incluir los SHORT perdedores de esos años.

## 7. Variante VW1-flip (descartada)

Invierte la posición cuando aparece la señal contraria con una posición abierta. Era una única variante, sin parámetros nuevos, con el criterio fijado de antemano: superar a VW1 en Calmar en TRAIN, VAL y OOS1 a la vez en ≥2 de 3 TF. 1h: D>C en VAL,OOS1; 4h: D>C en VAL,OOS1; 1d: D>C en OOS1. **No lo cumple**; además empeora el DD en FULL (1H −27,8 % vs −24,8 %, 4H −27,0 % vs −26,6 %, 1D −33,9 % vs −27,5 %) y el Calmar FULL en 1H y 1D. Se descarta y no se reabre. Esto no dice que invertir sea malo en general, solo que con las reglas actuales no aporta de forma consistente.

## 8. Cifras para comparar con TradingView

Resultado esperado del Python para VW1 (modelo «pine»: comisión 0,08 %, slippage 0). **No esperes que TradingView dé exactamente lo mismo**: otros datos de velas, otro emulador de órdenes (p. ej. el stop del LONG no vale en la barra de relleno, la toma parcial del SHORT en 1H) e indicadores con semilla ligeramente distinta. Sí deberías ver el mismo orden de magnitud de operaciones y de DD. Pon el rango del gráfico en 2017-08-17 en adelante (VW1 ya filtra por ese inicio, así que en 1D no entrarán las operaciones de 2015-2017 que sí aparecen en V10 sola).

| TF | Ventana | Rentabilidad | DD máx. | Operaciones | PF ($) | Acierto |
|---|---:|---:|---:|---:|---:|---:|
| 1H | 2017-08-17 → 2026-01-10 | 11.398 % | -24,8 % | 238 (129 L / 109 S) | 1,87 | 49 % |
| 1H | 2017-08-17 → 2026-10-03 | 14.990 % | -24,8 % | 271 (141 L / 130 S) | 1,79 | 49 % |
| 4H | 2017-08-17 → 2026-01-10 | 4.956 % | -26,6 % | 288 (117 L / 171 S) | 1,63 | 44 % |
| 4H | 2017-08-17 → 2026-10-03 | 6.026 % | -26,6 % | 326 (126 L / 200 S) | 1,55 | 43 % |
| 1D | 2017-08-17 → 2026-01-10 | 3.647 % | -21,7 % | 192 (95 L / 97 S) | 1,94 | 48 % |
| 1D | 2017-08-17 → 2026-10-03 | 3.506 % | -27,5 % | 219 (101 L / 118 S) | 1,57 | 47 % |

Con los costes de cada motor original («orig»), que incluyen funding en el LONG y slippage, el resultado FULL baja a 1H 11.623 %, 4H 5.108 %, 1D 3.053 %.

## 9. Limitaciones

- **Todo es simulación en Python con las convenciones de los motores originales.** El Pine VW1 no se ha compilado ni ejecutado en TradingView; la comparación del apartado 8 es justamente el test que falta.
- **Los parámetros de V10 y W10 se eligieron con datos de TRAIN/VAL (y, en el caso del LONG, el OOS ya se había visto).** Que VW1 sume los dos no elimina ese sesgo; solo los junta. La parte de la rentabilidad que viene de 2017-2021 (TRAIN) es la menos creíble como expectativa futura: en OOS1 VW1 hace +157 % (1H), +77 % (4H) y +113 % (1D), y en OOS2 +31 % / +21 % / −4 %.
- **La rentabilidad total mostrada es enorme porque compone dos ventajas en la misma cuenta durante 9 años con riesgo por operación del 4-6 %.** No la tomes como expectativa: usa Calmar, DD y los tramos OOS. El 5 % peor del remuestreo de DD es −39 % a −41 %.
- **4H:** el SHORT de 4H es el más débil de W10 (PF 1,5, evidencia no robusta al cambiar el percentil); en 2024-2026 VW1 4H apenas mejora a V10 sola. **1D:** pocas operaciones por tramo (el OOS1 de 1D tiene 27 operaciones LONG y 15 SHORT) y V10 1D depende del ancla del día; W10 1D con evidencia débil.
- **Costes:** sin funding en el SHORT (los dos motores originales no lo modelan) ni deslizamiento realista en capitulaciones; con costes ×3 VW1 sigue con Calmar > 1, pero eso no sustituye a datos reales.
- **Posición única:** si algún día se quiere que el SHORT pueda entrar con el LONG abierto (hoy cuesta 6,5-9 % de sus entradas), hace falta una cuenta/estrategia separada o cubrir en otro instrumento; en un solo gráfico de TradingView la posición es neta.
- **El 2026 de W10 es coherente con lo que viste en TradingView:** W10 sola en 1H hace −22,9 % de DD en 2026-01→10, parecido al −21 % de W9 que mencionaste.

## 10. Archivos

- `backtest_vw1/eng_vw.py` (motor conjunto), `prep_vw.py` (señales con el código original de V10 y W10, métricas), `validate_vw1.py`, `run_vw1.py`, `criterios_vw1.py`, `mk_informe_vw1.py`, `vw1_prereg.txt`, `oos_access_log.txt`.
- CSV: `resultados_VW1.csv` (todos los escenarios × tramos × costes), `solapamiento_VW1.csv`, `bootstrap_VW1.csv`, `retorno_anual_VW1.csv`, `criterios_VW1.csv`, `validacion_motor.csv`.
- Reproducir: `pip install numba pandas numpy scipy` y, desde `backtest_vw1/`, `python validate_vw1.py && python run_vw1.py && python criterios_vw1.py && python mk_informe_vw1.py`. Las rutas se calculan desde la ubicación del script.
