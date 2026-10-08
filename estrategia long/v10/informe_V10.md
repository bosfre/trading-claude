# V10 (optimización de V9) — informe

## 1. Conclusión

**V10 mantiene la lógica de V9 (= V8).** No he encontrado ninguna mejora de lógica que sea robusta, y prefiero decírtelo antes que forzar una. Probé **20 variantes nuevas (60 pruebas = variantes × 3 temporalidades)** de entrada, salida y gestión de posición, fijadas por escrito **antes** de ejecutarlas (`v10_prereg.txt`, con tres enmiendas fechadas) y evaluadas contra V9 solo con TRAIN y VAL en ETH + BTC + DOGE. **5 de 60 pasaron el criterio básico** (≈ 8 %, compatible con ruido), cada una en una sola temporalidad, con efecto pequeño y con vecinos de parámetros que fallan; ninguna cumplió las reglas anti-falso-positivo (R1: ≥ 2 temporalidades o efecto grande; R2: vecinos que no empeoren), así que no se abrió ningún holdout y no se adoptó nada.

**Qué significa para tus objetivos (1H, 4H y 1D en conjunto)**
- **Rentabilidad, Profit Factor, win rate y beneficio por operación: no mejorados.** Con riesgo 5 % V10 = V9 exactamente: 1H +1.431 % / DD -21,8 %, 4H +1.011 % / -17,6 %, 1D +483 % / -23,4 % (ETH, 2017-08 → 2026-10).
- **Drawdown: solo se reduce bajando el riesgo**, y entonces cae la rentabilidad casi en proporción (el Calmar apenas se mueve). Lo ofrezco como **preset de riesgo opcional** (sección 3), no como mejora de la estrategia. Con él, el DD baja a ≈ −15 % en las tres temporalidades; no lo activo por defecto porque en 1D reduce la rentabilidad de +483 % a +207 %, justo lo que pediste no empeorar.
- **1D**: no se empeora, pero tampoco mejora. Lo que sí he podido medir es **cuánto de su resultado es suerte**: con la misma estrategia y los mismos datos, solo desplazando la hora en que empieza el día, ETH 1D va de CAGR 18,6 % a 29,1 % (sección 5).

**Hallazgos nuevos que sí te sirven**
1. **El filtro de BTC puede estar desactivado en tu gráfico sin que lo notes.** En el Pine de V8/V9 el filtro no bloquea nada si BTC no tiene dato en una barra. Tus cifras de 1D (+366 %, DD ≈ 27 %) se parecen más a **V7 sin filtro** en mi backtest (+380 %, -26,0 %) que a V9 (+483 %, -23,4 %). El Pine V10 trae un panel que muestra si el filtro está activo y en cuántas barras faltan datos de BTC.
2. **En ETH, 1D es muy sensible al stop**: k = 4,0–4,5 ATR empeora el DD hasta −31 % y el Calmar cae de 0,91 a 0,63–0,66; pero en BTC y DOGE esa misma bajada **mejora** el Calmar (BTC 1,40 y DOGE 0,59 con k = 4,0, frente a 0,90 y 0,24). La dirección no es consistente entre activos, así que tampoco es una palanca que explotar: es otra muestra de que 1D tiene más azar que señal. 4H es la temporalidad más estable ante cambios de parámetros.
3. **El ancla estándar de 1D (00:00 UTC) es de las peores** para ETH y DOGE (puesto 23 de 24), pero está a mitad de tabla en BTC. No es una ventaja explotable a priori (no hay una razón económica para que un ancla sea mejor): es ruido de temporización.

## 2. Qué es V10 exactamente

Lógica idéntica a V8/V9: largo si el cierre supera el máximo de 140 h y la EMA de 800 h, **y** BTC está sobre su EMA de 800 h; stop inicial y trailing de 5 ATR, TP a 20 ATR, riesgo 5 % por operación (apalancamiento máx. 2×). Cambios **operativos** (no de edge) en `V10_ETH_Donchian_EMA_ATR_TP_BTC.pine`:
1. Panel de diagnóstico del filtro BTC (activo/desactivado, barras sin datos de BTC, señales bloqueadas, riesgo aplicado).
2. Preset de riesgo opcional por temporalidad (1H 3,3 % · 4H 4,2 % · 1D 3,0 %), por defecto en **Manual 5 % = V9**.
3. Se eliminó la piramidación experimental (venía apagada y está descartada desde V7).
El Pine **no está compilado ni probado en TradingView** desde este entorno.

## 3. V10 frente a V9 en 1H, 4H y 1D

Datos: tus CSV de ETH (1h/4h/1d hasta 2026-01-06) + tramo de Twelve Data hasta 2026-10-03; costes del repo (comisión 0,06 %, slippage por activo, funding). Las cifras de V9 se han **re-ejecutado con estos CSV**: 1H y 4H coinciden con el informe V9 (+1.431 % y +1.011 % frente a +1.429 % y +1.010 %); 1D da +483 % frente a +464 % del informe V9, porque aquí se lee el CSV diario directamente en vez de remuestrear desde 15 m.

| Métrica (ETH, 2017-08-17 → 2026-10-03) | 1H V9 = V10 (5 %) | 1H V10 preset | 4H V9 = V10 (5 %) | 4H V10 preset | 1D V9 = V10 (5 %) | 1D V10 preset |
|---|---|---|---|---|---|---|
| Rentabilidad total | 1.431 % | 563 % | 1.011 % | 688 % | 483 % | 207 % |
| CAGR | 34,8 % | 23,0 % | 30,2 % | 25,4 % | 21,3 % | 13,1 % |
| Máx. drawdown (intrabarra) | -21,8 % | -15,0 % | -17,6 % | -15,0 % | -23,4 % | -14,8 % |
| Calmar (CAGR/DD) | 1,60 | 1,53 | 1,72 | 1,69 | 0,91 | 0,88 |
| Operaciones | 143 | 143 | 126 | 126 | 105 | 105 |
| Win rate | 42,7 % | 42,7 % | 43,7 % | 43,7 % | 44,8 % | 44,8 % |
| Profit Factor (% por operación) | 2,41 | 2,41 | 2,54 | 2,54 | 2,15 | 2,15 |
| Profit Factor ($, como TradingView) | 1,94 | 2,08 | 2,11 | 2,18 | 1,64 | 1,81 |
| Beneficio medio / operación (% equity) | 2,2 % | 1,5 % | 2,2 % | 1,8 % | 2,0 % | 1,2 % |
| R medio / operación | 0,44 | 0,44 | 0,44 | 0,44 | 0,39 | 0,39 |
| Ganancia media / pérdida media | 3,24 | 3,24 | 3,28 | 3,28 | 2,65 | 2,65 |
| Sharpe (diario) | 1,34 | 1,35 | 1,30 | 1,30 | 1,05 | 1,06 |

**Qué ha mejorado, qué ha empeorado (preset DD ≈ 15 % frente a V9 con riesgo 5 %)**
- **Mejora**: el drawdown (1H -21,8 % → -15,0 %; 4H -17,6 % → -15,0 %; 1D -23,4 % → -14,8 %) y el Profit Factor en dólares (1H 1,94 → 2,08; 4H 2,11 → 2,18; 1D 1,64 → 1,81). Esto último es un efecto de ponderación (el PF en dólares da más peso a las operaciones recientes cuando la cuenta ya ha crecido y, con menos riesgo, crece más despacio), no una mejor calidad de operación: el PF por operación no cambia.
- **Empeora**: CAGR (1H 34,8 % → 23,0 %; 4H 30,2 % → 25,4 %; 1D 21,3 % → 13,1 %), rentabilidad total y beneficio medio por operación (1H 2,2 % → 1,5 %). El Calmar baja un poco (1H 1,60 → 1,53; 4H 1,72 → 1,69; 1D 0,91 → 0,88): es moverse por la misma curva, no mejorarla.
- **Igual**: win rate, Profit Factor por operación, R medio, ganancia/pérdida media y nº de operaciones (las señales son las mismas). Por eso **el win rate no se puede subir sin cambiar la lógica, y la lógica probada no lo mejora de forma robusta**.
- **Coste del preset por punto de drawdown recortado**: 1H 1,74 pp de CAGR por cada pp de DD, 4H 1,87 y 1D 0,95. En ninguna temporalidad se recorta DD gratis.

**Por ventanas** (CAGR / DD / Calmar). TRAIN y VAL fueron las ventanas de selección; OOS1 y OOS2 ya se conocían de V8/V9, así que describen pero no son pruebas independientes.

| Ventana (CAGR / DD / Calmar) | 1H V9 | 1H preset | 4H V9 | 4H preset | 1D V9 | 1D preset |
|---|---|---|---|---|---|---|
| TRAIN 2017-08→2021 | 53,0 % / -17,9 % / 2,97 | 34,0 % / -12,1 % / 2,81 | 43,1 % / -15,5 % / 2,79 | 35,9 % / -13,2 % / 2,72 | 36,4 % / -13,8 % / 2,64 | 21,4 % / -8,6 % / 2,50 |
| VAL 2022-23 | 12,4 % / -17,1 % / 0,72 | 8,7 % / -11,6 % / 0,75 | 16,0 % / -11,2 % / 1,43 | 13,6 % / -9,5 % / 1,44 | 13,5 % / -16,8 % / 0,80 | 8,6 % / -10,5 % / 0,82 |
| OOS1 2024→2026-01 | 29,1 % / -17,0 % / 1,71 | 19,5 % / -11,6 % / 1,68 | 30,0 % / -17,2 % / 1,75 | 25,3 % / -14,7 % / 1,73 | 12,4 % / -17,3 % / 0,71 | 8,2 % / -10,8 % / 0,76 |
| OOS2 2026-01→10 | 17,5 % / -12,1 % / 1,44 | 12,1 % / -8,2 % / 1,48 | 1,4 % / -11,3 % / 0,13 | 1,4 % / -9,6 % / 0,14 | -10,9 % / -9,1 % / -1,20 | -6,6 % / -5,5 % / -1,20 |
| ÚLTIMOS 2 AÑOS 2024-01→2026-10 | 25,9 % / -21,8 % / 1,19 | 17,5 % / -15,0 % / 1,17 | 21,8 % / -17,6 % / 1,24 | 18,5 % / -15,0 % / 1,23 | 5,7 % / -23,4 % / 0,24 | 4,1 % / -14,8 % / 0,27 |

**Frontera de riesgo** (riesgo que da cada DD en la ventana común; mide eficiencia, no una mejora):

| DD objetivo | 1H (riesgo → CAGR) | 4H (riesgo → CAGR) | 1D (riesgo → CAGR) |
|---|---|---|---|
| -10 % | 2,1 % → CAGR 14,6 % (Calmar 1,48) | 2,7 % → CAGR 16,3 % (Calmar 1,64) | 2,0 % → CAGR 8,8 % (Calmar 0,87) |
| -12 % | 2,6 % → CAGR 18,1 % (Calmar 1,50) | 3,3 % → CAGR 19,9 % (Calmar 1,66) | 2,4 % → CAGR 10,5 % (Calmar 0,88) |
| -15 % | 3,3 % → CAGR 23,0 % (Calmar 1,53) | 4,2 % → CAGR 25,4 % (Calmar 1,69) | 3,0 % → CAGR 13,1 % (Calmar 0,88) |
| -20 % | 4,5 % → CAGR 31,4 % (Calmar 1,58) | 5,8 % → CAGR 35,0 % (Calmar 1,74) | 4,2 % → CAGR 18,1 % (Calmar 0,90) |
| sin objetivo (riesgo 5 %) | 5,0 % → CAGR 34,8 % / DD -21,8 % (Calmar 1,60) | 5,0 % → CAGR 30,2 % / DD -17,6 % (Calmar 1,72) | 5,0 % → CAGR 21,3 % / DD -23,4 % (Calmar 0,91) |

## 4. Qué se probó y por qué se descartó (`experimentos_V10.csv`, `trials10.jsonl`)

Criterio por temporalidad (el de V9): ΔCalmar ETH > 0 en TRAIN **y** VAL; ΔCalmar BTC y DOGE ≥ 0; ΔDD ETH no peor de 1 pp; ΔR/operación ETH > 0. Reglas añadidas en V10: **R1** solo se adopta si pasa en ≥ 2 temporalidades con los mismos parámetros, o en 1 con efecto grande (ΔCalmar ≥ 0,3) y un vecino que también pase; **R2** debe haber un vecino de parámetros que no empeore; **R3** nunca se acepta nada que empeore 1D.

| Familia | Variantes | Pruebas (× 3 TF) | Pasan criterio básico | Cuáles |
|---|---|---|---|---|
| G1 volumen | 2 | 6 | 0 | ninguna |
| G2 estancamiento | 3 | 9 | 0 | ninguna |
| G3 enfriamiento tras perdida | 7 | 21 | 4 | enfria 100h (1H); enfria 50h (1H); enfria 75h (1H); enfria 125h (4H) |
| G4 ruptura fallida | 3 | 9 | 1 | fallida 150h/2ATR (1D) |
| G5 ancla del trailing en cierres | 1 | 3 | 0 | ninguna |
| G6 confirmacion 2 cierres | 1 | 3 | 0 | ninguna |
| G2b estancamiento (umbrales alcanzables) | 3 | 9 | 0 | ninguna |

- **Volumen de ruptura** (primera vez que se usa como regla): con ≥ 1,0× la media mejora 4H en TRAIN (+0,17) pero no en VAL, y 1D empeora (−0,21 / −0,14); con ≥ 1,5× es inestable (4H TRAIN +0,32, VAL −0,12; 1D TRAIN −1,35). El tramo 2026 no tiene volumen en los datos, así que el filtro no actúa ahí.
- **Parada por estancamiento**: mi primer intento (280-560 h) **era nulo por construcción**: el estancamiento máximo dentro de una operación 4H de la muestra es de 248 h (lo corregí en la enmienda 1 y conté las pruebas nuevas). Con umbrales alcanzables (100-200 h) ninguna pasa y en 1D empeora (ΔR/op hasta −0,12, DD hasta 3,4 pp peor).
- **Enfriamiento tras pérdida**: la única con apariencia de señal (100 h pasa en 1H). La curva de sensibilidad pre-registrada (C = 50-200 h) da **0 de 6 valores que pasen a la vez en 1H y 4H** (regla: ≥ 4), los signos cambian entre vecinos y con 300 h destroza TRAIN (−0,9 a −1,7). Es ruido.
- **Ruptura fallida**: solo 150 h/2 ATR pasa, en 1D, con efecto de +0,10 / +0,06: incumple R1; en 1H/4H empeora DOGE (−0,3 a −0,6).
- **Ancla del trailing en cierres** y **confirmación de 2 cierres**: signos contrarios entre TRAIN/VAL o entre activos.
- **Ya descartado en V6-V9 y no repetido**: pirámide, cortos, reentrada, parciales, entrada por stop, stop al cierre, throttle por DD, trinquetes, multi-velocidad, filtros de volatilidad/ADX/régimen, TP 0-40, rejilla N×L×ATR×k, ETH/BTC, salidas temporales, salidas por EMA/BTC, trailing más ancho, filtro de extensión, calidad de vela.
- **No probado** (prior bajo → minería de datos): hora/día de la semana; amplitud de mercado con ETC (no hay ETC en 2026).

**Aviso estadístico**: el criterio básico deja pasar por azar una fracción de pruebas que no puedo fijar con precisión (las pruebas están correlacionadas entre temporalidades y activos); 5 de 60 (8 %) es compatible con ruido, y ninguna sobrevive a R1/R2. Los 20 intentos se hicieron sobre un espacio ya muy explorado (V6-V9 acumulan cientos de variantes), así que la probabilidad a priori de una mejora real era baja.

## 5. Robustez de la base (V10 = V9)

### 5.1 Ancla de la vela: ¿cuánto del resultado es suerte?
Misma V9, mismos datos; las velas de 1D se construyen desde 1H con 24 anclas (la vela empieza a las 00, 01, … 23 h UTC) y las de 4H con 4 anclas. No es una búsqueda de parámetros: mide el ruido de temporización.

| Serie | Anclas | Rentabilidad (mín – mediana – máx) | CAGR (mín – mediana – máx) | Calmar (mín – mediana – máx) | Ancla estándar 00:00 UTC: CAGR |
|---|---|---|---|---|---|
| ETH 1D | 24 | 374 % – 589 % – 930 % | 18,6 % – 23,6 % – 29,1 % | 0,86 – 1,22 – 1,54 | 20,9 % (puesto 23 de 24) |
| BTC 1D | 24 | 300 % – 415 % – 527 % | 16,4 % – 19,7 % – 22,3 % | 0,46 – 0,69 – 0,89 | 20,6 % (puesto 10 de 24) |
| DOGE 1D | 24 | 124 % – 374 % – 678 % | 11,8 % – 24,0 % – 32,8 % | 0,25 – 0,80 – 1,48 | 12,0 % (puesto 23 de 24) |
| ETH 4H | 4 | 986 % – 1.081 % – 1.422 % | 29,9 % – 31,0 % – 34,8 % | 1,40 – 1,65 – 1,74 | 30,2 % (puesto 3 de 4) |
| BTC 4H | 4 | 788 % – 920 % – 953 % | 27,0 % – 29,0 % – 29,4 % | 0,95 – 1,01 – 1,13 | 28,9 % (puesto 3 de 4) |
| DOGE 4H | 4 | 455 % – 487 % – 698 % | 26,7 % – 27,7 % – 33,2 % | 0,80 – 0,93 – 1,29 | 33,2 % (puesto 1 de 4) |

El ancla estándar de 1D (00:00 UTC, la de TradingView) es la 23.ª de 24 en ETH y en DOGE y la 10.ª en BTC. **La dependencia es grande en 1D** (la rentabilidad de ETH va de +374 % a +930 %) **y pequeña en 4H**. Consecuencias: (1) diferencias de pocos puntos entre temporalidades, o entre tu TradingView y mi backtest, pueden ser solo esto; (2) la ventaja o desventaja de 1D frente a 4H no se puede leer al detalle: con la **mediana** de anclas, 1D (Calmar 1,22) sigue por debajo de 4H (1,65), pero la brecha es menor que con el ancla estándar (0,91 frente a 1,72).

**¿Mejora repartir el capital entre varias anclas?** (pesos iguales, sin optimizar; se compara con la **media** de las anclas sueltas, la comparación justa; contra el ancla 0 la mejora sería casi toda regresión a la media)

| Ensamble · activo (ventana común) | Ensamble CAGR / DD / Calmar | Media de anclas sueltas | Ancla estándar 0 |
|---|---|---|---|
| 1D K=4 · ETH | 23,3 % / -19,0 % / 1,23 | 23,9 % / -20,2 % / 1,20 | 20,9 % / -23,2 % / 0,90 |
| 1D K=4 · BTC | 20,1 % / -27,7 % / 0,73 | 19,6 % / -29,1 % / 0,69 | 20,6 % / -27,7 % / 0,74 |
| 1D K=4 · DOGE | 20,4 % / -31,9 % / 0,64 | 22,7 % / -30,5 % / 0,80 | 12,0 % / -43,1 % / 0,28 |
| 1D K=24 · ETH | 24,1 % / -18,7 % / 1,29 | 23,9 % / -20,2 % / 1,20 | 20,9 % / -23,2 % / 0,90 |
| 1D K=24 · BTC | 19,7 % / -27,8 % / 0,71 | 19,6 % / -29,1 % / 0,69 | 20,6 % / -27,7 % / 0,74 |
| 1D K=24 · DOGE | 23,5 % / -25,9 % / 0,91 | 22,7 % / -30,5 % / 0,80 | 12,0 % / -43,1 % / 0,28 |
| 4H K=4 · ETH | 31,8 % / -18,8 % / 1,69 | 31,7 % / -19,0 % / 1,69 | 30,2 % / -17,1 % / 1,77 |
| 4H K=4 · BTC | 28,6 % / -25,5 % / 1,12 | 28,6 % / -27,2 % / 1,06 | 28,9 % / -25,2 % / 1,15 |
| 4H K=4 · DOGE | 29,0 % / -26,5 % / 1,09 | 28,8 % / -28,8 % / 1,02 | 33,2 % / -24,3 % / 1,37 |

El ensamble de 24 anclas en 1D recorta ≈ 1,5 pp de DD y suma ≈ +0,1 de Calmar frente a la media de anclas: diversificación real pero pequeña (los sleeves están muy correlacionados). **No cumple mi criterio pre-registrado** (BTC en DEV: Calmar 0,93 frente a 0,95; el ensamble de 4 anclas falla en TRAIN y el de 4H en VAL) y exigiría ejecutar 24 sleeves en paralelo, que en TradingView no es práctico. Queda como hallazgo, no como cambio de V10.

### 5.2 Sensibilidad de parámetros (una a una, sobre V9)
**1H**

| Parámetro | CAGR | DD | Calmar (común) | Calmar DEV ETH | Calmar DEV BTC | Calmar DEV DOGE | Op. |
|---|---|---|---|---|---|---|---|
| base | 34,8 % | -21,8 % | 1,60 | 2,18 | 1,75 | 0,77 | 143 |
| N 100 h | 36,9 % | -23,8 % | 1,55 | 2,40 | 1,62 | 0,94 | 153 |
| N 120 h | 37,0 % | -21,7 % | 1,71 | 2,40 | 1,40 | 0,84 | 146 |
| N 170 h | 33,7 % | -24,8 % | 1,36 | 2,02 | 1,37 | 0,66 | 137 |
| N 200 h | 31,0 % | -25,6 % | 1,21 | 1,69 | 1,24 | 0,79 | 131 |
| EMA 600 h | 35,2 % | -22,9 % | 1,54 | 1,70 | 1,33 | 1,00 | 148 |
| EMA 700 h | 33,5 % | -21,5 % | 1,56 | 1,76 | 1,48 | 0,95 | 148 |
| EMA 900 h | 33,9 % | -20,5 % | 1,66 | 2,02 | 1,59 | 0,71 | 141 |
| EMA 1000 h | 32,4 % | -20,5 % | 1,58 | 1,86 | 1,76 | 0,75 | 141 |
| k 4,0 | 35,2 % | -24,5 % | 1,44 | 1,47 | 1,74 | 0,58 | 167 |
| k 4,5 | 35,9 % | -23,1 % | 1,56 | 1,98 | 1,74 | 0,65 | 155 |
| k 5,5 | 32,0 % | -22,4 % | 1,43 | 2,27 | 1,80 | 1,27 | 135 |
| k 6,0 | 27,0 % | -24,4 % | 1,11 | 1,85 | 1,40 | 1,40 | 128 |
| TP 0 | 34,2 % | -21,8 % | 1,57 | 1,72 | 1,81 | 0,98 | 126 |
| TP 15 | 31,3 % | -21,8 % | 1,43 | 1,92 | 1,89 | 0,73 | 149 |
| TP 25 | 32,5 % | -21,8 % | 1,49 | 1,67 | 1,97 | 0,73 | 134 |
| TP 30 | 33,8 % | -21,8 % | 1,55 | 1,70 | 2,03 | 0,81 | 132 |
| ATR 40 h | 33,7 % | -24,5 % | 1,38 | 2,31 | 1,71 | 1,07 | 145 |
| ATR 72 h | 34,4 % | -22,4 % | 1,53 | 2,01 | 1,68 | 0,61 | 141 |

**4H**

| Parámetro | CAGR | DD | Calmar (común) | Calmar DEV ETH | Calmar DEV BTC | Calmar DEV DOGE | Op. |
|---|---|---|---|---|---|---|---|
| base | 30,2 % | -17,6 % | 1,72 | 2,20 | 1,33 | 1,61 | 126 |
| N 100 h | 33,9 % | -21,2 % | 1,60 | 2,11 | 1,26 | 2,15 | 139 |
| N 120 h | 31,1 % | -21,5 % | 1,45 | 2,33 | 1,42 | 1,89 | 132 |
| N 170 h | 28,0 % | -20,7 % | 1,35 | 2,02 | 1,43 | 1,46 | 123 |
| N 200 h | 27,1 % | -22,8 % | 1,19 | 1,80 | 1,25 | 1,85 | 115 |
| EMA 600 h | 29,1 % | -18,5 % | 1,58 | 2,09 | 1,05 | 1,80 | 133 |
| EMA 700 h | 30,0 % | -17,2 % | 1,74 | 2,09 | 1,16 | 1,61 | 130 |
| EMA 900 h | 29,2 % | -18,0 % | 1,62 | 2,05 | 1,38 | 1,48 | 125 |
| EMA 1000 h | 29,2 % | -17,5 % | 1,67 | 2,01 | 1,51 | 1,29 | 123 |
| k 4,0 | 29,8 % | -18,0 % | 1,66 | 1,68 | 1,77 | 0,95 | 147 |
| k 4,5 | 28,6 % | -19,2 % | 1,50 | 2,09 | 1,42 | 1,19 | 141 |
| k 5,5 | 26,4 % | -18,2 % | 1,46 | 1,65 | 1,37 | 1,92 | 120 |
| k 6,0 | 24,7 % | -19,0 % | 1,30 | 1,52 | 1,34 | 1,68 | 115 |
| TP 0 | 30,3 % | -19,3 % | 1,57 | 1,72 | 1,51 | 1,94 | 115 |
| TP 15 | 30,6 % | -17,6 % | 1,74 | 2,22 | 1,22 | 2,02 | 136 |
| TP 25 | 29,7 % | -17,6 % | 1,68 | 1,94 | 1,47 | 1,66 | 123 |
| TP 30 | 31,0 % | -17,6 % | 1,76 | 2,06 | 1,49 | 1,85 | 121 |
| ATR 40 h | 29,5 % | -20,0 % | 1,48 | 1,68 | 1,45 | 1,40 | 130 |
| ATR 72 h | 30,7 % | -18,4 % | 1,67 | 2,18 | 1,36 | 1,38 | 124 |

**1D** (A_h y parte de N_h no cambian nada: los mínimos de barras del Pine, N ≥ 5, ATR ≥ 10, los fijan)

| Parámetro | CAGR | DD | Calmar (común) | Calmar DEV ETH | Calmar DEV BTC | Calmar DEV DOGE | Op. |
|---|---|---|---|---|---|---|---|
| base | 21,3 % | -23,4 % | 0,91 | 1,71 | 0,90 | 0,24 | 105 |
| N 100 h | 20,3 % | -20,9 % | 0,97 | 1,58 | 0,93 | 0,31 | 108 |
| N 120 h | 20,3 % | -20,9 % | 0,97 | 1,58 | 0,93 | 0,31 | 108 |
| N 170 h | 22,0 % | -23,4 % | 0,94 | 1,72 | 0,72 | 0,30 | 101 |
| N 200 h | 23,5 % | -23,4 % | 1,00 | 1,77 | 0,72 | 0,38 | 97 |
| EMA 600 h | 21,9 % | -21,4 % | 1,02 | 1,81 | 0,83 | 0,27 | 108 |
| EMA 700 h | 22,4 % | -21,4 % | 1,05 | 1,81 | 0,77 | 0,25 | 107 |
| EMA 900 h | 20,4 % | -23,4 % | 0,87 | 1,64 | 1,03 | 0,30 | 103 |
| EMA 1000 h | 18,7 % | -23,4 % | 0,80 | 1,56 | 0,92 | 0,35 | 103 |
| k 4,0 | 19,5 % | -31,0 % | 0,63 | 0,70 | 1,40 | 0,59 | 126 |
| k 4,5 | 17,4 % | -26,5 % | 0,66 | 0,83 | 0,97 | 0,50 | 117 |
| k 5,5 | 19,7 % | -24,5 % | 0,81 | 1,57 | 0,69 | 0,32 | 101 |
| k 6,0 | 15,7 % | -21,0 % | 0,75 | 1,18 | 0,78 | 0,46 | 97 |
| TP 0 | 21,3 % | -23,4 % | 0,91 | 1,71 | 0,89 | 0,44 | 96 |
| TP 15 | 22,2 % | -23,4 % | 0,95 | 1,79 | 0,88 | 0,21 | 107 |
| TP 25 | 21,4 % | -23,4 % | 0,91 | 1,73 | 0,82 | 0,24 | 101 |
| TP 30 | 21,5 % | -23,4 % | 0,92 | 1,73 | 0,88 | 0,30 | 99 |
| ATR 40 h | 21,3 % | -23,4 % | 0,91 | 1,71 | 0,90 | 0,24 | 105 |
| ATR 72 h | 21,3 % | -23,4 % | 0,91 | 1,71 | 0,90 | 0,24 | 105 |

Lectura: en 1H y 4H la base está en una meseta (Calmar 1,1-1,7 en 1H y 1,2-1,8 en 4H en los vecinos; N y EMA más largas empeoran de forma suave). **1D en ETH es frágil al stop**: k = 4,0-4,5 baja el Calmar de 0,91 a 0,63-0,66 y sube el DD a −26,5 % / −31 %, mientras que en BTC y DOGE la misma bajada mejora el Calmar DEV (BTC 1,40 y 0,97; DOGE 0,59 y 0,50, frente a 0,90 y 0,24): sin dirección común entre activos. Ningún valor mejora claramente la base en las tres temporalidades a la vez. La excepción aparente, EMA 600-700 h en 1D (Calmar 1,02-1,05), empeora BTC en DEV (0,77-0,83 frente a 0,90) y no ayuda en 1H, así que no la tomo como mejora; sirve para ver que 1D tiene más recorrido de azar que de señal.

### 5.3 Costes y slippage (ventana común)
| Costes (CAGR / DD / Calmar) | 1H | 4H | 1D |
|---|---|---|---|
| V9 x1 | 34,8 % / -21,8 % / 1,60 | 30,2 % / -17,6 % / 1,72 | 21,3 % / -23,4 % / 0,91 |
| V9 x2 | 30,4 % / -24,6 % / 1,24 | 26,4 % / -19,8 % / 1,33 | 18,4 % / -25,1 % / 0,73 |
| V9 x3 | 25,7 % / -27,2 % / 0,94 | 22,7 % / -21,9 % / 1,03 | 15,6 % / -27,2 % / 0,57 |
| V10 preset x1 | 23,0 % / -15,0 % / 1,53 | 25,4 % / -15,0 % / 1,69 | 13,1 % / -14,8 % / 0,88 |
| V10 preset x2 | 20,3 % / -17,0 % / 1,20 | 22,3 % / -16,9 % / 1,32 | 11,4 % / -15,9 % / 0,72 |
| V10 preset x3 | 17,4 % / -18,9 % / 0,92 | 19,3 % / -18,8 % / 1,02 | 9,8 % / -17,3 % / 0,57 |

Con costes ×3 el Calmar de V9 es 0,94 (1H), 1,03 (4H) y 0,57 (1D): el orden entre temporalidades no cambia y el recorte relativo de CAGR es parecido (−25 % a −27 %). El preset de riesgo aguanta igual.

### 5.4 Retorno por año (ETH, riesgo 5 %)
| Año (ETH, riesgo 5 %) | 1H | 4H | 1D |
|---|---|---|---|
| 2018 | 0,8 % | -8,5 % | -7,8 % |
| 2019 | 50,4 % | 49,9 % | 19,4 % |
| 2020 | 110,5 % | 95,1 % | 85,8 % |
| 2021 | 81,1 % | 78,0 % | 59,7 % |
| 2022 | 2,3 % | 5,5 % | -1,4 % |
| 2023 | 23,5 % | 27,4 % | 30,5 % |
| 2024 | 33,8 % | 37,6 % | 19,3 % |
| 2025 | 27,0 % | 25,6 % | 7,4 % |
| 2026 | 11,1 % | -0,4 % | -9,1 % |

## 6. Sobre tus cifras de 1D (+366 %, DD ≈ 27 %)
No las reproduzco con V9: en mi backtest 1D da +483 % / -23,4 % (2017-08 → 2026-10). **V7 sin filtro BTC**, re-ejecutada con los mismos datos y ventana (`v7_vs_v9_ref_V10.csv`), da +380 % / -26,0 %, mucho más cerca de lo que ves que V9. Es una pista, no una prueba: otras causas posibles son costes distintos, el ancla de la vela y el rango de fechas. Compruébalo en TradingView: (1) con el Pine V10, mira el panel (si dice que faltan datos de BTC, el filtro no actúa); (2) activa y desactiva "Filtro de régimen BTC": si el resultado no cambia, el filtro no se está aplicando; (3) usa el mismo símbolo de ETH (Binance ETHUSDT) y el mismo rango de fechas. Con periodos distintos, 1D también cambia mucho por el ancla de la vela (sección 5.1).

## 7. Qué NO puedo afirmar
- **No hay OOS virgen para V10**: 2024-2026 se conocía de V8/V9. Por eso todas las selecciones se hicieron solo con TRAIN/VAL y no se abrió ningún holdout (`oos_access_log.txt`). Que V10 = V9 en lógica **no añade sobreajuste**.
- 60 pruebas dan resultados espurios por azar; la regla R1/R2 los filtra, pero un efecto real pequeño (< ~0,1 de Calmar) tampoco es detectable con ~12-16 operaciones al año.
- El Pine no está compilado ni probado en TradingView; las diferencias con tu TradingView pueden venir de costes (los de TradingView son más benignos), de los datos de tu exchange y del ancla.
- Los datos de 2026 (Twelve Data) no tienen volumen y son de otro proveedor que Binance.

## 8. Siguientes pasos razonables
1. Verificar en TradingView el filtro de BTC con el panel de V10 (sección 6) antes de comparar nada más.
2. Si quieres DD ≈ 15 %: usar el preset o un riesgo intermedio de la tabla de frontera; no esperes que mejore el Calmar.
3. Para mejorar 1D "de verdad" hace falta información nueva (otros activos, datos de derivados, amplitud de mercado), no más reglas sobre el precio de ETH; 1D tiene el resultado más dependiente del azar de la vela.
4. Repetir el análisis cuando haya 6-12 meses más de datos fuera de muestra.

## 9. Archivos
`informe_V10.md`, `V10_ETH_Donchian_EMA_ATR_TP_BTC.pine`, `experimentos_V10.csv`, `comparativa_V9_V10.csv`, `frontera_riesgo_V10.csv`, `costes_V10.csv`, `sensibilidad_parametros_V10.csv`, `retorno_anual_V10.csv`, `anchor10_resultados.csv`, `ensamble_anclas_resultados.csv`, `v7_vs_v9_ref_V10.csv`, `v10_prereg.txt`, `oos_access_log.txt`, `trials10.jsonl` y el código en `backtest_v10/` (`eng10.py` motor, `exp10.py` arnés, `round10a/b/c.py` rondas, `anchor10.py`/`ens10.py` anclas, `final10.py` análisis, `verify10.py` verificación independiente, `test_eng10.py` test de que el motor reproduce V9 al bit).
