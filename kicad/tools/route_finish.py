"""Nacharbeit nach Freerouting (Schritt 6.6): restliche Verbindungen von Hand, gezielte Korrekturen an
Freerouting-Bahnen. Reihenfolge: place_v2 → route_manual → route_planevias → freeroute → route_finish → zones --fill-all.

- T/V wie in route_manual.py; alle Elemente in der Gruppe GROUP (bei jedem Lauf neu).
- DROP: Freerouting-Segmente, die einer Handverbindung im Weg sind (Netz, Punkt auf dem Segment); sie werden
  aus der Freerouting-Gruppe gelöscht. Danach Innenlagen füllen.

Aufruf (KiCad-Python, Board im Projektordner): python3 tools/route_finish.py LandyHeater.kicad_pcb
"""
import math
import os
import subprocess
import sys
import pcbnew

GROUP = 'Nacharbeit (tools/route_finish.py)'
FR_GROUP = 'Freerouting (tools/freeroute.py)'
VIA_D, VIA_DRILL = 0.6, 0.3
F, B = pcbnew.F_Cu, pcbnew.B_Cu
TRACKS, VIAS, DROP = [], [], []


def T(net, layer, pts, w=0.2):
    TRACKS.append((net, layer, pts, w))


def V(net, x, y):
    VIAS.append((net, x, y))


def D(net, x, y):
    """Freerouting-Segment/-Via des Netzes, das durch (x, y) geht, entfernen."""
    DROP.append((net, x, y))


BOOT, EN, RXD, TXD = '/ESP32 und RTC/BOOT_N', '/ESP32 und RTC/EN', 'Net-(U4-RXD0)', 'Net-(R11-Pad2)'

# ---------------------------------------------------------------------------------------------
# Rechts: RESET/BOOT-Taster, UART-Testpunkte (TP10 TX, TP11 RX)
#   RXD auf L1 in der Gasse zwischen Modulpads und SW1, unter SW1 hindurch zu TP11;
#   TXD (nach R11) über L4 von rechts neben R11 zu TP10; EN von SW1 über L4 unter dem Modul zum EN-Via (155,17/119,09)
# ---------------------------------------------------------------------------------------------
T(BOOT, F, [(170.75, 120.1), (172.6, 120.1), (173.2, 120.7)])                     # U4.27 → TP9
T(BOOT, F, [(173.75, 118.4), (177.85, 118.4)])                                     # SW2 Pin 2 links ↔ rechts
T(RXD, F, [(171.5, 108.67), (172.0, 109.17), (172.0, 112.9), (176.0, 112.9), (176.4, 113.7)])
T(TXD, F, [(174.43, 108.3), (175.4, 108.2)]); V(TXD, 175.4, 108.2)
T(TXD, B, [(175.4, 108.2), (175.4, 113.9), (175.0, 114.3)]); V(TXD, 175.0, 114.3); T(TXD, F, [(175.0, 114.3), (174.0, 114.3)])
T(EN, F, [(173.3, 111.8), (172.9, 111.4), (172.6, 111.0)]); V(EN, 172.6, 111.0)
T(EN, B, [(172.6, 111.0), (169.6, 114.0), (158.6, 114.0), (155.6, 117.0), (155.6, 118.66), (155.17, 119.09)])

# ---------------------------------------------------------------------------------------------
# Oben links: Diagnose-LEDs und DIAG-Taster
# ---------------------------------------------------------------------------------------------
DK = '/Taster und Anzeige/DIAG_K'
T('Net-(D19-A)', F, [(121.09, 103.6), (121.1, 107.53)])                              # D19.2 → R30.2, gerade
T('Net-(D20-A)', F, [(143.9, 107.8), (144.5, 108.3), (145.0, 108.8)])                # D20.2 → R32.2 durch die Gasse
T(DK, F, [(101.95, 113.8), (106.05, 113.8)])                                          # SW3 Pin 2 links ↔ rechts
T(DK, F, [(107.74, 109.3), (107.74, 113.0), (106.8, 113.8), (106.05, 113.8)])        # D16.3 → SW3
# D15/D16/SW3-Gruppe ↔ D17/Q1/D18-Gruppe: über L4 oberhalb der 12V/VBUS-Trassen (y 109,5)
V(DK, 107.74, 110.3); T(DK, B, [(107.74, 110.3), (108.54, 109.5), (116.4, 109.5), (117.0, 110.1), (117.0, 110.15)])
V(DK, 117.0, 110.15); T(DK, F, [(117.0, 110.15), (117.24, 110.6), (117.24, 111.7)])
D('DIAG_RUN', 110.4, 112.42)                                                          # doppelter Freerouting-Stich an R31

# ---------------------------------------------------------------------------------------------
# U7 (TXU0202): Freerouting hat CTRL_TX mit Via und Senkrechter direkt vor die linken U7-Pins gelegt und damit
# OE (Pin 6) und AUTOTERM_5V_F (Pin 7) eingesperrt → dieser CTRL_TX-Abschnitt (TP17 → R16.2) wird neu verlegt
# ---------------------------------------------------------------------------------------------
CT = '/AUTOTERM und 1-Wire/CTRL_TX'
for x, y in [(125.93, 128.03), (126.5, 128.03), (127.49, 127.48), (128.04, 126.93), (125.8, 130.0), (125.865, 128.09),
             (128.545, 126.44), (128.6, 124.1), (129.03, 125.2), (125.67, 131.47)]:
    D(CT, x, y)

# >>> maze_route.py (generiert, nicht von Hand ändern)
# kein Weg: /AUTOTERM und 1-Wire/AUTOTERM_5V_F (370 Schritte)
# kein Weg: /AUTOTERM und 1-Wire/AUTOTERM_5V_F (2500001 Schritte)
# kein Weg: AUTOTERM_OE (2500001 Schritte)
# AUTOTERM_OE: 199 Zellen, 3 Vias
T('AUTOTERM_OE', F, [(131.7, 120.4), (134.1, 120.4)], 0.2)
T('AUTOTERM_OE', B, [(134.1, 120.4), (142.2, 120.4)], 0.2)
T('AUTOTERM_OE', F, [(142.2, 120.4), (148.2, 120.4)], 0.2)
T('AUTOTERM_OE', B, [(148.2, 120.4), (150.9, 117.7), (151.2, 117.7)], 0.2)
V('AUTOTERM_OE', 134.1, 120.4)
V('AUTOTERM_OE', 142.2, 120.4)
V('AUTOTERM_OE', 148.2, 120.4)
# /AUTOTERM und 1-Wire/CTRL_TX: 77 Zellen, 2 Vias
T('/AUTOTERM und 1-Wire/CTRL_TX', F, [(128.4, 124.0), (129.0, 124.6), (129.0, 126.2), (128.3, 126.9), (128.0, 126.9)], 0.2)
T('/AUTOTERM und 1-Wire/CTRL_TX', B, [(128.0, 126.9), (126.2, 128.7), (126.2, 130.6)], 0.2)
T('/AUTOTERM und 1-Wire/CTRL_TX', F, [(126.2, 130.6), (126.2, 131.1)], 0.2)
V('/AUTOTERM und 1-Wire/CTRL_TX', 128.0, 126.9)
V('/AUTOTERM und 1-Wire/CTRL_TX', 126.2, 130.6)
# SENSOR_EN: 81 Zellen, 2 Vias
T('SENSOR_EN', F, [(163.5, 122.1), (163.5, 123.0)], 0.2)
T('SENSOR_EN', B, [(163.5, 123.0), (161.0, 125.5), (161.0, 126.1), (157.2, 129.9)], 0.2)
V('SENSOR_EN', 163.5, 123.0)
V('SENSOR_EN', 157.2, 129.9)
# BUTTON_LED_PWM: 204 Zellen, 2 Vias
T('BUTTON_LED_PWM', F, [(158.8, 122.1), (158.8, 122.9)], 0.2)
T('BUTTON_LED_PWM', B, [(158.8, 122.9), (158.0, 123.7), (143.2, 123.7)], 0.2)
T('BUTTON_LED_PWM', F, [(143.2, 123.7), (139.5, 127.4)], 0.2)
V('BUTTON_LED_PWM', 158.8, 122.9)
V('BUTTON_LED_PWM', 143.2, 123.7)
# /ESP32 und RTC/I2C_SDA: 152 Zellen, 1 Vias
T('/ESP32 und RTC/I2C_SDA', B, [(151.3, 112.7), (149.5, 114.5), (149.5, 115.6), (148.7, 116.4), (148.4, 116.4), (147.6, 117.2)], 0.2)
T('/ESP32 und RTC/I2C_SDA', F, [(147.6, 117.2), (147.6, 117.7), (145.5, 119.8), (137.9, 119.8)], 0.2)
V('/ESP32 und RTC/I2C_SDA', 147.6, 117.2)
# /ESP32 und RTC/RTC_INT_N: 33 Zellen, 1 Vias
T('/ESP32 und RTC/RTC_INT_N', F, [(139.4, 116.5), (139.4, 119.2)], 0.2)
T('/ESP32 und RTC/RTC_INT_N', B, [(139.4, 119.2), (139.4, 119.6)], 0.2)
V('/ESP32 und RTC/RTC_INT_N', 139.4, 119.2)
# /ESP32 und RTC/I2C_SCL: 90 Zellen, 2 Vias
T('/ESP32 und RTC/I2C_SCL', F, [(139.9, 121.8), (139.1, 121.0)], 0.2)
T('/ESP32 und RTC/I2C_SCL', B, [(139.1, 121.0), (137.0, 121.0)], 0.2)
T('/ESP32 und RTC/I2C_SCL', F, [(137.0, 121.0), (137.2, 120.8), (137.2, 116.3), (138.0, 115.5), (138.3, 115.5)], 0.2)
V('/ESP32 und RTC/I2C_SCL', 139.1, 121.0)
V('/ESP32 und RTC/I2C_SCL', 137.0, 121.0)
# Net-(U7-B2): 37 Zellen, 0 Vias
T('Net-(U7-B2)', F, [(130.2, 129.2), (130.2, 132.4), (130.6, 132.8)], 0.2)
# BUTTON_N: 18 Zellen, 0 Vias
T('BUTTON_N', F, [(146.4, 129.8), (146.5, 129.7), (146.5, 128.1)], 0.2)
# 1WIRE_DQ: 115 Zellen, 1 Vias
T('1WIRE_DQ', F, [(151.6, 130.6), (151.6, 130.1)], 0.2)
T('1WIRE_DQ', B, [(151.6, 130.1), (154.9, 130.1), (162.1, 122.9), (162.4, 122.9)], 0.2)
V('1WIRE_DQ', 151.6, 130.1)
# /ESP32 und RTC/VBAT: 63 Zellen, 0 Vias
T('/ESP32 und RTC/VBAT', F, [(135.0, 115.2), (135.9, 115.2), (141.2, 109.9)], 0.2)
# /AUTOTERM und 1-Wire/AUTOTERM_5V_F: 26 Zellen, 0 Vias
T('/AUTOTERM und 1-Wire/AUTOTERM_5V_F', F, [(126.60, 128.55), (125.55, 128.55), (125.35, 128.75)], 0.2)
# /AUTOTERM und 1-Wire/AUTOTERM_5V_F: 201 Zellen, 2 Vias
T('/AUTOTERM und 1-Wire/AUTOTERM_5V_F', F, [(129.35, 132.95), (129.55, 132.75), (129.55, 132.55)], 0.2)
T('/AUTOTERM und 1-Wire/AUTOTERM_5V_F', B, [(129.55, 132.55), (124.25, 132.55), (123.70, 132.00)], 0.2)
T('/AUTOTERM und 1-Wire/AUTOTERM_5V_F', F, [(123.70, 132.00), (123.70, 131.25), (126.40, 128.55), (126.60, 128.55)], 0.2)
V('/AUTOTERM und 1-Wire/AUTOTERM_5V_F', 129.55, 132.55)
V('/AUTOTERM und 1-Wire/AUTOTERM_5V_F', 123.70, 132.00)
# AUTOTERM_OE: 49 Zellen, 2 Vias
T('AUTOTERM_OE', F, [(126.90, 125.95), (126.90, 126.40)], 0.2)
T('AUTOTERM_OE', B, [(126.90, 126.40), (126.90, 126.85), (126.05, 127.70)], 0.2)
T('AUTOTERM_OE', F, [(126.05, 127.70), (126.40, 128.05), (126.60, 128.05)], 0.2)
V('AUTOTERM_OE', 126.90, 126.40)
V('AUTOTERM_OE', 126.05, 127.70)
# <<< maze_route.py


def main(path):
    b = pcbnew.LoadBoard(path); fm, mm = pcbnew.FromMM, pcbnew.ToMM
    old = [g for g in b.Groups() if g.GetName() == GROUP]
    if old:   # entfernen, speichern, neu starten (SWIG verliert nach BOARD.Remove() die Typen)
        for it in [it for g in old for it in g.GetItems()] + old:
            b.Remove(it)
        b.Save(path); sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, os.path.abspath(__file__), path])
    P = lambda x, y: pcbnew.VECTOR2I(fm(x), fm(y))
    net = lambda n: b.FindNet(n) if b.FindNet(n) else sys.exit(f'Netz fehlt: {n}')
    # zu löschende Freerouting-Elemente zuerst einsammeln
    fr = [g for g in b.Groups() if g.GetName() == FR_GROUP]
    drop = []
    for it in ([it for g in fr for it in g.GetItems()] if fr else []):
        if it.GetClass() not in ('PCB_TRACK', 'PCB_VIA'): continue
        for n, x, y in DROP:
            if it.GetNetname() != n: continue
            if it.GetClass() == 'PCB_VIA':
                hit = math.hypot(mm(it.GetPosition().x) - x, mm(it.GetPosition().y) - y) < 0.05
            else:
                ax, ay, bx, by = mm(it.GetStart().x), mm(it.GetStart().y), mm(it.GetEnd().x), mm(it.GetEnd().y)
                L = (bx - ax) ** 2 + (by - ay) ** 2
                t = 0 if L == 0 else max(0, min(1, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / L))
                hit = math.hypot(ax + t * (bx - ax) - x, ay + t * (by - ay) - y) < 0.05
            if hit: drop.append(it); break
    grp = pcbnew.PCB_GROUP(b); grp.SetName(GROUP); b.Add(grp)
    for n, layer, pts, w in TRACKS:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(fm(w)); t.SetLayer(layer)
            t.SetNet(net(n)); b.Add(t); grp.AddItem(t)
    for n, x, y in VIAS:
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(fm(VIA_D)); v.SetDrill(fm(VIA_DRILL)); v.SetNet(net(n))
        b.Add(v); grp.AddItem(v)
    for it in drop:
        b.Remove(it)
    b.Save(path)
    print(f'Nacharbeit: {len(TRACKS)} Bahnzüge, {len(VIAS)} Vias, {len(drop)}/{len(DROP)} Freerouting-Elemente entfernt', flush=True)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zones.py'), path, '--fill-stage'], check=True)
    os._exit(0)


if __name__ == '__main__':
    main(sys.argv[1])
