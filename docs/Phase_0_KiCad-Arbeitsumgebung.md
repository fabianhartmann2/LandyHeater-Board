# Phase 0 – KiCad-Arbeitsumgebung und Projektgerüst

Stand: 2026-09-06

Projektstatus: abgeschlossen und am 2026-09-06 durch den Auftraggeber freigegeben

## Werkzeugstand

- Betriebssystem: macOS
- KiCad: 10.0.6
- KiCad CLI: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`
- Projektformat: native KiCad-Projektdateien; das Gerüst wird mit KiCad 10 geprüft

Die Skripte suchen zuerst nach `KICAD_CLI_OVERRIDE`, danach nach `kicad-cli` im Suchpfad und abschließend am dokumentierten macOS-Standardpfad. Dadurch bleibt der Ablauf auch auf anderen Rechnern reproduzierbar.

## Projektstruktur

| Pfad | Zweck |
|---|---|
| `hardware/` | KiCad-Projekt, Schaltplan, PCB und lokale Bibliothekstabellen |
| `hardware/libraries/symbols/` | Projektlokale Symbole |
| `hardware/libraries/footprints/LandyHeater.pretty/` | Projektlokale Footprints |
| `hardware/libraries/3d/` | Geprüfte projektspezifische 3D-Modelle |
| `calculations/` | Auslegungs- und Worst-Case-Berechnungen |
| `manufacturing/` | Ausschließlich freigegebene Fertigungsstände |
| `scripts/` | Reproduzierbare KiCad-Prüf- und Exportabläufe |
| `build/` | Generierte Berichte und Review-Dateien; nicht versioniert |

## PCB-Grundeinstellungen

- Vier Kupferlagen: `F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`
- Zuordnung gemäß Anforderung: L1 Signale/Bauteile, L2 GND, L3 Versorgung/langsame Signale, L4 Displayseite/langsame Signale
- Nominale Dicke: 1,6 mm
- Oberfläche: ENIG als Projektvorgabe
- Provisorischer Zielumriss: 98 mm × 48 mm
- Revision im Titelblock: A
- Blind-/Buried-Vias und Microvias deaktiviert

Der eingetragene Lagenaufbau ist nur ein generisches Arbeitsmodell für KiCad. Die Dielektrikumsdicken, Kupferdicken der Innenlagen und impedanzabhängigen Regeln dürfen nicht als Fertigungsvorgabe verwendet werden. Der finale Stackup wird vor dem Routing in Phase 4 mit PCBWay bestätigt.

## Vorläufige Netzklassen

| Netzklasse | Zweck | Leiterbahnbreite | Clearance | Via/Bohrung |
|---|---|---:|---:|---:|
| `Default` | allgemeine Signale | 0,25 mm | 0,20 mm | 0,80/0,40 mm |
| `POWER_12V` | geschützte 12-V-Pfade | 1,00 mm | 0,30 mm | 1,00/0,50 mm |
| `POWER_LOW_VOLTAGE` | 5-V- und 3,3-V-Leistungspfade | 0,50 mm | 0,20 mm | 0,80/0,40 mm |
| `USB_DIFF_PROVISIONAL` | USB D+/D− | 0,20 mm | 0,20 mm | 0,60/0,30 mm |
| `SENSITIVE` | empfindliche langsame Signale | 0,25 mm | 0,25 mm | 0,80/0,40 mm |

Diese Werte sind Arbeitsvorgaben, keine abgeschlossene elektrische Auslegung. Besonders USB-Breite und -Abstand werden erst aus dem bestätigten Stackup berechnet. Stromtragfähigkeit und Spannungsabfall der Versorgungsklassen werden in Phase 1 berechnet und in Phase 4 umgesetzt.

## Bedienung

Im Repository-Stamm:

```sh
make doctor
make check
make export-review
make clean
```

- `doctor` prüft KiCad-Version und erforderliche Projektdateien.
- `check` führt ERC und DRC inklusive Schaltplan-/PCB-Paritätsprüfung aus.
- `export-review` erzeugt zusätzlich Schaltplan-PDF, PCB-Lagen-PDF und ein Board-only-STEP-Modell unter `build/review/`.
- `clean` entfernt ausschließlich den generierten Ordner `build/`.

Für einen abweichenden KiCad-Pfad:

```sh
KICAD_CLI_OVERRIDE=/vollständiger/pfad/kicad-cli make check
```

## Freigabekriterien

- [x] KiCad 10 und CLI erkannt
- [x] Projektstruktur angelegt
- [x] Leerer Schaltplan und elektrisch leeres Vierlagen-PCB angelegt
- [x] Titelblock, Revision und vorläufige Netzklassen eingetragen
- [x] Lokale Symbol-, Footprint- und 3D-Modellstruktur angelegt
- [x] Projekt ohne fehlende Bibliotheken in der KiCad-GUI geöffnet
- [x] ERC und DRC ohne ungeklärte Fehler
- [x] Review-Exporte reproduzierbar erzeugt und visuell geprüft
- [x] Phase 0 durch Auftraggeber am 06.09.2026 mit dem Auftrag zum Beginn von Phase 1 freigegeben

## Prüfergebnis

Der reproduzierbare Lauf mit `make export-review` wurde am 06.09.2026 erfolgreich durchgeführt:

- ERC: 0 Fehler, 0 Warnungen
- DRC: 0 Verletzungen, 0 offene Verbindungen
- Schaltplan-/PCB-Parität: 0 Abweichungen
- Schaltplan-PDF: erzeugt, eine Seite, Titelblock vollständig und ohne Darstellungsfehler
- PCB-Lagen-PDF: erzeugt, sieben Seiten, Titelblock und provisorischer Umriss ohne Darstellungsfehler
- Board-only-STEP: erzeugt und als nicht leere STEP-Datei validiert

Die in den Berichten aufgeführten ignorierten Prüfkategorien sind KiCad-Projekteinstellungen, keine gefundenen Verstöße. Mit zunehmendem Designumfang werden sie in den jeweiligen Reviewphasen erneut bewertet und nur mit technischer Begründung beibehalten.
