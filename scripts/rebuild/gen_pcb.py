"""Generate the 4-layer PCB (placement, nets, rules, zones, silkscreen) from design.py.

Run with KiCad's bundled Python (pcbnew module):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 gen_pcb.py

Board coordinates: mm, origin top-left of the outline, x → right, y ↓ down.
F (L1) = electronics / connector side (rear of the unit); B (L4) = display side.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).parent))
import design  # noqa: E402
import gen_sch  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hardware"
BOARD_FILE = HW / "LandyHeater-Board.kicad_pcb"
KFP = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
LOCAL = HW / "libraries" / "LandyHeater_RevA.pretty"

W, H = 98.0, 48.0
OX, OY = 100.0, 100.0  # board origin on the KiCad sheet


def mm(v):
    return pcbnew.FromMM(v)


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))


# ------------------------------------------------------------------ anchors
# ref: (x, y, rotation_deg, side)   rotation: KiCad positive = counter-clockwise
ANCHORS = {
    # connector edge (top, y = 0): Nano-Fit mating face up
    "J1": (3.5, 11.2, 90, "F"),
    "J2": (21.0, 11.2, 90, "F"),
    "J3": (36.0, 11.2, 90, "F"),
    "J4": (46.0, 11.2, 90, "F"),
    # USB-C on the right edge, opening outward
    "J5": (72.0, 4.0, 180, "F"),
    # ESP32 module, U.FL toward the bottom edge
    "U6": (68.0, 37.4, 180, "F"),
    # local buttons
    "SW2": (52.5, 24.3, 0, "F"),
    "SW1": (52.5, 30.4, 0, "F"),
    "SW3": (33.0, 44.0, 0, "F"),
    # RTC backup cell
    "BT1": (46.5, 40.5, 0, "F"),
    # display FPCs on the display side, insertion toward −x (display)
    "J8": (95.0, 5.6, 90, "B"),
    "J6": (95.0, 21.0, 90, "B"),
    "J7": (95.0, 35.4, 90, "B"),
    # big power parts
    "U1": (11.0, 19.5, 0, "F"),
    "Q1": (4.5, 20.5, 0, "F"),
    "D1": (13.0, 14.8, 0, "F"),
    "C6": (6.0, 31.5, 0, "F"),
    "U5": (10.5, 41.0, 0, "F"),
    "L2": (17.5, 41.0, 0, "F"),
    # diagnostics flow (12V / USB → 3V3 → RUN → HEAT)
    "LED1": (27.0, 27.0, 0, "F"),
    "LED2": (27.0, 33.0, 0, "F"),
    "LED3": (32.0, 30.0, 0, "F"),
    "LED5": (36.5, 30.0, 0, "F"),
    "LED4": (41.0, 30.0, 0, "F"),
    # display isolation, touch, front-light driver
    "U9": (75.0, 16.0, 90, "B"),
    "U19": (86.0, 9.0, 0, "B"),
    "L4": (85.0, 3.5, 0, "B"),
    "L3": (85.5, 21.0, 0, "B"),
}

# placement regions per block: (x0, y0, x1, y1, side)
REGION = {
    "12 V input": (0.8, 12.5, 24.5, 31.0, "F"),
    "USB-C sink": (56.5, 0.8, 97.2, 17.0, "F"),
    "3.3 V buck": (0.8, 31.0, 24.5, 47.2, "F"),
    "ESP32-S3": (49.0, 16.5, 80.0, 47.2, "F"),
    "Switched display": (58.0, 6.0, 80.0, 25.5, "B"),
    "GDEY029T94": (80.2, 12.0, 92.0, 33.0, "B"),
    "3.0 V always-on": (80.2, 33.0, 92.0, 47.2, "B"),
    "Optional wake latch": (80.2, 33.0, 92.0, 47.2, "B"),
    "RTC": (38.0, 30.0, 56.5, 47.2, "B"),
    "AUTOTERM": (18.5, 12.5, 36.0, 24.0, "F"),
    "1-Wire": (33.0, 12.5, 45.0, 24.0, "F"),
    "External APEM": (42.0, 12.5, 57.0, 24.0, "F"),
    "Front light": (80.2, 0.8, 92.0, 13.0, "B"),
    "Energy-flow": (25.0, 22.0, 42.0, 47.2, "B"),
}

HOLES = [(3.2, 44.8), (94.8, 44.8), (13.5, 3.2), (62.0, 3.5)]
HOLE_KEEP = 3.3

# net classes: name -> (track, clearance, via_d, via_drill, nets)
NETCLASSES = {
    # widths limited by the fine-pitch pads they must enter (LM74720 0.5 mm, TUSB321 0.4 mm pitch);
    # 0.3 mm / 1 oz carries > 1 A at 10 K rise, worst-case board current is 0.65 A
    "PWR_12V": (0.3, 0.2, 0.6, 0.3, ["BATT_12V_IN", "VIN_12V_PROT", "FET_DRAIN", "VIN_SYS"]),
    "PWR_LV": (0.25, 0.15, 0.5, 0.25, ["USB_VBUS", "3V3", "3V3_DISP", "3V3_SENSOR", "3V0_AON", "AUTOTERM_5V",
                                      "AUTOTERM_5V_P", "BUCK_SW", "FL_LX", "FL_ISENSE", "FL_LED_A", "FL_LED_K",
                                      "EPD_BOOST_SW", "LED_CC_PLUS", "LED_PWM_MINUS"]),
    "USB": (0.2, 0.15, 0.5, 0.25, ["USB_DP_CONN", "USB_DN_CONN", "USB_DP_MCU", "USB_DN_MCU"]),
    "Default": (0.15, 0.15, 0.5, 0.25, []),
}


def block_region(part):
    for key, reg in REGION.items():
        if part.block.startswith(key):
            return reg
    raise KeyError(part.block)


# ------------------------------------------------------------------ board setup
def new_board():
    board = pcbnew.NewBoard(str(BOARD_FILE))
    board.SetCopperLayerCount(4)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_MinClearance = mm(0.15)
    ds.m_ViasMinSize = mm(0.45)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.m_SolderMaskExpansion = mm(0.05)
    for lid, name in ((pcbnew.F_Cu, "L1_Top"), (pcbnew.In1_Cu, "L2_GND"), (pcbnew.In2_Cu, "L3_PWR"), (pcbnew.B_Cu, "L4_Display")):
        board.SetLayerName(lid, name)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)
    tb = board.GetTitleBlock()
    tb.SetTitle("LandyHeater-Board Rev A (rebuild)")
    tb.SetRevision("A")
    tb.SetDate("2026-10-12")
    tb.SetCompany("LandyHeater")
    tb.SetComment(0, "4 layers 1.6 mm, ENIG, PCBWay. L1 electronics, L2 GND, L3 3V3, L4 display side")
    return board


def outline(board):
    r = 1.5
    pts = [(r, 0), (W - r, 0), (W, r), (W, H - r), (W - r, H), (r, H), (0, H - r), (0, r)]
    segs = [((r, 0), (W - r, 0)), ((W, r), (W, H - r)), ((W - r, H), (r, H)), ((0, H - r), (0, r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(P(*a))
        s.SetEnd(P(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)
    for (sx, sy), (mx, my), (ex, ey) in (((0, r), (r - r * 0.7071, r - r * 0.7071), (r, 0)),
                                        ((W - r, 0), (W - r + r * 0.7071, r - r * 0.7071), (W, r)),
                                        ((W, H - r), (W - r + r * 0.7071, H - r + r * 0.7071), (W - r, H)),
                                        ((r, H), (r - r * 0.7071, H - r + r * 0.7071), (0, H - r))):
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetArcGeometry(P(sx, sy), P(mx, my), P(ex, ey))
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(mm(0.1))
        board.Add(a)


def load_fp(fpid: str):
    lib, name = fpid.split(":")
    path = LOCAL if lib == "LandyHeater_RevA" else KFP / f"{lib}.pretty"
    fp = pcbnew.FootprintLoad(str(path), name)
    if fp is None:
        raise RuntimeError(f"footprint not found {fpid}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def set_field(fp, name, value):
    fp.SetField(name, value or "")
    f = fp.GetField(name)
    if f is not None:
        f.SetVisible(False)
        f.SetLayer(pcbnew.F_Fab)


def courtyard(fp, margin=0.3):
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(layer)
    if cy.OutlineCount():
        bb = cy.BBox()
    else:
        bb = fp.GetBoundingBox(False)
    x0 = pcbnew.ToMM(bb.GetX()) - OX - margin
    y0 = pcbnew.ToMM(bb.GetY()) - OY - margin
    return (x0, y0, x0 + pcbnew.ToMM(bb.GetWidth()) + 2 * margin, y0 + pcbnew.ToMM(bb.GetHeight()) + 2 * margin)


def overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


# ------------------------------------------------------------------ main build
def build():
    board = new_board()
    outline(board)
    nets = {}
    for net in design.nets():
        ni = pcbnew.NETINFO_ITEM(board, net)
        board.Add(ni)
        nets[net] = ni

    # net classes
    ns = board.GetDesignSettings().m_NetSettings
    for cname, (tw, cl, vd, vdr, members) in NETCLASSES.items():
        nc = ns.GetDefaultNetclass() if cname == "Default" else pcbnew.NETCLASS(cname)
        nc.SetTrackWidth(mm(tw))
        nc.SetClearance(mm(cl))
        nc.SetViaDiameter(mm(vd))
        nc.SetViaDrill(mm(vdr))
        if cname == "USB":
            nc.SetDiffPairWidth(mm(0.25))
            nc.SetDiffPairGap(mm(0.15))
        if cname != "Default":
            ns.SetNetclass(cname, nc)
            for n in members:
                ns.SetNetclassPatternAssignment(n, cname)

    sheet_uuid = {key: gen_sch.U("sheet", key) for key, _, _ in design.SHEETS}
    sheet_file = {key: fname for key, fname, _ in design.SHEETS}
    fps = {}
    for part in design.PARTS:
        fp = load_fp(part.footprint)
        fp.SetReference(part.ref)
        fp.SetValue(part.value)
        sym_uuid = gen_sch.U("sym", part.sheet, part.ref)
        fp.SetPath(pcbnew.KIID_PATH(f"/{sheet_uuid[part.sheet]}/{sym_uuid}"))
        set_field(fp, "MPN", part.mpn)
        set_field(fp, "Manufacturer", part.mfr)
        set_field(fp, "LCSC", part.lcsc)
        set_field(fp, "Notes", part.note)
        set_field(fp, "Datasheet", "")
        keep_silk = part.ref[:1] in ("J", "S") or part.ref.startswith(("LED", "TP", "BT"))
        if not keep_silk:
            fp.Reference().SetLayer(pcbnew.F_Fab)
            fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5)))
            fp.Reference().SetTextThickness(mm(0.08))
        else:
            fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.7), mm(0.7)))
            fp.Reference().SetTextThickness(mm(0.12))
        fp.SetSheetfile(sheet_file[part.sheet])
        fp.SetSheetname(part.sheet)
        if part.dnp:
            fp.SetDNP(True)
        if part.symbol == "dev:TestPoint":
            fp.SetExcludedFromBOM(True)
            fp.SetExcludedFromPosFiles(True)
        for pad in fp.Pads():
            num = pad.GetNumber()
            net = part.pins.get(num)
            if num == "" or net is None:
                if num == "" and part.ref == "Q1":
                    pass
                continue
            pad.SetNet(nets[net])
        board.Add(fp)
        fps[part.ref] = fp
    # LFPAK56D paste apertures / secondary drain pads take the drain net
    for pad in fps["Q1"].Pads():
        if pad.GetNumber() in ("", "5", "6", "7", "8"):
            pad.SetNet(nets["FET_DRAIN"])

    occupied = {"F": [], "B": [(57.0, 26.0, 79.5, 48.0), (0.0, 31.0, 24.5, 48.0)]}
    for hx, hy in HOLES:
        for s in ("F", "B"):
            occupied[s].append((hx - HOLE_KEEP, hy - HOLE_KEEP, hx + HOLE_KEEP, hy + HOLE_KEEP))

    def put(fp, x, y, rot, side):
        if side == "B" and not fp.IsFlipped():
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(P(x, y))

    placed = set()
    for ref, (x, y, r, side) in ANCHORS.items():
        put(fps[ref], x, y, r, side)
        occupied[side].append(courtyard(fps[ref]))
        placed.add(ref)
        other = "B" if side == "F" else "F"
        for pad in fps[ref].Pads():
            if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                bb = pad.GetBoundingBox()
                occupied[other].append((pcbnew.ToMM(bb.GetX()) - OX - 0.6, pcbnew.ToMM(bb.GetY()) - OY - 0.6,
                                        pcbnew.ToMM(bb.GetRight()) - OX + 0.6, pcbnew.ToMM(bb.GetBottom()) - OY + 0.6))

    # remaining parts: nearest free spot to connected pads inside the block region
    big_nets = {"GND", "3V3", "VIN_SYS", "3V0_AON", "3V3_DISP", "USB_VBUS"}

    def target_of(part):
        pts = []
        for net in set(n for n in part.pins.values() if n and n not in big_nets):
            for ref, pin in design.nets()[net]:
                if ref in placed and ref != part.ref:
                    for pad in fps[ref].Pads():
                        if pad.GetNumber() == pin:
                            pts.append((pcbnew.ToMM(pad.GetPosition().x) - OX, pcbnew.ToMM(pad.GetPosition().y) - OY))
        if not pts:
            for net in set(n for n in part.pins.values() if n):
                for ref, pin in design.nets()[net]:
                    if ref in placed and ref != part.ref and design.by_ref()[ref].block == part.block:
                        pos = fps[ref].GetPosition()
                        pts.append((pcbnew.ToMM(pos.x) - OX, pcbnew.ToMM(pos.y) - OY))
        if not pts:
            x0, y0, x1, y1, _ = block_region(part)
            return ((x0 + x1) / 2, (y0 + y1) / 2)
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    order = [p for p in design.PARTS if p.ref not in placed]
    # parts that talk to an anchor first, test points last
    order.sort(key=lambda p: (p.symbol == "dev:TestPoint", p.dnp))
    failed = []
    def search(fp, region, tx, ty, side, limit=9000):
        x0, y0, x1, y1 = region
        step = 0.25
        cands = []
        nx, ny = int((x1 - x0) / step), int((y1 - y0) / step)
        for i in range(nx + 1):
            for j in range(ny + 1):
                cx, cy = x0 + i * step, y0 + j * step
                cands.append(((cx - tx) ** 2 + (cy - ty) ** 2, cx, cy))
        cands.sort()
        for _, cx, cy in cands[:limit]:
            for rot in (0, 90):
                put(fp, cx, cy, rot, side)
                cr = courtyard(fp, 0.1 if fp.GetReference().startswith("TP") else 0.3)
                if cr[0] < x0 - 0.01 or cr[1] < y0 - 0.01 or cr[2] > x1 + 0.01 or cr[3] > y1 + 0.01:
                    continue
                if cr[0] < 0.5 or cr[1] < 0.5 or cr[2] > W - 0.5 or cr[3] > H - 0.5:
                    continue
                if any(overlaps(cr, o) for o in occupied[side]):
                    continue
                return (cx, cy, rot, cr)
        return None

    for part in order:
        fp = fps[part.ref]
        x0, y0, x1, y1, side = block_region(part)
        tx, ty = target_of(part)
        best = None
        if part.symbol == "dev:TestPoint":
            side = "F"  # test pads must be reachable in the opened housing
            tries = [((x0, y0, x1, y1), 6000), ((0.5, 12.5, W - 0.5, H - 0.5), 30000)]
        else:
            tries = [((x0, y0, x1, y1), 9000), ((x0 - 6, y0 - 6, x1 + 6, y1 + 6), 20000),
                     ((0.5, 0.5, W - 0.5, H - 0.5), 60000)]
        for reg, lim in tries:
            best = search(fp, reg, tx, ty, side, lim)
            if best:
                break
        if not best:
            failed.append(part.ref)
            put(fp, W + 10 + len(failed) * 4, 10, 0, side)
            continue
        put(fp, best[0], best[1], best[2], side)
        occupied[side].append(best[3])
        placed.add(part.ref)
    return board, fps, nets, failed


def add_holes(board):
    for i, (x, y) in enumerate(HOLES):
        fp = load_fp("MountingHole:MountingHole_2.7mm_M2.5_Pad_Via")
        fp.SetReference(f"H{i + 1}")
        fp.SetValue("M2.5")
        fp.SetPosition(P(x, y))
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
        fp.SetBoardOnly(True)
        gnd = board.FindNet("GND")
        for pad in fp.Pads():
            pad.SetNet(gnd)
        board.Add(fp)


def add_zone(board, layer, netname, margin=0.4, priority=0, name=""):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(netname))
    z.SetZoneName(name or netname)
    poly = pcbnew.SHAPE_POLY_SET()
    chain = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in ((margin, margin), (W - margin, margin), (W - margin, H - margin), (margin, H - margin)):
        chain.Append(mm(OX + x), mm(OY + y))
    chain.SetClosed(True)
    poly.AddOutline(chain)
    poly.thisown = 0  # ZONE takes ownership
    z.SetOutline(poly)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(0.25))
    z.SetMinThickness(mm(0.2))
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    board.Add(z)
    return z


def silk_text(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS, bold=False, rot=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(P(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * (0.2 if bold else 0.15)))
    t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    board.Add(t)


def silk_line(board, a, b, layer=pcbnew.F_SilkS, w=0.15):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(*a))
    s.SetEnd(P(*b))
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    board.Add(s)


def pos(fps, ref):
    p = fps[ref].GetPosition()
    return pcbnew.ToMM(p.x) - OX, pcbnew.ToMM(p.y) - OY


def silkscreen(board, fps):
    for ref, label in (("J1", "12V IN"), ("J2", "AUTOTERM"), ("J3", "1-WIRE"), ("J4", "BUTTON/LED")):
        x, y = pos(fps, ref)
        silk_text(board, label, x + 3.5 if ref != "J1" else x + 2.2, 13.6 if ref != "J1" else 12.9, 0.8)
    silk_text(board, "USB-C", 72.0, 10.2, 0.8)
    # diagnostics energy-flow drawing
    l1, l2, l3, l5, l4 = (pos(fps, r) for r in ("LED1", "LED2", "LED3", "LED5", "LED4"))
    silk_text(board, "12V", l1[0], l1[1] - 1.6, 0.8)
    silk_text(board, "USB", l2[0], l2[1] + 1.6, 0.8)
    silk_text(board, "3V3", l3[0], l3[1] - 1.6, 0.8)
    silk_text(board, "RUN", l5[0], l5[1] - 1.6, 0.8)
    silk_text(board, "HEAT", l4[0], l4[1] - 1.6, 0.8)
    silk_line(board, (l1[0] + 1.3, l1[1]), (l3[0] - 2.2, l1[1]))
    silk_line(board, (l2[0] + 1.3, l2[1]), (l3[0] - 2.2, l2[1]))
    silk_line(board, (l3[0] - 2.2, l1[1]), (l3[0] - 2.2, l2[1]))
    silk_line(board, (l3[0] - 2.2, l3[1]), (l3[0] - 1.3, l3[1]))
    silk_line(board, (l3[0] + 1.3, l3[1]), (l5[0] - 1.3, l5[1]))
    silk_line(board, (l5[0] + 1.3, l5[1]), (l4[0] - 1.3, l4[1]))
    for ref, label in (("SW1", "RESET"), ("SW2", "BOOT"), ("SW3", "DIAG")):
        x, y = pos(fps, ref)
        silk_text(board, label, x, y + (3.7 if ref != "SW3" else -3.6), 0.8)
    x, y = pos(fps, "BT1")
    silk_text(board, "BR1225 (+ up)", x, y - 7.6, 0.8)
    silk_text(board, "LandyHeater-Board Rev A", 49.0, 46.6, 0.9, bold=True)
    silk_text(board, "LandyHeater Rev A – display side", 40.0, 24.0, 1.2, layer=pcbnew.B_SilkS, bold=True)
    for ref, label in (("J6", "E-PAPER"), ("J7", "TOUCH"), ("J8", "FRONTLIGHT")):
        x, y = pos(fps, ref)
        silk_text(board, label, x - 5.8, y, 0.8, layer=pcbnew.B_SilkS, rot=90)
    # display outline (79 x 36.7 mm) on B.Fab for mechanics
    dx0, dy0 = 0.8, (H - 36.7) / 2
    for a, b in (((dx0, dy0), (dx0 + 79, dy0)), ((dx0 + 79, dy0), (dx0 + 79, dy0 + 36.7)),
                 ((dx0 + 79, dy0 + 36.7), (dx0, dy0 + 36.7)), ((dx0, dy0 + 36.7), (dx0, dy0))):
        silk_line(board, a, b, layer=pcbnew.B_Fab, w=0.1)
    silk_text(board, "GDEY029T94-FT01 outline 79 x 36.7", 40, 41.5, 1.0, layer=pcbnew.B_Fab)


def main():
    board, fps, nets, failed = build()
    add_holes(board)
    add_zone(board, pcbnew.In1_Cu, "GND", name="L2_GND")
    # L3 3V3 pour is added after routing (route.py) so L3 stays a routing layer
    add_zone(board, pcbnew.F_Cu, "GND", name="L1_GND_fill")
    add_zone(board, pcbnew.B_Cu, "GND", name="L4_GND_fill")
    silkscreen(board, fps)
    board.Save(str(BOARD_FILE))
    print("unplaced:", failed)


if __name__ == "__main__":
    main()
