# Schaltungsentwurf – Phase 2

Stand: 2026-10-12 · Grundlage: [Anforderungsdokument](../docs/Anforderungsdokument_Neuentwicklung.md) Teil A, [Bauteilliste](Bauteilliste.md)

Dieses Dokument ist die Sollvorgabe für den Schaltplan und die Netzlistenprüfung nach N-05. Abweichungen von Teil B sind am Ende begründet.

## Seitenaufteilung

| Seite | Datei | Inhalt |
|---|---|---|
| 1 | `LandyHeater.kicad_sch` | Übersicht, Seitensymbole |
| 2 | `01_Versorgung.kicad_sch` | J1 12 V, Verpol-/Transientenschutz, USB-C mit eFuse, Zusammenführung VIN_SYS, 3,3-V-Buck |
| 3 | `02_ESP32_RTC.kicad_sch` | ESP32-S3, Reset/BOOT, USB-Daten, UART0-Testpads, RTC mit Knopfzelle |
| 4 | `03_AUTOTERM_1Wire.kicad_sch` | J2 AUTOTERM-UART mit Pegelwandler, J3 1-Wire mit Sensor-Lastschalter |
| 5 | `04_Taster_Anzeige.kicad_sch` | J4 Taster und Ring-LED, Energiefluss-Diagnose, Status-LEDs |

Seitenübergreifende Netze: Versorgungen als Power-Symbole (`GND`, `3V3_CORE`, `VIN_SYS`, `12V_PROT`, `VBUS_PROT`), Signale zwischen ESP32 und Peripherie als globale Labels mit den GPIO-Signalnamen aus A12.

## Seite 2 – Versorgung

| Ref | Teil | Wert | Verbindung |
|---|---|---|---|
| J1 | Nano-Fit 2-pol. | 1053131302 | 1 `BATT_12V_IN`, 2 `GND` |
| D1 | SMBJ18CA | TVS bidir. | `BATT_12V_IN` – `GND` |
| D2 | SS16 | 60 V/1 A | A `BATT_12V_IN`, K `12V_PROT` |
| FB1 | Ferrit 0805 | 600 Ω @ 100 MHz, ≥ 1 A | `12V_PROT` – `VIN_SYS` |
| C1 | Elko SMD | 47 µF/35 V | `VIN_SYS` – `GND` (dämpft die Resonanz Ferrit/MLCC) |
| J5 | USB-C USB4105 | 16P | VBUS (A4/A9/B4/B9) `USB_VBUS`; CC1 `CC1`; CC2 `CC2`; D+ (A6/B6) `USB_DP_C`; D− (A7/B7) `USB_DN_C`; SBU NC; GND/SH `GND` |
| R1, R2 | Rd | 5,1 kΩ 1 % | `CC1`/`CC2` – `GND` |
| D3 | ESD5Z5.0T1G | | `USB_VBUS` – `GND` |
| U1 | TPD2EUSB30 | | D+ `USB_DP_C`, D− `USB_DN_C`, GND |
| C2 | | 1 µF/25 V | `USB_VBUS` – `GND` |
| U2 | TPS259470L | eFuse | IN `USB_VBUS`, OUT `VBUS_PROT`, GND |
| R3/R4 | EN/UVLO-Teiler | 100 kΩ / 39 kΩ | `USB_VBUS` – EN – `GND` → UVLO ≈ 4,3 V |
| R5/R6 | OVLO-Teiler | 100 kΩ / 26,1 kΩ | `USB_VBUS` – OVLO – `GND` → OVLO ≈ 5,8 V |
| R7 | ILM | 3,32 kΩ 1 % | ILM – `GND` → ≈ 1 A |
| C3 | DVDT | 10 nF | DVDT – `GND` |
| C4 | ITIMER | DNP | ITIMER – `GND` (offen = schnellste Reaktion) |
| C5 | | 4,7 µF/10 V | `VBUS_PROT` – `GND` |
| D4 | SS16 | 60 V/1 A | A `VBUS_PROT`, K `VIN_SYS` |
| C6 | | 4,7 µF/50 V 1206 | `VIN_SYS` – `GND` (Buck-CIN) |
| C7 | | 100 nF/50 V | `VIN_SYS` – `GND` (am VIN-Pin) |
| U3 | LMR43620MSC3 | 3,3 V/2 A | VIN `VIN_SYS`, EN `VIN_SYS`, MODE/SYNC `GND` (Auto-PFM), PGOOD offen, VCC → C8, BOOT → C9 → SW, SW → L1, VOUT/FB `3V3_CORE`, GND |
| C8 | VCC | 1 µF/10 V | VCC – `GND` |
| C9 | BOOT | 100 nF | BOOT – SW |
| L1 | FAUL0420-2R2MT | 2,2 µH | SW – `3V3_CORE` |
| C10, C11 | COUT | 22 µF/10 V 1206 X7R | `3V3_CORE` – `GND` |

Testpunkte: TP1 `BATT_12V_IN`, TP2 `12V_PROT`, TP3 `VIN_SYS`, TP4 `3V3_CORE`, TP5 `USB_VBUS`, TP6 `VBUS_PROT`, TP7 `GND`.

## Seite 3 – ESP32 und RTC

| Ref | Teil | Wert | Verbindung |
|---|---|---|---|
| U4 | ESP32-S3-WROOM-1U-N16R8 | | 3V3 (2) `3V3_CORE`; GND (1, 40, 41) |
| C12, C13 | | 22 µF/10 V 1206 | `3V3_CORE` – `GND` am Pin 2 |
| C14 | | 100 nF | `3V3_CORE` – `GND` am Pin 2 |
| R8 | EN Pull-up | 10 kΩ | `3V3_CORE` – `EN` |
| C15 | EN | 1 µF | `EN` – `GND` |
| SW1 | RESET | KMR221GLFS | `EN` – `GND`, SH `GND` |
| U5 | TPS3808G33 | | VDD/SENSE `3V3_CORE`, ~RESET `EN`, CT offen (≈ 20 ms), ~MR offen (intern Pull-up), GND |
| C16 | | 100 nF | U5 VDD – `GND` |
| R9 | BOOT Pull-up | 10 kΩ | `3V3_CORE` – `BOOT_N` (IO0) |
| SW2 | BOOT | KMR221GLFS | `BOOT_N` – `GND`, SH `GND` |
| R10, R11 | USB-Serien-R | 22 Ω | IO19 – `USB_DN_C`, IO20 – `USB_DP_C` |
| C17, C18 | USB-Tuning | DNP | `USB_DN_C`/`USB_DP_C` – `GND` |
| R12 | U0TXD | 499 Ω | IO43 – TP `U0TXD` |
| U6 | RV-8263-C8 | | VDD `RTC_VDD`, VSS `GND`, CLKOE `GND`, CLKOUT offen, NC offen, SDA `I2C_SDA`, SCL `I2C_SCL`, ~INT `RTC_INT_N` |
| D5, D6 | BAS116 | | A `3V3_CORE` → K `RTC_VDD`; A `VBAT` → K `RTC_VDD` |
| C19 | | 100 nF | `RTC_VDD` – `GND` |
| BT1 | MY-1225-01-J + BR1225 | | + `VBAT`, − `GND` |
| R13, R14 | I2C Pull-up | 4,7 kΩ | `3V3_CORE` – `I2C_SDA` / `I2C_SCL` |
| R15 | INT Pull-up | 100 kΩ | `3V3_CORE` – `RTC_INT_N` |

ESP32-GPIO-Zuordnung (A12): IO1 `BUTTON_N`, IO2 `RTC_INT_N`, IO4 `1WIRE_DQ`, IO5 `SENSOR_EN`, IO6 `AUTOTERM_OE`, IO7 `BUTTON_LED_PWM`, IO8 `I2C_SDA`, IO9 `I2C_SCL`, IO10 `DIAG_RUN`, IO11 `STATUS_LED_1`, IO12 `STATUS_LED_2`, IO17 `AUTOTERM_TX_3V3`, IO18 `AUTOTERM_RX_3V3`, IO19/20 USB, IO43/44 UART0-Testpads; alle übrigen GPIOs No-Connect.

Testpunkte: TP8 `EN`, TP9 `BOOT_N`, TP10 `U0TXD`, TP11 `U0RXD`, TP12 `I2C_SDA`, TP13 `I2C_SCL`, TP14 `RTC_INT_N`, TP15 `GND`.

## Seite 4 – AUTOTERM und 1-Wire

| Ref | Teil | Wert | Verbindung |
|---|---|---|---|
| J2 | Nano-Fit 4-pol. | 1053131304 | 1 `AUTOTERM_5V`, 2 `GND`, 3 `CTRL_TX_TO_HEATER`, 4 `CTRL_RX_FROM_HEATER` |
| D7 | ESD5Z5.0T1G | | `AUTOTERM_5V` – `GND` |
| D8 | PESD5V2S2UT | | K1 `CTRL_TX_TO_HEATER`, K2 `CTRL_RX_FROM_HEATER`, A `GND` |
| R16 | | 100 Ω | `AUTOTERM_5V` – `AUTOTERM_5V_F` |
| C20 | | 1 µF/10 V | `AUTOTERM_5V_F` – `GND` |
| U7 | TXU0202 | | VCCA `3V3_CORE`, VCCB `AUTOTERM_5V_F`, OE `AUTOTERM_OE`, A1 `AUTOTERM_TX_3V3`, B1Y → R17, B2 ← R18, A2Y `AUTOTERM_RX_3V3`, GND |
| C21, C22 | | 100 nF | VCCA/VCCB – `GND` |
| R17 | TX-Serien-R | 100 Ω | B1Y – `CTRL_TX_TO_HEATER` |
| R18 | RX-Serien-R | 1 kΩ | `CTRL_RX_FROM_HEATER` – B2 |
| R19 | OE-Pulldown | 100 kΩ | `AUTOTERM_OE` – `GND` |
| J3 | Nano-Fit 3-pol. | 1053131303 | 1 `3V3_SENSOR_SW`, 2 `1WIRE_DQ_C`, 3 `GND` |
| U8 | TPS22945 | | VIN `3V3_CORE`, ON `SENSOR_EN`, VOUT `3V3_SENSOR_SW`, ~OC offen (TP), GND |
| C23, C24 | | 1 µF | VIN/VOUT – `GND` |
| R20 | ON-Pulldown | 100 kΩ | `SENSOR_EN` – `GND` |
| R21 | DQ-Pull-up | 4,7 kΩ | `3V3_SENSOR_SW` – `1WIRE_DQ_C` |
| R22 | DQ-Serie | 0 Ω | `1WIRE_DQ_C` – `1WIRE_DQ` |
| D9 | PESD3V3S2UT | | K1 `1WIRE_DQ_C`, K2 `3V3_SENSOR_SW`, A `GND` |

Testpunkte: TP16 `AUTOTERM_5V`, TP17 `CTRL_TX_TO_HEATER`, TP18 `CTRL_RX_FROM_HEATER`, TP19 `AUTOTERM_TX_3V3`, TP20 `AUTOTERM_RX_3V3`, TP21 `AUTOTERM_OE`, TP22 `1WIRE_DQ_C`, TP23 `3V3_SENSOR_SW`.

## Seite 5 – Taster, Ring-LED, Anzeige

| Ref | Teil | Wert | Verbindung |
|---|---|---|---|
| J4 | Nano-Fit 5-pol. | 1053131305 | 1 `BUTTON_N_C`, 2 `GND`, 3 `LED_CC_PLUS`, 4 `LED_PWM_MINUS`, 5 NC |
| D10 | PESD3V3S2UT | | K1 `BUTTON_N_C`, K2 an `GND` (unbenutzt), A `GND` |
| R23 | Taster-Serie | 1 kΩ | `BUTTON_N_C` – `BUTTON_N` |
| R24 | Taster-Pull-up | 10 kΩ | `3V3_CORE` – `BUTTON_N` |
| C25 | Taster-RC | 10 nF | `BUTTON_N` – `GND` |
| F1 | PTC 0805 | ≈ 50 mA Halte-, ≈ 150 mA Auslösestrom | `VIN_SYS` – `LED_CC_PLUS` (Kurzschlussschutz Kabel) |
| U9 | BCR421UW6Q | 10 mA | OUT (2, 3, 5) `LED_PWM_MINUS`, GND `GND`, REXT offen, EN ← R25 |
| R25 | EN-Serie | 100 Ω | `BUTTON_LED_PWM` – EN |
| R26 | EN-Pulldown | 100 kΩ | EN – `GND` |
| D11–D14 | LED rot 0603 | | Anzeige 12V, USB, 3V3, HEAT |
| R27 | 12V | 12 kΩ | `12V_PROT` – D11 → D15 (BAS116) → `DIAG_K` |
| R28 | USB | 3,3 kΩ | `VBUS_PROT` – D12 → D16 (BAS116) → `DIAG_K` |
| R29 | 3V3 | 1 kΩ | `3V3_CORE` – D13 → D17 (BAS116) → `DIAG_K` |
| R30 | HEAT | 3,3 kΩ | `AUTOTERM_5V_F` – D14 → D18 (BAS116) → `DIAG_K` |
| D19, R31, Q1 | RUN | 1,8 kΩ, 2N7002K | `3V3_CORE` – R31 – D19 – Q1 Drain; Q1 Source `DIAG_K`; Gate `DIAG_RUN` |
| R32 | RUN-Pulldown | 100 kΩ | `DIAG_RUN` – `GND` |
| SW3 | DIAG | KMR221GLFS | `DIAG_K` – `GND`, SH `GND`; parallel TP24 `DIAG_K` und TP25 `GND` |
| D20, D21 | Status rot 0603 | | `STATUS_LED_1`/`_2` – R33/R34 1 kΩ – LED – `GND` |
| R35, R36 | Pulldown | 100 kΩ | `STATUS_LED_1`/`_2` – `GND` |

LED-Strom (Vf ≈ 1,8 V, BAS116 ≈ 0,6 V): 12V 0,63–0,97 mA bei 10–14 V; USB 0,71–0,86 mA bei 4,75–5,25 V; 3V3 ≈ 0,85 mA; HEAT ≈ 0,8 mA; RUN ≈ 0,8 mA. Ohne gedrückten DIAG-Taster ist `DIAG_K` offen: kein Ruhestrom.

Testpunkte: TP24 `DIAG_K`, TP25 `GND`, TP26 `BUTTON_N`, TP27 `BUTTON_LED_PWM`, TP28 `DIAG_RUN`.

## Abweichungen von Teil B (begründet)

| # | Teil B | Umsetzung | Begründung |
|---|---|---|---|
| S-01 | eFuse-Ausgang direkt an VIN_SYS | zusätzliche Schottky-Diode D4 zwischen eFuse-Ausgang und VIN_SYS; mit D2 im 12-V-Zweig bildet sie ein Dioden-ODER | Löst P1-01: Der eFuse-Ausgang sieht 12-V-Transienten nicht mehr, die Grenze IN ≥ OUT − 21 V wird eingehalten. Rückspeisung in USB ist doppelt gesperrt. |
| S-02 | Diagnose mit gemeinsamem 2N7002 und Gate-Teiler | DIAG-Taster schaltet die gemeinsame Kathodenleitung direkt nach GND | Weniger Bauteile, kein Ruhestrom, keine Gate-Spannungsgrenze; Taster (50 mA) trägt die 5 mA der Anzeige. Sperrdioden verhindern Rückspeisung zwischen den Quellen. |
| S-03 | Ring-LED-Plus ohne Schutz | PTC F1 vor `LED_CC_PLUS` | Ein Kurzschluss im 3-m-Kabel würde sonst VIN_SYS kurzschließen. |
| S-04 | – | Ring-LED an USB: VIN_SYS ≈ 4,3 V; nach LED (≈ 3 V) bleiben ≈ 1,3 V für den BCR421 (Minimum 1,4 V) | Ring-LED leuchtet an USB etwas dunkler; an 12 V volle 10 mA. Wird in Abnahmetest 12 gemessen. |
