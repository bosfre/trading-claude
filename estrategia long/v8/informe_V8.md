# V8 (ETH, solo largos) — informe

## 1. Conclusión

**V8 = V7 + una confirmación de régimen de BTC**: solo se abren largos si, además de las condiciones de V7, el cierre de BTC está por encima de su EMA de 800 h (la misma EMA que ya se exige a ETH; no hay parámetro nuevo). Es el único cambio estructural, entre ~60 variantes nuevas y una rejilla de 3.360 combinaciones, que superó los criterios que fijé antes de mirar los datos de validación. Se aplica a 1H, 4H y 1D.

Lo que sí está demostrado y lo que no:

| | 1H | 4H | 1D |
|---|---|---|---|
| Mejora en TRAIN y VAL (selección) | sí | sí | TRAIN sí, **VAL no** |
| Mejora en OOS 2024-26 (ya abierto antes) | sí | sí | sí (menor) |
| Prueba hacia atrás 2015-17 | — | — | sí (Calmar 6,2 → 10,4) |
| A igual drawdown (CAGR extra, DEV) | +18,7 pp | +8,5 pp | +3,0 pp |
| Costes ×2 y ×3 | mantiene | mantiene | mantiene |
| **OOS virgen 2026-01 → 2026-10** | ≈ igual (+0,10 Calmar) | peor (−0,22) | peor (−0,55) |
| Años 2018-25 con V8 > V7 | 6 de 8 | 7 de 8 | 6 de 8 |

**Lectura honesta**: en 1H y 4H la evidencia es consistente en cinco ventanas distintas; en 1D (tu prioridad) es la más débil: mejora en el histórico completo y en 2015-17, pero falla en VAL y en el OOS virgen (6 operaciones, rentabilidades cercanas a cero en ambas versiones, así que no es concluyente). La mejora anual media es de +4,5 a +7 pp con t ≈ 1,4-1,8: consistente, **no estadísticamente concluyente**. No he encontrado ninguna mejora estructural que mejore 1D de forma robusta por sí sola; V8 mejora sobre todo 1H/4H y arrastra una mejora modesta en 1D.

## 2. Comparativa directa (ETH, mismo riesgo 5 %, costes del repo)

V6 y V7 tienen **las mismas señales en Python** (V7 solo corrige el Pine), así que la columna "V6 = V7" es común.

**2017-08 → 2026-01-10 (la ventana de los informes de V6/V7)**

| TF | Versión | Rentabilidad | CAGR | Máx. DD | Operaciones | Calmar |
|---|---|---|---|---|---|---|
| 1H | V6 = V7 | +824,8 % | 30,3 % | −22,5 % | 148 | 1,35 |
| 1H | **V8** | **+1.260,5 %** | 36,4 % | −17,9 % | 131 | 2,04 |
| 4H | V6 = V7 | +680,2 % | 27,7 % | −17,2 % | 135 | 1,61 |
| 4H | **V8** | **+998,3 %** | 33,0 % | −17,2 % | 117 | 1,92 |
| 1D | V6 = V7 | +385,0 % | 20,7 % | −18,8 % | 110 | 1,10 |
| 1D | **V8** | **+513,1 %** | 24,1 % | −17,3 % | 99 | 1,39 |

**TRAIN 2017-08 → 2021 / VAL 2022-23 / OOS 2024-01 → 2026-01-10** (rentabilidad; DD entre paréntesis)

| TF | Versión | TRAIN | VAL | OOS |
|---|---|---|---|---|
| 1H | V7 | +391,9 % (−18,1) | +17,1 % (−22,5) | +60,6 % (−21,9) |
| 1H | V8 | +541,3 % (−17,9) | +26,3 % (−17,1) | +67,9 % (−17,0) |
| 4H | V7 | +302,7 % (−15,9) | +25,6 % (−15,7) | +54,2 % (−17,2) |
| 4H | V8 | +378,1 % (−15,4) | +34,4 % (−11,2) | +70,9 % (−17,2) |
| 1D | V7 | +179,2 % (−15,7) | +41,6 % (−14,8) | +22,7 % (−18,8) |
| 1D | V8 | +275,2 % (−13,8) | **+28,7 % (−16,8)** | +26,9 % (−17,3) |

**OOS virgen 2026-01-11 → 2026-10-03 (0,73 años, datos que nadie había usado)**

| TF | V7 | V8 | Operaciones V7/V8 |
|---|---|---|---|
| 1H | +11,9 % (DD −12,4) | +12,4 % (DD −12,1) | 13 / 12 |
| 4H | +2,9 % (DD −11,8) | +1,0 % (DD −11,3) | 10 / 9 |
| 1D | −4,3 % (DD −9,1) | −8,0 % (DD −9,1) | 6 / 6 |

**Total 2017-08 → 2026-10-03 (9,1 años)**: 1H +934,7 % → +1.429,1 % (DD −22,5 → −21,8); 4H +703,0 % → +1.009,5 % (DD −18,9 → −17,3); 1D +364,0 % → +463,9 % (DD −25,8 → −23,2).

**Prueba hacia atrás (1D, ETH 2015-08 → 2017-08, datos diarios compuestos de FMP, no de Binance)**: V7 +261,8 % (DD −14,2 %, 33 op., Calmar 6,2) → V8 +305,6 % (DD −9,5 %, 23 op., Calmar 10,4). En DOGE 2017-09 → 2019-07: +220,4 % → +243,9 %, DD −15,4 → −11,0 %.

**Otros activos (no se ha ajustado nada en ellos)**: DOGE 2019-26 mejora en los 3 TF (Calmar 1H 0,53 → 0,84; 4H 0,97 → 1,47; 1D 0,20 → 0,29), pero en su OOS 2024-26 empeora en 1H (2,15 → 1,54) y 4H (1,45 → 1,29). **ETC (nunca usado): efecto neutro** (Calmar 2018-26 1H 0,16 → 0,17; 4H 0,43 → 0,48; 1D 0,31 → 0,36; OOS algo menos negativo). BTC no cambia (el filtro usa BTC como referencia). El efecto es real en ETH y DOGE, pequeño o nulo en ETC.

Todas las ventanas, activos y métricas (Sharpe, Sortino, PF, win rate) están en `comparativa_V6_V7_V8.csv`.

## 3. Tus diferencias de TradingView, con el histórico completo

Emulé en Python la semántica real de cada Pine (script al cierre, orden en la apertura siguiente, `strategy.exit` sin stop en la barra de relleno, indicadores exactos de Pine; ver `engtv.py`). Con la lógica "Python" el emulador reproduce mi backtest (91-93 % de operaciones idénticas).

**Qué diferencia realmente a V6.pine de V7.pine**: casi solo el **take profit** (V6.pine no lo activa nunca porque borra `atrEntry` en la barra de señal). El TP recorta las ganancias más grandes y a cambio baja el drawdown:

| Costes de TradingView, 2017-08 → 2026-01 | V6.pine | V7.pine |
|---|---|---|
| 1H | +1.009 % (DD −22,8) | +1.063 % (DD −20,1) |
| 4H | +860 % (DD −20,6) | +742 % (DD −16,6) |
| 1D | +496 % (DD −18,1) | +473 % (DD −18,1) |
| 1D desde 2015-08 (tu ventana) | +2.110 % | +1.994 % |

**¿Se mantienen tus diferencias (V6: 1H −2,7 %, 4H +91 %, 1D +1.500 %; V7: −9 %, +67 %, +1.869 %)?**
- **4H: sí.** V6.pine > V7.pine también con el histórico completo (+16 % relativo en rentabilidad a cambio de +4 pp de DD). Con la ventana que mejor encaja (5.000 velas que acaban en abril de 2026) mi emulación da +72,5 % / +61,1 % frente a tus +91 / +67 %: misma dirección, magnitud menor.
- **1D: no.** Que V7 supere a V6 **no se mantiene**: con datos desde 2015 y desde 2017, V6.pine ≥ V7.pine en la emulación (−5 a −6 % relativo para V7). Dato curioso: mi emulación de V7.pine reproduce tu 1D casi exacto (+1.863 % frente a tus +1.869 %, ventana desde 2015 hasta abril de 2026), lo que valida el emulador; lo que **no** reproduzco es tu V6 (+1.971 % frente a +1.500 %).
- **1H: no explicado.** En 5.000 velas V6.pine y V7.pine dan lo mismo en mi emulación (−4 % a −8 % con ventanas que acaban en febrero-abril de 2026, parecido a tus −2,7 / −9 %), pero tu diferencia de 6 pp entre ambas no la reproduzco; con ~7 meses y 7-8 operaciones cualquier detalle la mueve.
- **Tu ventana**: 1D "10-11 años" es ETH desde 2015 (no está en tus CSV; la añadí con FMP). Tus resultados de 4H y 1D encajan con 5.000 velas que acaban hacia **abril de 2026**; por eso en 2026-01 → hoy no coinciden con lo que ves ahora.
- **Para cerrarlo**: exporta de TradingView la *lista de operaciones* de V6.pine en 1D (CSV) y la comparo con la emulación; es la única forma de saber por qué tu V6 queda por debajo.

**Dos hallazgos que sí afectan a TradingView** (leídos en el código; no verificados en la plataforma):
1. **Margen**: ni V6.pine ni V7.pine declaraban `margin_long`; TradingView usa 100 % (sin apalancamiento) y las entradas de más de 1x (stop pequeño en 1H/4H) podrían recortarse o rechazarse. En 1H eso baja ~10 % la rentabilidad total; en 1D no cambia (el tamaño nunca supera 1x). V8 declara `margin_long = 50`.
2. **Costes**: `slippage = 2` son 2 ticks (0,02 USDT) frente a los 6 pb por lado (~1,8 USDT) del backtest; en TradingView todo sale más favorable (+20 % a +26 % de rentabilidad total en 2017-26).

Tablas: `paridad_pine_V6_V7_V8.csv`, `parity_v6pine_vs_v7pine.csv`, `parity2_decomp.csv`, `escaneo_ventana_TradingView.csv`.

## 4. Método

- **Datos nuevos**: (a) ETH/BTC/DOGE 1h desde 2026-01-06 hasta 2026-10-03 (Twelve Data; en ETH coincide con Binance al 0,02 % en el solape; sin huecos), agregados a 4H y 1D; (b) diario previo a 2017-08 (FMP: ETH desde 2015-08, BTC desde 2013, DOGE desde 2017-09; precio compuesto, no Binance). Estos datos se usaron como **OOS virgen (2026) y prueba hacia atrás (2015-17)**.
- **Sellado y pre-registro**: el tramo 2026 se dejó sellado hasta congelar V8 (`load_all(ext=False)` devuelve exactamente la serie de V6/V7). Las reglas de adopción están escritas y con fecha **antes** de mirar PRE/OOS (`v8_prereg.txt`) y todos los accesos están en `oos_access_log.txt`. Reconozco dos fugas menores: vi los precios diarios de ETH 2026 al descargarlos (sin resultados de estrategia) y tus números de TradingView ya contenían información aproximada de 2026.
- **Selección** solo con TRAIN (2017-08 → 2021) y VAL (2022-23), en ETH + BTC + DOGE; criterio por temporalidad: ΔCalmar ETH > 0 en TRAIN y VAL, ΔCalmar BTC y DOGE ≥ 0, ΔDD ETH no peor de 1 pp.
- **Validación**: prueba hacia atrás 2015-17, OOS 2024-26 (ya abierto dos veces en V7, por eso no cuenta como virgen), OOS virgen 2026, ETC, a igual drawdown, costes ×2/×3, año a año, y análisis de las operaciones eliminadas.
- Motor `eng8.py`: con las palancas nuevas apagadas es idéntico a V6/V7 al bit (9 series).

## 5. Qué se probó y por qué se descartó (`experimentos_V8.csv`, `trials8.jsonl`: 58 variantes registradas + 3.360 de la rejilla 1D; ~210 más en V7)

| Familia | Resultado | Por qué se descarta |
|---|---|---|
| Stop de trailing evaluado al cierre (6) | acepta solo en 1H y solo con kT = 4 | Con kT = 5 (el valor actual) no pasa: sensibilidad a un parámetro = ruido. En 1D el DD empeora 3-12 pp |
| Salida parcial 33 % / 50 % a +6 / +10 ATR (4) | peor en todo | Baja rentabilidad sin bajar DD; en 1H sube el DD |
| Reentrada tras stop con canal más corto (6) | inconsistente | TRAIN/VAL de signo contrario; BTC 1H −0,5/−0,9 de Calmar; DD hasta +7 pp |
| Entrada por stop en el canal (+0 / 0,5 ATR) (2) | inestable | Margen 0 falla en BTC y 1D VAL (−0,79); margen 0,5 ATR solo acepta en 4H y su vecino no |
| Salida por mínimos de 35/70/140 h (3) | peor | ETH 4H y 1D empeoran en TRAIN y VAL |
| Margen de ruptura 0,25/0,5/1 ATR (3) | inestable | ETH 1H −2,0 a +1,1 y no consistente en otros activos |
| **Escala de tiempo 1D nativa (3.360 combinaciones: N 4-55, EMA 20-200, ATR 10-20, k 1,5-4, TP 0-12)** | **0 de 3.360** mejoran ETH a la vez en TRAIN y VAL | V7 en 1D ya está en un óptimo local. Además la correlación de rangos entre mejora 2017-23 y mejora 2015-17 es ≈ 0 (ETH −0,01, BTC +0,11, DOGE −0,09): **el ajuste de parámetros no se traslada fuera de muestra** |
| Fuerza relativa ETH/BTC (6) | peor | Empeora ETH en las 3 TF |
| **Régimen de BTC (6 + 22 de meseta)** | **aceptada** | ver sección 6 |
| (V7) cortos, pirámide, throttle por DD, trinquetes, multi-velocidad, filtros de volatilidad y de régimen largos, TP 0-40, N×L (~210) | ninguna pasó | ver `informe_V7.md` |

Aviso estadístico: con ~60 variantes y 5 condiciones por variante cabe esperar 1-2 "aceptaciones" por azar (se observaron 2 en la ronda estructural, ambas inestables y descartadas). Por eso el candidato final se eligió además por tener una **explicación económica** (las rupturas de ETH fallan cuando BTC está bajo su tendencia), una **meseta** (EMA de BTC de 300 a 1.000 h) y se fijó con la longitud natural (800 h) en lugar de la mejor.

## 6. Robustez de V8

- **Meseta**: con EMA de BTC de 300 a 1.000 h el ΔCalmar de ETH es positivo en 1H y 4H en TRAIN y VAL; con 1.600 h es negativo. En 1D es positivo en TRAIN y negativo en VAL (−0,2 a −0,6) para L ≥ 400.
- **A igual drawdown (DEV)**: V8 con riesgo reescalado hasta el DD de V7 gana +18,7 / +8,5 / +3,0 pp de CAGR (1H / 4H / 1D). No es solo menos riesgo.
- **Costes (ETH 2017-26, CAGR / DD)**: ×1: V7 1H 30,3/−22,5, 4H 27,7/−17,2, 1D 20,7/−18,8 → V8 36,4/−17,9, 33,0/−17,2, 24,1/−17,3. ×2: V7 25,6/−25,5, 23,5/−18,8, 17,6/−19,9 → V8 32,1/−19,6, 29,1/−18,1, 21,1/−18,3. ×3: V7 20,7/−30,4, 19,4/−22,2, 14,6/−21,0 → V8 27,4/−23,2, 25,4/−18,9, 18,2/−19,8.
- **Año a año (ETH, V7 → V8, %)**: 1H 2018 −2,6→0,8; 2019 50,9→50,4; 2020 109,8→110,4; **2021 43,6→81,1**; 2022 −5,0→2,3; 2023 23,2→23,4; **2024 22,5→33,8**; 2025 30,8→27,0. 4H: −2,9→−8,5; 47,5→49,9; 89,5→95,1; **47,2→77,3**; 0,0→5,5; 25,7→27,4; **25,9→37,6**; 22,7→25,6. 1D: −7,5→−6,1; 5,9→13,1; 71,8→85,8; **39,4→59,7**; 5,1→−1,4; 34,7→30,5; 19,3→19,3; 3,8→7,4. **Buena parte de la mejora está en 2021 y 2024**; el resto de años es mixto-positivo.
- **Operaciones eliminadas** (ETH 2017-26): 29 (1H), 28 (4H) y 17 (1D) operaciones que V7 abría y V8 no tenían **win rate 17-24 %** y R medio −0,10 a −0,19, frente a 44-45 % de las operaciones comunes. Es el mecanismo esperado, pero con 17-29 operaciones no es significativo por sí solo.
- **OOS virgen 2026**: no confirma en 4H/1D (ver sección 2). El periodo (ETH 3.100 → 1.500 → 2.680) es lateral/bajista y con 6-13 operaciones por temporalidad; ambas versiones quedan cerca de 0.

## 7. Limitaciones

- El Pine V8 **no está compilado ni probado en TradingView desde este entorno**. Con "Filtro de régimen BTC" desactivado es V7: compara ambas en tu gráfico y contrasta el nº de operaciones con `comparativa_V6_V7_V8.csv`.
- `request.security` de BTC: usa un BTC con histórico suficiente (BINANCE:BTCUSDT empieza en 2017-08; si no hay dato, el filtro no bloquea).
- 1D: evidencia mixta (VAL y OOS virgen en contra, histórico completo y 2015-17 a favor). No lo vendería como mejora demostrada.
- Pocas operaciones (≈ 12-16 al año por TF): diferencias de pocos puntos son ruido.
- Los datos 2015-17 y 2026 vienen de proveedores distintos a los CSV originales; en ETH 2026 coinciden con Binance al 0,02 %, los de 2015-17 son precio compuesto.
- Del OOS 2024-26 ya se miró tres veces (V7 cortos, V7 pirámide, V8); el único virgen era 2026 y ya está abierto. **Para futuras versiones habrá que esperar a datos nuevos.**

## 8. Siguientes pasos razonables

1. Compilar V8 en TradingView y comparar con y sin filtro; exportar la lista de operaciones de V6.pine 1D para cerrar la paridad.
2. Usar V8 solo en 1H y 4H si prefieres exigir confirmación en el OOS virgen; en 1D el filtro tiene el respaldo más débil.
3. Repetir `v8_oos2.py` cuando haya 6-12 meses más de datos como OOS realmente nuevo.
4. Si quieres menos drawdown, la palanca limpia sigue siendo el riesgo por operación (p. ej. 4 %).

## 9. Archivos

`V8_ETH_Donchian_EMA_ATR_TP_BTC.pine`, `comparativa_V6_V7_V8.csv`, `retorno_anual_ETH_V7_vs_V8.csv`, `experimentos_V8.csv`, `trials8.jsonl`, `paridad_pine_V6_V7_V8.csv`, `parity_v6pine_vs_v7pine.csv`, `parity2_decomp.csv`, `escaneo_ventana_TradingView.csv`, `oos_access_log.txt`, `v8_prereg.txt`, `backtest_v8.zip` (código y datos nuevos).
