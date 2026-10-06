# V9 (optimización de V8) — informe

## 1. Conclusión

**V9 = V8 sin cambios de lógica.** Probé 15 hipótesis nuevas de stops, salidas, entradas y tamaño (45 pruebas = 15 × 3 temporalidades), fijadas por escrito **antes** de ejecutarlas (`v9_prereg.txt`) y evaluadas contra V8 solo con TRAIN y VAL en ETH + BTC + DOGE. **Una sola pasó el criterio** (1D: salir si el cierre cae 1 ATR por debajo de la EMA) y fue descartada en los holdouts: empeora en ETC (−0,05 de Calmar) y su efecto es de +0,6 pp de CAGR a igual drawdown. La que más "parecía" mejorar el beneficio por operación (no entrar si el precio está muy extendido sobre la EMA) **se hunde en 2015-17** (+96 % frente a +306 %) y en ETC, y por eso no la adopto. No he encontrado una forma robusta de cortar antes las perdedoras ni de dejar correr más las ganadoras.

**Lo que esto significa para tus objetivos**
- **1D: bajar el DD del 18 % hacia 10-15 % manteniendo la rentabilidad, o superar +3.000 %: no es posible con cambios de lógica; solo con menos riesgo** (y entonces baja la rentabilidad casi en proporción: el Calmar apenas se mueve). En mi backtest, 1D con DD −15 % exige riesgo 3,1 % por operación y da un CAGR de 13,1 % (frente a 20,9 % con riesgo 5 % y DD -23,2 %). El +2.491 % de tu TradingView es real (lo reproduzco), pero sale de **11 años de histórico que incluyen el tramo 2015-17**.
- **4H: mejorar el +42 % sin subir el DD del 14 %: no logrado.** Ningún cambio supera a V8 de forma robusta.
- **1H: no logrado**, y con 9 meses y ~11 operaciones no se puede demostrar ni refutar nada.

**Mejor temporalidad hoy: 4H.** Con periodos normalizados (mismas fechas, mismos costes), 4H tiene el mejor Calmar y el menor drawdown de la ventana común, gana en 4 de las 7 ventanas (1H gana TRAIN y los dos tramos de 2026, que se solapan) y mantiene el mejor Calmar con costes ×2 y ×3. 1H da algo más de rentabilidad bruta con más drawdown y es estadísticamente indistinguible de 4H. **1D es la peor en casi todo lo normalizado** y su ventaja aparente en TradingView viene de tener más años (2015-17). Detalle en la sección 2.

## 2. 1H vs 4H vs 1D, normalizado

Una comparación honesta exige la **misma ventana**. Tus cifras de TradingView no lo son: 1D son ~11,2 años (desde 2015), 4H son 2,8 años y 1H son 9 meses. Normalizadas a CAGR serían ≈ 33,9 % (1D), 13,6 % (4H) y 50,9 % (1H, con 11 operaciones: no inferible), y los periodos son tan distintos (2015-17 fue un mercado alcista parabólico) que tampoco son comparables entre sí.

**Ventana común 2017-08-17 → 2026-10-03 (9,1 años, mismas fechas, costes del repo)**

| Métrica (ETH, V8, riesgo 5 %) | 1H | 4H | 1D |
|---|---|---|---|
| Años analizados | 9,1 | 9,1 | 9,1 |
| Rentabilidad total | +1.429,1 % | +1.009,5 % | +463,9 % |
| **CAGR** | 34,8 % | 30,2 % | 20,9 % |
| Máx. drawdown | -21,8 % | -17,3 % | -23,2 % |
| **Calmar (CAGR/DD)** | 1,60 | 1,74 | 0,90 |
| Operaciones | 143 | 126 | 105 |
| Operaciones/año | 15,7 | 13,8 | 11,5 |
| Win rate | 42,7 % | 43,7 % | 43,8 % |
| Profit Factor (% por operación) | 2,41 | 2,55 | 2,13 |
| Profit Factor ($, como TradingView) | 1,94 | 2,12 | 1,64 |
| Beneficio medio/operación (% del equity) | +2,2 % | +2,2 % | +1,9 % |
| R medio/operación | 0,44 | 0,44 | 0,38 |
| Ganancia media / pérdida media | 3,24 | 3,29 | 2,74 |
| Horas medias en posición | 166 | 186 | 223 |
| % del tiempo en mercado | 29,7 % | 29,3 % | 29,4 % |

**Por ventanas** (la ventana común incluye OOS2; todas las temporalidades usan las mismas fechas)

| Ventana | CAGR 1H / 4H / 1D | Máx. DD 1H / 4H / 1D | Calmar 1H / 4H / 1D | Mejor Calmar | Operaciones |
|---|---|---|---|---|---|
| TRAIN 2017-08→2021 | 52,9 / 43,0 / 35,3 % | -17,9 / -15,4 / -13,8 % | 2,96 / 2,78 / 2,56 | **1H** | 67 / 59 / 50 |
| VAL 2022-23 | 12,4 / 15,9 / 13,5 % | -17,1 / -11,2 / -16,8 % | 0,72 / 1,42 / 0,80 | **4H** | 29 / 26 / 20 |
| OOS1 2024→2026-01 | 29,1 / 30,3 / 12,5 % | -17,0 / -17,2 / -17,3 % | 1,71 / 1,76 / 0,72 | **4H** | 35 / 32 / 29 |
| OOS2 2026-01→10 (0,73 años) | 17,5 / 1,4 / -10,9 % | -12,1 / -11,3 / -9,1 % | 1,44 / 0,13 / -1,21 | **1H** | 12 / 9 / 6 |
| Común 2017-08→2026-10 | 34,8 / 30,2 / 20,9 % | -21,8 / -17,3 / -23,2 % | 1,60 / 1,74 / 0,90 | **4H** | 143 / 126 / 105 |
| Últimos 2 años 2024-01→2026-10 | 25,9 / 21,9 / 5,8 % | -21,8 / -17,3 / -23,2 % | 1,19 / 1,27 / 0,25 | **4H** | 47 / 41 / 35 |
| Últimos 9 meses 2026-01→10 | 14,9 / -0,7 / -12,2 % | -12,7 / -12,1 / -12,7 % | 1,18 / -0,06 / -0,97 | **1H** | 13 / 10 / 7 |

Lectura: 4H es la mejor en VAL, OOS1, ventana común y últimos 2 años; 1H gana TRAIN y el tramo corto de 2026; **1D no es la mejor en ninguna ventana**.

**A igual drawdown** (riesgo reescalado para dar el mismo DD en la ventana común; mide la eficiencia, no el riesgo asumido)

| DD objetivo | 1H (riesgo → CAGR) | 4H (riesgo → CAGR) | 1D (riesgo → CAGR) |
|---|---|---|---|
| -10 % | 2,1 % → **14,8 %** | 2,8 % → **16,6 %** | 2,0 % → **8,6 %** |
| -12 % | 2,6 % → **18,0 %** | 3,4 % → **20,2 %** | 2,4 % → **10,4 %** |
| -15 % | 3,3 % → **23,0 %** | 4,3 % → **25,8 %** | 3,1 % → **13,1 %** |
| -20 % | 4,5 % → **31,6 %** | 5,9 % → **35,4 %** | 4,2 % → **17,8 %** |

A un DD del 15 %, 4H rinde ≈ 2 veces lo que 1D (25,8 % frente a 13,1 % de CAGR). Esto también responde a tu objetivo de DD 10-15 %: **si quieres ese drawdown, 4H lo da con más del doble de rentabilidad que 1D**.

**¿Es la ventaja de 1D simplemente tener más años?** Sí, y es lo contrario de una ventaja. 1D desde 2015-08: CAGR 31,7 %, Calmar 1,37 (en Python); desde 2017-08: CAGR 20,9 %, Calmar 0,90; 2024→2026-10: CAGR 5,8 %. Los dos años 2015-17 (+306 %, Calmar 10,4, win rate 74 %) elevan el CAGR de 1D en ~11 pp. 4H y 1H no tienen datos de Binance anteriores a 2017-08, así que no pueden "heredar" ese tramo.

**¿La diferencia entre temporalidades es real o ruido?** Bootstrap por bloques de 30 días sobre la ventana común (3.000 remuestreos conjuntos, para respetar la correlación entre temporalidades, 0,80-0,91):

| TF | CAGR (p5 – mediana – p95) | Máx. DD mediano | Calmar (p5 – mediana – p95) |
|---|---|---|---|
| 1H | 17,8 – 34,4 – 55,4 % | -24,6 % | 0,57 – 1,38 – 2,73 |
| 4H | 15,1 – 29,9 – 47,4 % | -23,4 % | 0,49 – 1,27 – 2,56 |
| 1D | 8,0 – 20,6 – 35,3 % | -25,3 % | 0,24 – 0,81 – 1,78 |

P(Calmar 4H > 1D) = 0,89 · P(Calmar 1H > 1D) = 0,93 · **P(Calmar 1H > 4H) = 0,64** (indistinguibles). Es decir: hay evidencia moderada de que 1D es peor, y **ninguna** de que 1H sea mejor o peor que 4H.

**Costes** (ventana común)

| Costes (comisión+slippage+funding) | 1H CAGR / DD / Calmar | 4H | 1D |
|---|---|---|---|
| x1 | 34,8 % / -21,8 % / 1,60 | 30,2 % / -17,3 % / 1,74 | 20,9 % / -23,2 % / 0,90 |
| x2 | 30,4 % / -24,6 % / 1,24 | 26,4 % / -19,5 % / 1,35 | 18,0 % / -24,9 % / 0,72 |
| x3 | 25,7 % / -27,2 % / 0,94 | 22,7 % / -21,7 % / 1,05 | 15,1 % / -27,0 % / 0,56 |

Con costes ×3 el Calmar de 4H sigue en 1,05, el de 1H en 0,94 y el de 1D en 0,56; el recorte relativo de CAGR es parecido en las tres (−25 % a −28 %), así que los costes no cambian el orden.

**Mezclar temporalidades no ayuda**: los retornos diarios están correlacionados (1H-4H 0,91; 4H-1D 0,86; 1H-1D 0,80).

| Cartera (pesos fijos, sin optimizar) | CAGR | Máx. DD | Calmar (común) | Calmar TRAIN | Calmar VAL | Calmar 2024→2026-10 |
|---|---|---|---|---|---|---|
| 1H | 34,8 % | -21,2 % | 1,64 | 3,65 | 0,74 | 1,22 |
| 4H | 30,2 % | -17,1 % | 1,77 | 3,03 | 1,44 | 1,28 |
| 1D | 20,9 % | -23,2 % | 0,90 | 2,56 | 0,80 | 0,25 |
| 1H+4H (50/50) | 32,6 % | -19,1 % | 1,71 | 3,77 | 1,09 | 1,26 |
| 4H+1D (50/50) | 25,6 % | -20,0 % | 1,28 | 2,91 | 1,15 | 0,69 |
| 1H+4H+1D (1/3 c/u) | 28,8 % | -20,3 % | 1,42 | 3,54 | 0,99 | 0,88 |

(Cifras calculadas sobre retornos diarios de cada cartera, por eso difieren ligeramente de la tabla de la ventana común, que usa el drawdown barra a barra.)

**Retorno por año (ETH, V8)**

| Año | 1H | 4H | 1D |
|---|---|---|---|
| 2017 (parcial) | +11,0 % | +0,8 % | +19,1 % |
| 2018 | +0,8 % | -8,5 % | -6,1 % |
| 2019 | +50,4 % | +49,9 % | +13,1 % |
| 2020 | +110,4 % | +95,1 % | +85,8 % |
| 2021 | +81,1 % | +77,3 % | +59,7 % |
| 2022 | +2,3 % | +5,5 % | -1,4 % |
| 2023 | +23,4 % | +27,4 % | +30,5 % |
| 2024 | +33,8 % | +37,6 % | +19,3 % |
| 2025 | +27,0 % | +25,6 % | +7,4 % |
| 2026 (parcial) | +11,1 % | -0,1 % | -8,9 % |

1D se queda atrás en los años de tendencia fuerte (2019, 2024, 2025) y solo gana a las otras dos en 2023 y en el tramo parcial de 2017; en 2026 pierde con 6-7 operaciones.

**Calidad por operación**: el beneficio medio por operación es parecido en las tres (2,2 % / 2,2 % / 1,9 % del equity) y el R medio también (0,44 / 0,44 / 0,38); el win rate es casi igual (≈ 43-44 %). La desventaja de 1D no está en la calidad de la operación sino en que hace **menos operaciones al año (11,5 frente a 15,7 y 13,8), tiene menor ratio ganancia/pérdida (2,7 frente a 3,2 y 3,3) y su peor DD es mayor** (episodios de 2023 y 2026).

**Veredicto por criterios** (ventana común salvo indicación)

| Criterio | 1H | 4H | 1D |
|---|---|---|---|
| Rentabilidad / CAGR | **1º** | 2º | 3º |
| Drawdown | 2º | **1º** | 3º |
| Rentabilidad ajustada (Calmar, a igual DD) | 2º | **1º** | 3º |
| Profit Factor ($) | 2º | **1º** | 3º |
| Robustez a costes (Calmar con ×3) | 2º | **1º** | 3º |
| Nº de operaciones (evidencia) | **1º** | 2º | 3º |
| Consistencia entre ventanas | 2º | **1º** | 3º |
| Tramo reciente (2026, ~10 operaciones) | **1º** | 2º | 3º |

**Recomendación**: operar **4H** como temporalidad principal. 1H es una alternativa válida: con riesgo 5 % da +4,6 pp de CAGR a cambio de +4,5 pp de DD, pero a igual drawdown 4H rinde más y la diferencia entre ambas no es estadísticamente distinguible. 1D solo tiene sentido si valoras operar con poca atención (11 operaciones/año), sabiendo que ha sido la menos eficiente.

## 3. Conciliación con tus números de TradingView

Emulé V8.pine con la semántica de TradingView (`engtv.py`, costes de TradingView: 0,06 % comisión + 2 ticks de slippage):

| Caso | Mi emulación de V8.pine (rentab. / DD / win / PF / operaciones) | Tu TradingView |
|---|---|---|
| 1D histórico completo (desde 2015) | +2.486 % / -22,4 % / 51 % / 1,97 / 122 | +2.491,84 % / 18 % / 46 % / 1,929 / ? |
| 4H 2024-01-01→2026-10 | +81 % / -16,6 % / 41 % / 1,95 / 39 (arranque limpio); +79 % / -16,6 % / 41 % / 1,89 / 41 (corrida continua) | +42 % / 14 % / ? / 2,17 / ? |
| 1H ~9 meses | +10 % / -11,4 % / 50 % / 1,88 / 10 (arranque limpio); +11 % / -11,4 % / 50 % / 1,93 / 12 (continua) | +36 % / 12 % / ? / 1,46 / 11 |

- **1D: reproducido.** Rentabilidad +2.486 % frente a tu +2.491,84 %; beneficio bruto 517.085 frente a 526.424 y pérdida bruta 261.973 frente a 272.840; PF 1,97 frente a 1,929. El win rate no lo reproduzco (50,8 % frente a 46 %; con arranque en 2017-08 sale 46,0 %, y no sé si es casualidad) y mi DD (−22,4 %, cierre a cierre con la operación abierta) es mayor que tu 18 %, que probablemente se mide de otra forma.
- **4H: parcialmente.** Tu +42 % / PF 2,17 se parece a un arranque entre febrero y junio de 2024 (con 5.750 velas: +41,4 %, PF 1,63; con 5.000 velas: +36,1 %), no a arrancar el 2024-01-01 (+81 %). Con arranques distintos (entre 4.250 y 7.000 velas) la rentabilidad de 4H en "2 años" se mueve entre +23 % y +99 %: **el resultado de un periodo corto depende del día de inicio**.
- **1H: no reproducido** (ningún inicio da más de +16 %; tú ves +36 %, con 11 operaciones). Con 10 operaciones y un periodo bajista-lateral, el resultado depende de detalles (datos de tu exchange, la última vela, una posición abierta).
- Mi backtest de Python usa costes más duros que TradingView; por eso en TradingView todo sale algo mejor (V8 informe, §3).

## 4. Qué se probó y por qué se descartó (`experimentos_V9.csv`, `trials9.jsonl`)

**Diagnóstico previo (solo TRAIN+VAL, V8)**: las perdedoras ya pierden poco (R mediano −0,55 / −0,53 / −0,66 en 1H / 4H / 1D) y el 44 % / 43 % / 34 % de ellas llegó a estar +2 ATR en beneficio antes de perder, de modo que el trailing ya recorta gran parte de la pérdida; entre las ganadoras, el 90 % no se mueve más de 2,3-2,9 ATR en contra antes de su máximo, así que un stop inicial mucho más ajustado cortaría ganadoras. Las mejores 10 % de operaciones aportan el 48-53 % del beneficio bruto (sin ellas el PF baja a 1,29-1,35): **es un sistema de colas gordas**, y cualquier regla que recorte las grandes ganadoras (TP, trailing más cerrado) cuesta más de lo que ahorra. El peor DD de 1D en DEV (−16,8 %) es un único episodio de 2023 (abril-octubre).

| Familia | Variantes | Resultado | Por qué se descarta |
|---|---|---|---|
| G1 Salida temporal (140/280 h; sin 1/2 ATR de beneficio) | 4 | ninguna pasa | TRAIN y VAL de signo contrario o nulo; en 1D empeora TRAIN (−0,15 a −0,24) |
| G1 Salir si cierre < EMA / < EMA−1 ATR | 2 | **1 pasa (1D, EMA−1 ATR)** | Cae en ETC (−0,05) y aporta +0,6 pp de CAGR a igual DD; 1H y 4H no pasan |
| G1 Salir si BTC < EMA 800 h | 1 | peor | ΔCalmar DOGE −0,25 (1H) y −0,39 (4H) y R/operación negativo en las tres TF |
| G2 Trailing 5→7 ATR tras +8 ATR / 5→8 tras +12 | 2 | peor | Empeora TRAIN o VAL en las tres TF y sube el DD (hasta 2,1 pp peor) |
| G2 TP 20 ATR → trailing 3,5 ATR | 1 | peor | −0,2 a −0,6 de Calmar en BTC, DOGE y VAL; DD de 1H 4,5 pp peor |
| G3 No entrar si extensión sobre EMA > 6 / > 8 ATR | 2 | **casi** (1D, > 6: ETH TRAIN +0,89, VAL +0,24, DOGE +0,14, BTC −0,02) | Falla el criterio por BTC; mirada exploratoria: **2015-17 −6,29 de Calmar** (+96 % frente a +306 %: las grandes tendencias empiezan muy extendidas), ETC −0,23. En 1H/4H BTC y DOGE empeoran (−0,2 a −0,6) |
| G3 Cierre de la vela de ruptura en el 50 % / 70 % superior | 2 | inestable | Signos contrarios TRAIN/VAL (1H, 4H: +0,6/−0,47; +0,32/−0,38) |
| G3 Tamaño ×0,5 si extensión > 6 ATR | 1 | peor | BTC/DOGE −0,1 a −0,28 en 1H y 4H |

Criterio de selección (por temporalidad, contra V8): ΔCalmar ETH > 0 en TRAIN **y** VAL; ΔCalmar BTC y DOGE ≥ 0; ΔDD ETH no peor de 1 pp; ΔR por operación ETH > 0. Holdouts solo para las que pasan: 2015-17 (1D), ETC, 2024→2026-10, costes ×2, igual DD, años.

**Aviso estadístico**: 45 pruebas dan 1-2 "aciertos" por azar; el que apareció (1D, EMA−1 ATR) se comportó como tal. Por eso no cambio V8.

**Lo que ya estaba descartado y no repetí** (V6/V7/V8): pirámide, cortos, reentrada, salidas parciales, entrada por stop, stop al cierre, throttle por DD, trinquetes, multi-velocidad, filtros de volatilidad/ADX/régimen largo, TP 0-40, N×L×ATR×k (hasta 3.360 combinaciones en 1D), ETH/BTC. **No probé**: volumen (la cola de 2026 no tiene volumen), filtros de renta variable/dominancia, nuevos activos. El stop inicial más estrecho (kI) ya estaba en la búsqueda de V6.

## 5. Método, validación y límites

- **Protocolo**: no hay OOS virgen para V9 (OOS1 2024→2026-01 se miró 3 veces y OOS2 2026-01→10 se abrió en V8). Por eso: (1) selección solo con TRAIN/VAL; (2) holdouts (2015-17, ETC) solo para candidatas aprobadas; (3) 2024→2026-10 solo como veto; (4) todo en `oos_access_log.txt`. Con esto, que V9 = V8 **no añade sobreajuste**. Las cifras de OOS1/OOS2 de V8 ya eran conocidas, así que esas ventanas valen como descripción, no como prueba independiente.
- **Limitaciones**: ~12-16 operaciones/año por temporalidad; las comparaciones entre 1H y 4H no son concluyentes; el bootstrap por bloques no incluye cambios de régimen no vistos; 1D solo tiene el filtro BTC con respaldo débil (V8, §1); datos de 2015-17 y 2026 de otros proveedores que Binance; los números de TradingView en periodos cortos no son reproducibles al detalle.
- **Siguientes pasos razonables**: (1) usar 4H con riesgo 4,0-4,3 % si quieres DD ≤ 14-15 % (CAGR ≈ 24-26 % en el backtest); (2) repetir V8 cuando haya 6-12 meses nuevos de datos; (3) probar más activos antes de seguir tocando la lógica; (4) si quieres mejorar de verdad 1D, hace falta información nueva, no más reglas sobre el precio de ETH.

## 6. Archivos

`informe_V9.md`, `experimentos_V9.csv`, `trials9.jsonl`, `v9_prereg.txt`, `oos_access_log.txt`, `tabla_TF_normalizada_V8.csv` (todas las métricas por ventana, V7 y V8), `igual_drawdown_V8_por_TF.csv`, `frontera_riesgo_V8.csv`, `costes_V8_por_TF.csv`, `mezcla_temporalidades_V8.csv`, `bootstrap_bloques_TF_V8.csv`, `retorno_anual_ETH_V8_por_TF.csv`, `emulacion_TV_V8_vs_tus_numeros.csv`, `backtest_v9.zip` (código). El Pine sigue siendo `V8_ETH_Donchian_EMA_ATR_TP_BTC.pine` (sin cambios).
