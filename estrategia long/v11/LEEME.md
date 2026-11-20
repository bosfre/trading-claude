# V11 — filtros macro sobre V10

Resultado: V11 = V10 en lógica (ningún filtro macro mejora; 0 de 21 pruebas pasan). Detalle en `informe_V11.md`; criterios fijados antes de ejecutar en `v11_prereg.txt`.

## Archivos
- `informe_V11.md`, `v11_prereg.txt`, `comparacion_TradingView_1D.md`
- `experimentos_V11.csv`, `descriptivo_V11_ETH.csv`, `diagnostico_funding_V11.csv`
- `macro_daily.csv` — Nasdaq, UUP y DXY sintético (diario)
- Código: `exp11.py` (arnés), `round11a.py` (ronda de 7 variantes), `verify11.py`, `funding11.py`, `mk_macro.py`

## Cómo ejecutar
Requiere `numba pandas numpy scipy`. Desde esta carpeta: `python3 round11a.py`. `exp11.py` añade automáticamente `../v10/backtest_v10` al path (motor `eng10.py` y arnés `exp9/exp10` de V10, sin cambios) y lee `../../csvs/`.
Comprobado: la variante NQ>SMA200 reproduce los ΔCalmar del informe (1H −0,11/−0,86, 4H +0,47/−1,37, 1D +0,23/−0,56).

## Notas
- `verify11.py` y `mk_macro.py` apuntan a archivos de entrada externos (CSV Nasdaq/UUP y FX de Alpha Vantage) que no están en el repo; sirven como documentación del proceso. `funding11.py` necesita `funding_eth.csv` (no incluido).
- `round11a.py` escribe `round11a.pkl` y `exp11.py` escribe `trials11.jsonl` en esta carpeta al ejecutarse.
