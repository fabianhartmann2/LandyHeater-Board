"""Routing-Prüfungen, die der DRC nicht abdeckt (Schritt 6.7), und Kennzahlen für den Bericht.

- Y-03: Leiterbahnen auf L4 (B.Cu) dürfen die Teilung von L3 (VIN_SYS / 3V3_CORE, Polygone aus tools/zones.py) nicht
  kreuzen – Ausnahme: statische Diagnose-Zuleitungen 12V_PROT und VBUS_PROT (~1 mA).
- Vias unter der Knopfzelle (BT1-Courtyard): nur GND (Zellunterseite = GND).
- Vias unter dem Modulkörper U4: nur die Wärmevias des Footprints.
- Kennzahlen: Bahnlänge je Lage, Vias je Herkunft (Gruppe), spitze Winkel (< 90°) zwischen Bahnsegmenten.

Aufruf (KiCad-Python): python3 tools/check_routing.py LandyHeater.kicad_pcb
"""
import math
import os
import sys
from collections import Counter, defaultdict
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zones import VIN, V33   # noqa: E402

EXEMPT = {'12V_PROT', 'VBUS_PROT'}
mm = pcbnew.ToMM


def in_poly(x, y, poly):
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c


def region(x, y):
    return 'VIN' if in_poly(x, y, VIN) else '3V3' if in_poly(x, y, V33) else 'Spalt'


def main(path):
    b = pcbnew.LoadBoard(path)
    errs, notes = [], []
    length = Counter(); grp_of = {}
    for g in b.Groups():
        for it in g.GetItems():
            grp_of[it.m_Uuid.AsString()] = g.GetName().split(' (')[0]
    vias = Counter()
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            vias[grp_of.get(t.m_Uuid.AsString(), 'ohne Gruppe')] += 1; continue
        length[b.GetLayerName(t.GetLayer())] += mm(t.GetLength())
        if t.GetLayer() != pcbnew.B_Cu: continue
        ax, ay, bx, by = mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y)
        n = max(2, int(math.hypot(bx - ax, by - ay) / 0.1))
        regs = {region(ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n + 1)} - {'Spalt'}
        if len(regs) > 1:
            (notes if t.GetNetname() in EXEMPT else errs).append(
                f'Y-03 L3-Teilung gekreuzt: {t.GetNetname()} ({ax:.2f},{ay:.2f})-({bx:.2f},{by:.2f})')
    fp = {f.GetReference(): f for f in b.GetFootprints()}

    def box(ref, layer):
        q = [g.GetBoundingBox() for g in fp[ref].GraphicalItems() if g.GetLayer() == layer]
        return (min(mm(x.GetLeft()) for x in q), min(mm(x.GetTop()) for x in q), max(mm(x.GetRight()) for x in q), max(mm(x.GetBottom()) for x in q))
    bt1, u4 = box('BT1', pcbnew.F_CrtYd), box('U4', pcbnew.F_Fab)
    for t in b.GetTracks():
        if t.GetClass() != 'PCB_VIA': continue
        x, y = mm(t.GetPosition().x), mm(t.GetPosition().y)
        if bt1[0] <= x <= bt1[2] and bt1[1] <= y <= bt1[3] and t.GetNetname() != 'GND':
            errs.append(f'Via {t.GetNetname()} unter der Knopfzelle ({x:.2f},{y:.2f})')
        if u4[0] <= x <= u4[2] and u4[1] <= y <= u4[3]:
            errs.append(f'Via {t.GetNetname()} unter dem Modulkörper ({x:.2f},{y:.2f})')
    # spitze Winkel: zwei Segmente desselben Netzes/derselben Lage mit gemeinsamem Endpunkt und Winkel < 90°
    ends = defaultdict(list)
    for t in b.GetTracks():
        if t.GetClass() != 'PCB_TRACK': continue
        a, c = (t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)
        if a == c: continue
        ends[(t.GetLayer(), t.GetNetCode(), a)].append(c); ends[(t.GetLayer(), t.GetNetCode(), c)].append(a)
    acute = 0
    for (layer, net, p), others in ends.items():
        if len(others) != 2: continue
        v1 = (others[0][0] - p[0], others[0][1] - p[1]); v2 = (others[1][0] - p[0], others[1][1] - p[1])
        cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
        if cosang > 0.01:   # Winkel zwischen den Schenkeln < 90°
            acute += 1
            if acute <= 15: notes.append(f'spitzer Winkel: {b.GetNetsByNetcode()[net].GetNetname()} {b.GetLayerName(layer)} ({mm(p[0]):.2f},{mm(p[1]):.2f})')
    print('Bahnlänge je Lage:', ', '.join(f'{k} {v:.0f} mm' for k, v in sorted(length.items())))
    print('Vias je Herkunft:', ', '.join(f'{k} {v}' for k, v in vias.most_common()), f'(gesamt {sum(vias.values())})')
    print(f'spitze Winkel: {acute}')
    for n in notes: print('  Hinweis:', n)
    for e in errs: print('  FEHLER:', e)
    print('Ergebnis:', 'OK' if not errs else f'{len(errs)} Fehler')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
