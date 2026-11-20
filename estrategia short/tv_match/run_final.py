"""
run_final.py - W8 y W9 (SHORT ETH) en 1D / 4H / 1H con las condiciones de TradingView del usuario.
Uso: python3 run_final.py [--fee 0.0006] [--slip 0.0006]
  --fee : comision por lado como fraccion del nominal (0.0006 = 0,06 %, valor actual del usuario)
  --slip: slippage por lado como fraccion del precio (0.0006 = 0,06 %, valor confirmado por el usuario); --slip 0 lo desactiva.
Escribe resultados/resumen_final.csv y resultados/trades_<ver>_<tf>.csv
"""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from backtest_tv import W8, W9, FAC, prep, backtest, rd


def arg(name, default):
    return float(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


fee, slip = arg('--fee', 0.0006), arg('--slip', 0.0006)
rd_csv = lambda f: pd.read_csv(f'{HERE}/data/{f}', parse_dates=['timestamp']).set_index('timestamp')
D = {'1d': rd_csv('ETHUSD_1d_hybrid_2015_2026.csv'), '4h': rd_csv('ETHUSD_4h_TD_ult2500.csv'), '1h': rd_csv('ETHUSD_1h_TD_ult2500.csv')}
os.makedirs(f'{HERE}/resultados', exist_ok=True)
rows = []
for ver, VC in (('W8', W8), ('W9', W9)):
    for tf in ('1d', '4h', '1h'):
        df = D[tf]; P = prep(df, tf, VC[tf]); eq, T = backtest(P, fee, slip, 'close')
        emaLen = rd(600 * FAC[tf]); w = T.pnl > 0; gl = -T.pnl[~w].sum()
        rows.append(dict(ver=ver, tf=tf, desde=df.index[0].date(), hasta=df.index[-1].date(), velas=len(df),
                         operable_desde=df.index[min(emaLen, len(df) - 1)].date(),
                         ret=100 * (eq[-1] - 1), dd=100 * (eq / np.maximum.accumulate(eq) - 1).min(),
                         pf=(T.pnl[w].sum() / gl if gl > 0 else np.nan), wr=(100 * w.mean() if len(T) else np.nan), ops=len(T)))
        if len(T):
            t = T.copy(); t['entrada_ts'] = df.index[t.ei.values]; t['salida_ts'] = df.index[t.xi.values]
            t.to_csv(f'{HERE}/resultados/trades_{ver}_{tf}.csv', index=False)
R = pd.DataFrame(rows).round(2)
print(f'fee {fee*100:.3f} %/lado  slip {slip*100:.3f} %/lado'); print(R.to_string(index=False))
R.to_csv(f'{HERE}/resultados/resumen_final.csv', index=False)
