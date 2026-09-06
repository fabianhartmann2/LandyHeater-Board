# Landy Heater Controller – Hardware-Anforderungsspezifikation Revision A

Dokumentversion: 1.0

Stand: 2026-09-06

Status: freigegeben als Grundlage für Schaltplan, PCB-Layout und Angebotserstellung; noch keine Fertigungsfreigabe

## 1. Zweck und Verbindlichkeit

Dieses Dokument beschreibt die vollständigen Hardwareanforderungen für Revision A des Landy-Heater-Steuergeräts. Ein PCB-Designer muss daraus Schaltplan, Leiterplattenlayout, Fertigungsdaten und Bestückungsdaten erstellen können. Anwendungssoftware und proprietäre Geräteprotokolle sind nicht Teil des Auftrags.

Die Begriffe haben folgende Bedeutung:

- **MUSS / DARF NICHT:** verbindliche Anforderung.
- **SOLL:** verbindliches Designziel; eine Abweichung ist schriftlich zu begründen.
- **KANN:** optionale Ausführung ohne Einfluss auf die Abnahme.
- **Verifikationspunkt:** vom PCB-Designer vor der Fertigungsfreigabe zu prüfen und zu dokumentieren; keine offene Funktionsentscheidung des Auftraggebers.

Bei Widersprüchen gilt diese Rangfolge:

1. Freigegebene Änderungsmitteilung zu diesem Dokument
2. Dieses Dokument
3. Aktuelles Datenblatt, Referenzschaltung, Landpattern und Layoutvorgaben des jeweiligen Bauteilherstellers
4. Espressif Hardware Design Guidelines für den ESP32-S3 und das offizielle WROOM-1U-Landpattern
5. Bestätigter Stackup und Fertigungsregeln von PCBWay
6. Predictable Designs „PCB Layout Rules Checklist“ als zusätzliche Review-Checkliste

Wenn eine Herstellerangabe einer Anforderung dieses Dokuments technisch widerspricht, darf nicht eigenmächtig davon abgewichen werden. Der Konflikt ist vor dem Schaltplan- oder Layout-Freeze zu melden.

## 2. Produktzweck und Systemgrenze

Revision A ist ein kompaktes Bedien- und Kommunikationssteuergerät für eine AUTOTERM/Planar-Dieselstandheizung. Das Gerät:

- kommuniziert über eine 5-V-UART-Schnittstelle mit der originalen Heizungssteuerung,
- liest drei extern zusammengeschaltete DS18B20-Temperatursensoren über einen gemeinsamen 1-Wire-Bus,
- besitzt ein E-Paper-Display mit kapazitivem Touch und Frontlicht,
- besitzt einen externen Taster mit dimmbarer weißer Ringbeleuchtung,
- besitzt eine batteriegepufferte Echtzeituhr,
- stellt WLAN über ein ESP32-S3-Modul bereit,
- wird aus einem abgesicherten 12-V-Zweitbatteriekreis oder zu Servicezwecken über USB-C versorgt.

Das Board steuert keine Glühkerze, Kraftstoffpumpe, Gebläselast oder andere Heizungsleistung direkt. Alle verbrennungs- und sicherheitsrelevanten Funktionen verbleiben in der originalen AUTOTERM-Steuerung.

## 3. Verbindliche Abgrenzung von Revision A

Revision A enthält ausdrücklich **nicht**:

- kein FireBeetle- oder anderes Entwicklungsboard,
- keine VOTRONIC-VBCS-Schnittstelle,
- keine VOTRONIC-Smart-Shunt-Schnittstelle,
- keine RS-485-Transceiver oder externen RS-485-Stecker,
- keinen CAN-Bus,
- keinen ACC-/KL15-Eingang,
- keine zusätzliche Sicherung auf dem PCB,
- keine 12-V-Last-, Relais-, High-Side- oder Open-Drain-Ausgänge,
- keine eigene PCB-Antenne und keine vom PCB-Designer zu routende HF-Leitung,
- kein separates Display-Bedienteil und keine Verlängerung der Display-FPCs,
- keine USB-PD-Funktion und keinen USB-UART-Wandler.

VBCS und Smart-Shunt sind nur als mögliche Funktionen einer späteren Leiterplattenrevision dokumentiert. Revision A muss dafür weder Schaltungsteile noch Steckverbinder oder reservierte GPIOs enthalten.

## 4. Einsatzbedingungen und Mechanik

### 4.1 Einbauort und Umwelt

- Einbauort ist die Cubby Box in der Mittelkonsole eines Land Rover.
- Der Einbauort ist vor direktem Spritzwasser und regulärer Kondensation geschützt.
- Eine IP-Zertifizierung und Schutzlackierung sind für Revision A nicht gefordert.
- Das 3D-gedruckte Gehäuse muss gegen versehentlich verschüttete Flüssigkeit schützen und den Kabelzug aufnehmen.
- Aktive Halbleiter und sonstige kritische Bauteile sollen, soweit verfügbar, mindestens für −40 °C bis +85 °C spezifiziert sein.
- Die Temperaturgrenzen des Displays nach Abschnitt 10 begrenzen die Gesamtbaugruppe unabhängig von den übrigen Bauteilen.
- Steckverbinder, Knopfzellenhalter und schwere Bauteile müssen für Fahrzeugvibration mechanisch gesichert sein.

### 4.2 Bauraum und Anordnung

- Maximaler Bauraum der kompletten Display-/PCB-Einheit: **100 mm × 50 mm × 35 mm**.
- Gegenstecker, herausgeführte Kabel und deren Biegeradien sind vom 100-mm-×-50-mm-Flächenlimit ausgenommen.
- Zielgröße des PCB: höchstens **98 mm × 48 mm**. Eine Überschreitung ist vor dem Layout schriftlich freizugeben.
- Das Display liegt auf der Bedien-/Vorderseite.
- Der überwiegende Teil der Elektronik darf auf der Rückseite bestückt werden. Beidseitige Bestückung ist zulässig und wird erwartet.
- USB-C muss an einer seitlichen Gehäusekante von außen erreichbar sein.
- Die Nano-Fit-Anschlüsse müssen auf der dem Display gegenüberliegenden Anschluss-/Rückseite angeordnet und im geöffneten Gehäuse entriegelbar sein.
- Antennenstecker, Knopfzelle, BOOT- und RESET-Taster müssen für Montage und Service zugänglich bleiben.
- Das Gehäuse wird nach dem finalen PCB als 3D-Druckteil konstruiert. PCB und Gehäuse müssen mindestens drei mechanisch belastbare Befestigungspunkte besitzen; Lage und Art werden beim Platzierungsreview gemeinsam festgelegt.
- Die drei Display-FPCs dürfen weder als mechanische Halterung noch als Zugentlastung dienen.

## 5. Versorgungskonzept

### 5.1 12-V-Eingang

- Quelle ist ausschließlich ein 12-V-Zweitbatterie-Verbraucherkreis.
- Normaler Betriebsbereich am Boardeingang: **10 V bis 14 V DC**.
- Ein vorgeschalteter Batteriewächter trennt die Lasten bei zu niedrigem Ladezustand. Eine eigene Unterspannungsabschaltung zum Batterieschutz ist keine Aufgabe dieses Boards.
- Die dedizierte Zuleitung ist außerhalb des Boards mit **1 A** abgesichert und verwendet **0,5 mm²** Leiterquerschnitt.
- Auf dem Board darf keine weitere Sicherung vorgesehen werden.
- Dauerbetrieb an 24 V und 24-V-Fremdstart sind keine Anforderungen.
- Das Board muss trotzdem gegen Verpolung, ESD sowie typische lokale Schalt- und Leitungstransienten eines 12-V-Fahrzeugnetzes geschützt sein.
- Verpolung mit −14 V am Eingang für mindestens 60 s darf keinen Schaden verursachen.
- Der Schutz ist verlustarm und mit niedrigem Ruhestrom auszulegen. Eine Schaltung auf Basis des `LM74502-Q1` und externer N-MOSFETs oder eine nachweislich gleichwertige Lösung ist zulässig.
- Eine TVS-Diode und ein gedämpfter Eingangs-/EMI-Filter sind vorzusehen. TVS-Klemmspannung, Toleranzen und parasitäre Überschwinger müssen unterhalb der zulässigen Transientenspannung aller nachfolgenden Bauteile bleiben und rechnerisch dokumentiert werden.
- Es ist keine formale ISO-7637- oder ISO-16750-Zertifizierung für Revision A gefordert. Das gewählte Schutzprofil und seine Grenzen müssen dennoch im Designbericht ausdrücklich genannt werden.

### 5.2 USB-C-Versorgung

- USB-C muss das komplette Logikboard ohne anliegende 12 V versorgen können, einschließlich ESP32, Display, Touch, RTC, 1-Wire-Sensorversorgung und Frontlicht.
- Für uneingeschränkten USB-Betrieb ist eine 5-V-Quelle mit mindestens **1 A** vorzusehen.
- Das Board arbeitet als USB-2.0-Gerät/Sink ohne USB-PD.
- CC1 und CC2 erhalten die normgerechten separaten Rd-Widerstände.
- USB-VBUS und D+/D− erhalten geeigneten ESD-Schutz; die VBUS-Eingangskapazität muss USB-konform sein.
- 12 V dürfen unter keinen Betriebs- oder Fehlerbedingungen auf USB-VBUS gelangen.
- USB-VBUS darf nicht in den 12-V-Fahrzeugkreis oder in `AUTOTERM_5V` zurückspeisen.

### 5.3 Power-OR und 3,3-V-Hauptversorgung

Die verbindliche Funktionskette lautet:

`J1 B+ -> Verpol-/Transientenschutz -> Filter -> ideal entkoppelter 12-V-Pfad -> VIN_SYS`

`USB-C 5 V -> Strom-/Rückstromschutz -> ideal entkoppelter USB-Pfad -> VIN_SYS`

`VIN_SYS -> Low-IQ-Buck 3,3 V / 2 A -> 3V3_CORE`

- Bei gleichzeitigem Anschluss von 12 V und USB muss der 12-V-Pfad Vorrang haben.
- Beide Quellen müssen gegeneinander rückstromgesperrt sein.
- Der 3,3-V-Regler wird mit dem automotive-qualifizierten `LMR43620-Q1`, 3,3-V-/2-A-Ausführung, realisiert. Die genaue bestellbare Variante und Schaltfrequenz werden anhand von Wirkungsgrad, EMI und PCBWay-Verfügbarkeit festgelegt und in der BOM genannt.
- Auto-/PFM-Leichtlastbetrieb muss möglich sein. Ein dauerhaft erzwungener FPWM-Modus ist wegen des Ruhestromziels nicht zulässig.
- Referenzschaltung, Bauteilberechnung, Hot-Loop und Layout des Herstellers sind einzuhalten.
- `3V3_CORE` muss bei zulässigen Quellen und Lastsprüngen zwischen 3,0 V und 3,6 V bleiben. Wi-Fi-Sendespitzen dürfen keinen Brownout oder unbeabsichtigten Reset verursachen.
- Mindestens 10 µF Bulk-Kapazität und die von Espressif geforderte lokale Abblockung sind nahe der ESP32-Modulversorgung vorzusehen.

### 5.4 Versorgungsdomänen

Folgende Netze sind getrennt und eindeutig zu benennen:

- `3V3_CORE`: ESP32, I2C-Bus und dauerhaft benötigte Logik.
- `3V3_TOUCH`: Touch-Controller im Komfort-Standby; für den Minimalmodus abschaltbar.
- `3V3_DISPLAY_SW`: E-Paper-Logik und Booster-Beschaltung; im Deep-Sleep aus.
- `3V3_SENSOR_SW`: externe DS18B20-Versorgung; im Deep-Sleep aus.
- `VIN_SYS`: strombegrenzte Versorgung der externen weißen Taster-LED, damit sie sowohl bei 12-V- als auch bei USB-Versorgung betrieben werden kann.
- `AUTOTERM_5V`: ausschließlich von der Heizung bereitgestellte Versorgung/Referenz der 5-V-Seite des UART-Pegelwandlers; keine Verbindung zu USB-VBUS oder `VIN_SYS`.
- `RTC_VBACKUP`: Backupversorgung ausschließlich aus der Knopfzelle.

Schaltbare Domänen dürfen bei ausgeschaltetem Zustand weder über GPIO-Schutzdioden noch über Bus-Pull-ups rückgespeist werden.

### 5.5 Betriebszustände und Ruhestrom

| Zustand | ESP32/WLAN | Display/Frontlicht | Touch | Sensor/UART/LEDs |
|---|---|---|---|---|
| Normalbetrieb | aktiv, WLAN typischerweise dauerhaft aktiv | nach Softwarebedarf | aktiv | nach Softwarebedarf |
| Komfort-Standby | ESP32 Deep-Sleep, WLAN aus | aus | aktiv für Touch-Wakeup | aus |
| Minimal-Standby | ESP32 Deep-Sleep, WLAN aus | aus | abgeschaltet oder tiefster Modus ohne Touch-Wakeup | aus |

- Wake-Quellen im Komfort-Standby sind der externe Taster und Touch-INT.
- Im Minimal-Standby ist mindestens der externe Taster als Wake-Quelle verfügbar.
- Ziel für den gesamten Strom aus dem 12-V-Eingang im Komfort-Standby: **< 0,5 mA bei 12 V**.
- Der Minimal-Standby muss einen messbar niedrigeren Strom erreichen; es wird kein fester Grenzwert vorgegeben.
- Keine LED darf im Reset, beim Booten oder im Deep-Sleep durch einen undefinierten GPIO-Zustand leuchten.
- Für jedes aktive Bauteil ist ein Worst-Case-Ruhestrombudget einschließlich Pull-ups, Schutzbauteilleckströmen und Reglerstrom zu erstellen.

## 6. Mikrocontroller, Programmierung und Funk

- Verbindliches Modul für Revision A: **`ESP32-S3-WROOM-1U-N16R8`**.
- Speicher: 16 MiB Quad-SPI-Flash und 8 MiB Octal-SPI-PSRAM.
- PSRAM-ECC muss in der Firmware aktiviert und am Prototyp geprüft werden. Damit reduziert sich der nutzbare PSRAM um 1/16; der laut Espressif mögliche maximale Umgebungstemperaturbereich des R8-Moduls steigt von +65 °C auf +85 °C.
- `ESP32-S3-WROOM-1U-N16R16VA` ist für Revision A **kein freigegebener Drop-in-Ersatz**. Bei dieser Variante arbeiten GPIO47/48 mit 1,8 V.
- GPIO35, GPIO36 und GPIO37 sind durch das Octal-PSRAM belegt und dürfen nicht verwendet werden.
- GPIO19 und GPIO20 sind für natives USB D−/D+ reserviert.
- GPIO0 dient ausschließlich der BOOT-Funktion. GPIO3, GPIO45 und GPIO46 dürfen nicht für externe Schnittstellen, Wake-Signale oder Signale mit problematischem Einschaltpegel verwendet werden.
- GPIO47 und GPIO48 sollen frei bleiben, solange dadurch kein anderer Designnachteil entsteht.
- Alle übrigen Pinzuordnungen sind vor Schaltplan-Freeze in einer Pin-Matrix mit Resetpegel, Pull-up/-down, Wake-Fähigkeit und Versorgungsdomäne zu dokumentieren.
- Es wird natives ESP32-S3-USB für Flashen, REPL und Diagnose verwendet.
- Ein lokaler, beschrifteter `RESET`-Taster muss `CHIP_PU/EN` gegen GND ziehen.
- Ein lokaler, beschrifteter `BOOT`-Taster muss GPIO0 gegen GND ziehen.
- Pull-ups und das RC-Netzwerk an `CHIP_PU` müssen den aktuellen Espressif-Vorgaben entsprechen; `CHIP_PU` darf nicht floaten.
- U0TXD/U0RXD sowie GND und 3,3 V sollen als beschriftete Testpads erreichbar sein, dürfen aber keinen zusätzlichen Außenstecker erfordern.
- Das Modul wird über seinen integrierten U.FL-/MHF-I-kompatiblen Antennenanschluss mit einer externen 2,4-GHz-/50-Ω-WLAN-Antenne und etwa 10 cm Koaxialkabel verbunden.
- Der Antennengewinn darf 2,33 dBi nicht überschreiten, sofern nicht eine gesonderte regulatorische/EMV-Bewertung eine andere Antenne freigibt.
- Auf dem Mainboard wird keine HF-Leitung zwischen Modul und Antenne geroutet.
- Die Antenne muss bei aktivem Funk angeschlossen sein. Koaxstecker und Kabel dürfen bei Gehäusemontage nicht auf Zug belastet werden.

## 7. Steckverbinder und Kabelbaum

### 7.1 Allgemeine Anforderungen

- Für alle drahtgebundenen Außenanschlüsse ist Molex Nano-Fit oder eine schriftlich freigegebene gleichwertige verriegelnde Steckverbindung zu verwenden.
- Auf dem PCB dürfen keine AUTOTERM- oder sonstigen Fremdgeräte-Originalstecker verwendet werden. Die Anpassung an Originalstecker erfolgt ausschließlich im Kabelbaum beziehungsweise über Adapterkabel.
- PCB-Header müssen eine positive Verriegelung und eine mechanisch robuste PCB-Befestigung besitzen. THT-Anschlüsse oder SMT-Ausführungen mit ausreichenden Metallhalteklammern sind zulässig.
- Für Kleinsignale sind vergoldete Kontakte zu bevorzugen.
- Sekundärverriegelung/TPA ist zu verwenden, sofern für die gewählte Ausführung verfügbar.
- Elektrisch unterschiedliche Schnittstellen dürfen nicht mit frei vertauschbaren Gegensteckern ausgeführt werden. Unterschiedliche Polzahlen, Gehäuseformen oder echte mechanische Codierungen sind zu verwenden; Farbe oder Beschriftung allein genügen nicht.
- Die 4-poligen Anschlüsse für AUTOTERM und Taster/LED müssen mechanisch nicht miteinander steckbar sein. Falls Nano-Fit dafür keine sichere Codierung bietet, muss einer der beiden Anschlüsse eine andere Polzahl oder Bauform erhalten; unbenutzte Pins bleiben dann `NC`.
- Pin 1, Signalname und Gegensteckerorientierung sind in Schaltplan, Silkscreen und Kabelbaumzeichnung eindeutig zu kennzeichnen.
- Kabelzug wird im Gehäuse abgefangen, nicht über den PCB-Header.
- Jede Leitung, die das Gehäuse verlässt, erhält am Steckverbinder einen zur Schnittstelle passenden ESD-/Transientenschutz.

### 7.2 Verbindliche elektrische Pinbelegung

Die Nummerierung ist elektrisch verbindlich. Die mechanische Draufsicht muss in der Kabelbaumzeichnung zusätzlich dargestellt werden.

| Anschluss | Pin | Signal | Beschreibung |
|---|---:|---|---|
| J1 Versorgung, 2-polig | 1 | `BATT_12V_IN` | extern mit 1 A abgesicherter Plusleiter |
|  | 2 | `GND` | Zweitbatterie-Minus/Masse |
| J2 AUTOTERM, 4-polig | 1 | `AUTOTERM_5V` | 5-V-Versorgung/Referenz von der Heizung |
|  | 2 | `GND` | gemeinsame Signalmasse |
|  | 3 | `CTRL_TX_TO_HEATER` | Ausgang des Controllers zur Heizung |
|  | 4 | `CTRL_RX_FROM_HEATER` | Eingang des Controllers von der Heizung |
| J3 1-Wire, 3-polig | 1 | `+3V3_SENSOR` | geschaltete, strombegrenzte Sensorversorgung |
|  | 2 | `1WIRE_DQ` | gemeinsame Datenleitung der drei Sensoren |
|  | 3 | `GND` | Sensormasse |
| J4 Taster/LED, elektrisch 4-polig | 1 | `BUTTON_N` | Active-Low-Tastereingang |
|  | 2 | `GND` | Tastermasse; verdrillt mit Pin 1 |
|  | 3 | `LED_CC_PLUS` | strombegrenzter Plusleiter für weiße LED |
|  | 4 | `LED_PWM_MINUS` | PWM-fähiger Low-Side-Rückleiter; verdrillt mit Pin 3 |

Für J4 darf zur sicheren mechanischen Unterscheidung ein 5-poliges Gehäuse verwendet werden; der zusätzliche Pin bleibt unbestückt beziehungsweise `NC` und wird nicht für eine spätere Funktion reserviert.

## 8. AUTOTERM-UART

- Schnittstelle: Full-Duplex-UART mit 5-V-Logik und gemeinsamer Masse.
- Kabellänge zwischen Board und Heizung: etwa 0,3 m bis 0,5 m.
- Die Pegelwandlung muss mit `TXU0202-Q1` oder einem funktional vollständig gleichwertigen automotive-qualifizierten Bauteil erfolgen. Die beiden Kanäle müssen fest in Gegenrichtung arbeiten.
- VCCA wird aus 3,3 V versorgt; VCCB ausschließlich aus `AUTOTERM_5V`.
- Die Heizung versorgt weder das Mainboard noch externe Lasten. USB-VBUS darf `AUTOTERM_5V` nicht ersetzen.
- OE erhält einen Hardware-Pull-down. `CTRL_TX_TO_HEATER` muss bei Reset, Boot, Deep-Sleep, ausgeschaltetem VCCB und vor expliziter Softwarefreigabe hochohmig bleiben.
- Die VCC-Isolation-/Ioff-Funktion muss Rückspeisung bei fehlender Heizungsversorgung verhindern.
- Es ist keine Softwareerkennung von `AUTOTERM_5V` erforderlich. Fehlt diese Spannung, bleibt nur die 5-V-Seite des Pegelwandlers funktionslos; das restliche Board muss über 12 V oder USB normal arbeiten.
- `AUTOTERM_5V` erhält lokale Strombegrenzung, Filterung, ESD-Schutz und Abblockung.
- TX und RX erhalten angemessene Serienwiderstände und niederkapazitiven Schutz. Die Werte dürfen das UART-Timing nicht beeinträchtigen.
- Testpunkte sind auf beiden Logikseiten für TX und RX sowie für `AUTOTERM_5V`, 3,3 V und GND vorzusehen.

## 9. 1-Wire / DS18B20

- Es gibt genau einen 3-poligen 1-Wire-Anschluss am Board.
- Drei DS18B20 sind außerhalb des Boards bereits parallel auf Versorgung, Daten und GND zusammengeführt.
- Die drei Sensorleitungen sind jeweils etwa 2 m bis 5 m lang.
- Betrieb ist ausschließlich dreidrahtig mit 3,3-V-Versorgung; parasitäre Versorgung ist nicht vorgesehen.
- `1WIRE_DQ` wird direkt mit **GPIO4** des ESP32-S3 verbunden, entsprechend dem bestehenden und elektrisch geprüften Software-/Testaufbau.
- Standard-Pull-up: 4,7 kΩ von `1WIRE_DQ` nach `+3V3_SENSOR`.
- Zwischen Steckverbinder und GPIO ist ein bestückter 0-Ω-Serienwiderstand vorzusehen. Footprint und Testpunkt müssen eine spätere Anpassung zur Dämpfung ohne PCB-Änderung erlauben.
- Am Steckverbinder ist ein niederkapazitiver ESD-Schutz vorzusehen. Zusätzliche Kapazität auf DQ muss klein bleiben.
- `+3V3_SENSOR` muss im Deep-Sleep abschaltbar und gegen Kurzschluss beziehungsweise übermäßigen Kabelstrom begrenzt sein. Ein externer Kurzschluss darf `3V3_CORE` nicht zusammenbrechen lassen.
- Die bewährte gemeinsame Bus-Topologie darf in Revision A nicht durch Multiplexer oder einzeln geschaltete Sensorzweige ersetzt werden.
- Im Kabelbaum sollen `1WIRE_DQ` und GND gemeinsam geführt werden.

## 10. Display, Touch und Frontlicht

### 10.1 Verbindliches Display

- Modell: **Good Display `GDEY029T94-FT01`**, komplette werkseitig verbundene Display-/Touch-/Frontlicht-Baugruppe.
- Anzeige: 2,9 Zoll, monochrom, 296 × 128 Pixel, Treiber `SSD1680Z8`, 4-Draht-SPI.
- Außenmaß des Moduls: 79,00 mm × 36,70 mm × 2,15 mm.
- Aktive Fläche: 66,896 mm × 29,056 mm.
- Das Display wird über seine originalen FPCs direkt mit der Hauptplatine verbunden. Verlängerungskabel sind nicht zulässig.
- Es sind drei separate FPC-Steckverbinder vorzusehen: 24-polig/0,5 mm für E-Paper, 6-polig für Touch und 6-polig für Frontlicht.
- Exakte Pinfolge, Raster, Kontaktseite, Steckverbinderhöhe und FPC-Austrittsrichtung müssen aus der aktuellen Herstellerzeichnung übernommen und an einem Originalmuster geprüft werden.
- Good Display weist darauf hin, dass Touch- und Frontlicht-FPC in umgekehrter Orientierung angeschlossen werden. Diese Angabe darf nicht aus einer Produktabbildung interpretiert werden; maßgeblich sind aktuelle Zeichnung, Datenblatt und physisches Muster.
- Die Steckverbinder sind unmittelbar an den FPC-Austritten zu platzieren. Mindestbiegeradius, Entriegelungsweg und beschädigungsfreie Demontage sind im 3D-Modell nachzuweisen.

### 10.2 E-Paper-Ansteuerung

- Benötigte Signale: `EPD_SCLK`, `EPD_MOSI`, `EPD_CS_N`, `EPD_DC`, `EPD_RESET_N`, `EPD_BUSY`.
- Die SSD1680-Booster-/Ladungspumpenbeschaltung muss exakt aus der Referenzschaltung des konkret beschafften Displays übernommen werden.
- Pinfolge, Kondensatorwerte und -spannungsfestigkeiten sowie Diodentypen dürfen nicht von einem ähnlich benannten Panel übernommen werden.
- Die Displaydomäne muss im Deep-Sleep vollständig abschaltbar sein, ohne Rückspeisung über SPI/Steuersignale.
- SPI-Leitungen sind kurz über einer durchgehenden Referenzfläche zu führen. Serien-Dämpfungsfootprints sind nahe am ESP32 vorzusehen.
- Testpunkte: Displayversorgung, SCLK, MOSI, CS, RESET und BUSY.

### 10.3 Kapazitiver Touch

- Touch-Controller: `FT6336U`, Versorgung 2,8 V bis 3,6 V, I2C bis 400 kHz.
- Touch teilt SDA und SCL mit der RTC. Es darf nur ein abgestimmter Satz Bus-Pull-ups auf der dauerhaft versorgten Seite existieren.
- `TOUCH_INT_N` wird direkt auf einen Deep-Sleep-wake-fähigen RTC-GPIO des ESP32-S3 aus dem Bereich GPIO0 bis GPIO21 geführt; Strapping- und USB-Pins sind ausgeschlossen.
- `TOUCH_RESET_N` wird direkt von einem GPIO angesteuert und erhält einen definierten Hardware-Resetpegel.
- Im Komfort-Standby muss eine Berührung den ESP32 aus Deep-Sleep wecken können.
- Der Hersteller nennt 55 µA Touch-Standby-Strom. Der konkrete Modus, die INT-Polarität, die Pegelhaltezeit und das tatsächliche Aufwachverhalten müssen mit dem beschafften Display geprüft werden.
- Falls Touch-INT im vorgesehenen Standby-Modus nicht lang genug pegelaktiv bleibt, muss vor Fertigungsfreigabe ein stromarmer Wake-Latch oder eine gleichwertige zuverlässige Lösung in den Schaltplan aufgenommen werden.
- Touch muss für den Minimal-Standby abschaltbar beziehungsweise in einen vom ESP32 nicht rückgespeisten Tiefstverbrauchszustand versetzbar sein.
- Touch-Wakeup ist außerhalb des spezifizierten Betriebstemperaturbereichs der Displaybaugruppe nicht garantiert. Der externe Taster bleibt die zuverlässige Kaltstart-Wake-Quelle.

### 10.4 Frontlicht

- Das integrierte Frontlicht besitzt laut Hersteller vier parallele weiße LEDs.
- Zulässige Versorgung: 2,8 V bis 3,3 V; Gesamtstrom maximal 60 mA.
- Es ist ein strombegrenzter, PWM-fähiger Treiber vorzusehen. Ein reiner Vorwiderstand ist nur zulässig, wenn Worst-Case-Strom und Helligkeit über alle Versorgung-, Temperatur- und LED-Toleranzen nachgewiesen werden.
- Hardware-Default bei Reset, Boot und Deep-Sleep ist AUS.
- Testpunkt beziehungsweise Messmöglichkeit für den Gesamtstrom ist vorzusehen.

### 10.5 Temperaturgrenzen

- Vom Hersteller spezifizierter Displaybetrieb: **0 °C bis +50 °C**.
- Vom Hersteller spezifizierte Displaylagerung: **−25 °C bis +70 °C**.
- Displayaktualisierungen außerhalb 0 °C bis +50 °C sind softwareseitig zu sperren. Bei −15 °C wird keine Aktualisierung erwartet; Bedienung bleibt über Taster und WLAN möglich.
- Das E-Paper darf seinen letzten Bildinhalt ohne Versorgung behalten.

## 11. Externer Taster und weiße Ring-LED

- Vorgesehenes Tastermodell: APEM AV, Bestellcode **`AV970220000700`** gemäß den bislang gewählten Optionen: 19-mm-Buchse, weiße LED ohne eingebauten Vorwiderstand, Silberkontakte, Lötanschlüsse, opalweißer Ring, vernickeltes Messing, ohne IP67-Zusatz `K`.
- Der Bestellcode ist vor Bestellung durch APEM oder den autorisierten Distributor gegen den dann aktuellen Bestellschlüssel zu bestätigen.
- Verwendet wird der Schließerkontakt (NO). Ein vorhandener NC-Kontakt bleibt im Kabelbaum isoliert und unbeschaltet.
- Kabellänge zwischen Taster und Board: etwa **3 m**, vieradrig.
- Paar 1: `BUTTON_N` mit GND. Paar 2: `LED_CC_PLUS` mit `LED_PWM_MINUS`. Verdrillte Paare sind zu verwenden.
- `BUTTON_N` ist Active-Low und wird direkt auf einen Deep-Sleep-wake-fähigen RTC-GPIO geführt.
- Der Eingang erhält am PCB-Stecker ESD-Schutz, Serienwiderstand, externen Pull-up und ein angemessenes RC-Filter. Die Filterung darf zuverlässiges Aufwachen nicht verhindern.
- Die Taster-LED besitzt keinen eingebauten Vorwiderstand und darf nicht direkt von einem GPIO oder unstrombegrenzt aus 3,3 V/12 V gespeist werden.
- Zielnennstrom der weißen LED: etwa **10 mA**, auf jeden Fall unterhalb der vom Tasterhersteller zulässigen 20 mA.
- Die Helligkeit wird durch ESP32-PWM über einen Low-Side-MOSFET geregelt.
- `LED_CC_PLUS` wird aus `VIN_SYS` über eine für 5-V- und 12-V-Eingang geeignete Strombegrenzung gespeist.
- Ein Hardware-Pull-down am Gate stellt AUS bei Reset, Boot und Deep-Sleep sicher.
- Die PWM-Führung und Filterung muss Einkopplung in den parallelen Tastereingang vermeiden.

## 12. RTC und Backup-Batterie

- RTC: **Micro Crystal `RV-3028-C7`** am gemeinsamen 3,3-V-I2C-Bus.
- Backupquelle: austauschbare **BR1225**-Lithium-Primärzelle in einem vibrationsfesten, auf dem Board montierten Halter.
- Der Halter muss verpolungssicher beziehungsweise eindeutig markiert und im geöffneten Gehäuse austauschbar sein.
- Die RTC muss bei fehlender 12-V- und USB-Versorgung mindestens vier Wochen weiterlaufen. Dies ist durch Worst-Case-Stromrechnung und Messung des Backupstroms nachzuweisen.
- Die interne Trickle-Charge-Funktion bleibt deaktiviert.
- Eine niederleckende hardwareseitige Sperre muss das Laden der Primärzelle auch bei fehlerhafter Softwarekonfiguration verhindern.
- Der RTC-Interrupt darf zu einem Testpunkt und einem freien RTC-GPIO geführt werden. RTC-Alarm ist jedoch keine geforderte Wake-Funktion von Revision A und kein Abnahmekriterium.
- Die bestehende Software verwendet teilweise einen DS3231-Adapter. Die Umstellung auf RV-3028 ist eine Softwareaufgabe; eine elektrische DS3231-Kompatibilität ist nicht gefordert.

## 13. Status-LEDs

- Auf dem Board sind genau vier einzeln steuerbare **rote** Status-LEDs vorzusehen.
- Jede LED erhält eine eigene Strombegrenzung.
- Direktansteuerung oder ein stromarmer Treiber sind zulässig; die vier Funktionen dürfen nicht von einem I2C-Portexpander abhängig gemacht werden.
- Hardware-Default bei Reset, Boot und Deep-Sleep ist AUS.
- Es gibt keine dauerhaft leuchtende Power-LED.
- Die LEDs müssen im montierten Zustand sichtbar sein oder über definierte Lichtleiterpositionen verfügen; dies wird beim Platzierungsreview festgelegt.

## 14. GPIO- und Bussystemregeln

- I2C wird gemeinsam von RV-3028 und FT6336U genutzt.
- E-Paper verwendet eine eigene SPI-Schnittstelle beziehungsweise einen eindeutig zugeordneten SPI-Bus ohne lange externe Leitungen.
- AUTOTERM verwendet eine Hardware-UART ungleich UART0; Signale dürfen über die ESP32-GPIO-Matrix auf geeignete Pins gelegt werden.
- 1-Wire ist fest GPIO4 zugeordnet.
- Taster und Touch-INT müssen direkte ESP32-Wake-Eingänge sein und dürfen nicht über Portexpander geführt werden.
- Rail-Enables, Pegelwandler-OE, LED-Treiber und sonstige Ausgänge erhalten externe Pull-ups/-downs für einen sicheren Zustand vor Firmwareinitialisierung.
- Ein I2C-Portexpander ist für Revision A nicht vorgesehen. Falls der PCB-Designer wider Erwarten einen benötigt, ist dies vor Schaltplan-Freeze mit vollständiger Pinbilanz, Ruhestromauswirkung und Resetverhalten zur Freigabe vorzulegen.
- Die Pin-Matrix muss mindestens Signalname, GPIO, Ein-/Ausgang, Resetpegel, externen Pull-Widerstand, Deep-Sleep-Zustand, Wake-Fähigkeit und Versorgungsdomäne enthalten.

## 15. Leiterplattenaufbau und Layoutregeln

### 15.1 Stackup und Basisspezifikation

- Verbindlich ist ein **vierlagiges PCB**.
- Erste Fertigungsmenge: **fünf vollständig bestückte Prototypen über PCBWay**.
- Nominale Dicke: 1,6 mm, sofern FPC- oder Gehäusemechanik keine dokumentierte Abweichung verlangt.
- FR-4 mit Tg mindestens 150 °C.
- Kupfer: mindestens 1 oz auf Außenlagen; Innenlagen nach bestätigtem PCBWay-Stackup.
- Oberflächenfinish: ENIG oder eine gleichwertige, für feine FPC-Pads und Lagerung geeignete Oberfläche.
- Standard-Durchkontaktierungen; keine Blind-/Buried-Vias.
- Via-in-Pad nur, wenn vom Hersteller zwingend gefordert und von PCBWay gefüllt/verschlossen ausgeführt.
- Der konkrete impedanzkontrollierte Stackup ist vor dem Routing von PCBWay zu bestätigen.

Empfohlene Lagenbelegung:

- L1: Bauteile, USB und kritische Signale.
- L2: durchgehende, ungeteilte GND-Referenzfläche; keine Signale.
- L3: Versorgungsflächen und wenige langsame Signale; keine Zerschneidung kritischer Rückstrompfade.
- L4: Bauteile, langsame Signale und möglichst zusammenhängende GND-Flächen.

### 15.2 Verbindliche Layoutregeln

- USB D+/D− als 90-Ω-Differenzpaar über durchgehender Referenzfläche, kurz, ohne Stubs und nach aktuellem Espressif-/USB-Layoutleitfaden.
- Keine Signalleitung darf einen Spalt ihrer Referenzfläche kreuzen.
- Abblockkondensatoren unmittelbar an den zugehörigen Versorgungspins mit sehr kurzem GND-Rückweg.
- Hot-Loop des Buck-Reglers minimieren und Hersteller-Referenzlayout übernehmen.
- Schaltknoten klein halten und von Touch, RTC, Antennenkoax, 1-Wire und USB fernhalten.
- GND-Stitching-Vias an Kanten, bei Lagenwechseln und um störende Leistungsbereiche vorsehen.
- Strompfade, Kupferbreiten und Via-Anzahl sind für Worst-Case-Strom und zulässigen Temperaturanstieg zu berechnen.
- ESD-/TVS-Bauteile direkt am jeweiligen Stecker platzieren; der Ableitpfad nach GND muss kurz und niederinduktiv sein.
- FPC-, WROOM-, QFN- und sonstige kritische Footprints müssen gegen die aktuelle Herstellerzeichnung unabhängig geprüft werden.
- Das offizielle Espressif-WROOM-1U-Landpattern einschließlich Thermal-Pad/Via-Vorgaben ist unverändert zu verwenden.
- Für das WROOM-1U-Modul gelten die Espressif-Platzierungsregeln. Trotz externer Antenne sind Koaxstecker, Modul und umgebendes Metall/Gehäuse mechanisch und HF-gerecht anzuordnen.
- Testpads dürfen keine ungewollten Stubs an USB oder anderen schnellen Signalen erzeugen.
- Bauteile sollen, sofern funktional und platzmäßig möglich, mindestens 0603 besitzen. Kleinere Bauformen und Spezialgehäuse sind zulässig, wenn sie für die Funktion oder den Bauraum nötig sind.
- Silkscreen muss Steckerbezeichnungen, Pin 1, Polaritäten, Batteriepolung, BOOT/RESET, PCB-Revision und alle Testpunkte eindeutig kennzeichnen.
- Die vollständige Predictable-Designs-Checkliste ist beim Layoutreview Punkt für Punkt abzuarbeiten und als ausgefülltes Reviewprotokoll abzugeben.

## 16. Sichere Hardware-Defaultzustände

Ohne laufende Firmware sowie während Reset, Boot und Deep-Sleep gelten zwingend:

| Funktion | Hardwarezustand |
|---|---|
| AUTOTERM-TX | hochohmig |
| UART-Pegelwandler OE | LOW / deaktiviert |
| E-Paper-Versorgung | aus |
| Frontlicht | aus |
| externe weiße Taster-LED | aus |
| vier rote Status-LEDs | aus |
| DS18B20-Sensorversorgung | aus |
| Tastereingang | definiert HIGH, Active-Low-wake-fähig |
| Touch-INT | definierter Pegel, im Komfort-Standby wake-fähig |
| USB-/12-V-Pfade | gegenseitig rückstromgesperrt |

Diese Zustände müssen durch Hardware-Pull-ups/-downs und Power-Off-Isolation entstehen, nicht allein durch Software.

## 17. Testpunkte und Design-for-Test

Mindestens folgende Netze benötigen zugängliche, beschriftete Testpunkte:

- `BATT_12V_IN`, geschützter 12-V-Pfad, `VIN_SYS`, `3V3_CORE`, alle geschalteten 3,3-V-Domänen und GND,
- USB D+/D− nur als messgerechte Pads ohne problematischen Stub,
- `CHIP_PU`, GPIO0/BOOT, U0TXD, U0RXD,
- AUTOTERM TX/RX auf 3,3-V- und 5-V-Seite, OE und `AUTOTERM_5V`,
- `1WIRE_DQ`,
- I2C SDA/SCL, Touch-INT, Touch-RESET und RTC-INT,
- E-Paper SCLK, MOSI, CS, RESET und BUSY,
- Frontlichtstrom sowie PWM-Signale der beiden Beleuchtungen.

Testpunkte müssen im bestückten, geöffneten Gerät zugänglich sein. Ein zusammenhängendes GND-Testpad für Oszilloskop-Masse ist in der Nähe der Leistungs- und Kommunikationsbereiche vorzusehen.

## 18. Prüf- und Abnahmekriterien für fünf Prototypen

Vor Bestellung müssen ERC und DRC ohne ungeklärte Fehler abgeschlossen sein. Für die Prototypen sind mindestens folgende Prüfungen zu dokumentieren:

1. Sichtprüfung, Polarität, Bestückung und Kurzschlusstest aller Versorgungsschienen.
2. Start und stabiler Betrieb bei 10 V, 12 V und 14 V Eingang.
3. USB-only-Betrieb ohne 12 V; Flashen und native USB-Kommunikation funktionieren.
4. Gleichzeitiger Anschluss von 12 V und USB ohne Rückspeisung in USB, Fahrzeugkreis oder AUTOTERM-Port.
5. Verpoltest am 12-V-Eingang gemäß Abschnitt 5.1 ohne Schaden.
6. Lastsprungtest mit aktivem WLAN ohne Brownout; 3,3 V bleibt innerhalb 3,0 V bis 3,6 V.
7. Gemessener Komfort-Standby-Strom kleiner 0,5 mA bei 12 V.
8. Wiederholtes Aufwachen aus Deep-Sleep durch externen Taster und durch Touch.
9. Hardware-Defaultzustände aus Abschnitt 16 bei Power-up, Reset und Deep-Sleep.
10. UART-Kommunikation mit angeschlossener AUTOTERM-Heizung; bei fehlendem `AUTOTERM_5V` keine Rückspeisung und hochohmiger Heizungs-TX.
11. Zuverlässiger gleichzeitiger Betrieb aller drei DS18B20 mit dem realen 2-bis-5-m-Kabelbaum.
12. Display-Voll- und Teilaktualisierung, BUSY/RESET, Touch und PWM-Frontlicht bei Raumtemperatur.
13. Dimmbereich und Maximalstrom der weißen externen Taster-LED.
14. RTC-Betrieb über I2C, Umschaltung auf BR1225, Backupstrommessung und rechnerischer Nachweis von mindestens vier Wochen Pufferzeit.

EMV-Vorzertifizierung ist für Revision A nicht zwingend, aber Nahfeldprüfung und Kontrolle des Buck-Schaltknotens, der USB-Verbindung, der 1-Wire-Leitung und der 3-m-PWM-/Tasterleitung werden dringend empfohlen.

## 19. Vom PCB-Designer zu liefernde Unterlagen

- editierbare native Schaltplan- und PCB-Quelldaten einschließlich vollständiger Bibliothek beziehungsweise eingebetteter Symbole/Footprints,
- Schaltplan als PDF,
- vollständige Pin-Matrix des ESP32-S3,
- Stückliste mit Hersteller, vollständiger MPN, Wert, Gehäuse, Toleranz, Spannungs-/Temperaturrating und PCBWay/LCSC-Artikelnummer soweit verfügbar,
- Gerber-/ODB++-Daten, NC-Drill, Pick-and-Place/CPL und Bestückungszeichnungen für beide Seiten,
- Fertigungszeichnung mit Stackup, Impedanzvorgaben, Leiterplattenkontur, Bohrungen und Toleranzen,
- 3D-STEP-Modell des vollständig bestückten Boards einschließlich Display, Steckverbinder, Batterie und ESP32-Antennenstecker,
- Kabelbaumzeichnungen für J1 bis J4 mit Ansicht der Steckseite, Pinfarben, Leiterquerschnitten und Gegenstecker-MPNs,
- Strom-, Verlustleistungs- und Ruhestrombudget,
- Berechnung des 12-V-Eingangsschutzes und der TVS-Klemmung,
- ausgefüllte ERC-, DRC-, Espressif- und Predictable-Designs-Reviewchecklisten,
- Testplan, Testpunktplan und dokumentierte Messergebnisse der fünf Prototypen,
- Änderungs-/Abweichungsliste gegenüber diesem Dokument.

Bauteilalternativen dürfen nicht nur anhand gleicher Nennwerte ersetzt werden. Footprint, Pinout, Einschaltzustand, Leckstrom, Temperaturbereich und Verfügbarkeit sind mitzuprüfen.

## 20. Verifikationspunkte vor Fertigungsfreigabe

Diese Punkte blockieren nicht den Beginn von Schaltplan und Platzierung, müssen aber vor der Fertigungsfreigabe abgeschlossen sein:

1. Originalmuster des `GDEY029T94-FT01` beschaffen; alle drei FPCs, Kontaktseiten und Biegeradien gegen Zeichnung und Footprints prüfen.
2. Touch-Standbymodus, INT-Polarität/-Pegelhaltezeit und Deep-Sleep-Wakeup messen; gegebenenfalls Wake-Latch bestücken.
3. Exakte Nano-Fit-Header, Gegenstecker, Kontakte und sichere Nichtvertauschbarkeit von J2/J4 festlegen.
4. APEM-Bestellcode `AV970220000700` durch Hersteller/Distributor bestätigen.
5. TVS, Verpolschutz-MOSFETs, Filter und `LMR43620-Q1` einschließlich aller Worst-Case-Spannungen und thermischen Reserven berechnen.
6. Mechanische Platzierung im 98-mm-×-48-mm-Zielumriss als 3D-Modell prüfen; USB, Antennenkoax, Knopfzelle, BOOT/RESET und alle Verriegelungen müssen erreichbar sein.
7. ESP32-Pin-Matrix und alle sicheren Reset-/Deep-Sleep-Zustände reviewen.
8. PCBWay-Stackup, Impedanzregeln, Bauteilverfügbarkeit und beidseitige Bestückbarkeit für fünf Stück bestätigen.

Es bestehen keine weiteren offenen Funktionsentscheidungen des Auftraggebers. Änderungen an Funktionsumfang, Versorgung, Display, Schnittstellen oder Mechanik bedürfen einer neuen Dokumentrevision.

## 21. Spätere Revisionen – nicht Teil des Auftrags

Für eine spätere Revision sind vorgemerkt:

- VOTRONIC `VBCS 45/30/350 Triple CI`,
- VOTRONIC `Smart-Shunt 100 A`.

Vor deren Integration müssen Original-Pinbelegung, elektrische Pegel, Busversorgung, Halb-/Vollduplex, Terminierung, galvanische Trennung und Protokoll belastbar verifiziert werden. Die bisherige Annahme „Standard-RS-485“ genügt nicht als Schaltungsgrundlage. Beide Geräte dürfen nicht ohne Nachweis auf denselben Bus gelegt werden.

## 22. Referenzen

- [LandyHeater Repository](https://github.com/fabianhartmann2/LandyHeater/tree/main)
- [Espressif ESP32-S3-WROOM-1/1U Datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [Espressif ESP32-S3 Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html)
- [Espressif ESP32-S3 PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html)
- [Predictable Designs PCB Layout Rules Checklist](https://predictabledesigns.com/pcb-layout-rules-checklist.pdf)
- [TI LMR43620-Q1](https://www.ti.com/product/LMR43620-Q1)
- [TI LM74502-Q1](https://www.ti.com/product/LM74502-Q1)
- [TI TXU0202-Q1](https://www.ti.com/product/TXU0202-Q1)
- [Micro Crystal RV-3028-C7](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7)
- [Panasonic BR1225A](https://energy.panasonic.com/na/business/products/lithium/coin-br-high-temp/models/BR1225A)
- [Molex Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors)
- [APEM AV Illuminated Pushbuttons](https://www.apem.com/api/asset/en/fbCPLUNNnaEJPS7JlAtdy/pusbutton-switches-serie-AV.pdf)
- [Good Display GDEY029T94-FT01](https://www.good-display.com/product/616.html)
- [Analog Devices – Guidelines for Reliable Long-Line 1-Wire Networks](https://www.analog.com/en/resources/technical-articles/guidelines-for-reliable-long-line-1wire-networks.html)
