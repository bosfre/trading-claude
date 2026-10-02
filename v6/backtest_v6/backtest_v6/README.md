# Backtest V6 / búsqueda de mejoras sobre V3 (ETH, BTC, DOGE · 1H, 4H, 1D)

Requisitos: `pip install numpy pandas numba`. Edita `R` y `SH` en `data.py` para apuntar a tu clon del repo
(`csvs/` para BTC/DOGE y `estrategia short/ETHUSDT_15m.csv` para ETH) y `U` para los CSV nuevos.
ETH 1H/4H/1D se construyen agregando el CSV de 15m (solo barras completas). Motor y costes = los de `bt.py` del repo
(comisión 6 pb, slippage ETH 6 pb / BTC 4 / DOGE 10 por lado, +1x slippage en stops, funding 0,005 %/8 h en largos).

| Fichero | Para qué |
|---|---|
| `eng.py` | Motor (numba): señal al cierre, entrada en la apertura siguiente, stop intrabarra, gaps, TP, trailing |
| `sigs.py`, `gen.py` | V3, V4, V5 (=W1 corto) y el generador paramétrico de señales |
| `baseline.py` | V3/V4/V5 en todas las ventanas |
| `search.py`, `search2.py` | Búsqueda aleatoria (1.500 + 40.000 configuraciones por temporalidad, solo datos <= 2023) |
| `core.py`, `robust.py`, `freeze.py` | Objetivo, ranking por robustez de vecindad, eliminación hacia atrás. Escribe `final_cfg.json` |
| `diag.py` | Test de cohorte (¿predice el DEV al OOS?) y cambios individuales sobre V3 |
| `risk.py` | Rejilla de riesgo por operación (2 %-10 %) |
| `final2.py`, `final3.py` | Tablas finales, costes x2/x3, remuestreo de operaciones, mezcla de TF, años |
| `newcsv.py` | Análisis de los CSV nuevos por separado |
| `resultados_completos.csv` | Todas las métricas: versión x TF x activo x ventana (TRAIN/VAL/OOS/FULL) |
| `oos_access_log.txt` | Registro del único acceso al OOS para las configuraciones congeladas |

Ventanas: TRAIN 2017-08 → 2021-12 · VAL 2022-01 → 2023-12 · OOS 2024-01 → 2026-01 (fin de datos).
