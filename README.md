# LandyHeater Board

Hardwareentwicklung für das Landy-Heater-Steuergerät auf Basis des `ESP32-S3-WROOM-1U-N16R8`.

## Aktueller Stand

Revision A hat Phase 0 und Phase 1 abgeschlossen. Der erste automatisch erzeugte Phase-2-Schaltplan hat den Lesbarkeitsreview nicht bestanden und wird als echter, funktionsorientierter KiCad-Schaltplan neu aufgebaut. Die verbindliche Grundlage bleibt Dokumentversion 1.5 mit den zugehörigen Entwicklungsunterlagen:

- [Hardware-Anforderungsspezifikation Revision A](docs/Hardware-Anforderungsspezifikation_Revision_A.md)
- [Ergebnisbericht Phase 0](docs/Phase_0_KiCad-Arbeitsumgebung.md)
- [Phase 1 – Architektur und Bauteilfestlegung](docs/Phase_1_Architektur-und-Bauteilfestlegung.md)
- [Phase 2 – KiCad-Schaltplan und Review](docs/Phase_2_Schaltplanreview.md)
- [GPIO-Matrix Revision A](docs/GPIO-Matrix_Revision_A.md)
- [Leistungs- und Ruhestrombudget Revision A](calculations/Leistungs-und-Ruhestrombudget_Revision_A.md)
- [Schaltplan-PDF Phase 2](output/pdf/LandyHeater-Board-schematic-Phase2.pdf)
- [Vorläufige BOM Phase 2](output/bom/LandyHeater-Board-BOM-Phase2.csv)

Die Spezifikation definiert Funktionsumfang, Schnittstellen, Versorgung, Mechanik, sichere Hardwarezustände, Layoutregeln, Fertigungsunterlagen und Abnahmetests. Die darin aufgeführten Verifikationspunkte müssen vor der Fertigungsfreigabe abgeschlossen werden.

## Phasenplan Revision A

Jede Phase wird einzeln beauftragt, geprüft und freigegeben. Mit der nächsten Phase wird erst nach ausdrücklicher Freigabe der Ergebnisse begonnen. Erkenntnisse, die Anforderungen verändern, werden zuerst in der Hardware-Anforderungsspezifikation dokumentiert.

### Phase 0 – KiCad-Arbeitsumgebung und Projektgerüst

- KiCad-10-Version und Kommandozeilenwerkzeuge prüfen und dokumentieren.
- Verzeichnisstruktur für KiCad-Quellen, lokale Symbole, Footprints, 3D-Modelle, Berechnungen und Fertigungsdaten anlegen.
- Leeres KiCad-Projekt mit vier Lagen, Revision, Titelblock und grundlegenden Netzklassen erstellen.
- Reproduzierbare Prüf- und Exportbefehle vorbereiten.

**Freigabepunkt:** Das Projekt lässt sich ohne fehlende Bibliotheken öffnen und die automatischen KiCad-Prüfwerkzeuge sind verfügbar.

**Status:** Technisch abgeschlossen und durch den Auftraggeber am 06.09.2026 mit dem Auftrag zum Beginn von Phase 1 freigegeben.

### Phase 1 – Schaltungsarchitektur und Bauteilfestlegung

- Blockschaltbild, Versorgungskonzept und Spannungsdomänen finalisieren.
- Vollständige ESP32-GPIO-Matrix einschließlich Reset-, Boot- und Deep-Sleep-Zuständen erstellen.
- Strom-, Ruhestrom-, Verlustleistungs- und USB-Lastbudget erstellen.
- Konkrete Herstellerteilenummern für aktive Bauteile, Schutzbeschaltung, Steckverbinder und FPC-Stecker auswählen.
- Footprints, Pinouts, Temperaturbereiche und PCBWay-Beschaffbarkeit vorprüfen.

**Freigabepunkt:** Architektur, GPIO-Matrix, Bauteilauswahl und Berechnungen sind nachvollziehbar dokumentiert; offene Punkte für den Schaltplan sind geschlossen oder ausdrücklich als Verifikationspunkte gekennzeichnet.

**Status:** Technisch abgeschlossen und durch den Auftraggeber am 06.09.2026 mit dem Auftrag zum Beginn von Phase 2 freigegeben.

### Phase 2 – KiCad-Schaltplan

- Hierarchischen Schaltplan für Versorgung, ESP32/USB, Display/Touch/Frontlicht, RTC, AUTOTERM, 1-Wire, Taster/LED und Diagnoseanzeige erstellen.
- Lokale Symbole und Footprint-Zuordnungen vollständig einbinden.
- Sichere Hardwarezustände, Testpunkte und Bestückungsoptionen abbilden.
- ERC durchführen und alle Warnungen entweder beheben oder schriftlich begründen.
- Schaltplan-PDF und vorläufige BOM für den Review erzeugen.

**Freigabepunkt:** Schaltplanreview abgeschlossen, ERC ohne ungeklärte Fehler und alle Hersteller-Pinouts unabhängig geprüft.

**Status:** In Überarbeitung seit 06.09.2026. Der erste ERC-fehlerfreie Entwurf wurde wegen überlagerter Labels, rasterartiger Platzierung und unzureichend erkennbarer Schaltungszusammenhänge im Review zurückgewiesen. Phase 2 ist nicht freigegeben.

### Phase 3 – Mechanik und Platzierung

- PCB-Kontur, Befestigungspunkte und zulässigen Bauraum festlegen.
- Display, drei FPC-Stecker, Nano-Fit-Anschlüsse, USB-C, Antennenkoax, Knopfzelle sowie BOOT-, RESET- und DIAG-Taster platzieren.
- Energiefluss-Diagnoseanzeige und gegebenenfalls zwei optionale Status-LEDs integrieren.
- Kritische Keep-outs, FPC-Biegeradien, Steck-/Entriegelungswege und Servicezugang prüfen.
- Vollständig bestücktes 3D-STEP-Modell für Gehäuse- und Kollisionsprüfung erzeugen.

**Freigabepunkt:** Platzierungs- und 3D-Review abgeschlossen; Gehäuseschnittstellen, Bedienung und Wartungszugang sind freigegeben.

### Phase 4 – Vierlagen-PCB-Layout

- Finalen PCBWay-Stackup und Netzklassen übernehmen.
- Versorgungsschutz, Buck-Regler, USB, ESP32, E-Paper-Booster und weitere Signale nach Priorität routen.
- Durchgehende GND-Referenz, Rückstrompfade, Abblockung, EMI-Abstände und thermische Reserven sicherstellen.
- DRC, ERC-Rückprüfung, Layoutchecklisten und visuellen Lagenreview durchführen.

**Freigabepunkt:** DRC ohne ungeklärte Fehler; Schaltplan, PCB, Pin-Matrix und BOM sind synchron und der Layoutreview ist dokumentiert.

### Phase 5 – PCBWay-Fertigungsfreigabe

- RS-274-X-Gerber, Excellon-Bohrdaten und gegebenenfalls ODB++/IPC-D-356 erzeugen.
- PCBWay-BOM und CPL/Centroid-Dateien mit Seite, Position und Rotation erstellen.
- Schaltplan, Bestückungszeichnungen, Fertigungszeichnung, DNP-Liste, STEP-Modell und spezielle Prozesshinweise beilegen.
- Gerber, Bohrungen, Lötstoppmaske, Pastenlagen, Silkscreen, Bauteilrotationen und Pin 1 unabhängig kontrollieren.
- Getrennte, eindeutig versionierte ZIP-Pakete für PCB-Fertigung und PCBA zusammenstellen.

**Freigabepunkt:** Manufacturing-Release-Checkliste vollständig; erst danach dürfen die fünf Prototypen bei PCBWay bestellt werden.

### Phase 6 – Inbetriebnahme der fünf Prototypen

- Sicht-, Kurzschluss- und Widerstandsprüfung vor dem ersten Einschalten.
- Versorgungsschienen mit strombegrenzten Laborquellen stufenweise prüfen.
- ESP32-Reset, Boot und USB-Programmierung verifizieren.
- Diagnoseanzeige, Deep-Sleep, RTC, Touch, Display, Frontlicht, 1-Wire und AUTOTERM in definierter Reihenfolge testen.
- Ruhestrom, Lastsprünge, Rückspeisung, Temperaturverhalten und alle Abnahmekriterien protokollieren.
- Abweichungen sammeln und Entscheidung über Nacharbeit oder Revision B treffen.

**Freigabepunkt:** Vollständiger Prüfbericht für alle fünf Prototypen und dokumentierte Entscheidung über den weiteren Einsatz.

### Geplante Endergebnisse

- editierbares KiCad-Projekt mit projektlokalen Bibliotheken,
- Schaltplan und Bestückungszeichnungen als PDF,
- vollständige BOM und GPIO-Matrix,
- PCB-Layout und 3D-STEP-Modell,
- Gerber-, Drill-, CPL-/Centroid- und PCBWay-BOM-Dateien,
- Fertigungs- und PCBA-ZIP-Pakete,
- Prüfplan und Prototypen-Prüfbericht.

## Abgrenzung Revision A

Revision A umfasst die AUTOTERM-UART-Schnittstelle, drei gemeinsam angeschlossene DS18B20-Sensoren, RTC, USB-C, externen Taster mit dimmbarer LED, eine lokale Energiefluss-Diagnoseanzeige sowie das Good-Display-E-Paper mit Touch und Frontlicht. VOTRONIC VBCS und Smart-Shunt sind für eine spätere Revision vorgemerkt.
