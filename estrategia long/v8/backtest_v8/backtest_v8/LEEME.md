# backtest_v8 (código de la investigación V8)
Requiere: python3, numpy, pandas, numba, scipy. Los CSV base (ETH 15m, BTC/DOGE 1h/4h, ETC) vienen del repo bosfre/trading-claude: ajusta las rutas R y U en data.py.
Los datos nuevos están en datos_nuevos/ (Twelve Data 1h 2026-01-06 -> 2026-10-03 para ETH/BTC/DOGE; FMP diario previo a 2017-08 para ETH 2015, BTC 2013, DOGE 2017-09). Ajusta W en data8.py.
- data8.py  carga de datos extendidos. load_all(ext=False) deja el OOS2 SELLADO (misma serie que V6/V7). ext=True lo abre.
- eng8.py   motor (con palancas apagadas es idéntico a eng7/V6 al bit; probado en 9 series).
- exp8.py   arnés (gen8, trial, matched_dd, filtro de régimen BTC en gen8 con p['xref']).
- engtv.py  emulador de la semántica de TradingView (V6.pine tal cual, V7.pine, V8.pine).
- round8a/8b/8c.py  experimentos; h7_*.py  validación del candidato; v8_oos2.py  OOS virgen; export_v8.py  tablas finales; tv_final.py / tv_scan.py  paridad TradingView.
- Registros: ../entrega8/trials8.jsonl, oos_access_log.txt, v8_prereg.txt (reglas fijadas antes de mirar PRE/OOS).
