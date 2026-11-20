import pandas as pd, numpy as np
T=pd.read_csv("tabla_TF_normalizada_V7_V8.csv"); V=T[T.version=="V8"]
def g(win,tf,col,ver="V8"):
    r=T[(T.version==ver)&(T.tf==tf)&(T.ventana==win)]; return float(r[col].iloc[0])
def es(s): return s.replace(",","§").replace(".",",").replace("§",".")
pc=lambda x,d=1: es(f"{x*100:+,.{d}f} %") if x==x else "—"
pc0=lambda x,d=1: es(f"{x*100:,.{d}f} %") if x==x else "—"
nf=lambda x,d=2: es(f"{x:,.{d}f}")
W0="COMUN 2017-08→2026-10"
def tab_common():
    rows=[("Años analizados","yrs","{:.1f}"),("Rentabilidad total","ret","pc"),("**CAGR**","cagr","pc0"),("Máx. drawdown","mdd","pc"),("**Calmar (CAGR/DD)**","calmar","{:.2f}"),("Operaciones","n","{:.0f}"),("Operaciones/año","trades_yr","{:.1f}"),
          ("Win rate","win","pc0"),("Profit Factor (% por operación)","pf","{:.2f}"),("Profit Factor ($, como TradingView)","pf_usd","{:.2f}"),("Beneficio medio/operación (% del equity)","avg_ret","pc"),("R medio/operación","avgR","{:.2f}"),
          ("Ganancia media / pérdida media","payoff","{:.2f}"),("Horas medias en posición","hours","{:.0f}"),("% del tiempo en mercado","expo","pc0")]
    L=["| Métrica (ETH, V8, riesgo 5 %) | 1H | 4H | 1D |","|---|---|---|---|"]
    for lab,c,f in rows:
        vals=[]
        for tf in ("1h","4h","1d"):
            x=g(W0,tf,c)
            vals.append(pc(x) if f=="pc" else pc0(x) if f=="pc0" else es(f.format(x)))
        L.append(f"| {lab} | "+" | ".join(vals)+" |")
    return "\n".join(L)
def tab_windows():
    wins=[("TRAIN 2017-08→2021","TRAIN"),("VAL 2022-23","VAL"),("OOS1 2024→2026-01","OOS1 2024-01→2026-01"),("OOS2 2026-01→10 (0,73 años)","OOS2"),("Común 2017-08→2026-10",None),("Últimos 2 años 2024-01→2026-10","L2"),("Últimos 9 meses 2026-01→10","L9")]
    name={"TRAIN":"TRAIN 2017-08→2021","VAL":"VAL 2022-23","OOS1 2024-01→2026-01":"OOS1 2024→2026-01","OOS2":"OOS2 2026-01→10","L2":"ÚLTIMOS 2 AÑOS (2024-01→2026-10)","L9":"ÚLTIMOS 9 MESES (2026-01-05→2026-10)"}
    L=["| Ventana | CAGR 1H / 4H / 1D | Máx. DD 1H / 4H / 1D | Calmar 1H / 4H / 1D | Mejor Calmar | Operaciones |","|---|---|---|---|---|---|"]
    for lab,k in wins:
        w=W0 if k is None else name[k]
        c=[g(w,tf,"cagr") for tf in ("1h","4h","1d")]; d=[g(w,tf,"mdd") for tf in ("1h","4h","1d")]; k_=[g(w,tf,"calmar") for tf in ("1h","4h","1d")]; n=[int(g(w,tf,"n")) for tf in ("1h","4h","1d")]
        best=("1H","4H","1D")[int(np.nanargmax(k_))]
        L.append(f"| {lab} | "+" / ".join(nf(x*100,1) for x in c)+" % | "+" / ".join(nf(x*100,1) for x in d)+" % | "+" / ".join(nf(x) for x in k_)+f" | **{best}** | "+" / ".join(str(x) for x in n)+" |")
    return "\n".join(L)
def tab_eqdd():
    E=pd.read_csv("igual_drawdown_V8_por_TF.csv"); L=["| DD objetivo | 1H (riesgo → CAGR) | 4H (riesgo → CAGR) | 1D (riesgo → CAGR) |","|---|---|---|---|"]
    for t in (-0.10,-0.12,-0.15,-0.20):
        r=[E[(E.dd_objetivo==t)&(E.tf==tf)].iloc[0] for tf in ("1h","4h","1d")]
        L.append(f"| {nf(t*100,0)} % | "+" | ".join(f"{nf(x.riesgo_pct,1)} % → **{nf(x.cagr*100,1)} %**" for x in r)+" |")
    return "\n".join(L)
def tab_costs():
    C=pd.read_csv("costes_V8_por_TF.csv"); L=["| Costes (comisión+slippage+funding) | 1H CAGR / DD / Calmar | 4H | 1D |","|---|---|---|---|"]
    for c in (1.0,2.0,3.0):
        r=[C[(C.coste==c)&(C.tf==tf)].iloc[0] for tf in ("1h","4h","1d")]
        L.append(f"| x{c:.0f} | "+" | ".join(f"{nf(x.cagr*100,1)} % / {nf(x.mdd*100,1)} % / {nf(x.calmar)}" for x in r)+" |")
    return "\n".join(L)
def tab_blend():
    B=pd.read_csv("mezcla_temporalidades_V8.csv"); L=["| Cartera (pesos fijos, sin optimizar) | CAGR | Máx. DD | Calmar (común) | Calmar TRAIN | Calmar VAL | Calmar 2024→2026-10 |","|---|---|---|---|---|---|---|"]
    for k in ("1H","4H","1D","1H+4H (50/50)","4H+1D (50/50)","1H+4H+1D (1/3 c/u)"):
        c=B[(B.cartera==k)&(B.ventana=="COMUN 2017-08→2026-10")].iloc[0]
        x=lambda w: B[(B.cartera==k)&(B.ventana==w)].iloc[0].calmar
        L.append(f"| {k} | {nf(c.cagr*100,1)} % | {nf(c.mdd*100,1)} % | {nf(c.calmar)} | {nf(x('TRAIN'))} | {nf(x('VAL'))} | {nf(x('OOS1+OOS2 2024→2026-10'))} |")
    return "\n".join(L)
def tab_year():
    Y=pd.read_csv("retorno_anual_ETH_V8_por_TF.csv",index_col=0); L=["| Año | 1H | 4H | 1D |","|---|---|---|---|"]
    for y,r in Y.iterrows(): L.append(f"| {y}{' (parcial)' if y in (2017,2026) else ''} | {pc(r['1h'])} | {pc(r['4h'])} | {pc(r['1d'])} |")
    return "\n".join(L)
def tab_boot():
    O=pd.read_csv("bootstrap_bloques_TF_V8.csv"); L=["| TF | CAGR (p5 – mediana – p95) | Máx. DD mediano | Calmar (p5 – mediana – p95) |","|---|---|---|---|"]
    for _,r in O.iterrows(): L.append(f"| {r.tf.upper()} | {nf(r.cagr_p5*100,1)} – {nf(r.cagr_med*100,1)} – {nf(r.cagr_p95*100,1)} % | {nf(r.mdd_med*100,1)} % | {nf(r.calmar_p5)} – {nf(r.calmar_med)} – {nf(r.calmar_p95)} |")
    return "\n".join(L)
def tab_tv():
    R=pd.read_csv("emulacion_TV_V8_vs_tus_numeros.csv"); R=R[R.version=="V8"]
    L=["| Caso | Mi emulación de V8.pine (rentab. / DD / win / PF / operaciones) | Tu TradingView |","|---|---|---|"]
    def r(caso,modo): x=R[(R.caso==caso)&(R.modo==modo)].iloc[0]; return es(f"{x.ret:+,.0f} % / {x.mdd:.1f} % / {x.win:.0f} % / {x.pf:.2f} / {int(x.n)}")
    L.append(f"| 1D histórico completo (desde 2015) | {r('1D histórico completo (2015-08→)','arranque limpio')} | +2.491,84 % / 18 % / 46 % / 1,929 / ? |")
    L.append(f"| 4H 2024-01-01→2026-10 | {r('4H últimos 2 años','arranque limpio')} (arranque limpio); {r('4H últimos 2 años','corrida continua recortada')} (corrida continua) | +42 % / 14 % / ? / 2,17 / ? |")
    L.append(f"| 1H ~9 meses | {r('1H últimos 9 meses','arranque limpio')} (arranque limpio); {r('1H últimos 9 meses','corrida continua recortada')} (continua) | +36 % / 12 % / ? / 1,46 / 11 |")
    return "\n".join(L)
E15=pd.read_csv("igual_drawdown_V8_por_TF.csv").query("dd_objetivo==-0.15 and tf=='1d'").iloc[0]
doc=f"""# V9 (optimización de V8) — informe

## 1. Conclusión

**V9 = V8 sin cambios de lógica.** Probé 15 hipótesis nuevas de stops, salidas, entradas y tamaño (45 pruebas = 15 × 3 temporalidades), fijadas por escrito **antes** de ejecutarlas (`v9_prereg.txt`) y evaluadas contra V8 solo con TRAIN y VAL en ETH + BTC + DOGE. **Una sola pasó el criterio** (1D: salir si el cierre cae 1 ATR por debajo de la EMA) y fue descartada en los holdouts: empeora en ETC (−0,05 de Calmar) y su efecto es de +0,6 pp de CAGR a igual drawdown. La que más "parecía" mejorar el beneficio por operación (no entrar si el precio está muy extendido sobre la EMA) **se hunde en 2015-17** (+96 % frente a +306 %) y en ETC, y por eso no la adopto. No he encontrado una forma robusta de cortar antes las perdedoras ni de dejar correr más las ganadoras.

**Lo que esto significa para tus objetivos**
- **1D: bajar el DD del 18 % hacia 10-15 % manteniendo la rentabilidad, o superar +3.000 %: no es posible con cambios de lógica; solo con menos riesgo** (y entonces baja la rentabilidad casi en proporción: el Calmar apenas se mueve). En mi backtest, 1D con DD −15 % exige riesgo 3,1 % por operación y da un CAGR de {nf(E15.cagr*100,1)} % (frente a {nf(g(W0,'1d','cagr')*100,1)} % con riesgo 5 % y DD {nf(g(W0,'1d','mdd')*100,1)} %). El +2.491 % de tu TradingView es real (lo reproduzco), pero sale de **11 años de histórico que incluyen el tramo 2015-17**.
- **4H: mejorar el +42 % sin subir el DD del 14 %: no logrado.** Ningún cambio supera a V8 de forma robusta.
- **1H: no logrado**, y con 9 meses y ~11 operaciones no se puede demostrar ni refutar nada.

**Mejor temporalidad hoy: 4H.** Con periodos normalizados (mismas fechas, mismos costes), 4H tiene el mejor Calmar y el menor drawdown de la ventana común, gana en 4 de las 7 ventanas (1H gana TRAIN y los dos tramos de 2026, que se solapan) y mantiene el mejor Calmar con costes ×2 y ×3. 1H da algo más de rentabilidad bruta con más drawdown y es estadísticamente indistinguible de 4H. **1D es la peor en casi todo lo normalizado** y su ventaja aparente en TradingView viene de tener más años (2015-17). Detalle en la sección 2.

## 2. 1H vs 4H vs 1D, normalizado

Una comparación honesta exige la **misma ventana**. Tus cifras de TradingView no lo son: 1D son ~11,2 años (desde 2015), 4H son 2,8 años y 1H son 9 meses. Normalizadas a CAGR serían ≈ 33,9 % (1D), 13,6 % (4H) y 50,9 % (1H, con 11 operaciones: no inferible), y los periodos son tan distintos (2015-17 fue un mercado alcista parabólico) que tampoco son comparables entre sí.

**Ventana común 2017-08-17 → 2026-10-03 (9,1 años, mismas fechas, costes del repo)**

{tab_common()}

**Por ventanas** (la ventana común incluye OOS2; todas las temporalidades usan las mismas fechas)

{tab_windows()}

Lectura: 4H es la mejor en VAL, OOS1, ventana común y últimos 2 años; 1H gana TRAIN y el tramo corto de 2026; **1D no es la mejor en ninguna ventana**.

**A igual drawdown** (riesgo reescalado para dar el mismo DD en la ventana común; mide la eficiencia, no el riesgo asumido)

{tab_eqdd()}

A un DD del 15 %, 4H rinde ≈ 2 veces lo que 1D (25,8 % frente a 13,1 % de CAGR). Esto también responde a tu objetivo de DD 10-15 %: **si quieres ese drawdown, 4H lo da con más del doble de rentabilidad que 1D**.

**¿Es la ventaja de 1D simplemente tener más años?** Sí, y es lo contrario de una ventaja. 1D desde 2015-08: CAGR 31,7 %, Calmar 1,37 (en Python); desde 2017-08: CAGR 20,9 %, Calmar 0,90; 2024→2026-10: CAGR 5,8 %. Los dos años 2015-17 (+306 %, Calmar 10,4, win rate 74 %) elevan el CAGR de 1D en ~11 pp. 4H y 1H no tienen datos de Binance anteriores a 2017-08, así que no pueden "heredar" ese tramo.

**¿La diferencia entre temporalidades es real o ruido?** Bootstrap por bloques de 30 días sobre la ventana común (3.000 remuestreos conjuntos, para respetar la correlación entre temporalidades, 0,80-0,91):

{tab_boot()}

P(Calmar 4H > 1D) = 0,89 · P(Calmar 1H > 1D) = 0,93 · **P(Calmar 1H > 4H) = 0,64** (indistinguibles). Es decir: hay evidencia moderada de que 1D es peor, y **ninguna** de que 1H sea mejor o peor que 4H.

**Costes** (ventana común)

{tab_costs()}

Con costes ×3 el Calmar de 4H sigue en 1,05, el de 1H en 0,94 y el de 1D en 0,56; el recorte relativo de CAGR es parecido en las tres (−25 % a −28 %), así que los costes no cambian el orden.

**Mezclar temporalidades no ayuda**: los retornos diarios están correlacionados (1H-4H 0,91; 4H-1D 0,86; 1H-1D 0,80).

{tab_blend()}

(Cifras calculadas sobre retornos diarios de cada cartera, por eso difieren ligeramente de la tabla de la ventana común, que usa el drawdown barra a barra.)

**Retorno por año (ETH, V8)**

{tab_year()}

1D se queda atrás en los años de tendencia fuerte (2019, 2024, 2025) y solo gana a las otras dos en 2023 y en el tramo parcial de 2017; en 2026 pierde con 6-7 operaciones.

**Calidad por operación**: el beneficio medio por operación es parecido en las tres (2,2 % / 2,2 % / 1,9 % del equity) y el R medio también (0,44 / 0,44 / 0,38); el win rate es casi igual (≈ 43-44 %). La desventaja de 1D no está en la calidad de la operación sino en que hace **menos operaciones al año (11,5 frente a 15,7 y 13,8), tiene menor ratio ganancia/pérdida (2,7 frente a 3,2 y 3,3) y su peor DD es mayor** (episodios de 2023 y 2026).

**Veredicto por criterios** (ventana común salvo indicación)

| Criterio | 1H | 4H | 1D |
|---|---|---|---|
| Rentabilidad / CAGR | **1º** | 2º | 3º |
| Drawdown | 2º | **1º** | 3º |
| Rentabilidad ajustada (Calmar, a igual DD) | 2º | **1º** | 3º |
| Profit Factor ($) | 2º | **1º** | 3º |
| Robustez a costes (Calmar con ×3) | 2º | **1º** | 3º |
| Nº de operaciones (evidencia) | **1º** | 2º | 3º |
| Consistencia entre ventanas | 2º | **1º** | 3º |
| Tramo reciente (2026, ~10 operaciones) | **1º** | 2º | 3º |

**Recomendación**: operar **4H** como temporalidad principal. 1H es una alternativa válida: con riesgo 5 % da +4,6 pp de CAGR a cambio de +4,5 pp de DD, pero a igual drawdown 4H rinde más y la diferencia entre ambas no es estadísticamente distinguible. 1D solo tiene sentido si valoras operar con poca atención (11 operaciones/año), sabiendo que ha sido la menos eficiente.

## 3. Conciliación con tus números de TradingView

Emulé V8.pine con la semántica de TradingView (`engtv.py`, costes de TradingView: 0,06 % comisión + 2 ticks de slippage):

{tab_tv()}

- **1D: reproducido.** Rentabilidad +2.486 % frente a tu +2.491,84 %; beneficio bruto 517.085 frente a 526.424 y pérdida bruta 261.973 frente a 272.840; PF 1,97 frente a 1,929. El win rate no lo reproduzco (50,8 % frente a 46 %; con arranque en 2017-08 sale 46,0 %, y no sé si es casualidad) y mi DD (−22,4 %, cierre a cierre con la operación abierta) es mayor que tu 18 %, que probablemente se mide de otra forma.
- **4H: parcialmente.** Tu +42 % / PF 2,17 se parece a un arranque entre febrero y junio de 2024 (con 5.750 velas: +41,4 %, PF 1,63; con 5.000 velas: +36,1 %), no a arrancar el 2024-01-01 (+81 %). Con arranques distintos (entre 4.250 y 7.000 velas) la rentabilidad de 4H en "2 años" se mueve entre +23 % y +99 %: **el resultado de un periodo corto depende del día de inicio**.
- **1H: no reproducido** (ningún inicio da más de +16 %; tú ves +36 %, con 11 operaciones). Con 10 operaciones y un periodo bajista-lateral, el resultado depende de detalles (datos de tu exchange, la última vela, una posición abierta).
- Mi backtest de Python usa costes más duros que TradingView; por eso en TradingView todo sale algo mejor (V8 informe, §3).

## 4. Qué se probó y por qué se descartó (`experimentos_V9.csv`, `trials9.jsonl`)

**Diagnóstico previo (solo TRAIN+VAL, V8)**: las perdedoras ya pierden poco (R mediano −0,55 / −0,53 / −0,66 en 1H / 4H / 1D) y el 44 % / 43 % / 34 % de ellas llegó a estar +2 ATR en beneficio antes de perder, de modo que el trailing ya recorta gran parte de la pérdida; entre las ganadoras, el 90 % no se mueve más de 2,3-2,9 ATR en contra antes de su máximo, así que un stop inicial mucho más ajustado cortaría ganadoras. Las mejores 10 % de operaciones aportan el 48-53 % del beneficio bruto (sin ellas el PF baja a 1,29-1,35): **es un sistema de colas gordas**, y cualquier regla que recorte las grandes ganadoras (TP, trailing más cerrado) cuesta más de lo que ahorra. El peor DD de 1D en DEV (−16,8 %) es un único episodio de 2023 (abril-octubre).

| Familia | Variantes | Resultado | Por qué se descarta |
|---|---|---|---|
| G1 Salida temporal (140/280 h; sin 1/2 ATR de beneficio) | 4 | ninguna pasa | TRAIN y VAL de signo contrario o nulo; en 1D empeora TRAIN (−0,15 a −0,24) |
| G1 Salir si cierre < EMA / < EMA−1 ATR | 2 | **1 pasa (1D, EMA−1 ATR)** | Cae en ETC (−0,05) y aporta +0,6 pp de CAGR a igual DD; 1H y 4H no pasan |
| G1 Salir si BTC < EMA 800 h | 1 | peor | ΔCalmar DOGE −0,25 (1H) y −0,39 (4H) y R/operación negativo en las tres TF |
| G2 Trailing 5→7 ATR tras +8 ATR / 5→8 tras +12 | 2 | peor | Empeora TRAIN o VAL en las tres TF y sube el DD (hasta 2,1 pp peor) |
| G2 TP 20 ATR → trailing 3,5 ATR | 1 | peor | −0,2 a −0,6 de Calmar en BTC, DOGE y VAL; DD de 1H 4,5 pp peor |
| G3 No entrar si extensión sobre EMA > 6 / > 8 ATR | 2 | **casi** (1D, > 6: ETH TRAIN +0,89, VAL +0,24, DOGE +0,14, BTC −0,02) | Falla el criterio por BTC; mirada exploratoria: **2015-17 −6,29 de Calmar** (+96 % frente a +306 %: las grandes tendencias empiezan muy extendidas), ETC −0,23. En 1H/4H BTC y DOGE empeoran (−0,2 a −0,6) |
| G3 Cierre de la vela de ruptura en el 50 % / 70 % superior | 2 | inestable | Signos contrarios TRAIN/VAL (1H, 4H: +0,6/−0,47; +0,32/−0,38) |
| G3 Tamaño ×0,5 si extensión > 6 ATR | 1 | peor | BTC/DOGE −0,1 a −0,28 en 1H y 4H |

Criterio de selección (por temporalidad, contra V8): ΔCalmar ETH > 0 en TRAIN **y** VAL; ΔCalmar BTC y DOGE ≥ 0; ΔDD ETH no peor de 1 pp; ΔR por operación ETH > 0. Holdouts solo para las que pasan: 2015-17 (1D), ETC, 2024→2026-10, costes ×2, igual DD, años.

**Aviso estadístico**: 45 pruebas dan 1-2 "aciertos" por azar; el que apareció (1D, EMA−1 ATR) se comportó como tal. Por eso no cambio V8.

**Lo que ya estaba descartado y no repetí** (V6/V7/V8): pirámide, cortos, reentrada, salidas parciales, entrada por stop, stop al cierre, throttle por DD, trinquetes, multi-velocidad, filtros de volatilidad/ADX/régimen largo, TP 0-40, N×L×ATR×k (hasta 3.360 combinaciones en 1D), ETH/BTC. **No probé**: volumen (la cola de 2026 no tiene volumen), filtros de renta variable/dominancia, nuevos activos. El stop inicial más estrecho (kI) ya estaba en la búsqueda de V6.

## 5. Método, validación y límites

- **Protocolo**: no hay OOS virgen para V9 (OOS1 2024→2026-01 se miró 3 veces y OOS2 2026-01→10 se abrió en V8). Por eso: (1) selección solo con TRAIN/VAL; (2) holdouts (2015-17, ETC) solo para candidatas aprobadas; (3) 2024→2026-10 solo como veto; (4) todo en `oos_access_log.txt`. Con esto, que V9 = V8 **no añade sobreajuste**. Las cifras de OOS1/OOS2 de V8 ya eran conocidas, así que esas ventanas valen como descripción, no como prueba independiente.
- **Limitaciones**: ~12-16 operaciones/año por temporalidad; las comparaciones entre 1H y 4H no son concluyentes; el bootstrap por bloques no incluye cambios de régimen no vistos; 1D solo tiene el filtro BTC con respaldo débil (V8, §1); datos de 2015-17 y 2026 de otros proveedores que Binance; los números de TradingView en periodos cortos no son reproducibles al detalle.
- **Siguientes pasos razonables**: (1) usar 4H con riesgo 4,0-4,3 % si quieres DD ≤ 14-15 % (CAGR ≈ 24-26 % en el backtest); (2) repetir V8 cuando haya 6-12 meses nuevos de datos; (3) probar más activos antes de seguir tocando la lógica; (4) si quieres mejorar de verdad 1D, hace falta información nueva, no más reglas sobre el precio de ETH.

## 6. Archivos

`informe_V9.md`, `experimentos_V9.csv`, `trials9.jsonl`, `v9_prereg.txt`, `oos_access_log.txt`, `tabla_TF_normalizada_V8.csv` (todas las métricas por ventana, V7 y V8), `igual_drawdown_V8_por_TF.csv`, `frontera_riesgo_V8.csv`, `costes_V8_por_TF.csv`, `mezcla_temporalidades_V8.csv`, `bootstrap_bloques_TF_V8.csv`, `retorno_anual_ETH_V8_por_TF.csv`, `emulacion_TV_V8_vs_tus_numeros.csv`, `backtest_v9.zip` (código). El Pine sigue siendo `V8_ETH_Donchian_EMA_ATR_TP_BTC.pine` (sin cambios).
"""
open("informe_V9.md","w").write(doc); print(len(doc.splitlines()),"líneas")
