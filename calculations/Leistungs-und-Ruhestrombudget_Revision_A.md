# Leistungs-, USB- und Ruhestrombudget – Revision A

Stand: 2026-09-06

Status: Phase-1-Auslegung; in Phase 2 mit den finalen Passivwerten und in Phase 6 durch Messung zu bestätigen

## 1. Ziele

- `3V3_CORE` muss ESP32-WLAN-Spitzen und alle vorgesehenen Nebenlasten ohne Brownout versorgen.
- Die USB-eFuse und das Board begrenzen den USB-Betrieb auf höchstens 1 A.
- Bei USB-Default-Current muss natives USB-Flashing innerhalb 500 mA möglich sein.
- Der Komfort-Standby soll am 12-V-Eingang weniger als 0,5 mA aufnehmen.
- Die BR1225 muss die RTC ohne externe Versorgung mindestens vier Wochen betreiben.

Alle Werte in diesem Dokument sind Engineering-Budgets, keine gemessenen Produkteigenschaften. Typische Datenblattwerte werden ausdrücklich nicht als garantierte Maximalwerte ausgegeben.

## 2. Lastbudget im Normalbetrieb

| Verbrauchergruppe | Versorgung | Auslegungsstrom | Grundlage |
|---|---:|---:|---|
| ESP32-S3-WROOM-1U, WLAN-Spitzen | 3,3 V | 500 mA | Espressif-Mindestdimensionierung der Modulversorgung; konservatives Boardbudget |
| E-Paper-Logik und Booster aus geschalteter Rail | 3,3 V | 50 mA | Designreserve; am Muster messen |
| FT6336U aktiv | 3,0 V | 10 mA | oberhalb 4,32 mA typ. laut Datenblatt |
| drei DS18B20 + Kabelbus | 3,3 V | 10 mA | drei Wandlungen plus Reserve |
| RTC, Supervisor, Pegelwandler, Isolation, Pulls | 3,0/3,3 V | 10 mA äquivalent | Sammelreserve |
| Diagnose-/Status-LEDs bei DIAG beziehungsweise aktiv | 3,3 V äquivalent | 10 mA | fünf Diagnose-LEDs mit 0,5…1 mA plus zwei optionale Status-LEDs |
| **Summe 3,3-V-äquivalent** | | **590 mA** | gerundet |
| **Auslegungswert mit 30 % Reserve** | | **767 mA** | `590 mA × 1,30` |

Der festgelegte `LMR43620MSC3RPERQ1` mit 2 A Nennstrom bietet damit einen Faktor von rund 2,6 gegenüber dem reservierten 767-mA-Dauer-/Spitzenbudget. Diese Reserve ist für WLAN-Lastsprünge, Kondensatortoleranzen und noch zu messende E-Paper-Impulse bestimmt; sie ist keine Freigabe für externe Lasten.

Frontlicht und externe Ring-LED werden nicht aus `3V3_CORE`, sondern direkt aus `VIN_SYS` gespeist:

- Frontlicht: 50 mA bei etwa 3,0 V LED-Leistung, also 0,15 W.
- Externe Ring-LED: 10 mA Konstantstrom; etwa 3 V an der LED.

## 3. USB-Lastfälle

### 3.1 Vollbetrieb bei mindestens 1,5-A-Ankündigung

Konservative Annahmen: 767 mA an 3,3 V, 85 % Buckwirkungsgrad bei 5 V, 80 % Frontlichttreiberwirkungsgrad.

```text
I_USB,3V3 = 0,767 A × 3,3 V / (5,0 V × 0,85) = 0,596 A
I_USB,Frontlicht = 0,050 A × 3,0 V / (5,0 V × 0,80) = 0,038 A
I_USB,Ring-LED = 0,010 A
USB-Controller/eFuse/Reserve = 0,006 A
--------------------------------------------------------------
I_USB,Vollbetrieb ≈ 0,650 A
```

Damit verbleiben rund 350 mA Abstand zur normalen Boardgrenze von 1 A. Die eFuse wird nominal auf 1 A eingestellt und dient der Einschalt- und Fehlerstrombegrenzung. TI spezifiziert ihre ±10-%-Genauigkeit erst oberhalb 1 A; deshalb wird die normale 1-A-Grenze durch die festgelegte Lastfreigabe, das 0,65-A-Budget und die Messung nachgewiesen. Die eFuse darf nicht als präziser 1-A-Abschalter beschrieben werden.

### 3.2 USB-Default-Current / Flashbetrieb

Bis `TUSB321A` mindestens 1,5 A erkannt hat, sind Display-Aktualisierung, Frontlicht, Sensorversorgung und externe Ring-LED aus. Für den ESP32 werden trotzdem 500 mA an 3,3 V als konservative Spitze angesetzt:

```text
I_USB,ESP32 = 0,500 A × 3,3 V / (5,0 V × 0,85) = 0,388 A
RTC, Supervisor, USB-Controller, eFuse und Reserve       < 0,032 A
---------------------------------------------------------------
I_USB,Flashbetrieb, Budget                             < 0,420 A
```

Das Budget liegt unter 500 mA. Einschaltstrom und tatsächliche WLAN-/USB-Spitzen werden am Prototyp gemessen. Die Firmware muss die USB-Stromstufe vor Zuschalten der erweiterten Lasten auswerten; Hardware-Pulldowns halten diese Lasten bis dahin aus.

### 3.3 Quellenumschaltung

Bei gleichzeitigem Anschluss von 12 V und USB liegt `VIN_SYS` auf dem höheren geschützten 12-V-Pfad. Der USB-eFuse-Ausgang sperrt Rückstrom. Für die Prüfung werden Ströme in beide Quellstecker bei allen Anschluss- und Abschaltfolgen gemessen; zulässige Leckströme werden nach den finalen Datenblattgrenzen bewertet.

## 4. 12-V-Last und Verlustleistung

Mit 90 % angenommenem Buckwirkungsgrad bei 12 V ergibt sich für das reservierte 3,3-V-Lastbudget:

```text
I_12V,3V3 = 0,767 A × 3,3 V / (12 V × 0,90) = 0,234 A
I_12V,Frontlicht = 0,050 A × 3,0 V / (12 V × 0,80) = 0,016 A
I_12V,Ring-LED = 0,010 A
Controller und Reserve ≈ 0,010 A
-----------------------------------------------------------
I_12V,Vollbetrieb ≈ 0,270 A
```

Die externe 1-A-Sicherung besitzt somit reichlich Betriebsreserve. Sie schützt die Leitung; sie ersetzt nicht die lokale Strombegrenzung an USB, Sensor- und AUTOTERM-Zweig.

### 4.1 Erste Verlustleistungsabschätzung

| Bauteil/Pfad | Rechenfall | Verlust |
|---|---|---:|
| LMR43620-Q1 aus 12 V | 2,53 W Ausgang, 90 % | ca. 0,28 W |
| LMR43620-Q1 aus USB | 2,53 W Ausgang, 85 % | ca. 0,45 W |
| zwei Schutz-MOSFETs | 0,30 A, je 26 mΩ max. | ca. 4,7 mW |
| TPS259470 eFuse | 0,65 A, 28,3 mΩ typ. | ca. 12 mW |
| Frontlichttreiber | 0,15 W LED-Leistung, 80 % | ca. 38 mW |
| Ring-LED-Konstantstromquelle | 14 V, VF = 3 V, 10 mA | ca. 110 mW in CCR/MOSF |
| 3,0-V-LDO | 10 mA aktiv, 0,3 V Drop | ca. 3 mW |

Die Buckverluste sind der thermisch dominante normale Rechenfall. Das Layout muss das Exposed Pad nach Herstellerempfehlung anbinden. In Phase 2 werden Datenblatt-/Herstellertoolwerte über 10 V, 12 V, 14 V und USB sowie Temperatur und Bauteiltoleranz gerechnet; in Phase 6 folgen Wärmebild beziehungsweise Temperaturmessung im Gehäuse.

## 5. Komfort-Standby bei 12 V

Displayrail, Sensorrail, Frontlicht, Ring-LED, Diagnoseanzeige und AUTOTERM-OE sind aus. Der FT6336U bleibt an `3V0_TOUCH_AON` im Monitor-Modus. Weil das Touch-Datenblatt für 220 µA nur einen typischen Wert nennt, wird für das Budget das Doppelte verwendet; dies ist eine Engineering-Reserve, kein garantierter Worst Case.

### 5.1 Direkt am Eingang verbleibende Lasten

| Anteil | Budget bei 12 V |
|---|---:|
| LM74720-Q1, Datenblatt-Maximum | 38 µA |
| TVS, eFuse-Rückseite und Eingangsfilter-Leckage | 5 µA |
| **Zwischensumme vor Buck** | **43 µA** |

### 5.2 Lasten hinter dem Buck, auf 3,3 V äquivalent

| Anteil | 3,3-V-äquivalentes Budget |
|---|---:|
| ESP32-S3 Deep-Sleep einschließlich Boardreserve | 50 µA |
| FT6336U Monitor: 2 × 220 µA bei 3,0 V | 400 µA |
| 3,0-V-LDO Eigenstrom | 1 µA |
| TPS3808 Supervisor | 4 µA |
| RTC-Hauptversorgung und I2C | 2 µA |
| TXU0202, Display-Isolation, Touch-Reset-Puffer | 70 µA |
| ausgeschaltete Lastschalter | 3 µA |
| Pulls, Schutzleckströme und Restreserve | 64 µA |
| **Summe** | **594 µA** |

Für die Umrechnung wird wegen des sehr kleinen Lastpunkts bewusst nur 65 % PFM-Wirkungsgrad angenommen und zusätzlich 3 µA Eigenstrom des Bucks angesetzt:

```text
I_12V,hinter Buck = 0,594 mA × 3,3 V / (12 V × 0,65) + 0,003 mA
                  = 0,254 mA
I_12V,Komfort = 0,254 mA + 0,043 mA = 0,297 mA
```

Das Rechenbudget liegt rund 0,20 mA unter dem Ziel von 0,5 mA. Es ist dennoch nicht als garantierter Worst Case zu verstehen, weil der FT6336U keine maximale Monitorstromangabe enthält und der tatsächliche Buck-Wirkungsgrad im Sub-mA-Bereich vom Aufbau abhängt. Der Abnahmewert wird daher ausschließlich durch Messung aller fünf Prototypen bei 12 V bestimmt.

## 6. Minimal-Standby

Für FT6336U-Hibernation werden vorsichtshalber 2 × 55 µA bei 3,0 V angesetzt, entsprechend 100 µA auf 3,3 V umgerechnet. Gegenüber dem Komfort-Standby sinkt die äquivalente Bucklast damit um etwa 300 µA:

```text
I_12V,Minimal ≈ 43 µA + ((294 µA × 3,3 V) / (12 V × 0,65) + 3 µA)
               ≈ 170 µA
```

Das Ergebnis ist ein Zielwert, kein Abnahmemaximum. Touch kann in diesem Zustand nicht wecken; der externe Taster bleibt aktiv.

## 7. RTC-Backupzeit

Die Panasonic BR1225 besitzt nominal etwa 48 mAh. Für einen absichtlich sehr konservativen Nachweis werden nur 10 % der Nennkapazität und 0,5 µA Gesamtlast aus RTC, Sperrdiode, Halter-/PCB-Leckage und Alterung angesetzt:

```text
t = 4,8 mAh / 0,0005 mA = 9 600 h = 400 Tage
```

Selbst diese starke Derating-Annahme übertrifft die geforderten vier Wochen um mehr als den Faktor 14. Der reale Backupstrom wird bei entfernter externer Versorgung gemessen. Die Zelle wird erst nach Löt- und Reinigungsprozess eingesetzt und darf hardwareseitig nicht geladen werden.

## 8. Mess- und Freigabekriterien

1. USB-Default-Current: Start, natives Flashen und WLAN-Spitze kleiner 500 mA, erweiterte Lasten aus.
2. USB mit mindestens 1,5-A-CC: Vollbetrieb kleiner 1 A; nominale eFuse-Stromgrenze und Kurzschlussabschaltung funktionieren innerhalb der Datenblatttoleranz.
3. 12-V-Vollbetrieb bei 10/12/14 V einschließlich WLAN, Frontlicht, Display und Ring-LED; kein Brownout.
4. `3V3_CORE`-Transient am Modul bei WLAN-TX und Displaystart bleibt zwischen 3,0 V und 3,6 V.
5. Komfort-Standby kleiner 0,5 mA am 12-V-Stecker nach stabiler Einschwingzeit.
6. Minimal-Standby ist messbar niedriger als Komfort-Standby.
7. Rückstrom in USB-, Batterie- und AUTOTERM-Port in jeder Quellenfolge messen.
8. Temperatur von Buck, Schutz-MOSFETs, eFuse, Frontlichttreiber und Ring-LED-CCR im finalen Gehäuse prüfen.
9. RTC-Backupstrom messen und Backupzeit mit Zellen-Derating neu berechnen.

## 9. Datenblätter

- [Espressif ESP32-S3-WROOM-1/1U Datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [TI LMR43620-Q1](https://www.ti.com/product/LMR43620-Q1)
- [TI LM74720-Q1](https://www.ti.com/product/LM74720-Q1)
- [TI TPS25947](https://www.ti.com/product/TPS25947)
- [FocalTech FT6336U Datasheet](https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf)
- [Micro Crystal RV-3028-C7](https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7)
- [Panasonic BR1225](https://industrial.panasonic.com/ww/products/pt/lithium-batteries/models/BR1225)
