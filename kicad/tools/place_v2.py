"""Platzierung v2 – hierarchisch nach Floorplan (Platzierung_1_Analyse_Floorplan.md).

Reihenfolge nach den PCB Layout Engineering Instructions:
  1. mechanische Anker  2. große ICs  3. kritische Passive  4. übrige Bauteile  5. Testpunkte
Jede Position ist explizit und begründet; keine Zufallsoptimierung.

Aufruf (KiCad-Python, Board im Projektordner):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/place_v2.py LandyHeater.kicad_pcb

Drehsinn KiCad: rot 90 bildet einen Pad-Offset (x0, y0) auf (x + y0, y - x0) ab, rot 180 auf (x - x0, y - y0),
rot 270 auf (x - y0, y + x0).
"""
import sys
import pcbnew

# (x, y, rot) in mm, Platinenursprung (100, 100), y nach unten
P = {}

# ---------------------------------------------------------------------------------------------
# 1. Mechanische Anker (freigegeben, unverändert)
# ---------------------------------------------------------------------------------------------
P.update({
    'H1': (104, 104, 0), 'H2': (176, 104, 0), 'H3': (104, 146, 0), 'H4': (176, 146, 0),
    # Nano-Fit an der Unterkante (M-07), Reihenfolge J1, J2, J4, J3 (freigegeben)
    'J1': (113, 139.07, 270), 'J2': (129, 139.07, 270), 'J4': (145, 139.07, 270), 'J3': (157, 139.07, 270),
    'J5': (175.8, 128, 90),          # USB-C rechte Kante (M-06)
    'U4': (162, 112, 0),             # Modul oben rechts, U.FL an der Oberkante (M-08)
    'BT1': (134.6, 107.2, 0),        # Knopfzelle oben Mitte, ruhige Zone (Z4), zugänglich (M-08)
    # RESET und BOOT nebeneinander am rechten Rand (zugänglich, M-08). EN läuft unter dem Modul auf L3/L4 –
    # langsam und mit 10 kΩ/1 µF gefiltert; dadurch bleibt die linke Modulkante für den Pad-Fan-out frei.
    'SW1': (175.8, 111.0, 0), 'SW2': (175.8, 117.6, 0),
    'SW3': (104.0, 113.0, 0),        # DIAG links unter der Diagnoseanzeige
    # Diagnose-LEDs nach G-01: 12V und USB übereinander, Zusammenführung -> 3V3 -> RUN -> HEAT.
    # Bild x 108,5–125,2 / y 100,6–106,3 bleibt frei für Beschriftung und Verbindungslinien (Silkscreen).
    # Alle LEDs 0°: Kathode links, Anode rechts.
    'D11': (112.6, 101.45, 0), 'D12': (112.6, 105.75, 0),
    'D13': (116.9, 103.6, 0), 'D19': (120.3, 103.6, 0), 'D14': (123.7, 103.6, 0),
    # Status-LEDs links am Modul in einer Spalte mit ihren Widerständen, sichtbar (G-06)
    'D20': (144.5, 107.4, 180), 'D21': (144.5, 111.0, 180),
    # Passermarken (G-10): unsymmetrisches Dreieck, >= 3,35 mm vom Rand, 2 mm Freiraum
    'FID1': (104.5, 140.5, 0), 'FID2': (175.5, 140.5, 0), 'FID3': (124.0, 116.75, 0),
})

# ---------------------------------------------------------------------------------------------
# 2. Große ICs, Ausrichtung nach Datenblatt
# ---------------------------------------------------------------------------------------------
P.update({
    # U3 LMR43620 (TI 8.5.1/Fig. 8-32): VIN links unten, GND oben links/Mitte, SW rechts unten, VOUT rechts oben.
    'U3': (110.0, 118.5, 0),
    'L1': (115.6, 117.6, 270),       # Pad 1 (SW) unten neben U3.5, Pad 2 (VOUT) oben
    # U2 TPS25947 unter J5; EN/OVLO links (Teiler), ILM/ITIMER/DVDT/GND rechts
    'U2': (165.5, 136.5, 0),
    # U1 TPD2EUSB30 direkt an J5 D+/D- (TI 10.1), Durchfluss: D+ 128,35 / D- 127,65 = J5 A6/A7
    'U1': (170.1, 128.0, 90),
    # U7 TXU0202, 180°: B-Seite (5 V, Kabel) unten zu J2, A-Seite (3,3 V) oben zum Modul
    'U7': (128.6, 128.3, 180),
    # U8 TPS22945 über J3
    'U8': (156.3, 128.6, 0),
    # U9 BCR421 über J4, OUT-Pins mit Kupferfläche (Wärme)
    'U9': (136.4, 133.2, 0),
    # U5 TPS3808, 270°: ~RESET oben rechts zum EN-Pad, VDD unten. Rechte Kante <= 150,85, damit vor den
    # Modulpads 4–12 ein Streifen x 150,9–152,2 für die Fan-out-Vias (Pitch 1,27 mm) frei bleibt.
    'U5': (149.1, 109.6, 270),
    # U6 RV-8263 am rechten Ende des RTC-Streifens, > 20 mm vom SW-Knoten (Y-04)
    'U6': (139.2, 115.7, 0),
    'Q1': (120.4, 111.85, 0),        # RUN-Schalter der Diagnoseanzeige
})

# ---------------------------------------------------------------------------------------------
# 3. Kritische Passive
# ---------------------------------------------------------------------------------------------
P.update({
    # Buck-Hot-Loop: C7 (100 nF) zwischen VIN (Pad 3/4) und GND (Pad 1), C6 (4,7 µF) daneben
    'C7': (107.55, 118.5, 90), 'C6': (105.4, 118.5, 90),
    'C9': (112.4, 118.8, 90),        # CBOOT zwischen BOOT (Pad 6) und SW (Pad 5)
    'C8': (112.4, 115.7, 90),        # CVCC an Pad 7, GND oben
    'C10': (119.4, 117.0, 270), 'C11': (119.4, 121.8, 270),   # COUT am L1-Ausgang
    # 12-V-Eingang: TVS an J1 (Pad 2 = BATT über J1.1, Pad 1 = GND über J1.2), Kette nach oben
    'D1': (111.4, 134.9, 0),
    'D2': (117.3, 133.3, 270),       # Anode unten (BATT), Kathode oben (12V_PROT)
    'FB1': (117.3, 127.3, 90),       # 12V_PROT unten, VIN_SYS oben
    'C26': (113.8, 129.5, 180),      # 100 nF an 12V_PROT vor FB1 (E-01)
    'C1': (105.6, 128.9, 180),       # 47 µF Bulk an VIN_SYS, + rechts
    # ESP32: 100 nF direkt an Pad 2, 22 µF daneben; EN-RC an Pad 3
    'C14': (150.6, 104.8, 180), 'C12': (149.2, 101.7, 0), 'C13': (145.9, 104.6, 0),
    'C15': (150.6, 106.4, 180), 'R7': (144.6, 101.7, 0),
    'C16': (149.1, 112.6, 0),        # U5 VDD, unter U5
    'R9': (150.6, 118.83, 180), 'R10': (150.6, 120.4, 180),   # USB-Serien-R an Pad 13/14
    'R11': (173.6, 108.3, 0),        # U0TXD 499 Ω an Pad 37
    'R8': (178.9, 121.0, 90),        # BOOT-Pull-up
    'C19': (141.6, 115.6, 90),       # RTC VDD
    # USB-Eingang
    'D3': (169.6, 130.6, 0),         # VBUS-ESD an J5 VBUS (130,4)
    'R2': (168.0, 125.3, 0),         # CC2 (126,25) oberhalb des Paares
    'R1': (166.6, 129.9, 0),         # CC1 (129,25) unterhalb des Paares
    'C17': (164.0, 126.0, 270), 'C18': (164.0, 130.0, 90),    # DNP, Pads direkt am Paar (stubfrei)
    'C2': (165.4, 133.3, 0),         # eFuse IN
    'R3': (161.9, 134.4, 0), 'R4': (161.9, 136.2, 0), 'R5': (161.9, 138.0, 0),   # Teiler an EN/OVLO
    'R6': (168.6, 136.3, 0), 'C3': (168.6, 138.0, 0), 'C4': (168.6, 134.6, 0),   # ILM, DVDT, ITIMER
    'C5': (165.6, 140.0, 0),         # eFuse OUT
    'D4': (165.0, 143.6, 0),         # ODER-Diode VBUS_PROT -> VIN_SYS
    # AUTOTERM
    'D7': (129.0, 135.4, 90),        # AUTOTERM_5V-ESD an J2.1
    'D8': (122.8, 134.2, 270),       # CTRL-ESD: RX links, TX rechts (wie J2), GND unten
    'C21': (132.3, 128.0, 90),       # VCCA
    'C22': (124.9, 128.4, 90), 'C20': (123.0, 128.4, 90),     # VCCB 100 nF + 1 µF
    # 1-Wire
    'D9': (155.75, 135.0, 90),       # Pins unten zu J3.2/J3.1, GND oben
    'C23': (158.6, 128.0, 90), 'C24': (153.9, 128.0, 90),     # VIN / VOUT
    # Taster/Ring-LED
    'D10': (145.9, 135.0, 90),       # Pin 1 über J4.1
    'F1': (140.0, 134.6, 270),       # VIN_SYS oben, LED_CC_PLUS unten zu J4.3
})

# ---------------------------------------------------------------------------------------------
# 4. Übrige Bauteile im jeweiligen Block
# ---------------------------------------------------------------------------------------------
P.update({
    # Diagnose Reihe 1 (y 106,8–109,9): Vorwiderstände, unter den Anoden von 3V3/RUN/HEAT; 12V/USB links daneben
    'R26': (111.4, 108.35, 90), 'R27': (113.2, 108.35, 90),
    'R28': (117.7, 108.35, 90), 'R30': (121.1, 108.35, 90), 'R29': (124.5, 108.35, 90),
    # Reihe 2 (y 110,1–113,6): Entkoppeldioden und RUN-Schalter Q1
    'D17': (116.3, 111.85, 0), 'D18': (124.4, 111.85, 0),
    # 12V/USB-Dioden und DIAG-Pulldown links unter H1
    'D15': (102.6, 109.3, 0), 'D16': (106.8, 109.3, 0), 'R31': (109.6, 111.6, 90),
    # RTC-Streifen unter BT1
    'D5': (131.0, 116.4, 0), 'D6': (135.2, 116.4, 0),
    # Status und I2C-/INT-Pull-ups links am Modul
    'R32': (144.5, 109.2, 0), 'R33': (144.5, 112.8, 0), 'R34': (144.5, 114.6, 0), 'R35': (144.5, 116.4, 0),
    'R14': (144.5, 118.2, 0),
    'R12': (149.1, 114.4, 0), 'R13': (149.1, 116.2, 0),
    # AUTOTERM
    'R15': (128.9, 132.5, 90), 'R16': (125.8, 132.3, 90), 'R17': (131.0, 132.3, 90), 'R18': (127.4, 125.5, 0),
    # 1-Wire
    'R19': (157.0, 131.0, 0), 'R21': (152.6, 131.0, 0), 'R20': (152.4, 132.8, 0),
    # Taster/Ring-LED
    'R22': (146.0, 131.0, 270), 'R23': (146.0, 127.7, 0), 'C25': (142.6, 129.0, 0),
    'R24': (135.6, 129.4, 0), 'R25': (135.6, 127.6, 0),
})

# ---------------------------------------------------------------------------------------------
# 5. Testpunkte, blockweise in Reihen
# ---------------------------------------------------------------------------------------------
P.update({
    'TP1': (102.0, 135.5, 0), 'TP2': (120.6, 130.2, 0),                           # 12-V-Eingang
    'TP3': (104.4, 123.0, 0), 'TP7': (107.4, 123.0, 0), 'TP4': (110.4, 123.0, 0),  # Buck: VIN_SYS, GND, 3V3
    'TP24': (109.3, 115.2, 0), 'TP25': (102.0, 117.6, 0), 'TP28': (112.4, 111.9, 0),   # Diagnose: DIAG_K, GND, RUN
    'TP19': (125.4, 120.6, 0), 'TP20': (128.2, 120.6, 0), 'TP21': (131.0, 120.6, 0),   # AUTOTERM 3,3 V
    'TP16': (125.4, 123.3, 0), 'TP17': (128.2, 123.3, 0), 'TP18': (131.0, 123.3, 0),   # AUTOTERM 5 V
    'TP14': (135.0, 122.0, 0), 'TP12': (137.8, 122.0, 0), 'TP13': (140.6, 122.0, 0),   # MCU-Reihe
    'TP8': (143.4, 122.0, 0), 'TP26': (146.2, 122.0, 0),
    'TP27': (138.8, 127.6, 0),                                                     # Ring-LED-PWM
    'TP22': (151.3, 126.5, 0), 'TP23': (151.4, 135.4, 0),                          # 1-Wire
    'TP10': (173.4, 114.3, 0), 'TP11': (176.2, 114.3, 0),                          # UART0 zwischen RESET und BOOT
    'TP9': (173.4, 121.0, 0), 'TP15': (176.2, 121.0, 0),                           # BOOT, GND
    'TP5': (170.0, 141.0, 0), 'TP6': (169.9, 144.6, 0),                            # VBUS, VBUS_PROT
})


def main(path):
    b = pcbnew.LoadBoard(path)
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    missing = sorted(r for r in fps if r not in P)
    unknown = sorted(r for r in P if r not in fps)
    if missing or unknown:
        raise SystemExit(f'nicht zugeordnet: {missing} | unbekannt: {unknown}')
    for r, (x, y, rot) in P.items():
        f = fps[r]
        f.SetOrientationDegrees(rot)
        f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    # Sperrflächen um die Passermarken (keine Leiterbahnen, Vias, Kupferflächen; Radius 2 mm), damit jeder
    # Router – auch Freerouting, das den lokalen Freiraum des Fiducial-Pads nicht kennt – Abstand hält.
    for z in list(b.Zones()):
        if z.GetIsRuleArea() and z.GetZoneName().startswith('Sperrfläche FID'):
            b.Remove(z)
    for r in ('FID1', 'FID2', 'FID3'):
        x, y, _ = P[r]
        z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetZoneName(f'Sperrfläche {r}')
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); ls.AddLayer(pcbnew.In1_Cu); ls.AddLayer(pcbnew.In2_Cu)
        z.SetLayerSet(ls)
        o = z.Outline(); o.NewOutline()
        for k in range(16):
            ang = 2 * 3.141592653589793 * k / 16
            o.Append(pcbnew.FromMM(x + 2.0 * __import__('math').cos(ang)), pcbnew.FromMM(y + 2.0 * __import__('math').sin(ang)))
        b.Add(z)
    b.Save(path)
    print(f'{len(P)} von {len(fps)} Footprints platziert, 3 Sperrflächen um die Passermarken')


if __name__ == '__main__':
    main(sys.argv[1])
