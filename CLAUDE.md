# LandyHeater-Board – Arbeitsregeln

## PCB-Layout

Für jede Arbeit an Platzierung und Routing gelten verbindlich die
[PCB Layout Engineering Instructions](docs/PCB_Layout_Engineering_Instructions.md).

Reihenfolge, jede Stufe als prüfbarer Meilenstein mit Freigabe durch den Auftraggeber:

1. Schaltplan und Datenblätter analysieren: Funktionsblöcke, Strompfade, kritische Signale, physikalische Randbedingungen.
2. Funktionale Platzierungszonen planen: Versorgung, MCU, Schnittstellen, Stecker, Analogteil, Schutz.
3. Hierarchisch platzieren: mechanische Anker → große ICs → kritische Passive → übrige Bauteile.
4. Elektrisch optimieren: Stromschleifen, Rückstrompfade, Ratsnest-Komplexität, Wärme.
5. Validieren und freigeben: DRC, Courtyards, Sperrflächen, Datenblattanforderungen, Platzierungsbericht.
6. Routing erst nach bewerteter und freigegebener Platzierung.

Die Platzierung ist ein eigener Meilenstein vor dem Routing. Er braucht:
- Floorplan der Funktionsblöcke,
- echtes Rendering der Leiterplatte,
- datenblattgestützte Platzierungsentscheidungen,
- DRC-Bericht.

Keine reine Verbindungslängen-Optimierung, keine Lockerung von Regeln, um den DRC zu bestehen. Schaltplan, Footprints, Kontur und Lagenaufbau nur mit Begründung und Freigabe ändern.

## Projekt

- KiCad-Projekt in `kicad/`, Anforderungen in `docs/Anforderungsdokument_Neuentwicklung.md` (Teil A verbindlich, Teil B informativ).
- Fertigung JLCPCB, 4 Lagen JLC04161H-7628.
- Boards, die mit dem KiCad-Python geladen werden, nur aus dem Projektordner speichern. Sonst schreibt `pcbnew` eine Standard-`.kicad_pro` daneben und die Netzklassen gehen verloren.
