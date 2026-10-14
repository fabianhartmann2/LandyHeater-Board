"""Platzierungsprüfung (Schritt 5 der Layout-Anleitung) – ergänzt den KiCad-DRC um Floorplan- und Datenblattkriterien.

Prüft: Vollständigkeit, Courtyard-Überlappung, Kontur, Lochfreiraum, Abblock- und Schutzabstände,
Trennabstände vom Schaltregler-SW-Knoten, Ausrichtung gepolter Bauteile.
Aufruf (KiCad-Python): python3 tools/check_placement.py LandyHeater.kicad_pcb
"""
import sys, math
import pcbnew

HOLES = [(104, 104), (176, 104), (104, 146), (176, 146)]
HOLE_R = 3.3                     # M3-Kopf 5,5 mm + Abstand
BOARD = (100.0, 100.0, 180.0, 150.0)
EDGE_OK = {'J1', 'J2', 'J3', 'J4', 'J5'}   # Stecker sitzen bewusst an der Kante

# (Bauteil-Pad, Ziel-Pad, Grenze mm, Quelle) – Abstand Padmitte zu Padmitte
DIST = [
    (('C7', '1'), ('U3', '4'), 2.5, 'LMR43620 8.5.1 CIN an VIN'),
    (('C7', '2'), ('U3', '1'), 2.5, 'LMR43620 8.5.1 CIN an GND'),
    (('C8', '1'), ('U3', '7'), 3.0, 'LMR43620 8.5.1 CVCC'),
    (('C9', '2'), ('U3', '6'), 3.0, 'LMR43620 8.5.1 CBOOT an BOOT'),
    (('C9', '1'), ('U3', '5'), 3.0, 'LMR43620 8.5.1 CBOOT an SW'),
    (('L1', '1'), ('U3', '5'), 5.5, 'LMR43620 8.5.1 SW-Fläche klein'),
    (('C14', '1'), ('U4', '2'), 2.5, 'Espressif: 100 nF am 3V3-Pin'),
    (('C15', '1'), ('U4', '3'), 3.0, 'WROOM-1U: EN-RC'),
    (('C16', '1'), ('U5', '5'), 3.0, 'TPS3808 8.4.1'),
    (('C19', '1'), ('U6', '5'), 3.0, 'RTC VDD'),
    (('C21', '1'), ('U7', '3'), 3.0, 'TXU0202 11.1 VCCA'),
    (('C22', '1'), ('U7', '7'), 3.0, 'TXU0202 11.1 VCCB'),
    (('C23', '1'), ('U8', '5'), 3.0, 'TPS22945 11.1 VIN'),
    (('C24', '1'), ('U8', '1'), 3.0, 'TPS22945 11.1 VOUT'),
    (('C2', '1'), ('U2', '5'), 3.5, 'TPS25947 8.4.1 IN-Kondensator'),
    (('R6', '1'), ('U2', '9'), 3.5, 'TPS25947 8.4.1 RILM nah'),
    (('C3', '1'), ('U2', '7'), 3.5, 'TPS25947 8.4.1 CdVdT nah'),
    (('R9', '1'), ('U4', '13'), 2.5, 'Espressif: USB-R am Modul'),
    (('R10', '1'), ('U4', '14'), 2.5, 'Espressif: USB-R am Modul'),
    (('R11', '1'), ('U4', '37'), 3.5, 'Espressif: UART-R am Modul'),
    (('U1', '1'), ('J5', 'A6'), 5.0, 'TPD2EUSB30 10.1 am Stecker (Abstand für A/B-Verbindung, Routing 6.3)'),
    (('U1', '2'), ('J5', 'A7'), 5.0, 'TPD2EUSB30 10.1 am Stecker (Abstand für A/B-Verbindung, Routing 6.3)'),
    (('D3', '1'), ('J5', 'A4'), 6.0, 'Y-06 VBUS-ESD am Stecker'),
    (('D1', '2'), ('J1', '1'), 5.0, 'Y-06 TVS am Stecker'),
    (('D7', '1'), ('J2', '1'), 5.0, 'Y-06 ESD am Stecker'),
    (('D8', '1'), ('J2', '3'), 6.5, 'Y-06 ESD am Stecker'),
    (('D8', '2'), ('J2', '4'), 6.5, 'Y-06 ESD am Stecker'),
    (('D9', '1'), ('J3', '2'), 5.0, 'Y-06 ESD am Stecker'),
    (('D9', '2'), ('J3', '1'), 5.0, 'Y-06 ESD am Stecker'),
    (('D10', '1'), ('J4', '1'), 5.0, 'Y-06 ESD am Stecker'),
]
# Mindestabstände vom SW-Knoten (L1 Pad 1) – Floorplan 2.3
SEP = [('U6', 20.0, 'RTC'), ('U1', 25.0, 'USB-ESD'), ('R9', 25.0, 'USB-R'), ('U8', 25.0, '1-Wire'),
       ('D9', 25.0, '1-Wire-ESD'), ('U4', 25.0, 'Modul')]
# Routing-Korridore ohne Bauteile (Schritt 4): (Name, x1, y1, x2, y2, erlaubte Bauteile)
KEEPOUT = [
    ('Fan-out Modulpads 4-12', 150.9, 107.2, 152.2, 118.0, set()),     # ab Oberkante Via Pad 4
    ('USB-Paar unter dem Modul', 149.0, 122.45, 161.6, 124.8, set()),
    ('USB-Paar senkrecht', 159.8, 122.45, 161.6, 129.2, set()),
    ('USB-Paar zu U1', 161.6, 126.6, 166.2, 129.1, {'C17', 'C18'}),   # DNP-Abgleich direkt am Paar (stubfrei)
]
POLAR_SAME = [['D11', 'D12', 'D13', 'D19', 'D14'], ['D20', 'D21']]


def main(path):
    b = pcbnew.LoadBoard(path); mm = pcbnew.ToMM
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    box, pad = {}, {}
    for r, f in fps.items():
        f.BuildCourtyardCaches(); c = f.GetCourtyard(pcbnew.F_CrtYd)
        bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
        box[r] = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
        for p in f.Pads():
            pad.setdefault((r, p.GetNumber()), (mm(p.GetPosition().x), mm(p.GetPosition().y)))
    err, warn = [], []
    refs = sorted(box)
    for i, a in enumerate(refs):
        A = box[a]
        if a not in EDGE_OK and (A[0] < BOARD[0] + 0.3 or A[1] < BOARD[1] + 0.3 or A[2] > BOARD[2] - 0.3 or A[3] > BOARD[3] - 0.3):
            err.append(f'KONTUR {a} {tuple(round(v, 2) for v in A)}')
        if not a.startswith('H'):
            for hx, hy in HOLES:
                nx = min(max(hx, A[0]), A[2]); ny = min(max(hy, A[1]), A[3])
                if math.hypot(nx - hx, ny - hy) < HOLE_R: err.append(f'LOCH {a} bei ({hx},{hy})')
        for bb_ in refs[i + 1:]:
            B = box[bb_]
            ox = min(A[2], B[2]) - max(A[0], B[0]); oy = min(A[3], B[3]) - max(A[1], B[1])
            if ox > 0.005 and oy > 0.005: err.append(f'COURTYARD {a}-{bb_} {ox:.2f} x {oy:.2f} mm')
    rows = []
    for (a, b_, lim, src) in DIST:
        d = math.dist(pad[a], pad[b_]); ok = d <= lim
        rows.append((ok, f'{a[0]}.{a[1]} -> {b_[0]}.{b_[1]}: {d:.2f} mm (Grenze {lim}) – {src}'))
        if not ok: err.append('ABSTAND ' + rows[-1][1])
    sw = pad[('L1', '1')]
    for r, lim, what in SEP:
        A = box[r]; nx = min(max(sw[0], A[0]), A[2]); ny = min(max(sw[1], A[1]), A[3])
        d = math.hypot(nx - sw[0], ny - sw[1]); rows.append((d >= lim, f'SW-Knoten -> {r} ({what}): {d:.1f} mm (min {lim})'))
        if d < lim: err.append('TRENNUNG ' + rows[-1][1])
    for name, x1, y1, x2, y2, allow in KEEPOUT:
        for r, A in box.items():
            if r in allow: continue
            if min(A[2], x2) - max(A[0], x1) > 0.005 and min(A[3], y2) - max(A[1], y1) > 0.005:
                err.append(f'KORRIDOR {name}: {r}')
    for grp in POLAR_SAME:
        rs = {round(fps[r].GetOrientationDegrees()) % 360 for r in grp}
        if len(rs) > 1: warn.append(f'Ausrichtung uneinheitlich {grp}: {rs}')
    print(f'Footprints: {len(fps)}')
    for ok, t in rows: print(('  ok  ' if ok else '  !!  ') + t)
    print('\n'.join(err) if err else 'Keine Platzierungsfehler')
    for w in warn: print('Hinweis:', w)
    return 1 if err else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
