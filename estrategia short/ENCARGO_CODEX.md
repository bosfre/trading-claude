# Encargo para Codex — mejorar la estrategia SHORT de ETH (siguiente versión: W12)

Lee primero, en este orden: `README.md` (raíz), `estrategia short/README.md`, `estrategia short/w11/W11_resultados.md`, `estrategia short/w12/W12_resultados.md`, `estrategia short/tv_match/README.md`.

## Objetivo
Encontrar una mejora **robusta** de W11 (short ETH en 1D, 4H y 1H) que se mantenga en datos nuevos, **o demostrar que no la hay**. Un informe honesto de «sin mejora» es un resultado válido. Está prohibido forzar una mejora o ajustar sobre el tramo reservado (`HOLDOUT26`).

## Condiciones fijas (no cambiar)
- **Costes:** comisión **0,06 % por lado** + slippage **0,06 % por lado** (≈ 0,12 % por lado), cantidad calculada al cierre de la señal, entrada en la apertura siguiente. Motor: `estrategia short/w12/backtest_w12.py` (`set_costs(0.0006, 0.0006, 'close')`; `cli_costs()` ya usa estos valores por defecto).
- **Datos:** `csvs/ETHUSDT_{1d,4h,1h}.csv` (Binance, hasta 2026-01-06) + `csvs/ext2026/` (ETH/USD hasta noviembre de 2026). Se cargan con `load(d, ext=True)`. No modificar los CSV.
- **Tramos de desarrollo:** TRAIN 2017-08-17 → 2021-12-31 · VALIDATION 2022 → 2023 · OOS 2024-01-01 → 2026-01-10. **`HOLDOUT26` (2026-01-07 →) es un test final: no se mira durante la búsqueda.**
- **Riesgo:** 1D 5 % · 4H 4 % · 1H 5,5 % (W11), tope de apalancamiento 2x. No subir el riesgo para inflar la rentabilidad.
- **Pine Script:** siempre `//@version=6`. Nomenclatura: short = `w` + versión.
- **Límites de TradingView del usuario:** 1D con historial completo; 4H y 1H con 2.500 velas máximo (con 1H, W8–W11 no operan en 2.500 velas porque la EMA de régimen necesita ~2.400). No puede exportar la lista de operaciones.

## Estado de partida (costes definitivos; ver `w12/resultados/baseline_W10_W11_tv_slip0.06.csv`)
| TF | Versión | Desarrollo (≤ 2026-01-10): Rentab. · DD · PF | 2026 (HOLDOUT26): Rentab. · DD · PF · Ops |
|---|---|---|---|
| 1D | W10 | +453,4 % · −21,0 % · 2,09 | −12,8 % · −25,8 % · 0,80 · 26 |
| 1D | W11 | +737,3 % · −21,1 % · 2,37 | −19,2 % · −29,3 % · 0,68 · 27 |
| 4H | W10 | +361,3 % · −25,1 % · 1,48 | +8,9 % · −22,8 % · 1,15 · 36 |
| 4H | W11 | +447,2 % · −21,8 % · 1,54 | +6,7 % · −22,8 % · 1,11 · 37 |
| 1H | W10 | +807,8 % · −18,4 % · 2,12 | +15,5 % · −26,2 % · 1,29 · 32 |
| 1H | W11 | +1.048,2 % · −18,7 % · 2,16 | +14,3 % · −29,4 % · 1,25 · 32 |

Hallazgos que condicionan la búsqueda: (1) **W11 no mejora a W10 en 2026**; (2) en 2026 el win rate cae (1D de 54 % a 30 %, 4H de 44 % a 27 %) pero **las pérdidas no vienen en racha** y el tamaño medio de ganancias y pérdidas casi no cambia; (3) ya se descartaron: toma parcial en 1D/4H, filtro de extensión, riesgo graduado por extensión, reducir riesgo tras un DD, trailing que se aprieta, enfriamiento tras pérdida, filtro de lateralidad (ER de Kaufman) y filtro de pendiente de la EMA de régimen (detalle en `W11_resultados.md` y `W12_resultados.md`).

## Tarea 1 — revisión del Pine W10/W11 frente al motor (rápida)
No se puede ejecutar TradingView desde aquí; es una revisión estática y de simulación.
1. **`margin_short=50` frente al tope 2x.** Los Pine declaran `margin_short=50` (apalancamiento máx. 2x) y el motor topa el nominal en 2x el patrimonio. Con el tope activo, el patrimonio iguala el margen exigido en la entrada y cualquier pérdida latente podría disparar un *margin call* en TradingView. El usuario ve etiquetas «Margin call» en su 1H de W10 (−21,6 %, 21 operaciones, 4 ganadoras, PF 0,469, DD 23,0 %, 1 ene–7 oct 2026, ETHUSD), mientras el motor da +22 % con 32 operaciones. **Hipótesis a comprobar:** implementar en el motor una regla de margin call tipo TradingView y ver si explica la diferencia; proponer `margin_short` menor (más margen) o un tope inferior a 2x y medir el coste en rentabilidad.
2. **Costes en el Pine.** W9–W11 usan `commission_value=0.08` y `slippage=0`. Las condiciones confirmadas son comisión 0,06 % + slippage 0,06 %. No usar `slippage` en ticks (es un importe fijo): modelarlo como comisión porcentual (`commission_value=0.12`) y documentarlo en la cabecera.
3. **Semántica de ejecución:** revisar que el Pine y `backtest()` coinciden en cantidad al cierre de la señal, trailing del stop (se actualiza al cierre, se aplica en la barra siguiente), gap al abrir, prioridad del stop si coincide con la toma parcial, calentamiento (`warmedUp`) y ventana.
4. **Referencias del usuario en TradingView (ETHUSD, no comparables al céntimo):** W10 1D +451,56 % · DD 24,94 % · PF 1,628 · 58/139 ganadoras; W10 4H (1 ene 2024 → 7 oct 2026) +43,05 % · DD 23,34 % · PF 1,262 · 27/83; W10 1H (1 ene → 7 oct 2026) −21,58 %.
**Entrega:** lista de discrepancias con su efecto estimado y, si procede, parche propuesto del Pine (sin cambiar la lógica de entrada/salida).

## Tarea 2 — búsqueda sistemática con walk-forward
1. **Pre-registro** antes de ejecutar: crear `estrategia short/w12/prereg_codex.txt` con espacio de búsqueda, criterios de aceptación y número máximo de pruebas. Registrar **cada prueba** en `trials.jsonl` (como en `estrategia long/v10/backtest_v10/.../trials10.jsonl`) y los accesos al tramo reservado en `oos_access_log.txt`.
2. **Espacio de búsqueda** (cambios estructurales, no solo parámetros): filtros de régimen alternativos (ADX, mitad del canal de Donchian, ancho de rango, pendiente combinada), entradas alternativas a la ruptura y al pullback, stops por estructura (último máximo local, ATR por tipo de entrada), salidas por tiempo o por pérdida de momentum, y diferencias por temporalidad. Mantener pocos parámetros y rangos razonables; escalar longitudes por temporalidad como en `FAC`.
3. **Validación:** walk-forward anclado (ventana creciente), reentrenando cada año 2021–2025 solo con años previos y evaluando en el año siguiente. Informar la curva walk-forward agregada.
4. **Control de comparaciones múltiples:** informar el número total de pruebas y calcular al menos una medida de sobreajuste (Sharpe deflactado o probabilidad de sobreajuste del backtest con CSCV).
5. **Criterios de aceptación** de una candidata frente a W11 (todos a la vez): (a) mejor CAGR/DD agregado en walk-forward; (b) no peor en al menos 4 de 5 años; (c) al menos el 70 % de sus vecinos inmediatos de parámetros también mejoran; (d) bajo costes ×2 (comisión 0,12 % + slippage 0,12 %) sigue por encima de W11; (e) coherente en las tres temporalidades o con justificación explícita por temporalidad; (f) DD no mayor que W11.
6. **Test final:** `HOLDOUT26` se mide **una sola vez**, como máximo para 2 finalistas más W11 y W10, y se anota en `oos_access_log.txt`. Si una finalista no supera a W11 en ese test, se informa y se detiene la búsqueda, sin reajustar. Tras ese uso, el tramo queda gastado y los datos posteriores a noviembre de 2026 pasan a ser el nuevo test.

## Entrega
- Rama nueva `codex-w12` (no tocar `main` ni la rama `organizar-tv-match`).
- Si alguna candidata pasa todos los criterios: `estrategia short/w12/W12_ETH_short.pine` (`//@version=6`, cabecera con costes y `margin_short` coherentes) y `W12_resultados.md` actualizado. Si no pasa ninguna: conservar W11, actualizar `W12_resultados.md` con lo probado y por qué se descarta.
- No borrar ni mover archivos existentes. Actualizar `estrategia short/README.md`.
- Informe breve con: qué se probó (nº de pruebas), qué pasó los criterios, resultado del test final y qué no está probado.

## Cómo ejecutar
```
cd "estrategia short/w12"
python3 backtest_w12.py ../../csvs                 # calibración (costes antiguos) + W10/W11 con costes definitivos
python3 diag12.py ../../csvs                       # diagnóstico de rachas
python3 exp12.py ../../csvs                        # rejilla de hipótesis de W12
python3 build_ext_data.py                          # regenera csvs/ext2026/ desde data_raw/
```
Necesita `numpy` y `pandas`. `backtest_w12.py` reproduce al céntimo las cifras de `W11_resultados.md` con `set_costs(0.0005, 0.0003, 'entry')` y datos hasta 2026-01-06: úsalo como prueba de que el motor no se ha roto.
