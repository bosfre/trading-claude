# backtest_v10 (código de la investigación V10 = optimización de V9)
Requiere python3, numpy, pandas, numba (`pip install numpy pandas numba`). Los datos de ETH (1h/4h/1d, 2017-08 → 2026-01-06) van en `datos/` (no incluidos en el zip: son tus `ETHUSDT_1h/4h/1d.csv`); BTC, DOGE y ETC se leen de `../../../csvs/` del repo `bosfre/trading-claude`; el tramo 2026-01 → 2026-10 (Twelve Data) y el histórico 2015-17 (FMP) van en `datos_nuevos/` (tampoco incluido en el zip: copia la carpeta del repo, `estrategia long/v9/backtest_v9/datos_nuevos/`).

Orden recomendado:
- `repro10.py` reproduce la línea base V9 (= V8) en ETH. `test_eng10.py` comprueba que el motor nuevo `eng10.py` (palancas apagadas) es idéntico a V8 en las 9 series.
- `v10_prereg.txt` pre-registro (hipótesis, criterios, reglas R1-R3 y 3 enmiendas fechadas). `exp10.py` arnés (señales y palancas nuevas); `exp9.py`/`exp8.py`/`data8.py` arnés heredado de V9.
- `round10a.py` (12 variantes), `round10b.py` (estancamiento con umbrales alcanzables), `round10c.py` (curva de sensibilidad del enfriamiento): SOLO TRAIN/VAL/DEV. `dbg_stall.py` comprueba que la palanca de estancamiento sí actúa. `mk_exp10.py` → `experimentos_V10.csv`.
- `anchor10.py` (24 anclas en 1D, 4 en 4H) y `ens10.py` (ensamble de anclas).
- `final10.py` (V9 vs V10 por ventanas, frontera de riesgo, costes, sensibilidad de parámetros, retorno anual), `v7ref10.py` (referencia V7 sin filtro BTC), `verify10.py` (verificación independiente desde la lista de operaciones), `mk_report10.py` → `../informe_V10.md`.
- Registros: `trials10.jsonl`, `oos_access_log.txt`, `v10_prereg.txt`.
