# Phase 2 – KiCad-Schaltplan und unabhängiger Review

Stand: 2026-09-06

Normative Grundlage: [Hardware-Anforderungsspezifikation Revision A](Hardware-Anforderungsspezifikation_Revision_A.md), Dokumentversion 1.6

Status: **elektrisch, strukturell und intern visuell geprüft, aber wegen offener Freigabegates und ausstehender Abnahme nicht für Phase 3 oder Fertigung freigegeben**

## 1. Ergebnis

Der erste automatisch erzeugte, rasterartige und überwiegend labelbasierte Entwurf wurde verworfen. Der aktuelle Stand ist ein neuer, editierbarer KiCad-10-Schaltplan mit funktionsorientierter Seitenaufteilung. Lokale Verbindungen innerhalb eines Funktionsblocks sind als sichtbare Leitungen gezeichnet; Labels dienen nur Seitenübergängen, globalen Spannungsdomänen, Einzelanschlüssen und bewusst entfernten Verbindungen. Quellen, Schutzglieder, Regler/Schalter, Filter und Verbraucher sind vorzugsweise von links nach rechts angeordnet. Versorgungssymbole liegen oben, sichtbare GND-Symbole unten. Steckverbinder schließen die jeweiligen Signalpfade am Blockrand ab.

Der Schaltplan umfasst:

- 7 Seiten,
- 232 eindeutige Referenzen, davon 56 ausdrücklich DNP,
- 141 gruppierte BOM-Zeilen,
- 0 ERC-Fehler und 0 ERC-Warnungen,
- 0 im Export-Audit erkannte unterbrochene oder ungewollt verschmolzene Sollnetze,
- 651 angeschlossene Pins in 175 Netzen vor und nach der grafischen Überarbeitung; identischer Topologie-Hash,
- Footprint-Zuordnung für jede Referenz.

Die automatischen Ergebnisse sind in `build/reports/erc.rpt` und `build/reports/phase2-audit.txt` reproduzierbar. Sie ersetzen weder Worst-Case-Auslegung noch die Prüfung der herstellerspezifischen Landpatterns.

Der Review erfolgte in drei getrennten Durchgängen: zuerst blockweise gegen Pinout, Referenzschaltung und Grenzwerte; anschließend systemweit über Spannungsdomänen, ausgeschaltete Zustände, Backfeeding, DNP-Kombinationen und die vollständig exportierte Pin-Netz-Matrix; zuletzt als visueller Review jeder einzelnen aus KiCad gerenderten A4-Seite. Der elektrische Durchgang entdeckte unter anderem unzulässige Verschmelzungen, die der ERC allein nicht gemeldet hatte; die Generatorlogik wurde daraufhin korrigiert und der Netzlisten-Audit als dauerhafte Regressionprüfung ergänzt.

## 2. Visueller A4-Review vom 2026-09-07

Alle sieben Seiten des final exportierten PDFs wurden mit 150 dpi gerendert und einzeln geprüft:

| Seite | Visuell verfolgter Hauptpfad | Ergebnis |
|---|---|---|
| 1 | 12 V/USB → VIN_SYS/3V3 → ESP32, Display, Touch, AUTOTERM/1-Wire und Controls | bestanden |
| 2 | J1 → TVS → LM74720-Q1 → Back-to-back-FET → Filter → VIN_SYS; USB-C → CC/eFuse/Rückstromsperre → VIN_SYS; VIN_SYS → Buck → 3V3_CORE | bestanden |
| 3 | Supervisor/RESET/BOOT, natives USB, ESP32 und E-Paper-Signalkonditionierung | bestanden |
| 4 | Display-Lastschalter, Power-off-Isolation, Referenz-Booster und J6 | bestanden |
| 5 | Always-on-Touchversorgung, Reset/FPC, direkter/optionaler Wake-Pfad und RTC-Backup | bestanden |
| 6 | ESP32 ↔ Pegelwandler ↔ Serienglieder ↔ ESD ↔ J2 sowie Sensorlastschalter ↔ Pull-up/Schutz ↔ J3 | bestanden |
| 7 | Externer Taster/Ring-LED, Frontlicht und DIAG-geschaltete Energieflussanzeige | bestanden |

Die PDF hat sieben Seiten im Format A4. Funktionsrahmen und Überschriften sind auf jeder Funktionsseite vorhanden. Der Generator bricht künftig mit einem Fehler ab, falls ein lokales Mehrpunktnetz nicht mit sichtbaren Leitungen geroutet werden kann; ein stiller Rückfall auf ein Label an jedem Bauteilende ist nicht mehr möglich.

## 3. Seitenstruktur

| Seite | Datei | Funktion |
|---|---|---|
| 1 | `LandyHeater-Board.kicad_sch` | Hierarchie und Funktionsübersicht |
| 2 | `01_Power_Input_USB.kicad_sch` | 12-V-Schutz, USB-C-Sink/eFuse, Power-OR, 3,3-V-Buck |
| 3 | `02_ESP32_USB_Reset.kicad_sch` | ESP32-S3, natives USB, Supervisor, BOOT/RESET, Signalserienglieder |
| 4 | `03_Display_EPaper.kicad_sch` | Display-Lastschalter, Pegelisolation, E-Paper-Booster, J6 |
| 5 | `04_Touch_RTC.kicad_sch` | 3,0-V-AON, Touch, optionale Wake-Latch-Variante, RTC/BR1225 |
| 6 | `05_AUTOTERM_1Wire.kicad_sch` | AUTOTERM-5-V-UART und geschützter 1-Wire-Bus |
| 7 | `06_Controls_Diagnostics.kicad_sch` | 3-m-Taster, dimmbare Ring-LED, Frontlicht, Energieflussanzeige |

## 4. Wesentliche Reviewkorrekturen

| Bereich | Korrektur |
|---|---|
| 12-V-Schutz | LM74720-Q1 nach TI-Grundschaltung ergänzt: 0-Ω-PD/Gate-Verbindung, 100 Ω plus 10 nF nach GND für Gate-Slew und 18-V-VGS-Klemme. RTN/EP bleibt elektrisch offen und verwendet deshalb den WSON-Footprint ohne Thermal Vias. |
| USB-Stromerkennung | TUSB321-Open-Drain-Pull-ups liegen nur an USB_VBUS. Q8 entkoppelt die unversorgte USB-Domäne von 3V3; GPIO40 ist jetzt `USB_HIGH_CURRENT`, active HIGH. |
| USB-eFuse | TPS259470L mit 1-A-Nennlimit, ca. 5,82-V-OVLO und 10-nF-dV/dt-Kondensator; USB-VBUS und VIN_SYS bleiben durch die echte Rückstromsperre getrennt. |
| 3,3-V-Buck | L2 auf `XAL4020-222MEC`, 2,2 µH/5,6 A Isat, geändert; 2 × 22 µF am Ausgang und ein konkreter 4,7-µF-/50-V-X7R-Eingangskondensator vorgesehen. |
| ESP32 | N16R8-Padbelegung, Octal-PSRAM-Reservierung, USB GPIO19/20, EN/BOOT und 2 × 22 µF lokale Pufferung geprüft. |
| E-Paper | C37 liegt korrekt zwischen PREVGL und GND; unbenutzte A6…A8 des 8-Bit-Pegelwandlers sind an GND; lokale VCCA/VCCB-Abblockung ergänzt. |
| ESD-Arrays | PESD5V2S2UT-Q und PESD3V3S2UT-Q korrigiert: Pins 1/2 an den geschützten Leitungen, gemeinsamer Anodenpin 3 an GND. |
| AUTOTERM | J2 = 5 V, GND, TX zur Heizung, RX von der Heizung. Die B-Seite des TXU0202 wird ausschließlich aus dem geschützten heizungsseitigen 5-V-Zweig gespeist. |
| 1-Wire | J3 = geschaltete 3,3 V, DQ, GND; 4,7-kΩ-Pull-up und bestückter 0-Ω-Abgleichlink vor GPIO4. |
| Ring-LED | `BCR421UW6Q-7` ersetzt den ungeeigneten BCR420/MOSFET-Aufbau. PWM erfolgt direkt am EN-Pin, hardwareseitig default AUS. |
| Frontlicht | AL8861 erhält 10 µF/100 V X7R lokal, 47-µH-Induktivität und automotive `B140Q-13-F`; Sollstrom 50 mA nominal. |
| Diagnose | USB-LED misst rohes USB_VBUS, nicht das zusammengeführte VIN_SYS. Der DIAG-Gateteiler begrenzt Q5-VGS auch an der maximalen OV-Abschaltschwelle. |

## 5. Hardwarezustände ohne Firmware

| Funktion | Zustand |
|---|---|
| ESP32 EN | TPS3808 überwacht 3V3; CT offen ergibt nominal 20 ms Verzögerung; RESET zieht MR low |
| BOOT | 10 kΩ high; nur lokaler BOOT-Taster zieht GPIO0 low |
| Display | `DISPLAY_EN` 100 kΩ low; Displayversorgung aus; Pegelwandler-Ausgänge hochohmig |
| Touch | 3,0-V-AON bleibt versorgt; Reset wird über Open Drain gesteuert; direkter INT-Pfad ist Standard |
| Sensoren | `SENSOR_EN` low; 1-Wire-Sensorversorgung aus |
| AUTOTERM | `AUTOTERM_OE` low; TX zur Heizung hochohmig |
| Frontlicht | PWM/VSET 100 kΩ low; aus |
| Taster-Ring | BCR421-EN 100 kΩ low; aus |
| Energiefluss-LEDs | gemeinsamer Diagnosepfad aus, solange DIAG nicht gedrückt/überbrückt ist |
| optionale Status-LEDs | Bauteile DNP |

## 6. DNP-Varianten

- Standard-Touch-Wake: R28 und R29 bestückt; R30, R71 und die gesamte Latch-Gruppe U13/C39/R31/R69/R70 DNP.
- Latch-Variante erst nach Messung: U13/C39/R31/R69/R70 bestücken und R28/R29/R30/R71 nicht bestücken.
- C40/C41 und C42…C46 sind ausschließlich unbestückte USB-/SPI-Tuningplätze.
- LED6/R52 und LED7/R53 sind optionale Statusanzeigen.
- TP1…TP38 sind DNP-Testpunkte ohne aufgelötete Buchsen.

## 7. Freigabesperren

Phase 2 ist aktuell **nicht freigabefähig**. Vor Phase 3 müssen mindestens folgende Punkte geschlossen werden:

1. Offizielle Landpatterns/ECAD-Modelle für Q1 (Infineon PG-TDSON-8-4 Dual), U3 (TI RPW), U4 (TI RPE), RV-3028 sowie L3/L4 geometrisch übernehmen und unabhängig prüfen.
2. FPC-Kontaktseite, Pin 1, FPC-Dicke und Einsteckrichtung von J6/J7/J8 am Originaldisplay bestätigen.
3. Fahrzeug-/Kabelbaum-Transientenprofil definieren und TVS-Klemmung, LM74720-FET-SOA, Filterdämpfung und Einschaltstrom rechnerisch/simulatorisch freigeben.
4. Effektive MLCC-Kapazitäten bei DC-Bias und Temperatur prüfen; Buck-Stabilität, Lastsprung und Ripple anschließend simulieren oder messen.
5. Touch-INT-Pulsdauer und Wake-Zuverlässigkeit am Originaldisplay messen; Standardpfad oder Latch-Bestückung festlegen.
6. AL8861-Stromwelligkeit, Temperatur und Frontlight-FPC-Polarität am Muster prüfen.
7. APEM-Code `AV970220000700`, Kontaktbelegung, LED-Polarität und LED-Flussspannung am bestellten Muster bestätigen.
8. Verfügbarkeit der exakten MPNs bei PCBWay klären; keine automatische Substitution kritischer Teile zulassen.

Details und quantitative Grenzen stehen in [Worst-Case-Berechnungen Phase 2](../calculations/Phase_2_Worst-Case-Berechnungen.md), die Quellenzuordnung in [Quellen und Rückverfolgbarkeit](Phase_2_Quellen-und-Rueckverfolgbarkeit.md).

## 8. Reproduzierbarkeit

```text
python3 scripts/generate_phase2_schematic.py
make sch-check
make export-phase2
```

`make export-phase2` erzeugt PDF, BOM und Netzliste und prüft anschließend jede exportierte Pin-Netz-Zuordnung gegen die kanonische Schaltungsdefinition. Zusätzlich vergleicht der Audit die elektrische Topologie mit dem unmittelbar vor der grafischen Überarbeitung gesicherten Stand. Das Ergebnis ist in [`LandyHeater-Board-Netlist-Comparison-Phase2.txt`](../output/reports/LandyHeater-Board-Netlist-Comparison-Phase2.txt) dokumentiert. Der Generator überschreibt die sieben Schaltplandateien; spätere manuelle KiCad-Änderungen müssen deshalb entweder zurück in den Generator übertragen oder der Generator bewusst stillgelegt werden.

Im ERC sind nur generische, für diesen Projektstand begründete Prüfklassen deaktiviert: einzeln vorkommende globale Labels (Test-/Seitenanschlüsse), Vierfach-Knoten (parallel geführte Versorgungs-/Gehäusepins), SPICE-Modelle (keine SPICE-Netzliste als Freigabenachweis) und Footprint-Filter (projektlokale kontrollierte Footprints). Konkrete ERC-Meldungen sind nicht einzeln unterdrückt; der Bericht enthält 0 Fehler und 0 Warnungen.

## 9. Phase-2-Freigabekriterien

- [x] lesbarer hierarchischer Funktionsschaltplan
- [x] interner visueller Review aller sieben aus KiCad gerenderten A4-Seiten
- [x] eindeutige Referenzen, Pinbelegungen und Footprints
- [x] sichere Defaultzustände und DNP-Varianten dokumentiert
- [x] ERC ohne Fehler/Warnungen
- [x] exportierte Netzliste ohne Sollnetz-Unterbrechung oder Netzverschmelzung
- [x] elektrische Pin-zu-Pin-Topologie vor/nach grafischer Überarbeitung identisch
- [x] BOM mit Footprint sowie MPN für aktive/elektromechanische/induktive Bauteile
- [x] Schaltplan-PDF und BOM reproduzierbar exportiert
- [ ] alle Punkte aus Abschnitt 7 geschlossen
- [ ] unabhängige Phase-2-Freigabe durch Auftraggeber/PCB-Designer
