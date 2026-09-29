"""
run_final.py - Reproduce el resultado final de la estrategia V3.

Requiere los 9 CSV originales (BTCUSDT/ETHUSDT/DOGEUSDT x 15m/1h/4h) en /mnt/user-data/uploads/
(ETCUSDT_1h.csv y ETCUSDT_4h.csv opcionales, se usan solo como activo EXTRA de robustez).

Uso:
    python3 run_final.py            # backtest en TRAIN + VALIDATION (sin tocar el OOS)
    python3 run_final.py --oos      # + prueba final unica sobre el conjunto out-of-sample

Ver bt.py para el motor (numba), harness.py para la evaluacion multi-activo/timeframe
y strategies.py para las reglas. V3 es la estrategia aceptada; V1/V2/V4 se dejan en
strategies.py como registro de las iteraciones descartadas o superadas.
"""
import sys
import pandas as pd
import harness as H
import bt
from strategies import v2_donchian_long_time as V3_STRATEGY

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)

# --- Parametros finales de V3 (congelados; elegidos por ser el CENTRO de una zona estable
#     del mapa de calor N_h x k, no el punto optimo puntual) ---
PARAMS = dict(N_h=140, L_h=800, k=5.0, atr_h=56)

REGLAS = """
ESTRATEGIA V3 - Donchian breakout + filtro de regimen + trailing ATR (solo largos)
------------------------------------------------------------------------------------
Definiciones (en TIEMPO, no en barras -> mismo comportamiento en 15m/1h/4h):
  - N  = 140 horas  -> ventana del canal de Donchian
  - L  = 800 horas  -> EMA de regimen (filtro de tendencia)
  - ATR se calcula con una ventana de 56 horas (Wilder) y se reescala por sqrt(4h / TF)
    para que el stop en % del precio sea comparable entre timeframes.
  - k  = 5.0  -> multiplicador del ATR reescalado para el stop inicial y el trailing (chandelier)

ENTRADA (largo unicamente):
  - Señal calculada al CIERRE de la barra t-1, ejecutada a la APERTURA de la barra t (sin lookahead).
  - Entrar en largo si: close > max(high, N horas previas) [Donchian] Y close > EMA(L horas)
  - Una sola posicion abierta por serie; no se piramida.

SALIDA:
  - Stop inicial = precio de entrada - k * ATR_escalado (en el momento de la entrada)
  - Trailing stop tipo "chandelier": stop = max(stop anterior, maximo_desde_entrada - k*ATR_escalado),
    recalculado en cada cierre de barra, activo desde la barra siguiente a su calculo.
  - Salida por gap: si la apertura ya esta mas alla del stop, se ejecuta en la apertura (peor precio).
  - Salida intrabarra: si el low de la barra toca el stop, se ejecuta ahi (o en la apertura si esta
    es peor que el stop, reflejando gap).
  - Sin take-profit fijo: la ganancia se deja correr hasta que el trailing stop la recoja.

GESTION DE POSICION (sizing por riesgo):
  - riesgo por operacion = 2% del equity (risk_frac = 0.02)
  - tamaño = riesgo / distancia_al_stop(%), con tope de apalancamiento max_lev = 1.0x nocional/equity
  - En el backtest, el tope de 1x NUNCA se activo (tamaño medio real 0.17x-0.31x) -> el sizing esta
    gobernado puramente por el riesgo, no por el limite de apalancamiento.

UNIVERSO EVALUADO: BTC, ETH, DOGE en 15m/1h/4h (9 series principales) + ETC 1h/4h (2 series EXTRA
de robustez, no usadas para fijar parametros).
"""

COSTES = """
COSTES DE TRADING (por lado, aplicados en cada entrada y cada salida):
  - Comision: 6 pbs (0.06%) tipo taker
  - Slippage + medio-spread: 4 pbs (BTC), 6 pbs (ETH), 10 pbs (DOGE y ETC) - mayor para activos
    menos liquidos, supuesto conservador ya que los CSV no traen spread/order book.
  - Slippage adicional en salidas por STOP (gap o mecha): +100% del slippage base (asume peor
    ejecucion en movimientos rapidos/gaps).
  - Funding estimado en posiciones largas: 0.005% cada 8h (prorrateado por barra), 0 en corto
    (supuesto conservador, no se asume cobro de funding).
  - Se probo sensibilidad a 2x y 3x estos costes (ver informe): la estrategia sigue siendo
    rentable con Sharpe positivo incluso a 3x costes.
"""

def main(run_oos=False):
    print(REGLAS)
    print(COSTES)
    print(f"Parametros: {PARAMS}\n")

    for sp in ("TRAIN", "VAL"):
        res, aggs, _ = H.evaluate("V3-final", V3_STRATEGY, PARAMS, splits=(sp,), note="run_final.py")
        print(f"\n===== {sp} =====")
        print(H.fmt_table(res, sp).to_string())
        print(H.summary_line(res, aggs, sp))

    if run_oos:
        bt.unlock_oos("run_final.py --oos: reproduccion de la prueba final unica, parametros ya congelados")
        res, aggs, _ = H.evaluate("V3-final-OOS", V3_STRATEGY, PARAMS, splits=("OOS",), oos=True, note="run_final.py --oos")
        print("\n===== OUT-OF-SAMPLE (2024-01-01 en adelante) =====")
        print(H.fmt_table(res, "OOS").to_string())
        print(H.summary_line(res, aggs, "OOS"))

if __name__ == "__main__":
    main(run_oos=("--oos" in sys.argv))
