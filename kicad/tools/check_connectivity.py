"""Unabhängige Verbindungsprüfung (Schritt 6, Abnahme): Kurzschlüsse und Fehlverdrahtung allein aus der Kupfergeometrie.

1. Kupfer-Zusammenhang ohne Netzzuordnung: alle Kupferelemente (Pads, Leiterbahnen, Bögen, Vias, gefüllte Flächen –
   jede Insel einzeln) je Lage; zwei Elemente gehören zusammen, wenn sich ihre Kupferformen berühren. Vias und
   durchkontaktierte Pads verbinden ihre Lagen. Ergebnis: Gruppen physikalisch verbundener Pads.
2. Vergleich mit der Netzliste aus dem SCHALTPLAN (kicad-cli sch export netlist), nicht mit den Netznamen der Platine:
   - jede Kupfergruppe darf Pads nur EINES Schaltplannetzes enthalten (sonst Kurzschluss),
   - alle Pads eines Schaltplannetzes müssen in EINER Kupfergruppe liegen (sonst Unterbrechung),
   - jedes Pad muss im Schaltplan dem gleichen Bauteilpin entsprechen (Footprint-/Pinzuordnung).

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/check_connectivity.py LandyHeater.kicad_pcb
"""
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
import pcbnew

CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]


def schematic_netlist(sch):
    out = os.path.join(tempfile.mkdtemp(), 'n.xml')
    subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', out, sch], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pin2net = {}
    for net in ET.parse(out).getroot().iter('net'):
        for node in net.iter('node'):
            pin2net[(node.get('ref'), node.get('pin'))] = net.get('name')
    return pin2net


def main(path):
    sch = os.path.splitext(path)[0] + '.kicad_sch'
    pin2net = schematic_netlist(sch)
    b = pcbnew.LoadBoard(path)

    # Kupferelemente: (Schlüssel, Lage, Form, Umriss)
    items = []          # (owner_id, layer, shape, bbox)
    pad_of = {}         # owner_id -> (ref, pin)
    owner = 0

    def add(shape, layer, oid):
        bb = shape.BBox(); items.append((oid, layer, shape, (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))

    for f in b.GetFootprints():
        for p in f.Pads():
            owner += 1
            pad_of[owner] = (f.GetReference(), p.GetNumber())
            for L in CU:
                if p.IsOnLayer(L) and (p.GetDrillSize().x == 0 or p.FlashLayer(L)):
                    add(p.GetEffectiveShape(L), L, owner)
            if p.GetDrillSize().x > 0 and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                for L in CU: add(p.GetEffectiveHoleShape(), L, owner)   # Hülse verbindet alle Lagen
    for t in b.GetTracks():
        owner += 1
        if t.GetClass() == 'PCB_VIA':
            for L in CU: add(t.GetEffectiveShape(L), L, owner)
        else:
            add(t.GetEffectiveShape(), t.GetLayer(), owner)
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        for L in CU:
            if not z.IsOnLayer(L): continue
            fill = z.GetFilledPolysList(L)
            for k in range(fill.OutlineCount()):
                owner += 1
                ps = pcbnew.SHAPE_POLY_SET(); ps.AddOutline(fill.Outline(k))
                for h in range(fill.HoleCount(k)): ps.AddHole(fill.Hole(k, h))
                items.append((owner, L, ps, (ps.BBox().GetLeft(), ps.BBox().GetTop(), ps.BBox().GetRight(), ps.BBox().GetBottom())))

    parent = list(range(owner + 1))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    def union(a, c):
        ra, rc = find(a), find(c)
        if ra != rc: parent[ra] = rc

    # Berührung je Lage, Kandidaten über ein Raster (2 mm)
    CELL = pcbnew.FromMM(2.0)
    for L in CU:
        grid = defaultdict(list)
        lay = [it for it in items if it[1] == L]
        for idx, (oid, _, sh, bb) in enumerate(lay):
            for gx in range(bb[0] // CELL, bb[2] // CELL + 1):
                for gy in range(bb[1] // CELL, bb[3] // CELL + 1):
                    grid[(gx, gy)].append(idx)
        done = set()
        for cell in grid.values():
            for i in range(len(cell)):
                for j in range(i + 1, len(cell)):
                    a, c = cell[i], cell[j]
                    if (a, c) in done: continue
                    done.add((a, c))
                    oa, _, sa, ba = lay[a]; oc, _, sc, bc = lay[c]
                    if find(oa) == find(oc): continue
                    if ba[2] < bc[0] or bc[2] < ba[0] or ba[3] < bc[1] or bc[3] < ba[1]: continue
                    if isinstance(sa, pcbnew.SHAPE_POLY_SET):
                        hit = sa.Collide(sc, 0) if not isinstance(sc, pcbnew.SHAPE_POLY_SET) else sc.Collide(sa.Outline(0), 0)
                    else:
                        hit = sc.Collide(sa, 0) if isinstance(sc, pcbnew.SHAPE_POLY_SET) else sa.Collide(sc, 0)
                    if hit: union(oa, oc)

    groups = defaultdict(set)          # Kupfergruppe -> Schaltplannetze
    net_groups = defaultdict(set)      # Schaltplannetz -> Kupfergruppen
    missing = []
    for oid, (ref, pin) in pad_of.items():
        net = pin2net.get((ref, pin))
        if net is None:
            if (ref, pin) not in pin2net and not ref.startswith(('H', 'FID')) and pin != '':
                missing.append(f'{ref}.{pin}')
            continue
        if net.startswith('unconnected-'): continue
        g = find(oid); groups[g].add(net); net_groups[net].add(g)
    shorts = [sorted(n) for n in groups.values() if len(n) > 1]
    opens = [n for n, g in net_groups.items() if len(g) > 1]
    sch_pins = {k for k, v in pin2net.items() if not v.startswith('unconnected-')}
    brd_pins = set(pad_of.values())
    not_on_board = sorted(f'{r}.{p}' for r, p in sch_pins - brd_pins)
    print(f'Kupferelemente: {len(items)}, Pads: {len(pad_of)}, Schaltplannetze: {len(net_groups)}')
    print(f'Kurzschlüsse (Kupfergruppe mit mehreren Netzen): {len(shorts)}')
    for s in shorts[:20]: print('   ', ' + '.join(s))
    print(f'Unterbrechungen (Netz auf mehrere Kupfergruppen verteilt): {len(opens)}')
    for n in opens[:20]: print('   ', n)
    print(f'Schaltplanpins ohne Pad auf der Platine: {len(not_on_board)}', ' '.join(not_on_board[:20]))
    print(f'Pads ohne Schaltplanpin: {len(missing)}', ' '.join(missing[:20]))
    ok = not shorts and not opens and not not_on_board and not missing
    print('Ergebnis:', 'OK – Kupfer entspricht exakt dem Schaltplan' if ok else 'FEHLER')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
