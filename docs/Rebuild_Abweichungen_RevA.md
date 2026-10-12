# Rev A Rebuild – Abweichungen und gefundene Fehler

Stand: 2026-10-12 · Branch `claude/revA-rebuild`

Grundlage: [Anforderungsliste](Anforderungsliste_RevA.md), freigegeben am 2026-10-12 mit diesen Entscheidungen:

- Fertiger bleibt PCBWay.
- Bauteile mit LCSC-Nummer; pin- und funktionsgleiche Alternativen sind zulässig, wenn sie dokumentiert werden.
- Kurzschlussschutz für `LED_CC_PLUS`.
- Kompletter Neuaufbau mit bewährten Schaltungen, besonders im Netzteil (Kfz-Spannungseinbrüche).

Die Schaltung ist vollständig in `scripts/rebuild/design.py` definiert. Schaltplan, Stückliste und PCB werden daraus erzeugt. `scripts/rebuild/verify.py` vergleicht die aus KiCad exportierte Netzliste Pin für Pin mit dieser Definition.

## 1. Fehler im bisherigen Phase-2-Stand (behoben)

| # | Bereich | Fehler | Korrektur | Quelle |
|---|---|---|---|---|
| F1 | USB-ESD U7 | `TPD2EUSB30DRTR` wurde als 5-poliger Durchgangstyp im SOT-23-5 verdrahtet. Das DRT-Gehäuse hat nur 3 Pins: D+, D−, GND. | ST `USBLC6-2SC6` mit 6 Pins (D−/D+ durchgeschleift, VBUS-Referenz) | TI SLVSAC2G Tabelle 5-1 |
| F2 | USB-eFuse | EN/UVLO hing direkt an VBUS. Der Pin ist nur bis 6,5 V absolut zulässig, empfohlen sind ≤ 5 V. | Teilerkette 105k/10,7k/30,1k: UVLO 4,29 V, OVLO 5,81 V | TI SLVSFC9C §6.1/§7.3 |
| F3 | USB-eFuse | Footprint mit Exposed Pad; das RPW0010A-Gehäuse hat keins. | Footprint neu aus der TI-Zeichnung 4225183/A | TI SLVSFC9C S. 73 |
| F4 | RTC | Der RV-3028-C7-Footprint war gespiegelt: Die Bottom-View-Zeichnung wurde als Top-View verwendet. | Pin 1 jetzt unten links, Pins 1–4 unten, 5–8 oben (Top View) | Micro Crystal App-Manual Rev 1.4 §8.1 |
| F5 | E-Paper-Booster | Der VSL-Kondensator lag zwischen PREVGH und VSL. | VSL → 1 µF → GND (GD C10) | Good Display GDEY029T94-FT01 Rev 1.0 Kap. 12 |
| F6 | 12-V-Schutz | Die 18-V-Z-Klemme überschritt VGS ±16 V des IPG20N06S4L-26. | Der neue FET hat ±20 V, 18-V-Klemme wie bei TI | Nexperia BUK7K17-60E §8 |
| F7 | 12-V-Schutz | Footprint des LM74720 mit Exposed Pad 1,5 mm statt 1,06 mm (DRR0012F). | Footprint neu aus TI 4225797/A, RTN-Pad ohne Vias und ohne Netz | TI SLVSFH8B S. 32 |
| F8 | Buck | Der projekteigene RPE-Footprint war geometrisch nur vorläufig. | Wegfall: neuer Buck im Standardgehäuse HSOIC-8 | – |
| F9 | Frontlicht | Der 100-kΩ-Pulldown an AL8861 VSET hält den Treiber gegen dessen internen Pull-up nicht sicher aus. | 4,7 kΩ | Diodes DS41798 Pinbeschreibung VSET |
| F10 | AUTOTERM_5V | Die eingehende Heizungsversorgung hatte keinen ESD-Schutz; die Spezifikation §8 fordert ihn. | `PESD5V0S1BA` direkt an J2 | Spec §8 |
| F11 | `LED_CC_PLUS` | 0 Ω direkt an VIN_SYS: Ein Kurzschluss im 3-m-Kabel hätte die ganze Versorgung kurzgeschlossen. | PTC `MF-USMF005-2` (50 mA Halte-, 150 mA Auslösestrom, 30 V) | Spec §11 |

## 2. Bewusste Abweichungen von der Spezifikation v1.6

| ID | Spezifiziert | Rev-A-Rebuild | Begründung |
|---|---|---|---|
| DEV-01 | TVS `TPSMB18CA-VR` | `TPSMB36CA` (Littelfuse, AEC-Q101, bidirektional) | TI-Referenz Bild 9-1 verwendet eine 36-V-TVS. Sie bleibt beim unterdrückten 35-V-Load-Dump hochohmig, der LM74720 trennt dann über die OV-Abschaltung bei 18,4 V. Die 18-V-TVS hätte beim Load-Dump die gesamte Energie absorbieren müssen. Klemmung 49,9 V bei 12 A liegt unter 60 V (FETs) und 65 V (LM74720). |
| DEV-02 | `IPG20N06S4L-26` | `BUK7K17-60EX` (Nexperia, Dual 60 V, 17 mΩ, AEC-Q101, VGS ±20 V) | IPG20 ohne Lagerbestand; gleiche Pinbelegung S1/G1/S2/G2/D2/D2/D1/D1 |
| DEV-03 | – | 47 µF/35 V Panasonic FK (AEC-Q200) an VIN_SYS | Hold-up bei Mikrounterbrechungen (LV124 E-10, TI §9.2.3.4) und ESR-Dämpfung des Ferrit/MLCC-Eingangsfilters |
| DEV-04 | GCT `USB4105-GF-A-120` | HRO `TYPE-C-31-M-12` | GCT ohne Lagerbestand; verbreiteter USB-2.0-Type-C-Stecker mit 16 Pins |
| DEV-05 | `TPD2EUSB30DRTR` | ST `USBLC6-2SC6` | siehe F1; Standard-USB-2.0-ESD mit 3,5 pF, für Full Speed ausreichend |
| DEV-06 | EN direkt an VBUS | UVLO/OVLO-Teilerkette | siehe F2 |
| DEV-07 | `LMR43620MSC3RPERQ1` (2,2 MHz, fest 3,3 V) | `LMR33630CDDAR` (2,1 MHz, HSOIC-8, 3,8–36 V) mit TI-Standardwerten aus Tabelle 9-2: 1,2 µH, 2 × 22 µF, 100k/43,2k | LMR43620 ohne Lagerbestand. Bewährter TI-Regler mit gleichem Frequenzband oberhalb des AM-Bands. Arbeitet bei Kaltstart-Einbrüchen im Dropout weiter (100 % Tastverhältnis). Ruhestrom 24 µA statt 1,5 µA; das Komfort-Standby-Budget steigt um rund 25 µA (siehe §4). |
| DEV-08 | `KMR221GLFS` | XKB `TS-1187A-B-A-B` (5,1 × 5,1 mm) | KMR2 ohne Lagerbestand |
| DEV-09 | `TPS22919QDCKRQ1` | `TPS22919DCKR` | Q1 ohne Lagerbestand; gleicher Chip, −40…125 °C |
| DEV-10 | `SN74LVC1G07QDBVRQ1` | `SN74LVC1G07DBVR` von UMW | TI-Q1 ohne Lagerbestand; −40…85 °C, pinkompatibel |
| DEV-11 | Keystone 500 (THT) | TE `BAT-HLD-012-SMT` | Keystone 500 ohne Lagerbestand; SMT-Halter für 12-mm-Zellen (CR/BR1225) |
| DEV-12 | – | `PESD5V0S1BA` an AUTOTERM_5V | siehe F10 |
| DEV-13 | `PESD5V2S2UT-Q` | `PESD5V0S2BT` (Nexperia, bidirektional, Dual) | Q-Version ohne Lagerbestand |
| DEV-14 | `R65` 0 Ω | PTC `MF-USMF005-2` | siehe F11; BCR421-Headroom bei USB 4,75 V: 4,75 − 3,0 (LED) − 0,03 (PTC) − 1,4 (BCR) = 0,3 V Reserve |
| DEV-15 | `BCR421UW6Q-7` | `BCR421UW6-7` | Q-Version ohne Lagerbestand; gleiches Datenblatt |
| DEV-16 | VSET-Pulldown 100 kΩ | 4,7 kΩ | siehe F9 |
| DEV-17 | `XAL4020-222MEC` | entfällt (Buck-Wechsel); 1,2 µH MetalLions `MMPC0402-1R2MT`, Isat 7,8 A | |
| DEV-18 | `LQH3NPZ470MJR` | Taiyo Yuden `NRS4018T470MDGJV` (47 µH, Isat 0,6 A, AEC-Q200) | Murata ohne Lagerbestand; Good Display fordert 47 µH / 500 mA |
| DEV-19 | `XPL2010-104ML` | APV `ANR3015T101M` (100 µH, Isat 250 mA) | Coilcraft ohne Lagerbestand; TI fordert > 175 mA |
| DEV-20 | `MBR0530T1G` | MCC `MBR0530-TP` | onsemi ohne Lagerbestand; gleicher Typ (30 V/0,5 A) |
| DEV-21 | `2N7002KQ-13`, `BC857BQ` | `2N7002K-7` (Diodes), `BC857BLT1G` (onsemi) | Q-Versionen ohne Lagerbestand |

Ohne LCSC-Lagerbestand, aber unverändert übernommen (PCBWay-Beschaffung über Distributoren): Molex Nano-Fit `1053131302/03/04/05` und Micro Crystal `RV-3028-C7-32.768kHz-1ppm-TA-QC`.

## 3. Netzteil – bewährte Schaltungen für Kfz-Einbrüche

1. **Eingang (TI LM74720-Q1, Bild 9-1, 1:1 übernommen):** bidirektionale TVS, LM74720-Q1 mit Back-to-back-FETs. Damit sind Verpolung (−14 V/60 s), Rückstromsperre bei Einbrüchen und Mikrounterbrechungen, aktive Gleichrichtung überlagerter Wechselspannung (ISO 16750-2) und die OV-Abschaltung (18,4 V nominal) abgedeckt. Der LM74720 arbeitet ab 3 V; TI legt die Referenz für 3,2-V-Kaltstart, 35-V-Load-Dump und ISO 7637-2 / LV124 aus.
2. **Hold-up:** Weil der LM74720 Rückstrom sperrt, entlädt sich VIN_SYS bei einem Einbruch nicht zurück in die Batterie. 47 µF + 13 µF MLCC überbrücken bei 0,3 A Last etwa 200 µs mit 1 V Spannungsverlust (LV124 E-10: 100 µs).
3. **Buck LMR33630C:** VIN 3,8–36 V. Im Dropout senkt er die Frequenz und fährt das Tastverhältnis gegen 100 %; 3,3 V bleiben bis etwa 3,6 V Eingang erhalten (Datenblatt §8.4.2).
4. **Reset:** TPS3808G33 hält das ESP32 im Reset, solange 3V3 unter 3,07 V liegt, plus 20 ms Verzögerung. Ein Kaltstart unter etwa 3,6 V führt zu einem sauberen Reset statt eines Brownout-Zustands.
5. **USB-Pfad:** TPS25947 mit echter Rückstromsperre. Der 12-V-Pfad hat automatisch Vorrang; ein Einbruch auf 12 V speist nicht in USB zurück.

## 4. Auswirkungen auf das Ruhestrombudget (Komfort-Standby, 12 V)

| Änderung | Δ am 12-V-Eingang |
|---|---:|
| LMR33630 IQ 24 µA (typ.) statt LMR43620 ≈ 3 µA | +21 µA |
| TPS25947 Rückleckstrom bei VOUT 12 V, VIN 0 V (4,9 µA typ.) | bereits im alten Budget enthalten |
| Hold-up-Elko Leckstrom (≤ 0,01 CV ≈ 16 µA max., typ. < 2 µA) | +2 µA typ. |

Neues Rechenbudget: etwa 0,43 mA, also weiterhin unter dem Ziel von 0,5 mA. Abnahme wie gehabt durch Messung.

## 5. Weiterhin offene Gates (unverändert, nur durch Muster/Messung lösbar)

- FPC-Kontaktseite und Pin 1 von J6/J7/J8 am Originaldisplay prüfen (FH12 Bottom-Contact als Baseline)
- Touch-INT-Pulsdauer und Wake-Zuverlässigkeit messen; erst danach entscheiden, ob das Latch bestückt wird
- Transientenprofil des Fahrzeugs: Lastsprung und Load-Dump am Prototyp prüfen
- APEM-Taster: Code, LED-Polarität und Flussspannung bestätigen
- Footprints von L2 (MMPC0402, verwendet wird der Sunlord-MWSA0402S-Footprint mit 4,4 × 4,2 mm) gegen das Datenblatt prüfen
