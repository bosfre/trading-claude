# VW1 — ETH LONG (V10) + SHORT (W10) en una sola estrategia

**Archivo:** [`VW1_ETH_long_short.pine`](VW1_ETH_long_short.pine) (Pine Script v6). Es la base sobre la que se desarrollará la estrategia combinada.

## Origen (sin cambios de lógica)

| Lado | Versión de origen | Archivo en el repo |
|---|---|---|
| LONG | V10 (= V8 = V9 = V11 en lógica) | `estrategia long/v10/V10_ETH_Donchian_EMA_ATR_TP_BTC.pine` |
| SHORT | W10 | `estrategia short/w10/W10_ETH_short.pine` |

- **LONG (V10):** ruptura Donchian 140 h + EMA de régimen 800 h + filtro BTC > EMA 800 h; stop/trailing 5 ATR (ATR 56 h); objetivo 20 ATR; riesgo 5 %; apalancamiento máx. 2x. Parámetros en horas.
- **SHORT (W10):** régimen `close < EMA 600` (barras de 4h) + ruptura de mínimos o pullback fallido + filtro de volatilidad (percentil ATR% 1H 65 / 4H 75 / 1D 70) + stop Chandelier (mult. 1H 3,0 / 4H 3,0 / 1D 2,0); 1H con filtro de extensión 9 ATR y toma parcial 25 % a 1,5 ATR; riesgo 1H 6 % / 4H 4 % / 1D 5 %; apalancamiento máx. 2x. Parámetros en barras de 4h escaladas por temporalidad.

Todos los parámetros conservan sus valores y unidades originales. Cada lado va en su grupo de inputs (`LONG (V10) · …`, `SHORT (W10) · …`) y sus variables de estado llevan prefijo `lg` / `sh`.

## Qué se ha cambiado para que convivan

1. **Una sola `strategy()`:** comisión 0,08 % por lado, slippage 0 (modelo de coste de W10: 0,05 % + 0,03 %), `pyramiding = 0`, `margin_long = margin_short = 50`. El LONG paga algo más que en el Pine de V10 (0,06 % + 2 ticks) y menos que en su backtest Python (6 pb + 6 pb + funding).
2. **Una sola posición a la vez.** Con un LONG abierto se ignoran las señales SHORT y viceversa; no se invierte. Si coinciden señal LONG y SHORT en la misma barra no se opera. Ambos casos se cuentan en el panel de diagnóstico.
3. **Ventana de test común** para los dos lados. El fin por defecto pasa de 2026-12-31 (W10) a **2030-12-31** para que la estrategia no deje de operar a final de año; no afecta a ningún resultado histórico.
4. **Interruptores** `Operar LONG` / `Operar SHORT` (activos por defecto). Desactivando uno se obtiene el otro perfil aislado.
5. **Guarda de temporalidad global:** solo 1H, 4H y 1D (error en otra).
6. **Panel de diagnóstico unificado** (posición, entradas por lado, bloqueos del filtro BTC, conflictos, señales descartadas).

## Qué se ha verificado y qué no

Verificado (revisión estática, sin compilador de Pine):
- No hay nombres de variables duplicados ni usados antes de declararse.
- Todas las líneas de cálculo, gestión de stop/TP y dimensionamiento de V10 y W10 aparecen en VW1 idénticas salvo el renombrado de variables.
- Los valores por defecto, mínimos, máximos y pasos de los 38 inputs de origen coinciden, con la única excepción intencionada de `endT`.

**No** verificado:
- **No se ha compilado ni ejecutado en TradingView.** Hazlo antes de fiarte de nada y mira el panel.
- **No existe backtest conjunto de VW1.** Las cifras de V10 (p. ej. 1H +1.431 %, 4H +1.011 %, 1D +483 % a riesgo 5 %) y de W10 (1H +887 %, 4H +403 %, 1D +500 %) se midieron por separado, con motores, costes y tramos distintos, cada una en su propia cuenta. **No se pueden sumar** ni esperar de VW1: la posición neta única descarta operaciones que antes se tomaban.
- No se ha medido cuántas señales se pierden por solapamiento ni el drawdown conjunto.
- Heredadas y vigentes: sensibilidad de 1D al ancla del día (V10), evidencia 1D débil y toma parcial de 1H que el emulador puede resolver distinto (W10); sin funding; solo ETHUSDT.

## Siguientes pasos naturales

1. Compilar en TradingView (1H, 4H, 1D) y comprobar que con `Operar SHORT` desactivado reproduce V10, y con `Operar LONG` desactivado reproduce W10 (con la diferencia de costes del punto 1).
2. Backtest conjunto en Python (equity única, posición neta) con TRAIN / VALIDACIÓN / OOS, midiendo solapamientos, DD combinado y coste de la regla "no invertir", comparado con V10 y W10 por separado.
3. Decidir si el SHORT debe pasar a W11 (stop por tipo de entrada, 1H sin toma parcial; ver `estrategia short/w11/W11_resultados.md`) y si se permite invertir la posición. Cualquier cambio debe validarse fuera de muestra; en esta versión no se ha tocado ningún parámetro.
