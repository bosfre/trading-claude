import numpy as np, pandas as pd
import bt

def v1_donchian_long(df, p):
    """V1 (baseline predefinido, NO optimizado): ruptura Donchian(N) + filtro de regimen EMA(L) + salida por trailing ATR (chandelier). Solo largos."""
    atr = bt.atr_wilder(df, p.get("atr_n", 14))
    hi = df.high.rolling(p["N"]).max().shift(1)
    regime = df.close > bt.ema(df.close, p["L"]) if p.get("L") else pd.Series(True, index=df.index)
    le = ((df.close > hi) & regime).values
    return dict(atr=atr.values, long_entry=le, warmup=max(p["N"], p.get("L") or 0, 30) + 5)

# ------------------------------------------------------------------ V2: parametros en TIEMPO REAL (invariantes al timeframe)
def hbars(hours, tf):
    return max(2, int(round(hours / bt.TF_HOURS[tf])))

def atr_scaled(df, tf, atr_hours=56.0, ref_hours=4.0):
    """ATR con ventana temporal fija, reescalado por sqrt(tiempo) a la escala de referencia (4h): stop del mismo tamano en % en todos los TF."""
    a = bt.atr_wilder(df, hbars(atr_hours, tf))
    return a * np.sqrt(ref_hours / bt.TF_HOURS[tf])

def v2_donchian_long_time(df, p):
    """V2: igual que V1 pero N, L y ATR definidos en horas (N=220h, L=800h, ATR=56h == 55/200/14 barras de 4h) y stop reescalado."""
    tf = p["tf"]
    atr = atr_scaled(df, tf, p.get("atr_h", 56.0))
    N = hbars(p["N_h"], tf); L = hbars(p["L_h"], tf)
    hi = df.high.rolling(N).max().shift(1)
    regime = df.close > bt.ema(df.close, L)
    le = ((df.close > hi) & regime).values
    return dict(atr=atr.values, long_entry=le, warmup=max(N, L) + 5)

def v4_donchian_longshort_time(df, p):
    """V4: V3 (largo) + regla simetrica de corto (mismos parametros, sin ajuste adicional): ruptura a la baja + precio bajo EMA(L)."""
    tf = p["tf"]
    atr = atr_scaled(df, tf, p.get("atr_h", 56.0))
    N = hbars(p["N_h"], tf); L = hbars(p["L_h"], tf)
    hi = df.high.rolling(N).max().shift(1)
    lo = df.low.rolling(N).min().shift(1)
    emaL = bt.ema(df.close, L)
    le = ((df.close > hi) & (df.close > emaL)).values
    se = ((df.close < lo) & (df.close < emaL)).values
    return dict(atr=atr.values, long_entry=le, short_entry=se, warmup=max(N, L) + 5)
