import pandas as pd,numpy as np,json,eng,core,gen
SER=eng.load_series()
KEYS=["N_b","L_b","A_b","sN_b","sL_b","kI","kT","tp","xf","tron","be","adx","ent","short","slope"]
def load_top(tf):
    r=pd.read_csv(f"robust_{tf}.csv").iloc[0]
    return {k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in KEYS}
# cada "característica" y cómo se neutraliza
OFF={"cortos":dict(short=0),"TP":dict(tp=0),"canal de salida":dict(xf=0),"trailing diferido":dict(tron=0),"break-even":dict(be=0),
     "filtro ADX":dict(adx=0),"pendiente EMA":dict(slope=0),"ruptura por cierre (vs máx.)":dict(ent="hh"),"trailing ancho (kT=kI)":None}
def off(p,name):
    q=dict(p)
    if name=="trailing ancho (kT=kI)": q["kT"]=q["kI"]
    else: q.update(OFF[name])
    return q
def sc(tf,p): return core.obj(core.evaluate(SER,tf,p))
out={}; report=[]
for tf in ("1h","4h","1d"):
    full=load_top(tf); base=sc(tf,full); cur=dict(full); cs=base
    loo=[]
    for n in OFF:
        q=off(full,n); 
        if q==full: continue
        loo.append((n,sc(tf,q)-base))
    # eliminación hacia atrás: quita la característica cuya retirada cuesta menos, mientras el coste sea < 0.04
    removed=[]
    while True:
        best=None
        for n in OFF:
            if n in removed: continue
            q=off(cur,n)
            if q==cur: continue
            s=sc(tf,q)
            if best is None or s>best[1]: best=(n,s,q)
        if best is None or (cs-best[1])>0.04: break
        removed.append(best[0]); cur=best[2]; cs=best[1]
    out[tf]=dict(full=full,lean=cur,removed=removed,score_full=base,score_lean=cs)
    report.append((tf,base,cs,removed,loo))
json.dump(out,open("final_cfg.json","w"),indent=1,default=lambda o:o.item() if hasattr(o,'item') else str(o))
for tf,b,c,rem,loo in report:
    print(f"\n=== {tf}: score DEV completa {b:.2f} -> simplificada {c:.2f} | características eliminadas: {rem}")
    print("   coste en score al quitar cada una (dentro de la config completa):",{n:round(v,2) for n,v in loo})
    print("   CONFIG SIMPLIFICADA:",{k:out[tf]['lean'][k] for k in KEYS})
