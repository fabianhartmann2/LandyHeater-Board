"""Manuelles Routing der kritischen Pfade (Schritt 6.3), blockweise mit Begründung.

Alle hier erzeugten Leiterbahnen und Vias liegen in der Gruppe GROUP, Kupferflächen tragen den Namenspräfix
ZPFX. Bei jedem Lauf werden sie entfernt und neu erzeugt (reproduzierbar). Gefüllt wird anschließend in einem
eigenen Prozess (tools/zones.py --fill-stage), weil KiCads SWIG-Bindung nach BOARD.Remove() Typen verliert.

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/route_manual.py LandyHeater.kicad_pcb
"""
import os
import subprocess
import sys
import pcbnew

GROUP = 'Routing manuell (tools/route_manual.py)'
ZPFX = 'R: '
VIA_D, VIA_DRILL = 0.6, 0.3

TRACKS, VIAS, ZONES = [], [], []


def T(net, layer, pts, w):
    TRACKS.append((net, layer, pts, w))


def V(net, x, y):
    VIAS.append((net, x, y))


def Z(name, net, layer, poly, prio=2):
    ZONES.append((name, net, layer, poly, prio))


F, B = pcbnew.F_Cu, pcbnew.B_Cu

# =============================================================================================
# A) 12-V-Eingang (J1 → D1 TVS → D2 → C26/FB1 → VIN_SYS)
# =============================================================================================
# BATT: J1.1 → D1.2 (TVS) → D2-Anode als Fläche; TVS direkt am Steckerpin (Y-06)
Z('BATT', '/Versorgung/BATT_12V_IN', F, [(112.1, 133.6), (118.3, 133.6), (118.3, 136.65), (113.9, 136.65), (113.9, 138.2), (112.1, 138.2)])
T('/Versorgung/BATT_12V_IN', F, [(112.6, 133.9), (112.6, 133.3), (103.2, 133.3), (102.0, 134.5), (102.0, 135.5)], 0.3)  # TP1 über D1, TVS-GND bleibt frei
# TVS- und Stecker-GND: Vias zwischen D1.1 und J1.2 direkt an L2 (kurzer GND-Pfad, Y-06)
for x in (108.7, 110.5):
    V('GND', x, 137.1); T('GND', F, [(x, 136.05), (x, 137.1)], 0.6)
T('GND', F, [(110.5, 137.1), (110.5, 137.97)], 0.6)                                                 # → J1.2
# 12V_PROT: D2-Kathode → FB1.1, C26.1, TP2 als Fläche
Z('12V_PROT', '12V_PROT', F, [(114.0, 127.75), (118.3, 127.75), (118.3, 129.35), (121.45, 129.35), (121.45, 131.05), (118.3, 131.05), (118.3, 132.65), (114.0, 132.65)])
V('GND', 113.0, 131.0); T('GND', F, [(113.0, 129.97), (113.0, 131.0)], 0.4)                          # C26.2
# C1 (47 µF) GND
for x in (102.0, 103.8):
    V('GND', x, 130.45); T('GND', F, [(x, 129.7), (x, 130.45)], 0.6)

# =============================================================================================
# B) 3,3-V-Schaltregler U3 (LMR43620, TI 8.5.1 / Fig. 8-31, 8-32)
# =============================================================================================
# VIN: Fläche über C6/C7/U3.3/U3.4, Lasche zu TP3, Gang zwischen TP3 und TP7, Streifen zu FB1.2 und C1(+)
Z('VIN Buck', 'VIN_SYS', F, [(104.4, 118.6), (109.6, 118.6), (109.6, 121.85), (106.45, 121.85), (106.45, 125.55), (118.05, 125.55),
                            (118.05, 126.95), (110.25, 126.95), (110.25, 129.9), (106.4, 129.9), (106.4, 126.95), (105.35, 126.95),
                            (105.35, 123.8), (103.6, 123.8), (103.6, 121.85), (104.4, 121.85)])
for x in (105.4, 106.95, 108.5):
    V('VIN_SYS', x, 121.25)                                     # zur L3-VIN-Fläche
for x in (112.0, 114.5):
    V('VIN_SYS', x, 126.25)                                     # FB1-Seite zur L3-VIN-Fläche
# GND: Fläche über C6.2/C7.2/U3.1/U3.9/C8.2 – kleinste Eingangsschleife, Vias neben den Kondensatoren
Z('GND Buck', 'GND', F, [(104.4, 113.4), (113.3, 113.4), (113.3, 115.6), (110.25, 115.6), (110.25, 118.62), (109.55, 118.62),
                         (109.55, 117.9), (104.4, 117.9)])
for x, y in ((104.9, 114.9), (106.5, 114.9), (108.0, 114.9), (109.5, 114.4), (112.4, 113.85)):
    V('GND', x, y)
# SW-Knoten: U3.5 → C9.1 → L1.1, so klein wie möglich
Z('SW', '/Versorgung/SW_BUCK', F, [(110.4, 119.09), (116.75, 119.09), (116.75, 120.4), (110.4, 120.4)])
# BOOT: U3.6 → C9.2 ; VCC: U3.7 → C8.1 (0,15 mm im 0,6-mm-Spalt zwischen Pin 8 und C8/C9)
T('Net-(U3-BOOT)', F, [(111.27, 118.765), (112.4, 118.765), (112.4, 118.35)], 0.15)
T('Net-(U3-VCC)', F, [(111.27, 118.265), (111.62, 118.265), (111.62, 117.25), (112.4, 117.25), (112.4, 116.8)], 0.15)
# VOUT-Messung: Pin 8 nach oben, weg vom SW-Knoten, zur L3-3V3-Fläche
T('3V3_CORE', F, [(110.89, 117.59), (110.95, 116.55)], 0.3); V('3V3_CORE', 110.95, 116.55)
# Ausgang: L1.2 → C10.1 als Fläche, Vias zur L3-3V3-Fläche; C11.1 eigener Via
Z('3V3 Buck', '3V3_CORE', F, [(114.4, 114.7), (121.4, 114.7), (121.4, 116.45), (114.4, 116.45)])
V('3V3_CORE', 117.6, 115.6); V('3V3_CORE', 121.0, 115.55)
V('3V3_CORE', 121.0, 120.33); T('3V3_CORE', F, [(119.4, 120.33), (121.0, 120.33)], 0.6)
V('GND', 121.0, 118.5); T('GND', F, [(119.4, 118.48), (121.0, 118.5)], 0.6)                         # C10.2
V('GND', 121.0, 123.28); T('GND', F, [(119.4, 123.28), (121.0, 123.28)], 0.6)                       # C11.2
# Testpunkte 3V3 und GND
V('3V3_CORE', 111.9, 123.0); T('3V3_CORE', F, [(110.4, 123.0), (111.9, 123.0)], 0.3)               # TP4
V('GND', 107.4, 124.6); T('GND', F, [(107.4, 123.0), (107.4, 124.6)], 0.3)                         # TP7


# =============================================================================================
# C) USB-C J5, ESD U1, CC, USB-Paar zum Modul (TPD2EUSB30 10.1, Espressif, Y-03)
# =============================================================================================
DP, DN = 'USB_DP_C', 'USB_DN_C'
# Stecker-GND (A12/B1, A1/B12) direkt in die Schirmpads (THT, an allen GND-Lagen)
T('GND', F, [(172.12, 124.8), (172.12, 124.0)], 0.4); T('GND', F, [(172.12, 131.2), (172.12, 132.0)], 0.4)
# D+: B6 und A6 über eine Schleife hinter den Padenden verbunden (kein Via)
T(DP, F, [(172.12, 127.25), (172.95, 127.25), (172.95, 128.25), (172.12, 128.25)], 0.15)
# Hauptpaar A7 (D-) / A6 (D+) zu U1; D- macht über dem Landevia einen Bogen nach oben
T(DN, F, [(171.54, 127.75), (170.2, 127.75), (169.9, 127.45), (169.2, 127.45), (168.9, 127.75), (167.57, 127.75), (167.42, 127.65)], 0.25)
T(DP, F, [(171.54, 128.25), (167.57, 128.25), (167.42, 128.35)], 0.25)
# D- B7: einziger Lagenwechsel (B.Cu-Brücke unter dem D+-Leiter) – nötig, weil D+/D- am Stecker abwechseln
T(DN, F, [(171.54, 128.75), (169.85, 128.75), (169.55, 129.0)], 0.15)
V(DN, 169.55, 129.0); T(DN, B, [(169.55, 129.0), (169.55, 127.45)], 0.25); V(DN, 169.55, 127.45)
# CC1 / CC2 zu den gedrehten Rd-Widerständen
T('/Versorgung/CC1', F, [(171.54, 129.25), (171.3, 129.25), (170.9, 129.65), (167.82, 129.65)], 0.2)
T('/Versorgung/CC2', F, [(171.54, 126.25), (170.4, 126.25), (169.5, 125.35), (169.22, 125.35)], 0.2)
V('GND', 165.75, 124.4); T('GND', F, [(166.78, 125.3), (165.75, 124.4)], 0.3)                     # R2.2
V('GND', 164.9, 131.3); T('GND', F, [(165.78, 130.38), (164.9, 131.3)], 0.3)                      # R1.2
T('GND', F, [(164.47, 131.22), (164.9, 131.3)], 0.3)                                               # C18.2
V('GND', 164.0, 123.7); T('GND', F, [(164.0, 124.28), (164.0, 123.7)], 0.3)                       # C17.2
# VBUS: obere Pads (A9/B4) über B.Cu zu den unteren (A4/B9); ESD D3 direkt an den unteren Pads
T('/Versorgung/USB_VBUS', F, [(171.54, 125.6), (171.0, 125.6)], 0.4); V('/Versorgung/USB_VBUS', 171.0, 125.6)
T('/Versorgung/USB_VBUS', B, [(171.0, 125.6), (171.0, 130.45)], 0.5); V('/Versorgung/USB_VBUS', 171.0, 130.45)
T('/Versorgung/USB_VBUS', F, [(171.54, 130.4), (171.0, 130.45), (170.6, 130.6)], 0.4)
V('GND', 168.0, 130.9); T('GND', F, [(168.6, 130.6), (168.0, 130.9)], 0.3)                         # D3.2
# VBUS weiter: Stichleitung nach unten zu TP5, Ast nach links zu C2 (eFuse IN) und R3 (UVLO-Teiler)
T('/Versorgung/USB_VBUS', F, [(171.0, 130.45), (171.0, 139.7), (170.4, 140.3)], 0.3)
T('/Versorgung/USB_VBUS', F, [(171.0, 132.35), (164.62, 132.35), (164.62, 132.9)], 0.4)
T('/Versorgung/USB_VBUS', F, [(164.62, 132.35), (161.07, 132.35), (161.07, 133.95)], 0.3)
T('/Versorgung/USB_VBUS', F, [(164.62, 133.6), (165.25, 134.25), (165.25, 135.4)], 0.3)
# U1-GND mit eigenem Via (TI: großes Via, kurzer Weg)
V('GND', 165.75, 128.0); T('GND', F, [(166.43, 128.0), (165.75, 128.0)], 0.3)
# Paar von U1 weiter: D- oben, D+ unten; C17/C18 (DNP) liegen mit dem Signalpad direkt auf der Leitung
T(DN, F, [(167.42, 127.5), (167.42, 126.75), (161.0, 126.75), (161.0, 123.6), (150.6, 123.6), (150.6, 118.83), (150.18, 118.83)], 0.25)
T(DP, F, [(167.42, 128.5), (167.42, 128.95), (165.2, 128.95), (164.9, 129.2), (160.6, 129.2), (160.6, 124.0), (148.9, 124.0),
          (148.9, 120.4), (149.38, 120.4)], 0.25)
# Modulseite der Serienwiderstände
T('Net-(U4-USB_D-)', F, [(151.82, 118.83), (152.5, 118.83)], 0.25)
T('Net-(U4-USB_D+)', F, [(151.82, 120.4), (152.2, 120.1), (152.5, 120.1)], 0.25)

# =============================================================================================
# D) eFuse U2 (TPS25947 8.4.1): Hilfsbauteile an ihren Pins, lokale GND-Insel mit einem Sternpunkt
# =============================================================================================
T('GND', F, [(166.7, 136.73), (169.4, 136.73)], 0.2)                       # Pin 8 GND nach rechts
T('GND', F, [(169.4, 133.3), (169.4, 138.4)], 0.3)                         # GND-Stamm durch C4.2, R6.2, C3.2
T('GND', F, [(166.17, 133.3), (169.4, 133.3)], 0.3)                        # C2.2 zum Stamm
V('GND', 170.25, 136.9); T('GND', F, [(169.4, 136.9), (170.25, 136.9)], 0.3)   # Sternpunkt zu L2
T('Net-(U2-ILM)', F, [(166.7, 136.27), (167.38, 136.27)], 0.2)
T('Net-(U2-DVDT)', F, [(166.7, 137.2), (167.1, 137.2), (167.5, 137.6)], 0.2)
T('Net-(U2-ITIMER)', F, [(166.7, 135.8), (167.0, 135.8), (167.0, 134.9), (167.5, 134.4)], 0.2)
T('Net-(U2-EN{slash}UVLO)', F, [(163.12, 134.4), (164.3, 135.55), (164.6, 135.75)], 0.2)
T('Net-(U2-EN{slash}UVLO)', F, [(162.32, 134.88), (161.47, 135.72)], 0.2)
T('Net-(U2-OVLO)', F, [(163.12, 136.27), (164.5, 136.27)], 0.2)
T('Net-(U2-OVLO)', F, [(162.32, 136.68), (161.47, 137.53)], 0.2)
V('GND', 162.72, 139.25); T('GND', F, [(162.72, 138.47), (162.72, 139.25)], 0.3)                  # R5.2
# OUT → VBUS_PROT-Fläche mit C5, D4-Anode, TP6
T('VBUS_PROT', F, [(165.75, 137.6), (165.75, 138.3)], 0.3)
Z('VBUS_PROT', 'VBUS_PROT', F, [(164.6, 138.0), (167.15, 138.0), (167.15, 138.7), (168.6, 138.7), (168.6, 143.6), (170.85, 143.6),
                                (170.85, 145.6), (164.6, 145.6)])
V('GND', 166.4, 141.15); T('GND', F, [(166.37, 140.47), (166.4, 141.15)], 0.3)                    # C5.2
# D4-Kathode (VIN_SYS) mit zwei Vias zur L3-VIN-Fläche
Z('VIN D4', 'VIN_SYS', F, [(161.6, 142.55), (164.35, 142.55), (164.35, 145.8), (161.6, 145.8)])
V('VIN_SYS', 162.3, 145.25); V('VIN_SYS', 163.6, 145.25)


def main(path):
    b = pcbnew.LoadBoard(path); fm = pcbnew.FromMM
    P = lambda x, y: pcbnew.VECTOR2I(fm(x), fm(y))
    # erst alles Alte einsammeln, dann entfernen (nach BOARD.Remove() verliert SWIG die Typen der übrigen Objekte)
    old_z = [z for z in b.Zones() if z.GetZoneName().startswith(ZPFX)]
    old_g = [g for g in b.Groups() if g.GetName() == GROUP]
    old_i = [it for g in old_g for it in g.GetItems()]
    for it in old_i + old_z + old_g:
        b.Remove(it)
    grp = pcbnew.PCB_GROUP(b); grp.SetName(GROUP); b.Add(grp)
    net = lambda n: b.FindNet(n) if b.FindNet(n) else sys.exit(f'Netz fehlt: {n}')
    for n, layer, pts, w in TRACKS:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(fm(w)); t.SetLayer(layer)
            t.SetNet(net(n)); b.Add(t); grp.AddItem(t)
    for n, x, y in VIAS:
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(fm(VIA_D)); v.SetDrill(fm(VIA_DRILL)); v.SetNet(net(n))
        b.Add(v); grp.AddItem(v)
    for name, n, layer, poly, prio in ZONES:
        z = pcbnew.ZONE(b); z.SetZoneName(ZPFX + name); z.SetLayer(layer); z.SetNet(net(n)); z.SetAssignedPriority(prio)
        z.SetLocalClearance(fm(0.2)); z.SetMinThickness(fm(0.2)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for x, y in poly: ps.Append(fm(x), fm(y))
        z.SetOutline(ps); ps.thisown = 0
        b.Add(z)
    b.Save(path)
    print(f'manuell: {len(TRACKS)} Bahnzüge, {len(VIAS)} Vias, {len(ZONES)} Flächen', flush=True)
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, 'zones.py'), path, '--fill-stage'], check=True)
    os._exit(0)


if __name__ == '__main__':
    main(sys.argv[1])
