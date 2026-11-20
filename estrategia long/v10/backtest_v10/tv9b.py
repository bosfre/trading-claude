import tv9, numpy as np, pandas as pd
from tv9 import *
for tf,df,Ns in (("4h",d4,range(4000,7001,250)),("1h",d1h,range(4000,8001,250))):
    print("==",tf)
    for N in Ns:
        i0=len(df)-N
        for fresh in (True,):
            m,_=go(df,tf,i0,fresh,True); print(f"N={N} desde {df.index[i0].date()} ret {m['ret']:.1f}% dd {m['mdd']:.1f} n {m['n']} win {m['win']:.0f} pf {m['pf']:.2f}")
