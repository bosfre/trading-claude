# backtest_v9 (código de la investigación V9 = optimización de V8)
Requiere python3, numpy, pandas, numba. Los CSV base (ETH 15m, BTC/DOGE 1h/4h, ETC) vienen del repo bosfre/trading-claude: ajusta R y U en data.py y W en data8.py (los datos nuevos están en datos_nuevos/).
- exp9.py    arnés V9: baseline V8 (V7 + BTC>EMA800h), palancas nuevas en gen9 (salida por tendencia, salida por BTC, filtro de extensión, calidad de vela, tamaño por extensión), métricas ampliadas (PF, win rate, R, payoff) y criterio pre-registrado accept9.
- d9_diag.py diagnóstico MFE/MAE y episodios de DD (solo TRAIN+VAL).   round9a.py  15 hipótesis (solo TRAIN/VAL).   gates9.py  holdouts H1-H6.
- compare9.py / compare9b.py / compare9c(_b).py  comparativa normalizada 1H/4H/1D, igual DD, mezcla, bootstrap, costes.   tv9.py / tv9b.py  emulación de V8.pine con la semántica de TradingView.
- mk_exp9.py / mk_report9.py  generan experimentos_V9.csv e informe_V9.md.   Registros: ../trials9.jsonl, ../oos_access_log.txt, ../v9_prereg.txt.
