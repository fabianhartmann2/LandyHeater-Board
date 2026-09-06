# Projektlokale Footprints

In diesem Verzeichnis werden projektspezifische KiCad-Footprints abgelegt. Jeder Footprint muss in der zugehörigen Bauteildokumentation gegen die aktuelle Herstellerzeichnung verifiziert werden.

Phase 2 enthält die elektrisch zugeordneten Footprints `RV-3028-C7` und `Texas_RPE0009A_VQFN-HR-9_2x2mm`. Beide sind ausdrücklich **noch kein Layout-Freeze**:

- Beim RTC ist das aktuelle Micro-Crystal-ECAD-Modell vor Phase 3 nochmals geometrisch zu vergleichen.
- Beim TI-RPE0009A müssen die vier L-förmigen Eckpads, Lötstoppmaske und segmentierte Paste exakt aus TI-Zeichnung `QFND681` übernommen beziehungsweise mit dem offiziellen CAD-Modell ersetzt werden. Die derzeitigen Pads sichern nur Pin-/Netzlisten-Konsistenz und dürfen nicht für Fertigungsdaten verwendet werden.
- Der derzeit zugeordnete generische RPW-Footprint des `TPS259470LRPWR` muss vor Phase 3 gegen die aktuelle TI-Landpatternzeichnung geometrisch geprüft und bei Abweichungen projektlokal ersetzt werden.
- `PROVISIONAL_Infineon_PG-TDSON-8-4_Dual` bildet alle acht Symbolpads eindeutig ab, ist aber nur ein Schaltplan-Platzhalter. Vor Phase 3 muss er durch das offizielle Infineon-PG-TDSON-8-4-Landpattern mit geteiltem Exposed Pad und passender Pastensegmentierung ersetzt werden.

Die drei FPC-Footprints bleiben bis zur Prüfung des Originaldisplays hinsichtlich Kontaktseite und Einsteckrichtung vorläufig.
