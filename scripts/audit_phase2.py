#!/usr/bin/env python3
"""Audit the exported Phase-2 BOM and netlist against the reviewed definition."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

from generate_phase2_schematic import pages, validate_definition


ROOT = Path(__file__).resolve().parents[1]
BOM = ROOT / "output" / "bom" / "LandyHeater-Board-BOM-Phase2.csv"
NETLIST = ROOT / "build" / "reports" / "phase2.net"
REPORT = ROOT / "build" / "reports" / "phase2-audit.txt"
OUTPUT_REPORT = ROOT / "output" / "reports" / "LandyHeater-Board-Audit-Phase2.txt"
NETLIST_COMPARISON_REPORT = ROOT / "output" / "reports" / "LandyHeater-Board-Netlist-Comparison-Phase2.txt"

# Captured from build/reports/phase2-before-rework.net immediately before the
# purely graphical rework requested on 2026-09-07.  The topology digest ignores
# timestamps, titles, properties and net names; it hashes only the partition of
# connected component pins.  This makes it a stable electrical regression gate.
GRAPHICAL_REWORK_BASELINE_RAW_SHA256 = "6077254ad38973092c4b5cefda012bff106fe935b2b8a473ba2dc4fbc516b3cb"
GRAPHICAL_REWORK_BASELINE_TOPOLOGY_SHA256 = "00ce8f7d7237aa13ae732818b4ef832ae0c6ac1b73049995a4f299356ca35dd0"
GRAPHICAL_REWORK_BASELINE_PIN_COUNT = 651
GRAPHICAL_REWORK_BASELINE_NET_COUNT = 175


def balanced_blocks(text: str, marker: str) -> list[str]:
    blocks: list[str] = []
    start = 0
    while True:
        start = text.find(marker, start)
        if start < 0:
            return blocks
        depth = 0
        quoted = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if escaped:
                escaped = False
            elif char == "\\" and quoted:
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        blocks.append(text[start:index + 1])
                        start = index + 1
                        break
        else:
            raise ValueError(f"Unbalanced block beginning with {marker!r}")


def exported_net_pins(text: str) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for block in balanced_blocks(text, "\n\t\t(net"):
        name_match = re.search(r'\(name "([^"]+)"\)', block)
        if not name_match:
            continue
        name = name_match.group(1)
        for node in balanced_blocks(block, "\n\t\t\t(node"):
            ref = re.search(r'\(ref "([^"]+)"\)', node)
            pin = re.search(r'\(pin "([^"]+)"\)', node)
            if ref and pin:
                result[(ref.group(1), pin.group(1))] = name
    return result


def topology_digest(pin_nets: dict[tuple[str, str], str]) -> tuple[str, int, int]:
    """Hash electrical connectivity independently of generated net names."""
    groups: dict[str, set[tuple[str, str]]] = {}
    for pin, net in pin_nets.items():
        groups.setdefault(net, set()).add(pin)
    canonical = "\n".join(
        sorted(",".join(f"{ref}.{pin}" for ref, pin in sorted(group)) for group in groups.values())
    ) + "\n"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), len(pin_nets), len(groups)


def main() -> int:
    definitions = pages()
    validate_definition(definitions)
    parts = [part for _title, _file, page_parts, _notes in definitions for part in page_parts]
    blockers: list[str] = []
    failures: list[str] = []
    comparison_lines: list[str] = []

    if not BOM.is_file() or not NETLIST.is_file():
        failures.append("Exportierte BOM oder Netzliste fehlt; zuerst make export-phase2 ausführen.")
    else:
        rows = list(csv.DictReader(BOM.open(encoding="utf-8", newline="")))
        expected_fields = {"Reference", "Value", "Footprint", "Datasheet", "Manufacturer", "MPN", "Assembly", "Notes"}
        if not rows or set(rows[0]) != expected_fields:
            failures.append("BOM-Spalten entsprechen nicht dem festgelegten Phase-2-Schema.")
        for row in rows:
            if not row["Footprint"].strip():
                failures.append(f"BOM-Gruppe {row['Reference']} hat keinen Footprint.")

        actual = exported_net_pins(NETLIST.read_text(encoding="utf-8"))
        topology_sha256, connected_pin_count, net_count = topology_digest(actual)
        raw_sha256 = hashlib.sha256(NETLIST.read_bytes()).hexdigest()
        topology_equal = (
            topology_sha256 == GRAPHICAL_REWORK_BASELINE_TOPOLOGY_SHA256
            and connected_pin_count == GRAPHICAL_REWORK_BASELINE_PIN_COUNT
            and net_count == GRAPHICAL_REWORK_BASELINE_NET_COUNT
        )
        comparison_lines = [
            "LandyHeater Revision A – Netzlistenvergleich vor/nach grafischer Überarbeitung",
            "=============================================================================",
            "Vergleichsbasis: Export unmittelbar vor der grundlegenden grafischen Überarbeitung vom 2026-09-07",
            f"Vorher, rohe Netzliste SHA-256: {GRAPHICAL_REWORK_BASELINE_RAW_SHA256}",
            f"Nachher, rohe Netzliste SHA-256: {raw_sha256}",
            "Hinweis: Der rohe Hash darf wegen Datum, Titel und sichtbaren Bauteileigenschaften abweichen.",
            "",
            f"Vorher: {GRAPHICAL_REWORK_BASELINE_PIN_COUNT} angeschlossene Pins in {GRAPHICAL_REWORK_BASELINE_NET_COUNT} elektrischen Netzen",
            f"Nachher: {connected_pin_count} angeschlossene Pins in {net_count} elektrischen Netzen",
            f"Vorher, Topologie SHA-256: {GRAPHICAL_REWORK_BASELINE_TOPOLOGY_SHA256}",
            f"Nachher, Topologie SHA-256: {topology_sha256}",
            "",
            "Ergebnis: " + (
                "IDENTISCH – keine Pin-zu-Pin-Verbindung wurde durch die grafische Überarbeitung geändert."
                if topology_equal else
                "ABWEICHUNG – die elektrische Topologie stimmt nicht mit dem Vorher-Stand überein."
            ),
        ]
        if not topology_equal:
            failures.append("Elektrische Topologie weicht vom Netzlistenstand vor der grafischen Überarbeitung ab.")
        expected_by_pin = {
            (part.ref, number): expected_net
            for part in parts
            for number, _pin_name, expected_net in part.pins
            if expected_net is not None
        }
        actual_to_expected: dict[str, set[str]] = {}
        for pin, expected_net in expected_by_pin.items():
            if pin not in actual:
                failures.append(f"Netzliste enthält den angeschlossenen Pin {pin[0]}.{pin[1]} nicht.")
                continue
            actual_to_expected.setdefault(actual[pin], set()).add(expected_net)
        for actual_net, expected_nets in sorted(actual_to_expected.items()):
            if len(expected_nets) > 1:
                failures.append(
                    f"Kurzschluss/Netzverschmelzung auf {actual_net}: {', '.join(sorted(expected_nets))}."
                )
        for part in parts:
            for number, _pin_name, expected_net in part.pins:
                if expected_net is None or (part.ref, number) not in actual:
                    continue
                actual_net = actual[(part.ref, number)]
                peers = [pin for pin, net in expected_by_pin.items() if net == expected_net]
                if any(actual.get(peer) != actual_net for peer in peers):
                    failures.append(f"Netz {expected_net} ist in der exportierten Netzliste unterbrochen.")
                    break

    for part in parts:
        if part.ref.startswith(("U", "Q", "D", "LED", "J", "BT", "L", "FB")) and not part.mpn:
            failures.append(f"{part.ref} hat keine Herstellerteilenummer.")
        if part.ref.startswith("U") and not part.dnp and not part.datasheet:
            failures.append(f"{part.ref} hat keinen Datenblattlink.")
        if "PROVISIONAL" in part.footprint or "PROVISIONAL" in part.note.upper():
            blockers.append(f"{part.ref}: {part.footprint} – {part.note}")

    report_lines = [
        "LandyHeater Revision A – Phase-2-Audit",
        "========================================",
        f"Definitionen: {len(parts)} Referenzen, davon {sum(part.dnp for part in parts)} DNP",
        f"BOM-Gruppen: {len(rows) if BOM.is_file() else 0}",
        f"Strukturelle Fehler: {len(failures)}",
        f"Dokumentierte Freigabesperren: {len(blockers)}",
        "",
    ]
    if failures:
        report_lines += ["FEHLER", "------", *[f"- {item}" for item in failures], ""]
    else:
        report_lines += ["Ergebnis: BOM und exportierte Netzliste stimmen strukturell mit der geprüften Definition überein.", ""]
    report_lines += ["PROVISORISCHE FOOTPRINTS / FREIGABESPERREN", "------------------------------------------"]
    report_lines += [f"- {item}" for item in blockers] or ["- keine"]
    report_lines += [
        "",
        "Hinweis: Ein fehlerfreier Struktur-Audit ersetzt weder Worst-Case-Auslegung, Layoutreview noch Prototypmessungen.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rendered = "\n".join(report_lines) + "\n"
    REPORT.write_text(rendered, encoding="utf-8")
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text(rendered, encoding="utf-8")
    if comparison_lines:
        NETLIST_COMPARISON_REPORT.write_text("\n".join(comparison_lines) + "\n", encoding="utf-8")
    print(f"Phase-2-Audit: {REPORT}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
