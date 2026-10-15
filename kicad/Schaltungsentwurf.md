# Schaltungsentwurf – Phase 2

Stand: 2026-10-12 · Grundlage: [Anforderungsdokument](../docs/Anforderungsdokument_Neuentwicklung.md) Teil A, [Bauteilliste](Bauteilliste.md)

Sollvorgabe für den Schaltplan und die Netzlistenprüfung nach N-05. Referenzen entsprechen dem gezeichneten Schaltplan. Abweichungen von Teil B sind am Ende begründet.

## Seitenaufteilung

| Seite | Datei | Inhalt |
|---|---|---|
| 1 | `LandyHeater.kicad_sch` | Übersicht, Seitensymbole |
| 2 | `01_Versorgung.kicad_sch` | J1 12 V mit Verpol-/Transientenschutz, USB-C mit eFuse, Dioden-ODER auf VIN_SYS, 3,3-V-Buck |
| 3 | `02_ESP32_RTC.kicad_sch` | ESP32-S3, Reset/BOOT, USB-Daten, UART0-Testpads, RTC mit Knopfzelle |
| 4 | `03_AUTOTERM_1Wire.kicad_sch` | J2 AUTOTERM-UART mit Pegelwandler, J3 1-Wire mit Sensor-Lastschalter |
| 5 | `04_Taster_Anzeige.kicad_sch` | J4 Taster und Ring-LED, Energiefluss-Diagnose, Status-LEDs |

Seitenübergreifend: Versorgungen als Power-Symbole (`GND`, `3V3_CORE`, `VIN_SYS`), Signale als globale Labels (`12V_PROT`, `VBUS_PROT`, `AUTOTERM_5V`, `USB_DN_C`, `USB_DP_C` und die GPIO-Signale aus A12). Seiteninterne Netze mit Netzklasse tragen lokale Labels (z. B. `USB_VBUS`, `SW_BUCK`, `CTRL_TX`).

## Seite 2 – Versorgung

| Ref | Teil / Wert | Verbindung |
|---|---|---|
| J1 | Nano-Fit 2-pol. | 1 `BATT_12V_IN`, 2 `GND` |
| D1 | SMBJ18CA | `BATT_12V_IN` – `GND` |
| D2 | SS16 | A `BATT_12V_IN`, K `12V_PROT` (Verpolschutz, ODER-Zweig 12 V) |
| C26 | 100 nF / 50 V X7R 0603 | `12V_PROT` – `GND` vor FB1 (Pi-Filter, begrenzt schnelle Pulse an D2; E-01, Phase 3) |
| FB1 | Ferrit 600 Ω | `12V_PROT` – `VIN_SYS` |
| C1 | 47 µF / 35 V Elko | `VIN_SYS` – `GND` (dämpft Ferrit/MLCC-Resonanz) |
| J5 | USB4105 | VBUS `USB_VBUS`, CC1/CC2, D+/D− `USB_DP_C`/`USB_DN_C`, SBU offen, GND/Schirm `GND` |
| R1, R2 | 5,1 kΩ | CC1/CC2 – `GND` (Rd) |
| D3 | ESD5Z5.0 | `USB_VBUS` – `GND` |
| U1 | TPD2EUSB30 | D+/D− – `GND` |
| C2 | 1 µF | `USB_VBUS` – `GND` |
| U2 | TPS259470L | IN `USB_VBUS`, OUT `VBUS_PROT` |
| R3/R4/R5 | 100 kΩ / 10 kΩ / 28,7 kΩ | Teiler `USB_VBUS` – EN/UVLO – OVLO – `GND`: UVLO 4,30 V, OVLO 5,80 V (Schwellen 1,20 V) |
| R6 | 3,32 kΩ | ILM → ≈ 1,0 A |
| C3 | 10 nF | DVDT |
| C4 | 1 nF, DNP | ITIMER (offen = schnellste Reaktion) |
| C5 | 4,7 µF | `VBUS_PROT` – `GND` |
| D4 | SS16 | A `VBUS_PROT`, K `VIN_SYS` (ODER-Zweig USB) |
| C6, C7 | 4,7 µF/50 V, 100 nF | `VIN_SYS` – `GND` |
| U3 | LMR43620MSC3 | VIN und EN `VIN_SYS`, MODE `GND` (Auto-PFM), PGOOD offen, SW `SW_BUCK`, VOUT `3V3_CORE` |
| C8 | 1 µF | VCC – `GND` |
| C9 | 100 nF | BOOT – `SW_BUCK` |
| L1 | 2,2 µH FAUL0420 | `SW_BUCK` – `3V3_CORE` |
| C10, C11 | 22 µF / 10 V | `3V3_CORE` – `GND` |

Testpunkte: TP1 `BATT_12V_IN`, TP2 `12V_PROT`, TP3 `VIN_SYS`, TP4 `3V3_CORE`, TP5 `USB_VBUS`, TP6 `VBUS_PROT`, TP7 `GND`.

## Seite 3 – ESP32 und RTC

| Ref | Teil / Wert | Verbindung |
|---|---|---|
| U4 | ESP32-S3-WROOM-1U-N16R8 | 3V3 `3V3_CORE`, GND |
| C12, C13, C14 | 22 µF, 22 µF, 100 nF | am 3V3-Pin |
| U5 | TPS3808G33 | VDD/SENSE `3V3_CORE`, ~RESET `EN`, CT offen (≈ 20 ms), ~MR offen |
| C16 | 100 nF | U5 VDD |
| R7, C15 | 10 kΩ, 1 µF | `EN` Pull-up / nach `GND` |
| SW1 | RESET | `EN` – `GND` |
| R8, SW2 | 10 kΩ, BOOT | `BOOT_N` (IO0) Pull-up / Taster nach `GND` |
| R9, R10 | 22 Ω | IO19 – `USB_DN_C`, IO20 – `USB_DP_C` |
| C17, C18 | 10 pF, DNP | USB-Tuning nach `GND` |
| R11 | 499 Ω | IO43 – TP10 (U0TXD) |
| U6 | RV-8263-C8 | VDD `RTC_VDD`, SDA/SCL `I2C_SDA`/`I2C_SCL`, ~INT `RTC_INT_N`, CLKOE `GND`, CLKOUT/NC offen |
| D5, D6 | BAS116 | `3V3_CORE` → `RTC_VDD`; `VBAT` → `RTC_VDD` |
| C19 | 100 nF | `RTC_VDD` |
| BT1 | MY-1225-01-J + BR1225 | + `VBAT`, − `GND` |
| R12, R13 | 4,7 kΩ | I2C-Pull-ups nach `3V3_CORE` |
| R14 | 100 kΩ | `RTC_INT_N` Pull-up |

GPIO-Zuordnung wie A12. Unbenutzte GPIOs mit No-Connect-Markierung.

Testpunkte: TP8 `EN`, TP9 `BOOT_N`, TP10 U0TXD, TP11 U0RXD, TP12 `I2C_SDA`, TP13 `I2C_SCL`, TP14 `RTC_INT_N`, TP15 `GND`.

## Seite 4 – AUTOTERM und 1-Wire

| Ref | Teil / Wert | Verbindung |
|---|---|---|
| J2 | Nano-Fit 4-pol. | 1 `AUTOTERM_5V`, 2 `GND`, 3 `CTRL_TX`, 4 `CTRL_RX` |
| D7 | ESD5Z5.0 | `AUTOTERM_5V` – `GND` |
| R15 | 100 Ω | `AUTOTERM_5V` – `AUTOTERM_5V_F` |
| C20, C22 | 1 µF, 100 nF | `AUTOTERM_5V_F` – `GND` |
| U7 | TXU0202 | VCCA `3V3_CORE` (C21), VCCB `AUTOTERM_5V_F`, OE `AUTOTERM_OE`, A1 `AUTOTERM_TX_3V3`, A2Y `AUTOTERM_RX_3V3` |
| R16 | 100 Ω | B1Y – `CTRL_TX` |
| R17 | 1 kΩ | `CTRL_RX` – B2 |
| R18 | 100 kΩ | `AUTOTERM_OE` – `GND` |
| D8 | PESD5V2S2UT | K1 `CTRL_TX`, K2 `CTRL_RX`, A `GND` |
| J3 | Nano-Fit 3-pol. | 1 `3V3_SENSOR_SW`, 2 `1WIRE_DQ_C`, 3 `GND` |
| U8 | TPS22945 | VIN `3V3_CORE` (C23), ON `SENSOR_EN`, VOUT `3V3_SENSOR_SW` (C24), ~OC offen |
| R19 | 100 kΩ | `SENSOR_EN` – `GND` |
| R20 | 4,7 kΩ | `3V3_SENSOR_SW` – `1WIRE_DQ_C` |
| R21 | 0 Ω | `1WIRE_DQ` – `1WIRE_DQ_C` |
| D9 | PESD3V3S2UT | K1 `1WIRE_DQ_C`, K2 `3V3_SENSOR_SW`, A `GND` |

Testpunkte: TP16 `AUTOTERM_5V`, TP17 `CTRL_TX`, TP18 `CTRL_RX`, TP19 `AUTOTERM_TX_3V3`, TP20 `AUTOTERM_RX_3V3`, TP21 `AUTOTERM_OE`, TP22 `1WIRE_DQ_C`, TP23 `3V3_SENSOR_SW`.

## Seite 5 – Taster, Ring-LED, Anzeige

| Ref | Teil / Wert | Verbindung |
|---|---|---|
| J4 | Nano-Fit 5-pol. | 1 `BUTTON_N_C`, 2 `GND`, 3 `LED_CC_PLUS`, 4 `LED_PWM_MINUS`, 5 NC |
| D10 | PESD3V3S2UT | K1 `BUTTON_N_C`, K2 offen, A `GND` |
| R22 | 1 kΩ | `BUTTON_N_C` – `BUTTON_N` |
| R23, C25 | 10 kΩ, 10 nF | `BUTTON_N` Pull-up / nach `GND` (≈ 10 µs) |
| F1 | PTC 0805, I_hold 50 mA / I_trip 150 mA, 60 V – BORN SMD0805-005/60N, LCSC C22366098 (Freigabe 15.10.2026); Symbol `LandyHeater:Polyfuse_0805` | `VIN_SYS` – `LED_CC_PLUS` |
| U9 | BCR421UW6Q | OUT (2, 3, 5) `LED_PWM_MINUS`, GND, REXT offen (10 mA), EN über R24 |
| R24, R25 | 100 Ω, 100 kΩ | `BUTTON_LED_PWM` – EN / EN – `GND` |
| R26 + D11 + D15 | 12 kΩ, LED, BAS116 | `12V_PROT` → `DIAG_K` |
| R27 + D12 + D16 | 3,3 kΩ, LED, BAS116 | `VBUS_PROT` → `DIAG_K` |
| R28 + D13 + D17 | 1 kΩ, LED, BAS116 | `3V3_CORE` → `DIAG_K` |
| R29 + D14 + D18 | 3,3 kΩ, LED, BAS116 | `AUTOTERM_5V` → `DIAG_K` |
| R30 + D19 + Q1 | 1,8 kΩ, LED, 2N7002K | `3V3_CORE` → Q1 Drain; Source `DIAG_K`; Gate `DIAG_RUN` |
| R31 | 100 kΩ | `DIAG_RUN` – `GND` |
| SW3 | DIAG | `DIAG_K` – `GND` |
| R32/D20, R33/D21 | 1 kΩ, LED | `STATUS_LED_1/2` → `GND` |
| R34, R35 | 100 kΩ | `STATUS_LED_1/2` – `GND` |

LED-Ströme (Vf ≈ 1,8 V, BAS116 ≈ 0,6 V): 12V 0,63–0,97 mA bei 10–14 V; USB 0,71–0,86 mA; 3V3 ≈ 0,85 mA; HEAT ≈ 0,8 mA; RUN ≈ 0,8 mA; Status ≈ 1,5 mA. Ohne gedrückten DIAG-Taster ist `DIAG_K` offen, kein Ruhestrom.

Testpunkte: TP24 `DIAG_K`, TP25 `GND`, TP26 `BUTTON_N`, TP27 `BUTTON_LED_PWM`, TP28 `DIAG_RUN`.

## Abweichungen von Teil B (begründet)

| # | Teil B | Umsetzung | Begründung |
|---|---|---|---|
| S-01 | eFuse-Ausgang direkt an VIN_SYS | Schottky D4 zwischen eFuse-Ausgang und VIN_SYS; mit D2 Dioden-ODER | Löst P1-01: Der eFuse-Ausgang sieht 12-V-Transienten nicht (Grenze IN ≥ OUT − 21 V). Rückspeisung in USB ist doppelt gesperrt. |
| S-02 | Diagnose mit gemeinsamem 2N7002 und Gate-Teiler | DIAG-Taster schaltet die gemeinsame Kathodenleitung direkt nach GND | Weniger Bauteile, kein Ruhestrom, keine Gate-Spannungsgrenze. Sperrdioden verhindern Rückspeisung zwischen den Quellen. |
| S-03 | Ring-LED-Plus ohne Schutz | PTC F1 vor `LED_CC_PLUS` | Kurzschluss im 3-m-Kabel würde sonst VIN_SYS kurzschließen. |
| S-04 | – | An USB bleiben nach LED (≈ 3 V) ≈ 1,3 V für den BCR421 (Minimum 1,4 V) | Ring-LED an USB etwas dunkler, an 12 V volle 10 mA. Messung in Abnahmetest 12. |
| S-05 | EN- und OVLO-Teiler getrennt | Ein dreistufiger Teiler R3/R4/R5 | Gleiche Schwellen, ein Widerstand weniger, geringerer Querstrom. |
| S-06 | HEAT-Anzeige aus `AUTOTERM_5V_F` | aus `AUTOTERM_5V` am Stecker | Funktional gleich (Anwesenheit der Heizungsspannung), übersichtlichere Verdrahtung. |
| S-07 | – | C26 100 nF an `12V_PROT` (Phase 3, E-01) | SPICE V-01: Puls 3a (−220 V, 0,1 µs) treibt D2 sonst kurz an die 60-V-Grenze; mit C26 38,8 V. Zusätzlich Pi-Filter C26–FB1–C1 gegen Buck-Störungen auf der 12-V-Leitung. |
