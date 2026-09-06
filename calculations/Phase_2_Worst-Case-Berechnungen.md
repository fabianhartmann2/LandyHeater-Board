# Phase 2 – Worst-Case-Berechnungen Revision A

Stand: 2026-09-06

Statuskennzeichnung: **ERFÜLLT** bedeutet mit Datenblattgrenzen rechnerisch abgedeckt. **NICHT VERIFIZIERT** bedeutet, dass eine notwendige Herstellerkurve, Systemannahme, Simulation oder Messung fehlt. Ein typischer Wert wird nie als garantierter Grenzwert ausgegeben.

## 1. LM74720-Q1 Überspannungsabschaltung

Bestückung: R1 = 100 kΩ ±1 %, R2 = 7,15 kΩ ±1 %. Aus TI: OV-Schwelle 1,13…1,33 V, konservativ zusätzlich ±1 µA OV-Pinleckstrom.

`VIN(OV) = VOV × (1 + R1/R2) ± ILEAK × R1`

| Fall | Ergebnis |
|---|---:|
| nominal, VOV = 1,231 V | 18,45 V |
| niedrigste Abschaltung, R1 −1 %, R2 +1 %, VOV min., Leckstrom ungünstig | 16,52 V |
| höchste Abschaltung, R1 +1 %, R2 −1 %, VOV max., Leckstrom ungünstig | 20,41 V |

Der garantierte 10…14-V-Betriebsbereich liegt unter der minimalen Abschaltschwelle: **ERFÜLLT**. Die höchste mögliche Weitergabespannung, TVS-Klemmung und dynamische Überschwinger bestimmen jedoch MOSFET-, Buck- und Kondensatorstress: **NICHT VERIFIZIERT**, bis das Eingangspulsprofil und die Quellenimpedanz festgelegt sind.

Die 18-V-Zenerdiode D17 liegt von Q2-Gate zu dessen Source/geschütztem Ausgang. R74 = 100 Ω und C4 = 10 nF nach GND entsprechen der Funktion von TI Figure 9-1. Die resultierende Inrush-/SOA-Koordination hängt von der gesamten effektiven Ausgangskapazität und dem MOSFET ab: **NICHT VERIFIZIERT**.

## 2. TVS und Eingangsfilter

D1 `TPSMB18CA-VR`: VRWM 18 V, Breakdown- und Klemmwerte gemäß ST-Datenblatt. Die TVS-Wahl schützt den nominalen 14-V-Betrieb vor normalem Leiten. Ohne definierte Pulsform, Quellimpedanz, Kabelinduktivität und Wiederholrate können Pulsstrom, Energie und reale Klemmspannung nicht seriös bestimmt werden.

Ergebnis: Bauteilklasse plausibel, aber TVS-Energie, Temperatur, LM74720-Abschaltdynamik, Q1-SOA und das Ferrit-/Kondensator-Netz sind **NICHT VERIFIZIERT**. Dies ist eine Phase-3-Sperre, kein stillschweigend bestandener Nachweis.

## 3. USB-eFuse TPS259470L

### 3.1 Stromgrenze

R9 = 3,32 kΩ ±1 %. Das aktuelle TI-Datenblatt spezifiziert für diesen Arbeitspunkt einen Stromgrenzbereich von ungefähr 0,85…1,15 A, typisch 1,007 A. Die Schaltung schützt daher gegen groben Überstrom, beweist aber nicht präzise eine USB-1-A-Dauergrenze.

Ergebnis: Schutzfunktion **ERFÜLLT**; maximale normale Boardaufnahme muss durch Laststeuerung und Messung ≤1 A bleiben.

### 3.2 OVLO

R7 = 100 kΩ ±1 %, R8 = 26,1 kΩ ±1 %, VOVLO = 1,183…1,223 V. Mit konservativ ±0,1 µA Pinleckstrom:

| Fall | Abschaltschwelle |
|---|---:|
| nominal | 5,82 V |
| Minimum | 5,62 V |
| Maximum | 6,01 V |

Der USB-5-V-Nennbereich wird nicht beschnitten und unzulässig hohe VBUS-Pegel werden vor VIN_SYS getrennt: **ERFÜLLT**.

### 3.3 Einschaltflanke

C8 = 10 nF. Nach TI-Näherung ergibt sich etwa 0,2 V/ms; 5 V werden in ca. 25 ms aufgebaut. Der reale Inrush ist `I = CLOAD × dV/dt` und muss mit der effektiven Gesamtkapazität hinter U3 geprüft werden. **NICHT VERIFIZIERT** bis zur DC-Bias-Auswertung und Messung.

## 4. 3,3-V-Buck LMR43620-Q1

Aus TI-Tabelle für feste 3,3 V/2,2 MHz: L2 = 2,2 µH, CIN = 4,7 µF + 100 nF, COUT = 2 × 22 µF. L2 `XAL4020-222MEC`: ±20 %, Isat 5,6 A. TI gibt als maximale High-Side-Spitzenstromgrenze 3,9 A an; 5,6 A > 3,9 A: Sättigungsreserve **ERFÜLLT**.

Konservative Induktivität 1,76 µH. Mit `ΔIL = VOUT × (1 − VOUT/VIN) / (L × f)` und 2,2 MHz:

| VIN | berechnete ΔIL p-p |
|---:|---:|
| 10 V | 0,57 A |
| 14 V | 0,65 A |
| 20,4 V bis zur maximalen OV-Abschaltung | 0,71 A |

Bei 2 A Last läge der rechnerische Spitzenstrom bei höchstens ca. 2,36 A und unter 3,9 A. Im vorgesehenen, deutlich kleineren normalen Lastbudget ist die Reserve größer.

Mit 2 × 22 µF, nur Kapazitätstoleranz −10 % und ohne ESR ergibt sich bei 14 V ideal etwa 0,94 mV Welligkeit. Diese Zahl ist **kein** fertiger Nachweis: DC-Bias, Temperatur, Leiterbahnparasiten, ESR, Lastsprung und Regelkreis müssen mit Herstellerkurven und realem Layout simuliert/gemessen werden. Stabilität/Ripple: **NICHT VERIFIZIERT**.

## 5. ESP32-3,3-V-Pufferung

C15/C16 sind je `GCJ31CR71A226KE01`, 22 µF/10 V/X7R/±10 %, plus C17 = 100 nF nahe am Modul. Nennkapazität 44 µF entspricht der vorgesehenen WLAN-Pufferung. Die effektive Kapazität bei 3,3 V und Temperatur sowie die Impedanz des fertigen Layouts sind **NICHT VERIFIZIERT**. Abnahme: 3V3-Minimum am WROOM-Pad während WLAN-Sendeimpulsen und gleichzeitiger Displayaktivität messen.

## 6. Frontlicht AL8861Q

R43 = 2,00 Ω ±1 %, Datenblatt-Sense-Schwelle 95…105 mV:

| Fall | LED-Strom |
|---|---:|
| nominal | 50,0 mA |
| Minimum | 95 mV / 2,02 Ω = 47,0 mA |
| Maximum | 105 mV / 1,98 Ω = 53,0 mA |

Die Anforderung <60 mA ist rechnerisch **ERFÜLLT**. L4 = 47 µH liegt im empfohlenen 33…100-µH-Bereich. C52 = 10 µF/100 V/X7R erfüllt Nennwert, Temperaturklasse und Spannungsreserve. Stromwelligkeit und AL8861-Verlustleistung hängen von Frontlight-VF, Schaltfrequenz und Layout ab: **NICHT VERIFIZIERT**. PWM gemäß Datenblatt bevorzugt ≤500 Hz.

Im ausgeschalteten Zustand nennt das Datenblatt maximal 100 µA Versorgungsstrom. Dieser garantierte Anteil allein entspricht bei 12 V bereits 0,1 mA Batteriestrom und muss im Ruhestrombudget enthalten sein.

## 7. Taster-Ring-LED BCR421

Der BCR421 liefert nominal 10 mA; EN erlaubt Low-Side-PWM unter 25 kHz. Bei 14 V und angenommener LED-VF 2,6 V liegt die Ausgangsverlustleistung grob bei `(14 − 2,6) V × 11 mA ≈ 125 mW`, zuzüglich EN-Verlust. Mit dem Datenblatt-RθJA von etwa 140 K/W ergibt das rund 18 K Temperaturanstieg auf einer geeigneten Kupferfläche.

Die Annahme der LED-VF und die Helligkeit am realen APEM-Teil sind nicht bestätigt. Besonders bei 4,75-V-USB-Minimum muss ausreichende Regler-Headroom bleiben. Thermik bei 14 V: plausibel; USB-Headroom und tatsächlicher LED-Strom über Temperatur: **NICHT VERIFIZIERT**.

## 8. Diagnose-Gate und LED-Zweige

R75 = 47 kΩ und R45 = 100 kΩ bilden am Q5-Gate einen Teiler von 0,680. Daraus folgen:

| Quelle | Q5-Gate ungefähr |
|---:|---:|
| USB 4,75 V | 3,23 V |
| Fahrzeug 14 V | 9,52 V |
| maximale LM74720-OV-Schwelle 20,41 V | 13,88 V |

Damit bleibt Q5-VGS unter seinem 20-V-Absolutmaximum: **ERFÜLLT**. Ob 3,23 V mit Bauteilstreuung für die gewünschte Helligkeit genügt, wird am Prototyp geprüft. Die Sperrdioden verhindern logische Rückspeisung; ihr temperaturabhängiger Leckstrom und die Resthelligkeit werden gemessen.

## 9. 3-m-Taster und I2C/1-Wire

- Taster: R38 × C35 = 1 kΩ × 10 nF = 10 µs. Der Pull-upstrom bei gedrücktem Taster ist 3,3 V/10 kΩ = 330 µA. Wake-Pulsbreite und Störfestigkeit am 3-m-Kabel: **NICHT VERIFIZIERT**.
- I2C: mit 4,7 kΩ und `tr ≈ 0,8473 × R × C` sind für 1 µs Standard-Mode theoretisch ca. 251 pF und für 300 ns Fast-Mode ca. 75 pF zulässig. Deshalb startet die Firmware mit 100 kHz; reale Buskapazität am Display-FPC ist zu messen.
- 1-Wire: drei Sensoren und 2…5 m Leitung haben unbekannte Kabelkapazität/Topologie. 4,7 kΩ ist durch den bisherigen Testaufbau plausibilisiert, aber Timingreserve und EMV am finalen Kabelbaum bleiben **NICHT VERIFIZIERT**.

## 10. RTC-Backup

Die BR1225 wird über eine BAS116 gegen Laden entkoppelt; die interne RV-3028-Ladefunktion muss softwareseitig dauerhaft aus bleiben. Selbst bei konservativ angenommenen 0,5 µA Gesamtbackupstrom ergäben 48 mAh rechnerisch etwa 96.000 h beziehungsweise über 10 Jahre; Selbstentladung und Temperatur dominieren. Die geforderten vier Wochen besitzen damit große rechnerische Reserve. Tatsächlicher Backupstrom und falscher Ladestrom werden vor Auslieferung gemessen.

## 11. Zusammenfassung der offenen Nachweise

| Nachweis | Status |
|---|---|
| 10…14-V-Betrieb unterhalb OV-Abschaltung | ERFÜLLT |
| USB-OVLO und grobe 1-A-Strombegrenzung | ERFÜLLT |
| Buck-Induktorsättigung | ERFÜLLT |
| Frontlight-Maximalstrom <60 mA | ERFÜLLT |
| Diagnose-Q5-VGS | ERFÜLLT |
| TVS-/MOSFET-SOA und Eingangsfilter | NICHT VERIFIZIERT |
| effektive MLCC-Werte, Buck-Regelkreis/Ripple/Lastsprung | NICHT VERIFIZIERT |
| USB-Inrush und vollständiges USB-Lastbudget am Muster | NICHT VERIFIZIERT |
| Ring-LED-Headroom/Thermik mit echtem APEM-Teil | NICHT VERIFIZIERT |
| Touch-Wake, I2C-Flanken, 1-Wire-Kabel | NICHT VERIFIZIERT |
| garantierter Gesamt-Ruhestrom | NICHT VERIFIZIERT |

Aufgrund dieser offenen Nachweise lautet die belastbare Phase-2-Empfehlung: **NICHT FREIGABEFÄHIG**.
