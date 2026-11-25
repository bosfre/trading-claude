# backtest_vw1 — backtest conjunto de VW1 (LONG V10 + SHORT W10)

Requiere `pip install numba pandas numpy scipy`. Lee los datos de `csvs/` (ETH y BTC) y el tramo 2026-01 → 2026-10 de `estrategia long/v9/backtest_v9/datos_nuevos/`; reutiliza el código de señales de `estrategia long/v10/backtest_v10/` (V10) y `estrategia short/w11/backtest_w11.py` (configuración W10) sin modificarlo. Las rutas se calculan desde la ubicación de los scripts.

Orden: `python validate_vw1.py` (el motor reproduce V10 y W10 con un solo lado activo) → `python run_vw1.py` (VW1 vs V10 sola vs W10 sola, tramos, costes, solapamiento, remuestreo) → `python criterios_vw1.py` (C1-C5 y variante flip) → `python mk_informe_vw1.py` (genera `../informe_VW1_backtest.md`).

- `eng_vw.py` motor conjunto (una equity, una posición neta, sin inversión; opción `flip` solo para la variante descartada). `prep_vw.py` datos, señales y métricas.
- `vw1_prereg.txt` pre-registro escrito antes de ejecutar; `oos_access_log.txt` accesos a ventanas OOS.
- CSV: `resultados_VW1.csv`, `solapamiento_VW1.csv`, `bootstrap_VW1.csv`, `retorno_anual_VW1.csv`, `criterios_VW1.csv`, `validacion_motor.csv`.
