# Estrategia LONG (ETH) — índice por versiones

Lógica vigente (V8 = V9 = V10 = V11): ruptura Donchian 140 h + filtro de régimen EMA 800 h + filtro BTC > EMA 800 h; stop/trailing 5 ATR (ATR 56 h), objetivo 20 ATR, riesgo 5 %, apalancamiento máx. 2x. Periodos en horas, por lo que se comporta igual en 1H, 4H y 1D.

| Versión | Qué cambia / conclusión | Informe | Pine |
|---|---|---|---|
| v3 | Primera versión Pine | — | `v3/v3_claude.pine` |
| v4 | Segunda iteración | — | `v4/estrategia_V4_ETH.pine` |
| v6 | Primera versión con backtest validado en Python | `v6/backtest_v6/README.md` | `v6/V6_ETH_Donchian_EMA_ATR_TP.pine` |
| v7 | Misma señal que V6; corrige el fallo del objetivo (TP) en el Pine | `v7/informe_V7.md` | `v7/V7_ETH_Donchian_EMA_ATR_TP.pine` |
| v8 | Añade filtro BTC > EMA 800 h | `v8/informe_V8.md` | `v8/V8_ETH_Donchian_EMA_ATR_TP_BTC.pine` |
| v9 | 15 hipótesis probadas, todas rechazadas; lógica = V8 | `v9/informe_V9.md` | (usa el de V8) |
| v10 | Lógica V9 + panel de diagnóstico, preset de riesgo (1H 3,3 % / 4H 4,2 % / 1D 3,0 %), sin pirámide | `v10/informe_V10.md` | `v10/V10_ETH_Donchian_EMA_ATR_TP_BTC.pine` |
| v11 | Filtros macro Nasdaq/DXY (0/21 pasan) y diagnóstico de funding (sin relación); lógica = V10 | `v11/informe_V11.md` | (usa el de V10) |

Estructura de cada versión: informe, CSV de resultados/comparativas, `.pine` si cambió, y `backtest_vN/` con el código Python (motor, experimentos, registros de pruebas y de acceso al OOS).

## Reproducir
- Datos: `csvs/` en la raíz del repo (ETH 1h/4h/1d incluidos).
- V10 y V11: `cd v10/backtest_v10` (o `cd v11`) y ejecutar los scripts. V11 reutiliza el motor de `v10/backtest_v10/` sin cambios (ver `v11/LEEME.md`).
- V6–V9 leen ETH 15m desde `csvs/ETHUSDT_15m.csv` (ya incluido); sus `data.py` cargan correctamente.

## Pendiente / no disponible en el repo
Solo existían en los zips originales y no se han podido recuperar (se añaden si los subes): informe de V6, Pine de V5, CSV extra de V9 (frontera, costes, mezcla, bootstrap, retorno anual, emulación TradingView, `v9_prereg`, `trials9`, log OOS), y de V11 `oos_access_log11.txt`, `trials11.jsonl`, `funding_eth.csv`, `test11.py`, `desc11.py`, `round11a.pkl`. 
