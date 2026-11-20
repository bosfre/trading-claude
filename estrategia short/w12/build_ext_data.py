"""
build_ext_data.py - Extiende los CSV de Binance (que acaban el 2026-01-06) hasta noviembre de 2026.
  1H/4H: Twelve Data ETH/USD (data_raw/). 1D: Alpha Vantage ETH/USD (../tv_match/data/raw/).
  Escribe csvs/ext2026/ETHUSD_<tf>_ext2026.csv con las velas desde el ultimo dato de Binance (inclusive: esa vela estaba incompleta).
  Se descarta la ultima vela (en formacion). Comprueba huecos y coincidencia con Binance en el solape.
Uso: python3 build_ext_data.py
"""
import os, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
CS = f'{REPO}/csvs'; OUT = f'{CS}/ext2026'; os.makedirs(OUT, exist_ok=True)
STEP = {'1h': pd.Timedelta('1h'), '4h': pd.Timedelta('4h'), '1d': pd.Timedelta('1D')}
rd = lambda p, **k: pd.read_csv(p, parse_dates=['timestamp'], **k).set_index('timestamp')

def td(files):
    parts = [pd.read_csv(f'{HERE}/data_raw/{f}', sep=';', parse_dates=['datetime']).rename(columns={'datetime': 'timestamp'}) for f in files]
    df = pd.concat(parts).set_index('timestamp').sort_index().astype(float)
    return df[~df.index.duplicated()]

SRC = {'1h': td(['TwelveData_ETHUSD_1h_2026-01-06_2026-06-20.csv', 'TwelveData_ETHUSD_1h_2026-06-19_2026-11-21.csv']),
       '4h': td(['TwelveData_ETHUSD_4h_2026-01-06_2026-11-21.csv'])}
av = rd(f'{REPO}/estrategia short/tv_match/data/raw/AlphaVantage_ETHUSD_1d_raw.csv').sort_index()[['open', 'high', 'low', 'close', 'volume']].astype(float)
SRC['1d'] = av
for tf in ('1h', '4h', '1d'):
    bn = rd(f'{CS}/ETHUSDT_{tf}.csv'); last = bn.index[-1]
    s = SRC[tf].iloc[:-1]                                   # ultima vela en formacion
    j = bn.join(s, how='inner', lsuffix='_bn', rsuffix='_new')
    if len(j):
        d = (j.close_new / j.close_bn - 1).abs() * 100
        print(f'{tf}: solape con Binance {len(j)} velas, dif cierre max {d.max():.3f} %')
    e = s[s.index >= last].copy(); e['volume'] = e.get('volume', 0.0)   # >= : la ultima vela de Binance estaba incompleta, la sustituye la completa
    if tf != '1d': e['volume'] = 0.0
    gaps = int((e.index.to_series().diff().dropna() != STEP[tf]).sum())
    e.to_csv(f'{OUT}/ETHUSD_{tf}_ext2026.csv')
    print(f'{tf}: Binance hasta {last} | extension {e.index[0]} -> {e.index[-1]} ({len(e)} velas) | huecos {gaps}')
