# Bauteilliste und Bibliotheksprüfung – Phase 1

Stand: 2026-10-12 · Grundlage: [Anforderungsdokument](../docs/Anforderungsdokument_Neuentwicklung.md) Teil B · Lager laut jlcpcb.com am 2026-10-12

## 1. Herkunft der Bibliotheksdaten

| Quelle | Verwendung |
|---|---|
| KiCad 10 Standardbibliothek | bevorzugt, wo Symbol und Footprint zum Teil passen |
| Projektbibliothek `LandyHeater` – Symbole | alle Symbole ohne KiCad-Entsprechung, selbst nach Datenblatt gezeichnet, mit korrekten Pin-Typen |
| Projektbibliothek `LandyHeater` – Footprints | aus EasyEDA/LCSC (`easyeda2kicad` 1.0.1) bzw. Antmicro, jeweils gegen Herstellerzeichnung geprüft, umbenannt, Courtyard neu, 3D-Modell projektlokal |

Prüfung nach N-03 für jedes Teil: Symbol-Pinnummer ↔ Footprint-Pad ↔ Herstellerzeichnung (Pinbelegung, Pad-Maße, Pin 1). Die automatische Kreuzprüfung Symbol ↔ Footprint ergibt für alle Projektsymbole vollständige Übereinstimmung.

## 2. Aktive Bauteile, Schutz, Steckverbinder

| Funktion | MPN | LCSC | Lager | Symbol | Footprint | Prüfung |
|---|---|---|---:|---|---|---|
| MCU-Modul | ESP32-S3-WROOM-1U-N16R8 | C3013946 | 12 380 | `RF_Module:ESP32-S3-WROOM-1` | `RF_Module:ESP32-S3-WROOM-1U` | 41 Pins = 41 Pads; Padnummern (EN 3, IO0 27, USB 13/14, EPAD 41) = Espressif-Datenblatt |
| 3,3-V-Buck | LMR43620MSC3RPERQ1 | C3190193 | 14 | `LandyHeater:LMR43620MSC3RPERQ1` | `LandyHeater:TI_RPE0009A_VQFN-HR-9_2x2mm` | Pinbelegung = TI Tab. 5-1. Landpattern deckt TI RPE0009A ab; Außenpads 0,08–0,14 mm länger (Lötkehle), Innenkanten wie TI |
| USB-eFuse | TPS259470LRPWR | C3662793 | 562 | `LandyHeater:TPS259470LRPWR` | `LandyHeater:TI_RPW0010A_VQFN-HR-10_2x2mm` | Pinbelegung Variante „0“ (OVLO, AUXOFF, FLT) = TI Tab. 5-1; Footprint Antmicro = TI RPW0010A |
| Reset-Supervisor | TPS3808G33DBVR | C51886189 | 3 407 | `Power_Supervisor:TPS3808DBV` | `Package_TO_SOT_SMD:SOT-23-6` | KiCad-Standard |
| Sensor-Lastschalter | TPS22945DCKR | C47507 | 9 908 | `LandyHeater:TPS22945DCKR` | `Package_TO_SOT_SMD:SOT-353_SC-70-5` | Pinbelegung = TI DCK (1 VOUT, 2 GND, 3 OC, 4 ON, 5 VIN) |
| AUTOTERM-Pegelwandler | TXU0202QDCURQ1 | C7372013 | 1 028 | `LandyHeater:TXU0202QDCURQ1` | `Package_SO:VSSOP-8_2.3x2mm_P0.5mm` | Pinbelegung = TI DCU; Richtung A1→B1Y (TX), B2→A2Y (RX) |
| RTC | RV-8263-C8-32.768KHZ-20PPM-TA-QC | C24955831 | 460 | `LandyHeater:RV-8263-C8` | `LandyHeater:MicroCrystal_C8_SON-8_2.0x1.2mm` | Pinbelegung und Pads (0,27 × 0,7 mm, Raster 0,54 mm) = Micro-Crystal-Datenblatt; Pin 1 unten links (Draufsicht) |
| Ring-LED-Treiber | BCR421UW6Q-7 | C154739 | 65 | `LandyHeater:BCR421UW6Q-7` | `Package_TO_SOT_SMD:SOT-23-6` | Pinbelegung = Diodes SOT26 (1 EN, 2/3/5 OUT, 4 GND, 6 REXT) |
| 12-V-Verpolschutz | SS16 | C2481 | 309 202 | `Diode:SS16` | `Diode_SMD:D_SMA` | KiCad-Standard |
| Eingangs-TVS | SMBJ18CA | C78413 | 84 358 | `Device:D_TVS` | `Diode_SMD:D_SMB` | bidirektional, KiCad-Standard |
| USB-ESD D+/D− | TPD2EUSB30DRTR | C97502 | 5 480 | `Power_Protection:TPD2EUSB30` | `Package_TO_SOT_SMD:Texas_DRT-3` | KiCad-Standard |
| USB-ESD VBUS | ESD5Z5.0T1G | C82044 | 373 429 | `Diode:ESD5Zxx` | `Diode_SMD:D_SOD-523` | KiCad-Standard |
| ESD AUTOTERM | PESD5V2S2UT,215 | C18441 | 150 578 | `LandyHeater:PESD5V2S2UT` | `Package_TO_SOT_SMD:SOT-23` | Nexperia: 1 K1, 2 K2, 3 gemeinsame Anode |
| ESD 1-Wire/Taster | PESD3V3S2UT,215 | C84276 | 55 431 | `LandyHeater:PESD3V3S2UT` | `Package_TO_SOT_SMD:SOT-23` | Nexperia: 1 K1, 2 K2, 3 gemeinsame Anode |
| Sperrdioden | BAS116,215 | C48502 | 42 689 | `LandyHeater:BAS116` | `Package_TO_SOT_SMD:SOT-23` | Nexperia: 1 A, 2 n.c. (als NC-Pin), 3 K |
| Klein-MOSFET | 2N7002K | C22379475 | 1 607 174 | `Transistor_FET:2N7002K` | `Package_TO_SOT_SMD:SOT-23` | KiCad-Standard |
| Buck-Drossel | FAUL0420-2R2MT | C3040383 | 2 606 | `Device:L` | `LandyHeater:L_CJiang_FAUL0420` | Pads auf Herstellerangabe korrigiert (1,5 × 2,2 mm, Abstand 2,5 mm); Isat ≥ 4,0 A |
| Knopfzellenklemme | MY-1225-01-J | C20606803 | 1 281 | `Device:Battery_Cell` | `LandyHeater:BatteryClip_MYOUNG_MY-1225-01-J` | Pads 1,3 × 5,5 mm bei ±7,25 mm = Zeichnung; Pad 2 = Minuskontakt auf der Platine, ohne Paste |
| Knopfzelle | Panasonic BR1225 | – | – | – | – | wird nicht bestückt |
| USB-C | USB4105-GF-A-060 | C3025063 | 1 123 | `Connector:USB_C_Receptacle_USB2.0_16P` | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` | KiCad-Standard für USB4105-xx-A |
| Lokale Taster | KMR221GLFS | C72443 | 5 668 | `Switch:SW_Push_Shielded` | `Button_Switch_SMD:SW_Push_1P1T-SH_NO_CK_KMR2xxG` | „G“ = Masseanschluss (SH) |
| LEDs rot | LTST-C190KRKT | C94869 | 337 173 | `Device:LED` | `LED_SMD:LED_0603_1608Metric` | KiCad-Standard |
| Nano-Fit J1–J4 | 1053131302/-03/-04/-05 | C17345480 / C17198650 / C17554326 / C17316840 | 0 / 0 / 9 / 0 | `Connector_Generic:Conn_01x0N` | `Connector_Molex:Molex_Nano-Fit_105313-xx0N_1x0N_P2.50mm_Horizontal` | KiCad-Standard; J1/J3/J4 nur Vorbestellung |

Widerstände, Kondensatoren und Ferrite werden in Phase 2 mit konkretem Wert aus dem JLCPCB-Basic-Sortiment (0603, X7R) gewählt und erhalten dann ihre LCSC-Nummer.

## 3. SPICE (N-07)

Passive Bauteile nutzen die KiCad-Standardmodelle. Für die ICs gibt es nur verschlüsselte PSpice/TINA-Modelle, für die Dioden ist kein Modell eingebunden. Diese Symbole tragen `Sim.Enable = 0` und eine Begründung im Feld `Sim.Hinweis`. Die SPICE-Prüfung im ERC meldet damit nur Teile, die weder Modell noch Begründung haben.

## 4. Befunde für Phase 2 (Schaltplan)

| # | Befund | Konsequenz |
|---|---|---|
| P1-01 | TPS25947: Absolutgrenze IN ≥ VOUT − 21 V. Liegt VIN_SYS bei einer 12-V-Transiente auf der TVS-Klemmspannung (bis 29,2 V) und ist USB nicht gesteckt, wird diese Grenze überschritten. | Im Schaltplan Spitzenspannung an VIN_SYS begrenzen (Filter hinter der Schottky-Diode, ggf. TVS mit niedrigerer Klemmung oder zusätzliche Begrenzung am eFuse-Ausgang) und rechnerisch nachweisen (V-01). |
| P1-02 | RV-8263: I2C-Betrieb erst ab VDD ≥ 1,8 V, Zeitbehalt ab 0,9 V; keine interne Backup-Umschaltung. | Dioden-ODER (BAS116) aus 3V3_CORE und Knopfzelle; CLKOE auf VSS (CLKOUT aus, spart Strom); INT mit Pull-up nach 3V3_CORE. |
| P1-03 | MY-1225-01-J ist nur die Plusklemme; der Minuspol liegt auf einem Kupferpad (ENIG) unter der Zelle. | Keine Vias/Leiterbahnen unter dem Minuspad außer der GND-Anbindung; Zelle 12,5 mm ragt seitlich über die Klemme (im Courtyard berücksichtigt). |
| P1-04 | BCR421: EN wird direkt vom GPIO (3,3 V) angesteuert. | Ausreichende Aussteuerung bei 3,3 V gegen Datenblattkennlinie prüfen; sonst kleine Treiberstufe. |
| P1-05 | FAUL0420: Isat ≥ 4,0 A, LMR43620-Stromgrenze max. 3,9 A. | Reserve knapp, im Normalbetrieb (≤ 0,6 A) unkritisch. |
| P1-06 | Bestand knapp: LMR43620MSC3 (14), BCR421 (65), Nano-Fit J2 (9); J1/J3/J4 nur Vorbestellung. | Vor Bestellung erneut prüfen und reservieren bzw. vorbestellen. |
