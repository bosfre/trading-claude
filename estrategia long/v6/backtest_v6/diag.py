import pandas as pd,numpy as np,eng,core,gen,sigs
pd.set_option("display.width",300); pd.set_option("display.max_columns",50)
SER=eng.load_series()
# ---------- 1) ¿La selección en DEV predice el OOS? cohorte de las 100 mejores por score DEV (con tope de MDD)
print("=== 1) COHORTE top-100 por score DEV -> rendimiento OOS (ETH, CAGR anual %, config con sizing 2%)")
KEYS=["N_b","L_b","A_b","sN_b","sL_b","kI","kT","tp","xf","tron","be","adx","ent","short","slope"]
for tf in ("1h","4h","1d"):
    d=pd.read_csv(f"search2_{tf}.csv").sort_values("score",ascending=False)
    res=[]
    for _,r in d.head(100).iterrows():
        p={k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in KEYS}
        m=core.evaluate(SER,tf,p,wins=("DEV","OOS"),assets=("ETH","BTC"))
        res.append((m["ETH"]["DEV"]["cagr"],m["ETH"]["OOS"]["cagr"],m["ETH"]["OOS"]["mdd"],m["BTC"]["OOS"]["cagr"]))
    a=np.array(res)
    # aleatorias: cohorte base (configs medianas) para comparar
    rnd=d.sample(100,random_state=1); rr=[]
    for _,r in rnd.iterrows():
        p={k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in KEYS}
        m=core.evaluate(SER,tf,p,wins=("DEV","OOS"),assets=("ETH",)); rr.append((m["ETH"]["DEV"]["cagr"],m["ETH"]["OOS"]["cagr"]))
    rr=np.array(rr)
    print(f"{tf}: top100 -> ETH CAGR DEV mediana {np.nanmedian(a[:,0])*100:.1f}% | OOS mediana {np.nanmedian(a[:,1])*100:.1f}% (p25 {np.nanpercentile(a[:,1],25)*100:.1f}%, % con OOS>0: {np.mean(a[:,1]>0)*100:.0f}%) | MDD OOS mediano {np.nanmedian(a[:,2])*100:.1f}% | BTC OOS mediana {np.nanmedian(a[:,3])*100:.1f}%"
          f"  || 100 configs al azar de las 40.000: DEV {np.nanmedian(rr[:,0])*100:.1f}% OOS {np.nanmedian(rr[:,1])*100:.1f}%")
# ---------- 2) cambios individuales sobre V3 (una sola modificación cada vez), V3 sizing 2%
print("\n=== 2) CAMBIOS INDIVIDUALES SOBRE V3 (solo un cambio cada vez; resto = V3). Celda = mejora de Calmar (CAGR/|MDD|) vs V3")
V3=dict(N_h=140,L_h=800,A_h=56,kI=5.0,kT=5.0,minN=5,minL=20,minA=10,ent="hh")
CH={"cierre en vez de máx. (ruptura)":dict(ent="hc"),"pendiente EMA>0":dict(slope=1),"TP 20 ATR":dict(tp=20),"trailing ancho kT=8":dict(kT=8),
    "Donchian 72h":dict(N_h=72),"Donchian 96h":dict(N_h=96),"añadir cortos simétricos":dict(short=1),"ADX>20":dict(adx=20),
    "salida por canal (=N)":dict(xN_h=140),"stop inicial kI=6":dict(kI=6.0),"stop inicial kI=4":dict(kI=4.0),"EMA 400h":dict(L_h=400),"break-even tras 4 ATR":dict(be=4)}
def calm(m): return m["calmar"] if m["calmar"]==m["calmar"] else np.nan
def stats(tf,a,p):
    m,_,_,_=gen.run(SER[(a,tf)],dict(V3,**p),wins=("TRAIN","VAL","OOS")); return m
base={(tf,a):stats(tf,a,{}) for tf in ("1h","4h","1d") for a in ("ETH","BTC","DOGE")}
# validación: gen reproduce sigs.v3
s=SER[("ETH","1h")]; e1=s.run(sigs.v3(s),5.0)[2]; print("check trades V3 ETH1h gen vs sigs:",len(e1),base[("1h","ETH")]["TRAIN"]["trades"]+base[("1h","ETH")]["VAL"]["trades"]+base[("1h","ETH")]["OOS"]["trades"])
rows=[]
for name,ch in CH.items():
    r={"cambio":name}; wins_all=0; cells=0; eth_oos_d=[]
    for tf in ("1h","4h","1d"):
        for a in ("ETH","BTC","DOGE"):
            m=stats(tf,a,ch)
            for w in ("TRAIN","VAL","OOS"):
                d=calm(m[w])-calm(base[(tf,a)][w])
                if d==d: cells+=1; wins_all+= (d>0)
                if a=="ETH" and w=="OOS": eth_oos_d.append(d)
    tr=np.nanmean([calm(stats(tf,"ETH",ch)["TRAIN"])-calm(base[(tf,"ETH")]["TRAIN"]) for tf in ("1h","4h","1d")])
    va=np.nanmean([calm(stats(tf,"ETH",ch)["VAL"])-calm(base[(tf,"ETH")]["VAL"]) for tf in ("1h","4h","1d")])
    oo=np.nanmean(eth_oos_d)
    bo=np.nanmean([calm(stats(tf,"BTC",ch)["OOS"])-calm(base[(tf,"BTC")]["OOS"]) for tf in ("1h","4h","1d")])
    do=np.nanmean([calm(stats(tf,"DOGE",ch)["OOS"])-calm(base[(tf,"DOGE")]["OOS"]) for tf in ("1h","4h","1d")])
    rows.append(dict(cambio=name,ETH_train=tr,ETH_val=va,ETH_oos=oo,BTC_oos=bo,DOGE_oos=do,celdas_mejoran=f"{wins_all}/{cells}"))
T=pd.DataFrame(rows).set_index("cambio").round(2); print(T.to_string())
T.to_csv("diag_changes.csv")
