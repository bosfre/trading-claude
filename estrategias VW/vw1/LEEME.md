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
- Heredadas y vigentes: sensibilidad de 1D al ancla del día (V10), evidencia 1D débil y toma parcial de 1H que el emulador puede resolver distinto (W10); sin funding; solo ETHUSDT.

## Backtest conjunto (Python)

Informe completo: [`informe_VW1_backtest.md`](informe_VW1_backtest.md). Código, CSV y pre-registro: [`backtest_vw1/`](backtest_vw1/). Motor validado: con un solo lado activo reproduce V10 y W10 con igualdad exacta de la curva de equity.

Con comisión 0,08 % por lado, ETH 2017-08-17 → 2026-10-03, riesgos por defecto:

| TF | VW1 rent. / DD | Calmar VW1 | Calmar V10 sola | Calmar W10 sola | Entradas SHORT perdidas por la posición única |
|---|---:|---:|---:|---:|---:|
| 1H | +14.990 % / −24,8 % | 2,96 | 1,84 | 1,27 | 9,1 % |
| 4H | +6.026 % / −26,6 % | 2,14 | 1,84 | 0,79 | 6,5 % |
| 1D | +3.506 % / −27,5 % | 1,75 | 1,03 | 0,88 | 7,8 % |

- V10 y W10 casi nunca están dentro a la vez (0,5-0,7 % de las barras), así que la regla de una posición cuesta poco y solo al SHORT; el LONG no pierde ninguna entrada.
- Se cumplen los cinco criterios pre-registrados (C1-C5), también con costes ×2 y ×3. La variante con inversión de posición (VW1-flip) no supera el criterio y se descarta.
- **Matiz importante:** la ventaja de Calmar sobre cada lado por separado está concentrada en TRAIN (2017-21). Por tramos, el Calmar de VW1 supera al del mejor componente en 3/3 TF en TRAIN, 2/3 en VAL, 1/3 en OOS1 (2024→2026-01) y 3/3 en OOS2 (2026, 9 meses). Fuera de muestra VW1 rinde más pero con más DD. En 4H el SHORT es el eslabón débil.
- El DD de VW1 es entre 0,2 y 4,1 puntos mayor que el del peor de sus componentes; el remuestreo de operaciones da DD mediano −26 % y 5 % peor −39 % a −41 %.
- Cifras esperadas para comparar con TradingView: apartado 8 del informe. No habrá coincidencia exacta (datos, emulador, indicadores); pon el rango desde 2017-08-17.

## Siguientes pasos naturales

1. Compilar en TradingView (1H, 4H, 1D) y comparar con la tabla del apartado 8 del informe; comprobar también que con `Operar SHORT` desactivado se parece a V10 y con `Operar LONG` desactivado a W10 (con la diferencia de costes del punto 1).
2. Decidir si el SHORT debe pasar a W11 (stop por tipo de entrada, 1H sin toma parcial; ver `estrategia short/w11/W11_resultados.md`) como VW2. Cualquier cambio debe medirse con el mismo motor conjunto (`backtest_vw1/`) y validarse fuera de muestra; en VW1 no se ha tocado ningún parámetro.
3. Investigar por qué el Calmar fuera de muestra (OOS1) no mejora en 4H y 1D, antes de añadir más lógica.
