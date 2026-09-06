# ESP32-S3 GPIO-Matrix – Revision A

Stand: 2026-09-06

Modul: `ESP32-S3-WROOM-1U-N16R8`

Status: in Phase 2 umgesetzt; GPIO18 ergänzt die DNP-Wake-Latch-Option

## 1. Ergebnis

Alle Pflichtfunktionen und die beiden optionalen Status-LEDs passen ohne Portexpander auf das Modul. GPIO48 bleibt als freie Reserve. GPIO47 wird für die sicherheitsrelevante Freigabe des AUTOTERM-Pegelwandlers verwendet; dies ist wichtiger als die unverbindliche Freihaltepräferenz für GPIO47/48.

GPIO35, GPIO36 und GPIO37 sind beim N16R8 intern durch das Octal-PSRAM belegt. Die Modulanschlüsse GPIO22 bis GPIO34 sind beim WROOM-1U nicht herausgeführt. Sie dürfen weder im Schaltplan noch in der Firmwarebelegung als verfügbar gelten.

## 2. Verbindliche Pin-Matrix

`Pull` bezeichnet die externe Hardwarebeschaltung. Werte sind Startwerte für Phase 2 und werden nur bei nachvollziehbarer elektrischer Berechnung geändert. `Z` bedeutet hochohmig.

| Modulpad | GPIO | Signal/Funktion | Richtung im Betrieb | Externer Pull / Schutz | Einschaltverhalten | Deep-Sleep / sicherer Zustand | Wake |
|---:|---:|---|---|---|---|---|---|
| 27 | 0 | `BOOT_N` | Eingang | 10 kΩ nach 3V3, Taster nach GND; kein großer C | Strapping; HIGH für Normalboot | HIGH | nein |
| 39 | 1 | `BUTTON_N` | Eingang | 10 kΩ nach 3V3; Serien-R und RC/ESD am J4 | etwa 60 µs LOW möglich; externer Pull stellt HIGH wieder her | Eingang HIGH, Taster zieht LOW | EXT1 ANY_LOW |
| 38 | 2 | `TOUCH_INT_N` | Eingang | Serien-R; 10-kΩ-Pull-up als Startwert, alternative Pull- und Latch-Bestückung | etwa 60 µs LOW möglich | FT6336U beziehungsweise `Q_N` des optionalen Latch, jeweils active LOW | EXT1 ANY_LOW |
| 15 | 3 | unbenutzt | Eingang | kein externer Pull; Firmware definiert nach Boot | Strapping `JTAG_SEL_ENABLE` | unbenutzt | nein |
| 4 | 4 | `1WIRE_DQ` | bidirektional Open-Drain | 4,7 kΩ nach `3V3_SENSOR_SW`, Serien-R/ESD | etwa 60 µs LOW möglich; Sensorrail AUS | Z, Sensorrail AUS | nein |
| 5 | 5 | `I2C_SDA` | bidirektional Open-Drain | 4,7 kΩ Startwert nach `3V0_TOUCH_AON` | etwa 60 µs LOW möglich | HIGH über AON-Pull-up | nein |
| 6 | 6 | `I2C_SCL` | bidirektional Open-Drain | 4,7 kΩ Startwert nach `3V0_TOUCH_AON` | etwa 60 µs LOW möglich | HIGH über AON-Pull-up | nein |
| 7 | 7 | `TOUCH_RESET_RELEASE` | Ausgang | 100 kΩ Pulldown; Open-Drain-Puffer zur 3,0-V-Seite | LOW; etwaiger LOW-Impuls ist sicher | im Komfort-Standby per Pad-Hold HIGH, sonst LOW | nein |
| 12 | 8 | `EPD_BUSY` | Eingang | AXC-Pegel-/Power-off-Isolation; 100 kΩ Pulldown coreseitig | etwa 60 µs LOW möglich | LOW, Displayrail AUS | nein |
| 17 | 9 | `EPD_SCLK` | Ausgang | AXC-Isolation; 100 kΩ Pulldown coreseitig; Serien-R | LOW-Puls möglich, erreicht Display wegen `/OE` HIGH nicht | LOW/Z, Displayrail AUS | nein |
| 18 | 10 | `EPD_SDIO_MOSI` | Ausgang | AXC-Isolation; 100 kΩ Pulldown; Serien-R | LOW-Puls möglich, isoliert | LOW/Z, Displayrail AUS | nein |
| 19 | 11 | `EPD_CS_N` | Ausgang | AXC-Isolation; 100 kΩ Pull-up core- und displayseitig | LOW-Puls möglich, isoliert; displayseitig HIGH | HIGH/Z, Displayrail AUS | nein |
| 20 | 12 | `EPD_DC` | Ausgang | AXC-Isolation; 100 kΩ Pulldown; Serien-R | LOW-Puls möglich, isoliert | LOW/Z, Displayrail AUS | nein |
| 21 | 13 | `EPD_RESET_N` | Ausgang | AXC-Isolation; 100 kΩ Pulldown core- und displayseitig | LOW, Display bleibt in Reset | LOW/Z, Displayrail AUS | nein |
| 22 | 14 | `DISPLAY_EN` | Ausgang | 100 kΩ Pulldown | etwa 60 µs LOW; sicher | LOW, Display AUS | nein |
| 8 | 15 | `SENSOR_EN` | Ausgang | 100 kΩ Pulldown | etwa 60 µs LOW; sicher | LOW, Sensoren AUS | nein |
| 9 | 16 | `AUTOTERM_TX_3V3` | Ausgang | Serien-R; TXU-Ausgang durch OE isoliert | etwa 60 µs LOW, aber TXU deaktiviert | Z zur Heizung | nein |
| 10 | 17 | `AUTOTERM_RX_3V3` | Eingang | Serien-R; TXU VCC-Isolation | etwa 60 µs LOW möglich | Eingang/Z | nein |
| 11 | 18 | `LATCH_CLR_GPIO_N` optional | Ausgang | 100-Ω-DNP-Serienwiderstand zum optionalen Wake-Latch; kein Außenanschluss | dokumentierter LOW- und HIGH-Impuls möglich; nur Latch-Reset und deshalb sicher | Standard unbenutzt; mit Latch kurzer LOW-Löschpuls nach INT-Freigabe | nein |
| 13 | 19 | `USB_D_N` | USB-D− | 22/33 Ω Serien-R nahe Modul, ESD am Stecker | USB-JTAG/ROM-Aktivität möglich | gemäß USB-Peripherie | nein |
| 14 | 20 | `USB_D_P` | USB-D+ | 22/33 Ω Serien-R nahe Modul, ESD am Stecker | USB-JTAG/ROM-Aktivität möglich | gemäß USB-Peripherie | nein |
| 23 | 21 | `FRONTLIGHT_PWM` | Ausgang/PWM | 100 kΩ Pulldown am Treiber; Serien-R | LOW durch Hardware | LOW, Frontlicht AUS | nein |
| 28 | 35 | nicht verfügbar | – | intern Octal-PSRAM | – | – | – |
| 29 | 36 | nicht verfügbar | – | intern Octal-PSRAM | – | – | – |
| 30 | 37 | nicht verfügbar | – | intern Octal-PSRAM | – | – | – |
| 31 | 38 | `BUTTON_LED_PWM` | Ausgang/PWM | 100 kΩ Gate-Pulldown; Serien-R | LOW | LOW, Ring-LED AUS | nein |
| 32 | 39 | `DIAG_RUN` | Ausgang | 100 kΩ Pulldown; isolierter Diagnosezweig | LOW | LOW, RUN AUS | nein |
| 33 | 40 | `USB_HIGH_CURRENT_N` | Eingang | TUSB321AI `OUT1`; mindestens 200 kΩ nach 3V3, Serien-R | HIGH wenn USB fehlt/default; Vollbetrieb gesperrt | HIGH/irrelevant | nein |
| 34 | 41 | `STATUS_LED_1` optional | Ausgang | LED-Vorwiderstand; Pulldown falls Treiberstufe | LOW | LOW, AUS | nein |
| 35 | 42 | `STATUS_LED_2` optional | Ausgang | LED-Vorwiderstand; Pulldown falls Treiberstufe | LOW | LOW, AUS | nein |
| 37 | 43 | `U0TXD_TEST` | Ausgang/Testpad | 499 Ω nahe Modul | ROM-/Boot-Ausgaben möglich | nur Testpad | nein |
| 36 | 44 | `U0RXD_TEST` | Eingang/Testpad | Testpad, optionaler Serien-R | Eingang | nur Testpad | nein |
| 26 | 45 | unbenutzt | Eingang | kein Pull-up; Strapping nicht verändern | Strapping | unbenutzt | nein |
| 16 | 46 | unbenutzt | Eingang | kein Pull-up; muss USB-/UART-Download erlauben | Strapping, ROM-Logik | unbenutzt | nein |
| 24 | 47 | `AUTOTERM_OE` | Ausgang | 100 kΩ Pulldown direkt am TXU OE | LOW, Pegelwandler AUS | LOW, TX zur Heizung Z | nein |
| 25 | 48 | Reserve, unbenutzt | Eingang | kein fester Außenanschluss; Firmware definiert | undefiniert | unbenutzt | nein |

Modulpads 1, 40 und 41/EPAD sind GND; Pad 2 ist 3V3 und Pad 3 `CHIP_PU/EN`. Diese Versorgungspins sind keine GPIOs.

## 3. Reset-, Boot- und Wake-Konzept

### 3.1 `CHIP_PU/EN`

- 10 kΩ nach `3V3_CORE`, 1 µF nach GND als Espressif-Ausgangspunkt.
- `TPS3808G33QDBVRQ1` zieht EN per Open Drain LOW, solange `3V3_CORE` nicht sicher über der Supervisor-Schwelle liegt.
- Der lokale RESET-Taster liegt parallel zum Open-Drain-Ausgang nach GND.
- Die endgültige CT-Kapazität muss nach dem realen Hochlauf des Buckreglers eine EN-Verzögerung mit ausreichender Reserve gegenüber den mindestens 50 µs liefern; Zielwert 20 ms nominal.

### 3.2 Download-Boot

GPIO0 bleibt durch 10 kΩ normalerweise HIGH. Für manuellen Download-Boot wird BOOT gehalten und RESET betätigt. GPIO46 erhält keinen Pull-up und keinen Außenanschluss. Ein automatischer DTR/RTS-Programmierpfad ist nicht vorgesehen, weil natives USB und die beiden lokalen Taster ausreichen.

### 3.3 Deep-Sleep-Wakeup

GPIO1 und GPIO2 gehören zum RTC-fähigen Bereich GPIO0 bis GPIO21. In der Standardbestückung werden beide gemeinsam über EXT1 mit `ANY_LOW` aktiviert:

- GPIO1 wird vom externen Schließertaster nach GND gezogen.
- GPIO2 wird vom FT6336U im Komfort-Standby active LOW angesteuert.

Im Minimal-Standby ist der Touch im Hibernation-Modus und nur GPIO1 gilt als zuverlässige Wake-Quelle. Nach jedem Wake liest die Firmware den EXT1-Status, bevor sie die Peripherie neu konfiguriert.

Falls die DNP-Latch-Option nach Prototypmessung aktiviert wird, setzt Touch-INT das Latch asynchron und dessen invertierter Ausgang `Q_N` hält GPIO2 LOW. GPIO18 löscht das Latch erst, nachdem die Firmware den Touch-Status gelesen hat und FT6336U-INT wieder HIGH ist. Taster und Touch behalten damit dieselbe EXT1-`ANY_LOW`-Polarität.

## 4. Buszuordnung

| Bus | Signale | GPIOs | Bemerkung |
|---|---|---|---|
| natives USB 2.0 FS | D− / D+ | 19 / 20 | keine UART-Bridge |
| I2C | SDA / SCL | 5 / 6 | RV-3028 + FT6336U, Pull-ups an 3,0 V |
| E-Paper SPI, write-only | SCLK / MOSI / CS / DC / RESET / BUSY | 9 / 10 / 11 / 12 / 13 / 8 | Power-off-isoliert; kein MISO |
| AUTOTERM UART | TX / RX / OE | 16 / 17 / 47 | Hardware-UART ungleich UART0 |
| 1-Wire | DQ | 4 | drei externe DS18B20 parallel |

ESP32-Peripheriesignale werden über die GPIO-Matrix zugeordnet; die Software darf diese GPIO-Nummern nicht ohne korrespondierende Hardware-Dokumentrevision ändern.

## 5. GPIO-Bilanz

| Kategorie | Anzahl |
|---|---:|
| Pflichtsignale einschließlich USB, BOOT und UART0-Testpads | 26 |
| optionale Status-LEDs und optionaler Latch-Clear | 3 |
| intern durch PSRAM belegt | 3 |
| bewusst unbenutzte Strapping-/Glitch-Pins | 3 |
| freie Reserve | 1 (`GPIO48`) |

Die optionalen Status-LEDs können somit in Revision A bestückt werden. Sie bleiben dennoch optional, falls der mechanische Platzierungsreview ihre Entfernung erfordert.

## 6. Verifikation in Phase 2 und am Prototyp

1. Modulpadnummern und N16R8-Speicherbelegung direkt gegen die dann aktuelle Espressif-Datenblattrevision prüfen.
2. Alle Startwerte der externen Pulls gegen Eingangsstrom, Anstiegszeit und Ruhestrom berechnen.
3. `BUTTON_N`-RC-Filter mit dem realen 3-m-Kabel auf zuverlässiges Wake und Störfestigkeit prüfen.
4. FT6336U-INT-Pegel, Ausgangstopologie und LOW-Dauer messen; Latch-Option danach bestücken oder als DNP dokumentieren.
5. Pad-Hold von GPIO7 im Komfort-Standby einschließlich Reset-/Wake-Sequenz verifizieren.
6. Sämtliche Enable-, PWM-, OE- und TX-Signale während Power-on, Reset, Bootloader und Deep-Sleep mit dem Oszilloskop prüfen.
7. Falls GPIO41/42 beim Booten eine sichtbare LED-Aktivität verursachen, die optionalen LEDs über Pulldown-/Treiberstufe sicher entkoppeln oder beide DNP setzen.

## 7. Referenzen

- [Espressif ESP32-S3-WROOM-1/1U Datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [Espressif ESP32-S3 GPIO & RTC GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html)
- [Espressif ESP32-S3 Sleep Modes](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html)
- [Espressif ESP32-S3 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html)
