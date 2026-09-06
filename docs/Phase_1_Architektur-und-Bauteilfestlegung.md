# Phase 1 – Schaltungsarchitektur und Bauteilfestlegung

Stand: 2026-09-06

Projektstatus: technisch abgeschlossen und durch Auftraggeber am 06.09.2026 freigegeben

Normative Grundlage: [Hardware-Anforderungsspezifikation Revision A](Hardware-Anforderungsspezifikation_Revision_A.md), Dokumentversion 1.6

## 1. Ergebnis und Geltungsbereich

Dieses Dokument legt die Architektur und die wesentlichen Herstellerteilenummern für Revision A fest. Es ist zusammen mit der Anforderungsspezifikation, der [GPIO-Matrix](GPIO-Matrix_Revision_A.md) und dem [Leistungs- und Ruhestrombudget](../calculations/Leistungs-und-Ruhestrombudget_Revision_A.md) die Eingabe für den Schaltplan in Phase 2.

Die Auswahl ist kein Fertigungsfreigabestand. Passive Werte, Kompensations- und Filterbauteile werden in Phase 2 anhand der Herstellerrechnungen festgelegt. Die in Abschnitt 9 genannten Prüfungen bleiben echte Freigabesperren.

## 2. Funktions- und Versorgungsarchitektur

```text
 J1 / 10…14 V
       │
       ├─ TVS ─ LM74720-Q1 + dualer N-MOSFET ─ gedämpfter Filter ─┐
       │                                                          │
 USB-C ─ ESD ─ CC-Erkennung ─ strombegrenzende Rückstromsperre ───┤─ VIN_SYS
                                                                  │
                                                                  ├─ 3,3-V-Buck ─ 3V3_CORE
                                                                  │                 ├─ ESP32-S3
                                                                  │                 ├─ RTC-Hauptversorgung
                                                                  │                 ├─ Display-/Sensor-Schalter
                                                                  │                 └─ 3,0-V-AON-LDO ─ Touch + I2C-Pull-ups
                                                                  ├─ Frontlicht-Bucktreiber
                                                                  └─ Konstantstromquelle ─ externe Taster-LED

 AUTOTERM_5V ─ Strombegrenzung ─ VCCB des UART-Pegelwandlers
 RTC-BR1225 ─ Sperrdiode ─ RTC_VBACKUP
```

Der 12-V- und der USB-Pfad werden als echte rückstromsperrende Ideal-Diodenpfade zusammengeführt. Weil der geschützte 12-V-Pfad stets deutlich über USB-VBUS liegt, erhält er ohne zusätzliche Umschaltlogik natürlichen Vorrang. Das Board darf deshalb keine Verbindung vom gemeinsamen `VIN_SYS` zurück zu USB, Batterie oder `AUTOTERM_5V` besitzen.

### 2.1 12-V-Pfad

- `TPSMB18CA-VR` nimmt lokale ESD- und Transientenenergie am Stecker auf. Die bidirektionale Ausführung vermeidet einen direkten Kurzschluss bei Verpolung.
- `LM74720QDRRRQ1` steuert den dualen N-Kanal-MOSFET `IPG20N06S4L-26` als Back-to-back-Idealdiode. Dadurch sind Verpolschutz, Rückstromsperre und eine OV-Abschaltung ohne Seriendiode möglich.
- Der `RTN`-Pin des LM74720-Q1 **muss elektrisch offen bleiben**. Eine Verbindung mit GND würde die vom Hersteller vorgesehene Verpolschutzfunktion außer Kraft setzen.
- Die OV-Schwelle wird in Phase 2 auf etwa 18 V bis 19 V ausgelegt. Teiler, Toleranzen, TVS-Klemmung, parasitäre Überschwinger und MOSFET-SOA werden als Worst-Case-Rechnung dokumentiert.
- Boost-Induktivität und Boost-Kondensator des Gate-Treibers werden exakt nach dem TI-Datenblatt dimensioniert; als Ausgangspunkt gelten 100 µH mit mindestens 175 mA und 1 µF.
- Hinter dem Ideal-Diodenpfad folgt ein gedämpfter Filter. Seine Werte werden erst nach Schleifen-, Einschaltstrom- und Impedanzprüfung festgelegt; ein undokumentierter LC-Resonator ist unzulässig.

### 2.2 USB-C-Pfad

- `USB4105-GF-A-120` ist der seitliche USB-2.0-Type-C-Stecker.
- `TUSB321AIRWBR` arbeitet als UFP/Sink, stellt die beiden Rd-Terminierungen bereit und erkennt den angekündigten Quellstrom. Separate 5,1-kΩ-Rd-Widerstände dürfen deshalb nicht zusätzlich bestückt werden.
- `OUT1` wird ausschließlich nach `USB_VBUS` hochgezogen und über einen `2N7002KQ-13` in die 3,3-V-Domäne entkoppelt. GPIO40 heißt deshalb `USB_HIGH_CURRENT`: HIGH bedeutet mindestens 1,5 A angekündigt oder kein USB, LOW bedeutet USB-Default-Current. `OUT2` bleibt im USB-Bereich und liegt nur an einem Testpunkt. Diese Schaltung verhindert Rückspeisung aus 3V3 in einen unversorgten TUSB321AI. Firmware sperrt Zusatzlasten bei LOW; ein gleichzeitiger 12-V-/Default-USB-Betrieb wird damit absichtlich konservativ behandelt.
- `TPS259470LRPWR` begrenzt Einschalt- und Fehlerstrom und sperrt Rückstrom zu USB. `RILM` wird in Phase 2 auf nominal 1 A ausgelegt. Weil TI die ±10-%-Genauigkeit erst für Einstellungen oberhalb 1 A spezifiziert, ist die eFuse kein Präzisionsnachweis für die 1-A-Betriebsgrenze; diese wird durch das auf etwa 0,65 A begrenzte Lastbudget und Messung nachgewiesen.
- `TPD2EUSB30DRTR` schützt D+ und D−. `ESD5Z5.0T1G` schützt VBUS. USB-Differenzpaar und ESD-Ableitweg bleiben kurz und stubfrei.
- Bei USB-Default-Current bleiben Frontlicht, externe Taster-LED, Display-Aktualisierung und Sensorversorgung zunächst aus. USB-Flashing einschließlich WLAN-Startspitze bleibt innerhalb des in der Berechnung angesetzten 500-mA-Rahmens.

### 2.3 Haupt- und Nebenversorgungen

- `LMR43620MSC3RPERQ1`: fester 3,3-V-/2-A-Buck, 2,2 MHz, AEC-Q100. `MODE/SYNC` erhält den Herstellerzustand für Auto-/PFM-Betrieb; er darf nicht dauerhaft auf FPWM gezwungen werden.
- `TPS3808G33QDBVRQ1`: Low-IQ-Supervisor mit Open-Drain-Reset und 3,07-V-Schwelle. Sein Ausgang und der lokale RESET-Taster ziehen `CHIP_PU/EN` nach GND. Die Verzögerung wird so bemessen, dass die ESP32-Versorgung vor EN sicher stabil ist; 20 ms nominal sind der Ausgangspunkt.
- `TPS7A0230PDBVR`: permanenter 3,0-V-/200-mA-LDO für `3V0_TOUCH_AON`.
- `TPS22919QDCKRQ1`: Lastschalter für `3V3_DISPLAY_SW`; Quick Output Discharge ist aktiv, Hardware-Default AUS.
- `TPS22945DCKR`: strombegrenzender Lastschalter für `3V3_SENSOR_SW`; Hardware-Default AUS. Ein zweites Exemplar begrenzt optional lokal `AUTOTERM_5V` auf etwa 100 mA, wenn die Datenblatt- und Spannungsabfallprüfung in Phase 2 dies bestätigt.

## 3. Funktionale Schnittstellen

### 3.1 ESP32, Reset und Programmierung

Das Modul ist verbindlich `ESP32-S3-WROOM-1U-N16R8`. GPIO35, GPIO36 und GPIO37 sind wegen des Octal-PSRAM nicht verfügbar. GPIO19/20 sind natives USB. GPIO0 ist ausschließlich BOOT; GPIO3, GPIO45 und GPIO46 bleiben unbenutzt. GPIO47 wird entgegen der unverbindlichen Freihaltepräferenz für `AUTOTERM_OE` benötigt; GPIO48 bleibt als Reserve frei.

BOOT zieht GPIO0 nach GND, RESET zieht EN nach GND. U0TXD, U0RXD, 3V3 und GND werden nur als Testpads herausgeführt; U0TXD erhält 499 Ω nahe am Modul. Alle Signalzuordnungen und Hardwarezustände stehen in der GPIO-Matrix.

### 3.2 AUTOTERM-UART

`TXU0202QDCURQ1` übersetzt zwei fest gegenläufige Kanäle zwischen `3V3_CORE` und dem ausschließlich von der Heizung gelieferten `AUTOTERM_5V`. OE liegt über einen Pulldown sicher LOW und wird erst über GPIO47 freigegeben. Dadurch bleibt `CTRL_TX_TO_HEATER` bei Reset, Boot, Deep-Sleep und fehlendem `AUTOTERM_5V` hochohmig. `PESD5V2S2UT-Q` schützt die beiden 5-V-Signalleitungen; Serienwiderstände werden im Schaltplan ergänzt.

### 3.3 1-Wire

GPIO4 führt über einen anpassbaren Serienwiderstand, `PESD3V3S2UT-Q` und J3 zum gemeinsamen externen Bus. Pull-up ist 4,7 kΩ nach `3V3_SENSOR_SW`. Der strombegrenzte Lastschalter verhindert, dass ein externer Kurzschluss `3V3_CORE` zusammenbrechen lässt.

### 3.4 Display und Touch

- FPC-Baseline: ein `FH12-24S-0.5SH(55)` sowie zwei `FH12-6S-0.5SH(55)`, jeweils 0,5-mm-Raster, Bottom-Contact und für 0,30-mm-FPC. Diese Auswahl bleibt bis zur Prüfung eines Originaldisplays mechanisch vorläufig.
- `SN74AXC8T245PWR` isoliert die fünf vom ESP32 zum E-Paper laufenden Leitungen. VCCA liegt an `3V3_CORE`, VCCB an `3V3_DISPLAY_SW`; alle Richtungen sind A nach B. `/OE` wird auf der Core-Seite standardmäßig HIGH gehalten und nur bei `DISPLAY_EN` über einen kleinen MOSFET LOW gezogen.
- `SN74AXC1T45DCKR` überträgt `EPD_BUSY` von der geschalteten Displaydomäne zur Core-Domäne und verhindert Rückspeisung.
- Revision A unterstützt den dokumentierten E-Paper-Schreibbetrieb. Das bidirektionale Lesen über SDA/FPC-Pin 14 wird nicht genutzt; ein MISO-GPIO ist nicht vorgesehen.
- Der E-Paper-Booster verwendet den im Good-Display-Schaltbild genannten `SI1308EDL-T1-GE3` und drei `MBR0530T1G`. Die passiven Werte und Spannungsfestigkeiten werden unverändert aus der Spezifikation übertragen und in Phase 2 erneut geprüft.
- `SN74LVC1G07QDBVRQ1` steuert `TOUCH_RESET_N` als pegelkompatiblen Open-Drain-Ausgang. Ein externer Pulldown an GPIO7 erzwingt Reset beim Einschalten; HIGH gibt den Reset über den 3,0-V-Pull-up frei. Der Zustand wird im Komfort-Standby per ESP32-Pad-Hold gehalten und am Prototyp geprüft.
- `TOUCH_INT_N` geht über Serienwiderstand und bestückbare Pull-Optionen direkt zu GPIO2. Zusätzlich werden ein 0-Ω-Bypass und ein unbestückter kleiner Logic-/Latch-Footprint vorgesehen. Ein konkreter Wake-Latch wird erst bestückt, wenn die Messung am Originaldisplay zeigt, dass der LOW-Puls für EXT1-Wakeup nicht zuverlässig pegelaktiv bleibt.

### 3.5 Beleuchtung

- `AL8861QMP-13` speist das Frontlicht aus `VIN_SYS` als Abwärts-Konstantstromtreiber. Nennstrom ist 50 mA; bei 0,1-V-Strommessschwelle ergibt sich als Startwert 2,0 Ω/1 %. Der Maximalstrom einschließlich Widerstandstoleranz bleibt unter 60 mA. GPIO21 steuert PWM; ein Hardware-Pulldown hält das Licht aus.
- `BCR421UW6Q-7` begrenzt die weiße Ring-LED des externen Tasters auf nominal 10 mA und übernimmt die Low-Side-PWM direkt über seinen EN-Pin. GPIO38 führt über 100 Ω auf EN; 100 kΩ nach GND hält die LED ohne Firmware aus. Die PWM bleibt unter 25 kHz. Spannungsreserve und Verlustleistung werden mit dem realen APEM-Taster bei 5 V und 14 V geprüft.

### 3.6 RTC und Backup

`RV-3028-C7-32.768kHz-1ppm-TA-QC` liegt mit dem Touch am gemeinsamen I2C-Bus. Eine austauschbare Panasonic `BR1225` sitzt im THT-Halter `Keystone 500`. `BAS116,215` sperrt den Ladestrom hardwareseitig von `3V3_CORE` zur Primärzelle. Die RTC-interne Ladefunktion bleibt zusätzlich dauerhaft deaktiviert. RTC-INT erhält einen Testpunkt, aber keinen ESP32-GPIO.

### 3.7 Lokale Taster und Diagnoseanzeige

BOOT, RESET und DIAG verwenden `KMR221GLFS`, SPST-NO, −40…+85 °C. Die sieben roten LEDs – fünf Diagnose- und zwei optionale Status-LEDs – sind `LTST-C190KRKT` im 0603-Gehäuse. Widerstände begrenzen die Diagnose-LEDs auf 0,5 mA bis 1 mA; die Status-LEDs werden auf vergleichbare Helligkeit abgeglichen.

Die Quellen 12V, USB, 3V3 und HEAT speisen jeweils ihren eigenen LED-/Widerstands-/Sperrdiodenzweig. Niedrig leckende `BAS116,215` verhindern eine Rückspeisung zwischen den Zweigen. Ein gemeinsamer `2N7002KQ-13`, dessen Gate nur der lokale DIAG-Taster über ein diodenentkoppeltes Presence-OR freigibt, schaltet die Anzeige. Im RUN-Zweig liegt ein zweiter GPIO39-gesteuerter `2N7002KQ-13` in Serie, sodass RUN nur bei gedrücktem DIAG und erfolgreichem Firmwarestart leuchtet. Gate-Klemmung, Widerstände und der Leckstromnachweis werden in Phase 2 berechnet.

## 4. Außensteckverbinder und Kabelbaumteile

Alle Board-Header sind rechtwinklige, schwarze, vergoldete Nano-Fit-THT-Typen. Unterschiedliche Polzahlen verhindern das Vertauschen der vier Schnittstellen.

| Ref. | Funktion | Board-Header | Gegenstecker | TPA | Crimpkontakt |
|---|---|---|---|---|---|
| J1 | Versorgung, 2-polig | `1053131302` | `1053071202` | `1053251002` | `1053002300`, 22–20 AWG, 0,76 µm Au |
| J2 | AUTOTERM, 4-polig | `1053131304` | `1053071204` | `1053251004` | `1053001300`, 26–24 AWG, 0,76 µm Au |
| J3 | 1-Wire, 3-polig | `1053131303` | `1053071203` | `1053251003` | `1053001300`, 26–24 AWG, 0,76 µm Au |
| J4 | Taster/LED, 5-polig | `1053131305` | `1053071205` | `1053251005` | `1053001300`, 26–24 AWG, 0,76 µm Au |

J4-Pin 5 bleibt NC. Falls der verwendete Sensorkabelquerschnitt größer als 24 AWG ist, wird für J3 der Kontakt `1053002300` verwendet. Gold darf nur mit Gold gepaart werden. Die korrekte Molex-Crimpzange und die Verarbeitungshöhen werden in der Kabelbaumzeichnung genannt. Die THT-Header können bei PCBWay Handbestückung beziehungsweise einen gesonderten PCBA-Arbeitsschritt erfordern.

## 5. Festgelegte Bauteile

| Funktionsblock | Herstellerteilenummer | Gehäuse / Bereich | Beschaffungsstatus für 5 Prototypen |
|---|---|---|---|
| ESP32-Modul | `ESP32-S3-WROOM-1U-N16R8` | Modul, −40…+85 °C mit PSRAM-ECC-Anforderung | Hersteller-/PCBWay-Angebot vor Bestellung |
| 12-V-Controller | `LM74720QDRRRQ1` | WSON-12 3×3 mm, −40…+125 °C | PCBWay-/LCSC-Angebot vor Bestellung |
| Dualer Schutz-MOSFET | `IPG20N06S4L-26` | TDSON-8, 60 V, AEC-Q101 | LCSC `C112995`, Bestand erneut prüfen |
| Eingangs-TVS | `TPSMB18CA-VR` | DO-214AA, 18 V, 600 W, AEC-Q101 | RFQ/Beistellung; Bestand schwankend |
| 3,3-V-Buck | `LMR43620MSC3RPERQ1` | VQFN-HR, −40…+150 °C, AEC-Q100 | LCSC `C3190193`, Bestand erneut prüfen |
| Buckinduktivität | `XAL4020-222MEC` | 2,2 µH ±20 %, Isat 5,6 A | Angebot/Bestand vor Bestellung |
| Buck-Eingangskondensator | `GCJ32ER71H475KA12` | 4,7 µF/50 V/X7R/1210, AEC-Q200 | DC-Bias-Kurve prüfen |
| USB-eFuse | `TPS259470LRPWR` | WQFN 2×2 mm, −40…+125 °C | LCSC `C3662793`, Bestand erneut prüfen |
| Type-C-Erkennung | `TUSB321AIRWBR` | X2QFN-12, −40…+85 °C | PCBWay-/LCSC-Angebot vor Bestellung |
| USB-C-Stecker | `USB4105-GF-A-120` | SMT + Halteanker, −40…+85 °C | LCSC `C5184243`, Bestand erneut prüfen |
| USB-Daten-ESD | `TPD2EUSB30DRTR` | SOT-5, 0,7 pF, −40…+85 °C | LCSC `C97502`, Bestand erneut prüfen |
| USB-VBUS-ESD | `ESD5Z5.0T1G` | SOD-523, −55…+150 °C | PCBWay-/LCSC-Angebot vor Bestellung |
| 3,3-V-Supervisor | `TPS3808G33QDBVRQ1` | SOT-23-6, −40…+125 °C, AEC-Q100 | LCSC `C414616`, Bestand erneut prüfen |
| 3,0-V-AON-LDO | `TPS7A0230PDBVR` | SOT-23-5, −40…+125 °C | LCSC `C3747031`, Bestand erneut prüfen |
| Display-Lastschalter | `TPS22919QDCKRQ1` | SC70-6, −40…+125 °C, AEC-Q100 | LCSC `C2871558`, Bestand erneut prüfen |
| Sensor-Lastschalter | `TPS22945DCKR` | SC70-5, −40…+85 °C | RFQ/Beistellung |
| AUTOTERM-Pegelwandler | `TXU0202QDCURQ1` | VSSOP-8, −40…+125 °C, AEC-Q100 | LCSC `C7372013`, Bestand erneut prüfen |
| Externe 5-V-ESD | `PESD5V2S2UT-Q` | SOT-23, AEC-Q101 | RFQ/Beistellung |
| Externe 3,3-V-ESD | `PESD3V3S2UT-Q` | SOT-23, AEC-Q101 | RFQ/Beistellung |
| Display-Ausgangsisolation | `SN74AXC8T245PWR` | TSSOP-24, −40…+125 °C | LCSC `C882718`, Bestand erneut prüfen |
| Display-BUSY-Isolation | `SN74AXC1T45DCKR` | SC70-6, −40…+125 °C | LCSC `C2677392`, Bestand erneut prüfen |
| Touch-Reset-Puffer | `SN74LVC1G07QDBVRQ1` | SOT-23-5, −40…+125 °C, AEC-Q100 | RFQ/Beistellung |
| E-Paper-Booster-MOSFET | `SI1308EDL-T1-GE3` | SOT-323, 30 V, −55…+150 °C | LCSC `C469327`/RFQ |
| E-Paper-Boosterdiode | `MBR0530T1G` | SOD-123, 30 V, 0,5 A | PCBWay-/LCSC-Angebot vor Bestellung |
| Frontlichttreiber | `AL8861QMP-13` | MSOP-8EP, −40…+125 °C, AEC-Q100 | LCSC `C2678638`, Bestand erneut prüfen |
| Display-/Frontlichtinduktivität | `LQH3NPZ470MJR` | 47 µH, mindestens 570 mA, 3-mm-Klasse | Footprint/Bestellsuffix offen |
| Frontlichtdiode | `B140Q-13-F` | SMA, 1 A/40 V, automotive | Bestand erneut prüfen |
| Frontlicht-Eingangskondensator | `CGA6P1X7R2A106K250AC` | 10 µF/100 V/X7R/1210, AEC-Q200 | DC-Bias-Kurve prüfen |
| Taster-LED-Konstantstrom/PWM | `BCR421UW6Q-7` | SOT-26, direkter EN-/PWM-Eingang, nominal 10 mA, AEC-Q101 | Bestand und Herstellerfreigabe erneut prüfen |
| USB-Stromsignal-Entkopplung/Diagnose-MOSFET | `2N7002KQ-13` | SOT-23, 60 V, AEC-Q101 | LCSC `C526325`, Bestand erneut prüfen |
| RTC | `RV-3028-C7-32.768kHz-1ppm-TA-QC` | C7, −40…+85 °C | LCSC `C3019759`/RFQ; MPN prüfen |
| Batteriesperrdiode | `BAS116,215` | SOT-23, AEC-Q101, Low Leakage | LCSC `C48502`, Bestand erneut prüfen |
| Knopfzelle | Panasonic `BR1225` | 12,5×2,5 mm, −30…+85 °C | Nicht durch PCBA-Reflow; separat einsetzen |
| Knopfzellenhalter | Keystone `500` | THT für 12-mm-Zelle | LCSC `C238121`/Beistellung |
| lokale Taster | `KMR221GLFS` | SMT 4,6×2,8 mm, SPST-NO, −40…+85 °C | LCSC `C72443`, Bestand erneut prüfen |
| rote Diagnose-/Status-LED | `LTST-C190KRKT` | 0603, −30…+85 °C | LCSC `C94869`, Bestand erneut prüfen |
| E-Paper-FPC | `FH12-24S-0.5SH(55)` | 24-polig, Bottom-Contact, 0,5 mm | LCSC `C202112`; Musterprüfung offen |
| Touch-/Licht-FPC | `FH12-6S-0.5SH(55)` | 6-polig, Bottom-Contact, 0,5 mm | LCSC `C202118`; Musterprüfung offen |

Die LCSC-Nummern sind eine Vorprüfung, keine Reservierung und keine Qualitätsfreigabe. Beim PCBA-Angebot müssen Herstellername und vollständige MPN Vorrang vor Distributor-Kurztexten haben. Kritische oder nicht lagernde Teile werden als genuine customer-supplied parts beigestellt.

## 6. Footprint- und Pinoutregeln

- WROOM-1U: ausschließlich das offizielle Espressif-Landpattern mit 41 Pads verwenden; die N16R8-Modulpins 35 bis 37 sind nicht als freie GPIOs zu behandeln.
- WSON/QFN mit Exposed Pad: Kupfer, Via-Anordnung und segmentierte Paste exakt nach Hersteller; keine automatische generische KiCad-Zuordnung ohne Zeichnungsprüfung.
- Nano-Fit: Bestellcode muss zum rechtwinkligen THT-Header, schwarzem Gehäuse und 0,76-µm-Goldkontakt passen. Schaltplansicht und Steckansicht werden getrennt dokumentiert.
- FPC: Pin 1, Kontaktseite, 0,30-mm-FPC-Dicke, Verriegelungsrichtung und FPC-Einsteckrichtung müssen in Footprint, 3D-Modell und Zeichnung identisch sein.
- Für jedes lokale Symbol werden Symbol-Pinout, Footprint-Padnummern und Herstellerzeichnung in Phase 2 in einer unabhängigen Dreifachprüfung abgeglichen.

## 7. Sichere Hardwarezustände

| Funktion | Hardwaremaßnahme | Zustand ohne Firmware |
|---|---|---|
| ESP32 EN | Supervisor + 10-kΩ-Pull-up + RESET nach GND | LOW bis Versorgung stabil |
| BOOT | 10-kΩ-Pull-up, Taster nach GND | HIGH / Normalboot |
| Displayversorgung | Pulldown an Lastschalter-EN | AUS |
| Displayausgänge | AXC-Isolation, `/OE`-Pull-up; displayseitige Pulls | hochohmig; nach Einschalten CS HIGH, RESET/SCLK/SDIO/DC LOW |
| Sensorversorgung | Pulldown an Lastschalter-EN | AUS |
| Touch-Reset | GPIO7-Pulldown + Open-Drain-Puffer | LOW beim Power-up |
| Frontlicht | Pulldown am PWM/DIM-Eingang | AUS |
| Taster-LED | Gate-Pulldown | AUS |
| AUTOTERM | OE-Pulldown | TX zur Heizung hochohmig |
| RUN/Status-LEDs | Pulldowns beziehungsweise active-high mit sicheren GPIOs | AUS |

## 8. Verfügbarkeit und Fertigungsstrategie

Für fünf Prototypen ist PCBWay-Turnkey grundsätzlich möglich, aber die Kombination aus automotive-qualifizierten Typen, mehreren Spezialgehäusen, THT-Nano-Fit und MSL-3-WROOM erfordert eine manuelle BOM-Prüfung. Vor Bestellung werden deshalb BOM und MPN-Liste als RFQ an PCBWay gesendet. Nicht eindeutig verfügbare Bauteile werden nicht automatisch ersetzt, sondern beigestellt oder nach dokumentierter Gleichwertigkeitsprüfung freigegeben.

Das WROOM-Modul darf nur einen Reflow-Zyklus erhalten. PCBWay muss bestätigen, dass es beim zweiten/finalen Reflow bestückt wird. Nano-Fit-THT, Knopfzellenhalter und eventuell weitere THT-Teile werden nach dem Reflow verarbeitet; die BR1225 wird erst nach Reinigung und Abschluss der Lötarbeiten eingesetzt.

## 9. Verifikationspunkte vor Phase-2-Freeze beziehungsweise Fertigung

### Vor Abschluss des Schaltplans in Phase 2

1. Pinouts aller ICs aus den aktuellen Herstellerdatenblättern unabhängig gegen Symbol und Footprint prüfen.
2. LMR43620-Q1-Induktivität, Ein-/Ausgangskondensatoren, Ripple, Stromgrenze, Start und thermische Reserve mit TI-Berechnung festlegen.
3. LM74720-Q1-OV-Teiler, Gate-Netz, Boostbauteile, MOSFET-SOA und TVS-/Filterkoordination rechnen; `RTN` bleibt NC.
4. TPS259470-RILM und Inrush so auslegen, dass USB-Grenzen inklusive Toleranzen eingehalten werden.
5. E-Paper-Booster exakt gegen Kapitel 12 der Display-Spezifikation übertragen und unabhängig prüfen.
6. Frontlicht-Induktivität, Schottkydiode, Messwiderstand, PWM-Frequenz und Worst-Case-LED-Strom rechnen.
7. Diagnose-LED-Trennung und Leckstrom kleiner 5 µA pro Quelle nachweisen.

### Vor Footprint-/Layout-Freeze

1. Originales `GDEY029T94-FT01` mechanisch prüfen; erst danach FPC-Kontaktseite und die drei Footprint-MPNs festschreiben.
2. FT6336U-INT-Topologie, LOW-Pulsdauer und Wake-Verhalten messen; danach 0-Ω-Direktpfad oder Wake-Latch bestücken.
3. APEM-Code `AV970220000700` und LED-Polarität durch Hersteller oder autorisierten Distributor bestätigen.
4. PCBWay-Angebot für alle exakten MPNs, beidseitige Bestückung, THT und Reflow-Reihenfolge bestätigen.
5. Vollständige Platzierung einschließlich aller Steck-/Entriegelungswege im 98-mm-×-48-mm-Zielumriss prüfen.

## 10. Phase-1-Freigabekriterien

- [x] Block- und Versorgungskonzept festgelegt
- [x] Spannungsdomänen und Power-OR festgelegt
- [x] Vollständige GPIO-Matrix einschließlich Wake-, Reset- und Bootzuständen erstellt
- [x] Leistungs-, USB-, Verlustleistungs- und Ruhestrombudget erstellt
- [x] Aktive Bauteile, Schutzbauteile, Nano-Fit und vorläufige FPC-Stecker mit vollständiger MPN festgelegt
- [x] Temperaturbereiche, Footprintregeln und Beschaffungsrisiken dokumentiert
- [x] Offene Punkte als mess- oder prüfbare Verifikationspunkte klassifiziert
- [x] Phase 1 durch Auftraggeber am 06.09.2026 freigegeben

## 11. Herstellerreferenzen

- [Espressif ESP32-S3-WROOM-1/1U Datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [TI LM74720-Q1](https://www.ti.com/product/LM74720-Q1)
- [TI LMR43620-Q1](https://www.ti.com/product/LMR43620-Q1)
- [TI TPS25947](https://www.ti.com/product/TPS25947)
- [TI TUSB321](https://www.ti.com/product/TUSB321)
- [TI TXU0202-Q1](https://www.ti.com/product/TXU0202-Q1)
- [Diodes Incorporated BCR420/BCR421UW6Q](https://www.diodes.com/datasheet/download/BCR420UW6Q.pdf)
- [Good Display GDEY029T94-FT01 specification](https://v4.cecdn.yun300.cn/100001_1909185148/GDEY029T94-FT01.pdf)
- [FocalTech FT6336U datasheet](https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf)
- [Micro Crystal RV-3028-C7](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7)
- [Molex Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors)
- [Hirose FH12 series](https://www.hirose.com/product/series/FH12)
