# Phase 3 – Kontur, Platzierung, Transientennachweis

Stand: 2026-10-13 (Überarbeitung nach Layout-Leitfäden) · Leiterplatte: `LandyHeater.kicad_pcb` · Regeln: `LandyHeater.kicad_dru`

## 1. Ergebnis

| Prüfung | Ergebnis |
|---|---|
| Kontur | 80 × 50 mm, Ecken R 2 mm (M-05) |
| Bestückung | alle 131 Bauteile auf der Oberseite |
| Befestigung | 4 × M3 (3,2 mm, NPTH) in den Ecken, 3,3 mm Freiraum |
| Passermarken | 3 × 1 mm / Maske 2 mm bei (104,5 / 109,5), (104,5 / 140), (172 / 135,5), ≥ 3,35 mm vom Rand, unsymmetrisch |
| Courtyard-Kollisionen | keine |
| DRC | 0 Fehler außer 249 nicht gerouteten Verbindungen (Phase 4) |
| ERC / Netzlistenprüfung N-05 | 0 Fehler (1 begründete Warnung F1) / 0 Abweichungen nach GPIO-Neubelegung |
| Schaltplan-Parität | 0 Fehler |
| Layout-Checkliste B7 | Abschnitt 4 |
| Transienten (V-01) | Abschnitt 5 |

## 2. Überarbeitung gegenüber dem ersten Entwurf

Der erste Entwurf war nach Zonen gepackt, aber nicht auf kurze Verbindungen optimiert. Daraus folgten lange Wege: USB-Zickzack, U0TXD 50 mm, Diagnose-Widerstände 30 mm von ihren LEDs. Deshalb drei Änderungen.

**GPIO-Neubelegung (A12, Anforderungsdokument 2.1):** Jeder Block liegt an der Modulseite, die ihm zugewandt ist. Fest bleiben EN, GPIO0, GPIO19/20 (USB) und GPIO43/44 (UART0).

| Block | Modulpads (GPIO) | Lage des Blocks |
|---|---|---|
| Status-LEDs, DIAG_RUN | 4, 5, 6 (GPIO4–6) | links oben |
| RTC_INT_N, I2C | 7, 8, 9 (GPIO7, 15, 16) | links Mitte (RTC) |
| AUTOTERM TX/RX/OE | 10, 11, 12 (GPIO17, 18, 8) | links unten → J2 |
| USB | 13, 14 (fest) | links unten, Serien-R direkt am Pad |
| Taster/LED | 17, 18 (GPIO9, 10) | unten → J4 |
| 1-Wire | 21, 22 (GPIO13, 14) | unten → J3 |
| BOOT, UART0 | 27, 36, 37 (fest) | rechter Streifen |

**Steckerreihenfolge:** J1, J2, J4 (Taster/LED), J3 (1-Wire) von links nach rechts. J3 und J4 sind getauscht, damit beide Blöcke unter ihren Modulpads liegen. A6 legt keine Reihenfolge fest.

**Verbindungsorientierte Platzierung:** Die Platzierung minimiert die Verbindungslängen (Simulated Annealing, mehrere Läufe, bester übernommen). Höher gewichtet sind Abblockung, USB, UART und Buck-Schleife; der Schutz sitzt direkt am Stecker. Feste Vorgaben:
- Modul, Stecker, Löcher und Knopfzelle.
- Diagnose-LEDs als Reihe im Energiefluss: 12 V, USB, 3V3, RUN, AUTOTERM.

Jeder Block bleibt in seinem Bereich, Überlappungen sind ausgeschlossen.

| Verbindung (Spannbaum ohne Testpunkte) | vorher | nachher |
|---|---:|---:|
| USB D− / D+ Modul → Serien-R | 16,9 / 17,2 mm | 2,1 / 3,7 mm |
| USB D− / D+ Serien-R → Stecker/ESD | 26,5 / 23,6 mm | 24,7 / 23,2 mm |
| U0TXD Modul → 499 Ω | 50,2 mm | 2,1 mm |
| BOOT_N | 34,8 mm | 6,8 mm |
| RTC_INT_N | 44,9 mm | 15,6 mm |
| I2C SDA / SCL | 26,9 / 30,4 mm | 14,2 / 15,4 mm |
| BUTTON_N / BUTTON_LED_PWM | 44,8 / 25,6 mm | 16,2 / 12,2 mm |
| 1WIRE_DQ / SENSOR_EN | 17,8 / 23,5 mm | 4,9 / 12,4 mm |
| AUTOTERM TX / RX / OE | 24,3 / 26,3 / 30,5 mm | 24,5 / 21,4 / 23,8 mm |
| STATUS_LED_1 / 2 | 36,6 / 39,2 mm | 8,3 / 7,0 mm |
| Diagnose-LED zu Vorwiderstand (3V3, AUTOTERM, RUN) | 25,7 / 29,4 / 34,3 mm | 1,9 / 10,8 / 1,9 mm |
| BATT_12V_IN (J1 → TVS → Verpolschutz) | 15,6 mm | 11,0 mm |
| SW-Knoten Buck | 11,5 mm | 5,8 mm |
| **Summe aller Netze außer GND und 3V3** | **1377 mm** | **729 mm** |

**Schutzbauteile zum Steckerpin** (Padmitte):
- J1: D1 TVS 4,5 mm, D2 6,6 mm.
- J2: D7 2,6 mm, D8 3,1/4,2 mm.
- J4: D10 2,6 mm.
- J3: D9 2,9/2,8 mm.
- J5: U1 1,6 mm, D3 2,3 mm.

Lang bleiben nur die Diagnoseleitungen (`DIAG_RUN` 34 mm, `VBUS_PROT` zur USB-Diagnose-LED). Sie sind langsam und bewusst so geführt, weil die Diagnose-LEDs gemeinsam oben links sitzen.

## 3. Platzierung

| Bereich | Lage | Bauteile |
|---|---|---|
| 12-V-Eingang | über J1 | D1 TVS und D2 direkt am Stecker, FB1, C1 |
| 3,3-V-Buck | links Mitte | U3, L1, C6–C11; CIN 100 nF 1,6 mm vom VIN-Pin |
| Diagnose | oben links | LED-Reihe D11, D12, D13, D19, D14; SW3, Q1, BAS116, Vorwiderstände direkt an den LEDs |
| RTC | Mitte oben | BT1, U6 am Modul (Pads 7–9), D5/D6, C19 |
| Reset, Status | links neben dem Modul | SW1 RESET an EN, U5, C12–C15, D20/D21 |
| ESP32-S3-WROOM-1U | oben rechts | U.FL am oberen Rand, keine Leitungen unter dem U.FL |
| BOOT, UART0 | rechter Streifen | SW2 BOOT an GPIO0, R11 2 mm vom U0TXD-Pad, TP10/TP11 |
| USB | rechts | J5 am Rand, U1 ESD und D3 direkt am Stecker, R9/R10 am Modul |
| eFuse | unter J5 | U2, R3–R6, C2–C5, D4 |
| AUTOTERM | über J2 | U7, D7, D8, R15–R18, C20–C22 |
| Taster/LED | über J4 | U9, F1, D10, R22–R25, C25 |
| 1-Wire | über J3 | U8, D9, R19–R21, C23/C24 |

**Taster:** SW1 = RESET (links neben dem Modul, oben), SW2 = BOOT (rechts neben dem Modul), SW3 = DIAG (bei den Diagnose-LEDs). Die Bestückungsdruck-Beschriftung „RST“, „BOOT“, „DIAG“ folgt bei der Beschriftungsbereinigung (P3-02).

## 4. Layout-Checkliste (Anforderungsdokument B7)

| # | Regel | Stand Phase 3 |
|---|---|---|
| G-01 | 3V3 ≥ 0,65 mm | Netzklasse Power auf 0,65 mm erhöht ✅ |
| G-02 | 100 nF ≤ 2 mm vom Versorgungspin | Padmitte zu Padmitte 1,4–2,7 mm, Kante zu Kante ≤ 1 mm: U4 2,0 · U3 1,6 · U5 1,7 · U6 1,4 · U7 2,0 · U8 1,5 · U2 2,2 mm ✅ |
| G-03 | U0TXD-Serien-R am Modul | 2,1 mm ✅ |
| G-04 | USB-Serien-R am Modul, ESD am Stecker | R9/R10 2,1/3,7 mm vom Pad, U1 1,6 mm von J5 ✅; Impedanz und Rückführungsvias in Phase 4 |
| G-05 | USB/UART fern vom U.FL | USB unten links am Modul; UART-Testpads rechts, ≈ 10 mm vom U.FL ✅ |
| G-06 | In1.Cu durchgehend GND, Vias um das Modul | Phase 4 |
| G-07 | Schutz direkt am Stecker | alle Schutzbauteile 1,6–4,5 mm vom Steckerpin (Abschnitt 2) ✅ |
| G-08 | Buck-Schleife klein, VOUT-Messung fern vom SW-Knoten | CIN 1,6 mm, VCC-Kondensator 1,7 mm, SW-Knoten 5,8 mm ✅; Messleitung in Phase 4 |
| G-09 | GND-Vias an den Kondensatoren | Phase 4 |
| G-10 | 3 Passermarken | ✅ |
| G-11 | Nutzenränder für die Bestückung | Phase 5 |
| G-12 | Masse ungeteilt | Phase 4 |
| G-13 | kurze Wege, Signalfluss, gepolte Teile einheitlich | Abschnitt 2 ✅; gepolte Teile nur in 0° oder 90° (Kathode links bzw. oben) |

## 5. Designregeln

Die Netzklassen stehen auf 0,15 mm, die Regeln in `LandyHeater.kicad_dru` setzen den allgemeinen Abstand. KiCad verwendet nämlich den größeren Wert aus Netzklasse und Regel, sonst wären keine Ausnahmen möglich.

| Regel | Wert | Grund |
|---|---|---|
| Kupferabstand | 0,2 mm | allgemein |
| Pad-Pad in U2, U3, U6, U7 | 0,12 mm | Hersteller-Footprints (VSSOP 0,5 mm, VQFN-HR) haben 0,15 mm; JLCPCB-Minimum 0,09 mm |
| USB-Paar | 0,13 mm | Spalt im Differenzpaar |
| Bohrung zu Kupfer | 0,25 mm | allgemein |
| USB-C J5 | 0,15 mm | NPTH-Führungsstifte zu GND-Pads laut GCT-Footprint (0,194 mm) |
| Bohrung Minimum | 0,2 mm | Wärmevias im ESP32-Footprint; JLCPCB 4 Lagen ab 0,15 mm |
| Netzklasse Power | 0,65 mm Bahn | G-01 |

## 6. Transientennachweis V-01 (P-03)

**Angenommenes Profil:** Typische lokale Schalttransienten im 12-V-Netz, angelehnt an ISO 7637-2, Pegel IV. Das ist keine Zertifizierung (P-03).

**Modell:** `sim/v01_transienten.py`, ngspice aus KiCad.
- TVS D1 mit ungünstiger Durchbruchspannung 22,1 V und V<sub>C</sub> 29,2 V bei 20,5 A.
- SS16 mit 60 V Sperrspannung.
- Ferrit mit 1 µH ∥ 600 Ω.
- C1 47 µF mit 0,3 Ω ESR; C6 4,7 µF auf 2,5 µF reduziert (DC-Bias).
- Buck mit kleiner Last (1 W).

| Puls | V(J1) max/min | VIN_SYS max | U<sub>R</sub> D2 | P D1 | E D1 |
|---|---|---|---|---|---|
| 2a +112 V, 2 Ω, 50 µs | 37,4 / 7,7 V | 24,9 V | 10 V | 768 W | 7 mJ |
| 2a wie oben, 100 µs | 37,4 / 7,7 V | 28,6 V | 14 V | 772 W | 22 mJ |
| 1 −150 V, 10 Ω, 2 ms (Batterie getrennt) | −31,3 V | 13,5 V | 45 V | 370 W | 189 mJ |
| 3a −220 V, 50 Ω, 0,1 µs | −25,1 V | 13,5 V | 60 V¹ | 75 W | < 0,1 mJ |
| 3b +150 V, 50 Ω, 0,1 µs | 24,7 V | 13,5 V | 2,5 V | 61 W | < 0,1 mJ |

| Bauteil | Grenze | Höchstwert | Reserve |
|---|---|---|---|
| U3 LMR43620 VIN | 42 V absolut, 36 V Betrieb | 28,6 V | 21 % auf Betriebsgrenze |
| C1 Elko | 35 V | 28,6 V | 18 % |
| C6 | 50 V | 28,6 V | 43 % |
| U9 BCR421 (an VIN_SYS über F1) | 40 V | 28,6 V | 28 % |
| D1 Spitzenleistung | ≈ 2,7 kW bei 50 µs (600 W bei 1 ms, ∝ t<sup>−½</sup>) | 772 W | ausreichend |
| D1 Energie | ≈ 0,86 J (10/1000 µs, 600 W) | 0,19 J | ausreichend |
| D2 SS16 Sperrspannung | 60 V | 45 V (Puls 1) | 25 % |
| D4 SS16 (VIN_SYS gegen USB) | 60 V | 28,6 V | 52 % |
| eFuse U2 (P1-01) | IN ≥ OUT − 21 V | durch D4 getrennt | erfüllt |

¹ Bei Puls 3a erreicht D2 im Modell für etwa 15 ns die Durchbruchspannung, mit 39 nJ Lawinenenergie. Die Ursache ist die Resonanz der Ferrit-Induktivität mit der Sperrschichtkapazität von D2. Mit realistischen Ferritverlusten oder 22 pF Leiterbahnkapazität an `12V_PROT` bleibt sie bei ≤ 51 V. Das ist unkritisch; s. Empfehlung E-01.

**Grenzen der Schutzschaltung:**
- **Lastabwurf ohne zentrale Begrenzung** (ISO 16750-2 Test A) wird nicht beherrscht. Die TVS würde überlastet und niederohmig ausfallen; die externe 1-A-Sicherung (P-01) trennt dann.
- **Lastabwurf mit zentraler Begrenzung auf ≈ 35 V** (Test B) überlastet die TVS ebenfalls, weil die SMBJ18CA ab ≈ 20 V leitet.
- Beides ist für einen Verbraucherkreis an einer Zweitbatterie hinter Ladebooster nicht zu erwarten und keine Anforderung.

## 7. Empfehlungen und offene Punkte

| # | Punkt | Phase |
|---|---|---|
| E-01 | Optional 100 nF / 50 V (0603) von `12V_PROT` nach GND vor FB1. Begrenzt die Spitze aus Puls 3a an D2 auf 25 V und verbessert das Eingangsfilter. Kleine Schaltplanänderung. | Entscheid Auftraggeber |
| P3-01 | Footprints aus Bibliothek aktualisieren (26 Rundungswarnungen gedrehter Footprints) | 4 |
| P3-02 | Beschriftung bereinigen: RST/BOOT/DIAG, Energiefluss-Grafik an der Diagnose-LED-Reihe, Steckerbelegung | 4 |
| P3-03 | USB-Impedanz mit dem JLCPCB-Rechner bestätigen (P2-03) | 4 |
| P3-04 | 3D-Ansicht im KiCad-3D-Viewer prüfen (`kicad-cli pcb render` liefert ohne Grafikkontext leere Bilder) | 4 |
| P3-05 | Steckerreihenfolge J1, J2, J4, J3 in Gehäuse und Kabelbaumzeichnung übernehmen | Mechanik |

## 8. Freigabekriterien Phase 3

- [x] Kontur innerhalb 80 × 50 mm
- [x] alle Bauteile einseitig platziert, keine Courtyard-Kollision
- [x] Befestigungslöcher mit Freiraum, Passermarken
- [x] Stecker am Rand, Schutzbauteile am Stecker
- [x] kurze Verbindungen, Abblockung am Pin (Layout-Checkliste B7)
- [x] DRC ohne Fehler außer nicht gerouteten Verbindungen; ERC und Netzlistenprüfung ohne Abweichung
- [x] Transientenprofil festgelegt und mit SPICE nachgewiesen (V-01)
- [ ] Freigabe durch Auftraggeber
