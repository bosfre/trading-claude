# estrategia short — ETH SOLO SHORT (versiones `w`)

Convención de nombres: las estrategias **short** se llaman `w` + versión (w1, w2…); las **long** se llaman `v` + versión (ver `../estrategia long/`). Todo el Pine Script está en `//@version=6`.

## Contenido por versión
| Carpeta | Contiene | Notas |
|---|---|---|
| `w1/` | `backtest_eth_short.py` | Motor de la primera versión (EMA 200, ruptura 75, ATR 14, Chandelier 3,5, riesgo 3 %). Parte de ETHUSDT 15m y agrega a 1H/4H. El Pine de w1 **no está** en el repo. |
| `w2/`, `w3/` | — | **No están en el repo** (ni Pine ni informes). |
| `w4/` | Pine, `backtest_w4.py`, `w4_vs_w3_equity.png` | `backtest_w4.py` es el motor de referencia: reproduce W4 y W8 exactos. |
| `w5/` | Pine, `W5_resultados.md` | Sin script de backtest en el repo. |
| `w6/` | Pine, `W6_resultados.md` | Sin script de backtest en el repo. |
| `w7/` | — | **No está en el repo.** |
| `w8/` | Pine, `W8_resultados.md` | Base W4 + stop más ajustado. Sin script propio: se reproduce con `w11/backtest_w11.py` o `tv_match/`. |
| `w9/` | Pine, `W9_resultados.md` | W8 + mejoras de calidad por temporalidad. Sin script propio. |
| `w10/` | Pine, `W10_resultados.md` | **Reconstrucción** (el archivo original no estaba disponible cuando se hizo W11; ver `w11/W11_resultados.md`). `backtest_w11.py` la reproduce como baseline. |
| `w11/` | Pine, `W11_resultados.md`, `backtest_w11.py` | Baseline W10 + stop por tipo de entrada. Uso: `python backtest_w11.py ../../csvs` (necesita `ETHUSDT_1h/4h/1d.csv`). |
| `w12/` | `W12_resultados.md`, `backtest_w12.py`, `exp12.py`, `diag12.py`, `build_ext_data.py`, `data_raw/`, `resultados/` | **Intento de mejora sobre W11: sin mejora robusta, no hay Pine W12.** Motor con costes de TradingView y datos hasta nov-2026; contiene el test fuera de muestra de W10/W11 en 2026. |
| `ENCARGO_CODEX.md` | — | Encargo para Codex: revisión de los Pine (margen, costes) y búsqueda de mejora con walk-forward y test final reservado. |
| `tv_match/` | Motor, datos, resultados, README propio | Backtest de W8/W9 con las condiciones del TradingView del usuario. Ver su README. |

## Datos
Los CSV de ETHUSDT (Binance, 2017-08-17 → 2026-01-06) están en `../csvs/` (`ETHUSDT_1d.csv`, `ETHUSDT_4h.csv`, `ETHUSDT_1h.csv`). `tv_match/data/` lleva sus propios datos (ETH/USD hasta noviembre de 2026) para que sea autocontenido.

## Tramos
`backtest_w4.py`/`backtest_w11.py`: TRAIN 2017-08-17 → 2021-12-31 · VALIDATION 2022-01-01 → 2023-12-31 · OOS 2024-01-01 → 2026-01-10 (OOS fuera de toda optimización). W5 y W6 usaron otros tramos (TRAIN 2017-08 → 2020-12, VALID 2021-01 → 2023-06, OOS 2023-07 → 2026-01), así que sus cifras no son comparables tal cual con W8+.

## Modelos de costes (no son iguales entre versiones)
| Versiones | Comisión | Slippage |
|---|---|---|
| W5 | 0,05 % por lado | ver `W5_resultados.md` |
| W6 | 0,05 % por lado | 0,02 % (doble en entradas stop) |
| W8–W11 (`backtest_w4.py`, `backtest_w11.py`) | 0,05 % por lado | 0,03 % por lado |
| `tv_match/`, `w12/` | **0,06 % por lado** (la del usuario en TradingView) | **0,06 % por lado** (confirmado). Los Pine W9–W11 siguen con comisión 0,08 % y `slippage=0`: ver `ENCARGO_CODEX.md` |

## Límites de TradingView (plan gratuito del usuario)
- **1D:** ve todo el historial (desde 2015).
- **4H y 1H:** máximo 2.500 velas por gráfico.
- No puede exportar la lista de operaciones, así que no se puede comparar operación a operación.

## Hallazgos a tener en cuenta
1. Los costes no explican la diferencia con TradingView; la explican la **serie de datos** (vendor y fecha de inicio) y la **ventana de velas**.
2. **1H con 2.500 velas no genera operaciones** en W8/W9: la EMA de régimen equivale a 2.400 velas de 1H.
3. **2026 es un test limpio (no usado para optimizar) y es negativo** en 1D y 4H para W8/W9; hay que comprobar cualquier versión nueva sobre 2026.
4. Los resultados 1D cambian mucho según el vendor de datos (p. ej. 2018 en W8: +95 % con Binance, +157 % con ETH/USD de Alpha Vantage).

5. **W11 no mejora a W10 en 2026** (test fuera de muestra, desde 2026-01-07, costes de TradingView): 1D −19,2 % frente a −12,8 %; 4H +6,7 % frente a +8,9 %; 1H +14,3 % frente a +15,5 % (comisión 0,06 % + slippage 0,06 %). Pocas operaciones (26–37), no concluyente, pero la ventaja de W11 solo está confirmada en el periodo de diseño. Ver `w12/W12_resultados.md`.

## Pendiente
- Alinear los Pine W9–W11 con las condiciones confirmadas (comisión 0,06 % + slippage 0,06 % ≈ 0,12 % por lado, modelado como comisión porcentual) y revisar `margin_short` (ver `ENCARGO_CODEX.md`).
- Recuperar o regenerar `w1`–`w3`, `w7`, el Pine de `w1` y los scripts de backtest de W5–W10, si se quieren reproducibles uno a uno.
