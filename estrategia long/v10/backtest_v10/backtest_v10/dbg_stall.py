import exp10, exp9, numpy as np
S = exp10.load(True)
def V(y): return dict(name="t", p=dict(xref=exp10.B800), x={}, y=y)
for tf in ("4h","1d"):
    s = S[("ETH", tf)]
    base = exp10.run10v(s, V({}))
    print(tf, "base ops", len(base[2]), "eq final", round(base[0][-1],3))
    for y in (dict(st_h=280, st_k=3.5), dict(st_h=560, st_k=3.5), dict(st_h=100, st_k=1.0), dict(st_h=24, st_k=0.5)):
        r = exp10.run10v(s, V(y))
        print("  ", y, "ops", len(r[2]), "eq final", round(r[0][-1],3), "razones de salida", np.bincount(r[2][:,8].astype(int), minlength=8))
# cuantas veces el estancamiento llega a darse: barras en posicion con (i-last_hi)>=st_bars
s = S[("ETH","4h")]; eq,ex,trd = exp10.run10v(s, V({}))
h = s.h; mx = 0
for t in trd:
    ei, xi = int(t[0]), int(t[1]); ext = t[3]; last = ei; worst = 0
    for i in range(ei, xi+1):
        if h[i] > ext: ext = h[i]; last = i
        worst = max(worst, i-last)
    mx = max(mx, worst)
print("max barras 4h sin nuevo maximo dentro de una operacion:", mx, "=", mx*4, "h")
