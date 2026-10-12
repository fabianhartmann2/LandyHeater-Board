# LandyHeater Controller – KiCad-Projekt (Rev B)

Neuaufbau nach [Anforderungsdokument v2.0](../docs/Anforderungsdokument_Neuentwicklung.md). Aus dem bisherigen Repository wurden keine KiCad-Dateien, Bibliotheken oder Skripte übernommen (N-01).

## Stand

| Phase | Status |
|---|---|
| 0 – Projekt, Lagen, Regeln, Bibliotheken | abgeschlossen, Freigabe ausstehend |
| 1 – Bauteilauswahl, Symbole, Footprints | offen |

## Struktur

| Pfad | Inhalt |
|---|---|
| `LandyHeater.kicad_pro/.kicad_sch/.kicad_pcb` | Projekt, Schaltplan, Leiterplatte (KiCad 10.0) |
| `libraries/LandyHeater.kicad_sym` | projektlokale, geprüfte Symbole (Bibliothek `LandyHeater`) |
| `libraries/LandyHeater.pretty/` | projektlokale, geprüfte Footprints (Bibliothek `LandyHeater`) |
| `libraries/3dmodels/` | 3D-Modelle, im Projekt als `${LANDYHEATER_3DMODELS}` |
| `output/` | erzeugte Berichte und Fertigungsdaten (nicht versioniert) |

## Leiterplatte

- 4 Lagen, JLCPCB-Stackup **JLC04161H-7628**, 1,6 mm, ENIG:
  F.Cu 35 µm · Prepreg 7628 0,2104 mm (εr 4,4) · In1.Cu 15,2 µm · Kern 1,065 mm · In2.Cu 15,2 µm · Prepreg 0,2104 mm · B.Cu 35 µm.
- Lagennutzung (A14): F.Cu Bauteile/Signale, In1.Cu GND durchgehend, In2.Cu Versorgung/langsame Signale, B.Cu GND/langsame Signale.
- Kontur: noch nicht gezeichnet (Phase 3, maximal 80 × 50 mm). Der DRC meldet deshalb bis dahin `invalid_outline`.

## Designregeln (JLCPCB 4 Lagen, mit Reserve)

| Regel | Wert | JLCPCB-Minimum |
|---|---|---|
| Leiterbahn Standard / Minimum | 0,2 / 0,127 mm | 0,09 mm |
| Abstand Kupfer | 0,15 mm | 0,09 mm |
| Via Standard | 0,6 / 0,3 mm | 0,45 / 0,3 mm (ohne Aufpreis) |
| Via Minimum | 0,45 / 0,3 mm | – |
| Kupfer zum Platinenrand | 0,3 mm | 0,2 mm |
| Bohrung zu Kupfer | 0,25 mm | – |
| Courtyard | Pflicht (Fehler) | – |

## Netzklassen

| Klasse | Bahn | Abstand | Via | Zuordnung (Muster) |
|---|---|---|---|---|
| Default | 0,2 mm | 0,15 mm | 0,6/0,3 | alle übrigen Netze |
| Power | 0,5 mm | 0,2 mm | 0,8/0,4 | `BATT_12V_IN`, `12V_PROT`, `VIN_SYS`, `USB_VBUS`, `VBUS_PROT`, `3V3_CORE`, `SW_BUCK` |
| USB | Diff.-Paar 0,25 mm / Spalt 0,13 mm | 0,15 mm | 0,6/0,3 | `USB_D*` |
| Extern | 0,3 mm | 0,2 mm | 0,6/0,3 | `AUTOTERM_*`, `CTRL_*`, `1WIRE_DQ`, `3V3_SENSOR_SW`, `BUTTON_N`, `LED_CC_PLUS`, `LED_PWM_MINUS` |

Das USB-Paar ist für ≈ 90 Ω differentiell über In1.Cu (Abstand 0,2104 mm) abgeschätzt. Vor dem Routing mit dem JLCPCB-Impedanzrechner für JLC04161H-7628 bestätigen und die Werte gegebenenfalls anpassen. Netznamen in den Mustern sind die geplanten Namen aus dem Anforderungsdokument; neue Netze werden bei Bedarf ergänzt.

## Prüfregeln

Alle ERC-Prüfungen sind aktiv, einschließlich der SPICE-Modellprüfung (Warnung): Jedes Symbol braucht ein SPICE-Modell oder eine begründete Abschaltung (`Sim.Enable` = 0, z. B. Steckverbinder, Testpunkte, Module ohne Herstellermodell). Im DRC sind nur die KiCad-Standardausnahmen „track not centered on via“ und „tuning profile track geometries“ ausgeblendet.

## Prüf- und Exportbefehle

```bash
KICAD_CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$KICAD_CLI sch erc -o output/erc.rpt LandyHeater.kicad_sch
$KICAD_CLI pcb drc --schematic-parity -o output/drc.rpt LandyHeater.kicad_pcb
$KICAD_CLI sch export netlist -o output/LandyHeater.net LandyHeater.kicad_sch
$KICAD_CLI sch export pdf -o output/LandyHeater-schematic.pdf LandyHeater.kicad_sch
$KICAD_CLI sch export bom -o output/LandyHeater-bom.csv LandyHeater.kicad_sch
$KICAD_CLI pcb export gerbers -o output/gerber/ LandyHeater.kicad_pcb
$KICAD_CLI pcb export drill -o output/gerber/ LandyHeater.kicad_pcb
$KICAD_CLI pcb export pos --side front --format csv --units mm -o output/LandyHeater-cpl.csv LandyHeater.kicad_pcb
$KICAD_CLI pcb export step -o output/LandyHeater.step LandyHeater.kicad_pcb
```

Die Netzlistenprüfung nach N-05 erfolgt anhand der exportierten Netzliste gegen das Anforderungsdokument. Für JLCPCB werden BOM (mit Spalte `LCSC`) und CPL in Phase 5 in das JLCPCB-Format gebracht.
