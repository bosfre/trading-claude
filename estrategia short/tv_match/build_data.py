"""
build_data.py - Construye los CSV que usa run_final.py a partir de data/raw/.
  1D  : serie hibrida = ETH/USD Alpha Vantage (2015-08-08 .. 2017-08-16) + Binance ETHUSDT (2017-08-17 .. 2026-01-06)
        + ETH/USD Alpha Vantage (2026-01-07 .. ultimo dia cerrado). TradingView muestra todo el historial en 1D.
  4H/1H: Twelve Data ETH/USD, ultimas ~2.500 velas cerradas (limite de TradingView gratuito en 4H y 1H).
Uso: python3 build_data.py
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = f'{HERE}/data/raw', f'{HERE}/data'
COLS = ['open', 'high', 'low', 'close', 'volume']

av = pd.read_csv(f'{RAW}/AlphaVantage_ETHUSD_1d_raw.csv', parse_dates=['timestamp']).set_index('timestamp').sort_index()[COLS].astype(float)
av = av.iloc[:-1]  # el ultimo dia aun esta en formacion
bn = pd.read_csv(f'{RAW}/Binance_ETHUSDT_1d.csv', parse_dates=['timestamp']).set_index('timestamp')
hy = pd.concat([av[av.index < '2017-08-17'], bn, av[av.index > bn.index[-1]]])
hy.to_csv(f'{OUT}/ETHUSD_1d_hybrid_2015_2026.csv')
print('1d', hy.index[0].date(), hy.index[-1].date(), len(hy))

for tf, step in (('4h', '4h'), ('1h', '1h')):
    df = pd.read_csv(f'{RAW}/TwelveData_ETHUSD_{tf}_raw.csv', sep=';', parse_dates=['datetime']).rename(columns={'datetime': 'timestamp'})
    df = df.set_index('timestamp').sort_index().astype(float)
    df = df[~df.index.duplicated()].iloc[:-1]  # ultima vela en formacion
    gaps = int((df.index.to_series().diff().dropna() != pd.Timedelta(step)).sum())
    df['volume'] = 0.0
    df.to_csv(f'{OUT}/ETHUSD_{tf}_TD_ult2500.csv')
    print(tf, df.index[0], df.index[-1], len(df), 'huecos', gaps)
