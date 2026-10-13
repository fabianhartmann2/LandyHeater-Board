# Phase 2 – Schaltplanreview

Stand: 2026-10-12 · Schaltplan: `LandyHeater.kicad_sch` (5 Seiten) · Sollvorgabe: [Schaltungsentwurf](Schaltungsentwurf.md)

## 1. Ergebnis

| Prüfung | Ergebnis |
|---|---|
| ERC (alle Prüfungen aktiv, inkl. SPICE-Modellprüfung) | 0 Fehler, 1 Warnung (begründet, s. 4) |
| Netzlistenprüfung N-05 (Sollknoten aus dem Entwurf gegen exportierte Netzliste) | 66 Sollknoten und 12 Reihenschaltungen geprüft, 0 Abweichungen |
| SPICE-Netzliste | alle R/C/L mit gültigen Zahlenwerten; Teile ohne Modell mit `Sim.Enable = 0` und Begründung (`Sim.Hinweis`) |
| Footprint-Zuordnung | jede Referenz hat einen geprüften Footprint (Phase 1) |
| BOM | Export mit MPN, Hersteller, LCSC (aktive Teile, Stecker) und Spezifikation (passive Teile); Testpunkte nicht in der BOM |
| Lesbarkeit (N-04) | Funktionsblöcke mit Rahmen und Überschrift, lokale Verbindungen als Leitungen, Labels nur für Seitenübergänge und benannte Netze |

Umfang: 131 Bauteile (inkl. 28 Testpunkte, 3 DNP), 103 Netze.

## 2. Auslegung (Nachweise)

| Größe | Rechnung | Ergebnis |
|---|---|---|
| USB-UVLO / OVLO | 1,20 V × (R3+R4+R5)/(R4+R5) bzw. 1,20 V × (R3+R4+R5)/R5 | 4,30 V / 5,80 V (Toleranz der Schwelle ±2 %) |
| USB-Strombegrenzung | ILM 3,32 kΩ (Datenblatt: 6,65 kΩ ≙ 0,5 A) | ≈ 1,0 A |
| eFuse-Absolutgrenze IN ≥ OUT − 21 V (P1-01) | eFuse-Ausgang durch D4 von VIN_SYS getrennt | 12-V-Transienten erreichen die eFuse nicht |
| Buck | LMR43620 fest 3,3 V, 2,2 MHz, L = 2,2 µH, COUT 2 × 22 µF | Werte nach TI-Tabelle; Isat L ≥ 4,0 A > Stromgrenze 3,9 A |
| Eingangsschutz | SMBJ18CA: Klemmung 29,2 V bei 20,6 A | < 36 V (Buck), < 60 V (SS16) |
| RTC-Versorgung | Dioden-ODER BAS116: RTC_VDD ≈ 2,7–2,9 V; I2C ab 1,8 V | erfüllt; Zelle wird nie geladen (Sperrdiode) |
| RTC-Pufferzeit | BR1225 48 mAh, RTC 0,24 µA max. + Diodenleckstrom < 0,1 µA | > 10 Jahre rechnerisch (Ziel 4 Wochen) |
| Diagnose-LEDs | (U − 1,8 V − 0,6 V) / R | 0,6–1,0 mA je LED; ohne DIAG 0 µA |
| Standby-Strom (12 V) | ESP32 Deep-Sleep ≈ 8–10 µA, Supervisor 2,8 µA, Lastschalter/Pegelwandler/RTC/Leckströme ≈ 5 µA, Buck-Ruhestrom ≈ 1,2 µA; auf 12 V umgerechnet (η ≈ 70 %) | ≈ 15 µA ≪ 0,5 mA |
| USB-Aufnahme | ESP32-Spitze 500 mA bei 3,3 V → ≈ 390 mA aus 5 V, + Sensoren, Ring-LED | ≈ 420 mA < 500 mA |

## 3. Sichere Defaultzustände (A13)

| Funktion | Umsetzung |
|---|---|
| AUTOTERM-TX/RX gesperrt | OE-Pulldown R18 100 kΩ; TXU0202 Ioff bei fehlendem VCCB |
| Sensorversorgung aus | ON-Pulldown R19 100 kΩ |
| Ring-LED, RUN, Status-LEDs aus | Pulldowns R25, R31, R34, R35 (100 kΩ) |
| Diagnose-LEDs aus | Kathodenleitung nur über DIAG-Taster nach GND |
| Taster- und RTC-Wake HIGH | R23 10 kΩ, R14 100 kΩ nach 3V3_CORE |
| Reset definiert | TPS3808 hält EN bis 3V3 stabil + ≈ 20 ms |
| 12-V-/USB-Pfade rückstromgesperrt | D2, D4 und eFuse-Rückstromsperre |

## 4. Begründete Warnung

`footprint_filter` an F1: Das Polyfuse-Symbol erwartet Footprints mit „PTC“ im Namen. Verwendet wird der KiCad-Standard-Footprint `Fuse_0805_2012Metric`, der das 0805-PTC-Gehäuse exakt abbildet. Kein Handlungsbedarf.

## 5. Offene Punkte für Phase 3 und später

| # | Punkt | Phase |
|---|---|---|
| V-01 | Transientenprofil festlegen und TVS/Filter rechnerisch nachweisen | 3 (vor Layout-Freeze) |
| V-02 | MLCC-DC-Bias (22 µF / 10 V an 3,3 V) prüfen; ggf. 25-V-Typ wählen | 5 (Bauteilauswahl JLCPCB) |
| P2-01 | LCSC-Nummern der passiven Bauteile (Basic bevorzugt) mit dem JLCPCB-Plugin zuweisen | 5 |
| P2-02 | PTC F1 und Ferrit FB1 konkretes Teil bei JLCPCB wählen | 5 |
| P2-03 | USB-Diff.-Paar 90 Ω mit JLCPCB-Impedanzrechner bestätigen | 4 |
| P2-04 | Firmware: GPIO7 (RTC_INT_N) und GPIO9 (BUTTON_N) als EXT1 ANY_LOW (Belegung seit Phase 3, s. A12), RTC-Alarm-Ausgang, CLKOUT aus; DQ hochohmig/LOW solange Sensorversorgung aus | Firmware |
| P2-05 | Bestand knapp (LMR43620MSC3 14 Stück, BCR421 65, Nano-Fit J2 9), J1/J3/J4 nur Vorbestellung | 5 |

## 6. Freigabekriterien Phase 2

- [x] lesbarer hierarchischer Schaltplan, Funktionsblöcke mit Überschrift
- [x] ERC ohne Fehler, Warnungen begründet
- [x] Netzlistenprüfung nach N-05 ohne Abweichung
- [x] SPICE-Prüfung (N-07): Modelle bzw. begründete Ausschlüsse
- [x] sichere Defaultzustände umgesetzt
- [x] BOM exportiert
- [ ] Freigabe durch Auftraggeber
