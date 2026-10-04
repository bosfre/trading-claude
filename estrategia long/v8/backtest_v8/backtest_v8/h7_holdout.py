import exp8, data8, eng, pandas as pd, numpy as np, json, time
SP=data8.load_all(False,pre=True,etc=True); exp8.set_refs(SP)
pd.set_option("display.width",250)
V=dict(name="V8-A BTC>EMA800h filtro",fam="H7_btcreg",p=dict(xref=dict(type="btc",mode="filter",L_h=800)))
rows=[]
for a in ("ETH","DOGE","ETC"):
    for tf in exp8.TFS:
        if (a,tf) not in SP: continue
        s=SP[(a,tf)]; eqb,_,tb=exp8.run_variant(s,{}); eqv,_,tv=exp8.run_variant(s,V)
        for w in ("PRE","OOS1","FULL"):
            if w=="PRE" and tf!="1d": continue
            b=s.stat(eqb,tb,w); x=s.stat(eqv,tv,w)
            if b is None or x is None: continue
            rows.append(dict(a=a,tf=tf,w=w,b_ret=b["ret"],v_ret=x["ret"],b_cagr=b["cagr"],v_cagr=x["cagr"],b_mdd=b["mdd"],v_mdd=x["mdd"],b_cal=b["calmar"],v_cal=x["calmar"],b_n=b["trades"],v_n=x["trades"]))
D=pd.DataFrame(rows); D["dcal"]=D.v_cal-D.b_cal; D["dmdd"]=D.v_mdd-D.b_mdd
print(D.round(3).to_string(index=False)); D.to_pickle("h7_holdout.pkl")
open("oos_access_log.txt","a").write(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())+" PRE (1D, ETH/DOGE) y OOS1 3a mirada (veto, reglas R1/R2 de v8_prereg.txt): V8-A BTC>EMA800h. OOS2 sigue sellado.\n")
