import exp9, data8, numpy as np, pandas as pd, sys, time
pd.set_option("display.width",250)
B=exp9.B800
def V(name,x=None,ext=None,p=None):
    pp=dict(xref=B); pp.update(p or {}); return dict(name=name,p=pp,ext=ext or {},x=x or {})
S=exp9.load(True); SP=data8.load_all(True,pre=True,etc=False); SE=data8.load_all(False,pre=False,etc=True)
def run_on(Sx,a,tf,v,wn):
    exp9_refs(Sx); s=Sx[(a,tf)]; eq,ex,trd=exp9.run9(s,v); return exp9.wstat(s,eq,ex,trd,None,None,wn),eq,ex,trd
def exp9_refs(Sx): exp9.exp8.set_refs(Sx); exp9.exp8._REFS.clear() if False else None
def reset_refs(Sx):
    for k in [k for k in exp9.exp8._REFS if not isinstance(k,str)]: del exp9.exp8._REFS[k]
    exp9.exp8.set_refs(Sx)
def gate(v,tf):
    out={}
    # H1 PRE (solo 1D)
    if tf=="1d":
        reset_refs(SP); mn,_,_,_=run_on(SP,"ETH",tf,v,"PRE"); mb,_,_,_=run_on(SP,"ETH",tf,exp9.V8,"PRE")
        out["H1_PRE"]=(round(exp9.calm(mn)-exp9.calm(mb),2),round(mn["ret"]*100,1),round(mb["ret"]*100,1),round(mn["mdd"]*100,1),round(mb["mdd"]*100,1))
    # H2 ETC (FULL = todos los datos de ETC)
    reset_refs(SE); mn,_,_,_=run_on(SE,"ETC",tf,v,"FULL"); mb,_,_,_=run_on(SE,"ETC",tf,exp9.V8,"FULL")
    out["H2_ETC"]=(round(exp9.calm(mn)-exp9.calm(mb),2),round(exp9.calm(mn),2),round(exp9.calm(mb),2))
    # H3 OOSX
    reset_refs(S); mn,_,_,_=run_on(S,"ETH",tf,v,"OOSX"); mb,_,_,_=run_on(S,"ETH",tf,exp9.V8,"OOSX")
    out["H3_OOSX"]=(round(exp9.calm(mn)-exp9.calm(mb),2),round(mn["ret"]*100,1),round(mb["ret"]*100,1),round((mn["mdd"]-mb["mdd"])*100,1))
    # H4 costes x2 (DEV)
    s=S[("ETH",tf)]; eq,ex,trd=exp9.run9(s,v,2.0); a=exp9.wstat(s,eq,ex,trd,None,None,"DEV"); eq,ex,trd=exp9.run9(s,exp9.V8,2.0); b=exp9.wstat(s,eq,ex,trd,None,None,"DEV")
    out["H4_x2"]=round(exp9.calm(a)-exp9.calm(b),2)
    # H5 a igual DD
    eq,ex,trd=exp9.run9(s,exp9.V8); b=exp9.wstat(s,eq,ex,trd,None,None,"DEV"); m,st=exp9.matched_dd9(S,v,"ETH",tf,b["mdd"])
    out["H5_ddmatch"]=(round((st["cagr"]-b["cagr"])*100,1),round(m,2))
    # H6 años 2018-25
    def yearly(vv):
        eq,ex,trd=exp9.run9(s,vv); e=pd.Series(eq,index=s.idx).ffill(); ye=e.resample("YE").last(); r=ye/ye.shift(1)-1; r.index=r.index.year; return r
    yn=yearly(v); yb=yearly(exp9.V8); d=(yn-yb).loc[2018:2025]
    out["H6_anios"]=(int((d>0).sum()),len(d),round(d.mean()*100,1))
    return out
if __name__=="__main__":
    cands=[("1d",V("salida close<EMA-1ATR",x=dict(trend_exit=1.0)),"PASA criterio previo"),("1d",V("saltar si ext>6",x=dict(ext_max=6)),"CASI (BTC -0.02): EXPLORATORIA, no adoptable")]
    for tf,v,tag in cands:
        open("oos_access_log.txt","a").write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} V9 holdouts H1-H6 abiertos para '{v['name']}' ({tf}) [{tag}]\n")
        print(tf,v["name"],tag); r=gate(v,tf)
        for k,x in r.items(): print("  ",k,x)
