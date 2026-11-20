# trading-claude

Desarrollo y optimización de estrategias de trading sobre ETH (TradingView / Pine Script v6 + backtests en Python). Convención: `w` + versión = SHORT, `v` + versión = LONG.

## Estructura
| Ruta | Qué hay |
|---|---|
| `csvs/` | Datos OHLCV. ETHUSDT 1D/4H/1H (Binance, 2017-08-17 → 2026-01-06) usados por los backtests; BTCUSDT y DOGEUSDT (15m, 1h, 4h) y ETCUSDT (1h, 4h); tres extractos pequeños `ETHUSDT-*-2026-01-*.csv` en bruto (timestamp unix en ms); `ext2026/` = ETH/USD de 2026-01-06 a noviembre de 2026 (Twelve Data 1H/4H, Alpha Vantage 1D) para extender los CSV de Binance. |
| `estrategia short/` | Versiones SHORT w1–w11, `w12/` (intento sin mejora), `tv_match/` y `ENCARGO_CODEX.md`. **Empezar por `estrategia short/README.md`.** |
| `estrategia long/` | Versiones LONG (v3, v4, v6–v10): Pine, informes (`informe_V8/V9/V10.md`) y carpetas `backtest_vN/` con los motores. |

## Notas para quien lea el repo
- En `estrategia long/` varias carpetas están anidadas (`backtest_v6/backtest_v6/`, `backtest_v7/backtest_v7/`, `backtest_v10/backtest_v10/`). **No aplanarlas:** algunos scripts calculan la raíz del repo desde su propia ubicación (p. ej. `HERE/../../..`).
- Algunos scripts long conservan rutas absolutas de sesiones anteriores (`/home/claude/...`, `/mnt/user-data/uploads`). Hay que ajustarlas antes de ejecutarlos en otra máquina.
- Los resultados de las versiones short no son comparables sin mirar el modelo de costes y los tramos de cada una (ver tabla en `estrategia short/README.md`).
- Para comparar contra TradingView, usar `estrategia short/tv_match/` (comisión 0,06 % + slippage 0,06 %, ventanas de 2.500 velas en 4H y 1H).
