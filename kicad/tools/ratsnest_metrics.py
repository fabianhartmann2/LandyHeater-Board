"""Ratsnest-Kennzahlen (Schritt 4): Summe der Luftlinien (minimaler Spannbaum je Netz) und Anzahl
sich kreuzender Luftlinien verschiedener Netze. Flächennetze (GND auf L2, 3V3_CORE/VIN_SYS auf L3) zählen nicht.
Aufruf (KiCad-Python): python3 tools/ratsnest_metrics.py board_a.kicad_pcb [board_b.kicad_pcb]
"""
import sys, math, itertools
import pcbnew

PLANE = {'GND', '3V3_CORE', 'VIN_SYS'}


def edges(path):
    b = pcbnew.LoadBoard(path); mm = pcbnew.ToMM
    nets = {}
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname()
            if not n or n.startswith('unconnected') or n in PLANE: continue
            nets.setdefault(n, []).append((mm(p.GetPosition().x), mm(p.GetPosition().y)))
    out = []
    for n, pts in nets.items():
        pts = list(dict.fromkeys(pts))
        if len(pts) < 2: continue
        inside = {0}
        while len(inside) < len(pts):
            d, i, j = min((math.dist(pts[i], pts[j]), i, j) for i in inside for j in range(len(pts)) if j not in inside)
            inside.add(j); out.append((n, pts[i], pts[j], d))
    return out


def cross(a, b, c, d):
    def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def metrics(path):
    e = edges(path)
    total = sum(x[3] for x in e)
    n = sum(1 for x, y in itertools.combinations(e, 2) if x[0] != y[0] and cross(x[1], x[2], y[1], y[2]))
    return total, n, len(e)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        t, n, k = metrics(p)
        print(f'{p.split("/")[-1]}: Luftlinien {k}, Summe {t:.0f} mm, Kreuzungen {n}')
