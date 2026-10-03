import pandas as pd, numpy as np, datetime, eng, eng7, exp, lab
pd.set_option("display.width",270); pd.set_option("display.max_columns",60); pd.set_option("display.max_rows",300)
with open("oos_access_log.txt","a") as f:
    f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} OOS 2a mirada (solo VETO): V6 + piramidacion (+4 ATR, 25%, 1 anadido), unica candidata solo-largos que paso el cribado DEV. Regla fijada antes: adoptar solo si Calmar OOS y FULL >= V6 en los 3 TF de ETH\n")
S=eng.load_series()
V6={}; VP=dict(ext=dict(pyr_at=4,pyr_frac=.25,pyr_n=1))
def rng(s,eq,t0):
    i0=int(s.idx.searchsorted(pd.Timestamp(t0))); tot,mdd,*_=eng.stats_nb(eq,s.dend,i0,s.n,np.zeros((1,9)),0); return tot,mdd
rows=[]
for a in lab.ASSETS:
    for tf in lab.TFS:
        s=S[(a,tf)]
        for nm,v in (("V6",V6),("V6+pir",VP)):
            eq,ex,trd=exp.run_variant(s,v)
            for w in ("TRAIN","VAL","OOS","FULL"):
                m=s.stat(eq,trd,w); rows.append(dict(ver=nm,asset=a,tf=tf,w=w,ret=m["ret"]*100,cagr=m["cagr"]*100,mdd=m["mdd"]*100,sharpe=m["sharpe"],pf=m["pf"],calmar=m["calmar"],n=m["trades"]))
R=pd.DataFrame(rows); R.to_pickle("final3_R.pkl")
for a,ws in (("ETH",("TRAIN","VAL","OOS","FULL")),("BTC",("OOS","FULL")),("DOGE",("OOS","FULL"))):
    for w in ws:
        t=R[(R.asset==a)&(R.w==w)].round(2).set_index(["tf","ver"])[["ret","cagr","mdd","sharpe","pf","calmar","n"]].sort_index()
        print(f"\n#### {a} {w}"); print(t.to_string())
e=R[(R.asset=="ETH")]
ok=all(e[(e.w==w)&(e.tf==tf)&(e.ver=="V6+pir")].calmar.iloc[0] >= e[(e.w==w)&(e.tf==tf)&(e.ver=="V6")].calmar.iloc[0] for w in ("OOS","FULL") for tf in lab.TFS)
print("\nREGLA DE VETO (Calmar OOS y FULL >= V6 en 1H/4H/1D de ETH):","SUPERADA -> adoptar" if ok else "NO SUPERADA -> no adoptar; V7 mantiene señales de V6")
# costes x1/x2/x3 V6 (ETH, FULL/OOS) y ventanas tipo TradingView
print("\n#### Costes V6 ETH (CAGR % / MDD %)")
for tf in lab.TFS:
    s=S[("ETH",tf)]; out=[]
    for c in (1,2,3):
        eq,ex,trd=exp.run_variant(s,dict(cost=c)); f=s.stat(eq,trd,"FULL"); o=s.stat(eq,trd,"OOS"); out.append(f"x{c}: FULL {f['cagr']*100:.1f}%/{f['mdd']*100:.1f}%  OOS {o['cagr']*100:.1f}%/{o['mdd']*100:.1f}%")
    print(tf," | ".join(out))
print("\n#### Ventanas aprox. de tu prueba en TradingView, V6 en el backtest Python (NO comparables 1:1)")
for tf,t0 in (("1h","2025-01-10"),("4h","2024-01-10"),("1d","2015-08-01")):
    s=S[("ETH",tf)]; eq,ex,trd=exp.run_variant(s,V6); tot,mdd=rng(s,eq,max(pd.Timestamp(t0),s.idx[0]))
    print(f"ETH {tf} desde {max(pd.Timestamp(t0),s.idx[0]).date()}: retorno {tot*100:.1f}%  MDD {mdd*100:.1f}%")
print("\n#### Retorno por año V6 (ETH, %)")
Y={tf:exp.yearly(S[('ETH',tf)],exp.run_variant(S[('ETH',tf)],V6)[0])*100 for tf in lab.TFS}; print(pd.DataFrame(Y).round(1).to_string())
