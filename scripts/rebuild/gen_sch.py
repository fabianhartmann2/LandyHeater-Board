"""Generate the hierarchical KiCad schematic from design.py.

Every pin gets a short wire stub that ends in a global label, a GND symbol or
a no-connect flag.  Parts are grouped in titled functional blocks.  Correctness
is verified afterwards by exporting the netlist with kicad-cli and comparing
it pin by pin with design.py (see verify.py).
"""
from __future__ import annotations

import math
import uuid
from pathlib import Path

import design
import sexpr
import symbols
from sexpr import Sym

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hardware"
PROJECT = "LandyHeater-Board"
GRID = 1.27
STUB = 2.54


def U(*parts) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "landyheater-sch/" + "/".join(map(str, parts))))


def snap(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


ROOT_UUID = U("root")


# ------------------------------------------------------------------ symbol cache
class SymInfo:
    def __init__(self, lib_id: str, sym: list):
        self.lib_id = lib_id
        self.sym = sym
        self.pins = symbols.pin_positions(sym)
        self.types = {}

        def walk(n):
            for c in n:
                if isinstance(c, list) and c:
                    if c[0] == "pin":
                        self.types[sexpr.find(c, "number")[1]] = str(c[1])
                    elif c[0] == "symbol":
                        walk(c)
        walk(sym)
        xs = [p[0] for p in self.pins.values()] or [0]
        ys = [p[1] for p in self.pins.values()] or [0]
        bx, by = [], []

        def body(n):
            for c in n:
                if isinstance(c, list) and c:
                    if c[0] == "rectangle":
                        st, en = sexpr.find(c, "start"), sexpr.find(c, "end")
                        bx.extend([float(st[1]), float(en[1])]); by.extend([float(st[2]), float(en[2])])
                    elif c[0] == "polyline":
                        for xy in sexpr.find_all(sexpr.find(c, "pts"), "xy"):
                            bx.append(float(xy[1])); by.append(float(xy[2]))
                    elif c[0] == "circle":
                        ce, r = sexpr.find(c, "center"), float(sexpr.find(c, "radius")[1])
                        bx.extend([float(ce[1]) - r, float(ce[1]) + r]); by.extend([float(ce[2]) - r, float(ce[2]) + r])
                    elif c[0] == "symbol":
                        body(c)
        body(sym)
        self.body = (min(bx or [0]), min(by or [0]), max(bx or [0]), max(by or [0]))
        self.bbox = (min(xs + bx), min(ys + by), max(xs + bx), max(ys + by))


_syms: dict[str, SymInfo] = {}


def info(sym_key: str) -> SymInfo:
    if sym_key not in _syms:
        lib_id, s = symbols.symbol_for(sym_key)
        _syms[sym_key] = SymInfo(lib_id, s)
    return _syms[sym_key]


def rot(px, py, r):
    a = math.radians(r)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)


DIRS = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}  # screen vectors


class Placed:
    def __init__(self, part: design.Part):
        self.part = part
        self.si = info(part.symbol)
        self.rot = self.choose_rotation()
        self.x = self.y = 0.0

    def choose_rotation(self) -> int:
        pins = self.si.pins
        if not self.part.symbol.startswith("dev:") or self.part.symbol in ("dev:D_SOT23", "dev:D_Dual_CA", "dev:D_TVS_uni"):
            return 0
        if len(pins) == 2:
            (a, b) = list(pins.values())
            if abs(a[0] - b[0]) < 0.01:  # vertical pins → make horizontal
                # put pin "1" left
                p1 = pins.get("1", a)
                return 90 if p1[1] > 0 else 270
            p1 = pins.get("1", a)
            return 0 if p1[0] < 0 else 180
        if len(pins) == 1:
            return 90
        return 0

    def pin_screen(self, num):
        px, py, pa = self.si.pins[num]
        rx, ry = rot(px, py, self.rot)
        out = int(round((pa + 180 + self.rot) % 360)) % 360
        return self.x + rx, self.y - ry, out

    def extent(self):
        """bounding box relative to origin incl. stubs and labels."""
        xs, ys = [], []
        for num, net in self.part.pins.items():
            if num not in self.si.pins:
                continue
            px, py, pa = self.si.pins[num]
            rx, ry = rot(px, py, self.rot)
            sx, sy = rx, -ry
            out = int(round((pa + 180 + self.rot) % 360)) % 360
            dx, dy = DIRS[out]
            L = STUB + (label_len(net) if net and net != "GND" else 3.0)
            xs += [sx, sx + dx * L]
            ys += [sy, sy + dy * L]
        bx0, by0, bx1, by1 = self.si.bbox
        corners = [rot(bx0, by0, self.rot), rot(bx1, by1, self.rot)]
        xs += [c[0] for c in corners]
        ys += [-c[1] for c in corners]
        # reference/value text
        ys += [min(ys) - 3.0, max(ys) + 3.0]
        return min(xs) - 1.5, min(ys), max(xs) + 1.5, max(ys)


def label_len(net: str | None) -> float:
    if not net:
        return 0
    return len(net) * 1.05 + 3.5


# ------------------------------------------------------------------ layout
SHEET_W, SHEET_H = 420.0, 297.0  # A3
MARGIN_X0, MARGIN_Y0, MARGIN_X1, MARGIN_Y1 = 15.0, 22.0, 405.0, 265.0


def layout_block(parts: list[Placed], max_w: float):
    """Row packing; returns (items with relative positions, w, h)."""
    rows, row, row_w = [], [], 0.0
    for p in parts:
        x0, y0, x1, y1 = p.extent()
        w = x1 - x0 + 3
        if row and row_w + w > max_w:
            rows.append(row)
            row, row_w = [], 0.0
        row.append((p, w, (x0, y0, x1, y1)))
        row_w += w
    if row:
        rows.append(row)
    y = 8.0  # title space
    width = 0.0
    for row in rows:
        h = max(e[3] - e[1] for _, _, e in row)
        x = 2.0
        for p, w, (x0, y0, x1, y1) in row:
            p.x = x - x0
            p.y = y - y0 + (h - (y1 - y0)) / 2
            x += w
        width = max(width, x)
        y += h + 1.5
    return width, y


PAPERS = [("A4", 297.0, 210.0), ("A3", 420.0, 297.0), ("A2", 594.0, 420.0)]


def build_sheet(sheet_key: str):
    for paper, w, h in PAPERS:
        for ncols in (1, 2, 3):
            res = _build_sheet(sheet_key, w, h, ncols)
            if res[1] <= h - 30:
                return res + (paper,)
    return res + ("A2",)


def _build_sheet(sheet_key: str, pw: float, ph: float, ncols: int):
    blocks: dict[str, list[Placed]] = {}
    for part in design.PARTS:
        if part.sheet == sheet_key:
            blocks.setdefault(part.block, []).append(Placed(part))
    col_w = (pw - 2 * MARGIN_X0 - 6 * (ncols - 1)) / ncols
    laid = []
    for name, plist in blocks.items():
        w, h = layout_block(plist, col_w - 6)
        laid.append((name, plist, w, h))
    # place blocks: big ones full width if they do not fit in a column
    cols_y = [MARGIN_Y0] * ncols
    placed_blocks = []
    for name, plist, w, h in laid:
        c = cols_y.index(min(cols_y))
        bx = MARGIN_X0 + c * (col_w + 6)
        by = cols_y[c]
        cols_y[c] += h + 6
        placed_blocks.append((name, plist, bx, by, col_w, h))
    height_needed = max(cols_y)
    return placed_blocks, height_needed


# ------------------------------------------------------------------ emit
def prop(name, value, x, y, hide=False, size=1.27, angle=0, justify=None):
    eff = [Sym("effects"), [Sym("font"), [Sym("size"), size, size]]]
    if justify:
        eff.append([Sym("justify"), Sym(justify)])
    if hide:
        eff.append([Sym("hide"), Sym("yes")])
    return [Sym("property"), name, value, [Sym("at"), snap(x), snap(y), angle], eff]


def wire(a, b, key):
    return [Sym("wire"), [Sym("pts"), [Sym("xy"), snap(a[0]), snap(a[1])], [Sym("xy"), snap(b[0]), snap(b[1])]],
            [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]], [Sym("uuid"), U(*key)]]


def glabel(net, at, angle, key):
    just = {0: "left", 180: "right", 90: "left", 270: "right"}[angle]
    return [Sym("global_label"), net, [Sym("shape"), Sym("passive")], [Sym("at"), snap(at[0]), snap(at[1]), angle],
            [Sym("fields_autoplaced"), Sym("yes")],
            [Sym("effects"), [Sym("font"), [Sym("size"), 1.0, 1.0]], [Sym("justify"), Sym(just)]],
            [Sym("uuid"), U(*key)],
            [Sym("property"), "Intersheetrefs", "${INTERSHEET_REFS}", [Sym("at"), 0, 0, 0],
             [Sym("effects"), [Sym("font"), [Sym("size"), 1.0, 1.0]], [Sym("hide"), Sym("yes")]]]]


def no_connect(at, key):
    return [Sym("no_connect"), [Sym("at"), snap(at[0]), snap(at[1])], [Sym("uuid"), U(*key)]]


def text(s, x, y, size=1.8, bold=True, key=()):
    font = [Sym("font"), [Sym("size"), size, size]] + ([[Sym("bold"), Sym("yes")]] if bold else [])
    return [Sym("text"), s, [Sym("exclude_from_sim"), Sym("no")], [Sym("at"), snap(x), snap(y), 0],
            [Sym("effects"), font, [Sym("justify"), Sym("left"), Sym("bottom")]], [Sym("uuid"), U("text", *key)]]


def rect(x0, y0, x1, y1, key):
    return [Sym("rectangle"), [Sym("start"), x0, y0], [Sym("end"), x1, y1],
            [Sym("stroke"), [Sym("width"), 0.2], [Sym("type"), Sym("dash")]], [Sym("fill"), [Sym("type"), Sym("none")]],
            [Sym("uuid"), U("rect", *key)]]


def symbol_instance(lib_id, ref, value, x, y, r, sheet_path, key, fields=None, pins=(), dnp=False, in_bom=True,
                    on_board=True, ref_at=None, val_at=None, hide_value=False):
    s = [Sym("symbol"), [Sym("lib_id"), lib_id], [Sym("at"), snap(x), snap(y), r], [Sym("unit"), 1],
         [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("yes" if in_bom else "no")],
         [Sym("on_board"), Sym("yes" if on_board else "no")], [Sym("dnp"), Sym("yes" if dnp else "no")],
         [Sym("uuid"), U("sym", *key)]]
    rx, ry = ref_at or (x, y - 3)
    vx, vy = val_at or (x, y + 3)
    fa = (360 - r) % 360 if r in (90, 270) else 0
    s.append(prop("Reference", ref, rx, ry, angle=fa))
    s.append(prop("Value", value, vx, vy, hide=hide_value, angle=fa))
    for k, v in (fields or {}).items():
        s.append(prop(k, v, x, y, hide=True))
    for pn in pins:
        s.append([Sym("pin"), pn, [Sym("uuid"), U("pin", *key, pn)]])
    s.append([Sym("instances"), [Sym("project"), PROJECT,
                                 [Sym("path"), sheet_path, [Sym("reference"), ref], [Sym("unit"), 1]]]])
    return s


def gen_child(sheet_key, filename, title, page, sheet_uuid):
    placed_blocks, height, paper = build_sheet(sheet_key)
    items = []
    lib_syms = {}
    sheet_path = f"/{ROOT_UUID}/{sheet_uuid}"
    gnd = info("dev:GND")
    lib_syms[gnd.lib_id] = gnd.sym
    gnd_count = 0
    for bi, (bname, plist, bx, by, bw, bh) in enumerate(placed_blocks):
        items.append(rect(snap(bx), snap(by), snap(bx + bw), snap(by + bh), (sheet_key, bi)))
        items.append(text(bname, bx + 2, by + 5, 1.6, True, (sheet_key, bi)))
        for p in plist:
            p.x = snap(bx + p.x)
            p.y = snap(by + p.y)
            part = p.part
            lib_syms[p.si.lib_id] = p.si.sym
            fields = {"Footprint": part.footprint, "Datasheet": "", "Manufacturer": part.mfr, "MPN": part.mpn,
                      "LCSC": part.lcsc, "Notes": part.note}
            x0, y0, x1, y1 = p.extent()
            single = len(p.si.pins) <= 2
            b0x, b0y, b1x, b1y = p.si.body
            ref_at = (p.x, p.y - 2.6) if single else (p.x + 0, p.y - b1y - 1.6)
            val_at = (p.x, p.y + 2.6) if single else (p.x, p.y - b0y + 1.9)
            if len(p.si.pins) == 1:
                ref_at, val_at = (p.x, p.y - 3.2), (p.x + 2.0, p.y - 5.4)
            value = part.value + (" (DNP)" if part.dnp else "")
            items.append(symbol_instance(p.si.lib_id, part.ref, value, p.x, p.y, p.rot, sheet_path,
                                         (sheet_key, part.ref), fields, list(p.si.pins.keys()), dnp=part.dnp,
                                         in_bom=part.symbol != "dev:TestPoint" or False,
                                         ref_at=ref_at, val_at=val_at))
            for num in p.si.pins:
                net = part.pins.get(num)
                sx, sy, out = p.pin_screen(num)
                dx, dy = DIRS[out]
                key = (sheet_key, part.ref, num)
                if net is None:
                    items.append(no_connect((sx, sy), key))
                    continue
                ex, ey = sx + dx * STUB, sy + dy * STUB
                items.append(wire((sx, sy), (ex, ey), key + ("stub",)))
                if net == "GND":
                    if out == 270:
                        gx, gy, gr = ex, ey, 0
                    elif out == 90:
                        gx, gy, gr = ex, ey, 180
                    elif out == 0:
                        gx, gy, gr = ex, ey, 90
                    else:
                        gx, gy, gr = ex, ey, 270
                    gnd_count += 1
                    items.append(symbol_instance(gnd.lib_id, f"#PWR{sheet_key}{gnd_count:03d}", "GND", gx, gy, gr,
                                                 sheet_path, (sheet_key, "gnd", gnd_count), {"Footprint": ""},
                                                 list(gnd.pins.keys()), in_bom=False, on_board=False,
                                                 ref_at=(gx, gy + 6), val_at=(gx, gy + 3.5)))
                    items[-1][items[-1].index([p_ for p_ in items[-1] if isinstance(p_, list) and p_ and p_[0] == "property" and p_[1] == "Reference"][0])][4].append([Sym("hide"), Sym("yes")])
                else:
                    items.append(glabel(net, (ex, ey), out, key + ("lbl",)))
    # power flags on this sheet for nets that need a driver
    flags = power_flags_for_sheet(sheet_key)
    fx = MARGIN_X0 + 4
    fy = height + 6
    if flags:
        items.append(text("Power flags (ERC: nets driven from connectors/passives)", fx, fy - 4, 1.27, False, (sheet_key, "pf")))
    pf = info("dev:PWR_FLAG")
    if flags:
        lib_syms[pf.lib_id] = pf.sym
    for i, net in enumerate(flags):
        x = fx + i * 28
        y = fy + 4
        items.append(symbol_instance(pf.lib_id, f"#FLG{sheet_key}{i:02d}", "PWR_FLAG", x, y, 0, sheet_path,
                                     (sheet_key, "flag", net), {"Footprint": ""}, list(pf.pins.keys()),
                                     in_bom=False, on_board=False, ref_at=(x, y - 5), val_at=(x, y - 3.5)))
        items[-1][[k for k, v in enumerate(items[-1]) if isinstance(v, list) and v and v[0] == "property" and v[1] == "Reference"][0]][4].append([Sym("hide"), Sym("yes")])
        if net == "GND":
            g = (x, y + STUB)
            items.append(wire((x, y), g, (sheet_key, "flagw", net)))
            items.append(symbol_instance(gnd.lib_id, f"#PWR{sheet_key}F{i:02d}", "GND", g[0], g[1], 0, sheet_path,
                                         (sheet_key, "flaggnd", net), {"Footprint": ""}, list(gnd.pins.keys()),
                                         in_bom=False, on_board=False, ref_at=(g[0], g[1] + 6), val_at=(g[0], g[1] + 3.5)))
        else:
            items.append(wire((x, y), (x, y + STUB), (sheet_key, "flagw", net)))
            items.append(glabel(net, (x, y + STUB), 270, (sheet_key, "flaglbl", net)))
    head = [Sym("kicad_sch"), [Sym("version"), 20250114], [Sym("generator"), "eeschema"],
            [Sym("generator_version"), "10.0"], [Sym("uuid"), sheet_uuid], [Sym("paper"), paper],
            title_block(title, page),
            [Sym("lib_symbols")] + list(lib_syms.values())]
    return head + items


def title_block(title, page):
    return [Sym("title_block"), [Sym("title"), f"LandyHeater-Board Rev A – {title}"], [Sym("date"), "2026-10-12"],
            [Sym("rev"), "A (rebuild)"], [Sym("company"), "LandyHeater"],
            [Sym("comment"), 1, "Generated from scripts/rebuild/design.py – edit the definition, not this file"],
            [Sym("comment"), 2, "Spec v1.6 with documented deviations DEV-xx (docs/Rebuild_Abweichungen_RevA.md)"]]


_flag_plan: dict[str, list[str]] | None = None


def power_flags_for_sheet(sheet_key):
    global _flag_plan
    if _flag_plan is None:
        need: dict[str, bool] = {}
        driven: dict[str, bool] = {}
        first_sheet: dict[str, str] = {}
        for part in design.PARTS:
            si = info(part.symbol)
            for num, net in part.pins.items():
                if not net:
                    continue
                t = si.types.get(num, "passive")
                if t == "power_in":
                    need[net] = True
                if t == "power_out":
                    driven[net] = True
                first_sheet.setdefault(net, part.sheet)
        need["GND"] = True
        _flag_plan = {}
        for net in sorted(need):
            if not driven.get(net):
                sk = "Power" if net in ("GND",) else first_sheet[net]
                _flag_plan.setdefault(sk, []).append(net)
    return _flag_plan.get(sheet_key, [])


def gen_root(sheet_uuids):
    items = []
    x, y = 25.4, 40.64
    for i, (key, fname, title) in enumerate(design.SHEETS):
        su = sheet_uuids[key]
        sx = 25.4 + (i % 3) * 120
        sy = 40.64 + (i // 3) * 60
        items.append([Sym("sheet"), [Sym("at"), sx, sy], [Sym("size"), 101.6, 40.64],
                      [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("yes")], [Sym("on_board"), Sym("yes")],
                      [Sym("dnp"), Sym("no")], [Sym("fields_autoplaced"), Sym("yes")],
                      [Sym("stroke"), [Sym("width"), 0.1524], [Sym("type"), Sym("solid")]],
                      [Sym("fill"), [Sym("color"), 0, 0, 0, 0.0]],
                      [Sym("uuid"), su],
                      [Sym("property"), "Sheetname", f"{i + 1}. {title}", [Sym("at"), sx, sy - 0.71, 0],
                       [Sym("effects"), [Sym("font"), [Sym("size"), 1.6, 1.6]], [Sym("justify"), Sym("left"), Sym("bottom")]]],
                      [Sym("property"), "Sheetfile", fname, [Sym("at"), sx, sy + 41.2, 0],
                       [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]], [Sym("justify"), Sym("left"), Sym("top")]]],
                      [Sym("instances"), [Sym("project"), PROJECT, [Sym("path"), f"/{ROOT_UUID}", [Sym("page"), str(i + 2)]]]]])
        summary = {
            "Power": "J1 12 V → TVS → LM74720-Q1 + BUK7K17 → FB → VIN_SYS\nUSB-C → TUSB321AI / USBLC6 → TPS259470L → VIN_SYS\nVIN_SYS → LMR33630C 2.1 MHz → 3V3",
            "MCU": "ESP32-S3-WROOM-1U-N16R8, native USB, TPS3808 supervisor,\nBOOT/RESET, UART0 test pads, SPI series resistors",
            "Display": "TPS22919 display rail, AXC8T245/AXC1T45 power-off isolation,\nGDEY029T94 booster per Good Display ch. 12, J6 24p FPC",
            "Touch_RTC": "TPS7A02 3.0 V always-on, I²C pull-ups, touch FPC J7,\nLVC1G07 reset, DNP wake latch, RV-3028-C7 + BR1225",
            "IO": "J2 AUTOTERM 5 V UART via TXU0202-Q1 (OE default low),\nJ3 1-Wire with TPS22945 switched sensor supply",
            "Controls": "J4 button + ring LED (BCR421, PTC), AL8861 front light → J8,\nDIAG-gated energy-flow LEDs, optional status LEDs (DNP)",
        }[key]
        items.append(text(summary, sx + 2, sy + 12, 1.27, False, ("root", key)))
    items.append(text("LandyHeater-Board Rev A – rebuild 2026-10. All pins are connected by net name (global labels).", 25.4, 30, 2.0, True, ("root", "t")))
    items.append(text("Function: AUTOTERM/Planar heater controller – 5 V UART, 3 × DS18B20, 2.9\" e-paper with touch and front light,\n"
                      "external illuminated button, RTC with backup cell, Wi-Fi (U.FL), native USB. 12 V vehicle supply or USB-C.",
                      25.4, 175, 1.5, False, ("root", "f")))
    head = [Sym("kicad_sch"), [Sym("version"), 20250114], [Sym("generator"), "eeschema"],
            [Sym("generator_version"), "10.0"], [Sym("uuid"), ROOT_UUID], [Sym("paper"), "A3"],
            title_block("Overview", 1), [Sym("lib_symbols")]]
    tail = [[Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]]]
    return head + items + tail


def main():
    sheet_uuids = {key: U("sheet", key) for key, _, _ in design.SHEETS}
    # validate symbol pins vs design pins
    errors = []
    for part in design.PARTS:
        si = info(part.symbol)
        a, b = set(si.pins), set(part.pins)
        if a != b:
            errors.append(f"{part.ref}: symbol pins {sorted(a - b)} not in design, design pins {sorted(b - a)} not in symbol")
    if errors:
        raise SystemExit("\n".join(errors))
    for i, (key, fname, title) in enumerate(design.SHEETS):
        tree = gen_child(key, fname, title, i + 2, sheet_uuids[key])
        (HW / fname).write_text(sexpr.dump(tree) + "\n")
    (HW / f"{PROJECT}.kicad_sch").write_text(sexpr.dump(gen_root(sheet_uuids)) + "\n")
    keys = sorted({p.symbol for p in design.PARTS})
    symbols.write_library(HW / "libraries" / "LandyHeater_RevA.kicad_sym", keys)
    print("schematic written")


if __name__ == "__main__":
    main()
