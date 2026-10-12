"""Compare the KiCad-exported netlist (and optionally the PCB) pin by pin with design.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import design
import sexpr

ROOT = Path(__file__).resolve().parents[2]
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"


def kicad_netlist() -> dict[tuple[str, str], str]:
    out = ROOT / "build" / "reports" / "netlist.net"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "--output", str(out),
                    str(ROOT / "hardware" / "LandyHeater-Board.kicad_sch")], check=True, capture_output=True)
    tree = sexpr.parse(out.read_text())[0]
    nets = sexpr.find(tree, "nets")
    pinmap = {}
    for net in sexpr.find_all(nets, "net"):
        name = sexpr.find(net, "name")[1].lstrip("/")
        for node in sexpr.find_all(net, "node"):
            ref = sexpr.find(node, "ref")[1]
            pin = sexpr.find(node, "pin")[1]
            if ref.startswith("#"):
                continue
            pinmap[(ref, pin)] = name
    return pinmap


def expected() -> dict[tuple[str, str], str | None]:
    return {(p.ref, pin): net for p in design.PARTS for pin, net in p.pins.items()}


def compare(actual: dict, label: str) -> int:
    exp = expected()
    errors = 0
    # group actual pins by net, expected pins by net, compare as partitions
    for key, net in exp.items():
        got = actual.get(key)
        if net is None:
            if got is not None and not got.startswith("unconnected-"):
                print(f"[{label}] {key} expected NC, got {got}")
                errors += 1
            continue
        if got != net:
            print(f"[{label}] {key} expected {net}, got {got}")
            errors += 1
    extra = set(actual) - set(exp)
    for k in sorted(extra):
        print(f"[{label}] unexpected pin {k} on {actual[k]}")
        errors += 1
    return errors


if __name__ == "__main__":
    n = compare(kicad_netlist(), "schematic")
    print(f"schematic netlist check: {n} differences, {len(expected())} pins compared")
    sys.exit(1 if n else 0)
