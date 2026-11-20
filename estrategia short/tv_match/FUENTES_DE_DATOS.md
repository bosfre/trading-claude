# Fuentes de datos para backtests (ETH)

Autorizado por el usuario: usar todas las fuentes de datos de mercado conectadas para descargar datos de ETH cuando hagan falta (p. ej. completar las velas hasta hoy o el historial antiguo que no está en los CSV).

## Límites de TradingView del usuario (plan gratuito)
- 1D: ve todas las velas desde cualquier fecha (su gráfico llega hasta 2015).
- 4H y 1H: máximo 2.500 velas por gráfico.
- No puede exportar la lista de operaciones ni el OHLCV.

## Fuentes disponibles
| Fuente | Herramienta | Verificado |
|---|---|---|
| Alpha Vantage | `DIGITAL_CURRENCY_DAILY` (symbol=ETH, market=USD, datatype=csv, return_full_data=true) | Diario ETH/USD completo desde 2015-08-08 hasta hoy (4.123 filas). El resultado es muy grande y se guarda solo en un archivo: procesarlo con Python, no leerlo entero. |
| Alpha Vantage | `CRYPTO_INTRADAY` | Sin probar |
| Twelve Data | `get_time_series` (symbol=ETH/USD, interval=1day/4h/1h, outputsize máx. 5000, start_date/end_date) | El diario empieza el 2018-01-17 (no sirve para 2015-2017). 4H y 1H sin probar. |
| FMP | `crypto`, `chart` | Sin probar |
| CoinMarketCap | `get_crypto_quotes_latest`, etc. | Solo cotizaciones y análisis, no velas históricas largas |

## Notas
- Estos datos son ETH/USD agregado, no ETHUSDT de Binance: hay pequeñas diferencias de precio (en el cierre diario: mediana 0,1 %, percentil 95 1,5 %). Los resultados de la estrategia son sensibles al vendor.
- CSV de referencia 1D: Binance 2017-08-17 → 2026-01-06 en medio, y ETH/USD de Alpha Vantage en 2015-08 → 2017-08 y 2026-01 → 2026-11 (serie híbrida).
