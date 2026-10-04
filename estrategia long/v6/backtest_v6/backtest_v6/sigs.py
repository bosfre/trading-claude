import numpy as np
import eng
def hb(hours,tf,mn=2): return max(mn,int(round(hours/eng.TFH[tf])))
def v3(S,N_h=140,L_h=800,atr_h=56,short=False):
    # clamps idénticos al Pine de V3/V4 (N>=5, L>=20, ATR>=10 barras)
    N=hb(N_h,S.tf,5); L=hb(L_h,S.tf,20); A=hb(atr_h,S.tf,10)
    atr=S.ind("atr",A)*np.sqrt(4.0/eng.TFH[S.tf]); em=S.ind("ema",L)
    d=dict(atr=atr,le=(S.c>S.ind("hh",N))&(S.c>em),warm=max(N,L)+5)
    if short: d["se"]=(S.c<S.ind("ll",N))&(S.c<em)
    return d
def v4(S): return v3(S,atr_h=200)               # V4 del repo = V3 con ventana ATR de 200h
def v5(S,ema_b=200,look_b=75,atr_b=14):         # V5 = W1 (ETH solo cortos): 'estrategia v5(v3 optimizada).pine'
    f=14400.0/(eng.TFH[S.tf]*3600.0)
    E=max(2,int(ema_b*f)); Lk=max(2,int(look_b*f)); A=max(2,int(atr_b*f))
    return dict(atr=S.ind("atr",A)*np.sqrt(f),se=(S.c<S.ind("ema",E))&(S.c<S.ind("ll",Lk)),warm=max(E,Lk,A)+5)
