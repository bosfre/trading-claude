import pandas as pd, numpy as np, eng, exp, lab
S=eng.load_series()
a=pd.read_pickle("final_R.pkl"); b=pd.read_pickle("final3_R.pkl")
a=a[a.ver.isin(["V6","V7"])].assign(ver=lambda d:d.ver.map({"V6":"V6","V7":"V7-cortos (RECHAZADA)"}))
for c in ("ret","cagr","mdd"): a[c]=a[c]*100
b=b[b.ver=="V6+pir"].assign(ver="V7-piramide (opcional, no adoptada)")
C=pd.concat([a[["ver","asset","tf","w","ret","cagr","mdd","sharpe","pf","calmar","trades"]].rename(columns={"trades":"n"}),b[["ver","asset","tf","w","ret","cagr","mdd","sharpe","pf","calmar","n"]]])
C=C.rename(columns={"w":"ventana","ret":"rent_%","cagr":"CAGR_%","mdd":"maxDD_%","n":"operaciones"}).round(3)
C.to_csv("/home/claude/work/entrega/comparativa_V6_vs_V7.csv",index=False)
for tf in lab.TFS:
    s=S[("ETH",tf)]; eq,ex,trd=exp.run_variant(s,{})
    t=pd.DataFrame(dict(entrada=s.idx[trd[:,0].astype(int)],precio_entrada=trd[:,3].round(2),salida=s.idx[trd[:,1].astype(int)],precio_salida=trd[:,4].round(2),
        ret_operacion_pct=(trd[:,5]*100).round(2),tamano_x_equity=trd[:,7].round(3),motivo=pd.Series(trd[:,8].astype(int)).map({0:"stop/trailing",1:"señal",2:"fin de datos",3:"TP"}).values))
    t.to_csv(f"/home/claude/work/entrega/trades_V6_ETH_{tf}.csv",index=False); print(tf,len(t),"operaciones exportadas")
print(C[(C.asset=="ETH")&(C.ventana.isin(["FULL","OOS"]))].sort_values(["tf","ventana","ver"]).to_string(index=False))
