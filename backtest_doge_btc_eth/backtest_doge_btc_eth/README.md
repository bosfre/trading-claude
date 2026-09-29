# Backtest cuantitativo BTC/ETH/DOGE — Estrategia V3

## Archivos
- `bt.py` — motor de backtest (numba): split temporal con bloqueo del OOS, indicadores
  causales, simulación con costes, stops y trailing, cálculo de métricas.
- `harness.py` — evaluación multi-activo/timeframe (9 series principales + 2 extra de ETC),
  agregación de cartera equiponderada.
- `strategies.py` — reglas de V1 (descartada), V2, V3 (aceptada) y V4 (descartada).
- `run_final.py` — reproduce el resultado final. `python3 run_final.py --oos` incluye la
  prueba final sobre el conjunto out-of-sample (bloqueada por defecto).
- `registro_iteraciones.csv` — tabla Versión | Cambios | Rentabilidad | Drawdown | Profit
  Factor | Sharpe | Operaciones | Resultado OOS | Decisión.

## Requisitos
`pip install numpy pandas numba --break-system-packages`

Colocar los CSV originales (`BTCUSDT_15m.csv`, `BTCUSDT_1h.csv`, `BTCUSDT_4h.csv`,
`ETHUSDT_15m.csv`, `DOGEUSDT_15m.csv`, `DOGEUSDT_1h.csv`, `DOGEUSDT_4h.csv`,
`ETCUSDT_1h.csv`, `ETCUSDT_4h.csv`) en `/mnt/user-data/uploads/` (o editar `UP` en `bt.py`).
ETH 1h/4h se derivan automáticamente del CSV de 15m (no había ficheros nativos).
