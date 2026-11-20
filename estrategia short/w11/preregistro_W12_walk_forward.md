# Pre-registro W12: paridad de ejecución y walk-forward

Fecha de congelación: 2026-11-20. Alcance: ETHUSDT short; versiones Pine W10/W11; 1D, 4H y 1H. Este documento se fija antes de ejecutar nuevas variantes. Las pruebas/decisiones ya descritas en `W10_resultados.md` y `W11_resultados.md` cuentan como exploratorias, no como validación independiente.

## Tarea 1 — Paridad Pine ↔ motor

Congelar como referencia los Pine W10 y W11, sin cambiar parámetros. Antes de juzgar rentabilidad, comparar la lista de operaciones y equity con el motor en ventanas idénticas, en este orden: fecha/señal, precio/fecha de entrada, tipo de entrada (ruptura/pullback), cantidad, stop inicial, trailing, parcial TP, precio/fecha de salida y costes.

### Semántica que el motor debe reproducir

- Señal evaluada al cierre; entrada market en la apertura siguiente (`process_orders_on_close=false`).
- En shorts, gap por encima del stop: cubrir al open; si no, comprobar el máximo intrabar. El trailing calculado al cierre empieza a regir en la barra siguiente.
- W10: stop inicial = cierre de señal + `mult × ATR_eq`; tamaño calculado al cierre con riesgo y tope de nocional 2×.
- W11: mismo proceso, pero `multTrade = mult × rho` para ruptura (si coinciden ruptura y pullback prevalece ruptura); el `multTrade` gobierna tamaño, stop inicial y trailing.
- W10 1H: parcial de 25 % a 1,5 ATR_eq. Si TP y stop son tocados en la misma vela, conservar ambos escenarios de emulador y usar stop primero como caso conservador; verificar contra Strategy Tester antes de decidir cuál coincide.
- Diferenciar fills, comisión y slippage. Pine declara comisión 0,08 % por ejecución y slippage cero. El motor histórico declara comisión 0,05 % más slippage 0,03 % por lado. Comparar primero costes igualados al Pine y después costes separados/estresados; no atribuir la diferencia a la lógica.
- Verificar margen: Pine fija `margin_short=50` (requisito del 50 %) y limita el nocional por cálculo a 2×. El motor limita `MAXLEV=2` pero debe comprobarse si reproduce las liquidaciones por margen del emulador. Registrar precio de liquidación/margin call; no asumir que el cap 2× equivale al margen de TradingView.

### Criterio de paridad

En una muestra de operaciones que incluya gaps, stops y el TP parcial, se exige coincidencia exacta de señales/tipo de entrada y número de operaciones; diferencia de entrada/salida ≤ 1 tick salvo costes configurados; y equity final dentro de 0,5 % relativo una vez igualados costes y propiedades. Si no se cumple, no se inicia búsqueda de parámetros: se localiza la primera divergencia de operación y se corrige el motor.

## Tarea 2 — Búsqueda walk-forward

### Datos y aislamiento

- Fuente primaria: velas Binance ETHUSDT, UTC, mismas velas que Pine. Validar continuidad, duplicados, OHLC inválidos y límites de fecha.
- Investigación y selección: 2017-08-17 a 2025-12-31. No leer, cargar, consultar ni resumir filas de 2026 hasta congelar selección, código, parámetros y costes.
- El informe W11 existente ya presenta un OOS agregado 2024–enero 2026 y dice que `rho` se seleccionó tras ver toda la muestra. Por eso 2026 ya no es un holdout virgen del proyecto. Se reserva aquí para una única medición terminal, claramente etiquetada como contaminada por exposición previa; la siguiente prueba verdaderamente virgen será futura.

### Familia registrada

No reabrir la minería amplia de entradas/salidas ya descrita en los informes. Una sola pregunta nueva: ¿aporta valor la regla de stop por tipo de entrada (`rho`) de W11 frente a W10 (`rho=1`) fuera de muestra, cuando la selección se hace solo con el pasado?

- Valores candidatos fijos: `rho ∈ {1.00, 0.85, 0.75, 0.70}`. Sin valores intermedios, extensiones ni segundo barrido.
- Tres temporalidades evaluadas separadamente (1D, 4H, 1H): familia de 12 comparaciones; el cambio solo se adoptará en la temporalidad que cumpla todos los criterios.
- En cada fold, seleccionar rho con mayor CAGR/DD neto de costes sobre todo el historial anterior disponible; empates a favor de rho=1.00. Aplicar el elegido sin reajuste al siguiente año natural.
- Walk-forward: entrenamiento inicial 2017-08-17 a 2020-12-31; evaluación 2021, 2022, 2023, 2024 y 2025, reentrenando al cierre de cada año. Mantener señales calentadas con barras anteriores; no reiniciar indicadores en el límite del fold. Medir retornos solo de las operaciones/variación de equity atribuibles al año evaluado.
- Referencias por fold: W10 fijo (rho=1) y W11 fijo (rho=.70), con el mismo riesgo, costes y motor corregido. No ajustar riesgo para ganar la comparación.

### Costes, margen y ejecución

La paridad de Tarea 1 determina el motor antes de esta búsqueda. Presentar resultados con costes Pine (0,08 % por lado, sin ticks de slippage) y una sensibilidad de costes ×2; presentar además funding solo como análisis separado si la serie perpetua y el calendario de pagos están disponibles. Incluir margen/liquidaciones reales del modelo de TradingView. Si la paridad no se alcanza, todo resultado de optimización queda bloqueado.

### Métricas y aceptación

Métrica primaria: CAGR/DD de los retornos netos acumulados fuera de muestra; secundarias: CAGR, drawdown máximo, retorno, profit factor, expectativa por operación, win rate, operaciones y exposición/apalancamiento. No seleccionar por retorno total aislado.

Una variante se acepta para una temporalidad solo si: (1) mejora CAGR/DD frente a W10 en al menos 4 de 5 folds; (2) el incremento compuesto OOS 2021–2025 es positivo y el límite inferior del IC 95 % de bootstrap por bloques de 14 días para la diferencia de log-equity es > 0; (3) DD máximo conjunto no empeora más de 2 puntos porcentuales; (4) conserva signo positivo al duplicar costes; (5) Holm–Bonferroni mantiene significación familiar al 5 % para las 12 comparaciones. Si falla cualquiera, no se adopta. Si no hay suficientes trades para estimar el intervalo (menos de 30 operaciones OOS agregadas), resultado inconcluso, no aprobado.

### Medición terminal de 2026

Solo después de publicar el informe de selección 2017–2025, ejecutar una vez el candidato congelado y las referencias W10/W11 sobre el tramo 2026 disponible. Registrar hash del código, parámetros, fechas y costes antes de abrir ese resultado. No retocar parámetros a partir de esta medición.

