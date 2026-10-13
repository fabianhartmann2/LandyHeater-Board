# LandyHeater-Board – Anforderungsdokument für die Neuentwicklung

Dokumentversion: 2.1
Stand: 2026-10-13
Status: Grundlage für einen vollständigen Neuaufbau (Schaltplan, Layout, Fertigung) von Grund auf

Änderungen:

- 1.1 – E-Paper-Display einschließlich integriertem Touch und Frontlicht entfallen.
- 2.0 – Aufteilung in **Teil A (verbindlich)** und **Teil B (informativ)**. Leiterplatte maximal 80 × 50 mm, einseitige Bestückung bevorzugt, Status-LEDs bestückt, RTC als Wake-Quelle, GPIO-Belegung neu festgelegt, USB-Stromerkennung entfallen, Fertigung bei JLCPCB statt PCBWay.
- 2.1 – GPIO-Belegung nach Modulseite zum jeweiligen Funktionsblock neu verteilt (kurze Wege, A12); Layout-Checkliste aus Hersteller-Leitfäden ergänzt (B7).

## Aufbau und Verbindlichkeit

- **Teil A – Lastenheft (verbindlich):** was das Board können muss, welche Schnittstellen und Grenzwerte gelten, wie es geprüft wird. Teil A legt nur dort konkrete Bauteile fest, wo sie von außen vorgegeben sind (ESP32-Modul, Steckverbinder/Kabelbaum, externer Taster).
- **Teil B – Referenzlösung (informativ):** empfohlene Schaltungsarchitektur, Bauteile und Startwerte. Teil B ist ein Startpunkt, keine Vorgabe. Abweichungen sind zulässig, wenn Teil A erfüllt bleibt; sie werden in der Abweichungsliste kurz begründet.

Begriffe: **MUSS / DARF NICHT** = verbindlich; **SOLL** = verbindliches Ziel, Abweichung begründen; **KANN** = optional.

Rangfolge bei Widersprüchen: (1) freigegebene Änderung dieses Dokuments, (2) Teil A, (3) Herstellerdatenblatt/Referenzschaltung/Landpattern, (4) Espressif ESP32-S3 Hardware Design Guidelines, (5) JLCPCB-Fertigungsregeln und Stackup, (6) Teil B. Konflikte werden vor dem Schaltplan- bzw. Layout-Freeze gemeldet, nicht eigenmächtig gelöst.

---

# Teil A – Lastenheft (verbindlich)

## A0. Regeln für die Neuentwicklung

| ID | Regel |
|---|---|
| N-01 | Aus dem bisherigen Repository werden **keine** KiCad-Dateien (`*.kicad_sch`, `*.kicad_pcb`, `*.kicad_pro`, Bibliotheken) und **keine** Generator-, Routing- oder Audit-Skripte übernommen. |
| N-02 | Der Schaltplan wird als normal editierbarer KiCad-Schaltplan aufgebaut, nicht durch ein Skript erzeugt, das spätere manuelle Änderungen überschreibt. |
| N-03 | Symbole und Footprints stammen aus offiziellen Herstellerunterlagen oder geprüften Bibliotheken und werden je Bauteil abgeglichen: Symbol-Pinout ↔ Footprint-Padnummer ↔ Herstellerzeichnung. |
| N-04 | Lokale Verbindungen innerhalb eines Funktionsblocks als sichtbare Leitungen; Labels nur für Seitenübergänge, Versorgungsnetze und Einzelanschlüsse. Signalfluss links → rechts, Versorgung oben, GND unten. |
| N-05 | Nach dem Schaltplan wird die exportierte Netzliste Pin für Pin gegen dieses Dokument geprüft (ERC allein genügt nicht). |
| N-07 | Die SPICE-Modellprüfung des ERC ist aktiv. Jedes Symbol erhält ein SPICE-Modell (Passive über KiCad-Standardmodelle, ICs über Herstellermodelle, sofern verfügbar). Bauteile ohne sinnvolles Modell (Steckverbinder, Testpunkte, Module) werden mit `Sim.Enable` = 0 und kurzer Begründung ausgenommen. |
| N-06 | Jede Phase (Abschnitt A18) wird einzeln abgeschlossen und ausdrücklich freigegeben, bevor die nächste beginnt. |

## A1. Funktion und Abgrenzung

Kompaktes Kommunikations- und Steuergerät für eine AUTOTERM/Planar-Dieselstandheizung in einem Land Rover. Bedienung über einen externen beleuchteten Taster und WLAN.

| ID | Funktion |
|---|---|
| F-01 | 5-V-Full-Duplex-UART zur originalen Heizungssteuerung |
| F-02 | Drei extern parallel geschaltete DS18B20 an einem gemeinsamen 3-Draht-1-Wire-Bus |
| F-03 | Externer Taster mit dimmbarer weißer Ring-LED |
| F-04 | Batteriegepufferte Echtzeituhr, die den ESP32 aus dem Deep-Sleep wecken kann |
| F-05 | WLAN über `ESP32-S3-WROOM-1U-N16R8` mit externer Antenne |
| F-06 | Natives USB-C für Flashen, Konsole, Diagnose und Service-Versorgung |
| F-07 | Energiefluss-Diagnoseanzeige (nur bei gedrücktem DIAG-Taster aktiv) und zwei Status-LEDs |
| F-08 | Versorgung aus abgesichertem 12-V-Zweitbatteriekreis oder USB-C |

Das Board schaltet **keine** Glühkerze, Pumpe, Gebläse oder andere Heizungsleistung; alle sicherheitsrelevanten Funktionen bleiben in der AUTOTERM-Steuerung.

**Nicht enthalten:** Display, Touch, Frontlicht, FPC-Stecker, Entwicklungsboard, VOTRONIC-VBCS/Smart-Shunt, RS-485, CAN, ACC/KL15-Eingang, Sicherung auf dem PCB, 12-V-Last-/Relais-/High-Side-Ausgänge, PCB-Antenne oder geroutete HF-Leitung, USB-PD, USB-UART-Wandler, I2C-Portexpander. Für spätere Erweiterungen werden keine Schaltungsteile, Stecker oder GPIOs reserviert.

## A2. Umgebung und Mechanik

| ID | Anforderung |
|---|---|
| M-01 | Einbau in der Cubby Box der Mittelkonsole; geschützt vor Spritzwasser und Kondensation. Keine IP-Zertifizierung, keine Schutzlackierung. |
| M-02 | Aktive Halbleiter und kritische Bauteile SOLLEN für −40 … +85 °C spezifiziert sein. |
| M-03 | Steckverbinder, Knopfzellenhalter und schwere Bauteile MÜSSEN gegen Fahrzeugvibration gesichert sein. |
| M-04 | Leiterplatte **maximal 80 × 50 mm**; so kompakt wie möglich (SOLL). |
| M-05 | Einseitige Bestückung SOLL angestrebt werden. Zweiseitig nur, wenn M-04 sonst nicht erreichbar ist (begründen). |
| M-06 | USB-C von außen an einer Gehäusekante erreichbar. |
| M-07 | Nano-Fit-Anschlüsse an einer gemeinsamen Anschlusskante, im geöffneten Gehäuse entriegelbar. |
| M-08 | Antennenstecker (U.FL), Knopfzelle, BOOT-, RESET- und DIAG-Taster sowie alle LEDs bei geöffnetem Gehäuse zugänglich bzw. sichtbar. Sichtbarkeit bei geschlossenem Gehäuse ist nicht gefordert. |
| M-09 | Mindestens drei mechanisch belastbare Befestigungspunkte. Gehäuse (3D-Druck) wird nach dem finalen PCB konstruiert. |
| M-10 | Kabelzug wird im Gehäuse abgefangen, nicht am PCB-Header. |

## A3. Versorgung

| ID | Anforderung |
|---|---|
| P-01 | 12-V-Eingang: Betriebsbereich **10–14 V DC** aus 12-V-Zweitbatterie-Verbraucherkreis, extern mit 1 A abgesichert (0,5 mm²). Keine Sicherung und keine Batterieschutz-Unterspannungsabschaltung auf dem Board. 24 V/Fremdstart sind keine Anforderung. |
| P-02 | Verpolung mit **−14 V für ≥ 60 s** ohne Schaden. |
| P-03 | Schutz gegen ESD und typische lokale Schalt-/Leitungstransienten eines 12-V-Bordnetzes. Keine ISO-7637/16750-Zertifizierung; das angenommene Transientenprofil und die Grenzen der Schutzschaltung werden dokumentiert. Kein Bauteil darf bei Klemmspannung der Schutzbeschaltung seine Spannungsgrenze überschreiten. |
| P-04 | USB-C MUSS das komplette Board ohne 12 V versorgen (USB-2.0-Gerät/Sink, ohne PD). Gesamtaufnahme aus USB **≤ 500 mA** inklusive WLAN-Spitzen, Sensoren und Ring-LED; damit ist keine CC-Stromstufenerkennung nötig. CC1/CC2 normgerecht mit Rd terminiert. |
| P-05 | 12 V und USB werden rückstromsicher zusammengeführt. 12 V DARF NIE auf USB-VBUS gelangen; USB-VBUS DARF NICHT in den 12-V-Kreis oder `AUTOTERM_5V` speisen. Bei gleichzeitigem Anschluss SOLL 12 V die Last übernehmen. |
| P-06 | `3V3_CORE` bleibt bei allen Quellen, Quellenwechseln und Lastsprüngen (WLAN-TX) innerhalb **3,0–3,6 V**; ≥ 0,5 A am Modul. Abblockung am WROOM-3V3-Pin nach Espressif (mindestens 22 µF + 100 nF). |
| P-07 | Die 1-Wire-Sensorversorgung `3V3_SENSOR_SW` ist per GPIO schaltbar (Default aus), strom-/kurzschlussbegrenzt; ein Kurzschluss am Sensorkabel DARF `3V3_CORE` nicht einbrechen lassen. |
| P-08 | RTC-Backup aus austauschbarer Lithium-Primärzelle (12-mm-Klasse); Laden der Zelle hardwareseitig ausgeschlossen. Pufferzeit ≥ 4 Wochen. |
| P-09 | Ausgeschaltete Domänen DÜRFEN NICHT über GPIOs, Schutzdioden oder Pull-ups rückgespeist werden. |

## A4. Betriebszustände und Ruhestrom

| Zustand | ESP32/WLAN | Sensoren/UART/LEDs | Wake-Quellen | Strom am 12-V-Eingang |
|---|---|---|---|---|
| Normal | aktiv | nach Bedarf | – | – |
| Standby | Deep-Sleep, WLAN aus | aus | externer Taster, RTC-Alarm | **< 0,5 mA** |

- Keine LED darf in Reset, Boot oder Deep-Sleep leuchten; keine dauerhaft leuchtende Power-LED.
- Für jedes aktive Bauteil wird ein Worst-Case-Ruhestrombudget erstellt (inkl. Pull-ups, Leckströme, Reglerstrom).

## A5. Mikrocontroller, Programmierung, Funk

| ID | Anforderung |
|---|---|
| U-01 | Modul **`ESP32-S3-WROOM-1U-N16R8`** (festgelegt). `-N16R16VA` ist kein Ersatz. |
| U-02 | Natives USB (GPIO19/20) für Flashen und Konsole. D+/D− mit bestückbaren Serienwiderständen am Modul und ESD am Stecker. |
| U-03 | Lokale, beschriftete Taster `BOOT` (GPIO0 → GND) und `RESET` (`CHIP_PU/EN` → GND). GPIO0 mit 10 kΩ Pull-up, kein großer Kondensator. |
| U-04 | `CHIP_PU/EN` darf nicht floaten und wird erst freigegeben, wenn 3V3 stabil ist (≥ 50 µs, Ziel ≈ 20 ms); bei Unterspannung definiert zurückgesetzt – auch bei langsamem, unterbrochenem oder wechselndem Versorgungsanstieg. |
| U-05 | Strapping-Pins GPIO3, GPIO45, GPIO46 bleiben unbenutzt und ohne externen Pull-up; GPIO46 muss für Download-Boot LOW bleiben können. |
| U-06 | U0TXD/U0RXD (GPIO43/44) mit GND und 3V3 als beschriftete Testpads; kein Außenstecker. |
| U-07 | Externe 2,4-GHz-Antenne (≤ 2,33 dBi) über den integrierten U.FL-Stecker mit ≈ 10 cm Koax. Keine HF-Leitung auf dem PCB; mechanischer Freiraum für Gegenstecker und Biegeradius. |

## A6. Steckverbinder und Kabelbaum

| ID | Anforderung |
|---|---|
| C-01 | Alle Außenanschlüsse Molex Nano-Fit, verriegelnd, rechtwinklig THT, Goldkontakte, mit TPA (Teilenummern unten, festgelegt). Keine Original-Fremdgerätestecker auf dem PCB. |
| C-02 | Schnittstellen nicht vertauschbar: unterschiedliche Polzahlen (J4 deshalb 5-polig, Pin 5 NC). |
| C-03 | Pin 1, Signalnamen und Steckrichtung eindeutig in Schaltplan, Silkscreen und Kabelbaumzeichnung. |
| C-04 | Jede Leitung, die das Gehäuse verlässt, erhält am Stecker passenden ESD-/Transientenschutz. |

| Stecker | Pin | Signal | Beschreibung |
|---|---:|---|---|
| J1 Versorgung (2-pol.) | 1 | `BATT_12V_IN` | extern 1 A abgesichert |
| | 2 | `GND` | |
| J2 AUTOTERM (4-pol.) | 1 | `AUTOTERM_5V` | 5 V von der Heizung (am Gerät gemessen) |
| | 2 | `GND` | |
| | 3 | `CTRL_TX_TO_HEATER` | Controller → Heizung |
| | 4 | `CTRL_RX_FROM_HEATER` | Heizung → Controller |
| J3 1-Wire (3-pol.) | 1 | `3V3_SENSOR_SW` | geschaltet, strombegrenzt |
| | 2 | `1WIRE_DQ` | |
| | 3 | `GND` | |
| J4 Taster/LED (5-pol.) | 1 | `BUTTON_N` | active LOW; verdrillt mit Pin 2 |
| | 2 | `GND` | |
| | 3 | `LED_CC_PLUS` | strombegrenzter LED-Plus; verdrillt mit Pin 4 |
| | 4 | `LED_PWM_MINUS` | PWM-Low-Side-Rückleiter |
| | 5 | NC | nur Codierung |

| Stecker | Board-Header | Gegenstecker | TPA | Crimpkontakt |
|---|---|---|---|---|
| J1 | `1053131302` | `1053071202` | `1053251002` | `1053002300` (22–20 AWG) |
| J2 | `1053131304` | `1053071204` | `1053251004` | `1053001300` (26–24 AWG) |
| J3 | `1053131303` | `1053071203` | `1053251003` | `1053001300` (bei > 24 AWG: `1053002300`) |
| J4 | `1053131305` | `1053071205` | `1053251005` | `1053001300` |

## A7. AUTOTERM-UART

| ID | Anforderung |
|---|---|
| A-01 | Full-Duplex-UART, 5-V-Logik, gemeinsame Masse, Kabel 0,3–0,5 m; Hardware-UART ≠ UART0. |
| A-02 | Pegelwandlung 3,3 V ↔ 5 V; die 5-V-Seite wird ausschließlich aus `AUTOTERM_5V` versorgt (Strombegrenzung, Filter, ESD). Die Heizung versorgt nichts anderes auf dem Board. |
| A-03 | TX und RX werden über einen GPIO freigegeben (Hardware-Default: gesperrt). Bei Reset, Boot, Deep-Sleep, fehlendem `AUTOTERM_5V` und vor Softwarefreigabe ist `CTRL_TX_TO_HEATER` hochohmig; keine Rückspeisung in die Heizung oder aus ihr. |
| A-04 | Fehlt `AUTOTERM_5V`, arbeitet das restliche Board normal. |
| A-05 | TX/RX mit Serienwiderständen und niederkapazitivem ESD-Schutz; UART-Timing darf nicht beeinträchtigt werden. |

## A8. 1-Wire / DS18B20

| ID | Anforderung |
|---|---|
| W-01 | Genau ein 3-poliger Anschluss; drei DS18B20 extern parallel, Leitungen je 2–5 m; nur dreidrahtig (keine parasitäre Versorgung). |
| W-02 | Pull-up 4,7 kΩ (bestückungsseitig anpassbar) von DQ nach `3V3_SENSOR_SW`; bestückter 0-Ω-Serienwiderstand vor dem GPIO (später als Dämpfung nutzbar); niederkapazitiver ESD-Schutz am Stecker. |
| W-03 | Die Datenleitung muss nicht galvanisch oder per Schalter abgekoppelt werden. Die Firmware hält DQ hochohmig oder LOW, solange `3V3_SENSOR_SW` aus ist. |
| W-04 | Gemeinsame Bus-Topologie, kein Multiplexer. |

## A9. RTC

| ID | Anforderung |
|---|---|
| R-01 | RTC am I2C-Bus, Hauptversorgung aus `3V3_CORE`, Backup gemäß P-08. Genauigkeit SOLL ≤ ±20 ppm; die Uhrzeit wird zusätzlich per WLAN/NTP synchronisiert. |
| R-02 | Der RTC-Interrupt-/Alarmausgang wird auf einen Deep-Sleep-wake-fähigen GPIO geführt und MUSS den ESP32 aus dem Deep-Sleep wecken können (gemeinsam mit dem Taster, EXT1 ANY_LOW). Pull-up an einer im Deep-Sleep versorgten Schiene. |
| R-03 | Knopfzelle verpolungssicher bzw. eindeutig markiert, im geöffneten Gehäuse tauschbar; Einsetzen erst nach Löten/Reinigen. |

## A10. Externer Taster und Ring-LED

| ID | Anforderung |
|---|---|
| B-01 | Taster APEM AV, Bestellcode **`AV970220000700`** (19 mm, weiße LED ohne Vorwiderstand, Silberkontakte, Lötanschlüsse; vor Bestellung bestätigen). NO-Kontakt. Kabel ≈ 3 m, zwei verdrillte Paare. |
| B-02 | `BUTTON_N` active LOW direkt an einen Deep-Sleep-wake-fähigen GPIO; externer Pull-up, Serienwiderstand, RC-Filter, ESD am Stecker. Filter darf Wake nicht verhindern. |
| B-03 | Ring-LED mit Konstantstrom ≈ 10 mA (sicher < 20 mA), aus 12 V und USB betreibbar, per GPIO-PWM dimmbar, Hardware-Default aus. Nie direkt aus GPIO oder unbegrenzt aus einer Schiene. |
| B-04 | PWM darf nicht in den parallel geführten Tastereingang einkoppeln. |

## A11. Diagnoseanzeige und Status-LEDs

| ID | Anforderung |
|---|---|
| G-01 | Fünf rote LEDs mit Silkscreen-Beschriftung und Verbindungslinien:<br>`12V ●─┐`<br>`      ├─● 3V3 ─● RUN ─● HEAT`<br>`USB ●─┘` |
| G-02 | 12V = geschützter 12-V-Pfad vor der Zusammenführung; USB = geschütztes VBUS vor der Zusammenführung; 3V3 = `3V3_CORE`; RUN = GPIO, den die Firmware nach erfolgreicher Initialisierung setzt; HEAT = `AUTOTERM_5V` vorhanden. |
| G-03 | Die fünf LEDs leuchten nur bei gedrücktem DIAG-Taster (lokal, NO) oder überbrückten Testpads DIAG/GND. DIAG weckt den ESP32 nicht und verändert keinen Zustand. 12V/USB/3V3/HEAT funktionieren ohne GPIO. |
| G-04 | Keine Rückspeisung zwischen 12 V, USB-VBUS, `3V3_CORE` und `AUTOTERM_5V` über die Anzeige – weder gedrückt noch ungedrückt. |
| G-05 | 0,5–1 mA je LED über alle Quelltoleranzen, BOM-seitig anpassbar. Ruhestrom der Anzeige ohne DIAG ≤ 5 µA je Versorgungszweig. |
| G-06 | **Zwei rote Status-LEDs werden bestückt**, je über einen eigenen GPIO steuerbar, eigene Strombegrenzung, Hardware-Default aus. Sichtbar bei geöffnetem Gehäuse genügt. |

## A12. GPIO-Regeln und Belegung

Regeln:

- Wake-Eingänge (Taster, RTC-Alarm) direkt an RTC-GPIOs aus GPIO0–21, nicht an Strapping- oder USB-Pins.
- Jeder Ausgang, der etwas einschaltet, ist active HIGH mit externem Pulldown, damit der kurze LOW-Impuls von GPIO1–17 beim Einschalten und ein undefinierter Zustand vor der Firmware sicher „aus“ bedeuten.
- GPIO18 (LOW- und HIGH-Impuls beim Einschalten) nicht für Enables oder LED-Ausgänge.
- GPIO35–37 (Octal-PSRAM) und GPIO22–34 (nicht herausgeführt) sind nicht verfügbar.
- Unbenutzte GPIOs ohne Außenanschluss; Definition per Firmware.
- Kein Pin unter −0,3 V oder über VDD33 + 0,3 V.

Festgelegte Belegung (Änderung im Layout zulässig, wenn die Regeln eingehalten und dokumentiert werden):

| GPIO | Modulpad | Signal | Richtung | Externe Beschaltung | Default / Deep-Sleep | Wake |
|---:|---:|---|---|---|---|---|
| 0 | 27 | `BOOT_N` | E | 10 kΩ → 3V3, Taster → GND | HIGH | – |
| 4 | 4 | `STATUS_LED_1` | A | Vorwiderstand, 100 kΩ PD | LOW = aus | – |
| 5 | 5 | `STATUS_LED_2` | A | Vorwiderstand, 100 kΩ PD | LOW = aus | – |
| 6 | 6 | `DIAG_RUN` | A | 100 kΩ PD | LOW = aus | – |
| 7 | 7 | `RTC_INT_N` | E | Pull-up → 3V3_CORE (Open-Drain der RTC) | HIGH | EXT1 low |
| 15 | 8 | `I2C_SDA` | OD | 4,7 kΩ → 3V3_CORE | HIGH | – |
| 16 | 9 | `I2C_SCL` | OD | 4,7 kΩ → 3V3_CORE | HIGH | – |
| 17 | 10 | `AUTOTERM_TX_3V3` | A | Serien-R | gesperrt über OE | – |
| 18 | 11 | `AUTOTERM_RX_3V3` | E | Serien-R | – | – |
| 8 | 12 | `AUTOTERM_OE` | A | 100 kΩ PD | LOW = gesperrt | – |
| 19 | 13 | `USB_D_N` | USB | 22–33 Ω | – | – |
| 20 | 14 | `USB_D_P` | USB | 22–33 Ω | – | – |
| 9 | 17 | `BUTTON_N` | E | Pull-up → 3V3, Serien-R/RC, ESD | HIGH | EXT1 low |
| 10 | 18 | `BUTTON_LED_PWM` | A | 100 kΩ PD am Treiber | LOW = aus | – |
| 13 | 21 | `1WIRE_DQ` | OD | 4,7 kΩ → 3V3_SENSOR_SW, 0 Ω, ESD | Z | – |
| 14 | 22 | `SENSOR_EN` | A | 100 kΩ PD | LOW = aus | – |
| 43 | 37 | `U0TXD_TEST` | A | 499 Ω, Testpad | – | – |
| 44 | 36 | `U0RXD_TEST` | E | Testpad | – | – |
| 3, 45, 46 | 15, 26, 16 | Strapping, unbenutzt | – | kein Pull | – | – |
| 1, 2, 11, 12, 21, 38–42, 47, 48 | | Reserve | – | – | – | – |

Begründung: Jeder Funktionsblock liegt an der Modulseite, die ihm im Layout zugewandt ist (Platzierung Phase 3): linke Modulkante oben Status/Diagnose und RTC/I2C, darunter AUTOTERM, unten USB; untere Modulkante Taster/LED und 1-Wire über ihren Steckern; rechte Modulkante BOOT und UART0-Testpads. Fest sind nur EN, GPIO0, GPIO19/20 (USB) und GPIO43/44 (UART0). Alle Wake-Eingänge (GPIO7, GPIO9) sind RTC-GPIOs; alle Ausgänge liegen in GPIO4–17, sind active HIGH mit Pulldown (Einschaltimpuls = aus); GPIO18 wird nur als Eingang (RX) genutzt. GPIO15/16 sind frei, weil kein 32-kHz-Quarz am Modul hängt. Die JTAG-Pins GPIO39–42 bleiben frei. Modulpads 1, 40, 41/EPAD = GND; Pad 2 = 3V3; Pad 3 = `CHIP_PU/EN`.

## A13. Sichere Hardware-Defaultzustände

Ohne Firmware sowie in Reset, Boot und Deep-Sleep – durch Hardware erzeugt, nicht durch Software:

| Funktion | Zustand |
|---|---|
| AUTOTERM-TX/RX | gesperrt, TX hochohmig |
| Sensorversorgung | aus |
| Ring-LED, Status-LEDs, RUN | aus |
| Diagnose-LEDs 12V/USB/3V3/HEAT | aus, solange DIAG nicht gedrückt |
| Taster- und RTC-Wake-Eingang | HIGH, wake-fähig |
| 12-V-/USB-Pfade | gegenseitig rückstromgesperrt |

## A14. Leiterplatte und Layout

| ID | Anforderung |
|---|---|
| Y-01 | 4 Lagen, 1,6 mm, FR-4, ENIG, Standard-Vias (keine Blind/Buried), JLCPCB-Standardstackup mit Impedanzkontrolle. |
| Y-02 | L1 Bauteile und Signale; L2 durchgehende ungeteilte GND-Fläche; L3 Versorgung und langsame Signale; L4 GND und langsame Signale, möglichst ohne Bauteile. |
| Y-03 | USB D+/D− als 90-Ω-Differenzpaar, kurz, stubfrei, über durchgehender Referenz. Keine Signalleitung kreuzt einen Spalt ihrer Referenzfläche. |
| Y-04 | Abblockkondensatoren unmittelbar an den Pins; Schaltregler-Hot-Loop nach Hersteller-Referenzlayout, Schaltknoten klein und fern von RTC-Quarz/I2C, U.FL, 1-Wire und USB. |
| Y-05 | Offizielles Espressif-WROOM-1U-Landpattern unverändert (nicht WROOM-1); GND-Pads und EPAD mit mehreren Vias an L2; kein Antennen-Keep-out (U-Variante), aber Freiraum am U.FL. |
| Y-06 | ESD/TVS direkt am jeweiligen Stecker mit kurzem GND-Pfad; GND-Stitching an Kanten und um Leistungsbereiche; Leiterbreiten für Worst-Case-Strom. |
| Y-07 | Bauteile SOLLEN ≥ 0603 sein (kleiner nur wo nötig) und möglichst aus dem JLCPCB-Basic-/Preferred-Sortiment stammen. |
| Y-08 | Silkscreen: Steckerbezeichnungen, Pin 1, Polaritäten, Batteriepolung, BOOT/RESET/DIAG, Status-LEDs, Energiefluss-Diagramm, PCB-Revision, Testpunkte. |

## A15. Fertigung (JLCPCB)

| ID | Anforderung |
|---|---|
| X-01 | Erste Menge: 5 bestückte Prototypen bei **JLCPCB** (PCB + PCBA). Alle Bauteile mit LCSC-Nummer; keine automatische Substitution kritischer Teile. Nicht verfügbare Teile werden ersetzt (mit Prüfung nach N-03/Teil A) oder über JLCPCB Global Sourcing bzw. Beistellung beschafft. |
| X-02 | ESP32-Modul ist MSL 3 und SOLL genau einen Reflow-Zyklus erhalten – bei einseitiger Bestückung erfüllt. |
| X-03 | THT-Teile (Nano-Fit, ggf. Batteriehalter) über JLCPCB-THT-Bestückung oder Handlötung; Knopfzelle wird nicht mitbestückt. |
| X-04 | Fertigungsdaten im JLCPCB-Format: Gerber, Drill, BOM (mit LCSC-Spalte) und CPL mit korrekten Rotationen. |

## A16. Testpunkte

Beschriftete Pads, im geöffneten Gerät zugänglich: `BATT_12V_IN`, geschützter 12-V-Pfad, `VIN_SYS`, `3V3_CORE`, `3V3_SENSOR_SW`, GND (inkl. Oszilloskop-GND-Pad); `CHIP_PU`, GPIO0, U0TXD, U0RXD; AUTOTERM TX/RX beidseitig, OE, `AUTOTERM_5V`; `1WIRE_DQ`; SDA, SCL, `RTC_INT_N`; Ring-LED-PWM; DIAG und RUN. USB D+/D− nur stubfrei.

## A17. Abnahmetests (5 Prototypen)

Vor Bestellung: ERC/DRC ohne ungeklärte Fehler, Netzlistenprüfung nach N-05. Am Prototyp:

1. Sichtprüfung, Polarität, Kurzschlusstest aller Schienen.
2. Start und stabiler Betrieb bei 10 / 12 / 14 V.
3. USB-only: Flashen und Betrieb mit < 500 mA Aufnahme (inkl. WLAN-Spitzen, Sensoren, Ring-LED).
4. 12 V + USB gleichzeitig ohne Rückspeisung in USB, Fahrzeug oder AUTOTERM, alle Anschlussreihenfolgen.
5. Verpolung −14 V ≥ 60 s ohne Schaden.
6. WLAN-Lastsprung ohne Brownout; 3V3 am Modulpad 3,0–3,6 V.
7. Standby < 0,5 mA bei 12 V.
8. Wiederholtes Wake aus Deep-Sleep per Taster und per RTC-Alarm.
9. Defaultzustände (A13) bei Power-up, Reset, Deep-Sleep; Oszilloskop auf allen Enables, TX und LED-Ausgängen.
10. UART mit realer Heizung; ohne `AUTOTERM_5V` keine Rückspeisung, TX hochohmig.
11. Drei DS18B20 am realen 2–5-m-Kabelbaum; Kurzschluss am Sensorstecker ohne Einbruch von 3V3_CORE.
12. Ring-LED Dimmbereich und Maximalstrom bei 12 V und USB.
13. RTC über I2C, Umschalten auf Knopfzelle, Backupstrom.
14. 3V3 und EN bei Ein-/Ausschalten, Quellenwechsel, Brownout, schneller Wiederkehr.
15. Recovery: BOOT halten + RESET → USB-Download-Boot.
16. WLAN-Reichweite/Durchsatz im Gehäuse am Einbauort.
17. Diagnoseanzeige in allen Quellkombinationen; Rückspeisungsfreiheit; ≤ 5 µA ohne DIAG. Status-LEDs einzeln.
18. Temperatur der Leistungsbauteile im geschlossenen Gehäuse.

## A18. Lieferumfang und Vorgehen

Lieferumfang: KiCad-Projekt mit geprüften projektlokalen Bibliotheken; Schaltplan-PDF; GPIO-Tabelle; BOM mit LCSC-Nummern; JLCPCB-Fertigungsdaten (Gerber, Drill, BOM, CPL); Bestückungszeichnung; STEP-Modell des bestückten Boards; Kabelbaumzeichnungen J1–J4; Strom-/Ruhestrombudget und Berechnung der Eingangsschutzbeschaltung; ERC-/DRC-Berichte; Testprotokolle; Abweichungsliste gegenüber diesem Dokument.

| Phase | Inhalt | Freigabekriterium |
|---|---|---|
| 0 | KiCad-Projekt anlegen (4 Lagen, Titelblock, Netzklassen, JLCPCB-Regeln) | öffnet ohne fehlende Bibliotheken |
| 1 | Bauteilauswahl finalisieren (Teil B als Start), JLCPCB-Verfügbarkeit prüfen, Symbole/Footprints erstellen und prüfen | Bibliothek vollständig und geprüft, alle Teile mit LCSC-Nummer |
| 2 | Schaltplan manuell, hierarchisch: Versorgung/USB · ESP32/Reset/RTC · AUTOTERM/1-Wire · Taster/Diagnose/Status; ERC, Netzlistenprüfung, PDF, BOM | Review abgeschlossen |
| 3 | Kontur ≤ 80 × 50 mm, Befestigung, Platzierung, 3D-Prüfung | Platzierungsreview freigegeben |
| 4 | Routing nach A14 | DRC sauber, Schaltplan/PCB/BOM synchron |
| 5 | JLCPCB-Fertigungsdaten | Release-Checkliste vollständig |
| 6 | Inbetriebnahme und Abnahme nach A17 | Prüfbericht aller 5 Prototypen |

---

# Teil B – Referenzlösung (informativ)

Teil B beschreibt einen empfohlenen, gegenüber dem bisherigen Entwurf vereinfachten Lösungsweg. Die JLCPCB-Verfügbarkeit wurde am 2026-10-12 geprüft (B2) und ist vor der Bestellung erneut zu bestätigen; bei Nichtverfügbarkeit ist ein funktional gleichwertiges JLCPCB-Teil zu wählen.

## B1. Blockschaltbild

```text
J1 12V ─ TVS (bidir.) ─ Schottky 60 V ─ Ferrit/C ─────────┐
                                                          ├─ VIN_SYS ─ Buck 3,3 V ─ 3V3_CORE ─┬─ ESP32-S3-WROOM-1U
USB-C VBUS ─ ESD ─ eFuse mit Rückstromsperre ─────────────┘     (Rd 5,1 kΩ an CC1/CC2)        ├─ RTC + I2C-Pull-ups
                                                                                              ├─ Lastschalter ─ 3V3_SENSOR_SW ─ J3
VIN_SYS ─ Konstantstromregler ─ J4 Ring-LED                                                   └─ Supervisor ─ EN
J2 AUTOTERM_5V ─ R/C/ESD ─ VCCB Pegelwandler ─ J2 TX/RX
3V3_CORE / Knopfzelle ─ Dioden-ODER ─ RTC
```

## B2. Bauteilvorschläge mit JLCPCB-Verfügbarkeit

Lagerbestand am 2026-10-12 laut jlcpcb.com/parts (5 Prototypen benötigen je Teil nur wenige Stück). „Vorbestellung“ = über JLCPCB Global Sourcing bestellbar, mit Lieferzeit. Alle Teile sind bei JLCPCB „Extended“ (einmalige Rüstgebühr je Teil); Widerstände, Kondensatoren und Standard-Dioden werden in Phase 1 bevorzugt aus dem Basic-Sortiment gewählt.

| Funktion | Vorschlag | LCSC | Lager | Bewertung |
|---|---|---|---:|---|
| ESP32-Modul | `ESP32-S3-WROOM-1U-N16R8` | C3013946 | 12 380 | Festgelegt (A5), gut verfügbar. Datenblatt nennt hier −40…+65 °C; +85 °C nur mit PSRAM-ECC (Firmware). |
| 12-V-Verpol- und Rückstromschutz | 60-V-Schottky 1 A `SS16` (SMA) | C2481 | 309 202 | **Vereinfacht.** Ersetzt `LM74720-Q1` + Dual-MOSFET. Bei ≈ 0,1–0,3 A sind 0,5–0,7 V Abfall unkritisch; kein Ruhestrom, sperrt −14 V dauerhaft. |
| Eingangs-TVS | `SMBJ18CA` (bidirektional, 600 W, Klemmung 29,2 V) | C78413 | 84 358 | Ersetzt `TPSMB18CA-VR` (bei JLCPCB nicht lieferbar). Bidirektional, damit Verpolung die TVS nicht leitend macht. 29,2 V < 36 V Buck-Eingangsgrenze. |
| OV-Abschaltung | entfällt | – | – | Buck verträgt die TVS-Klemmspannung. |
| USB-C-Buchse | `USB4105-GF-A-060` (16-pol. USB 2.0) | C3025063 | 1 123 | Gleiche Buchse wie `-120`, kürzere Haltestifte; Footprint daran anpassen. |
| USB-CC | 2 × 5,1 kΩ Rd | Basic | – | **Vereinfacht.** Ersetzt `TUSB321` + `2N7002` + GPIO, da Aufnahme ≤ 500 mA. |
| USB-Pfad | `TPS259470LRPWR` eFuse (Strombegrenzung, OVLO ≈ 5,8 V, Rückstromsperre, 23 V am Ausgang zulässig) | C3662793 | 562 | Übernommen. Eine Schottky-Diode würde bei warmem Board durch Leckstrom aus VIN_SYS in VBUS zurückspeisen. |
| USB-ESD D+/D− | `TPD2EUSB30DRTR` | C97502 | 5 480 | Übernommen. |
| USB-ESD VBUS | `ESD5Z5.0T1G` | C82044 | 373 429 | Übernommen. |
| 3,3-V-Buck | `LMR43620MSC3RPERQ1` (fest 3,3 V, 2 A, 36 V, 1,2 µA Ruhestrom, Auto-PFM) | C3190193 | **14** | Übernommen; Bestand reicht für 5 Boards, früh reservieren. Die 1-A-Variante `LMR43610MSC3` (C5219290) ist nur vorbestellbar, die Varianten `…R5`/`…MB5` haben 5 V Ausgang. |
| Buck-Induktivität | 2,2 µH, 4,5 A, abgeschirmt, 4 × 4 mm (`FAUL0420-2R2MT`) | C3040383 | 2 606 | Ersetzt `XAL4020-222MEC` (nur vorbestellbar); Sättigungsstrom > 3,9 A Spitzenstromgrenze des Buck. |
| ESP32-Abblockung | 2 × 22 µF/10 V X7R 1206 (`GCJ31CR71A226KE01L`) + 100 nF | C6565118 | 817 | Übernommen; alternativ Basic-22-µF-X7R. |
| Reset | `TPS3808G33DBVR` (Open-Drain, ≈ 20 ms) + 10 kΩ/1 µF an EN | C51886189 | 3 407 | Übernommen (Nicht-Automotive-Variante, gleiche Funktion). |
| Sensor-Lastschalter | `TPS22945DCKR` (Strombegrenzung 100 mA) | C47507 | 9 908 | Übernommen. |
| AUTOTERM-Pegelwandler | `TXU0202QDCURQ1` (fest gerichtet, OE, Ioff) | C7372013 | 1 028 | Übernommen. |
| `AUTOTERM_5V`-Versorgung | 100 Ω + 1 µF + ESD statt Lastschalter | Basic | – | **Vereinfacht.** VCCB braucht nur µA; Spannung am Gerät gemessen. |
| ESD AUTOTERM | `PESD5V2S2UT,215` | C18441 | 150 578 | Übernommen; gemeinsame Anode an Pin 3. |
| ESD 1-Wire/Taster | `PESD3V3S2UT,215` | C84276 | 55 431 | Übernommen; gemeinsame Anode an Pin 3. |
| RTC | `RV-8263-C8-32.768KHZ-20PPM-TA-QC` (190 nA, Alarm, Open-Drain-INT, I2C) | C24955831 | 460 | **Geändert.** `RV-3028-C7` ist bei JLCPCB nicht lieferbar (≈ 76 Tage Vorbestellung). RV-8263 hat keine eingebaute Backup-Umschaltung → Versorgung über Dioden-ODER (2 × `BAS116`) aus 3V3_CORE und Knopfzelle. ±20 ppm genügt, da die Zeit per WLAN/NTP synchronisiert wird. Bevorzugt, falls beschaffbar: `RV-3028-C7` (C3019759). |
| Sperrdioden (RTC-Backup, Diagnose) | `BAS116,215` (Leckstrom 3 pA) | C48502 | 42 689 | Übernommen. |
| Knopfzelle/Halter | `BR1225` in SMD-Klemme `MY-1225-01-J` (Minuspol = Kupferpad unter der Zelle) | C20606803 | 1 281 | Ersetzt Keystone `500` (nicht lieferbar). Zelle wird nicht bestückt. |
| Ring-LED-Treiber | `BCR421UW6Q-7` (10 mA, EN = PWM < 25 kHz) | C154739 | **65** | Übernommen; Bestand ausreichend, früh reservieren. Thermik bei 14 V (≈ 125 mW) und Headroom bei USB prüfen. |
| Diagnose-Schalter | `2N7002K` | C22379475 | 1 607 174 | Übernommen; Gate-Teiler so, dass VGS bei 14 V + Transienten < 20 V bleibt. |
| LEDs | `LTST-C190KRKT` (rot, 0603) | C94869 | 337 173 | Übernommen. |
| Lokale Taster | `KMR221GLFS` | C72443 | 5 668 | Übernommen. |
| Nano-Fit J2 | `1053131304` | C17554326 | **9** | Knapp, sofort reservieren. |
| Nano-Fit J1, J3, J4 | `1053131302`, `1053131303`, `1053131305` | C17345480, C17198650, C17316840 | 0 | Nur vorbestellbar (Mindestmenge 4–8). Alternativ Beistellung. JLCPCB-Beschreibung nennt „Tin“ – Kontaktoberfläche gegen Molex-Datenblatt prüfen (Gold-zu-Gold-Regel, A6). |

## B3. Startwerte

- Taster: 10 kΩ Pull-up, 1 kΩ Serie, 10 nF (≈ 10 µs).
- I2C: 4,7 kΩ nach 3V3_CORE, 100 kHz.
- RTC-INT: 100 kΩ Pull-up nach 3V3_CORE (Open-Drain, im Alarm-LOW sonst kein Strom).
- RTC-Versorgung: Dioden-ODER aus 3V3_CORE und Knopfzelle (je `BAS116`); RTC arbeitet ab 0,9 V.
- Enables/PWM/OE/LED-GPIOs: 100 kΩ Pulldown.
- USB D+/D−: 22 Ω Serie, optionaler DNP-Kondensator nach GND.
- U0TXD: 499 Ω Serie.
- TPS259470L: RILM ≈ 3,3 kΩ (≈ 1 A) bzw. höher für ≈ 0,6 A; OVLO-Teiler 100 kΩ/26,1 kΩ; dV/dt 10 nF.
- Diagnose-LEDs: Vorwiderstände für 0,5–1 mA je Quelle berechnen.

## B4. Strom- und Ruhestromabschätzung

- USB-Spitze: ESP32 500 mA bei 3,3 V → ≈ 390 mA aus 5 V (85 %), plus Sensoren, Ring-LED, Reserve ≈ 30 mA → **≈ 420 mA < 500 mA**.
- 12-V-Vollbetrieb: ≈ 0,2 A; Verlust Schottky ≈ 0,1 W, Buck ≈ 0,3 W.
- Standby, grob: ESP32 Deep-Sleep ≈ 10–20 µA, Buck ≈ 2 µA, Supervisor ≈ 2 µA, Pegelwandler/Lastschalter/RTC/Leckströme ≈ 10–20 µA → ≈ 40 µA bei 3,3 V, also deutlich **unter 50 µA bei 12 V**. Großes Polster zum 0,5-mA-Ziel (der Hauptverbraucher Touch/Frontlicht ist entfallen).
- RTC-Backup: BR1225 ≈ 48 mAh bei < 0,5 µA → weit über 4 Wochen.

## B5. Offene Prüfpunkte

| # | Punkt |
|---|---|
| V-01 | Transientenprofil festlegen; TVS-Klemmung und Spannungsfestigkeit von Schottky, Buck und Eingangskondensatoren nachweisen. |
| V-02 | Effektive MLCC-Kapazitäten (DC-Bias); Buck-Ripple und Lastsprung messen. |
| V-03 | USB-Einschaltstrom und Gesamtaufnahme am Muster. |
| V-04 | APEM-Code, Kontaktbelegung, LED-Polarität und -Flussspannung am Muster; BCR421-Headroom bei USB. |
| V-05 | 1-Wire-Timing am realen Kabelbaum; Taster-RC am 3-m-Kabel. |
| V-06 | JLCPCB: Bestand vor Bestellung erneut prüfen (knapp: Buck 14, BCR421 65, Nano-Fit J2 9 Stück); Vorbestellung bzw. Beistellung für Nano-Fit J1/J3/J4 und Batteriehalter; THT-Bestückung; Stackup. |
| V-07 | Nano-Fit-Teile gegen Herstellerzeichnung, Crimpwerkzeug, Gold-zu-Gold. |

## B6. Lehren aus dem bisherigen Versuch

- Der skriptgenerierte Schaltplan war schlecht lesbar und an einen Generator gebunden, der manuelle Änderungen überschreibt → N-01/N-02.
- ERC hat unzulässige Netzverschmelzungen nicht erkannt → N-05.
- Häufige Fehler, die von Anfang an richtig umzusetzen sind: ESD-Arrays mit gemeinsamer Anode an Pin 3; keine Doppelterminierung an USB-CC; Diagnose-USB-LED am VBUS vor der Zusammenführung; Strapping-Pins ohne Pull-ups.

## B7. Layout-Checkliste (aus Hersteller-Leitfäden)

Quellen: Espressif *ESP32-S3 Hardware Design Guidelines – PCB Layout Design*, TI LMR43620-Q1 Datenblatt Abschnitt 8.5, TI-Layoutleitfäden für ESD-Schutz, Renesas *Full-Speed USB 2.0 Board Design*, JLCPCB-Hilfe zu Passermarken und Nutzenrändern, In Compliance Magazine *PCB Layout Considerations*.

| # | Regel | Phase |
|---|---|---|
| G-01 | 3V3-Hauptversorgung ≥ 0,65 mm (25 mil); Lagenwechsel der Versorgung mit mindestens 2 Vias. | 3/4 |
| G-02 | Am Modul 10–22 µF am Versorgungseingang, 100 nF direkt an Pad 2 (≤ 2 mm), GND-Via am Kondensator. Allgemein: jeder 100-nF-Abblockkondensator ≤ 2 mm vom Versorgungspin. | 3 |
| G-03 | U0TXD-Serienwiderstand am Modulpad; UART-Leitungen kurz, auf der Oberseite, mit GND-Umrandung. | 3/4 |
| G-04 | USB-Serienwiderstände am Modul, ESD am Stecker; D+/D− parallel, längengleich, 90 Ω ± 10 %, möglichst ohne Via; falls doch, je ein GND-Rückführungsvia; GND-Kupfer beidseitig. | 3/4 |
| G-05 | USB, UART und schnelle Signale vom U.FL-Anschluss fernhalten; unter dem U.FL alle Lagen frei. | 3/4 |
| G-06 | In1.Cu durchgehend GND ohne Leiterbahnen; dichte GND-Vias um die Modul-Massepads und das EPAD. | 4 |
| G-07 | ESD-/TVS-Schutz direkt am Stecker; geschützte Leitung vom Stecker zum Schutzbauteil gerade und ohne Via; ungeschützte Leitungen von geschützten fernhalten. | 3/4 |
| G-08 | Buck: CIN direkt an VIN/GND (≤ 1 mm), VCC- und BOOT-Kondensator kurz und breit, SW-Fläche minimal, VOUT-Messleitung nicht neben SW; laute Ströme auf eine Seite der Massefläche, empfindliche Leitungen auf die andere. | 3/4 |
| G-09 | GND-Vias direkt an den Ein- und Ausgangskondensatoren; Kupferfläche zur Wärmeableitung. | 4 |
| G-10 | 3 Passermarken: 1 mm Kupfer, 2 mm Lötstoppfreistellung, ≥ 3,35 mm vom Rand, nicht symmetrisch. | 3 |
| G-11 | Bauteile am Rand → Nutzenränder (5 mm) für die JLCPCB-Bestückung vorsehen. | 5 |
| G-12 | Massefläche nie teilen, Blöcke räumlich trennen; schnelle Signale nur über ungeteilter Masse; GND-Vias an jedem Lagenwechsel. | 4 |
| G-13 | Signale kurz und direkt, 45°-Knicke; Funktionsblöcke nach Signalfluss; gepolte Bauteile einheitlich ausgerichtet. | 3/4 |

## B8. Referenzen

- Espressif: [ESP32-S3-WROOM-1/1U Datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), [Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), [PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html), [Sleep Modes](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html)
- TI: [LMR43610-Q1/LMR43620-Q1](https://www.ti.com/product/LMR43620-Q1), [TPS25947](https://www.ti.com/product/TPS25947), [TPS3808-Q1](https://www.ti.com/product/TPS3808-Q1), [TXU0202-Q1](https://www.ti.com/product/TXU0202-Q1)
- [Diodes BCR421UW6Q](https://www.diodes.com/datasheet/download/BCR420UW6Q.pdf), [Micro Crystal RV-8263-C8](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-8263-c8), [Panasonic BR1225](https://industrial.panasonic.com/ww/products/pt/lithium-batteries/models/BR1225), [Molex Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors), [APEM AV](https://www.apem.com/api/asset/en/fbCPLUNNnaEJPS7JlAtdy/pusbutton-switches-serie-AV.pdf)
- [USB Type-C Specification R2.0](https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf), [JLCPCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [ADI Long-Line 1-Wire Guidelines](https://www.analog.com/en/resources/technical-articles/guidelines-for-reliable-long-line-1wire-networks.html)
