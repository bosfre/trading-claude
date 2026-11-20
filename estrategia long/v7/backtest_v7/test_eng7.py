import numpy as np, time, eng, eng7, gen, lab
S=eng.load_series()
worst=0
for (a,tf),s in S.items():
    d,q=gen.gen(s,lab.V6P)
    eq0,ex0,tr0=s.run(d,q["kI"],q["kT"],risk=q["risk"],mlev=q["mlev"],tp=q["tp"])
    eq1,ex1,tr1=eng7.run7(s,d,q["kI"],q["kT"],risk=q["risk"],mlev=q["mlev"],tp=q["tp"])
    ok=np.allclose(eq0,eq1,equal_nan=True,rtol=0,atol=1e-12) and np.allclose(tr0,tr1[:,:9])
    worst=max(worst,np.nanmax(np.abs(eq0-eq1)))
    print(a,tf,"equivalente" if ok else "DIFIERE",len(tr0),len(tr1))
print("max |dEq|",worst)
s=S[("ETH","1h")]; d,q=gen.gen(s,lab.V6P)
t=time.time()
for _ in range(50): eng7.run7(s,d,q["kI"],q["kT"],risk=.05,mlev=2.0,tp=20)
print("ms por backtest 1H ETH:",(time.time()-t)/50*1000)
# palancas: ejecutan sin error y cambian resultados
for ext in (dict(ddthr=.10,ddmult=.5),dict(rat_m=8,rat_k=3.5),dict(pyr_at=3,pyr_frac=.5),dict(ts_bars=100,ts_mfe=1.0)):
    eq,ex,tr=eng7.run7(s,d,q["kI"],q["kT"],risk=.05,mlev=2.0,tp=20,ext=ext)
    print(ext,"final",round(eq[-1],3),"n",len(tr),"adds",int(tr[:,9].sum()))
