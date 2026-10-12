"""Manufacturing export for PCBWay: Gerber + drill, pick&place, BOM, PDFs, STEP, DRC/ERC reports."""
from __future__ import annotations

import csv
import shutil
import subprocess
import zipfile
from collections import OrderedDict
from pathlib import Path

import design

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hardware"
OUT = ROOT / "manufacturing" / "RevA_rebuild"
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
PCB = HW / "LandyHeater-Board.kicad_pcb"
SCH = HW / "LandyHeater-Board.kicad_sch"


def run(*args):
    r = subprocess.run([CLI, *args], capture_output=True, text=True)
    if r.returncode not in (0, 5):
        print(r.stdout, r.stderr)
        raise SystemExit(f"kicad-cli failed: {args[:3]}")
    return r


def package(fp: str) -> str:
    name = fp.split(":")[1]
    for key in ("0603", "0805", "1206", "1210", "SOT-23-6", "SOT-23-5", "SOT-23", "SC-70-5", "SC-70-6", "SOT-323",
                "SOD-123", "SOD-323", "SOD-523", "SMA", "SMB", "TSSOP-24", "VSSOP-8", "MSOP-8", "HSOP-8"):
        if key in name:
            return key
    return name


def bom():
    groups: "OrderedDict[tuple, list]" = OrderedDict()
    for p in design.PARTS:
        if p.symbol == "dev:TestPoint":
            continue
        key = (p.value, p.footprint, p.mfr, p.mpn, p.lcsc, p.dnp)
        groups.setdefault(key, []).append(p)
    path = OUT / "BOM_LandyHeater_RevA_PCBWay.csv"
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Item", "Designator", "Qty", "Value", "Manufacturer", "Manufacturer Part Number", "LCSC Part #",
                    "Package", "Type", "Populate", "Notes"])
        item = 0
        for (value, fp, mfr, mpn, lcsc, dnp), parts in sorted(groups.items(), key=lambda kv: (kv[0][5], kv[1][0].ref[0], kv[1][0].ref)):
            item += 1
            refs = sorted((x.ref for x in parts), key=lambda r: (r.rstrip("0123456789"), int(''.join(c for c in r if c.isdigit()) or 0)))
            tht = "THT" if "Nano-Fit" in fp else "SMD"
            notes = "; ".join(sorted({x.note for x in parts if x.note}))
            w.writerow([item, ",".join(refs), len(parts), value, mfr, mpn, lcsc, package(fp), tht,
                        "DNP" if dnp else "Yes", notes])
    return path


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "gerber").mkdir(parents=True)
    rep = ROOT / "build" / "reports"
    rep.mkdir(parents=True, exist_ok=True)
    run("sch", "erc", "--severity-all", "--output", str(OUT / "ERC_report.rpt"), str(SCH))
    run("pcb", "drc", "--severity-all", "--schematic-parity", "--refill-zones", "--output", str(OUT / "DRC_report.rpt"), str(PCB))
    layers = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
    run("pcb", "export", "gerbers", "--layers", layers, "--subtract-soldermask", "--use-drill-file-origin",
        "--output", str(OUT / "gerber"), str(PCB))
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map",
        "--map-format", "gerberx2", "--output", str(OUT / "gerber") + "/", str(PCB))
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp",
        "--output", str(OUT / "CPL_LandyHeater_RevA.csv"), str(PCB))
    run("sch", "export", "pdf", "--output", str(OUT / "Schematic_LandyHeater_RevA.pdf"), str(SCH))
    run("pcb", "export", "pdf", "--layers", "F.Cu,F.Silkscreen,F.Fab,Edge.Cuts", "--include-border-title",
        "--output", str(OUT / "Assembly_Top.pdf"), str(PCB))
    run("pcb", "export", "pdf", "--layers", "B.Cu,B.Silkscreen,B.Fab,Edge.Cuts", "--mirror", "--include-border-title",
        "--output", str(OUT / "Assembly_Bottom_display_side.pdf"), str(PCB))
    run("pcb", "export", "step", "--subst-models", "--output", str(OUT / "LandyHeater_RevA.step"), str(PCB))
    bom()
    with zipfile.ZipFile(OUT / "Gerber_LandyHeater_RevA_PCBWay.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((OUT / "gerber").iterdir()):
            z.write(f, f.name)
    print("exported to", OUT)


if __name__ == "__main__":
    main()
