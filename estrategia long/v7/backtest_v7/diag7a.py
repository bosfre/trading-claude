import numpy as np, pandas as pd, eng, gen, lab
pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
S=eng.load_series()
allt=[]
for (a,tf),s in S.items():
    m,eq,ex,trd=lab.run_v(s,lab.V6P)
    T=lab.trade_table(s,lab.V6P,trd); T["asset"]=a; T["tf"]=tf
    T=T[lab.dev_mask(s,T)]   # SOLO DEV
    allt.append(T)
A=pd.concat(allt,ignore_index=True)
print("operaciones DEV por activo/tf:"); print(A.groupby(["asset","tf"]).size().unstack())
print("\n== Motivo de salida (0=stop/trailing,1=señal,2=fin datos,3=TP) por tf (ETH+BTC+DOGE, DEV)")
print(A.groupby(["tf","reason"]).agg(n=("R","size"),meanR=("R","mean"),win=("ret",lambda x:(x>0).mean())).round(2).to_string())
print("\n== Perfil de operaciones DEV (ETH) por tf")
for tf in lab.TFS:
    x=A[(A.asset=="ETH")&(A.tf==tf)]
    w=x[x.ret>0]; l=x[x.ret<=0]
    print(tf, f"n={len(x)} win={len(w)/len(x):.0%} meanR={x.R.mean():.2f} ganadoras: R medio {w.R.mean():.2f}, MFE medio {w.mfe_atr.mean():.1f} ATR, barras {w.bars.mean():.0f} | perdedoras: R medio {l.R.mean():.2f}, MFE medio {l.mfe_atr.mean():.1f} ATR, MAE {l.mae_atr.mean():.1f} ATR, barras {l.bars.mean():.0f}")
print("\n== Captura de MFE: ret final / MFE (ganadoras, ETH DEV): ")
for tf in lab.TFS:
    x=A[(A.asset=="ETH")&(A.tf==tf)&(A.ret>0)]
    print(tf, "mediana MFE (ATR)",x.mfe_atr.median().round(1),"mediana ganancia en ATR aprox", (x.R*5).median().round(1))
# Perdedoras que llegaron a MFE >= X ATR antes de perder
print("\n== % de operaciones PERDEDORAS que antes llegaron a MFE >= X ATR (todas, DEV)")
L=A[A.ret<=0]
for X in (1,2,3,4,6):
    print(f"MFE>={X} ATR:", (L.mfe_atr>=X).mean().round(2), " (n perdedoras",len(L),")")
# Buckets de características (DEV, todas)
def buckets(col,qs=5):
    A["b"]=pd.qcut(A[col],qs,duplicates="drop")
    g=A.groupby("b",observed=True).agg(n=("R","size"),win=("ret",lambda x:(x>0).mean()),meanR=("R","mean"),medR=("R","median"))
    print(f"\n-- {col}"); print(g.round(2).to_string())
for col in ("ext","brk","volr","er","vrel","slope","atrpct"): buckets(col)
A.to_pickle("A_v6_trades_dev.pkl")
