"""¿Qué fecha de fin de ventana reproduce tus números de TradingView? (V6.pine / V7.pine, últimas 5000 velas, costes TV)"""
import numpy as np, pandas as pd, data8, engtv
from engtv import pine_signals, run_tv, tv_stats
SX=data8.load_all(True,pre=True,etc=False); TFH={"1h":1.0,"4h":4.0,"1d":24.0}
USER={"1h":(-0.027,-0.09),"4h":(0.91,0.67),"1d":(15.0,18.69)}
ends=pd.date_range("2026-01-10","2026-09-30",freq="7D")
rows=[]
for tf in ("1h","4h","1d"):
    df=SX[("ETH",tf)].df
    for e in ends:
        j=int(df.index.searchsorted(e,side="right"))
        if j<300: continue
        sub=df.iloc[max(0,j-5000):j]
        for mm,mmn in ((0,"2x"),(1,"1x-clip")):
            r={}
            for mode in ("v6pine","v7pine"):
                eq,t=run_tv(sub,TFH[tf],mode,comm=0.0006,slip_abs=0.02,margin_mode=mm); r[mode]=tv_stats(sub,eq,t)["ret"]
            rows.append(dict(tf=tf,fin=e.date(),margen=mmn,desde=str(sub.index[0].date()),v6=r["v6pine"],v7=r["v7pine"],u6=USER[tf][0],u7=USER[tf][1]))
R=pd.DataFrame(rows); R.to_pickle("tv_scan.pkl")
R["err"]=(np.log1p(R.v6.clip(lower=-0.99))-np.log1p(R.u6)).abs()+(np.log1p(R.v7.clip(lower=-0.99))-np.log1p(R.u7)).abs()
pd.set_option("display.width",200)
for tf in ("1h","4h","1d"):
    x=R[(R.tf==tf)]
    print("== ",tf,"(tu TV: V6 %.1f%% / V7 %.1f%%) =="%(USER[tf][0]*100,USER[tf][1]*100)); print(x.sort_values("err").head(5)[["fin","margen","desde","v6","v7","err"]].round(3).to_string(index=False))
# error conjunto por fecha y margen
G=R.groupby(["fin","margen"]).err.sum().reset_index().sort_values("err"); print("== mejor fecha de fin conjunta (suma de errores 3 TF) =="); print(G.head(6).round(2).to_string(index=False))
