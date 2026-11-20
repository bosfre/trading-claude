"""
diag12.py - Diagnostico: ¿una perdida tiende a seguirse de otra? ¿Cuanto duran los stops? Desarrollo (<=2026-01-06) frente a 2026.
Costes TradingView (0,06 %, slip 0, cantidad al cierre). Uso: python diag12.py [carpeta csvs]
"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_w12 as B

d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'csvs')
B.set_costs(0.0006, 0.0, 'close')
D = B.load(d, ext=True); TS = {tf: B.TF(D[tf], tf) for tf in D}
cut = {tf: TS[tf].idx.searchsorted(pd.Timestamp('2026-01-07')) for tf in TS}
rows = []
for name, cfgs, rks in B.BASE:
    for tf in ('1d', '4h', '1h'):
        T = TS[tf]; _, _, tr = B.run_cfg(T, cfgs[tf], rks[tf], ['TOTAL'], 'ALL')
        tr = tr.copy(); tr['win'] = tr.pnl > 0
        tr['prev_win'] = tr.win.shift(1); tr['gap'] = tr.ei - tr.xi.shift(1)          # barras entre la salida previa y esta entrada
        tr['quick'] = tr.bars <= max(2, B.RD(2 * T.f * 6 / 6))                          # parada rapida: <=2 barras (>=2)
        fa = B.RD(24 * T.f)                                                              # ~4 dias en barras de esta TF (24 barras de 4H)
        for per, m in (('dev<=2026-01', tr.xi < cut[tf]), ('2026', tr.xi >= cut[tf])):
            t = tr[m]; l = t[~t.win]
            after_loss = t[t.prev_win == False]; after_win = t[t.prev_win == True]
            near = t[(t.prev_win == False) & (t.gap <= fa)]
            rows.append(dict(ver=name, tf=tf, per=per, n=len(t), wr=100 * t.win.mean(),
                             wr_tras_perdida=100 * after_loss.win.mean() if len(after_loss) else np.nan, n_tras_perdida=len(after_loss),
                             wr_tras_ganancia=100 * after_win.win.mean() if len(after_win) else np.nan,
                             wr_tras_perdida_cercana=100 * near.win.mean() if len(near) else np.nan, n_cercana=len(near),
                             perdidas_rapidas_pct=100 * (l.bars <= 2).mean() if len(l) else np.nan,
                             perdida_media=100 * l.ret.mean() if len(l) else np.nan, ganancia_media=100 * t[t.win].ret.mean() if t.win.any() else np.nan))
pd.set_option('display.width', 250)
print(pd.DataFrame(rows).round(1).to_string(index=False))
