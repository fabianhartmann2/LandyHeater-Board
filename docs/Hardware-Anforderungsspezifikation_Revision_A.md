# Landy Heater Controller – Hardware-Anforderungsspezifikation Revision A

Dokumentversion: 1.3

Stand: 2026-09-06

Status: freigegeben als Grundlage für Schaltplan, PCB-Layout und Angebotserstellung; noch keine Fertigungsfreigabe

Änderungsstand 1.3: Systemprüfung nach Integration der Espressif-, Good-Display- und FocalTech-Herstellerangaben. GPIO45- und WROOM-1U-Keep-out-Aussagen korrigiert, USB-C-Stromfreigabe konkretisiert, Touch-/I2C-Spannungsdomäne und Deep-Sleep-Resetzustand eindeutig festgelegt, sichere E-Paper-Signalzustände ergänzt und Status-LEDs bei GPIO-Mangel als verzichtbare Komfortfunktion eingestuft.

Änderungsstand 1.2: Anforderungen der Herstellerunterlagen `GDEY029T94-FT01` Revision 1.0 und `FT6336U` Datasheet Version 1.0 für FPC-Pinout, E-Paper-Referenzschaltung, SPI-Timing, Touch-Betriebsarten, Reset-/Power-Sequenz und Frontlicht konkretisiert. Insbesondere ist Touch-Wakeup nur im FT6336U-Monitor-Modus, nicht im 55-µA-Hibernation-Modus, gefordert.

Änderungsstand 1.1: Anforderungen aus dem Espressif-Datenblatt v1.8 und den aktuellen ESP32-S3 Hardware Design Guidelines für Versorgung, Reset/Boot, USB, GPIO, Layout, Antenne und Fertigung konkretisiert.

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
- Für uneingeschränkten USB-Betrieb ist eine 5-V-USB-C-Quelle erforderlich, die über CC mindestens **1,5 A** ankündigt. Die Auslegung des Boards darf davon höchstens 1 A verwenden.
- Das Board arbeitet als USB-2.0-Gerät/Sink ohne USB-PD.
- CC1 und CC2 erhalten jeweils eine normgerechte Rd-Terminierung. Diese darf durch separate Widerstände oder durch die nachgewiesen normgerechte interne Terminierung des gewählten Type-C-Sink-Controllers realisiert werden; eine Doppelterminierung ist unzulässig.
- Eine USB-Type-C-Sink-/Stromankündigungserkennung ohne USB-PD oder eine vollständig gleichwertige Lösung muss die über CC angebotene Stromstufe auswerten. Bei lediglich angekündigtem USB-Default-Current muss natives USB-Flashing zuverlässig möglich sein; Frontlicht, Sensorversorgung und andere nicht notwendige Lasten sind hardware- oder firmwaregestützt so zu sperren beziehungsweise zu begrenzen, dass die zulässige Stromaufnahme einschließlich Einschaltstrom nicht überschritten wird.
- Das Ergebnis der CC-Stromerkennung muss dem ESP32 zur Verfügung stehen oder die Lastbegrenzung muss unabhängig vom ESP32 hardwareseitig erfolgen. Ruhestrom, Startverhalten ohne laufende Firmware und GPIO-Bedarf der gewählten Lösung sind zu dokumentieren.
- USB-VBUS und D+/D− erhalten geeigneten ESD-Schutz; die VBUS-Eingangskapazität muss USB-konform sein.
- In D− und D+ ist jeweils unmittelbar am ESP32-Modul ein bestückbarer Serienwiderstand vorzusehen. Anfangswert: 22 Ω oder 33 Ω gemäß Espressif; der endgültige Wert wird nach Signalintegritätsprüfung festgelegt.
- Hinter den Serienwiderständen ist je Leitung ein optionaler, standardmäßig nicht bestückter Kondensator-Footprint nach GND vorzusehen. ESD-Schutz und optionale Kondensatoren müssen so kapazitätsarm gewählt werden, dass das USB-Full-Speed-Signal nicht unzulässig belastet wird.
- USB-Testpads sind nur zulässig, wenn sie ohne relevante Stichleitung in den Hauptpfad integriert werden.
- 12 V dürfen unter keinen Betriebs- oder Fehlerbedingungen auf USB-VBUS gelangen.
- USB-VBUS darf nicht in den 12-V-Fahrzeugkreis oder in `AUTOTERM_5V` zurückspeisen.

### 5.3 Power-OR und 3,3-V-Hauptversorgung

Die verbindliche Funktionskette lautet:

`J1 B+ -> Verpol-/Transientenschutz -> Filter -> ideal entkoppelter 12-V-Pfad -> VIN_SYS`

`USB-C 5 V -> Strom-/Rückstromschutz -> ideal entkoppelter USB-Pfad -> VIN_SYS`

`VIN_SYS -> Low-IQ-Buck 3,3 V / 2 A -> 3V3_CORE`

`3V3_CORE -> Low-IQ-LDO nominal 3,0 V -> 3V0_TOUCH_AON`

- Bei gleichzeitigem Anschluss von 12 V und USB muss der 12-V-Pfad Vorrang haben.
- Beide Quellen müssen gegeneinander rückstromgesperrt sein.
- Der 3,3-V-Regler wird mit dem automotive-qualifizierten `LMR43620-Q1`, 3,3-V-/2-A-Ausführung, realisiert. Die genaue bestellbare Variante und Schaltfrequenz werden anhand von Wirkungsgrad, EMI und PCBWay-Verfügbarkeit festgelegt und in der BOM genannt.
- Auto-/PFM-Leichtlastbetrieb muss möglich sein. Ein dauerhaft erzwungener FPWM-Modus ist wegen des Ruhestromziels nicht zulässig.
- Referenzschaltung, Bauteilberechnung, Hot-Loop und Layout des Herstellers sind einzuhalten.
- `3V3_CORE` muss bei zulässigen Quellen und Lastsprüngen zwischen 3,0 V und 3,6 V bleiben. Wi-Fi-Sendespitzen dürfen keinen Brownout oder unbeabsichtigten Reset verursachen.
- Die 3,3-V-Versorgung muss am ESP32-Modul mindestens 0,5 A liefern können. Der festgelegte 2-A-Regler erfüllt diese Mindestanforderung mit Reserve für Wi-Fi-Sendespitzen und Peripherie.
- Direkt am 3,3-V-Pin des WROOM-1U sind mindestens **22 µF plus 100 nF** gemäß Espressif-Peripherieschaltung vorzusehen. Leiterwege zu Modul und GND müssen kurz und niederinduktiv sein.
- Bei der 22-µF-Kapazität sind DC-Bias, Temperatur, Alterung und Bauteiltoleranz zu berücksichtigen. Die effektive Kapazität bei 3,3 V muss im Designbericht dokumentiert werden.
- Am Eintritt von `3V3_CORE` in den ESP32-Bereich ist zusätzlich mindestens 10 µF wirksame Bulk-Kapazität vorzusehen, sofern diese Funktion nicht bereits nachweislich durch die vorgenannten 22 µF erfüllt wird.
- Die Spannung am Modul darf den absoluten Bereich −0,3 V bis 3,6 V niemals überschreiten; der normale Betrieb bleibt auf 3,0 V bis 3,6 V begrenzt.

### 5.4 Versorgungsdomänen

Folgende Netze sind getrennt und eindeutig zu benennen:

- `3V3_CORE`: ESP32, RV-3028-Hauptversorgung und dauerhaft benötigte 3,3-V-Logik. Die I2C-Pull-ups liegen nicht an diesem Netz.
- `3V0_TOUCH_AON`: separate, rauscharme und ruhestromarme nominelle 3,0-V-Versorgung für FT6336U und den gemeinsamen I2C-Bus. Am Touch-FPC muss sie unter allen Regler-, Last- und Temperaturtoleranzen zwischen 2,8 V und 3,3 V bleiben. Die I2C-Pull-ups werden ausschließlich an dieses Netz angeschlossen. ESP32- und RV-3028-Eingangspegel müssen bei den Worst-Case-Spannungen nachweislich kompatibel sein. Normalbetrieb, Komfort-Standby und Minimal-Standby nutzen diese Versorgung; im Minimal-Standby wird der FT6336U in Hibernation versetzt. Vollständiges Abschalten ist nur mit Power-off-Isolation aller Touch-Signale und Einhaltung der Reset-/Power-Sequenz aus Abschnitt 10.3 zulässig.
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
| Komfort-Standby | ESP32 Deep-Sleep, WLAN aus | aus | FT6336U Monitor-Modus für Touch-Wakeup | aus |
| Minimal-Standby | ESP32 Deep-Sleep, WLAN aus | aus | FT6336U Hibernation oder vollständig isoliert abgeschaltet; kein Touch-Wakeup | aus |

- Wake-Quellen im Komfort-Standby sind der externe Taster und Touch-INT.
- Im Minimal-Standby ist mindestens der externe Taster als Wake-Quelle verfügbar.
- Der typische Strom des FT6336U beträgt laut Datenblatt bei 2,8 V und 25 °C etwa 220 µA im Monitor-Modus und 55 µA im Sleep-/Hibernation-Modus. Diese Werte sind typische Werte ohne garantierte Obergrenze und dürfen nicht ohne Reserve als Worst-Case-Budget verwendet werden.
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
- GPIO0 erhält einen externen 10-kΩ-Pull-up nach 3,3 V und den BOOT-Taster nach GND. An GPIO0 darf kein großer Kondensator vorgesehen werden.
- Beim N16R8 ist VDD_SPI für das integrierte PSRAM werkseitig per eFuse auf 3,3 V festgelegt; der GPIO45-Pegel beeinflusst VDD_SPI bei dieser Modulvariante nicht. GPIO45 bleibt dennoch wegen seiner Strapping-Funktion unbenutzt und erhält keinen externen Pull-up. Auch GPIO46 darf keinen externen Pull-up erhalten und muss für den gemeinsamen USB-/UART-Download-Boot LOW bleiben können.
- Die Strapping-Pegel müssen mindestens 3 ms nach dem Anstieg von `CHIP_PU/EN` unverändert gültig bleiben.
- eFuses für VDD_SPI, Bootmodus, ROM-Ausgabe, USB-JTAG oder JTAG dürfen während Fertigung und Prototypentest nicht programmiert werden, sofern dies nicht ausdrücklich dokumentiert und freigegeben wurde.
- GPIO47 und GPIO48 sollen frei bleiben, solange dadurch kein anderer Designnachteil entsteht.
- Alle übrigen Pinzuordnungen sind vor Schaltplan-Freeze in einer Pin-Matrix mit Resetpegel, Pull-up/-down, Wake-Fähigkeit, Versorgungsdomäne und bekanntem Einschaltimpuls zu dokumentieren.
- Es wird natives ESP32-S3-USB für Flashen, REPL und Diagnose verwendet.
- Ein lokaler, beschrifteter `RESET`-Taster muss `CHIP_PU/EN` gegen GND ziehen.
- Ein lokaler, beschrifteter `BOOT`-Taster muss GPIO0 gegen GND ziehen.
- `CHIP_PU/EN` darf nicht floaten. Als Ausgangspunkt sind 10 kΩ Pull-up nach 3,3 V und 1 µF nach GND gemäß Espressif vorzusehen.
- Vor dem Anstieg von `CHIP_PU/EN` müssen die 3,3-V-Modulversorgung und die internen Versorgungsschienen mindestens 50 µs stabil sein. Ein Hardware-Reset muss EN mindestens 50 µs unter dem zulässigen LOW-Pegel halten.
- Wegen Fahrzeugversorgung, vorgeschaltetem Relais und Umschaltung zwischen USB und 12 V muss ein Low-IQ-Spannungswächter oder eine gleichwertige PGOOD-qualifizierte Resetlösung vorgesehen werden. Ein reines RC-Netzwerk ist nur zulässig, wenn sein sicheres Verhalten bei langsamem Spannungsanstieg/-abfall, Brownout, Prellen des Versorgungsrelais und Quellenwechsel per Worst-Case-Analyse nachgewiesen wird.
- U0TXD/U0RXD sowie GND und 3,3 V sollen als beschriftete Testpads erreichbar sein, dürfen aber keinen zusätzlichen Außenstecker erfordern. U0TXD erhält nahe am Modul den von Espressif empfohlenen 499-Ω-Serienwiderstand.
- Das Modul wird über seinen integrierten U.FL-/MHF-I-kompatiblen Antennenanschluss mit einer externen 2,4-GHz-/50-Ω-WLAN-Antenne und etwa 10 cm Koaxialkabel verbunden.
- Der Antennengewinn darf 2,33 dBi nicht überschreiten, sofern nicht eine gesonderte regulatorische/EMV-Bewertung eine andere Antenne freigibt.
- Auf dem Mainboard wird keine HF-Leitung zwischen Modul und Antenne geroutet.
- Die Antenne muss bei aktivem Funk angeschlossen sein. Koaxstecker und Kabel dürfen bei Gehäusemontage nicht auf Zug belastet werden.
- Antennenreichweite und Datendurchsatz müssen mit der tatsächlichen Antenne, dem 10-cm-Koaxkabel, dem finalen Gehäuse und am vorgesehenen Einbauort geprüft werden.

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
| J3 1-Wire, 3-polig | 1 | `3V3_SENSOR_SW` | geschaltete, strombegrenzte Sensorversorgung |
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
- Standard-Pull-up: 4,7 kΩ von `1WIRE_DQ` nach `3V3_SENSOR_SW`.
- Zwischen Steckverbinder und GPIO ist ein bestückter 0-Ω-Serienwiderstand vorzusehen. Footprint und Testpunkt müssen eine spätere Anpassung zur Dämpfung ohne PCB-Änderung erlauben.
- Am Steckverbinder ist ein niederkapazitiver ESD-Schutz vorzusehen. Zusätzliche Kapazität auf DQ muss klein bleiben.
- `3V3_SENSOR_SW` muss im Deep-Sleep abschaltbar und gegen Kurzschluss beziehungsweise übermäßigen Kabelstrom begrenzt sein. Ein externer Kurzschluss darf `3V3_CORE` nicht zusammenbrechen lassen.
- Die bewährte gemeinsame Bus-Topologie darf in Revision A nicht durch Multiplexer oder einzeln geschaltete Sensorzweige ersetzt werden.
- Im Kabelbaum sollen `1WIRE_DQ` und GND gemeinsam geführt werden.

## 10. Display, Touch und Frontlicht

### 10.1 Verbindliches Display

- Modell: **Good Display `GDEY029T94-FT01`**, komplette werkseitig verbundene Display-/Touch-/Frontlicht-Baugruppe.
- Normative Herstellerunterlagen für diesen Abschnitt sind die [Good-Display-Spezifikation `GDEY029T94-FT01`, Revision 1.0](https://v4.cecdn.yun300.cn/100001_1909185148/GDEY029T94-FT01.pdf) und das darin referenzierte [FocalTech-Datenblatt `FT6336U`, Version 1.0](https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf). Verwendet wurde der von Good Display am 18.11.2025 bereitgestellte Stand der Display-Spezifikation. Bei einer neueren Dokumentrevision ist vor Übernahme eine Änderungsprüfung erforderlich.
- Anzeige: 2,9 Zoll, monochrom, 296 × 128 Pixel, Treiber `SSD1680Z8`, 4-Draht-SPI.
- Außenmaß des Moduls: 79,00 mm × 36,70 mm × 2,15 mm.
- Aktive Fläche: 66,896 mm × 29,056 mm.
- Das Display wird über seine originalen FPCs direkt mit der Hauptplatine verbunden. Verlängerungskabel sind nicht zulässig.
- Es sind drei separate FPC-Steckverbinder vorzusehen: 24-polig/0,5 mm für E-Paper, 6-polig/0,5 mm für Touch und 6-polig/0,5 mm für Frontlicht. Die Herstellerzeichnung nennt für alle drei FPC-Enden 0,30 mm ± 0,03 mm Dicke.
- Exakte Pinfolge, Raster und Kontaktseite werden verbindlich aus der aktuellen Herstellerzeichnung übernommen. Steckverbinderhöhe, FPC-Austrittsrichtung und mechanische Passung werden im 3D-Modell festgelegt. Ein Originalmuster dient vor Fertigungsfreigabe als unabhängige Kontrolle von Footprint, Kontaktseite und Mechanik, ist aber keine Voraussetzung für den Beginn des Schaltplanentwurfs.
- Good Display weist darauf hin, dass Touch- und Frontlicht-FPC in umgekehrter Orientierung angeschlossen werden. Diese Angabe darf nicht aus einer Produktabbildung interpretiert werden; maßgeblich sind aktuelle Zeichnung, Datenblatt und physisches Muster.
- Die Steckverbinder sind unmittelbar an den FPC-Austritten zu platzieren. Mindestbiegeradius, Entriegelungsweg und beschädigungsfreie Demontage sind im 3D-Modell nachzuweisen.
- Die Pin-1-Ansicht der Herstellerzeichnung darf im Footprint nicht gespiegelt werden. Schaltplan, PCB-Footprint, 3D-Modell und Bestückungszeichnung müssen dieselbe Kontaktseitenansicht verwenden.

### 10.2 E-Paper-Ansteuerung

- Benötigte MCU-Signale: `EPD_SCLK`, `EPD_SDIO/MOSI`, `EPD_CS_N`, `EPD_DC`, `EPD_RESET_N`, `EPD_BUSY`. Es gibt keine separate MISO-Leitung; FPC-Pin 14 ist im Lesebetrieb bidirektional.
- Der 24-polige E-Paper-FPC wird elektrisch wie folgt belegt:

| Pin | Herstellername | Verbindliche Beschaltung |
|---:|---|---|
| 1 | `NC` | offen lassen; nicht mit Pin 4 verbinden |
| 2 | `GDR` | Gate des externen Booster-MOSFET gemäß Referenzschaltung |
| 3 | `RESE` | Strommess-/Regelpfad mit 2,2 Ω und 1 MΩ gemäß Referenzschaltung |
| 4 | `NC` | offen lassen; nicht mit Pin 1 verbinden |
| 5 | `VSH2` | 1 µF/25 V nach GND gemäß Referenzschaltung |
| 6 | `TSCL` | unbenutzte I2C-Masterschnittstelle für einen externen digitalen Temperatursensor; offen lassen |
| 7 | `TSDA` | unbenutzte I2C-Masterschnittstelle für einen externen digitalen Temperatursensor; offen lassen |
| 8 | `BS1` | fest LOW/GND für 4-Draht-SPI |
| 9 | `BUSY` | `EPD_BUSY` zum ESP32; HIGH bedeutet beschäftigt |
| 10 | `RES#` | `EPD_RESET_N` zum ESP32; active LOW |
| 11 | `D/C#` | `EPD_DC`; LOW = Befehl, HIGH = Daten |
| 12 | `CS#` | `EPD_CS_N`; active LOW |
| 13 | `SCL` | `EPD_SCLK` |
| 14 | `SDA` | `EPD_SDIO/MOSI` |
| 15 | `VDDIO` | mit FPC-Pin 16/`VCI` an `3V3_DISPLAY_SW` |
| 16 | `VCI` | `3V3_DISPLAY_SW` |
| 17 | `VSS` | GND |
| 18 | `VDD` | 1 µF/25 V nach GND gemäß Referenzschaltung; nicht extern speisen |
| 19 | `VPP` | Testpin; offen lassen |
| 20 | `VSH1` | Booster-Kondensatornetz gemäß Referenzschaltung |
| 21 | `VGH` | Booster-Kondensatornetz `PREVGH` gemäß Referenzschaltung |
| 22 | `VSL` | Booster-Kondensatornetz gemäß Referenzschaltung |
| 23 | `VGL` | Booster-Kondensatornetz `PREVGL` gemäß Referenzschaltung |
| 24 | `VCOM` | Booster-Kondensatornetz gemäß Referenzschaltung |

- `VCI` und `VDDIO` haben laut Display-Spezifikation einen Betriebsbereich von 2,2 V bis 3,7 V; beide werden gemeinsam aus `3V3_DISPLAY_SW` gespeist. Die absoluten 4,0-V- beziehungsweise E/A-Grenzen dürfen auch bei Einschalt- und Abschaltvorgängen nicht verletzt werden.
- Die SSD1680-Booster-/Ladungspumpenbeschaltung muss exakt aus Kapitel 12 der oben verlinkten Spezifikation des konkret beschafften `GDEY029T94-FT01` übernommen werden. Pinfolge, Bauteilwerte, Polaritäten und Spannungsfestigkeiten dürfen nicht von einem ähnlich benannten Panel übernommen werden.
- Die Referenzschaltung fordert insbesondere eine 47-µH-Induktivität mit 500-mA-Eignung, drei `MBR0530`-Dioden oder vollständig gleichwertige Typen, einen `Si1308EDL`-MOSFET oder vollständig gleichwertigen Typ, 1 MΩ und 2,2 Ω mit 1 % sowie X5R-/X7R-Kondensatoren in 0603/0805 mit mindestens 25 V. Gleichwertigkeit ist gegen alle in der Hersteller-Tabelle genannten Grenzwerte nachzuweisen.
- Der Booster-Hot-Loop, `GDR`, `RESE`, Induktivität, MOSFET, Dioden und zugehörige Kondensatoren sind kompakt und abseits von Touch, RTC, USB und Antennenkoax zu platzieren. Die Hochspannungsnetze dürfen nicht unter Touch-FPC oder Touch-Sensorfläche geführt werden.
- Im Schreibbetrieb darf `EPD_SCLK` 20 MHz nicht überschreiten. Falls die bidirektionale Lesefunktion verwendet wird, darf der Lesetakt 2,5 MHz nicht überschreiten. Die Daten werden beim Schreiben an der steigenden SCLK-Flanke übernommen.
- Solange `EPD_BUSY` HIGH ist, dürfen keine neuen Befehle gesendet und keine laufenden Displayoperationen unterbrochen werden.
- Die Displaydomäne muss im Deep-Sleep vollständig abschaltbar sein, ohne Rückspeisung über SPI/Steuersignale.
- Bei abgeschalteter `3V3_DISPLAY_SW` müssen alle MCU-Signale zum E-Paper hochohmig beziehungsweise nicht rückspeisend sein oder durch Bauteile mit nachgewiesener Power-off-Isolation getrennt werden.
- Sobald `3V3_DISPLAY_SW` eingeschaltet ist, aber bevor die Firmware den Displaycontroller initialisiert, gelten folgende sichere Pegel: `EPD_CS_N` HIGH/inaktiv, `EPD_RESET_N` LOW/Reset aktiv sowie `EPD_SCLK`, `EPD_SDIO/MOSI` und `EPD_DC` LOW. Pull-Widerstände und gegebenenfalls Isolation sind auf der jeweils versorgten Seite anzuordnen, sodass diese Zustände auch bei ESP32-Reset entstehen.
- SPI-Leitungen sind kurz über einer durchgehenden Referenzfläche zu führen. Serien-Dämpfungsfootprints sind nahe am ESP32 vorzusehen.
- Testpunkte: Displayversorgung, SCLK, SDIO/MOSI, CS, D/C, RESET und BUSY.

### 10.3 Kapazitiver Touch

- Touch-Controller: `FT6336U`. Der spezifizierte Betriebsbereich für VDDA/VDD3 beträgt 2,8 V bis 3,3 V; 3,6 V ist nur die absolute Maximalgrenze und kein freigegebener Dauerbetriebswert. `3V0_TOUCH_AON` muss am FPC unter allen Toleranzen innerhalb 2,8 V bis 3,3 V bleiben.
- Der 6-polige Touch-FPC wird gemäß Herstellerzeichnung belegt: Pin 1 `GND`, Pin 2 `TOUCH_INT_N`, Pin 3 `TOUCH_RESET_N`, Pin 4 `3V0_TOUCH_AON`, Pin 5 `I2C_SCL`, Pin 6 `I2C_SDA`.
- I2C darf gemäß FT6336U-Datenblatt zwischen 10 kHz und 400 kHz betrieben werden.
- Touch teilt SDA und SCL mit der RTC. Es darf nur ein abgestimmter Satz Bus-Pull-ups auf der dauerhaft versorgten Seite existieren.
- Pull-up-Spannung, ESP32-Eingangspegel, RV-3028-Eingangspegel und die am integrierten Touch-FPC nicht separat herausgeführte IOVCC-Versorgung müssen zueinander kompatibel sein. Keine Touch-Leitung darf die aktuelle `3V0_TOUCH_AON`-Versorgung übersteigen oder den unversorgten Controller über Schutzdioden speisen.
- `TOUCH_INT_N` wird direkt auf einen Deep-Sleep-wake-fähigen RTC-GPIO des ESP32-S3 aus dem Bereich GPIO0 bis GPIO21 geführt; Strapping- und USB-Pins sind ausgeschlossen.
- Das FocalTech-Datenblatt bezeichnet das Signal als `/INT`; `TOUCH_INT_N` wird deshalb als active LOW ausgelegt. Das Datenblatt garantiert in der vorliegenden Fassung jedoch weder Ausgangstopologie noch minimale LOW-Pulsdauer. Der Schaltplan muss einen Serienwiderstand und bestückbare schwache Pull-up-/Pull-down-Optionen vorsehen; ein Open-Drain-Ausgang darf nicht ungeprüft angenommen werden.
- `TOUCH_RESET_N` wird über eine zu `3V0_TOUCH_AON` pegelkompatible Ansteuerung mit definiertem Einschaltzustand geführt. Vor und während des Einschaltens bleibt Reset hardwareseitig LOW. Nach der softwaregesteuerten Freigabe wird `TOUCH_RESET_N` ausschließlich auf `3V0_TOUCH_AON` hochgezogen beziehungsweise pegelbegrenzt; ein direkter 3,3-V-Push-Pull-HIGH-Pegel ist ohne Worst-Case-Nachweis nicht zulässig.
- Im Komfort-Standby muss `TOUCH_RESET_N` während des gesamten ESP32-Deep-Sleep zuverlässig HIGH bleiben, damit der FT6336U im Monitor-Modus weiterarbeitet. Wird dafür ESP32-Pad-Hold verwendet, sind die notwendigen Funktionen `gpio_hold_en()` und `gpio_deep_sleep_hold_en()` beziehungsweise deren aktuelle ESP-IDF-Entsprechungen, der Zustand beim Eintritt und Aufwachen sowie das Verhalten bei Reset am Prototyp nachzuweisen. Alternativ ist eine stromarme Hardware-Halteschaltung zulässig.
- Die Touch-seitigen INT-, SDA- und SCL-Pins dürfen vor anliegender `3V0_TOUCH_AON` nicht HIGH getrieben werden; bei unabhängigem Einschalten oder vollständigem Abschalten der Touch-Domäne ist dies durch Power-off-Isolation sicherzustellen.
- Im Komfort-Standby muss der FT6336U im **Monitor-Modus** bleiben. In diesem Modus scannt er laut Datenblatt standardmäßig mit 25 Bildern/s, erkennt eine Berührung, wechselt in den Active-Modus und kann über `/INT` den ESP32 wecken. Der typische Strom beträgt 220 µA bei 2,8 V und 25 °C.
- Der im Datenblatt mit typisch 55 µA angegebene Sleep-/Hibernation-Modus reagiert nur auf ein hostseitiges RESET-/Wakeup-Signal. Eine Berührung weckt ihn nicht. Dieser Modus ist deshalb nur für den Minimal-Standby ohne Touch-Wakeup zulässig; nach Taster-Wakeup des ESP32 wird der Touch-Controller hostseitig aufgeweckt beziehungsweise zurückgesetzt.
- Falls Touch-INT im vorgesehenen Standby-Modus nicht lang genug pegelaktiv bleibt, muss vor Fertigungsfreigabe ein stromarmer Wake-Latch oder eine gleichwertige zuverlässige Lösung in den Schaltplan aufgenommen werden.
- Bei jedem Power-on des FT6336U muss die Versorgung von 0,1 VDD auf 0,9 VDD in höchstens 3 ms ansteigen. `TOUCH_RESET_N` bleibt nach Power-on mindestens 1 ms LOW. Nach Freigabe von Reset sind mindestens 300 ms bis zum ersten I2C-Zugriff beziehungsweise zuverlässigen Touch-Report einzuplanen.
- Ein Resetimpuls muss mindestens 5 ms LOW dauern; danach sind wiederum mindestens 300 ms bis zur Kommunikation einzuplanen.
- Für einen vollständigen Power-Cycle muss `3V0_TOUCH_AON` unter 0,3 V fallen und dort mindestens 5 ms verbleiben. Während abgeschalteter Touch-Versorgung müssen SDA, SCL, INT und RESET durch Power-off-Isolation oder gleichwertige Schaltung gegen Rückspeisung gesperrt sein.
- Da der Touch-Controller während seiner Start-/Resetsequenz den gemeinsamen I2C-Bus vorübergehend LOW halten kann, darf die Hardware keine RTC-Transaktion in dieser Phase voraussetzen. Die Firmware darf frühestens 300 ms nach Resetfreigabe auf den Touch zugreifen; die tatsächliche Zeit bis zur Busfreigabe ist am Muster zu messen, weil das Datenblatt dafür keinen Maximalwert nennt.
- Normal- und Monitorstrom, Hibernationstrom, INT-Polarität/-Pulsdauer, Wake-Zuverlässigkeit und das Verhalten am gemeinsamen I2C-Bus müssen am beschafften Display gemessen werden.
- Touch-Wakeup ist außerhalb des spezifizierten Betriebstemperaturbereichs der Displaybaugruppe nicht garantiert. Der externe Taster bleibt die zuverlässige Kaltstart-Wake-Quelle.

### 10.4 Frontlicht

- Das integrierte Frontlicht besitzt laut Hersteller vier intern parallel geschaltete weiße LED-Dies. Die Herstellerzeichnung nennt eine Durchlassspannung von 2,75 V minimal, 2,9 V typisch und 3,0 V maximal sowie einen Gesamtstrom von 60 mA. Diese Spannungswerte sind LED-Durchlassspannungen und kein zulässiger Versorgungsspannungsbereich.
- Der 6-polige Frontlicht-FPC wird belegt: Pins 1 und 2 gemeinsam `FRONTLIGHT_LED_PLUS`, Pins 3 und 4 offen/`NC`, Pins 5 und 6 gemeinsam `FRONTLIGHT_LED_MINUS`. Beide Plus- und beide Minuskontakte sind mit kurzen, symmetrischen Leiterwegen anzuschließen; die NC-Pins dürfen nicht verbunden werden.
- Es ist ein stromgeregelter, PWM-fähiger Treiber mit Hardware-Abschaltung vorzusehen. Der Gesamtstrom aller vier LED-Dies darf unter keiner Kombination aus Versorgung, Temperatur, Bauteiltoleranz und PWM-Zustand 60 mA überschreiten. Der Sollstrom muss über einen BOM-Wert anpassbar sein.
- Versorgung und Treibertopologie müssen bei 3,0 V maximaler LED-Durchlassspannung und minimaler speisender Spannung noch ausreichend Regelreserve besitzen. Eine verlustreiche lineare Speisung direkt aus dem bis 14 V reichenden `VIN_SYS` ist nicht zulässig.
- Hardware-Default bei Reset, Boot und Deep-Sleep ist AUS.
- Testpunkt beziehungsweise Messmöglichkeit für den Gesamtstrom ist vorzusehen.

### 10.5 Temperaturgrenzen

- Vom Hersteller spezifizierter Displaybetrieb: **0 °C bis +50 °C**.
- Vom Hersteller spezifizierte Displaylagerung: **−25 °C bis +70 °C**.
- Displayaktualisierungen außerhalb 0 °C bis +50 °C sind softwareseitig zu sperren. Bei −15 °C wird keine Aktualisierung erwartet; Bedienung bleibt über Taster und WLAN möglich.
- Das E-Paper darf seinen letzten Bildinhalt ohne Versorgung behalten.
- Nach höchstens fünf aufeinanderfolgenden Fast- oder Partial-Refresh-Vorgängen ist laut Hersteller ein Full Refresh vorzusehen, um Artefaktansammlung zu reduzieren. Dies ist eine dokumentierte Firmwareabhängigkeit.

### 10.6 Handhabung und mechanischer Schutz

- Die drei FPC-Verbindungen dürfen nicht bei versorgtem E-Paper, Touch oder Frontlicht gesteckt oder getrennt werden.
- Das Gehäuse darf keinen punktuellen Druck auf das E-Paper ausüben. Displayauflage, Toleranzen und Befestigung müssen thermische Ausdehnung ohne Verspannung zulassen.
- Die ungeschützten FPC-/Bondingbereiche dürfen weder als Griff- noch als Klemmfläche verwendet werden und sind gegen Kontakt mit Gehäusekanten zu schützen.

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

- RTC: **Micro Crystal `RV-3028-C7`** mit Hauptversorgung aus `3V3_CORE` am gemeinsamen I2C-Bus. Die Bus-Pull-ups liegen gemäß Abschnitt 5.4 an `3V0_TOUCH_AON`.
- Backupquelle: austauschbare **BR1225**-Lithium-Primärzelle in einem vibrationsfesten, auf dem Board montierten Halter.
- Der Halter muss verpolungssicher beziehungsweise eindeutig markiert und im geöffneten Gehäuse austauschbar sein.
- Die RTC muss bei fehlender 12-V- und USB-Versorgung mindestens vier Wochen weiterlaufen. Dies ist durch Worst-Case-Stromrechnung und Messung des Backupstroms nachzuweisen.
- Die interne Trickle-Charge-Funktion bleibt deaktiviert.
- Eine niederleckende hardwareseitige Sperre muss das Laden der Primärzelle auch bei fehlerhafter Softwarekonfiguration verhindern.
- Der RTC-Interrupt darf zu einem Testpunkt und einem freien RTC-GPIO geführt werden. RTC-Alarm ist jedoch keine geforderte Wake-Funktion von Revision A und kein Abnahmekriterium.
- Die bestehende Software verwendet teilweise einen DS3231-Adapter. Die Umstellung auf RV-3028 ist eine Softwareaufgabe; eine elektrische DS3231-Kompatibilität ist nicht gefordert.

## 13. Optionale Status-LEDs

- Vier einzeln steuerbare **rote** Status-LEDs sind als gemeinsamer Funktionsblock gewünscht, aber optional und kein Abnahmekriterium. Revision A wird entweder mit allen vier LEDs oder ohne Status-LEDs ausgeführt; eine Teilbestückung ist nicht vorgesehen.
- Funktionale Schnittstellen, beide Wake-Eingänge, sichere Rail-/Reset-Steuerungen, natives USB und die geforderten Diagnosemöglichkeiten haben bei der GPIO-Zuteilung Vorrang. Zeigt die vollständige Pin-Matrix nicht genügend geeignete GPIOs, werden die vier Status-LEDs vollständig weggelassen; hierfür darf kein I2C-Portexpander ergänzt und keine sicherheits- oder diagnosebezogene Funktion eingeschränkt werden.
- Werden die vier LEDs umgesetzt, erhält jede eine eigene Strombegrenzung. Direktansteuerung oder ein stromarmer Treiber sind zulässig; die Funktionen dürfen nicht von einem I2C-Portexpander abhängig gemacht werden.
- Hardware-Default bei Reset, Boot und Deep-Sleep ist AUS.
- Es gibt keine dauerhaft leuchtende Power-LED.
- Umgesetzte LEDs müssen im montierten Zustand sichtbar sein oder über definierte Lichtleiterpositionen verfügen; dies wird beim Platzierungsreview festgelegt.

## 14. GPIO- und Bussystemregeln

- I2C wird gemeinsam von RV-3028 und FT6336U genutzt.
- E-Paper verwendet eine eigene SPI-Schnittstelle beziehungsweise einen eindeutig zugeordneten SPI-Bus ohne lange externe Leitungen.
- AUTOTERM verwendet eine Hardware-UART ungleich UART0; Signale dürfen über die ESP32-GPIO-Matrix auf geeignete Pins gelegt werden.
- 1-Wire ist fest GPIO4 zugeordnet.
- Taster und Touch-INT müssen direkte ESP32-Wake-Eingänge sein und dürfen nicht über Portexpander geführt werden.
- Die vollständige Pin-Matrix wird vor Auswahl beziehungsweise Freigabe der optionalen Status-LEDs erstellt. GPIO47/48, U0TXD/U0RXD, Wake-Fähigkeit und sichere Einschaltzustände sind ausdrücklich in die Bilanz aufzunehmen.
- Rail-Enables, Pegelwandler-OE, LED-Treiber und sonstige Ausgänge erhalten externe Pull-ups/-downs für einen sicheren Zustand vor Firmwareinitialisierung.
- Die Pinplanung muss die von Espressif dokumentierten Einschaltimpulse berücksichtigen. GPIO1 bis GPIO17 können beim Einschalten etwa 60 µs LOW sein; GPIO18 kann LOW- und HIGH-Impulse zeigen. GPIO18 darf deshalb nicht für ein ungefiltertes Active-High-Enable einer externen Last verwendet werden.
- Unbenutzte GPIOs dürfen nicht dauerhaft floaten. Sie erhalten einen geeigneten externen Pull-Widerstand oder werden nach dem Booten per Firmware mit einem internen Pull definiert. Strapping-Pins dürfen dadurch nicht verändert werden.
- Jeder externe GPIO-Pfad muss durch Pegelwandlung, Serienimpedanz und Schutzbeschaltung sicherstellen, dass am Modul kein Pin unter −0,3 V oder über `VDD33 + 0,3 V` beaufschlagt wird. Eingangs- und Ausgangsstromgrenzen des Moduls sind einzuhalten.
- Ein I2C-Portexpander ist für Revision A nicht vorgesehen. Falls der PCB-Designer wider Erwarten einen benötigt, ist dies vor Schaltplan-Freeze mit vollständiger Pinbilanz, Ruhestromauswirkung und Resetverhalten zur Freigabe vorzulegen.
- Die Pin-Matrix muss mindestens Signalname, GPIO, Ein-/Ausgang, Resetpegel, externen Pull-Widerstand, Power-up-Glitch, Deep-Sleep-Zustand, Wake-Fähigkeit und Versorgungsdomäne enthalten.

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

- L1 ist für dieses Projekt die Elektronik-/Anschlussseite auf der Rückseite der Einheit; L4 ist die Display-/Bedienseite.
- L1: ESP32-S3-WROOM-1U, USB, weitere Bauteile und kritische Signale.
- L2: durchgehende, ungeteilte GND-Referenzfläche; keine Signale.
- L3: Versorgungsflächen und wenige langsame Signale; keine Zerschneidung kritischer Rückstrompfade.
- L4: Bauteile, langsame Signale und möglichst zusammenhängende GND-Flächen.

Espressif empfiehlt für den generischen vierlagigen Aufbau keine Bauteile auf L4. Die wegen Display und Bauraum erforderliche beidseitige Bestückung ist hier eine dokumentierte mechanische Abweichung. Auf L4 sind deshalb nur störungsarme Bauteile zulässig; unter WROOM-1U, USB, Buck-Hot-Loop und kritischen Rückstrompfaden bleibt L4 frei.

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
- Das offizielle Espressif-WROOM-1U-Landpattern einschließlich Copper-Pads, GND-Pads, EPAD und Via-Geometrie ist unverändert zu verwenden. Das Landpattern des längeren WROOM-1-Moduls darf nicht verwendet werden.
- Die beiden seitlichen GND-Pads des Moduls sind mit kurzen, breiten Verbindungen und mehreren Vias an die L2-GND-Fläche anzubinden. Das EPAD-Copper und seine Thermal-/Ground-Vias sind ebenfalls mit GND zu verbinden.
- Ob das zentrale EPAD verlötet wird, ist im Fertigungsdatensatz ausdrücklich festzulegen. Bei verlötetem EPAD muss die Pastenöffnung so begrenzt werden, dass das Modul nicht angehoben wird und sämtliche seitlichen Pads zuverlässig verlötet werden.
- Das ESP32-S3-WROOM-1U und USB müssen auf L1 unmittelbar über der durchgehenden L2-GND-Fläche liegen. Eine Platzierung des Moduls auf L4 ist nur zulässig, wenn der Stackup gespiegelt wird und die unmittelbar benachbarte Innenlage eine ungeteilte GND-Fläche bildet.
- Im WROOM-Bereich dürfen auf der gegenüberliegenden PCB-Seite keine Schaltregler, Induktivitäten oder schnellen Signale angeordnet werden. Die Rückstromfläche unter den digitalen Modulanschlüssen muss zusammenhängend bleiben.
- Das WROOM-1U besitzt laut Espressif keine Antennen-Keep-out-Zone auf dem Basis-PCB. Es darf daher kein vom WROOM-1-Modul mit PCB-Antenne übernommener Kupfer-Keep-out verwendet werden. Das offizielle WROOM-1U-Landpattern bleibt unverändert; über und um den U.FL-/MHF-I-Stecker ist mechanischer Freiraum für Gegenstecker, Koaxkabel und zulässigen Biegeradius vorzusehen. Modul, Koaxkabel und umgebendes Metall/Gehäuse sind mechanisch und HF-gerecht anzuordnen.
- Am E-Paper-SPI-Takt ist nahe am ESP32 ein bestückbarer Serienwiderstand oder Ferrit sowie ein optionaler, zunächst unbestückter Kondensator nach GND vorzusehen. Entsprechende Dämpfungsfootprints sollen, sofern der Platz reicht, auch für die übrigen SPI-Signale vorgesehen werden.
- Booster-MOSFET, 47-µH-Induktivität, drei Dioden und Hochspannungs-Kondensatoren des E-Papers sind unmittelbar am 24-poligen FPC-Stecker gemäß Good-Display-Referenzschaltung zu gruppieren. Booster-Schleifen und -Kupferflächen sind zu minimieren und von Touch-FPC, I2C, RTC, USB und Antennenkoax fernzuhalten.
- Die FPC-Steckerbereiche müssen mechanische Keep-outs für Verriegelungsbetätigung, FPC-Einschub und Biegeradius enthalten. Unter den drei FPC-Zungen dürfen keine scharfkantigen Vias, Bauteile oder freiliegenden Kupferkanten liegen.
- Testpads dürfen keine ungewollten Stubs an USB oder anderen schnellen Signalen erzeugen.
- Bauteile sollen, sofern funktional und platzmäßig möglich, mindestens 0603 besitzen. Kleinere Bauformen und Spezialgehäuse sind zulässig, wenn sie für die Funktion oder den Bauraum nötig sind.
- Silkscreen muss Steckerbezeichnungen, Pin 1, Polaritäten, Batteriepolung, BOOT/RESET, PCB-Revision und alle Testpunkte eindeutig kennzeichnen.
- Die vollständige Predictable-Designs-Checkliste ist beim Layoutreview Punkt für Punkt abzuarbeiten und als ausgefülltes Reviewprotokoll abzugeben.

### 15.3 Fertigung und Handhabung des ESP32-Moduls

- Das `ESP32-S3-WROOM-1U-N16R8` ist ein MSL-3-Bauteil.
- Nach Öffnung des Moisture-Barrier-Bags muss das Modul innerhalb von 168 Stunden bei 25 ± 5 °C und höchstens 60 % relativer Feuchte verlötet werden. Bei Überschreitung ist es nach Espressif-Vorgabe zu trocknen beziehungsweise zu backen.
- Das ESP32-Modul darf nur **einen Reflow-Zyklus** durchlaufen.
- Bei doppelseitiger Reflow-Bestückung darf das Modul deshalb erst für den zweiten/finalen Reflow bestückt werden. Eine andere Prozessfolge ist nur mit einem dokumentierten Verfahren zulässig, das ebenfalls genau einen Reflow des Moduls sicherstellt.
- Das aktuelle Espressif-Reflowprofil und bleifreies SAC305 sind einzuhalten; PCBWay muss die Prozessfolge vor Produktionsfreigabe bestätigen.
- Das bestückte Modul darf keiner Ultraschallreinigung und keiner Ultraschallschweißung ausgesetzt werden.

## 16. Sichere Hardware-Defaultzustände

Ohne laufende Firmware sowie während Reset, Boot und Deep-Sleep gelten zwingend:

| Funktion | Hardwarezustand |
|---|---|
| AUTOTERM-TX | hochohmig |
| UART-Pegelwandler OE | LOW / deaktiviert |
| E-Paper-Versorgung | aus |
| Frontlicht | aus |
| externe weiße Taster-LED | aus |
| optionale rote Status-LEDs, sofern umgesetzt | aus |
| DS18B20-Sensorversorgung | aus |
| Tastereingang | definiert HIGH, Active-Low-wake-fähig |
| Touch-INT | im Komfort-Standby durch versorgten FT6336U-Monitor-Modus definiert und active-LOW-wake-fähig; im Minimal-Standby keine Touch-Wake-Anforderung |
| Touch-RESET | bei Power-up/ESP32-Reset LOW; nach Freigabe im Normalbetrieb und während Komfort-Standby HIGH an `3V0_TOUCH_AON` |
| E-Paper-Signale | bei ausgeschalteter Displaydomäne hochohmig/nicht rückspeisend; bei eingeschalteter Domäne vor Initialisierung CS HIGH, RESET LOW, SCLK/SDIO/D/C LOW |
| USB-/12-V-Pfade | gegenseitig rückstromgesperrt |

Die sicheren Power-up-, Reset- und Power-off-Zustände müssen durch Hardware-Pull-ups/-downs und Power-Off-Isolation entstehen, nicht allein durch Software. Ein nach expliziter Softwarefreigabe absichtlich gehaltener Betriebszustand während Deep-Sleep, insbesondere `TOUCH_RESET_N` HIGH im Komfort-Standby, darf die dokumentierte ESP32-Pad-Hold-Funktion verwenden und muss nach Abschnitt 18 verifiziert werden.

## 17. Testpunkte und Design-for-Test

Mindestens folgende Netze benötigen zugängliche, beschriftete Testpunkte:

- `BATT_12V_IN`, geschützter 12-V-Pfad, `VIN_SYS`, `3V3_CORE`, `3V0_TOUCH_AON`, alle geschalteten 3,3-V-Domänen und GND,
- USB D+/D− nur als messgerechte Pads ohne problematischen Stub,
- `CHIP_PU`, GPIO0/BOOT, U0TXD, U0RXD,
- AUTOTERM TX/RX auf 3,3-V- und 5-V-Seite, OE und `AUTOTERM_5V`,
- `1WIRE_DQ`,
- I2C SDA/SCL, Touch-INT, Touch-RESET und RTC-INT,
- E-Paper SCLK, SDIO/MOSI, CS, D/C, RESET und BUSY,
- Frontlichtstrom sowie PWM-Signale der beiden Beleuchtungen.

Testpunkte müssen im bestückten, geöffneten Gerät zugänglich sein. Ein zusammenhängendes GND-Testpad für Oszilloskop-Masse ist in der Nähe der Leistungs- und Kommunikationsbereiche vorzusehen.

## 18. Prüf- und Abnahmekriterien für fünf Prototypen

Vor Bestellung müssen ERC und DRC ohne ungeklärte Fehler abgeschlossen sein. Für die Prototypen sind mindestens folgende Prüfungen zu dokumentieren:

1. Sichtprüfung, Polarität, Bestückung und Kurzschlusstest aller Versorgungsschienen.
2. Start und stabiler Betrieb bei 10 V, 12 V und 14 V Eingang.
3. USB-only-Betrieb ohne 12 V: Flashen und native USB-Kommunikation funktionieren bei USB-Default-Current. Uneingeschränkter Betrieb wird nur bei erkannter CC-Ankündigung von mindestens 1,5 A freigegeben; die gemessene Boardaufnahme bleibt in beiden Fällen innerhalb der jeweils erlaubten Grenze.
4. Gleichzeitiger Anschluss von 12 V und USB ohne Rückspeisung in USB, Fahrzeugkreis oder AUTOTERM-Port.
5. Verpoltest am 12-V-Eingang gemäß Abschnitt 5.1 ohne Schaden.
6. Lastsprungtest mit aktivem WLAN ohne Brownout; 3,3 V bleibt innerhalb 3,0 V bis 3,6 V.
7. Gemessener Komfort-Standby-Strom kleiner 0,5 mA bei 12 V.
8. Wiederholtes Aufwachen aus Deep-Sleep durch externen Taster sowie durch Touch im FT6336U-Monitor-Modus. `TOUCH_RESET_N` bleibt während des gesamten Komfort-Standby HIGH. Im Hibernation-Modus darf Touch nicht als Wake-Quelle gewertet werden.
9. Hardware-Defaultzustände aus Abschnitt 16 bei Power-up, Reset und Deep-Sleep.
10. UART-Kommunikation mit angeschlossener AUTOTERM-Heizung; bei fehlendem `AUTOTERM_5V` keine Rückspeisung und hochohmiger Heizungs-TX.
11. Zuverlässiger gleichzeitiger Betrieb aller drei DS18B20 mit dem realen 2-bis-5-m-Kabelbaum.
12. Display-Voll-, Fast- und Teilaktualisierung, `BUSY`-HIGH-Verhalten, Reset, SPI-Schreibbetrieb bis zur freigegebenen Taktgrenze sowie Full Refresh nach fünf Fast-/Partial-Zyklen bei Raumtemperatur.
13. Dimmbereich und Maximalstrom der weißen externen Taster-LED.
14. RTC-Betrieb über I2C, Umschaltung auf BR1225, Backupstrommessung und rechnerischer Nachweis von mindestens vier Wochen Pufferzeit.
15. Oszilloskopprüfung von `3V3_CORE` und `CHIP_PU/EN` bei 12-V-Einschalten/-Ausschalten, USB-Einschalten/-Ausschalten, Quellenwechsel, Brownout und schnell wiederkehrender Versorgung.
16. Manueller Recovery-Test: BOOT gedrückt halten, RESET auslösen und erfolgreichen USB-Download-Boot nachweisen; GPIO46 bleibt dabei LOW.
17. Prüfung aller extern wirksamen Enable-, TX- und LED-Ausgänge während Power-up, Reset und den dokumentierten GPIO-Einschaltimpulsen.
18. WLAN-Reichweiten- und Durchsatztest im finalen Gehäuse am vorgesehenen Einbauort.
19. Durchgangs- und Pin-1-Prüfung aller drei nach Herstellerzeichnung erstellten Display-FPC-Verbindungen gegen das Originalmuster; insbesondere darf keine gespiegelte Kontaktseitenzuordnung vorliegen.
20. Touch-Prüfung bei Power-on, Reset und Deep-Sleep: Spannung und Anstiegszeit von `3V0_TOUCH_AON`, Worst-Case-I2C-HIGH-Pegel an ESP32/RV-3028/FT6336U, Reset-LOW-Zeiten, `TOUCH_RESET_N`-Haltezustand, 300-ms-Initialisierungszeit, I2C-Busfreigabe, INT-Polarität/-Pulsdauer sowie Stromaufnahme in Active-, Monitor- und Hibernation-Modus.
21. Falls Touch vollständig abschaltbar ausgeführt wird: Nachweis von unter 0,3 V für mindestens 5 ms, fehlender Rückspeisung über SDA/SCL/INT/RESET und erfolgreicher Wiederinbetriebnahme.
22. Frontlichtmessung über den gesamten PWM-Bereich; der Worst-Case-Gesamtstrom bleibt unter 60 mA und der Treiber besitzt bei maximaler LED-Durchlassspannung ausreichende Regelreserve.

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
2. `3V0_TOUCH_AON`, FT6336U-Monitor-, Hibernation- und optionalen Power-off-Zustand, `TOUCH_RESET_N`-Hold, INT-Polarität/-Pegelhaltezeit, gemeinsamen I2C-Bus und Deep-Sleep-Wakeup messen; gegebenenfalls Wake-Latch beziehungsweise Power-off-Isolation bestücken.
3. 24-/6-/6-polige FPC-Footprints und komplette E-Paper-Booster-Beschaltung gegen Kapitel 4, 5 und 12 der verlinkten `GDEY029T94-FT01`-Spezifikation unabhängig prüfen.
4. Exakte Nano-Fit-Header, Gegenstecker, Kontakte und sichere Nichtvertauschbarkeit von J2/J4 festlegen.
5. APEM-Bestellcode `AV970220000700` durch Hersteller/Distributor bestätigen.
6. TVS, Verpolschutz-MOSFETs, Filter und `LMR43620-Q1` einschließlich aller Worst-Case-Spannungen und thermischen Reserven berechnen.
7. Mechanische Platzierung im 98-mm-×-48-mm-Zielumriss als 3D-Modell prüfen; USB, Antennenkoax, Knopfzelle, BOOT/RESET und alle Verriegelungen müssen erreichbar sein.
8. ESP32-Pin-Matrix und alle sicheren Reset-/Deep-Sleep-Zustände reviewen. Reichen geeignete GPIOs nicht aus, sind die optionalen Status-LEDs gemäß Abschnitt 13 vollständig zu entfernen.
9. EN-/Resetlösung gegen langsame, unterbrochene und wechselnde Versorgung analysieren; Supervisor beziehungsweise PGOOD-Lösung festlegen.
10. PCBWay-Stackup, Impedanzregeln, Bauteilverfügbarkeit und beidseitige Bestückbarkeit für fünf Stück bestätigen.
11. PCBWay-Prozessfolge so bestätigen, dass das WROOM-1U trotz beidseitiger Bestückung genau einen Reflow-Zyklus durchläuft und die MSL-3-Handhabung eingehalten wird.

Es bestehen keine weiteren offenen Funktionsentscheidungen des Auftraggebers. Die in diesem Abschnitt genannten Bauteil-, Schaltungs-, GPIO- und Layoutentscheidungen des PCB-Designers bleiben bis zu ihrer dokumentierten Verifikation offen. Änderungen am vorgegebenen Funktionsumfang, an Versorgung, Display, Schnittstellen oder Mechanik bedürfen einer neuen Dokumentrevision.

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
- [Espressif ESP32-S3 Sleep Modes und EXT1-Wakeup](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html)
- [USB-IF USB Type-C Specification Release 2.0](https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf)
- [Predictable Designs PCB Layout Rules Checklist](https://predictabledesigns.com/pcb-layout-rules-checklist.pdf)
- [TI LMR43620-Q1](https://www.ti.com/product/LMR43620-Q1)
- [TI LM74502-Q1](https://www.ti.com/product/LM74502-Q1)
- [TI TXU0202-Q1](https://www.ti.com/product/TXU0202-Q1)
- [Micro Crystal RV-3028-C7](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7)
- [Panasonic BR1225A](https://energy.panasonic.com/na/business/products/lithium/coin-br-high-temp/models/BR1225A)
- [Molex Nano-Fit](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/nano-fit-connectors)
- [APEM AV Illuminated Pushbuttons](https://www.apem.com/api/asset/en/fbCPLUNNnaEJPS7JlAtdy/pusbutton-switches-serie-AV.pdf)
- [Good Display GDEY029T94-FT01](https://www.good-display.com/product/616.html)
- [Good Display GDEY029T94-FT01 Specification, Revision 1.0](https://v4.cecdn.yun300.cn/100001_1909185148/GDEY029T94-FT01.pdf)
- [FocalTech FT6336U Self-Capacitive Touch Panel Controller Datasheet, Version 1.0](https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf)
- [Analog Devices – Guidelines for Reliable Long-Line 1-Wire Networks](https://www.analog.com/en/resources/technical-articles/guidelines-for-reliable-long-line-1wire-networks.html)
