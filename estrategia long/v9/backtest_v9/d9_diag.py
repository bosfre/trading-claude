import exp9, numpy as np, pandas as pd, eng
pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
S=exp9.load(True)
# 1) regresión: V8 reproduce el informe V8 (FULL0 = 2017-08 -> 2026-01-10)
for tf in exp9.TFS:
    s=S[("ETH",tf)]; eq,ex,trd=exp9.run9(s,exp9.V8); m=exp9.wstat(s,eq,ex,trd,None,None,"FULL0") if False else exp9.wstat(s,eq,ex,trd,"2017-01-01","2026-01-11")
    print(tf,"V8 FULL0 ret %.1f%% cagr %.1f%% mdd %.1f%% n %d"%(m["ret"]*100,m["cagr"]*100,m["mdd"]*100,m["n"]))
# 2) diagnóstico DEV (TRAIN+VAL): MFE/MAE por operación, motivo de salida
rows=[]
for tf in exp9.TFS:
    s=S[("ETH",tf)]; eq,ex,trd=exp9.run9(s,exp9.V8); d,q=exp9.gen9(s,exp9.V8); atr=d["atr"]
    for t in trd:
        ei,xi=int(t[0]),int(t[1])
        if xi>=s.i_va: continue
        a0=atr[ei-1]; ef=t[3]
        hh=s.h[ei:xi+1]; ll=s.l[ei:xi+1]; pk=int(np.argmax(hh))
        rows.append(dict(tf=tf,ret=t[5],R=t[6],reason=int(t[8]),bars=xi-ei,mfe=(hh.max()-ef)/a0,mae=(ef-ll.min())/a0,mae_pre=(ef-ll[:pk+1].min())/a0,exit_atr=(t[4]-ef)/a0,
                         giveback=(hh.max()-t[4])/a0, yr=s.idx[ei].year))
T=pd.DataFrame(rows); T["win"]=T.ret>0
T.to_pickle("d9_trades_dev.pkl")
for tf in exp9.TFS:
    x=T[T.tf==tf]; w=x[x.win]; l=x[~x.win]
    print(f"\n== {tf} DEV n={len(x)} win={x.win.mean():.2f} avgR={x.R.mean():.2f} avgR_win={w.R.mean():.2f} avgR_loss={l.R.mean():.2f} payoff={w.ret.mean()/abs(l.ret.mean()):.2f}")
    print(" motivos salida:",x.reason.value_counts().to_dict())
    print(" ganadoras: MAE_pre-pico pctl 50/75/90 =",np.round(w.mae_pre.quantile([.5,.75,.9]).values,2)," MFE med %.1f"%w.mfe.median()," giveback med %.1f ATR"%w.giveback.median())
    print(" perdedoras: MFE pctl 50/75/90 =",np.round(l.mfe.quantile([.5,.75,.9]).values,2)," R med %.2f, frac con MFE>=2ATR %.2f, >=4ATR %.2f"%(l.R.median(),(l.mfe>=2).mean(),(l.mfe>=4).mean()))
    print(" perdedoras bars med %.0f ; ganadoras bars med %.0f ; todas con bars<=3 pierden: %.2f"%(l.bars.median(),w.bars.median(), 1-x[x.bars<=3].win.mean() if (x.bars<=3).any() else np.nan))
    # aporte de las 10% mejores operaciones al beneficio
    r=x.ret.sort_values(ascending=False).values; k=max(1,len(r)//10); print(" top10%% de operaciones aportan %.0f%% del beneficio bruto; sin ellas PF=%.2f"%(100*r[:k][r[:k]>0].sum()/r[r>0].sum(), r[k:][r[k:]>0].sum()/-r[k:][r[k:]<=0].sum()))
# 3) episodios de drawdown ETH (DEV) por TF
for tf in exp9.TFS:
    s=S[("ETH",tf)]; eq,ex,trd=exp9.run9(s,exp9.V8)
    e=pd.Series(eq[:s.i_va],index=s.idx[:s.i_va]).ffill(); pk=e.cummax(); dd=e/pk-1
    # tres peores episodios
    out=[]; x=dd.copy()
    for _ in range(3):
        t1=x.idxmin(); t0=e[:t1].idxmax(); out.append((t0.date(),t1.date(),round(x.min()*100,1))); x[t0:t1+pd.Timedelta(days=40)]=0
    print(tf,"peores DD DEV:",out)
