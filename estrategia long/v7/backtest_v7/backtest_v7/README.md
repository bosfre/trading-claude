# V7 (ETH, solo largos) — informe de la optimización de V6

## 1. Conclusión

**No existe una mejora robusta de las señales de V6 con los datos disponibles.** V7 conserva las señales de V6 (Donchian 140 h, EMA 800 h, stop/trailing 5 ATR, TP 20 ATR, riesgo 5 %, apalancamiento máx. 2x) y aporta:

1. **Corrección de un fallo del Pine de V6** (hallado leyendo el código; no he podido verificarlo en TradingView): el bloque `if strategy.position_size == 0` borra `atrEntry` en la propia barra de señal (la orden aún no se ha ejecutado), así que por la semántica de Pine **el take profit no llega a activarse nunca**. Compruébalo buscando operaciones con comentario "TP" en tu lista de V6. En V7 se arregla (precio real de entrada + indicador de orden pendiente) y el stop inicial se calcula como en el backtest de Python.
2. La piramidación como **opción experimental apagada por defecto** (no superó la regla de veto).
3. El registro completo de lo probado y lo descartado (para no repetirlo).

Se probaron ~210 variantes con TRAIN/VAL (≤2023). **Ninguna cumplió los criterios de aceptación fijados de antemano.** Las dos candidatas que más se acercaron se confirmaron una vez en el OOS (2024-01 → 2026-01) y no pasaron:

- **Cortos selectivos** (solo en mercados bajistas profundos): mejoraban TRAIN/VAL (Calmar ETH 1H 2,43→3,29; 4H 2,36→2,96; 1D 1,68→2,16), pero **empeoran en OOS en los tres TF** y el total 2017-26 queda en empate o peor en Calmar. La ganancia venía de 2018 (+39 pp en 1H, +34 pp en 4H) y 2022; en 2024-25 restaron (2024: −8 pp en 1H, −10 pp en 4H). Además quedan fuera del alcance LONG del proyecto.
- **Piramidación pequeña** (+4 ATR, 25 % del tamaño, 1 añadido): Calmar OOS 1H 1,20→1,19, 4H 1,39→1,49, 1D 0,56→0,73, pero **+1 a +4 pp de drawdown** en los tres TF y, a igual drawdown, solo aportaba +0,6 / +1,5 / +2,9 pp de CAGR en DEV. No cumplió la regla de veto (Calmar OOS y total ≥ V6 en los 3 TF).

## 2. Comparativa directa (ETH, mismo riesgo 5 %, costes del repo)

**Total 2017-08 → 2026-01 (8,4 años)**

| TF | Versión | Rentabilidad | CAGR | Máx. DD | Operaciones |
|---|---|---|---|---|---|
| 1H | **V6 = V7 (señales)** | +824,8 % | 30,3 % | −22,5 % | 148 |
| 1H | cortos (rechazada) | +1.317,6 % | 37,1 % | −26,6 % | 229 |
| 1H | piramidación (opcional) | +1.236,4 % | 36,2 % | −26,3 % | 148 |
| 4H | **V6 = V7 (señales)** | +680,2 % | 27,7 % | −17,2 % | 135 |
| 4H | cortos (rechazada) | +1.001,2 % | 33,1 % | −22,6 % | 209 |
| 4H | piramidación (opcional) | +995,8 % | 33,0 % | −19,1 % | 135 |
| 1D | **V6 = V7 (señales)** | +385,0 % | 20,7 % | −18,8 % | 110 |
| 1D | cortos (rechazada) | +474,1 % | 23,1 % | −23,8 % | 168 |
| 1D | piramidación (opcional) | +537,6 % | 24,7 % | −20,7 % | 110 |

**OOS 2024-01 → 2026-01 (2,0 años, no usado para elegir nada)**

| TF | Versión | Rentabilidad | CAGR | Máx. DD | Operaciones |
|---|---|---|---|---|---|
| 1H | **V6 = V7 (señales)** | +60,6 % | 26,3 % | −21,9 % | 37 |
| 1H | cortos (rechazada) | +47,2 % | 21,0 % | −26,6 % | 62 |
| 1H | piramidación (opcional) | +67,9 % | 29,1 % | −24,5 % | 37 |
| 4H | **V6 = V7 (señales)** | +54,2 % | 23,8 % | −17,2 % | 35 |
| 4H | cortos (rechazada) | +36,1 % | 16,4 % | −22,6 % | 59 |
| 4H | piramidación (opcional) | +61,6 % | 26,7 % | −17,9 % | 35 |
| 1D | **V6 = V7 (señales)** | +22,7 % | 10,6 % | −18,8 % | 30 |
| 1D | cortos (rechazada) | +17,5 % | 8,3 % | −23,8 % | 46 |
| 1D | piramidación (opcional) | +33,0 % | 15,1 % | −20,7 % | 30 |

V6 se reprodujo **exactamente** (1H +824,8 %, 4H +680,2 %, 1D +385,0 %; mismos DD y nº de operaciones, diferencia ≤1e-15). Más ventanas (TRAIN, VAL, BTC, DOGE, Sharpe, PF) en `comparativa_V6_vs_V7.csv`.

## 3. Método

- **Ventanas**: TRAIN 2017-08 → 2021-12, VAL 2022-01 → 2023-12, OOS 2024-01 → 2026-01. Toda la exploración usó solo TRAIN/VAL; el OOS se abrió dos veces, ambas con configuraciones ya congeladas y solo para aceptar/vetar (ver `oos_access_log.txt`). Aun así, esas dos miradas hacen que el OOS ya no sea virgen para futuras versiones.
- **Motor** `eng7.py`: el de V6 más palancas opcionales; con ellas apagadas reproduce V6 bit a bit (probado en 9 series). Señal al cierre, entrada en la apertura siguiente, stop intrabarra con gaps, comisión 6 pb + slippage 6 pb por lado (+ extra en stops), funding 0,005 %/8 h (también pagado en cortos).
- **Criterios pre-registrados** (por variante, solo DEV): ΔCalmar ETH >0 en TRAIN y en VAL; >0 en ≥2 de 3 TF; BTC y DOGE no peor que −0,05; DD ETH no peor de 1 pp. Además, comparación **a igual drawdown** (reescalando el riesgo) para separar mejora de lógica de simple aumento de riesgo.
- **Evidencia previa del repo**: la búsqueda masiva anterior ("BUSCADA", optimizada ≤2023) tampoco generalizó (4H Calmar OOS 0,58 vs 1,45 de V3). Por eso no se repitió una búsqueda aleatoria masiva.

## 4. Qué se probó (todo en `trials_log.csv`)

| Familia | Resultado en DEV |
|---|---|
| Filtro/tamaño por régimen de volatilidad (10) | Mejora ETH en los 3 TF pero **empeora BTC** → efecto específico de ETH, descartado |
| Throttle de riesgo por drawdown (6) | Baja DD 1,5-3,4 pp pero baja más el CAGR → Calmar peor |
| Trinquete de trailing, apretar (6) y ensanchar (9) | Peor en ETH en todas las variantes: V6 necesita dejar correr las ganadoras |
| kI/kT (7), TP 0/15/30/40 (4), ATR 28-168 h (5) | Todos los vecinos de 5/5/20/56 h empeoran o no mejoran: V6 está en un óptimo local |
| Núcleo N×L (25 combinaciones) | Meseta alrededor de 140 h / 800 h, ningún vecino consistentemente mejor |
| Ruptura por cierre, stop de tiempo, salida por régimen, filtro largos por EMA 1200-2400 h (12) | Mixto o negativo |
| Conjuntos multi-velocidad (0,5x/1x/2x) | Peor que V6 en los 3 TF de ETH |
| Piramidación (26) | Calmar +, pero casi todo es más riesgo; a igual DD +0,6/+1,5/+2,9 pp |
| Cortos (simétricos, selectivos, rejilla fina 42+) | Mejoran 2018/2022, fallan en OOS |

Un solo indicador de entrada mostró señal consistente entre activos (baja volatilidad relativa → rupturas más rentables por unidad de riesgo), pero al probarlo como filtro en el sistema completo no generalizó a BTC.

## 5. Robustez de V6 (la versión que queda)

- **Costes** (CAGR / DD, ETH): ×1 → 1H 30,3 %/−22,5 %, 4H 27,7 %/−17,2 %, 1D 20,7 %/−18,8 %. ×2 → 25,7 %/−25,5 %, 23,5 %/−18,8 %, 17,6 %/−19,9 %. ×3 → 20,7 %/−30,4 %, 19,5 %/−22,2 %, 14,6 %/−21,0 %. En OOS con costes ×3 el 1D cae a +4,0 % anual: es la temporalidad más frágil.
- **Retorno por año** (1H / 4H / 1D, %): 2018 −2,6 / −2,9 / −7,5; 2019 50,9 / 47,5 / 5,9; 2020 109,8 / 89,5 / 71,8; 2021 43,6 / 47,2 / 39,4; 2022 −5,0 / 0,0 / 5,1; 2023 23,2 / 25,7 / 34,7; 2024 22,5 / 25,9 / 19,3; 2025 30,8 / 22,7 / 3,8. Sin años de pérdida grande, pero 2019-2021 aportan la mayor parte.
- **Pocas operaciones** (13-17 al año por TF): cualquier diferencia de pocos puntos entre variantes es indistinguible del ruido.
- Planifica un drawdown de 25-45 % con riesgo 5 % (remuestreo de operaciones de V6, ver repo).

## 6. Tus resultados de TradingView (referencia, no comparables 1:1)

- **1H**: Python V6 en la última ventana de ~1 año (2025-01-10 → 2026-01-10) da **+31,1 %** (DD −11,7 %); TradingView te dio ≈ −2 %. Hay una diferencia que no puedo explicar desde aquí. Que el TP no se activara en TradingView no la explica (en el backtest el TP aporta poco). Comprueba con `trades_V6_ETH_1h.csv` si las fechas/precios de entrada coinciden con la lista de operaciones de TradingView; puede influir el inicio de la serie (con ~1 año de historia, la EMA de 800 barras y el Donchian necesitan calentamiento) y que pocas operaciones hacen el resultado muy sensible.
- **4H** (~2 años): Python +54,2 % desde 2024-01-10 vs +91 % en TradingView. Misma magnitud, distinto periodo y tamaño.
- **1D**: tu +1.500 % en ~10-11 años incluye 2015-2017, que no está en nuestros CSV (nuestros datos empiezan en 2017-08, +385 % en 8,4 años). No comparable.
- `slippage = 2` en Pine son 2 ticks (0,02 USDT); el backtest usa 6 pb por lado (~1,8 USDT a 3.000). Para comparar, sube el slippage en TradingView.

## 7. Limitaciones

- ~210 variantes probadas con pocas operaciones: aunque se exigió consistencia, parte de lo "aceptable" en DEV puede ser ruido. Por eso el resultado final es no cambiar las señales.
- El Pine V7 **no está compilado ni probado en TradingView**.
- No se contrastó con ETC (activo del repo que nunca se usó en la selección): sería la siguiente prueba independiente razonable.
- No hay datos posteriores a 2026-01-10 ni anteriores a 2017-08.

## 8. Siguientes pasos razonables

1. Usar V6/V7 tal cual y no seguir afinando señales con estos datos.
2. Verificar la paridad con TradingView con las listas de operaciones adjuntas.
3. Cuando haya meses nuevos de datos, repetir `final2_oos.py` como OOS realmente virgen para cualquier idea futura.
4. Si quieres menos drawdown, la palanca limpia es el riesgo por operación (p. ej. 4 %), no la lógica.

---
## Cómo reproducir
`pip install numpy pandas numba`; edita `R` y `U` en `data.py` (rutas al repo y a los CSV nuevos). Orden: `repro_v6.py` (reproduce V6 al bit) → `test_eng7.py` (motor extendido = V6 con palancas apagadas) → `round1..7.py` (hipótesis, solo TRAIN/VAL) → `final1_dev.py` → `final2_oos.py` (OOS, cortos) → `final3_confirm.py` (OOS, piramidación + costes). `trials_log.csv` y `oos_access_log.txt` registran todas las pruebas y los accesos al OOS.
