import pandas as pd,numpy as np,eng,gen,data as DT
import final2 as F
pd.set_option("display.width",250)
SER=F.SER
NEW={"1h":"ETHUSDT-1h-2026-01-05.csv","4h":"ETHUSDT-4h-2026-01-12.csv","1d":"ETHUSDT-1d-2026-01-08.csv"}
print("=== 1) COHERENCIA de los CSV nuevos con el histórico (ETH)")
mod={}
for tf,fn in NEW.items():
    n=DT.new_csv(fn); h=SER[("ETH",tf)].df
    com=n.index.intersection(h.index)
    print(f"\n{fn}: {len(n)} barras  {n.index[0]} -> {n.index[-1]} | último dato del histórico ({tf}): {h.index[-1]} | barras que ya estaban en el histórico: {len(com)}, realmente nuevas: {len(n.index.difference(h.index))}")
    if len(com):
        d=(n.loc[com,["open","high","low","close"]]/h.loc[com,["open","high","low","close"]]-1)
        print(f"   diferencia relativa OHLC vs histórico: media {d.abs().values.mean()*100:.3f}% | máx {d.abs().values.max()*100:.3f}% | volumen nuevo/histórico: x{(n.loc[com,'volume']/h.loc[com,'volume']).mean():.1f}")
    # serie modificada: sustituye barras solapadas y añade las nuevas
    m=h.copy()
    if len(com): m.loc[com,["open","high","low","close","volume"]]=n.loc[com,["open","high","low","close","volume"]].values
    new=n.loc[n.index.difference(h.index)]
    if len(new): m=pd.concat([m,new]).sort_index()
    mod[tf]=eng.Series("ETH",tf,m)
print("\n=== 2) ¿Qué hace la estrategia en esas ventanas? (V3 y V6; histórico original vs histórico con CSV nuevo)")
WIN={"1h":("2026-01-05 00:00","2026-01-05 23:00"),"4h":("2026-01-12 00:00","2026-01-12 20:00"),"1d":("2026-01-08 00:00","2026-01-08 00:00")}
def run(ver,s):
    p=dict(F.V3P)
    if ver=="V6": p.update(tp=20,risk=.05,mlev=2.0)
    else: p.update(risk=.02,mlev=1.0)
    d,q=gen.gen(s,p); eq,ex,trd=s.run(d,q["kI"],q["kT"],risk=q["risk"],mlev=q["mlev"],tp=q["tp"]); return eq,ex,trd
for tf in ("1h","4h","1d"):
    a,b=WIN[tf]
    for ver in ("V3","V6"):
        out=[]
        for nm,s in (("histórico",SER[("ETH",tf)]),("con CSV nuevo",mod[tf])):
            eq,ex,trd=run(ver,s); e=pd.Series(eq,index=s.idx)
            if pd.Timestamp(a) not in e.index or pd.Timestamp(b) not in e.index: out.append(f"{nm}: sin barras en ventana"); continue
            i0=e.index.get_loc(pd.Timestamp(a)); base=e.iloc[i0-1] if i0>0 else e.iloc[0]
            ret=e.loc[b]/base-1; pos=ex[e.index.get_loc(pd.Timestamp(b))]
            ntr=int(((trd[:,1]>=i0)&(trd[:,1]<=e.index.get_loc(pd.Timestamp(b)))).sum()) if len(trd) else 0
            out.append(f"{nm}: Δequity ventana {ret*100:+.2f}% | exposición al cierre {pos:+.2f}x | operaciones cerradas en ventana {ntr} | equity final {e.iloc[-1]:.4f}")
        print(f"ETH {tf} {ver}  [{a} → {b}]\n    "+"\n    ".join(out))
print("\n=== 3) Estado de V6 al final de los datos (¿hay posición abierta?)")
for tf in ("1h","4h","1d"):
    for nm,s in (("histórico",SER[("ETH",tf)]),("con CSV nuevo",mod[tf])):
        eq,ex,trd=run("V6",s); last=trd[-1] if len(trd) else None
        print(f"ETH {tf} {nm}: última barra {s.idx[-1]} | exposición {ex[-1]:+.2f}x | última operación: entrada {s.idx[int(last[0])]} salida {s.idx[int(last[1])]} ret {last[5]*100:+.1f}% motivo {int(last[8])}")
