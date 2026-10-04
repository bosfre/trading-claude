import pandas as pd, numpy as np, itertools, eng, exp, lab
pd.set_option("display.width",260); pd.set_option("display.max_columns",40); pd.set_option("display.max_rows",300)
S=eng.load_series(); base=exp.eval_variant(S,{})
# ---------- (1) conjunto multi-velocidad
def sl(m): return dict(p=dict(N_h=140*m,L_h=800*m))
print("=== (1) CONJUNTO MULTI-VELOCIDAD (DEV): cada sleeve y mezcla, delta de Calmar vs V6 (media TRAIN/VAL/DEV por activo)")
rows=[]
def stats_for(s,comb,tr,w): return s.stat(comb,tr,w)
for tf in lab.TFS:
    for a in lab.ASSETS:
        s=S[(a,tf)]
        for name,sleeves in (("V6 (1x)",[sl(1)]),("0.5x",[sl(.5)]),("2x",[sl(2)]),("mezcla 0.5x+1x+2x",[sl(.5),sl(1),sl(2)]),("mezcla 1x+2x",[sl(1),sl(2)]),("mezcla 0.7x+1x+1.4x",[sl(.7),sl(1),sl(1.4)])):
            comb,tr=exp.ens_run(s,sleeves)
            for w in ("TRAIN","VAL","DEV"):
                st=s.stat(comb,tr,w); rows.append(dict(tf=tf,asset=a,name=name,w=w,ret=st["ret"],cagr=st["cagr"],mdd=st["mdd"],cal=st["calmar"],n=st["trades"]))
R=pd.DataFrame(rows)
P=R.pivot_table(index=["asset","tf","w"],columns="name",values="cal")
for nm in P.columns: P[nm+"_d"]=P[nm]-P["V6 (1x)"]
d=P[[c for c in P.columns if c.endswith("_d")]].reset_index()
print(d[d.w!="DEV"].groupby(["asset","w"]).mean(numeric_only=True).round(2).to_string())
print("\nDEV por tf (ETH):"); print(d[(d.asset=="ETH")&(d.w=="DEV")].set_index("tf").drop(columns=["asset","w"]).round(2).to_string())
R.to_pickle("round3_ens.pkl")
# ---------- (2) combinaciones
V={"V6":{}}
sh=dict(short=1,sN_h=280,sL_h=1600)
V["P4x.25"]=dict(ext=dict(pyr_at=4,pyr_frac=.25,pyr_n=1))
V["P4x.5"]=dict(ext=dict(pyr_at=4,pyr_frac=.5,pyr_n=1))
V["S(280/1600)x.5"]=dict(p=sh,ext=dict(fund_s=-1),sw=.5)
V["S+P4x.25"]=dict(p=sh,ext=dict(fund_s=-1,pyr_at=4,pyr_frac=.25,pyr_n=1),sw=.5)
V["S+P4x.5"]=dict(p=sh,ext=dict(fund_s=-1,pyr_at=4,pyr_frac=.5,pyr_n=1),sw=.5)
print("\n=== (2) COMBINACIONES vs V6 (DEV)")
rows=[]
for name,v in V.items():
    if name=="V6": continue
    r=exp.eval_variant(S,v); d=exp.delta_table(base,r); sm=exp.summarize(name,d); rows.append(sm); exp.log_trial(name,sm)
print(pd.DataFrame(rows).to_string(index=False))
# ---------- (3) por años, solo DEV (2018-2023), ETH
print("\n=== (3) RETORNO POR AÑO (ETH, solo 2017-2023) V6 vs candidatos")
for tf in lab.TFS:
    s=S[("ETH",tf)]; out={}
    for name,v in V.items():
        eq,ex,trd=exp.run_variant(s,v); out[name]=exp.yearly(s,eq,years=range(2017,2024))*100
    print(f"\n-- ETH {tf}"); print(pd.DataFrame(out).round(1).to_string())
# ---------- (4) a igual drawdown (ETH, DEV): CAGR de V7 candidato con riesgo escalado hasta MDD = MDD de V6
print("\n=== (4) A IGUAL DRAWDOWN (MDD DEV de V6 por tf/activo): CAGR(DEV) V6 vs candidato con riesgo reescalado (m = multiplicador del riesgo base 5%)")
rows=[]
for a in ("ETH","BTC","DOGE"):
    for tf in lab.TFS:
        s=S[(a,tf)]; eq,ex,trd=exp.run_variant(s,{}); b=s.stat(eq,trd,"DEV")
        for name in ("P4x.25","P4x.5","S(280/1600)x.5","S+P4x.25","S+P4x.5"):
            m,st=exp.matched_dd(S,V[name],a,tf,b["mdd"])
            rows.append(dict(asset=a,tf=tf,cand=name,mdd_v6=b["mdd"],cagr_v6=b["cagr"],m=m,cagr_cand=st["cagr"],mdd_cand=st["mdd"],d_cagr=st["cagr"]-b["cagr"]))
M=pd.DataFrame(rows)
print((M.pivot_table(index=["asset","tf"],columns="cand",values="d_cagr")*100).round(1).to_string())
print("\nmultiplicador de riesgo medio que iguala DD:"); print(M.pivot_table(index=["asset","tf"],columns="cand",values="m").round(2).to_string())
