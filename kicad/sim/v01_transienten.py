"""V-01: Transientennachweis des 12-V-Eingangs mit ngspice (libngspice aus KiCad).

Pfad: J1 -> D1 SMBJ18CA (bidirektional) -> D2 SS16 -> FB1 -> VIN_SYS (C1, C6, C7, Buck-Last).
Aufruf mit dem KiCad-Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 -I kicad/sim/v01_transienten.py
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngs

# D1: VBR max 22,1 V (ungünstig für nachfolgende Teile), Rdyn so, dass Vc = 29,2 V bei 20,5 A
RD = (29.2 - 22.1) / 20.5
CIRCUIT = f"""
.model ZTVS D(IS=1e-12 N=1 BV=22.1 IBV=1m RS={RD:.4f} CJO=2n)
.model SS16 D(IS=5e-6 N=1.1 RS=0.06 BV=60 IBV=0.5m CJO=150p)
D1a in t1 ZTVS
D1b 0 t1 ZTVS
VD2 in d2a 0
D2 d2a p12 SS16
* FB1: DC 0,15 Ohm, ~1 uH, bei HF resistiv (600 Ohm parallel, ungünstig hohe Güte)
RFB p12 f1 0.15
LFB f1 vin 1u
RFBhf f1 vin 600
* C1 47 uF/35 V Elko (ESR 0,3 Ohm), C6 4,7 uF/50 V mit DC-Bias ~2,5 uF, C7 100 nF
C1 vin c1n 47u IC=13.5
RC1 c1n 0 0.3
C6 vin 0 2.5u IC=13.5
C7 vin 0 100n IC=13.5
* Buck-Last ~1 W (kleine Last = ungünstig)
RL vin 0 180
"""

# Angenommenes Profil (P-03): Pulse nach ISO 7637-2, Pegel IV für 12-V-Netze.
# (Us, Ri, tr, td bis 10 %, Batteriespannung während des Pulses)
CASES = [
    ('2a  +112 V / 2 Ohm / 50 us', 112, 2.0, 1e-6, 50e-6, 13.5),
    ('2a  +112 V / 2 Ohm / 100 us', 112, 2.0, 1e-6, 100e-6, 13.5),
    ('1   -150 V / 10 Ohm / 2 ms', -150, 10.0, 1e-6, 2e-3, 0.0),
    ('3a  -220 V / 50 Ohm / 0,1 us', -220, 50.0, 5e-9, 0.1e-6, 13.5),
    ('3b  +150 V / 50 Ohm / 0,1 us', 150, 50.0, 5e-9, 0.1e-6, 13.5),
]


def integrate(t, y):
    return sum(0.5 * (y[k] + y[k + 1]) * (t[k + 1] - t[k]) for k in range(len(t) - 1))


print(f"{'Puls':30} {'V(J1)':>14} {'VIN_SYS':>14} {'UR D2':>6} {'P D1':>7} {'E D1':>9} {'E Lawine D2':>12}")
for name, us, ri, tr, td, ub in CASES:
    src = f"Vs src 0 EXP({ub} {ub + us} 0 {tr / 2.2} {tr} {td / math.log(10)})"
    step = min(tr / 5, td / 200)
    ngs.run(f"* {name}\n{src}\nRi src in {ri}\n{CIRCUIT}\n.options reltol=1e-4\n.tran {step} {max(5 * td, 20e-6)} uic\n")
    t, vs, vi, vp, vv = (ngs.vec(n) for n in ('time', 'src', 'in', 'p12', 'vin'))
    i_d2 = ngs.vec('vd2#branch')
    i_d1 = [(a - b) / ri - c for a, b, c in zip(vs, vi, i_d2)]
    p_d1 = [abs(v * i) for v, i in zip(vi, i_d1)]
    ur = [b - a for a, b in zip(vi, vp)]
    e_av = integrate(t, [u * -i if u > 50 and i < 0 else 0 for u, i in zip(ur, i_d2)])
    print(f"{name:30} {max(vi):6.1f}/{min(vi):6.1f} {max(vv):6.1f}/{min(vv):6.1f} {max(ur):6.1f} "
          f"{max(p_d1):6.0f}W {integrate(t, p_d1) * 1e3:7.1f}mJ {e_av * 1e9:9.1f}nJ")
