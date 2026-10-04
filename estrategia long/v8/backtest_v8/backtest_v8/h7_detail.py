import exp8, data8, eng, pandas as pd, numpy as np, json
S=data8.load_all(False,pre=False,etc=True); exp8.set_refs(S)
pd.set_option("display.width",250); pd.set_option("display.max_rows",200)
V=dict(name="V8-A BTC>EMA800h filtro",fam="H7_btcreg",p=dict(xref=dict(type="btc",mode="filter",L_h=800)))
rows=[]
for a in ("ETH","DOGE","ETC"):
    for tf in exp8.TFS:
        s=S[(a,tf)]
        eqb,_,tb=exp8.run_variant(s,{}); eqv,_,tv=exp8.run_variant(s,V)
        for w in ("TRAIN","VAL","DEV"):
            b=s.stat(eqb,tb,w); x=s.stat(eqv,tv,w)
            rows.append(dict(a=a,tf=tf,w=w,b_ret=b["ret"],v_ret=x["ret"],b_cagr=b["cagr"],v_cagr=x["cagr"],b_mdd=b["mdd"],v_mdd=x["mdd"],b_cal=b["calmar"],v_cal=x["calmar"],b_n=b["trades"],v_n=x["trades"]))
D=pd.DataFrame(rows); D["dcal"]=D.v_cal-D.b_cal
print(D.round(3).to_string(index=False))
