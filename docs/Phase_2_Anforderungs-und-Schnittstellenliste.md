# Phase 2 – Anforderungs- und Schnittstellenliste Revision A

Stand: 2026-09-06

Diese Liste ist die kompakte Prüfansicht der [Hardware-Anforderungsspezifikation 1.6](Hardware-Anforderungsspezifikation_Revision_A.md). Bei Widersprüchen gilt die Hauptspezifikation.

## 1. Betriebs- und Versorgungsanforderungen

| ID | Anforderung | Umsetzung/Netz | Nachweisstatus |
|---|---|---|---|
| PWR-01 | Zweitbatterie 10…14 V nominal | J1.1 `BATT_12V_IN`, J1.2 GND | Schaltplan erfüllt |
| PWR-02 | Nur 12-V-System, keine 24-V-Dauerfunktion | LM74720-Q1, 60-V-MOSFET, 18-V-OV-Teiler | erfüllt; Transientenprofil offen |
| PWR-03 | externe 1-A-Sicherung; keine Boardsicherung | J1 ohne Sicherung | erfüllt |
| PWR-04 | Verpolung, Rückstrom und Überspannungsabschaltung | D1/U1/Q1/D17, `VIN_12V_PROTECTED` | Topologie erfüllt; SOA/TVS offen |
| PWR-05 | USB-C versorgt Board ohne 12 V | J5/U2/U3/NT1 nach `VIN_SYS` | erfüllt |
| PWR-06 | keine Rückspeisung 12 V→USB oder 3V3→TUSB321 | TPS259470L und Q8-Domänenentkopplung | erfüllt, am Prototyp messen |
| PWR-07 | effizienter 3,3-V-Regler, 2-A-Spitzenreserve | LMR43620-Q1, 2,2 µH, 2 × 22 µF | Startauslegung erfüllt; Stabilität offen |
| PWR-08 | sichere Resetfolge | TPS3808G33-Q1, CT offen ≈20 ms, EN-RC | erfüllt; Hochlauf messen |
| PWR-09 | Low-Power-Hardwarezustand | schaltbare Display-/Sensorlasten, Front-/Ringlicht aus | erfüllt; Ruhestrom messen |

## 2. Außenanschlüsse

| Anschluss | Stecker | Pin | Signal | Elektrische Funktion |
|---|---|---:|---|---|
| J1 12 V | Molex Nano-Fit 2-pol. `1053131302` | 1 | `BATT_12V_IN` | +10…14 V aus abgesicherter Zweitbatterie |
|  |  | 2 | GND | Masse |
| J2 AUTOTERM | Nano-Fit 4-pol. `1053131304` | 1 | `AUTOTERM_5V` | von der Heizung gelieferte 5 V; keine Boardquelle |
|  |  | 2 | GND | gemeinsame Masse |
|  |  | 3 | `CTRL_TX_TO_HEATER` | 5-V-UART, Controller→Heizung |
|  |  | 4 | `CTRL_RX_FROM_HEATER` | 5-V-UART, Heizung→Controller |
| J3 1-Wire | Nano-Fit 3-pol. `1053131303` | 1 | `3V3_SENSOR_SW` | geschaltete Sensorversorgung |
|  |  | 2 | `1WIRE_DQ` | drei DS18B20 parallel, zusammengeführt, 2…5 m |
|  |  | 3 | GND | Sensor-Masse |
| J4 Taster/LED | Nano-Fit 5-pol. `1053131305` | 1 | `BUTTON_N_EXT` | NO-Taster nach GND, 3-m-Leitung |
|  |  | 2 | GND | Tasterpaar-Rückleiter |
|  |  | 3 | `LED_CC_PLUS` | Versorgung weiße Ring-LED aus VIN_SYS |
|  |  | 4 | `LED_PWM_MINUS` | stromgeregelter PWM-Kathodenpfad |
|  |  | 5 | NC | Reserve, unbeschaltet |
| J5 USB-C | GCT `USB4105-GF-A-120` | USB-Standard | VBUS, CC1/2, D±, GND, Shield | USB-2.0-Gerät/Sink, kein PD |
| J6 E-Paper | Hirose `FH12-24S-0.5SH(55)` | 1…24 | gemäß Displaytabelle | elektrisch gemäß GDEY029T94-FT01; mechanisch vorläufig |
| J7 Touch | Hirose `FH12-6S-0.5SH(55)` | 1…6 | GND, INT, RESET, 3V0, SCL, SDA | elektrisch gemäß Display; mechanisch vorläufig |
| J8 Frontlight | Hirose `FH12-6S-0.5SH(55)` | 1…6 | A, A, NC, NC, K, K | 50-mA-Konstantstrom; Orientierung vorläufig |

Kabelbaumvorgabe J4: Pins 1/2 als verdrilltes Paar, Pins 3/4 als zweites verdrilltes Paar. J2 und J3 benötigen eine robuste gemeinsame Masse; Schirm/Reserve ist in Revision A nicht vorgesehen.

## 3. Logik- und Peripherieschnittstellen

| ID | Funktion | ESP32 | Hardwarebedingungen |
|---|---|---|---|
| IF-01 | natives USB 2.0 FS | GPIO19 D−, GPIO20 D+ | TPD2EUSB30 am Stecker; 22 Ω am Modul; 10-pF-Plätze DNP |
| IF-02 | AUTOTERM UART | GPIO16 TX, GPIO17 RX, GPIO47 OE | TXU0202-Q1; 3,3-V-A-Seite, heizungsseitige 5-V-B-Seite; default hochohmig |
| IF-03 | 1-Wire | GPIO4 | 4,7 kΩ nach geschalteten 3,3 V; 0 Ω Serie; ESD-Array |
| IF-04 | I2C | GPIO5 SDA, GPIO6 SCL | Pull-ups 4,7 kΩ an 3,0 V AON; RV-3028 + FT6336U |
| IF-05 | E-Paper SPI | GPIO9/10/11/12/13 plus GPIO8 BUSY | write-only, Power-off-Pegelisolation; Serien-R 33 Ω; Tuning-C DNP |
| IF-06 | Touch-Wake | GPIO2 | active LOW; Standard-Direktpfad, Latch vollständig DNP |
| IF-07 | Taster-Wake | GPIO1 | active LOW, 1 kΩ/10 nF/ESD, externer 10-kΩ-Pull-up |
| IF-08 | Ring-LED PWM | GPIO38 | BCR421 EN, <25 kHz, hardwareseitig aus |
| IF-09 | Frontlight PWM | GPIO21 | AL8861 VSET/PWM, empfohlen ≤500 Hz, hardwareseitig aus |
| IF-10 | Diagnose RUN | GPIO39 | leuchtet nur bei DIAG-Freigabe und Firmware-HIGH |
| IF-11 | USB-Leistung | GPIO40 | `USB_HIGH_CURRENT`; LOW = USB Default Current, HIGH = ≥1,5 A oder kein USB |
| IF-12 | optionale LEDs | GPIO41/42 | R/LED standardmäßig DNP |

## 4. Display- und Touchpflichten

- GDEY029T94-FT01 wird elektrisch nach Herstellerkapitel 12 angeschlossen; die dortige Booster-Topologie darf nicht eigenmächtig ersetzt werden.
- Displaylogik liegt an `3V3_DISPLAY_SW`; abgeschaltet dürfen keine ESP32-Signale das Display rückspeisen.
- FT6336U liegt dauerhaft an `3V0_TOUCH_AON = 3,0 V`; I2C-HIGH liegt damit innerhalb 2,8…3,3 V.
- Komfort-Standby nutzt Touch-Monitor und active-low INT als Wakequelle. Hibernation ist sparsamer, unterstützt aber kein zugesichertes Touch-Wake.
- FPC-Kontaktseite und Pin-1-Orientierung müssen am echten Modul geprüft werden. Die Datenblätter definieren die elektrische Reihenfolge, nicht hinreichend sicher die konkrete Steck-/Biegegeometrie im geplanten Gehäuse.

## 5. Mechanik und Fertigung

- Zielkontur höchstens 100 × 50 mm; Arbeitsziel 98 × 48 mm. Kabel und externe Steckergehäuse zählen nicht zum Umriss.
- Vierlagenaufbau: L1 Bauteile/Signale, L2 durchgehende GND-Fläche, L3 Versorgung/langsame Signale, L4 Signale/Displayseite. Kein Zweilagen-Redesign ohne erneuten EMV-/Power-Review.
- Display auf einer Seite, Nano-Fit gegenüber, USB-C seitlich; 35 mm verfügbare Einbautiefe; Gehäuse wird 3D-gedruckt.
- ESP32-S3-WROOM-1U verwendet die U.FL-/IPEX-Antenne am Modul; keine PCB-Antenne und keine HF-Leiterbahn auf dem Board.
- PCBWay-Bestückung für fünf Prototypen. Kritische MPNs dürfen nicht ohne schriftliche technische Gleichwertigkeitsprüfung ersetzt werden.

## 6. Nicht Teil von Revision A

VOTRONIC VBCS 45/30/350 Triple CI und VOTRONIC Smart-Shunt 100 A sind nur für eine spätere Revision vorgemerkt. Es gibt in Revision A keine RS-485-Hardware, Relaisausgänge oder zusätzlichen Open-Drain-Lasttreiber.
