"""Flächenanbindung (Schritt 6.4): jedes SMD-Pad eines Flächennetzes, das noch keine Verbindung zu seiner Ebene
hat, bekommt ein eigenes Via mit kurzer Leiterbahn.

Ebenen: GND → L2 (In1.Cu, ganz), 3V3_CORE und VIN_SYS → L3 (In2.Cu, geteilt, Polygone aus tools/zones.py).
- Via 0,6/0,3 mm, kein Via-in-Pad (0,1 mm Luft zu Pads des eigenen Netzes), 0,2 mm zu fremdem Kupfer
  (Pads, Leiterbahnen aller Lagen, Vias, Handrouting-Flächen „R: …"), 0,5 mm zum Rand.
- L3-Teilung: 3V3- bzw. VIN-Vias nur innerhalb ihrer L3-Teilfläche (0,5 mm Abstand zur Polygongrenze).
- Sperrbereiche: Passermarken-Sperrflächen, Modulkörper U4 (Antenne/Unterseite, Espressif), Knopfzelle BT1
  (Courtyard): dort nur GND-Vias – die Zellunterseite ist GND, ein fremdes Via unter der Zelle wäre ein Kurzschlussrisiko.
- Bahnbreite 0,3 mm (bei schmalen Pads 0,25 mm); gerader Weg, sonst L-förmiger Ausstieg aus dem Pad.
Die Pads werden nach Netz-Zusammenhang geprüft (Pad hängt schon über Leiterbahn/Fläche an einem Via → übersprungen).

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/route_planevias.py LandyHeater.kicad_pcb
"""
import math
import os
import sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zones import VIN, V33   # noqa: E402  L3-Teilflächen

GROUP = 'Flächenvias (tools/route_planevias.py)'
PLANE = {'GND': pcbnew.In1_Cu, '3V3_CORE': pcbnew.In2_Cu, 'VIN_SYS': pcbnew.In2_Cu}
L3POLY = {'3V3_CORE': V33, 'VIN_SYS': VIN}
VIA_D, DRILL, CLR, SAME = 0.6, 0.3, 0.2, 0.1
BOARD = (100.0, 100.0, 180.0, 150.0)
SEARCH = {'BT1': 2.5}   # Zellkontakt: Via am Padrand unter der Zelle
NO_VIA_BODY = {'U4'}     # Modulkörper (F.Fab)
GND_ONLY = {'BT1'}       # Courtyard: nur GND-Vias


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def seg_seg(a, b, c, d):
    def inter(p1, p2, p3, p4):
        def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return (o(p1, p2, p3) * o(p1, p2, p4) < 0) and (o(p3, p4, p1) * o(p3, p4, p2) < 0)
    if inter(a, b, c, d): return 0.0
    return min(seg_dist(*a, *c, *d), seg_dist(*b, *c, *d), seg_dist(*c, *a, *b), seg_dist(*d, *a, *b))


def rect_dist(x, y, r):
    return math.hypot(min(max(x, r[0]), r[2]) - x, min(max(y, r[1]), r[3]) - y)


def seg_rect(a, b, r):
    if r[0] <= a[0] <= r[2] and r[1] <= a[1] <= r[3]: return 0.0
    cs = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    return min(seg_seg(a, b, cs[i], cs[(i + 1) % 4]) for i in range(4))


def in_poly(x, y, poly):
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): inside = not inside
    return inside


def poly_edge_dist(x, y, poly):
    return min(seg_dist(x, y, *p, *q) for p, q in zip(poly, poly[1:] + poly[:1]))


def main(path):
    b = pcbnew.LoadBoard(path); mm, fm = pcbnew.ToMM, pcbnew.FromMM
    old = [g for g in b.Groups() if g.GetName() == GROUP]
    if old:   # Entfernen, speichern, neu starten (SWIG verliert nach BOARD.Remove() die Typen)
        for it in [it for g in old for it in g.GetItems()] + old:
            b.Remove(it)
        b.Save(path); sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, os.path.abspath(__file__), path])
    b.BuildConnectivity(); conn = b.GetConnectivity()

    def bbox(q): return (mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom()))
    pads, todo = [], []
    for f in b.GetFootprints():
        for p in f.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu): continue
            pads.append((p.GetNetname(), bbox(p.GetBoundingBox()), p))
            n = p.GetNetname()
            if n in PLANE and p.GetDrillSize().x == 0:
                items = conn.GetConnectedItems(p)
                if not any(it.GetClass() == 'PCB_VIA' or (it.GetClass() == 'ZONE' and it.GetLayer() == PLANE[n]) for it in items):
                    todo.append((f.GetReference(), p))
    # Leiterbahnen auf F.Cu (für die Anbindungsbahn) und auf allen Lagen (ein Via durchdringt alle Lagen)
    tracks_all = [(t.GetNetname(), (mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y)), mm(t.GetWidth()),
                   t.GetLayer()) for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
    tracks = [t[:4] for t in tracks_all if t[4] == pcbnew.F_Cu]
    vias = [(v.GetNetname(), mm(v.GetPosition().x), mm(v.GetPosition().y), mm(v.GetWidth(pcbnew.F_Cu)))
            for v in b.GetTracks() if v.GetClass() == 'PCB_VIA']
    rzones = []   # Handrouting-Flächen auf F.Cu: (Netz, Polygon)
    for z in b.Zones():
        if z.GetZoneName().startswith('R: ') and z.GetLayer() == pcbnew.F_Cu:
            o = z.Outline().Outline(0)
            rzones.append((z.GetNetname(), [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())]))
    keep = []   # (Rechteck, nur GND erlaubt?)
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowVias(): keep.append((bbox(z.GetBoundingBox()), False))
    for f in b.GetFootprints():
        r = f.GetReference()
        if r in NO_VIA_BODY or r in GND_ONLY:
            L = pcbnew.F_Fab if r in NO_VIA_BODY else pcbnew.F_CrtYd
            q = [g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() == L]
            keep.append(((min(mm(x.GetLeft()) for x in q), min(mm(x.GetTop()) for x in q),
                          max(mm(x.GetRight()) for x in q), max(mm(x.GetBottom()) for x in q)), r in GND_ONLY))

    def via_ok(x, y, net, own):
        R = VIA_D / 2
        if not (BOARD[0] + 0.5 + R <= x <= BOARD[2] - 0.5 - R and BOARD[1] + 0.5 + R <= y <= BOARD[3] - 0.5 - R): return False
        for r, gnd_ok in keep:
            if r[0] - R <= x <= r[2] + R and r[1] - R <= y <= r[3] + R and not (gnd_ok and net == 'GND'): return False
        if net in L3POLY and not (in_poly(x, y, L3POLY[net]) and poly_edge_dist(x, y, L3POLY[net]) >= 0.5): return False
        for n2, r2, p2 in pads:
            if rect_dist(x, y, r2) < R + (SAME if n2 == net else CLR): return False
        for n2, a, c, w, _ in tracks_all:
            if n2 != net and seg_dist(x, y, *a, *c) < R + w / 2 + CLR: return False
        for n2, vx, vy, vd in vias:
            if math.hypot(x - vx, y - vy) < R + vd / 2 + (0.15 if n2 == net else CLR): return False
        for n2, poly in rzones:
            if n2 != net and (in_poly(x, y, poly) or poly_edge_dist(x, y, poly) < R + CLR): return False
        return True

    def seg_ok(a, c, w, net, own):
        for n2, r2, p2 in pads:
            if p2 is own or n2 == net: continue
            if seg_rect(a, c, r2) < w / 2 + CLR: return False
        for n2, s1, s2, w2 in tracks:
            if n2 != net and seg_seg(a, c, s1, s2) < w / 2 + w2 / 2 + CLR: return False
        for n2, vx, vy, vd in vias:
            if n2 != net and seg_dist(vx, vy, *a, *c) < w / 2 + vd / 2 + CLR: return False
        for n2, poly in rzones:
            if n2 != net and (in_poly(*a, poly) or in_poly(*c, poly) or
                              min(seg_seg(a, c, p, q) for p, q in zip(poly, poly[1:] + poly[:1])) < w / 2 + CLR): return False
        return True

    grp = pcbnew.PCB_GROUP(b); grp.SetName(GROUP); b.Add(grp)
    P = lambda x, y: pcbnew.VECTOR2I(fm(x), fm(y))
    placed, failed = [], []
    for ref, p in sorted(todo, key=lambda t: (t[0], t[1].GetNumber())):
        net = p.GetNetname(); r = bbox(p.GetBoundingBox()); cx, cy = mm(p.GetPosition().x), mm(p.GetPosition().y)
        w = 0.3 if min(r[2] - r[0], r[3] - r[1]) >= 0.5 else 0.25
        s = SEARCH.get(ref, 1.2)
        cand = []
        for j in range(int((r[3] - r[1] + 2 * s) / 0.1) + 1):
            for i in range(int((r[2] - r[0] + 2 * s) / 0.1) + 1):
                x, y = round(r[0] - s + i * 0.1, 2), round(r[1] - s + j * 0.1, 2)
                d0 = rect_dist(x, y, r)
                if d0 < VIA_D / 2 + SAME: continue
                cand.append((d0, x, y))
        cand.sort()
        route = None
        exits = [(cx, cy)]
        hw, hh = (r[2] - r[0]) / 2, (r[3] - r[1]) / 2
        for d0, x, y in cand:
            if not via_ok(x, y, net, p): continue
            # Bahn vom Padrand-nächsten Punkt (im Pad) zum Via
            sx, sy = min(max(x, r[0] + w / 2), r[2] - w / 2), min(max(y, r[1] + w / 2), r[3] - w / 2)
            if r[2] - r[0] < w: sx = cx
            if r[3] - r[1] < w: sy = cy
            if p.GetShape() not in (pcbnew.PAD_SHAPE_RECTANGLE, pcbnew.PAD_SHAPE_ROUNDRECT): sx, sy = cx, cy   # runde Pads: aus der Mitte
            if seg_ok((sx, sy), (x, y), w, net, p):
                route = [(sx, sy), (x, y)]; break
        if route is None:
            for ex, ey in [(cx + hw + 0.45, cy), (cx - hw - 0.45, cy), (cx, cy + hh + 0.45), (cx, cy - hh - 0.45)]:
                if not seg_ok((cx, cy), (ex, ey), 0.25, net, p): continue
                for d0, x, y in sorted(cand, key=lambda c: math.hypot(c[1] - ex, c[2] - ey)):
                    if math.hypot(x - ex, y - ey) > 1.5: break
                    if via_ok(x, y, net, p) and seg_ok((ex, ey), (x, y), 0.25, net, p):
                        route = [(cx, cy), (ex, ey), (x, y)]; w = 0.25; break
                if route: break
        if route is None:
            failed.append((ref, p)); continue
        x, y = route[-1]
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(fm(VIA_D)); v.SetDrill(fm(DRILL)); v.SetNet(p.GetNet())
        b.Add(v); grp.AddItem(v); vias.append((net, x, y, VIA_D))
        for a, c in zip(route, route[1:]):
            if math.hypot(a[0] - c[0], a[1] - c[1]) < 1e-3: continue
            t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(fm(w)); t.SetLayer(pcbnew.F_Cu)
            t.SetNet(p.GetNet()); b.Add(t); grp.AddItem(t); tracks.append((net, a, c, w)); tracks_all.append((net, a, c, w, pcbnew.F_Cu))
        placed.append(f'{ref}.{p.GetNumber()}')
    # ohne eigenes Via, aber über eine Leiterbahn an einem Pad mit (neuem) Via angebunden → in Ordnung
    b.BuildConnectivity(); conn = b.GetConnectivity()
    failed = [f'{ref}.{p.GetNumber()} ({p.GetNetname()})' for ref, p in failed
              if not any(it.GetClass() == 'PCB_VIA' or (it.GetClass() == 'ZONE' and it.GetLayer() == PLANE[p.GetNetname()])
                         for it in conn.GetConnectedItems(p))]
    b.Save(path)
    print(f'Flächenvias: {len(placed)} gesetzt, {len(failed)} ohne Anbindung')
    for f_ in failed: print('   ohne Anbindung:', f_)
    sys.stdout.flush()
    import subprocess
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zones.py'), path, '--fill-stage'], check=True)
    os._exit(0)


if __name__ == '__main__':
    main(sys.argv[1])
