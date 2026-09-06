# Phase 2 – KiCad-Schaltplan und Review

Stand: 2026-09-06

Projektstatus: technisch abgeschlossen, Freigabe durch Auftraggeber ausstehend

Normative Grundlage: [Hardware-Anforderungsspezifikation Revision A](Hardware-Anforderungsspezifikation_Revision_A.md), Dokumentversion 1.5; [Phase-1-Festlegung](Phase_1_Architektur-und-Bauteilfestlegung.md)

## 1. Ergebnis

Der hierarchische Schaltplan für Revision A ist als editierbares KiCad-10-Projekt umgesetzt. Er umfasst 197 einzelne Referenzen, davon 33 ausdrücklich als DNP gekennzeichnete Test-, Mess- oder Bestückungsoptionen. Der vorläufige BOM-Export fasst identische Bauteile in 122 Zeilen zusammen.

Die automatische KiCad-Prüfung vom 06.09.2026 ergibt:

- 7 Schaltplanseiten,
- 0 ERC-Fehler,
- 0 ERC-Warnungen,
- vollständige Referenz- und Footprint-Zuordnung für alle 197 Bauteile,
- vollständige KiCad-Netzliste und BOM.

Dieser Stand ist **keine Fertigungsfreigabe**. Die in Abschnitt 8 genannten mechanischen und elektrischen Freigabesperren bleiben vor Phase 3 beziehungsweise vor dem Manufacturing Release verbindlich.

## 2. Schaltplanstruktur

| Seite | Datei | Inhalt |
|---|---|---|
| 1 | `LandyHeater-Board.kicad_sch` | Hierarchie und Funktionsübersicht |
| 2 | `01_Power_Input_USB.kicad_sch` | 12-V-Eingang, Verpol-/Rückspeiseschutz, USB-C-Sink, USB-eFuse, 3,3-V-Buck |
| 3 | `02_ESP32_USB_Reset.kicad_sch` | ESP32-S3-WROOM-1U-N16R8, native USB-Daten, Supervisor, BOOT/RESET, GPIO-Serienwiderstände |
| 4 | `03_Display_EPaper.kicad_sch` | geschaltete Displayversorgung, Pegelisolation, 24-poliger FPC und E-Paper-Booster |
| 5 | `04_Touch_RTC.kicad_sch` | 3,0-V-Always-on-Zweig, Touch-I2C/INT/RESET, optionale Wake-Schaltung, RV-3028-C7 und BR1225 |
| 6 | `05_AUTOTERM_1Wire.kicad_sch` | heizungsseitig gespeister 5-V-UART-Pegelwandler und geschützter 1-Wire-Anschluss |
| 7 | `06_Controls_Diagnostics.kicad_sch` | 3-m-Tasterleitung, dimmbare Ring-LED, Frontlicht und lokale Energieflussanzeige |

Netze sind funktionsübergreifend mit eindeutigen globalen Netzbezeichnungen verbunden. Die Darstellung verwendet bewusst kompakte, pinorientierte Funktionssymbole. Damit lassen sich Pinnummer, Netz, MPN und Footprint direkt gegeneinander prüfen. Die projektspezifischen Symbole verwenden in Phase 2 passive ERC-Pintypen; der ERC prüft daher Syntax, Anschlussvollständigkeit, offene Pins, Netzkonflikte und Rastertreue, aber nicht jede mögliche Treiberkollision. Die elektrische Topologie wurde zusätzlich anhand der in Abschnitt 4 aufgeführten Herstellerunterlagen geprüft.

## 3. Umgesetzte sichere Hardwarezustände

| Funktion | Umsetzung | Zustand ohne Firmware |
|---|---|---|
| ESP32-Enable | `TPS3808G33QDBVRQ1`, 10-kΩ-Pull-up und 1-µF-EN-Kondensator | Reset bis 3,3 V stabil; manueller RESET über MR |
| BOOT | 10-kΩ-Pull-up und lokaler Taster | Normalboot; GPIO0 nur bei Tastendruck LOW |
| Display | `TPS22919QDCKRQ1`, EN-Pulldown und AXC-Ausgangsisolation | Versorgung AUS, Ausgänge hochohmig |
| Touch | permanenter 3,0-V-Zweig, I2C-Pull-ups, Open-Drain-Reset | Touch bleibt im Komfort-Standby versorgt und kann GPIO2 wecken |
| Sensoren | strombegrenzter `TPS22945DCKR`, EN-Pulldown | 1-Wire-Sensorversorgung AUS |
| AUTOTERM | B-Seite nur durch `AUTOTERM_5V_IN`, OE-Pulldown | Heizungsschnittstelle hochohmig |
| Frontlicht | 100-kΩ-Pulldown an VSET/PWM | AUS |
| Taster-Ring-LED | MOSFET-Gate-Pulldown | AUS |
| Diagnoseanzeige | lokaler DIAG-Taster mit PNP/NMOS-Freigabe | alle fünf Energiefluss-LEDs AUS |
| optionale Status-LEDs | DNP-Widerstand und DNP-LED | nicht bestückt |

Der direkte, active-low Touch-INT-Pfad über 100 Ω ist die Standardbestückung; `R30` erlaubt DNP-seitig einen 0-Ω-Direktpfad. Die alternative Latch-Option `U13/C39/R31/R69/R70` bleibt DNP, bis die INT-Pulsform am Originaldisplay gemessen ist. Bei dieser Option initialisiert `R31/C39` das Latch inaktiv; ein LOW an FT6336U-INT setzt es danach asynchron und hält dessen invertierten Ausgang `Q_N` und damit GPIO2 LOW. So bleibt für Taster und Touch dieselbe EXT1-`ANY_LOW`-Polarität erhalten. Nach dem Auslesen und Deassertieren von INT löscht die Firmware das Latch mit einem kurzen LOW an GPIO18. `R28`, `R29` und `R30` werden bei dieser Variante nicht bestückt; gleichzeitiges Aktivieren beider Pfade ist unzulässig.

## 4. Hersteller- und Pinoutprüfung

Die elektrisch relevanten Pins wurden jeweils zwischen Hersteller-Pin-Tabelle, lokalem Symbol und zugeordnetem Footprint-Pad verglichen. Das Ergebnis ist im Schaltplan und in der Generator-Selbstprüfung verankert.

| Baugruppe | Prüfergebnis |
|---|---|
| ESP32-S3-WROOM-1U-N16R8 | Modul-Pads 1–41 stimmen mit Espressif v1.8 überein. GPIO35–37 sind wegen Octal-PSRAM NC; GPIO19/20 sind USB D−/D+; GPIO1/2 sind RTC-fähige Wake-Eingänge. GPIO47/48 bleiben beim N16R8 3,3-V-I/O. |
| LM74720-Q1 | DRR-Pads 1–12 und RTN-Exposed-Pad geprüft. RTN bleibt NC. VSNS/SW nutzen den internen Trennschalter; CAP liegt über 1 µF an VS; LX über 100 µH am gemeinsamen MOSFET-Drain. |
| IPG20N06S4L-26 | Dual-MOSFET-Pins 1=S1, 2=G1, 3=S2, 4=G2, 5/6=D2 und 7/8=D1 geprüft. Der Schaltplan ist pinvollständig; das endgültige geteilte Exposed-Pad-Landpattern bleibt Phase-3-Gate. |
| LMR43620-Q1 | RPE-Pads 1–9 geprüft: MODE/SYNC, PGOOD, EN, VIN, SW, BOOT, VCC, VOUT/FB, GND. Beschaltung folgt der festen 3,3-V-/2,2-MHz-Variante. |
| TUSB321AI / TPS259470 | RWB- beziehungsweise RPW-Pinfolge geprüft. TUSB321 ist als UFP konfiguriert; die eFuse ist die `470L`-Variante mit einstellbarer OV-Abschaltung und Latch-off. |
| TPS22919 / TPS22945 | DCK-Pinfolgen geprüft. Beim TPS22919 ist QOD direkt an VOUT; beide TPS22945-OC-Ausgänge sind bewusst unbenutzt und als NC markiert. |
| USB-Datenschutz | `TPD2EUSB30DRTR` liegt zwischen Buchse und 22-Ω-Serienwiderständen; beide USB-Leitungen bleiben getrennt und gehen auf ESP32-Pads 13/14. |
| Display-Pegelwandler | `SN74AXC8T245PWR`-PW-Pins 1–24 und `SN74AXC1T45DCKR` geprüft. A-Seite liegt an 3V3_CORE, B-Seite an der geschalteten Displaydomäne. |
| E-Paper | J6-Pins 1–24 stimmen elektrisch mit dem Good-Display-Referenzschaltbild überein. D3–D5 sind mit KiCad-Pad 1 = Kathode und Pad 2 = Anode ausdrücklich gepolt. |
| Touch | J7-Pins 1–6 sind GND, INT, RESET, 3,0 V, SCL, SDA. FT6336U bleibt im Standby versorgt; INT geht auf RTC_GPIO2. |
| RTC | RV-3028-C7-Pads 1–8 geprüft. VBACKUP erhält die BR1225 über eine niedrig leckende BAS116; EVI liegt an GND; CLKOUT bleibt NC. |
| AUTOTERM | `TXU0202QDCURQ1` hat zwei fest gegenläufige Kanäle. A-Seite = 3,3 V, B-Seite = ausschließlich heizungsseitige 5 V; bei fehlender B-Versorgung bleiben Ausgänge hochohmig. |
| Beleuchtung | `BCR420UW6Q-7` und `AL8861QMP-13` gegen Hersteller-Pinout geprüft. Die Frontlicht-Freilaufdiode hat Pad 1/K an VIN_SYS und Pad 2/A an LX. |
| LEDs und Sperrdioden | Alle 0603-LEDs verwenden Pad 1 = K und Pad 2 = A. BAS116 verwendet Pad 1 = A, Pad 2 = NC, Pad 3 = K. |

### Verwendete Herstellerdokumente

- [Espressif ESP32-S3-WROOM-1/1U Datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [TI LM74720-Q1](https://www.ti.com/lit/ds/symlink/lm74720-q1.pdf)
- [Infineon IPG20N06S4L-26](https://www.infineon.com/assets/row/public/documents/10/49/infineon-ipg20n06s4l-26-datasheet-en.pdf)
- [Infineon PG-TDSON-8-4 package](https://www.infineon.com/package/PG-TDSON-8-4)
- [TI LMR43620-Q1](https://www.ti.com/lit/ds/symlink/lmr43620-q1.pdf)
- [TI TPS25947](https://www.ti.com/lit/ds/symlink/tps25947.pdf)
- [TI TUSB321AI](https://www.ti.com/lit/ds/symlink/tusb321ai.pdf)
- [TI TPS22919](https://www.ti.com/lit/ds/symlink/tps22919.pdf)
- [TI TPS22945](https://www.ti.com/lit/ds/symlink/tps22945.pdf)
- [TI SN74AXC8T245](https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf)
- [Good Display GDEY029T94-FT01, Rev. 1.0](https://v4.cecdn.yun300.cn/100001_1909185148/GDEY029T94-FT01.pdf)
- [FocalTech FT6336U, V1.0](https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf)
- [Micro Crystal RV-3028-C7](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7)
- [Diodes Inc. AL8861Q](https://www.diodes.com/datasheet/download/AL8861Q.pdf)
- [Nexperia BAS116](https://assets.nexperia.com/documents/data-sheet/BAS116.pdf)

## 5. Rechenprüfung der kritischen Startwerte

### 5.1 12-V-Überspannungsabschaltung

Mit `R1 = 100 kΩ`, `R2 = 7,15 kΩ` und der typischen LM74720-OV-Schwelle von 1,231 V gilt:

`V_OV,nom = 1,231 V × (1 + 100 kΩ / 7,15 kΩ) = 18,45 V`

Mit der Datenblatt-Schwelle 1,13…1,33 V und 1-%-Widerständen ergibt sich konservativ 16,62…20,31 V. Die minimale Abschaltung bleibt damit oberhalb des spezifizierten 14-V-Dauerbetriebs. TVS-Klemmung, Pulsenergie, MOSFET-SOA und Filterdämpfung werden vor dem Layout mit Mess-/Simulationsannahmen endgültig freigegeben.

### 5.2 USB-eFuse

`R9 = 3,32 kΩ` ergibt nach der TI-Näherung `ILIM ≈ 3334 / RILM = 1,00 A`. `R7/R8 = 100 kΩ/26,1 kΩ` setzt die nominale OV-Abschaltung auf ungefähr 5,9 V. Die reale USB-Leistungsaufnahme bleibt durch Firmware-Lastfreigabe und das Phase-1-Leistungsbudget unterhalb des angekündigten Type-C-Stroms.

### 5.3 Frontlicht

Für den AL8861Q gilt mit der typischen 0,1-V-Strommessschwelle und `R43 = 2,0 Ω`:

`I_LED,nom = 0,1 V / 2,0 Ω = 50 mA`

`L4 = 47 µH` und die SS14-Freilaufdiode sind als Startwerte festgelegt. Stromwelligkeit, PWM-Frequenz, thermische Reserve und der reale Display-LED-Spannungsabfall werden vor Layout-Freeze verifiziert.

### 5.4 Diagnoseanzeige

Bei angenommener roter LED-Flussspannung von 1,8 V und etwa 0,7 V an der BAS116 ergeben sich ungefähr 0,8 mA am 12-V-Zweig, 0,76 mA am USB-/HEAT-Zweig und 0,67 mA am 3V3-/RUN-Zweig. Die Anzeige zieht nur bei gedrücktem DIAG-Taster Strom. Jeder Quellenzweig besitzt eine eigene niedrig leckende Sperrdiode; rechnerisch wird die Forderung von weniger als 5 µA Rückleckstrom pro Quelle deutlich unterschritten, die Prototypmessung bleibt verbindlich.

### 5.5 3-m-Tasterleitung

`R38 = 1 kΩ` und `C35 = 10 nF` ergeben 10 µs Zeitkonstante als HF-/ESD-Filter. Die eigentliche Entprellung erfolgt in Software. GPIO1 bleibt mit 10 kΩ definiert HIGH und kann als RTC-GPIO aus Deep-Sleep wecken.

## 6. DNP- und Serviceoptionen

- `U13`, `C39`, `R31`, `R69`, `R70`: optionale Touch-Wake-Latch-Schaltung mit Power-on-Clear, erst nach INT-Messung bestücken; in dieser Variante bleiben `R28/R29/R30` unbestückt.
- `R28/R29`: Standardpfad für active-low Touch-INT; `R30` ist der alternative 0-Ω-Direktpfad. `R71` ist eine reine DNP-Messoption für einen Pulldown und darf nie gleichzeitig mit `R29` bestückt werden. Alle Direktpfadteile bleiben bei bestücktem Latch unbestückt.
- `R52/LED6`, `R53/LED7`: zwei optionale, softwaregesteuerte Status-LEDs.
- `TP1` bis `TP22`: elektrische Testpunkte, standardmässig keine aufgelöteten Buchsen.
- BR1225: nicht im Reflow bestücken; Zelle erst nach Reinigung und Endprüfung einsetzen.

## 7. Fertigungs- und Footprintstatus

Alle Schaltplansymbole besitzen eine Footprint-Zuordnung und alle referenzierten Bibliotheksnamen sind unter KiCad 10.0.6 aufgelöst. Drei Footprintgruppen bleiben absichtlich vorläufig:

1. `Texas_RPE0009A_VQFN-HR-9_2x2mm` muss vor Phase 3 durch das exakte TI-/Ultra-Librarian-Padbild mit L-förmigen Eckpads, Lötstoppmaske und segmentierter Paste ersetzt oder dagegen geometrisch freigegeben werden.
2. `RV-3028-C7` muss mit dem aktuellen Micro-Crystal-ECAD-Modell geometrisch verglichen werden.
3. Die drei Hirose-FPC-Stecker müssen am Originaldisplay auf Kontaktseite, Pin-1-Lage, FPC-Dicke und Einsteckrichtung geprüft werden.

Der achtpolige Q1-Schaltplan ist elektrisch vollständig. Sein `PROVISIONAL_Infineon_PG-TDSON-8-4_Dual`-Footprint ist nur ein pinvollständiger Platzhalter und muss vor Phase 3 durch das offizielle Infineon-Landpattern mit geteiltem Exposed Pad ersetzt werden. Der zuvor naheliegende KiCad-Standardfootprint für einen einzelnen TDSON-MOSFET besitzt nur die Netznamen 1…5 und ist für diesen Dual-MOSFET ausdrücklich ungeeignet.

Der aktuelle TPS259470-Footprint ist elektrisch pinrichtig, muss aber vor Layout-Freeze gegen die aktuelle TI-RPW-Landpatternzeichnung geprüft werden.

## 8. Offene Freigabesperren

Diese Punkte verhindern **nicht** den Schaltplanreview, aber sie verhindern Layout- oder Fertigungsfreigabe:

- Originaldisplay mechanisch vermessen und FPC-Kontaktseite eindeutig bestätigen.
- Touch-INT-Pulsdauer, Pegel im Deep-Sleep und Wake-Zuverlässigkeit messen; danach Direktpfad oder Latch-Variante freigeben.
- TI-RPE-, TI-RPW- und RV-3028-Landpatterns geometrisch einfrieren.
- LM74720/TVS/MOSFET-Transientenkoordination einschließlich SOA und Eingangsfilter prüfen.
- LMR43620-Ausgangsripple, Lastsprung, thermische Reserve und Stabilität mit den realen Kondensator-Deratings prüfen.
- AL8861-Stromwelligkeit und Temperatur bei 10…14 V sowie maximaler Frontlicht-PWM prüfen.
- APEM-Bestellcode `AV970220000700`, Schalterkontaktbelegung und LED-Polarität am realen Teil bestätigen.
- PCBWay-Verfügbarkeit und keine automatischen MPN-Substitutionen für die fünf Prototypen bestätigen.

## 9. Reproduzierbarkeit und Dateien

- Schaltplanquelle: `hardware/LandyHeater-Board.kicad_sch` mit sechs Untersheets.
- Projektlokale Bibliotheken: `hardware/libraries/`.
- Deterministischer Erstgenerator: `scripts/generate_phase2_schematic.py`. Er dient der Nachvollziehbarkeit des Phase-2-Ausgangsstands; nach manuellen KiCad-Änderungen darf er nur bewusst ausgeführt werden, weil er die sieben Schaltplandateien neu erzeugt.
- Prüfung und Export: `make sch-check` sowie `make export-phase2`.
- `make check` prüft in Phase 2 den Schaltplan und das noch leere PCB-Gerüst getrennt. Die Schaltplan-/PCB-Paritätsprüfung wird erst mit der Übernahme des freigegebenen Schaltplans in das Layout ab Phase 3 verbindlich aktiviert.
- Review-PDF: `output/pdf/LandyHeater-Board-schematic-Phase2.pdf`.
- Vorläufige BOM: `output/bom/LandyHeater-Board-BOM-Phase2.csv`.

## 10. Phase-2-Freigabekriterien

- [x] Hierarchischer KiCad-Schaltplan erstellt
- [x] Sichere Hardwarezustände und DNP-Optionen abgebildet
- [x] Alle Referenzen eindeutig und Footprints zugeordnet
- [x] Hersteller-Pinouts elektrisch gegengeprüft
- [x] E-Paper-Referenzbeschaltung einschließlich Diodenpolarität übertragen
- [x] ERC ohne Fehler oder Warnungen
- [x] Schaltplan-PDF und vorläufige BOM erzeugt
- [x] Verbleibende Layout-/Fertigungsfreigabesperren dokumentiert
- [ ] Phase 2 durch Auftraggeber freigegeben
