"""Floorplan-Zeichnung für den Platzierungsmeilenstein.

Arbeitet auf einer KOPIE der Leiterplatte (mit kopierter .kicad_pro daneben): entfernt alle Footprints außer den
mechanischen Ankern und zeichnet die Zonen aus Platzierung_1_Analyse_Floorplan.md auf Dwgs.User.
Aufruf (KiCad-Python): python3 tools/floorplan.py <kopie>.kicad_pcb
"""
import sys, pcbnew
P = sys.argv[1]
b = pcbnew.LoadBoard(P); fm = pcbnew.FromMM
V = lambda x, y: pcbnew.VECTOR2I(fm(x), fm(y))
KEEP = {'H1', 'H2', 'H3', 'H4', 'J1', 'J2', 'J3', 'J4', 'J5', 'U4', 'BT1'}
for f in list(b.GetFootprints()):
    if f.GetReference() not in KEEP: b.Remove(f)
ZONES = [
    ('Z1 12V-Eingang', 101, 127, 121, 137.4), ('Z2 Buck 3V3', 101, 113, 121, 127), ('Z3 Diagnose', 108, 100.3, 124, 113),
    ('Z4 RTC', 124, 100.3, 140, 119), ('Z6 Reset/Status/RTC-IC', 140, 100.3, 152, 119), ('Z5 MCU', 152, 102, 172, 122),
    ('Z7 BOOT/UART', 172, 108, 180, 121), ('Z8 USB/eFuse', 160, 122, 180, 148), ('USB-Korridor', 150, 121.5, 171, 125),
    ('Z9 AUTOTERM', 124, 119, 134, 137.4), ('Z10 Taster/LED', 134, 124, 150, 137.4), ('Z11 1-Wire', 150, 125, 159.5, 137.4),
]
LABEL = {'Z4 RTC': (124.7, 115.2), 'Z5 MCU': (153.5, 117.5), 'Z6 Reset/Status/RTC-IC': (140.7, 100.9), 'USB-Korridor': (150.6, 121.9)}
ZONES = [(n.replace('Z6 Reset/Status/RTC-IC', 'Z6 Reset/Status'), *r) for n, *r in ZONES]
LABEL['Z6 Reset/Status'] = (140.7, 100.9)
for name, x1, y1, x2, y2 in ZONES:
    r = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_RECT); r.SetStart(V(x1, y1)); r.SetEnd(V(x2, y2))
    r.SetLayer(pcbnew.Dwgs_User); r.SetWidth(fm(0.3 if 'Korridor' not in name else 0.15)); b.Add(r)
    t = pcbnew.PCB_TEXT(b); t.SetText(name); t.SetLayer(pcbnew.Dwgs_User)
    t.SetTextSize(pcbnew.VECTOR2I(fm(1.1), fm(1.1))); t.SetTextThickness(fm(0.18))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_TOP)
    lx, ly = LABEL.get(name, (x1 + 0.7, y1 + 0.7))
    if x2 - x1 < 12 and y2 - y1 > x2 - x1:
        t.SetTextAngleDegrees(90); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_TOP); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
        lx, ly = LABEL.get(name, (x1 + 0.7, y1 + 0.7))
    t.SetPosition(V(lx, ly))
    b.Add(t)
b.Save(P)
print('ok')
