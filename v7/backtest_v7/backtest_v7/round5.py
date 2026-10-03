import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=eng.load_series(); base=exp.eval_variant(S,{})
Ns=(180,210,240,270,300,330,360); Ls=(1200,1400,1600,1800,2000,2400)
rows=[]
for n,l in itertools.product(Ns,Ls):
    v=dict(p=dict(short=1,sN_h=n,sL_h=l),ext=dict(fund_s=-1),sw=.5)
    r=exp.eval_variant(S,v); d=exp.delta_table(base,r)
    e=d[d.asset=="ETH"]; b=d[(d.asset=="BTC")&(d.w=="DEV")]; g=d[(d.asset=="DOGE")&(d.w=="DEV")]
    rows.append(dict(N=n,L=l,trn=e[e.w=="TRAIN"].d_cal.mean(),val=e[e.w=="VAL"].d_cal.mean(),
        c1h=e[(e.w=="DEV")&(e.tf=="1h")].d_cal.iloc[0],c4h=e[(e.w=="DEV")&(e.tf=="4h")].d_cal.iloc[0],c1d=e[(e.w=="DEV")&(e.tf=="1d")].d_cal.iloc[0],
        btc=b.d_cal.mean(),doge=g.d_cal.mean(),dmdd=e[e.w=="DEV"].d_mdd.mean()*100,dcagr=e[e.w=="DEV"].d_cagr.mean()*100))
T=pd.DataFrame(rows)
T["score"]=(T.trn+T.val)/2*0.5+(T.c1h+T.c4h+T.c1d)/3*0.5          # ETH
T["score2"]=T.score*0.75+T.btc*0.25                                 # + BTC como control cruzado
T.to_pickle("round5.pkl")
for col in ("score","c1h","c4h","c1d","btc"):
    print(f"\n{col} (filas N horas, columnas L horas)"); print(T.pivot(index="N",columns="L",values=col).round(2).to_string())
# suavizado 3x3 sobre la rejilla
P=T.pivot(index="N",columns="L",values="score2"); Q=P.copy()
for i,n in enumerate(P.index):
    for j,l in enumerate(P.columns):
        blk=P.iloc[max(0,i-1):i+2,max(0,j-1):j+2].values; Q.iloc[i,j]=np.nanmean(blk)
print("\nscore2 suavizado 3x3"); print(Q.round(2).to_string())
bi=np.unravel_index(np.nanargmax(Q.values),Q.shape); print("\nmáximo suavizado en N=",Q.index[bi[0]],"L=",Q.columns[bi[1]],"valor",round(Q.values[bi],3),"| celda cruda:",round(P.values[bi],3))
print("fracción de celdas con ETH TRAIN>0 y VAL>0:", ((T.trn>0)&(T.val>0)).mean().round(2), "| con 1h,4h,1d todos >0:",((T.c1h>0)&(T.c4h>0)&(T.c1d>0)).mean().round(2),"| mediana score",T.score.median().round(2))
