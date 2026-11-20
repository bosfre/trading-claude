import exp8, data8, eng, pandas as pd, numpy as np, pickle
SX=data8.load_all(True,pre=True,etc=False); exp8.set_refs(SX)
pd.set_option("display.width",250)
V=dict(name="V8-A",p=dict(xref=dict(type="btc",mode="filter",L_h=800)))
rows=[]
for a in ("ETH","DOGE","BTC"):
    for tf in exp8.TFS:
        s=SX[(a,tf)]; eqb,_,tb=exp8.run_variant(s,{}); eqv,_,tv=exp8.run_variant(s,V)
        for w in ("OOS2","OOS1","FULL"):
            b=s.stat(eqb,tb,w); x=s.stat(eqv,tv,w)
            rows.append(dict(a=a,tf=tf,w=w,b_ret=b["ret"],v_ret=x["ret"],b_cagr=b["cagr"],v_cagr=x["cagr"],b_mdd=b["mdd"],v_mdd=x["mdd"],b_cal=b["calmar"],v_cal=x["calmar"],b_n=b["trades"],v_n=x["trades"],yrs=b["yrs"]))
D=pd.DataFrame(rows); D["dcal"]=D.v_cal-D.b_cal; D["dmdd"]=D.v_mdd-D.b_mdd; D["dret"]=D.v_ret-D.b_ret
print(D[D.w=="OOS2"].round(3).to_string(index=False)); D.to_pickle("v8_oos2.pkl")
print(); print(D[(D.w=="FULL")].round(3).to_string(index=False))
