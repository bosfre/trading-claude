"""Configuraciones congeladas. V7 = V6 (largos idénticos) + cortos selectivos de régimen bajista profundo.
Parámetros congelados con datos <= 2023 (TRAIN+VAL). Ver informe."""
import lab
V6 = {}                                                       # base: lab.V6P (V3 + TP 20 ATR, riesgo 5 %, apal. máx. 2x)
SHORT_N_H, SHORT_L_H, SHORT_W = 270, 1800, 0.5
V7 = dict(p=dict(short=1, sN_h=SHORT_N_H, sL_h=SHORT_L_H), ext=dict(fund_s=-1), sw=SHORT_W)
V7_LONG = {}                                                  # V7 con cortos apagados == V6
