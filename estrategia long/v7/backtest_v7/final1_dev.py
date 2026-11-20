import pandas as pd, numpy as np, eng, exp, lab, v7cfg
pd.set_option("display.width",260); pd.set_option("display.max_columns",40)
S=eng.load_series()
def tab(v,asset="ETH",wins=("TRAIN","VAL","DEV")):
    rows=[]
    for tf in lab.TFS:
        s=S[(asset,tf)]; eq,ex,trd=exp.run_variant(s,v)
        for w in wins:
            m=s.stat(eq,trd,w); rows.append(dict(tf=tf,w=w,ret=m["ret"]*100,cagr=m["cagr"]*100,mdd=m["mdd"]*100,sharpe=m["sharpe"],pf=m["pf"],calmar=m["calmar"],n=m["trades"]))
    return pd.DataFrame(rows).set_index(["tf","w"])
for a in ("ETH","BTC","DOGE"):
    b=tab(v7cfg.V6,a); c=tab(v7cfg.V7,a)
    t=pd.concat({"V6":b,"V7":c},axis=1).round(2)
    print(f"\n######## {a} (solo TRAIN/VAL/DEV)"); print(t.to_string())
# DD igualado (DEV) para la configuración congelada
print("\n######## DD igualado en DEV: multiplicador de riesgo m que iguala el MDD de V6 y CAGR resultante")
rows=[]
for a in lab.ASSETS:
    for tf in lab.TFS:
        s=S[(a,tf)]; eq,ex,trd=exp.run_variant(s,v7cfg.V6); b=s.stat(eq,trd,"DEV")
        m,st=exp.matched_dd(S,v7cfg.V7,a,tf,b["mdd"])
        rows.append(dict(asset=a,tf=tf,mdd_v6=b["mdd"]*100,cagr_v6=b["cagr"]*100,m=m,cagr_v7_igual_dd=st["cagr"]*100,mejora_pp=(st["cagr"]-b["cagr"])*100))
print(pd.DataFrame(rows).round(2).to_string(index=False))
