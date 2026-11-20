"""
exp12.py - Rejilla de hipotesis W12 sobre W10/W11. SELECCION SOLO CON DESARROLLO: TRAIN / VALIDATION / OOS (<= 2026-01-10).
El tramo HOLDOUT26 (2026-01-07 ->) NO se mide aqui: se mide una sola vez al final, solo para los finalistas, con backtest_w12.py (segmento HOLDOUT26).
Costes TradingView (--fee 0,06 % y --slip 0,06 % por defecto, cantidad al cierre). Unidades de longitud: barras de 4H (se escalan por temporalidad).
Hipotesis:  cool  = enfriamiento tras perdida (control: el diagnostico no ve rachas)
            er    = filtro de lateralidad: no entrar si el ratio de eficiencia de Kaufman < umbral
            slope = filtro de pendiente: solo entrar si la EMA de regimen cae al menos X en n barras
Uso: python exp12.py [carpeta csvs] [--fee ..] [--slip ..]  -> resultados/exp_dev_<slipX>.csv y resumen en pantalla
"""
import os, sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest_w12 as B

HERE = os.path.dirname(os.path.abspath(__file__))
d = B.cli_dir(os.path.join(HERE, '..', '..', 'csvs'))
FEE, SLIP = B.cli_costs(); LABEL = f'slip{SLIP * 100:g}'; B.set_costs(FEE, SLIP, 'close')
D = B.load(d, ext=True); TS = {tf: B.TF(D[tf], tf) for tf in D}
DEV = ['TRAIN', 'VALIDATION', 'OOS', 'TOTAL']

GRID = [('base', {})]
GRID += [('cool', dict(cool=c, cool_k=k)) for c in (6, 12, 24, 48) for k in (1, 2)]
GRID += [('er', dict(er=(n, t))) for n in (45, 90) for t in (0.10, 0.15, 0.20, 0.30)]
GRID += [('slope', dict(slope=(n, t))) for n in (90, 180) for t in (0.0, 0.02, 0.05, 0.10)]


def with_h(cfg, tf, h):
    h = dict(h)
    if 'cool' in h: h['cool'] = B.RD(h['cool'] * B.FAC[tf])
    return dict(cfg, **h)


rows = []
for bname, cfgs, rks in B.BASE:
    for tf in ('1d', '4h', '1h'):
        for hname, h in GRID:
            cfg = with_h(cfgs[tf], tf, h)
            out, eq, tr = B.run_cfg(TS[tf], cfg, rks[tf], DEV, 'ALL')
            r = dict(base=bname, tf=tf, hyp=hname, par=str({k: v for k, v in h.items()}) if h else '-')
            for seg in DEV:
                o = out[seg]; r[f'calmar_{seg}'] = o['cagr'] / abs(o['dd']) if o['dd'] < 0 else np.nan
                r[f'ret_{seg}'] = o['ret']; r[f'dd_{seg}'] = o['dd']; r[f'pf_{seg}'] = o['pf']; r[f'n_{seg}'] = o['n']
            rows.append(r)
R = pd.DataFrame(rows)
# mejora frente a la base de la misma (base, tf) en cada tramo de desarrollo
for seg in ('TRAIN', 'VALIDATION', 'OOS'):
    b = R[R.hyp == 'base'].set_index(['base', 'tf'])[f'calmar_{seg}']
    R[f'mejora_{seg}'] = [R.loc[i, f'calmar_{seg}'] > b[(R.loc[i, 'base'], R.loc[i, 'tf'])] + 1e-9 for i in R.index]
R['mejora_n'] = R[['mejora_TRAIN', 'mejora_VALIDATION', 'mejora_OOS']].sum(axis=1)
os.makedirs(f'{HERE}/resultados', exist_ok=True); R.to_csv(f'{HERE}/resultados/exp_dev_{LABEL}.csv', index=False)

pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
cols = ['base', 'tf', 'hyp', 'par', 'ret_TOTAL', 'dd_TOTAL', 'pf_TOTAL', 'n_TOTAL', 'calmar_TRAIN', 'calmar_VALIDATION', 'calmar_OOS', 'mejora_n']
print('BASES (desarrollo):'); print(R[R.hyp == 'base'][cols].round(2).to_string(index=False))
print('\nCandidatos que mejoran CALMAR (CAGR/DD) en los TRES tramos de desarrollo:')
print(R[(R.hyp != 'base') & (R.mejora_n == 3)][cols].round(2).to_string(index=False))
print('\nRecuento por hipotesis (combinaciones que mejoran 3/3 | 2/3 | total):')
print(R[R.hyp != 'base'].groupby(['hyp', 'tf']).mejora_n.agg(lambda s: f'{(s == 3).sum()} | {(s == 2).sum()} | {len(s)}').unstack().to_string())
