"""Bestückungsdruck nach Entscheidung E-02 und Y-08.

- Referenzbezeichner auf F.Fab (Bestückungszeichnung), Mitte des Bauteils, 0,5 mm.
- Silkscreen: Steckernamen, RESET/BOOT/DIAG, Status-LEDs, Energiefluss-Bild (G-01), Testpunktnamen (A16),
  Revision. Batteriepolung und Pin-1-/Polaritätsmarken stammen aus den Footprints.
- Alle hier erzeugten Elemente liegen in der Gruppe GROUP und werden bei jedem Lauf neu erzeugt.

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/silkscreen.py LandyHeater.kicad_pcb
"""
import math
import os
import sys
import pcbnew

GROUP = 'Bestückungsdruck (tools/silkscreen.py)'
H_MAIN, H_TP, W_TXT, W_LINE = 0.9, 0.8, 0.15, 0.15
HOLES = [(104, 104), (176, 104), (104, 146), (176, 146)]
FIDS = ['FID1', 'FID2', 'FID3']

# (Text, x, y, Drehung, Höhe) – Stecker: Beschriftung jeweils links vom Stecker, Leserichtung von unten
LABELS = [
    ('12V IN', 107.35, 141.6, 90, H_MAIN),
    ('AUTOTERM', 117.25, 143.8, 90, H_MAIN),
    ('TASTER/LED', 132.0, 143.8, 90, H_TP),
    ('1-WIRE', 148.5, 143.6, 90, H_MAIN),
    # RESET/BOOT: links neben den Tastern zwischen Modulkante (171,8) und Tasterpads (173,3)
    ('RST', 172.5, 111.0, 90, H_TP), ('BOOT', 172.5, 117.9, 90, H_TP),
    # engste Ecke (zwischen RESET/BOOT, J5, R8): Beschriftung jeweils rechts vom Testpad, senkrecht
    ('TX', 175.09, 114.3, 90, H_TP),     # TP10, mittig zwischen den Silk-Kreisen von TP10 und TP11
    ('GND', 177.75, 121.0, 90, H_TP),    # TP15, zwischen Pad und R8
    ('DIAG', 103.6, 115.55, 0, H_TP),
    ('1', 146.7, 107.4, 0, H_TP), ('2', 146.7, 111.0, 0, H_TP), ('STATUS', 146.7, 115.3, 90, H_TP),
    # Energiefluss-Bild G-01
    ('12V', 109.6, 101.45, 0, H_TP), ('USB', 109.6, 105.75, 0, H_TP),
    ('3V3', 116.9, 105.3, 0, H_TP), ('RUN', 120.3, 105.3, 0, H_TP), ('HEAT', 123.7, 105.3, 0, H_TP),
    ('LandyHeater Rev B', 165.6, 146.75, 0, H_TP), ('10/2026', 165.6, 148.45, 0, H_TP),
]
LINES = [  # G-01: 12V ●─┐  ├─● 3V3 ─● RUN ─● HEAT ;  USB ●─┘
    # LED 0°: Anodenpad endet 1,225 mm rechts der Mitte, Kathodenstrich (Silk) 1,485 mm links der Mitte
    ((114.0, 101.45), (114.55, 101.45)), ((114.55, 101.45), (114.55, 105.75)), ((114.0, 105.75), (114.55, 105.75)),
    ((114.55, 103.6), (115.2, 103.6)), ((118.3, 103.6), (118.6, 103.6)), ((121.7, 103.6), (122.0, 103.6)),
]
FIXED_TP = {'TP10', 'TP15'}   # Beschriftung steht in LABELS
TP_NAMES = {
    'TP1': 'BAT', 'TP2': '12VP', 'TP3': 'VIN', 'TP4': '3V3', 'TP5': 'VBUS', 'TP6': 'VBP', 'TP7': 'GND', 'TP8': 'EN',
    'TP9': 'IO0', 'TP10': 'TX', 'TP11': 'RX', 'TP12': 'SDA', 'TP13': 'SCL', 'TP14': 'INT', 'TP15': 'GND',
    'TP16': '5VA', 'TP17': 'CTX', 'TP18': 'CRX', 'TP19': 'TX3', 'TP20': 'RX3', 'TP21': 'OE', 'TP22': 'DQ',
    'TP23': '3VS', 'TP24': 'DIAG', 'TP25': 'GND', 'TP26': 'BTN', 'TP27': 'PWM', 'TP28': 'RUN',
}


def main(path):
    b = pcbnew.LoadBoard(path); mm, fm = pcbnew.ToMM, pcbnew.FromMM
    V = lambda x, y: pcbnew.VECTOR2I(fm(x), fm(y))
    # alte Werkzeug-Gruppe entfernen, speichern und neu starten: nach BOARD.Remove() verliert die SWIG-Bindung
    # die Typen der übrigen Objekte (Footprints werden unbrauchbar)
    old_g = [g for g in b.Groups() if g.GetName() == GROUP]
    if old_g:
        for it in [it for g in old_g for it in g.GetItems()] + old_g:
            b.Remove(it)
        b.Save(path); sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, os.path.abspath(__file__), path])
    grp = pcbnew.PCB_GROUP(b); grp.SetName(GROUP); b.Add(grp)

    fps = {f.GetReference(): f for f in b.GetFootprints()}
    # 1. Referenzen auf die Bestückungszeichnung
    for f in fps.values():
        r = f.Reference(); r.SetLayer(pcbnew.F_Fab); r.SetVisible(True)
        r.SetTextSize(V(0.5, 0.5)); r.SetTextThickness(fm(0.08)); r.SetPosition(f.GetPosition()); r.SetTextAngleDegrees(0)
        if f.Value().GetLayer() == pcbnew.F_SilkS:
            f.Value().SetLayer(pcbnew.F_Fab)

    # Hindernisse für die Prüfung
    pads, crt, silk = [], {}, []
    for f in fps.values():
        # Bauteilkörper = Umriss auf F.Fab (Courtyard-Rand bleibt sichtbar und darf beschriftet werden)
        fab = [g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab and g.GetClass() != 'PCB_TEXT']
        if fab:
            crt[f.GetReference()] = (min(mm(q.GetLeft()) for q in fab), min(mm(q.GetTop()) for q in fab),
                                     max(mm(q.GetRight()) for q in fab), max(mm(q.GetBottom()) for q in fab))
        for p in f.Pads():
            q = p.GetBoundingBox(); pads.append((mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom())))
        for g in f.GraphicalItems():
            if g.GetLayer() == pcbnew.F_SilkS:
                q = g.GetBoundingBox(); silk.append((mm(q.GetLeft()), mm(q.GetTop()), mm(q.GetRight()), mm(q.GetBottom())))
    fid = [(mm(fps[r].GetPosition().x), mm(fps[r].GetPosition().y)) for r in FIDS]

    def ov(a, c, gap):
        return min(a[2], c[2]) - max(a[0], c[0]) > -gap and min(a[3], c[3]) - max(a[1], c[1]) > -gap

    def free(bb, own=None, use_crt=True):
        if bb[0] < 100.4 or bb[1] < 100.4 or bb[2] > 179.6 or bb[3] > 149.6: return 'Rand'
        for hx, hy in HOLES + fid:
            r_ = 3.3 if (hx, hy) in HOLES else 2.0
            if math.hypot(min(max(hx, bb[0]), bb[2]) - hx, min(max(hy, bb[1]), bb[3]) - hy) < r_: return 'Loch/Passermarke'
        if any(ov(bb, q, 0.15) for q in pads): return 'Pad'
        if any(ov(bb, q, 0.05) for q in silk): return 'Silk'   # = min_silk_clearance der Projektregeln
        if use_crt and any(ov(bb, q, 0.0) for r, q in crt.items() if r != own and not r.startswith(('H', 'FID'))): return 'Bauteil'
        return None

    def add_text(txt, x, y, ang, h):
        t = pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(V(h, h)); t.SetTextThickness(fm(W_TXT)); t.SetTextAngleDegrees(ang)
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        t.SetPosition(V(x, y))
        # tatsächliche Strichgeometrie der Zeichen (GetBoundingBox enthält Zeilenabstand und ist ~1,8-fach zu hoch)
        q = t.GetEffectiveTextShape().BBox(); w2 = W_TXT / 2
        return t, (mm(q.GetLeft()) - w2, mm(q.GetTop()) - w2, mm(q.GetRight()) + w2, mm(q.GetBottom()) + w2)

    report = []
    # 2. feste Beschriftungen (geprüft; Steckernamen dürfen über dem eigenen Steckerkörper-Rand liegen)
    for txt, x, y, ang, h in LABELS:
        t, bb = add_text(txt, x, y, ang, h)
        why = free(bb, use_crt=False)
        b.Add(t); grp.AddItem(t); silk.append(bb)
        if why: report.append(f'fest „{txt}“: Konflikt {why}')
    for (x1, y1), (x2, y2) in LINES:
        s_ = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_SEGMENT); s_.SetStart(V(x1, y1)); s_.SetEnd(V(x2, y2))
        s_.SetLayer(pcbnew.F_SilkS); s_.SetWidth(fm(W_LINE)); b.Add(s_); grp.AddItem(s_)
        silk.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
    # 3. Testpunktnamen: Ring um das Pad (1,7–3,6 mm, 16 Richtungen, waagrecht und senkrecht), nächste freie Lage
    cand = []
    for d in (1.7, 1.95, 2.3, 2.6, 3.0, 3.6):
        for k in range(16):
            a_ = 2 * math.pi * k / 16
            for ang in (0, 90):
                cand.append((d + (0 if ang == 0 else 0.05), round(d * math.cos(a_), 3), round(d * math.sin(a_), 3), ang))
    cand.sort(key=lambda c: (c[0], c[3]))
    for tp in sorted((t for t in TP_NAMES if t not in FIXED_TP), key=lambda r: int(r[2:])):
        f = fps[tp]; x, y = mm(f.GetPosition().x), mm(f.GetPosition().y)
        done = False
        for _, dx, dy, ang in cand:
            t, bb = add_text(TP_NAMES[tp], x + dx, y + dy, ang, H_TP)
            if free(bb, own=tp) is None:
                b.Add(t); grp.AddItem(t); silk.append(bb); done = True; break
        if not done:
            report.append(f'{tp} ({TP_NAMES[tp]}): kein freier Platz')
    b.Save(path)
    print(f'Silkscreen: {len(LABELS)} feste Texte, {len(LINES)} Linien, {len(TP_NAMES)} Testpunkte')
    for r in report: print('  ', r)
    sys.stdout.flush(); os._exit(0)   # Python-Aufräumen kann nach Save abstürzen


if __name__ == '__main__':
    main(sys.argv[1])
