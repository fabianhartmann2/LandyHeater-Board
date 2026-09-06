# Phase 2 – Quellen und Rückverfolgbarkeit

Stand: 2026-09-06

Es gelten jeweils die verlinkte Dokumentrevision und zusätzlich das bei Fertigungsfreigabe aktuelle Herstellerdatenblatt. Bei einer Revision ist eine Änderungsprüfung erforderlich.

| Baugruppe / Referenzen | Primärquelle | Im Schaltplan verwendete Vorgabe |
|---|---|---|
| U5 ESP32-S3-WROOM-1U-N16R8 | [Espressif WROOM-1/1U Datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), Abschnitte Pin Definitions, Power Supply und Peripheral Schematics; [Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html) | Modulpadfolge, 3,3-V-Versorgung/Abblockung, CHIP_PU, Strapping, USB GPIO19/20, Octal-PSRAM-Pins, Modul-Landpattern |
| U1/Q1/D1/D17 | [TI LM74720-Q1, Rev. März 2022](https://www.ti.com/lit/ds/symlink/lm74720-q1.pdf), Figure 9-1 S.14 sowie 9.2.3.2/9.2.3.3/9.2.3.5 S.17 ff.; [Infineon IPG20N06S4L-26](https://www.infineon.com/assets/row/public/documents/10/49/infineon-ipg20n06s4l-26-datasheet-en.pdf); [ST TPSMB](https://www.st.com/resource/en/datasheet/tpsmb.pdf) | Figure-9-1-Anlaufnetz, 18-V-VGS-Klemme, 100-µH-Boostzweig, RTN offen, MOSFET-Pinout, TVS-Grenzwerte |
| U4/L2/C11/C13/C14 | [TI LMR43620-Q1 SNVSBE0H, Rev. März 2026](https://www.ti.com/lit/ds/symlink/lmr43620-q1.pdf), Tabelle 8-2 S.29 und Abschnitte 8.2.2.2/8.2.2.3; [Coilcraft XAL4000](https://www.coilcraft.com/getmedia/6adcb47d-8b55-416c-976e-1e22e0d2848c/xal4000.pdf); [Murata GCJ](https://www.murata.com/products/capacitor/ceramiccapacitor/overview/lineup/smd/gcj) | feste 3,3-V-/2,2-MHz-Anwendung: 2,2 µH, 4,7 µF + 100 nF Eingang, 2 × 22 µF Ausgang; Isat ≥ maximale Stromgrenze |
| J5/U2 | [GCT USB4105](https://gct.co/connector/usb4105), [TI TUSB321AI, Rev. Mai 2017](https://www.ti.com/lit/ds/symlink/tusb321ai.pdf), Pin Functions und Detailed Description | USB-C-UFP, interne Rd, VBUS_DET 900 kΩ, OUT-Pull-ups ≥200 kΩ an USB_VBUS |
| U3 | [TI TPS25947, Rev. Mai 2026](https://www.ti.com/lit/ds/symlink/tps25947.pdf), Electrical Characteristics sowie 7.3.3/7.3.5 | Latch-off, Rückstromsperre, 3,32-kΩ-ILIM, OVLO-Teiler, dV/dt |
| U6 | [TI TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf) | 3,07-V-Schwelle; CT offen = feste nominelle 20-ms-Verzögerung |
| U7 | [TI TPD2EUSB30](https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf) | kapazitätsarmer USB-D±-ESD-Schutz |
| U8/U9/U10 | [TI TPS22919](https://www.ti.com/lit/ds/symlink/tps22919.pdf), [TI SN74AXC8T245](https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf), [TI SN74AXC1T45](https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf) | geschaltete Displayversorgung, Power-off-Schutz, Richtungen/OE und lokale Abblockung |
| J6/L3/Q3/D3…D5/C22…C38 | [Good Display GDEY029T94-FT01 Rev. 1.0](https://v4.cecdn.yun300.cn/100001_1909185148/GDEY029T94-FT01.pdf), Pin Definition/Absolute Ratings und Kapitel 12, S.29 | FPC-Pinfolge, Panelgrenzen und Booster-Referenzschaltung Kapitel 12 |
| J7/U11/U12/U13 | [FocalTech FT6336U V1.0](https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf), Abschnitte Power/Reset/I2C/Power Modes; [TI TPS7A02](https://www.ti.com/lit/ds/symlink/tps7a02.pdf), [TI SN74LVC1G07-Q1](https://www.ti.com/lit/ds/symlink/sn74lvc1g07-q1.pdf), [TI SN74LVC1G74-Q1](https://www.ti.com/lit/ds/symlink/sn74lvc1g74-q1.pdf) | 2,8…3,3 V, I2C, Resetfolge, Monitor/Hibernation, INT-Wake und DNP-Latch |
| U14/BT1/D6 | [Micro Crystal RV-3028-C7](https://www.microcrystal.com/fileadmin/Media/Products/RTC/App.Manual/RV-3028-C7_App-Manual.pdf), [Nexperia BAS116](https://assets.nexperia.com/documents/data-sheet/BAS116.pdf) | Pinout, VBACKUP, Primärzellenentkopplung, Ladefunktion deaktiviert |
| J2/U15/U16/D7 | [TI TXU0202-Q1](https://www.ti.com/lit/ds/symlink/txu0202-q1.pdf), [TI TPS22945](https://www.ti.com/lit/ds/symlink/tps22945.pdf), [Nexperia PESD5V2S2UT-Q](https://assets.nexperia.com/documents/data-sheet/PESD5V2S2UT-Q.pdf) | Teilversorgungsverhalten, OE-default LOW, 5-V-Seite aus AUTOTERM, Common-Anode-ESD-Pinout |
| J3/U17/D8 | [TI TPS22945](https://www.ti.com/lit/ds/symlink/tps22945.pdf), [Nexperia PESD3V3S2UT](https://assets.nexperia.com/documents/data-sheet/PESD3V3S2UT.pdf), [Analog Devices 1-Wire long lines](https://www.analog.com/en/resources/technical-articles/guidelines-for-reliable-long-line-1wire-networks.html) | geschaltete/strombegrenzte Sensorrail, ESD-Pinout, 4,7-kΩ-Startwert und Messpflicht am Kabel |
| J4/U18 | [APEM AV series](https://www.apem.com/api/asset/en/fbCPLUNNnaEJPS7JlAtdy/pusbutton-switches-serie-AV.pdf), Ordering Guide; [Diodes BCR420/BCR421 Rev. 6-2, Juli 2023](https://www.diodes.com/datasheet/download/BCR420UW6Q.pdf), Pin Assignments/Electrical Characteristics/Application | 19-mm-Tasteroptionen, externe LED ohne Vorwiderstand, 10-mA-Regler, EN-PWM <25 kHz |
| U19/L4/D10/C52 | [Diodes AL8861Q Rev. 4-2, Juli 2023](https://www.diodes.com/datasheet/download/AL8861Q.pdf), Application Information; [Diodes B140Q](https://www.diodes.com/assets/Datasheets/ds38236.pdf); [Murata LQH3NPZ](https://www.murata.com/products/inductor/power/overview/lineup/pi2); [TDK CGA6P1X7R2A106K250AC](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6P1X7R2A106K250AC) | 50-mA-Buck-LED-Treiber, 47 µH, 40-V-Schottky, mindestens 10 µF X7R lokal |
| Gesamtlayout | [Predictable Designs PCB Layout Rules Checklist](https://predictabledesigns.com/pcb-layout-rules-checklist.pdf), Espressif/TI/Diodes-Layoutkapitel | Reviewcheckliste zusätzlich zu den verbindlichen Herstellerregeln |

## Nicht verifizierte Quellenpunkte

- Die Good-Display- und FocalTech-Unterlagen legen die elektrischen Pins fest, ersetzen aber nicht die physische Prüfung von Kontaktseite, Pin 1 und Biegerichtung am konkreten Displaymuster.
- Datenblatt-typische Stromwerte ohne garantierten Maximalwert sind nicht als Worst Case gekennzeichnet; sie bleiben Messwerte für die Prototypabnahme.
- Distributor-/PCBWay-Bestand und zulässige Bestellsuffixe sind zum Fertigungszeitpunkt neu zu prüfen. Der BOM-Eintrag ist keine Beschaffungsgarantie.

## Angepasste Werte gegenüber Referenzschaltungen

| Schaltung | Hersteller-Ausgangspunkt | Projektanpassung und Begründung |
|---|---|---|
| LM74720 OV | einstellbarer OV-Eingang | 100 kΩ/7,15 kΩ für nominal 18,45 V; garantiert oberhalb 14 V, aber unterhalb der 60-V-Bauteilgrenzen; dynamische Koordination bleibt offen |
| LM74720 Gate-Slew | TI Figure 9-1: 0 Ω, 100 Ω, C nach GND und 18-V-Zener | Topologie unverändert, C = 10 nF als Startwert; Inrush und Q1-SOA werden erst nach effektiver CLOAD freigegeben |
| TPS259470L | programmierbarer ILIM/OVLO/dVdt | 3,32 kΩ ≈1 A, 100 kΩ/26,1 kΩ ≈5,82 V, 10 nF ≈0,2 V/ms; auf USB-Boardgrenzen angepasst |
| LMR43620 | TI-Tabelle für feste 3,3 V/2,2 MHz | Werte ohne Topologieänderung übernommen; konkrete automotive MLCC/Induktivität gewählt, DC-Bias-Prüfung offen |
| AL8861 | ILED = 0,1 V/RS, L = 33…100 µH, CIN ≥10 µF X7R | RS = 2,0 Ω für 50 mA; 47 µH und 10 µF/100 V; realer Frontlight-VF/Ripple offen |
| BCR421 | interner 10-mA-Stromregler mit EN-PWM | direkt an GPIO38 über 100 Ω, 100-kΩ-Pulldown; ersetzt die zuvor ungeeignete floating-source-MOSFET-Kaskade |
