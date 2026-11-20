# Revisión estática inicial: W10/W11 Pine frente al motor

Estado: revisión de código, no paridad certificada. Fecha: 2026-11-20.

## Lógica que coincide

- Ambos Pine calculan señales al cierre y ordenan entrada market para la apertura siguiente (`process_orders_on_close=false`).
- W10 arriesga 1D/4H/1H = 5/4/6 %, con tope de nocional 2×. W11 conserva 1D/4H y baja 1H a 5,5 %.
- W10: `stop = close_señal + mult × ATR_eq`. W11 aplica a rupturas `rho × mult`, con `rho=0,70` en 1D/4H y 1,00 en 1H; si ruptura y pullback coinciden, prevalece ruptura. Ese multiplicador también cambia el tamaño calculado, el stop inicial y el trailing.
- El motor Python (`backtest_w11.py`) codifica las mismas señales de ruptura/pullback, EMA recursiva, ATR Wilder, percentil de volatilidad desplazado una barra y stops por tipo de entrada. La traducción estática parece coherente; falta la comparación orden a orden con TradingView.

## Diferencias materiales por resolver

1. **Margen/liquidación.** Pine declara `margin_short=50`, equivalente a apalancamiento teórico 2×, además de `maxLev=2`. TradingView fuerza liquidación cuando equity actual cae por debajo del margen requerido. El motor Python limita nocional a 2×, pero no simula margin calls; por tanto, el límite de tamaño no basta para reproducirlo. Hay que extraer/contar eventos “Margin Call” en TradingView y añadir esa mecánica al emulador antes de validar W10/W11.
2. **Costes.** Pine cobra 0,08 % de comisión por ejecución y slippage cero. Python aplica 0,05 % de comisión + 0,03 % de slippage por lado. El coste esperado se parece, pero el fill, la base de comisión, el tamaño y el PnL no son idénticos. Hacer comparación controlada: primero Pine equivalente (comisión 0,08 %, slip 0); luego costes separados del motor y sensibilidad ×2.
3. **Tamaño de entrada con gap.** Pine calcula `qty` usando el cierre de señal en `qty = notional / close`; el motor usa el precio de apertura siguiente (y slippage) como divisor. Si abre con gap, las cantidades difieren aunque coincidan señal y riesgo nominal.
4. **Barras con stop y parcial.** TradingView resuelve órdenes según su ruta OHLC inferida (o Bar Magnifier); el motor prioriza siempre el stop cuando stop y TP parcial podrían ejecutarse en la misma vela. Esto es conservador, pero no replica necesariamente el orden de fills de TradingView. Separar estos casos y comparar con el listado de operaciones.
5. **Financiación.** Los Pine no modelan funding; el backtest tampoco. Si la estrategia representa un perpetual, medir funding histórico aparte y después incluirlo de forma temporalmente correcta; no mezclarlo con comisión/slippage.

## Datos disponibles en este checkout

Está `ETHUSDT_1d.csv` (2017-08-17 a 2026-01-06), pero no aparecen los CSV ETHUSDT 1H/4H requeridos por `backtest_w11.py`. Por tanto, aún no se puede reproducir localmente la validación de W10/W11 en 1H/4H con los datos exactos del informe. El informe W11 muestra resultados 2026 dentro de un OOS agregado 2024–enero 2026; ese segmento ya no es un holdout virgen.

## Siguiente comprobación

Congelar parámetros y comparar operaciones de TradingView con el motor con costes, margen y fills igualados. No interpretar los resultados de búsqueda hasta que la primera divergencia de fill esté localizada. El protocolo de selección está en `preregistro_W12_walk_forward.md`.

