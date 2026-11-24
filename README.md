# trading-claude

Estrategias de trading sobre Ethereum desarrolladas y validadas con backtests (disciplina TRAIN / VALIDACIÓN / OOS, criterios pre-registrados).

- `estrategia long/` — estrategia LONG (tendencia: Donchian + EMA + ATR). Una carpeta por versión (v3 … v11). Empieza por [`estrategia long/README.md`](estrategia%20long/README.md).
- `estrategia short/` — estrategias SHORT.
- `estrategias VW/` — estrategias combinadas LONG + SHORT en un solo Pine (VW1 = V10 + W10). Empieza por [`estrategias VW/README.md`](estrategias%20VW/README.md).
- `csvs/` — datos de precios compartidos (ETH 1h/4h/1d, BTC, DOGE, ETC…). Los backtests leen de aquí.

Los backtests calculan la raíz del repo a partir de su propia ubicación, así que se pueden ejecutar desde cualquier carpeta (`pip install numba pandas numpy scipy`).
