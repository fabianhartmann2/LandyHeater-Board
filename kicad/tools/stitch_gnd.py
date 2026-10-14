"""GND-Heftvias (Schritt 6.7): verbinden die GND-Füllungen auf L1 und L4 mit der GND-Ebene L2 und verkürzen Rückstrompfade.

- Raster 3 mm, dazu ein Ring 1,2 mm innerhalb der Platinenkante (Abstand 3 mm).
- Ein Via wird nur gesetzt, wo die gefüllte GND-Fläche auf L1 UND auf L4 den ganzen Via-Umfang (Radius 0,3 mm
  + 0,25 mm Rand) enthält – damit hält es automatisch den Abstand zu allem anderen Kupfer ein.
- Nicht unter dem Modulkörper U4 und nicht in Sperrflächen; 1,0 mm Abstand zu vorhandenen Vias.
Vorher müssen die Außenlagen gefüllt sein (tools/zones.py … --fill-all); danach wird erneut gefüllt.

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/stitch_gnd.py LandyHeater.kicad_pcb
"""
import math
import os
import subprocess
import sys
import pcbnew

GROUP = 'GND-Heftvias (tools/stitch_gnd.py)'
PITCH, RING, VIA_D, DRILL, MARGIN, MIN_VIA_DIST = 3.0, 1.2, 0.6, 0.3, 0.25, 1.0
fm, mm = pcbnew.FromMM, pcbnew.ToMM


def main(path):
    b = pcbnew.LoadBoard(path)
    old = [g for g in b.Groups() if g.GetName() == GROUP]
    if old:
        for it in [it for g in old for it in g.GetItems()] + old:
            b.Remove(it)
        b.Save(path); sys.stdout.flush()
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zones.py'), path, '--fill-stage', '--fill-all'], check=True)
        os.execv(sys.executable, [sys.executable, os.path.abspath(__file__), path])
    fills = {}
    for z in b.Zones():
        if z.GetZoneName() in ('GND L1', 'GND L4'):
            fills[z.GetZoneName()] = z.GetFilledPolysList(z.GetLayer())
    if len(fills) != 2 or any(f.OutlineCount() == 0 for f in fills.values()):
        sys.exit('Außenlagen nicht gefüllt – zuerst tools/zones.py <board> --fill-all')
    q = [g.GetBoundingBox() for f in b.GetFootprints() if f.GetReference() == 'U4' for g in f.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab]
    u4 = (min(mm(x.GetLeft()) for x in q), min(mm(x.GetTop()) for x in q), max(mm(x.GetRight()) for x in q), max(mm(x.GetBottom()) for x in q))
    keep = [z.GetBoundingBox() for z in b.Zones() if z.GetIsRuleArea()]
    vias = [(mm(v.GetPosition().x), mm(v.GetPosition().y)) for v in b.GetTracks() if v.GetClass() == 'PCB_VIA']
    vias += [(mm(p.GetPosition().x), mm(p.GetPosition().y)) for f in b.GetFootprints() for p in f.Pads() if p.GetDrillSize().x > 0]

    cand = []
    x = 100.0 + RING
    while x <= 180.0 - RING + 1e-6:             # Ring entlang der Kante
        cand += [(x, 100.0 + RING), (x, 150.0 - RING)]; x += PITCH
    y = 100.0 + RING + PITCH
    while y <= 150.0 - RING - PITCH + 1e-6:
        cand += [(100.0 + RING, y), (180.0 - RING, y)]; y += PITCH
    for i in range(1, int(80 / PITCH)):
        for j in range(1, int(50 / PITCH)):
            cand.append((100.0 + i * PITCH, 100.0 + j * PITCH))

    def inside_all(x, y):
        r = VIA_D / 2 + MARGIN
        pts = [(x, y)] + [(x + r * math.cos(a * math.pi / 4), y + r * math.sin(a * math.pi / 4)) for a in range(8)]
        return all(f.Contains(pcbnew.VECTOR2I(fm(px), fm(py))) for f in fills.values() for px, py in pts)

    grp = pcbnew.PCB_GROUP(b); grp.SetName(GROUP); b.Add(grp)
    gnd = b.FindNet('GND'); n = 0
    for x, y in cand:
        if u4[0] - 0.5 <= x <= u4[2] + 0.5 and u4[1] - 0.5 <= y <= u4[3] + 0.5: continue
        if any(k.Contains(pcbnew.VECTOR2I(fm(x), fm(y))) for k in keep): continue
        if any(math.hypot(x - vx, y - vy) < MIN_VIA_DIST for vx, vy in vias): continue
        if not inside_all(x, y): continue
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(fm(x), fm(y))); v.SetWidth(fm(VIA_D)); v.SetDrill(fm(DRILL))
        v.SetNet(gnd); b.Add(v); grp.AddItem(v); vias.append((x, y)); n += 1
    b.Save(path)
    print(f'GND-Heftvias: {n} von {len(cand)} Rasterpunkten', flush=True)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zones.py'), path, '--fill-stage', '--fill-all'], check=True)
    os._exit(0)


if __name__ == '__main__':
    main(sys.argv[1])
