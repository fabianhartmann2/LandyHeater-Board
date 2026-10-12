"""Autoroute the generated board with Freerouting and refill zones.

Usage (KiCad Python):  python3.9 route.py [max_passes]
Inner planes L2 (GND) and L3 (3V3) are exported as Specctra planes, so
Freerouting connects those nets with vias.  The outer GND fills are removed
for routing and re-created afterwards.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import gen_pcb  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "hardware" / "LandyHeater-Board.kicad_pcb"
BUILD = ROOT / "build" / "route"
JAVA = "/opt/homebrew/opt/openjdk@21/bin/java"
JAR = Path.home() / ".local/share/freerouting/freerouting-2.1.0.jar"


def main():
    passes = sys.argv[1] if len(sys.argv) > 1 else "100"
    import_only = "--import-only" in sys.argv
    BUILD.mkdir(parents=True, exist_ok=True)
    board = pcbnew.LoadBoard(str(BOARD))
    for z in list(board.Zones()):
        if z.GetLayer() in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In2_Cu):
            board.Remove(z)
    try:
        tracks = list(board.GetTracks())
    except TypeError:
        tracks = []
    for t in tracks:
        board.Remove(t)
    dsn = BUILD / "board.dsn"
    ses = BUILD / "board.ses"
    if not import_only:
        if ses.exists():
            ses.unlink()
        if not pcbnew.ExportSpecctraDSN(board, str(dsn)):
            raise SystemExit("DSN export failed")
    cmd = [JAVA, "-Djava.awt.headless=true", "-jar", str(JAR), "-de", str(dsn), "-do", str(ses),
           "-mp", passes, f"--router.max_passes={passes}", "--router.job_timeout=00:35:00", "-mt", "8", "--gui.enabled=false"]
    if not import_only:
        print(" ".join(cmd), flush=True)
        log = open(BUILD / "freerouting.log", "w")
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False)
    if not ses.exists():
        raise SystemExit("Freerouting produced no session file – see build/route/freerouting.log")
    if not pcbnew.ImportSpecctraSES(board, str(ses)):
        raise SystemExit("SES import failed")
    gen_pcb.add_zone(board, pcbnew.In2_Cu, "3V3", name="L3_3V3")
    gen_pcb.add_zone(board, pcbnew.F_Cu, "GND", name="L1_GND_fill")
    gen_pcb.add_zone(board, pcbnew.B_Cu, "GND", name="L4_GND_fill")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(str(BOARD))
    print("routed and saved")


if __name__ == "__main__":
    main()
