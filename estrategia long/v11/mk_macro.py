import pandas as pd, numpy as np, glob
T="/root/.claude/projects/-home-claude/570c478a-c7e6-5472-8270-1e8aa65cbf61/tool-results/"
F={"EURUSD":"9ttczs","GBPUSD":"mblmrq","USDJPY":"ynwamh","USDCAD":"5hryvt","USDSEK":"1bxo7h","USDCHF":"4nbllt"}
fx={}
for k,v in F.items():
    p=glob.glob(T+f"*{v}.txt")[0]
    d=pd.read_csv(p,parse_dates=["timestamp"]).set_index("timestamp").sort_index()
    assert not d.index.duplicated().any()
    fx[k]=d.close
fx=pd.DataFrame(fx)
fx=fx["2016-01-01":]
print("filas FX",len(fx),"NaN\n",fx.isna().sum().to_dict())
print(fx.loc["2017-01-03"].to_dict())
fx=fx.ffill()
w=dict(EURUSD=-0.576,USDJPY=0.136,GBPUSD=-0.119,USDCAD=0.091,USDSEK=0.042,USDCHF=0.036)
dxy=50.14348112*np.prod([fx[k]**w[k] for k in w],axis=0)
dxy=pd.Series(dxy,index=fx.index,name="dxy_syn")
m=pd.read_csv("/mnt/user-data/attachments/570c478a-c7e6-5472-8270-1e8aa65cbf61/55966dba-NASDAQ_UUP_daily_2017_latest.csv",parse_dates=["date"])
nq=m[m.symbol=="NASDAQ"].set_index("date").close.rename("nasdaq")
uup=m[m.symbol=="UUP"].set_index("date").close.rename("uup")
out=pd.concat([nq,uup,dxy],axis=1,sort=True)
out["dxy_syn"]=out["dxy_syn"].ffill(); print(out.isna().sum().to_dict())
print(out.tail(3))
# validacion: DXY sintetico vs UUP (retornos diarios, excluyendo dias de reparto: |ret UUP|>2.5% en dic)
r=out[["uup","dxy_syn"]].pct_change().dropna()
ex=(r.index.month==12)&(r.uup.abs()>0.012)
print("dias dic con |ret UUP|>1.2%:",[(str(i.date()),round(r.uup[i]*100,2),round(r.dxy_syn[i]*100,2)) for i in r.index[ex]])
rr=r[~ex]
print("corr retornos diarios (sin reparto):",rr.corr().iloc[0,1].round(3),"| con todo:",r.corr().iloc[0,1].round(3))
# nivel dxy conocido: 2017-01-03 ~102.2 (DXY real aprox 102.2) ; 2022-09-27 ~114.1
for dt in ["2017-01-03","2020-03-20","2022-09-27","2024-12-31"]:
    if pd.Timestamp(dt) in out.index: print(dt,"dxy_syn",round(out.dxy_syn[dt],2))
out.index.name="date"; out.to_csv("macro_daily.csv")
print(len(out))
