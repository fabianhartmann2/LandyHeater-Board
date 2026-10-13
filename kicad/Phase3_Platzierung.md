# Phase 3 – Kontur, Platzierung, Transientennachweis

Stand: 2026-10-13 · Leiterplatte: `LandyHeater.kicad_pcb` · Regeln: `LandyHeater.kicad_dru`

## 1. Ergebnis

| Prüfung | Ergebnis |
|---|---|
| Kontur | 80 × 50 mm, Ecken R 2 mm (M-05: maximal 80 × 50 mm) |
| Bestückung | alle 131 Bauteile auf der Oberseite (einseitige Bestückung) |
| Befestigung | 4 × M3 (3,2 mm, NPTH) bei (104, 104), (176, 104), (104, 146), (176, 146); 3,3 mm Freiraum für den Schraubenkopf |
| Courtyard-Kollisionen | keine |
| DRC | 0 Fehler außer 249 nicht gerouteten Verbindungen (Phase 4) |
| Schaltplan-Parität | 0 Fehler; 1 Warnung F1 (Footprint-Filter, s. Phase-2-Review) |
| Transienten (V-01) | Nachweis mit ngspice, s. Abschnitt 4 |

Verbleibende DRC-Warnungen und ihre Behandlung:

| Warnung | Anzahl | Behandlung |
|---|---|---|
| `silk_overlap`, `silk_over_copper`, `silk_edge_clearance`, `text_height` | 262 | Beschriftung wird nach dem Routing bereinigt (Phase 4) |
| `lib_footprint_mismatch` | 15 | nur gedrehte Footprints betroffen (Rundung beim Drehen); zu Beginn von Phase 4 mit „Footprints aus Bibliothek aktualisieren“ zurücksetzen |

## 2. Platzierung

| Bereich | Lage | Bauteile |
|---|---|---|
| 12-V-Eingang | unten links an J1 | D1 TVS, D2, FB1, C1, TP1/TP2/TP7 |
| 3,3-V-Buck | links Mitte | U3, L1, C6–C11, TP3/TP4 – kurze Schleife VIN–C7–U3–GND |
| Diagnose | oben links | D11–D19, Q1, SW3, R26–R31, TP24/TP25/TP28 |
| RTC und Pufferzelle | oben Mitte | BT1, U6, D5/D6, C19, I2C-Pull-ups |
| Reset/BOOT | oben Mitte rechts | SW1, SW2, U5, R7/R8, C15, TP8/TP9 |
| ESP32-S3-WROOM-1U | oben rechts | U4 mit C12–C14; U.FL-Anschluss am oberen Rand |
| USB-C und eFuse | rechts | J5 am rechten Rand, U1 ESD direkt dahinter, U2, R1–R6, C2–C5, D4, R9/R10 |
| AUTOTERM | über J2 | U7, D7, D8, R15–R18, C20–C22, TP16–TP21 |
| Taster/LED | über J4 | U9, F1, D10, R22–R25, C25 |
| 1-Wire | über J3 | U8, D9, R19–R21, C23/C24 |
| Status-LEDs | Mitte | D20/D21 mit R32–R35 |

Alle Stecker J1–J4 liegen an der Unterkante, die Schutzbauteile (TVS/ESD) direkt dahinter (C-04, Y-06).

## 3. Designregeln

Die Netzklassen stehen auf 0,15 mm. Den allgemeinen Kupferabstand von 0,2 mm setzt `LandyHeater.kicad_dru`, weil KiCad sonst keine Ausnahmen erlaubt. Der DRC verwendet nämlich den größeren Wert aus Netzklasse und Regel.

| Regel | Wert | Grund |
|---|---|---|
| Kupferabstand | 0,2 mm | allgemein |
| Pad-Pad in U2, U3, U6, U7 | 0,12 mm | Hersteller-Footprints (VSSOP 0,5 mm, VQFN-HR) haben 0,15 mm; JLCPCB-Minimum 0,09 mm |
| USB-Paar | 0,13 mm | Spalt im Differenzpaar |
| Bohrung zu Kupfer | 0,25 mm | allgemein |
| USB-C J5 | 0,15 mm | NPTH-Führungsstifte zu GND-Pads laut GCT-Footprint (0,194 mm) |
| Bohrung Minimum | 0,2 mm | Wärmevias im ESP32-Footprint; JLCPCB 4 Lagen ab 0,15 mm |

## 4. Transientennachweis V-01 (P-03)

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

¹ Bei Puls 3a erreicht D2 im Modell für etwa 15 ns die Durchbruchspannung, mit 39 nJ Lawinenenergie. Die Ursache ist die Resonanz der Ferrit-Induktivität mit der Sperrschichtkapazität von D2. Mit realistischen Ferritverlusten oder schon 22 pF Leiterbahnkapazität an `12V_PROT` bleibt sie bei ≤ 51 V. Das ist unkritisch; s. Empfehlung E-01.

**Grenzen der Schutzschaltung (dokumentiert nach P-03):**
- **Lastabwurf ohne zentrale Begrenzung** (ISO 16750-2 Test A, bis ≈ 100 V für 40–400 ms) wird nicht beherrscht. Die TVS würde überlastet und niederohmig ausfallen; die externe 1-A-Sicherung (P-01) trennt dann.
- **Lastabwurf mit zentraler Begrenzung auf ≈ 35 V** (Test B) überlastet die TVS ebenfalls, weil die SMBJ18CA ab ≈ 20 V leitet.
- Beides ist für einen Verbraucherkreis an einer Zweitbatterie hinter Ladebooster nicht zu erwarten und keine Anforderung.

## 5. Empfehlungen und offene Punkte

| # | Punkt | Phase |
|---|---|---|
| E-01 | Optional 100 nF / 50 V (0603) von `12V_PROT` nach GND vor FB1. Begrenzt die Spitze aus Puls 3a an D2 auf 25 V und verbessert das Eingangsfilter. Kleine Schaltplanänderung, Platz neben FB1 vorhanden. | Entscheid Auftraggeber |
| P3-01 | Footprints aus Bibliothek aktualisieren (15 Rundungswarnungen) | 4 |
| P3-02 | Beschriftung und Bestückungsdruck bereinigen, Energiefluss-Grafik an den Diagnose-LEDs | 4 |
| P3-03 | USB-Impedanz mit dem JLCPCB-Rechner bestätigen (P2-03) | 4 |
| P3-04 | 3D-Ansicht im KiCad-3D-Viewer prüfen. `kicad-cli pcb render` liefert ohne Grafikkontext leere Bilder. | 4 |

## 6. Freigabekriterien Phase 3

- [x] Kontur innerhalb 80 × 50 mm
- [x] alle Bauteile einseitig platziert, keine Courtyard-Kollision
- [x] Befestigungslöcher mit Freiraum
- [x] Stecker am Rand, Schutzbauteile am Stecker
- [x] DRC ohne Fehler außer nicht gerouteten Verbindungen
- [x] Transientenprofil festgelegt und mit SPICE nachgewiesen (V-01)
- [ ] Freigabe durch Auftraggeber
