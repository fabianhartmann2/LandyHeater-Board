"""Machbarkeit der Flächenanbindung (Schritt 5): Hat jedes Pad eines Flächennetzes Platz für ein eigenes Via
in seiner Nähe? Flächennetze: GND (L2), 3V3_CORE und VIN_SYS (L3).

Via 0,6/0,3 mm (Netzklasse Default), kein Via-in-Pad; Abstand 0,2 mm zu Kupfer anderer Netze, 0,1 mm zu Pads
des eigenen Netzes und 0,3 mm zum Rand,
Suchradius 1,2 mm um die Padkante. Vias unter Bauteilkörpern (zwischen Pads) sind zulässig.
Aufruf (KiCad-Python): python3 tools/check_plane_vias.py LandyHeater.kicad_pcb
"""
import sys, math
import pcbnew

PLANE = {'GND', '3V3_CORE', 'VIN_SYS'}
VIA_R = 0.3
CLR = 0.2
SEARCH = 1.2
BOARD = (100.0, 100.0, 180.0, 150.0)


def main(path):
    b = pcbnew.LoadBoard(path); mm = pcbnew.ToMM
    pads = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu): continue
            bb = p.GetBoundingBox()
            pads.append((f.GetReference(), p.GetNumber(), p.GetNetname(),
                         (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())),
                         p.GetDrillSize().x > 0))

    def dist_rect(x, y, r):
        return math.hypot(min(max(x, r[0]), r[2]) - x, min(max(y, r[1]), r[3]) - y)

    fail, ok = [], 0
    for ref, num, net, r, tht in pads:
        if net not in PLANE or tht: continue          # THT-Pads erreichen die Innenlagen selbst
        found = False
        x0, y0, x1, y1 = r[0] - SEARCH, r[1] - SEARCH, r[2] + SEARCH, r[3] + SEARCH
        steps = 0.1
        xs = [x0 + i * steps for i in range(int((x1 - x0) / steps) + 1)]
        ys = [y0 + j * steps for j in range(int((y1 - y0) / steps) + 1)]
        for y in ys:
            for x in xs:
                if not (BOARD[0] + 0.3 + VIA_R <= x <= BOARD[2] - 0.3 - VIA_R and BOARD[1] + 0.3 + VIA_R <= y <= BOARD[3] - 0.3 - VIA_R):
                    continue
                # kein Via-in-Pad: zu Pads desselben Netzes 0,1 mm Luft, zu anderen Netzen 0,2 mm
                if all(dist_rect(x, y, r2) >= VIA_R + (0.1 if n2 == net else CLR) for _, _, n2, r2, _ in pads):
                    found = True; break
            if found: break
        if found: ok += 1
        else: fail.append(f'{ref}.{num} ({net})')
    print(f'Pads mit Via-Platz: {ok}; ohne: {len(fail)}')
    for f in fail: print('  kein Via-Platz:', f)
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
