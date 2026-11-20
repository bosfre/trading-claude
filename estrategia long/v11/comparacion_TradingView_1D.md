# Comparación con TradingView (1D, operaciones 1-27, oct 2015 → jun 2017)

Fecha: 2026-11-19. Origen: capturas de la "Lista de operaciones" del Probador de estrategias del usuario (gráfico ETH 1D de TradingView).

## Resultado
- **Con el filtro BTC sin dato antes de 2017-08-17, el motor reproduce 26 de las 27 entradas de TradingView (±1 día) y 21 de 27 salidas.** Con el filtro BTC activo usando BTC real desde 2015 (datos FMP), solo coinciden 17 de 27 entradas.
- Explicación: en TradingView el símbolo de BTC que usa el Pine por defecto (BINANCE:BTCUSDT) empieza en agosto de 2017. Antes de esa fecha no hay dato y el filtro no actúa (el Pine lo programa así: sin dato → no filtra). Por eso en 2015-2017 TradingView opera como la versión sin filtro BTC (V7). Es coherente con el diseño, no es un error.
- **Consecuencia:** el 1D de TradingView incluye 2015-2017 (ETH entre 0,7 y 330 USD), que mi backtest de V10 no usaba (empieza el 2017-08-17, primer dato de Binance). En el motor, con esa condición: 2015-10 → 2017-08 = +262 % (33 operaciones); 2017-08 → 2026-10 = +463 %; total 2015-10 → 2026-10 = +1.937 % (138 operaciones, win rate 47,8 %, PF en $ 1,72, DD −23,4 %). Los retornos se componen: 3,62 × 5,63 ≈ 20,4 (+1.938 %). Es lo que explica gran parte de la diferencia entre el +1.500 % / +2.491 % que ves en TradingView y mis +483 %.
- **Lo que no se explica del todo:** TradingView (V8, 1D, historial completo) da +2.491,84 %, DD 18 %, PF 1,93, win rate 46 %; el motor da +1.937 %, DD −23,4 %, PF 1,72, win rate 47,8 %. Probables causas (no comprobadas): costes distintos (el Pine usa comisión 0,06 % y deslizamiento de solo 2 ticks, unos 0,02 USD, mientras que el motor aplica un 0,06 % de deslizamiento por operación, mucho mayor), el origen de los datos (precios de entrada 1-2 % distintos: 0,73 frente a 0,71 en la primera operación) y la fecha de fin de los datos.
- **Desviaciones concretas (6 de 27 salidas no coinciden; una entrada, la #25, no la abre el motor):** #6 (el motor sale el mismo día, TradingView 3 días después), #15 y #16 (salida con 2 días de diferencia), #24 y #26 (salida más temprana en el motor) y #25 (TradingView entra el 5 may 2017 y el motor no). Son operaciones sensibles al ATR y a mínimos intradía, y los datos OHLC de 2015-2017 difieren entre fuentes. No tengo prueba de la causa.

## Cautela
2015-2017 es un tramo con muy poca liquidez (ETH a 1-10 USD, volumen diario muy bajo). Operaciones como entrar a 0,73 USD con un tamaño de 2-3 mil USD no se pueden dar por ejecutables con el deslizamiento que usa el motor. Los resultados que incluyen ese tramo son una referencia histórica, no una expectativa realista; por eso mis informes comparan desde 2017-08.

## Detalle de las 27 operaciones
| # | TradingView: entrada | precio | salida | precio | Motor: entrada | precio | salida | precio | Entrada coincide | Salida coincide |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2015-10-27 | 0,73 | 2015-10-31 | 0,93 | 2015-10-27 | 0,71 | 2015-10-31 | 0,95 | sí | sí |
| 2 | 2015-11-18 | 1,00 | 2015-11-26 | 0,80 | 2015-11-18 | 0,98 | 2015-11-26 | 0,82 | sí | sí |
| 3 | 2015-12-12 | 0,92 | 2015-12-16 | 0,83 | 2015-12-12 | 0,90 | 2015-12-16 | 0,86 | sí | sí |
| 4 | 2016-01-09 | 1,01 | 2016-01-13 | 1,08 | 2016-01-09 | 0,99 | 2016-01-13 | 1,10 | sí | sí |
| 5 | 2016-01-16 | 1,22 | 2016-01-19 | 1,30 | 2016-01-16 | 1,20 | 2016-01-19 | 1,32 | sí | sí |
| 6 | 2016-01-24 | 1,91 | 2016-01-27 | 2,13 | 2016-01-24 | 1,89 | 2016-01-24 | 1,48 | sí | no |
| 7 | 2016-02-08 | 2,81 | 2016-02-11 | 3,92 | 2016-02-08 | 2,79 | 2016-02-11 | 3,94 | sí | sí |
| 8 | 2016-02-12 | 6,02 | 2016-02-13 | 4,78 | 2016-02-12 | 6,00 | 2016-02-13 | 4,80 | sí | sí |
| 9 | 2016-02-23 | 5,62 | 2016-03-07 | 9,30 | 2016-02-23 | 5,60 | 2016-03-07 | 9,31 | sí | sí |
| 10 | 2016-03-13 | 13,47 | 2016-03-14 | 11,35 | 2016-03-13 | 13,46 | 2016-03-14 | 11,36 | sí | sí |
| 11 | 2016-05-01 | 8,85 | 2016-05-03 | 8,50 | 2016-05-01 | 8,84 | 2016-05-03 | 8,51 | sí | sí |
| 12 | 2016-05-13 | 10,26 | 2016-05-24 | 12,62 | 2016-05-13 | 10,24 | 2016-05-24 | 12,82 | sí | sí |
| 13 | 2016-06-01 | 14,08 | 2016-06-17 | 18,15 | 2016-06-01 | 14,16 | 2016-06-17 | 18,66 | sí | sí |
| 14 | 2016-07-23 | 14,69 | 2016-07-24 | 12,76 | 2016-07-23 | 15,00 | 2016-07-24 | 12,85 | sí | sí |
| 15 | 2016-08-10 | 12,21 | 2016-08-18 | 10,72 | 2016-08-10 | 12,29 | 2016-08-16 | 11,03 | sí | no |
| 16 | 2016-09-01 | 11,64 | 2016-09-04 | 11,46 | 2016-09-01 | 11,67 | 2016-09-06 | 11,51 | sí | no |
| 17 | 2016-09-11 | 12,16 | 2016-09-21 | 13,13 | 2016-09-11 | 12,21 | 2016-09-21 | 13,90 | sí | sí |
| 18 | 2016-10-19 | 12,63 | 2016-10-25 | 11,89 | 2016-10-19 | 12,56 | 2016-10-25 | 11,89 | sí | sí |
| 19 | 2016-12-30 | 8,35 | 2017-01-05 | 9,65 | 2016-12-30 | 8,30 | 2017-01-05 | 9,66 | sí | sí |
| 20 | 2017-01-22 | 10,94 | 2017-02-09 | 10,79 | 2017-01-21 | 10,66 | 2017-02-09 | 10,92 | sí | sí |
| 21 | 2017-02-15 | 13,06 | 2017-03-03 | 18,96 | 2017-02-15 | 13,17 | 2017-03-03 | 19,26 | sí | sí |
| 22 | 2017-03-12 | 21,27 | 2017-03-17 | 44,85 | 2017-03-12 | 21,68 | 2017-03-17 | 45,94 | sí | sí |
| 23 | 2017-03-25 | 51,82 | 2017-04-03 | 45,15 | 2017-03-25 | 52,96 | 2017-04-03 | 44,56 | sí | sí |
| 24 | 2017-04-13 | 46,22 | 2017-05-01 | 78,35 | 2017-04-13 | 46,51 | 2017-04-16 | 48,87 | sí | no |
| 25 | 2017-05-05 | 94,42 | 2017-05-07 | 82,78 | — | — | — | — | no | no |
| 26 | 2017-05-19 | 96,11 | 2017-05-25 | 185,22 | 2017-05-19 | 96,26 | 2017-05-23 | 160,28 | sí | no |
| 27 | 2017-05-31 | 226,02 | 2017-06-14 | 333,23 | 2017-05-31 | 228,81 | 2017-06-14 | 343,11 | sí | sí |
