# LandyHeater-Board Rev. A – Anforderungsliste (Extrakt zur Freigabe)

Quelle: `fabianhartmann2/LandyHeater-Board`, Branch `codex/phase2-schematic-review` (Commit c8ee5d1), Spezifikation v1.6 vom 2026-09-06, Phase-1-Architektur, GPIO-Matrix, Budgets, Phase-2-Netzliste.

## 1. Funktion

Bedien- und Kommunikationssteuergerät für eine AUTOTERM/Planar-Dieselstandheizung (Land Rover, Mittelkonsole/Cubby Box).

- F1 – 5-V-UART zur originalen Heizungssteuerung (Vollduplex, 0,3 bis 0,5 m)
- F2 – drei DS18B20 an einem gemeinsamen 3-Draht-1-Wire-Bus (2 bis 5 m), fest an GPIO4
- F3 – E-Paper 2,9" mit kapazitivem Touch und Frontlicht (Good Display GDEY029T94-FT01)
- F4 – externer Taster (APEM AV970220000700, 3 m Leitung) mit dimmbarer weißer Ring-LED (10 mA)
- F5 – RTC mit Knopfzellenpufferung (≥ 4 Wochen)
- F6 – WLAN über ESP32-S3, externe Antenne per U.FL (keine HF-Leitung auf dem PCB)
- F7 – natives USB für Flashen/REPL, kein USB-UART-Wandler
- F8 – Energiefluss-Diagnose: 5 rote LEDs (12V, USB → 3V3 → RUN → HEAT), leuchten nur bei gedrücktem DIAG-Taster
- F9 – Betriebszustände: Normal; Komfort-Standby (Deep-Sleep, Touch im Monitor-Modus, Wake per Taster oder Touch); Minimal-Standby (Touch in Hibernation, Wake nur per Taster)
- Das Board schaltet keine Heizungslasten. Ausgeschlossen sind: RS-485, CAN, VOTRONIC, KL15, Relais/High-Side-Ausgänge, PCB-Antenne, USB-PD und eine Sicherung auf dem Board.

## 2. Versorgung und Spannungsdomänen

| Netz | Quelle / Bauteil | Wert | Anforderung |
|---|---|---|---|
| `BATT_12V_IN` | J1, extern mit 1 A abgesichert, 0,5 mm² | 10–14 V | Verpolung −14 V ≥ 60 s; TVS TPSMB18CA; LM74720-Q1 + Dual-FET IPG20N06S4L-26 (Verpolung, Rückstrom, OV ≈ 18,5 V); RTN offen |
| `USB_VBUS` | USB-C USB4105-GF-A-120 | 5 V | Sink ohne PD; TUSB321AI (Rd intern, Stromerkennung); eFuse TPS259470L (1 A, OVLO 5,8 V, Rückstromsperre) |
| `VIN_SYS` | Power-OR aus 12 V (Ferrit-Filter) und USB-eFuse | 4,75–14 V (OV bis ca. 20 V) | 12 V hat Vorrang, gegenseitige Rückstromsperre |
| `3V3_CORE` | LMR43620-Q1 Buck, fest 3,3 V / 2 A / 2,2 MHz, 2,2 µH | 3,0–3,6 V | Auto-PFM; ≥ 0,5 A für das ESP32; 2 × 22 µF + 100 nF am Modul |
| `3V0_TOUCH_AON` | TPS7A0230 LDO | 2,8–3,3 V | Touch-Controller und I2C-Pull-ups, immer an |
| `3V3_DISPLAY_SW` | TPS22919-Q1 Lastschalter | 3,3 V | E-Paper, im Deep-Sleep aus, Quick-Discharge |
| `3V3_SENSOR_SW` | TPS22945 (strombegrenzt) | 3,3 V | DS18B20, im Deep-Sleep aus, kurzschlussfest |
| `AUTOTERM_5V(_PROTECTED)` | nur von der Heizung, über TPS22945 | 5 V | nur VCCB des Pegelwandlers; keine Verbindung zu USB oder VIN_SYS |
| `RTC_VBACKUP` | BR1225 im Keystone 500, über BAS116 | 3 V | Laden hardwareseitig gesperrt |

Budgets: Vollbetrieb ca. 0,27 A bei 12 V und ca. 0,65 A bei USB; Flashen mit USB-Default-Current < 0,5 A; Ziel im Komfort-Standby < 0,5 mA bei 12 V (gerechnet 0,41 mA).

## 3. Schnittstellen

### 3.1 Außenanschlüsse (Molex Nano-Fit, rechtwinklig, THT, Goldkontakte, durch Polzahl codiert)

| Ref | MPN | Pins |
|---|---|---|
| J1 Versorgung | 1053131302 | 1 `BATT_12V_IN`, 2 GND |
| J2 AUTOTERM | 1053131304 | 1 `AUTOTERM_5V`, 2 GND, 3 `CTRL_TX_TO_HEATER`, 4 `CTRL_RX_FROM_HEATER` |
| J3 1-Wire | 1053131303 | 1 `3V3_SENSOR_SW`, 2 `1WIRE_DQ`, 3 GND |
| J4 Taster/LED | 1053131305 | 1 `BUTTON_N`, 2 GND, 3 `LED_CC_PLUS`, 4 `LED_PWM_MINUS`, 5 NC |
| J5 USB-C | USB4105-GF-A-120 | USB 2.0 FS, D± über TPD2EUSB30, 22 Ω am Modul, 10-pF-Plätze als DNP |

### 3.2 Display-FPCs (Hirose FH12, 0,5 mm, Bottom-Contact, vorläufig)

- J6 E-Paper 24-polig (FH12-24S-0.5SH(55)), Pinbelegung gemäß Spezifikation §10.2: SPI nur schreibend (SCLK, MOSI, CS, DC, RES, BUSY), BS1 auf GND, Booster-Referenzschaltung aus Kapitel 12 (Si1308EDL, 3 × MBR0530, 47 µH, 2,2 Ω / 1 MΩ, C ≥ 25 V)
- J7 Touch 6-polig: GND, INT, RESET, 3V0, SCL, SDA
- J8 Frontlicht 6-polig: A, A, NC, NC, K, K; AL8861Q, 50 mA (< 60 mA im Worst Case), PWM an GPIO21

### 3.3 Interne Logik

- E-Paper-Signale über SN74AXC8T245 (5 Ausgänge) und SN74AXC1T45 (BUSY) mit Power-off-Isolation, 33-Ω-Serienwiderstände
- Touch-Reset über SN74LVC1G07-Q1 (Open-Drain); optionales Wake-Latch SN74LVC1G74 als DNP
- AUTOTERM über TXU0202-Q1, OE mit Pulldown (TX hochohmig bis zur Freigabe), PESD5V2S2UT-Q, 100 Ω in Serie
- 1-Wire: 4,7 kΩ an `3V3_SENSOR_SW`, 0 Ω in Serie, PESD3V3S2UT-Q
- Taster: 1 kΩ / 10 nF / 10 kΩ Pull-up / PESD3V3S1BA; Ring-LED: BCR421UW6Q auf der Low-Side, EN = PWM an GPIO38, 100-kΩ-Pulldown
- RTC RV-3028-C7 und Touch FT6336U am gemeinsamen I2C-Bus (4,7 kΩ an 3V0)

### 3.4 GPIO-Matrix (verbindlich)

| GPIO | Signal | GPIO | Signal |
|---|---|---|---|
| 0 | BOOT (10 k Pull-up, Taster) | 14 | DISPLAY_EN |
| 1 | BUTTON_N (EXT1-Wake) | 15 | SENSOR_EN |
| 2 | TOUCH_INT_N (EXT1-Wake) | 16 / 17 | AUTOTERM TX / RX |
| 4 | 1WIRE_DQ | 18 | LATCH_CLR (DNP) |
| 5 / 6 | I2C SDA / SCL | 19 / 20 | USB D− / D+ |
| 7 | TOUCH_RESET_RELEASE | 21 | FRONTLIGHT_PWM |
| 8 | EPD_BUSY | 38 | BUTTON_LED_PWM |
| 9–13 | EPD SCLK / MOSI / CS / DC / RST | 39 | DIAG_RUN |
| 40 | USB_HIGH_CURRENT | 41 / 42 | Status-LEDs (optional, DNP) |
| 43 / 44 | U0TXD (499 Ω) / U0RXD, nur Testpads | 47 | AUTOTERM_OE |

Nicht verwenden: GPIO3, 45, 46 und 48 (Reserve) sowie 35–37 (PSRAM).

Reset: TPS3808G33-Q1 und RESET-Taster an EN, EN mit 10 kΩ / 1 µF. Alle Enables und PWM-Ausgänge haben Pull-downs; ohne Firmware ist alles aus.

## 4. Schlüsselbauteile

ESP32-S3-WROOM-1U-**N16R8**, LM74720QDRRRQ1, IPG20N06S4L-26, TPSMB18CA-VR, LMR43620MSC3RPERQ1 und XAL4020-222MEC, TPS259470LRPWR, TUSB321AIRWBR, USB4105-GF-A-120, TPD2EUSB30, ESD5Z5.0, TPS3808G33-Q1, TPS7A0230, TPS22919-Q1, 2 × TPS22945, TXU0202-Q1, SN74AXC8T245, SN74AXC1T45, SN74LVC1G07-Q1, Si1308EDL, 3 × MBR0530, AL8861Q, LQH3NPZ470 (2 ×), B140Q, BCR421UW6Q, RV-3028-C7, BAS116 (6 ×), 2N7002KQ (4 ×), BC857BQ, LTST-C190KRKT (5 + 2 DNP), KMR221G (3 ×), Keystone 500, Nano-Fit (4 ×), FH12 (3 ×). Insgesamt 232 Referenzen, davon 56 DNP (hauptsächlich Testpunkte).

## 5. Mechanik und PCB

- PCB höchstens **98 × 48 mm**; die Gesamteinheit mit Display passt in 100 × 50 × 35 mm
- **4 Lagen**, 1,6 mm, FR-4 mit Tg ≥ 150, 1 oz außen, ENIG, keine Blind- oder Buried-Vias
- Lagen: L1 (Top) = Elektronikseite mit ESP32, USB und Buck; L2 = durchgehende GND-Fläche; L3 = Versorgung; L4 (Bottom) = Displayseite, nur störarme Bauteile
- Display liegt auf L4. Nano-Fit-Stecker sitzen an der gegenüberliegenden Anschlussseite, USB-C an einer seitlichen Kante
- FPC-Stecker direkt an den FPC-Austritten, mit Keep-outs für Biegeradius und Verriegelung
- ≥ 3 Befestigungspunkte; Knopfzelle, BOOT, RESET, DIAG und U.FL im geöffneten Gehäuse erreichbar
- Layoutregeln: USB als 90-Ω-Differenzpaar; offizielles WROOM-1U-Landpattern; kein Antennen-Keep-out (1U); Hot-Loops von Buck und E-Paper-Booster kompakt und fern von Touch, I2C, RTC und USB; ESD direkt an den Steckern; GND-Stitching; unter dem WROOM auf L4 nichts Schnelles
- ESP32 durchläuft nur **einen Reflow** (MSL 3), also wird es auf der zweiten Seite bestückt
- Silkscreen: Pin 1, Polarität, Steckernamen, BOOT/RESET/DIAG, Rev. A, Testpunkte, Diagnose-Flussbild

## 6. Was mir beim Lesen aufgefallen ist

1. **Fertiger:** Die Spezifikation schreibt durchgehend PCBWay vor (Stackup, Prozessfolge, Handbestückung). Ihr Auftrag nennt JLCPCB. Ich würde auf JLCPCB umstellen (JLC04161H-7628, Impedanz nach JLC-Rechner).
2. **LCSC-Verfügbarkeit:** Die Spezifikation verbietet Ersatzteile ohne Gleichwertigkeitsnachweis. Folgende Teile sind im Repo bereits als „RFQ/Beistellung“ oder „Angebot vor Bestellung“ markiert: TPSMB18CA-VR, TPS22945DCKR, PESD5V2S2UT-Q, PESD3V3S2UT-Q, SN74LVC1G07QDBVRQ1, XAL4020-222MEC, LQH3NPZ470MJR, LM74720QDRRRQ1, TUSB321AIRWBR, ESD5Z5.0T1G, MBR0530T1G, außerdem eventuell ESP32-S3-WROOM-1U-N16R8 und Nano-Fit. Für JLC brauche ich eine dieser Regeln: (a) nur exakte MPN, notfalls über JLC Global Sourcing oder Beistellung; oder (b) pin- und funktionsgleiche LCSC-Alternativen mit dokumentiertem Vergleich.
3. **Lücke im Bestand:** `LED_CC_PLUS` hängt über R65 (0 Ω) direkt an `VIN_SYS`. Ein Kurzschluss im 3-m-Tasterkabel schließt damit VIN_SYS kurz. Abgesichert ist das dann nur durch die externe 1-A-Sicherung bzw. die USB-eFuse. Die Spezifikation §11 fordert eine „geeignete Strombegrenzung“. Mein Vorschlag: ein PTC oder ein Serienwiderstand mit ca. 100 Ω statt 0 Ω (der BCR421 regelt trotzdem auf 10 mA).
4. **Kleinigkeiten:** Die BOM-Notiz zu R8 nennt eine OVLO von ca. 5,95 V, die Rechnung ergibt 5,82 V. L1 (XPL2010, 2 × 1,9 mm) hat einen generischen 0805-Footprint. Wird korrigiert.
5. **Offene Gates aus dem Repo:** FPC-Kontaktseite und Pin 1 am Originaldisplay, offizielle Footprints für Q1, U3, U4, RV-3028 und L3/L4, Transientenprofil, Touch-INT-Messung. Ohne Muster kann ich sie nicht schließen. Ich verwende die besten verfügbaren Datenblatt-Footprints und markiere sie im Layout und in der BOM. Gerber zum **Prototyp-Review**, nicht als freigegebener Fertigungsstand.
6. **Werkzeuge:** KiCad 10.0.6 ist installiert. Java und Freerouting fehlen. Dafür würde ich OpenJDK (Homebrew) und das offizielle Freerouting-JAR von GitHub (freerouting/freerouting, Release v2.x, ca. 20 MB) installieren.
7. **Erwartung an das Autorouting:** Freerouting liefert hier kein abnahmefähiges Layout für die kritischen Bereiche. Mein Plan: Platzierung von Hand; USB-Paar, Buck- und Booster-Hot-Loop, Leistungspfade und GND-Anbindung route ich selbst vor; Freerouting übernimmt nur die übrigen langsamen Signale. Danach DRC und Review.
