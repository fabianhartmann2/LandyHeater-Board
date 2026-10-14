"""Kupferflächen nach Y-02 und Routbarkeits-Probelauf 9 (Platzierung_2_Bericht.md, Abschnitt 10).

- In1.Cu (L2): GND, ganze Platine, ungeteilt.
- In2.Cu (L3): geteilt – VIN_SYS unten/links (12-V-Seite: FB1 → Schaltregler, F1, D4), 3V3_CORE oben (Last),
  0,4 mm Trennspalt. Über den Spalt laufen auf L4 nur statische Gleichspannungsleitungen (Diagnose).
- F.Cu (L1) und B.Cu (L4): GND-Füllung um die Leiterbahnen.
Vorhandene Flächen mit gleichem Namen werden ersetzt.
Aufruf (KiCad-Python): python3 tools/zones.py LandyHeater.kicad_pcb [--fill-all]
Ohne --fill-all werden nur die Innenlagen gefüllt (Routing-Phase); --fill-all füllt auch L1/L4 (nach dem Routing).
"""
import sys
import pcbnew

FULL = [(100.3, 100.3), (179.7, 100.3), (179.7, 149.7), (100.3, 149.7)]
VIN = [(100.3, 116.0), (109.3, 116.0), (109.3, 124.6), (121.0, 124.6), (121.0, 131.0), (179.7, 131.0), (179.7, 149.7), (100.3, 149.7)]
V33 = [(100.3, 100.3), (179.7, 100.3), (179.7, 130.6), (121.4, 130.6), (121.4, 124.2), (109.7, 124.2), (109.7, 115.6), (100.3, 115.6)]
ZONES = [  # Name, Lage, Netz, Polygon, Priorität
    ('GND L2', pcbnew.In1_Cu, 'GND', FULL, 0),
    ('VIN_SYS L3', pcbnew.In2_Cu, 'VIN_SYS', VIN, 1),
    ('3V3 L3', pcbnew.In2_Cu, '3V3_CORE', V33, 1),
    ('GND L1', pcbnew.F_Cu, 'GND', FULL, 0),
    ('GND L4', pcbnew.B_Cu, 'GND', FULL, 0),
]


def main(path):
    b = pcbnew.LoadBoard(path); fm = pcbnew.FromMM
    names = {z[0] for z in ZONES}
    for z in list(b.Zones()):
        if not z.GetIsRuleArea() and z.GetZoneName() in names:
            b.Remove(z)
    b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)
    for name, layer, net, poly, prio in ZONES:
        z = pcbnew.ZONE(b); z.SetZoneName(name); z.SetLayer(layer); z.SetNet(b.FindNet(net)); z.SetAssignedPriority(prio)
        z.SetLocalClearance(fm(0.25 if layer in (pcbnew.F_Cu, pcbnew.B_Cu) else 0.2))
        z.SetMinThickness(fm(0.2)); z.SetThermalReliefGap(fm(0.3)); z.SetThermalReliefSpokeWidth(fm(0.4))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for x, y in poly: ps.Append(fm(x), fm(y))
        z.SetOutline(ps); ps.thisown = 0   # Zone übernimmt das Polygon (sonst gibt Python es frei -> Absturz)
        b.Add(z)
    b.Save(path)
    # Füllen in einem eigenen Prozess: nach b.Remove() ist die SWIG-Typzuordnung im laufenden Prozess gestört
    import subprocess
    subprocess.run([sys.executable, __file__, path, '--fill-stage'] + (['--fill-all'] if '--fill-all' in sys.argv else []), check=True)
    print('Flächen:', ', '.join(f'{z[0]} ({z[2]})' for z in ZONES), flush=True)
    import os; os._exit(0)   # Python-Aufräumen würde Objekte freigeben, die dem Board gehören (Absturz beim Beenden)


def fill(path, fill_all):
    b = pcbnew.LoadBoard(path)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    if not fill_all:   # Außenlagen erst nach dem Routing füllen (sonst blockieren sie Leiterbahnen)
        for z in b.Zones():
            if not z.GetIsRuleArea() and z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu):
                z.UnFill()
    b.Save(path)


if __name__ == '__main__':
    if '--fill-stage' in sys.argv:
        fill(sys.argv[1], '--fill-all' in sys.argv)
    else:
        main(sys.argv[1])
