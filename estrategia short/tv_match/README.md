# tv_match — backtest de W8 / W9 (ETH SHORT) con las condiciones de TradingView

Objetivo: que el backtest en Python use las mismas condiciones que el Strategy Tester de TradingView del usuario (plan gratuito), para poder comparar cifras sin diferencias de costes, ventana de datos ni ejecución.

## Condiciones fijadas (por el usuario)
| Concepto | Valor |
|---|---|
| Comisión | **0,06 % por lado** sobre el nominal de cada fill |
| Slippage | **PENDIENTE**: el usuario lo confirmará. Por ahora 0. Se pasa con `--slip` (fracción del precio por lado, p. ej. `--slip 0.0006`) |
| Ventana 1D | Historial completo (TradingView muestra todo, desde 2015-08) |
| Ventana 4H y 1H | Últimas **2.500 velas** (límite del plan gratuito) |
| Lista de operaciones de TradingView | No disponible (plan gratuito): no se puede comparar operación a operación |

## Semántica de ejecución (igual que los Pine W8/W9)
- Señal al cierre de la barra; entrada en la apertura de la siguiente.
- Cantidad = `min(maxLev·equity, riesgo·equity / dist) / close_señal`, con `dist = mult·ATR_eq/close`, tope 2x.
- Stop inicial `close_señal + mult·ATR_eq`; trailing `mínimo_desde_entrada + mult·ATR_eq` (solo baja), actualizado al cierre.
- Stop intrabarra con gap al open; si stop y toma parcial coinciden en la misma barra, manda el stop.
- Cada ventana se ejecuta como serie independiente: EMA sembrada con el primer cierre y sin operar hasta `emaLen` barras (como `warmedUp` en el Pine).
- Parámetros: ver `W8` y `W9` en `backtest_tv.py` (riesgo 1D 5 %, 4H 4 %, 1H 4 % en W8 / 6 % en W9; mult 1D 2,0, 1H/4H 3,0; W9 añade EMA rápida 55 en 1D y, en 1H, filtro de extensión 9 + toma parcial 25 % a 1,5 ATR).

## Datos (`data/`)
| Archivo | Contenido |
|---|---|
| `ETHUSD_1d_hybrid_2015_2026.csv` | ETH/USD Alpha Vantage 2015-08-08 → 2017-08-16, Binance ETHUSDT 2017-08-17 → 2026-01-06, Alpha Vantage 2026-01-07 → 2026-11-19 |
| `ETHUSD_4h_TD_ult2500.csv` | Twelve Data ETH/USD 4H, 2.499 velas cerradas (2025-09-29 → 2026-11-20) |
| `ETHUSD_1h_TD_ult2500.csv` | Twelve Data ETH/USD 1H, 2.499 velas cerradas (2026-08-08 → 2026-11-20) |
| `raw/` | Descargas originales sin tocar (se regeneran los CSV con `build_data.py`) |

Notas: Twelve Data 4H coincide con Binance (diferencia mediana 0 % en el solape). Alpha Vantage 1D difiere de Binance (cierre: mediana 0,1 %, p95 1,5 %) y los resultados son sensibles a la fuente: con la serie diaria solo de Alpha Vantage, 2018 sale +157 % en W8 frente a +95 % con Binance.

## Cómo ejecutar
```
python3 build_data.py                   # regenera los CSV de data/ desde data/raw/
python3 run_final.py                    # comisión 0,06 %, slippage 0
python3 run_final.py --slip 0.0006      # cuando se confirme el slippage
```
Necesita `numpy` y `pandas`. Resultados en `resultados/` (`resumen_final.csv`, `trades_<ver>_<tf>.csv`).

## Resultados actuales (comisión 0,06 %, slippage 0)
| TF | Versión | Ventana | Rentab. | DD | PF | Win rate | Ops |
|---|---|---|---:|---:|---:|---:|---:|
| 1D | W8 | 2015-08 → 2026-11 | +319,0 % | −39,7 % | 1,30 | 40,9 % | 176 |
| 1D | W9 | 2015-08 → 2026-11 | +529,1 % | −24,4 % | 1,51 | 44,9 % | 156 |
| 4H | W8 = W9 | 2.499 velas | +13,0 % | −21,9 % | 1,22 | 27,8 % | 36 |
| 1H | W8 = W9 | 2.499 velas | 0 % | — | — | — | 0 |

Referencia de TradingView (cifras del usuario, aprox.): W8 1D +327 % (DD 42 %); W9 1D +366 % (DD 27 %, PF 1,494); W4 1D +252 % (DD 29 %, PF 1,54, 110 ops).

## Hallazgos importantes
1. **Los costes no explican la diferencia con TradingView.** Pasar de 0,05 % + 0,03 % de slippage a 0,08 % de comisión sin slippage cambia el 1D de +449 % a +449 % (Binance 2017-2026). Lo que cambia las cifras es la serie de datos y la ventana.
2. **1H no es verificable con 2.500 velas:** la EMA de régimen equivale a 2.400 velas de 1H, así que no queda casi ninguna operable y salen 0 operaciones.
3. **2026 es un test limpio (no se usó para optimizar) y sale negativo:** en 1D, W8 −29 % (32 ops, 7 ganadoras) y W9 −11 % (27 ops, 7 ganadoras) en 2026. En 4H, 10 ganadoras de 36. Cualquier versión nueva (W10/W11) debe comprobarse sobre 2026 antes de darla por buena.
4. **Calibración imperfecta:** mi W4 en 1D da +198 %, DD −28,2 %, PF 1,43, 126 ops frente a +252 %, DD 29 %, PF 1,54, 110 ops en TradingView: parecido pero no idéntico (diferencias de datos entre fuentes).

## Historial
- Los informes y motores anteriores (W4–W9) usan costes 0,05 % + 0,03 % de slippage y cantidad al precio de entrada; ver `estrategia short/w4`, `w8`, `w9`.
- Este motor reproduce W8 1D (+449,3 %), 4H (+403,2 %) y 1H (+745,6 %) con ese modelo antiguo.
