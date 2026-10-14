"""Hilfswerkzeug für die Nacharbeit (Schritt 6.6): Labyrinth-Router (A*, 0,1-mm-Raster, L1/L4, 45°) für die
restlichen offenen Verbindungen. Schreibt KEINE Platine, sondern gibt T()/V()-Zeilen für tools/route_finish.py
aus – das Ergebnis bleibt damit explizit, prüfbar und reproduzierbar.

Regeln (wie Projekt): 0,2 mm Abstand zu fremdem Kupfer, 0,25 mm zu Bohrungen, Bahn 0,2 mm (Netzklasse Extern 0,3),
Via 0,6/0,3 mm (nicht unter dem Modulkörper U4, nicht in den Passermarken-Sperrflächen, im BT1-Courtyard nur GND),
0,5 mm zum Platinenrand. Pads als Rechteck/Kreis (Rechteck = umhüllend, konservativ), Netzflächen „R: …" als Polygon.

Aufruf (KiCad-Python): python3 tools/maze_route.py <board> <drc.json> [Netze zuerst …]
"""
import heapq
import json
import math
import sys
from array import array
import pcbnew

G = 0.1                       # Rastermaß mm
X0, Y0, NX, NY = 100.0, 100.0, 800, 500
CLR, HOLE_CLR, VIA_R, EDGE = 0.2, 0.25, 0.3, 0.5
VIA_COST, TURN_COST = 12.0, 0.6
EXTERN = ('AUTOTERM_5V', 'CTRL_', '1WIRE_DQ_C', '3V3_SENSOR_SW', 'BUTTON_N_C')
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
mm = pcbnew.ToMM


def width_for(net):
    return 0.3 if any(net.endswith(p) for p in EXTERN) else 0.2


class Grid:
    """Je Zelle: 0 frei, Netzcode >0 = nur dieses Netz in der Nähe, -1 = mehrere Netze."""
    def __init__(self):
        self.a = array('i', [0]) * (NX * NY)

    def mark(self, i, j, net):
        k = j * NX + i; v = self.a[k]
        if v == 0: self.a[k] = net
        elif v != net: self.a[k] = -1

    def free(self, i, j, net):
        v = self.a[j * NX + i]
        return v == 0 or v == net


def cells_near_box(x1, y1, x2, y2, r):
    i1, i2 = max(0, int((x1 - r - X0) / G)), min(NX - 1, int((x2 + r - X0) / G) + 1)
    j1, j2 = max(0, int((y1 - r - Y0) / G)), min(NY - 1, int((y2 + r - Y0) / G) + 1)
    for j in range(j1, j2 + 1):
        for i in range(i1, i2 + 1):
            yield i, j, X0 + i * G, Y0 + j * G


def d_rect(x, y, r):
    return math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))


def d_seg(x, y, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / L))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)


def in_poly(x, y, poly):
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c


def d_poly(x, y, poly):
    if in_poly(x, y, poly): return 0.0
    return min(d_seg(x, y, *p, *q) for p, q in zip(poly, poly[1:] + poly[:1]))


def shapes(b):
    """Kupferformen: (Netzcode, Lagen{'F','B'}, Art, Geometrie, Bohrradius)."""
    out = []
    for f in b.GetFootprints():
        for p in f.Pads():
            layers = {L for L, lid in (('F', pcbnew.F_Cu), ('B', pcbnew.B_Cu)) if p.IsOnLayer(lid)}
            q = p.GetBoundingBox(); r = (mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom()))
            drill = mm(p.GetDrillSize().x) / 2 if p.GetDrillSize().x > 0 else 0
            if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
                out.append((p.GetNetCode(), layers, 'C', ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, (r[2] - r[0]) / 2), drill, p))
            else:
                out.append((p.GetNetCode(), layers, 'R', r, drill, p))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA':
            out.append((t.GetNetCode(), {'F', 'B'}, 'C', (mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth(pcbnew.F_Cu)) / 2),
                        mm(t.GetDrill()) / 2, t))
        elif t.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu):
            out.append((t.GetNetCode(), {'F' if t.GetLayer() == pcbnew.F_Cu else 'B'}, 'S',
                        (mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), mm(t.GetWidth()) / 2), 0, t))
    for z in b.Zones():
        if z.GetIsRuleArea() or not z.GetZoneName().startswith('R: '): continue
        o = z.Outline().Outline(0); poly = [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())]
        out.append((z.GetNetCode(), {'F' if z.GetLayer() == pcbnew.F_Cu else 'B'}, 'P', poly, 0, z))
    return out


def bbox_of(kind, g):
    if kind == 'R': return g
    if kind == 'C': return (g[0] - g[2], g[1] - g[2], g[0] + g[2], g[1] + g[2])
    if kind == 'S': return (min(g[0], g[2]) - g[4], min(g[1], g[3]) - g[4], max(g[0], g[2]) + g[4], max(g[1], g[3]) + g[4])
    xs, ys = [p[0] for p in g], [p[1] for p in g]; return (min(xs), min(ys), max(xs), max(ys))


def dist(kind, g, x, y):
    if kind == 'R': return d_rect(x, y, g)
    if kind == 'C': return max(0.0, math.hypot(x - g[0], y - g[1]) - g[2])
    if kind == 'S': return max(0.0, d_seg(x, y, *g[:4]) - g[4])
    return d_poly(x, y, g)


def rasterize(grids, net, layers, kind, g, drill, w_half, _owner=None):
    """Sperrzellen für Bahnen (Radius CLR+w/2) und Vias (CLR+VIA_R bzw. Bohrabstand)."""
    bb = bbox_of(kind, g); rmax = max(CLR + w_half, CLR + VIA_R, HOLE_CLR + VIA_R if drill else 0) + 0.01
    for i, j, x, y in cells_near_box(*bb, rmax):
        d = dist(kind, g, x, y)
        for L in layers:
            if d < CLR + w_half: grids[L].mark(i, j, net)
        if kind in ('R', 'C') and isinstance(_owner, pcbnew.PAD) and d < VIA_R + 0.1:
            grids['V'].mark(i, j, -1)                        # kein Via-in-Pad, auch nicht im eigenen Netz
        if d < CLR + VIA_R or (drill and math.hypot(x - bb[0] - (bb[2] - bb[0]) / 2, y - bb[1] - (bb[3] - bb[1]) / 2) < drill + HOLE_CLR + VIA_R):
            grids['V'].mark(i, j, net)


def main(path, drc, flt):
    b = pcbnew.LoadBoard(path); b.BuildConnectivity(); conn = b.GetConnectivity()
    d = json.load(open(drc))
    S = shapes(b)
    W_HALF = 0.1                                     # Raster für 0,2-mm-Bahnen; 0,3-mm-Netze prüfen wir zusätzlich
    grids = {'F': Grid(), 'B': Grid(), 'V': Grid()}
    for net, layers, kind, g, drill, _ in S:
        rasterize(grids, net if net > 0 else -2, layers, kind, g, drill, W_HALF, _)
    # Rand, Sperrflächen, Modulkörper (Vias)
    for i in range(NX):
        for j in range(NY):
            x, y = X0 + i * G, Y0 + j * G
            if x < 100 + EDGE or y < 100 + EDGE or x > 180 - EDGE or y > 150 - EDGE or i in (0, NX - 1) or j in (0, NY - 1):
                for L in 'FBV': grids[L].a[j * NX + i] = -1
            elif x < 100 + EDGE + VIA_R or y < 100 + EDGE + VIA_R or x > 180 - EDGE - VIA_R or y > 150 - EDGE - VIA_R:
                grids['V'].a[j * NX + i] = -1
    gnd = b.FindNet('GND').GetNetCode()
    for z in b.Zones():
        if z.GetIsRuleArea():
            bb = z.GetBoundingBox()
            for i, j, x, y in cells_near_box(mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()), VIA_R):
                for L in 'FBV': grids[L].a[j * NX + i] = -1
    body = {}
    for f in b.GetFootprints():
        if f.GetReference() in ('U4', 'BT1'):
            L = pcbnew.F_Fab if f.GetReference() == 'U4' else pcbnew.F_CrtYd
            q = [g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() == L]
            body[f.GetReference()] = (min(mm(x.GetLeft()) for x in q), min(mm(x.GetTop()) for x in q),
                                      max(mm(x.GetRight()) for x in q), max(mm(x.GetBottom()) for x in q))
    for i, j, x, y in cells_near_box(*body['U4'], VIA_R):
        grids['V'].a[j * NX + i] = -1
    bt1 = body['BT1']

    by_uuid = {}
    for it in list(b.GetTracks()) + [p for f in b.GetFootprints() for p in f.Pads()] + list(b.Zones()):
        by_uuid[it.m_Uuid.AsString()] = it
    shape_of = {id(o): (k, g, layers) for net, layers, k, g, dr, o in S}

    def own_cells(items, w_half):
        cells = set()
        for it in items:
            for net, layers, k, g, dr, o in S:
                if o is it or (hasattr(o, 'm_Uuid') and o.m_Uuid.AsString() == it.m_Uuid.AsString()):
                    for i, j, x, y in cells_near_box(*bbox_of(k, g), 0):
                        if dist(k, g, x, y) == 0:            # Zellmitte liegt im eigenen Kupfer
                            for L in layers: cells.add((i, j, L))
                    break
        return cells

    out = []
    # Netzfilter = Reihenfolge: passende Verbindungen zuerst (in Filterreihenfolge), dann alle übrigen
    def prio(u):
        desc = u['items'][0]['description']
        return next((k for k, s_ in enumerate(flt) if s_ in desc), len(flt))
    pairs = sorted(d['unconnected_items'], key=prio)
    for u in pairs:
        a, c = by_uuid.get(u['items'][0]['uuid']), by_uuid.get(u['items'][1]['uuid'])
        if a is None or c is None:
            out.append(f"# nicht gefunden: {u['items'][0]['description']}"); continue
        net = a.GetNetCode(); name = a.GetNetname(); wh = width_for(name) / 2
        ca = [a] + [x for x in conn.GetConnectedItems(a)]
        cc = [c] + [x for x in conn.GetConnectedItems(c)]
        if any(x.m_Uuid.AsString() == c.m_Uuid.AsString() for x in ca):
            continue                                  # bereits durch einen früheren Weg verbunden
        src, dst = own_cells(ca, wh), own_cells(cc, wh)
        if not src or not dst:
            out.append(f'# keine Zellen: {name}'); continue
        tx = [(i, j) for i, j, L in dst]; tb = (min(t[0] for t in tx), min(t[1] for t in tx), max(t[0] for t in tx), max(t[1] for t in tx))

        def h(i, j):
            dx = max(tb[0] - i, 0, i - tb[2]); dy = max(tb[1] - j, 0, j - tb[3])
            return (max(dx, dy) + 0.414 * min(dx, dy))

        def ok(i, j, L):
            if not (0 <= i < NX and 0 <= j < NY): return False
            if (i, j, L) in dst or (i, j, L) in src: return True
            return grids[L].free(i, j, net)

        def via_ok(i, j):
            if not grids['V'].free(i, j, net): return False
            x, y = X0 + i * G, Y0 + j * G
            if net != gnd and bt1[0] <= x <= bt1[2] and bt1[1] <= y <= bt1[3]: return False
            return True

        start = [(0.0, 0.0, i, j, L, -1) for i, j, L in src]
        heapq.heapify(start)
        best = {}; prev = {}; goal = None; n = 0
        for _, gcost, i, j, L, dr in start: best[(i, j, L, dr)] = 0.0
        pq = [(h(i, j), 0.0, i, j, L, -1) for i, j, L in src]; heapq.heapify(pq)
        while pq:
            f_, gc, i, j, L, dr = heapq.heappop(pq); n += 1
            if gc > best.get((i, j, L, dr), 1e18): continue
            if (i, j, L) in dst and (i, j, L) not in src: goal = (i, j, L, dr); break
            if n > 2_500_000: break
            for k, (di, dj) in enumerate(DIRS):
                ni, nj = i + di, j + dj
                if not ok(ni, nj, L): continue
                if di and dj and not (ok(i + di, j, L) and ok(i, j + dj, L)): continue
                ng = gc + (1.4142 if di and dj else 1.0) + (TURN_COST if dr not in (-1, k) else 0)
                key = (ni, nj, L, k)
                if ng < best.get(key, 1e18):
                    best[key] = ng; prev[key] = (i, j, L, dr); heapq.heappush(pq, (ng + h(ni, nj), ng, ni, nj, L, k))
            if via_ok(i, j):
                L2 = 'B' if L == 'F' else 'F'
                if ok(i, j, L2):
                    key = (i, j, L2, -1); ng = gc + VIA_COST
                    if ng < best.get(key, 1e18):
                        best[key] = ng; prev[key] = (i, j, L, dr); heapq.heappush(pq, (ng + h(i, j), ng, i, j, L2, -1))
        if goal is None:
            out.append(f'# kein Weg: {name} ({n} Schritte)'); continue
        path = [goal]
        while path[-1] in prev: path.append(prev[path[-1]])
        path = [(i, j, L) for i, j, L, _ in reversed(path)]
        # in Bahnzüge zerlegen, kollineare Punkte zusammenfassen
        segs, vias = [], []
        cur = [path[0]]
        for p_ in path[1:]:
            if p_[2] != cur[-1][2]:
                vias.append(cur[-1][:2]); segs.append(cur); cur = [p_]
            else:
                cur.append(p_)
        segs.append(cur)
        txt = []
        for s in segs:
            pts = [s[0]]
            for k in range(1, len(s) - 1):
                a0, a1, a2 = pts[-1], s[k], s[k + 1]
                if (a1[0] - a0[0]) * (a2[1] - a1[1]) != (a1[1] - a0[1]) * (a2[0] - a1[0]): pts.append(a1)
            if len(s) > 1: pts.append(s[-1])
            if len(pts) < 2: continue
            coords = ', '.join(f'({X0 + i * G:.2f}, {Y0 + j * G:.2f})' for i, j, _ in pts)
            txt.append(f"T({name!r}, {'F' if s[0][2] == 'F' else 'B'}, [{coords}], {2 * wh:.1f})")
        for i, j in vias: txt.append(f"V({name!r}, {X0 + i * G:.2f}, {Y0 + j * G:.2f})")
        out.append(f'# {name}: {len(path)} Zellen, {len(vias)} Vias'); out += txt
        # Weg als Hindernis für die folgenden Netze
        for (i, j, L) in path:
            R_ = int(0.7 / G) + 1                        # 0,7 mm deckt Bahn- (0,4) und Via-Abstand (0,6) ab
            for ii in range(i - R_, i + R_ + 1):
                for jj in range(j - R_, j + R_ + 1):
                    if 0 <= ii < NX and 0 <= jj < NY:
                        dd = math.hypot(ii - i, jj - j) * G
                        if dd < CLR + 2 * wh: grids[L].mark(ii, jj, net)
                        if dd < CLR + VIA_R + wh: grids['V'].mark(ii, jj, net)
        for (i, j) in vias:
            R_ = int(0.9 / G) + 1
            for ii in range(i - R_, i + R_ + 1):
                for jj in range(j - R_, j + R_ + 1):
                    if 0 <= ii < NX and 0 <= jj < NY:
                        dd = math.hypot(ii - i, jj - j) * G
                        if dd < CLR + VIA_R + wh: grids['F'].mark(ii, jj, net); grids['B'].mark(ii, jj, net)
                        if dd < 2 * VIA_R + CLR: grids['V'].mark(ii, jj, net)
    print('\n'.join(out))


if __name__ == '__main__':
    args = sys.argv[3:]
    if '--win' in args:   # feines Raster in einem Fenster: --win x0 y0 x1 y1 raster (z. B. 0,5-mm-Pinraster)
        k = args.index('--win'); x0_, y0_, x1_, y1_, g_ = map(float, args[k + 1:k + 6]); args = args[:k] + args[k + 6:]
        G, X0, Y0 = g_, x0_, y0_; NX, NY = int((x1_ - x0_) / g_) + 1, int((y1_ - y0_) / g_) + 1
    main(sys.argv[1], sys.argv[2], args)
