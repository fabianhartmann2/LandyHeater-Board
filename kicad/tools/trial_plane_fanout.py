"""NUR FÜR DEN ROUTBARKEITS-PROBELAUF auf einer Kopie: setzt neben jedes SMD-Pad eines Flächennetzes ein Via
mit kurzer Verbindung (Fan-out) und legt die Probe-Ebenen an: GND auf In1.Cu, 3V3_CORE auf In2.Cu.
Freerouting 2.1.0 kann das nicht selbst (Fan-out-Routine bricht mit NullPointerException ab).

Via 0,6/0,3 mm, Leiterbahn 0,3 mm, kein Via-in-Pad, 0,2 mm Abstand zu fremden Netzen (Pads und schon gesetzte Vias),
0,3 mm zum Rand, Suchradius 1,2 mm um die Padkante.
Aufruf (KiCad-Python): python3 tools/trial_plane_fanout.py <kopie>.kicad_pcb [--l3-split | --l3-signal]
--l3-split: L3 geteilt in VIN_SYS (unten/links) und 3V3_CORE (oben).
--l3-signal: keine 3V3-Ebene; L3 bleibt Lage für Versorgung und langsame Signale, 3V3-Pads bekommen nur Vias.
"""
import sys, math
import pcbnew

PLANES = {'GND': pcbnew.In1_Cu, '3V3_CORE': pcbnew.In2_Cu}
VIA_ONLY = set()   # Netze, die nur Vias bekommen, ohne eigene Ebene (Option --l3-signal)
FULL = [(100.3, 100.3), (179.7, 100.3), (179.7, 149.7), (100.3, 149.7)]
OUTLINE = {}       # Netz -> Polygon; Standard ganze Platine
# Option --l3-split: L3 geteilt – VIN_SYS unten/links (12-V-Seite), 3V3_CORE oben (Last), 0,4 mm Trennspalt
SPLIT = {
    'VIN_SYS': [(100.3, 116.0), (109.3, 116.0), (109.3, 124.6), (121.0, 124.6), (121.0, 131.0), (179.7, 131.0), (179.7, 149.7), (100.3, 149.7)],
    '3V3_CORE': [(100.3, 100.3), (179.7, 100.3), (179.7, 130.6), (121.4, 130.6), (121.4, 124.2), (109.7, 124.2), (109.7, 115.6), (100.3, 115.6)],
}
VIA_D, DRILL, W, CLR, SEARCH = 0.6, 0.3, 0.3, 0.2, 1.2
BOARD = (100.0, 100.0, 180.0, 150.0)


def main(path):
    b = pcbnew.LoadBoard(path); mm, fm = pcbnew.ToMM, pcbnew.FromMM
    # Probe-Ebenen
    for net, layer in PLANES.items():
        if net in VIA_ONLY: continue
        if any(z.GetLayer() == layer and z.GetNetname() == net for z in b.Zones()):
            continue
        b.SetLayerType(layer, pcbnew.LT_POWER)
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet(net))
        o = z.Outline(); o.NewOutline()
        for x, y in OUTLINE.get(net, FULL):
            o.Append(fm(x), fm(y))
        z.SetLocalClearance(fm(0.2)); z.SetMinThickness(fm(0.2)); b.Add(z)
    pads = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu): continue
            bb = p.GetBoundingBox()
            pads.append((f.GetReference(), p, p.GetNetname(),
                         (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())), p.GetDrillSize().x > 0))

    def drect(x, y, r):
        return math.hypot(min(max(x, r[0]), r[2]) - x, min(max(y, r[1]), r[3]) - y)

    vias = []          # (x, y, net)
    placed, failed, viapad = 0, [], []
    for ref, p, net, r, tht in pads:
        if net not in PLANES or tht: continue
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2

        def seg_ok(x1, y1, x2, y2, w=W, target=None):
            for _, _, n2, r2, _ in pads:
                if r2 is r or r2 is target or n2 == net: continue
                for k in range(0, 21):
                    t = k / 20; px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                    if drect(px, py, r2) < w / 2 + CLR: return False
            return True

        def search(sx, sy):
            best = None
            for j in range(int((r[3] - r[1] + 2 * SEARCH) / 0.1) + 1):
                for i in range(int((r[2] - r[0] + 2 * SEARCH) / 0.1) + 1):
                    x, y = r[0] - SEARCH + i * 0.1, r[1] - SEARCH + j * 0.1
                    if not (BOARD[0] + 0.3 + VIA_D / 2 <= x <= BOARD[2] - 0.3 - VIA_D / 2 and BOARD[1] + 0.3 + VIA_D / 2 <= y <= BOARD[3] - 0.3 - VIA_D / 2):
                        continue
                    d0 = drect(x, y, r)
                    if d0 < VIA_D / 2 + 0.1: continue                         # kein Via-in-Pad
                    if any(r2 is not r and drect(x, y, r2) < VIA_D / 2 + (0.1 if n2 == net else CLR) for _, _, n2, r2, _ in pads):
                        continue
                    if any(math.hypot(x - vx, y - vy) < VIA_D + (0.05 if vn == net else CLR) for vx, vy, vn in vias):
                        continue
                    if best is not None and d0 >= best[0]: continue
                    if seg_ok(sx, sy, x, y): best = (d0, x, y)
            return best

        route = None
        best = search(cx, cy)
        if best is not None:
            route = [(cx, cy), (best[1], best[2])]
        else:
            # L-förmiger Ausstieg: erst senkrecht aus dem Pin heraus, dann zum Via
            hw, hh = (r[2] - r[0]) / 2, (r[3] - r[1]) / 2
            for dx, dy in [(hw + 0.45, 0), (-hw - 0.45, 0), (0, hh + 0.45), (0, -hh - 0.45)]:
                ex, ey = cx + dx, cy + dy
                if not seg_ok(cx, cy, ex, ey): continue
                best = search(ex, ey)
                if best is not None:
                    route = [(cx, cy), (ex, ey), (best[1], best[2])]; break
        if route is None:
            # Innenpins von Feinraster-ICs: zum benachbarten Pad desselben Netzes (Abblockkondensator mit Via),
            # vgl. TPS25947 8.4.1 (Rückführung der Hilfsbauteile zum GND-Pin)
            cands = sorted((math.hypot((r2[0] + r2[2]) / 2 - cx, (r2[1] + r2[3]) / 2 - cy), r2, p2) for _, p2, n2, r2, _ in pads
                           if n2 == net and r2 is not r and p2.GetParentFootprint().GetReference() != ref)
            for d, r2, p2 in cands:
                if d > 3.0: break
                tx, ty = (r2[0] + r2[2]) / 2, (r2[1] + r2[3]) / 2
                if seg_ok(cx, cy, tx, ty, 0.2, r2):
                    t = pcbnew.PCB_TRACK(b); t.SetStart(p.GetPosition()); t.SetEnd(p2.GetPosition())
                    t.SetWidth(fm(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(p.GetNet()); b.Add(t)
                    viapad.append(f'{ref}.{p.GetNumber()} -> {p2.GetParentFootprint().GetReference()}.{p2.GetNumber()}'); break
                hw, hh = (r[2] - r[0]) / 2, (r[3] - r[1]) / 2
                done_ = False
                for dx, dy in [(hw + 0.45, 0), (-hw - 0.45, 0), (0, hh + 0.45), (0, -hh - 0.45)]:
                    ex, ey = cx + dx, cy + dy
                    if seg_ok(cx, cy, ex, ey, 0.2) and seg_ok(ex, ey, tx, ty, 0.2, r2):
                        for (x1, y1), (x2, y2) in [((cx, cy), (ex, ey)), ((ex, ey), (tx, ty))]:
                            t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(fm(x1), fm(y1))); t.SetEnd(pcbnew.VECTOR2I(fm(x2), fm(y2)))
                            t.SetWidth(fm(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(p.GetNet()); b.Add(t)
                        viapad.append(f'{ref}.{p.GetNumber()} -> {p2.GetParentFootprint().GetReference()}.{p2.GetNumber()} (L)'); done_ = True; break
                if done_: break
            else:
                failed.append(f'{ref}.{p.GetNumber()} ({net})')
            continue
        x, y = route[-1]
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(fm(x), fm(y))); v.SetWidth(fm(VIA_D)); v.SetDrill(fm(DRILL))
        v.SetNet(p.GetNet()); b.Add(v)
        for (x1, y1), (x2, y2) in zip(route, route[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(fm(x1), fm(y1))); t.SetEnd(pcbnew.VECTOR2I(fm(x2), fm(y2)))
            t.SetWidth(fm(W if len(route) == 2 else 0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(p.GetNet()); b.Add(t)
        vias.append((x, y, net)); placed += 1
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(path)
    print(f'Fan-out-Vias gesetzt: {placed}; ohne Platz: {len(failed)}')
    for f in failed: print('  ', f)
    print(f'über Nachbarpad angebunden: {len(viapad)}')
    for f in viapad: print('  ', f)


if __name__ == '__main__':
    if '--l3-split' in sys.argv:
        PLANES['VIN_SYS'] = pcbnew.In2_Cu; OUTLINE.update(SPLIT)
    if '--l3-signal' in sys.argv:   # L3 bleibt Signal-/Versorgungslage wie im echten Lagenaufbau (Y-02)
        VIA_ONLY.add('3V3_CORE')
    main(sys.argv[1])
