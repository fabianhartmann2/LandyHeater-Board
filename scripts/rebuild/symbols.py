"""Schematic symbols: copied KiCad library symbols plus project IC/connector symbols.

Custom IC pin names and numbers are transcribed from the manufacturers' pin
tables (see design.py block comments for the documents used).
"""
from __future__ import annotations

from pathlib import Path

import sexpr
from sexpr import Sym

KICAD_SYM = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
LIBNAME = "LandyHeater_RevA"

# generic device symbols: key -> (library, symbol)
DEVICE = {
    "R": ("Device", "R"), "C": ("Device", "C"), "C_Polarized": ("Device", "C_Polarized"),
    "L": ("Device", "L"), "FerriteBead": ("Device", "FerriteBead"), "D_TVS": ("Device", "D_TVS"),
    "D_Zener": ("Device", "D_Zener"), "D_Schottky": ("Device", "D_Schottky"), "LED": ("Device", "LED"),
    "Polyfuse": ("Device", "Polyfuse"), "Battery_Cell": ("Device", "Battery_Cell"),
    "Q_NMOS": ("Transistor_FET", "Q_NMOS_GSD"), "Q_PNP": ("Transistor_BJT", "Q_PNP_BEC"),
    "SW_Push": ("Switch", "SW_Push"), "TestPoint": ("Connector", "TestPoint"),
    "GND": ("power", "GND"), "PWR_FLAG": ("power", "PWR_FLAG"),
}

# pin type codes
I, O, B, P, W, WO, OC, NC = "input", "output", "bidirectional", "passive", "power_in", "power_out", "open_collector", "no_connect"

# custom symbols: key -> dict(left=[(num, name, type)], right=[...], ref="U", width)
IC: dict[str, dict] = {
    "LM74720": dict(ref="U", left=[("2", "A", P), ("3", "VSNS", I), ("6", "EN", I), ("4", "SW", P), ("5", "OV", I), ("7", "GND", W)],
                    right=[("12", "C", P), ("11", "VS", W), ("1", "GATE", O), ("8", "PD", O), ("9", "LX", P), ("10", "CAP", P), ("13", "RTN(float)", NC)]),
    "DUALNFET": dict(ref="Q", left=[("1", "S1", P), ("2", "G1", I), ("4", "G2", I), ("3", "S2", P)],
                     right=[("7", "D1", P), ("8", "D1", P), ("5", "D2", P), ("6", "D2", P)]),
    "USBLC6": dict(ref="U", left=[("1", "I/O1", P), ("3", "I/O2", P), ("5", "VBUS", P), ("2", "GND", P)],
                   right=[("6", "I/O1", P), ("4", "I/O2", P)]),
    "TUSB321": dict(ref="U", left=[("12", "VDD", W), ("5", "VBUS_DET", I), ("1", "CC1", B), ("2", "CC2", B), ("3", "CURRENT_MODE", I), ("4", "PORT", I), ("10", "GND", W)],
                    right=[("7", "OUT1", OC), ("8", "OUT2", OC), ("9", "ID", OC), ("11", "DIR", OC), ("6", "VCONN_FAULT", OC)]),
    "TPS25947": dict(ref="U", left=[("5", "IN", W), ("1", "EN/UVLO", I), ("2", "OVLO", I), ("8", "GND", W)],
                     right=[("6", "OUT", WO), ("4", "FLT", OC), ("3", "AUXOFF", OC), ("7", "DVDT", P), ("9", "ILM", P), ("10", "ITIMER", P)]),
    "LMR33630": dict(ref="U", left=[("2", "VIN", W), ("3", "EN", I), ("1", "PGND", W), ("9", "AGND/EP", W)],
                     right=[("8", "SW", WO), ("7", "BOOT", P), ("5", "FB", I), ("4", "PG", OC), ("6", "VCC", P)]),
    "ESP32S3": dict(ref="U", width=30.48,
                    left=[("2", "3V3", W), ("3", "EN", I), ("27", "IO0/BOOT", B), ("39", "IO1", B), ("38", "IO2", B), ("15", "IO3", B),
                          ("4", "IO4", B), ("5", "IO5", B), ("6", "IO6", B), ("7", "IO7", B), ("12", "IO8", B), ("17", "IO9", B),
                          ("18", "IO10", B), ("19", "IO11", B), ("20", "IO12", B), ("21", "IO13", B), ("22", "IO14", B), ("8", "IO15", B),
                          ("9", "IO16", B), ("10", "IO17", B), ("1", "GND", W), ("40", "GND", W), ("41", "GND/EPAD", W)],
                    right=[("11", "IO18", B), ("13", "IO19/USB_D-", B), ("14", "IO20/USB_D+", B), ("23", "IO21", B),
                           ("28", "IO35/PSRAM", B), ("29", "IO36/PSRAM", B), ("30", "IO37/PSRAM", B), ("31", "IO38", B), ("32", "IO39", B),
                           ("33", "IO40", B), ("34", "IO41", B), ("35", "IO42", B), ("37", "TXD0/IO43", B), ("36", "RXD0/IO44", B),
                           ("26", "IO45", B), ("16", "IO46", B), ("24", "IO47", B), ("25", "IO48", B)]),
    "TPS3808": dict(ref="U", left=[("6", "VDD", W), ("5", "SENSE", I), ("3", "~{MR}", I), ("2", "GND", W)],
                    right=[("1", "~{RESET}", OC), ("4", "CT", P)]),
    "TPS22919": dict(ref="U", left=[("1", "IN", W), ("3", "ON", I), ("2", "GND", W)],
                     right=[("6", "VOUT", WO), ("5", "QOD", P), ("4", "NC", NC)]),
    "AXC8T245": dict(ref="U", width=17.78,
                     left=[("1", "VCCA", W), ("2", "DIR1", I), ("11", "DIR2", I), ("22", "~{OE}", I), ("3", "A1", I), ("4", "A2", I), ("5", "A3", I),
                           ("6", "A4", I), ("7", "A5", I), ("8", "A6", I), ("9", "A7", I), ("10", "A8", I), ("12", "GND", W), ("13", "GND", W)],
                     right=[("23", "VCCB", W), ("24", "VCCB", W), ("21", "B1", O), ("20", "B2", O), ("19", "B3", O), ("18", "B4", O),
                            ("17", "B5", O), ("16", "B6", O), ("15", "B7", O), ("14", "B8", O)]),
    "AXC1T45": dict(ref="U", left=[("1", "VCCA", W), ("3", "A", O), ("5", "DIR", I), ("2", "GND", W)],
                    right=[("6", "VCCB", W), ("4", "B", I)]),
    "TPS7A02": dict(ref="U", left=[("1", "IN", W), ("3", "EN", I), ("2", "GND", W)], right=[("5", "OUT", WO), ("4", "NC", NC)]),
    "LVC1G07": dict(ref="U", left=[("5", "VCC", W), ("2", "A", I), ("3", "GND", W)], right=[("4", "Y(OD)", OC), ("1", "NC", NC)]),
    "LVC1G74": dict(ref="U", left=[("8", "VCC", W), ("2", "D", I), ("3", "CLK", I), ("4", "~{PRE}", I), ("1", "~{CLR}", I), ("7", "GND", W)],
                    right=[("5", "Q", O), ("6", "~{Q}", O)]),
    "RV3028": dict(ref="U", left=[("7", "VDD", W), ("6", "VBACKUP", W), ("3", "SCL", I), ("4", "SDA", B), ("8", "EVI", I), ("5", "VSS", W)],
                   right=[("2", "~{INT}", OC), ("1", "CLKOUT", O)]),
    "TPS22945": dict(ref="U", left=[("5", "VIN", W), ("4", "ON", I), ("2", "GND", W)], right=[("1", "VOUT", WO), ("3", "~{OC}", OC)]),
    "TXU0202": dict(ref="U", left=[("3", "VCCA", W), ("6", "OE", I), ("5", "A1", I), ("4", "A2Y", O), ("2", "GND", W)],
                    right=[("7", "VCCB", W), ("8", "B1Y", O), ("1", "B2", I)]),
    "BCR421": dict(ref="U", left=[("1", "EN", I), ("6", "REXT", P), ("4", "GND", W)], right=[("2", "OUT", P), ("3", "OUT", P), ("5", "OUT", P)]),
    "AL8861": dict(ref="U", left=[("8", "VIN", W), ("1", "ISENSE", I), ("4", "VSET", I), ("2", "GND", W), ("3", "GND", W), ("9", "EP", W)],
                   right=[("5", "LX", P), ("6", "LX", P), ("7", "NC", NC)]),
}

CONN: dict[str, dict] = {
    "J1": dict(pins=["1", "2"], names=["BATT_12V_IN", "GND"]),
    "J2": dict(pins=["1", "2", "3", "4"], names=["AUTOTERM_5V", "GND", "TX_TO_HEATER", "RX_FROM_HEATER"]),
    "J3": dict(pins=["1", "2", "3"], names=["3V3_SENSOR", "DQ", "GND"]),
    "J4": dict(pins=["1", "2", "3", "4", "5"], names=["BUTTON_N", "GND", "LED+", "LED-PWM", "NC"]),
    "USBC": dict(pins=["A4", "A9", "B4", "B9", "A5", "B5", "A6", "B6", "A7", "B7", "A8", "B8", "A1", "A12", "B1", "B12", "SH"],
                 names=["VBUS", "VBUS", "VBUS", "VBUS", "CC1", "CC2", "D+", "D+", "D-", "D-", "SBU1", "SBU2",
                        "GND", "GND", "GND", "GND", "SHIELD"]),
    "FPC24": dict(pins=[str(i) for i in range(1, 25)] + ["MP"],
                  names=["NC", "GDR", "RESE", "NC", "VSH2", "TSCL", "TSDA", "BS1", "BUSY", "RES#", "D/C#", "CS#", "SCL",
                         "SDA", "VDDIO", "VCI", "VSS", "VDD", "VPP", "VSH1", "VGH", "VSL", "VGL", "VCOM", "MOUNT"]),
    "FPC6": dict(pins=["1", "2", "3", "4", "5", "6", "MP"], names=["GND", "INT", "RESET", "VDD", "SCL", "SDA", "MOUNT"]),
    "FPC6L": dict(pins=["1", "2", "3", "4", "5", "6", "MP"], names=["LED+", "LED+", "NC", "NC", "LED-", "LED-", "MOUNT"]),
}

DIODE3 = {  # SOT-23 single diode / dual common-anode ESD
    "D_SOT23": dict(left=[("1", "A", P)], right=[("3", "K", P), ("2", "NC", NC)]),
    "D_Dual_CA": dict(left=[("1", "K1", P), ("2", "K2", P)], right=[("3", "A(common)", P)]),
    "D_TVS_uni": dict(left=[("1", "K", P)], right=[("2", "A", P)]),
}


def load_lib(lib: str) -> dict[str, list]:
    tree = sexpr.parse((KICAD_SYM / f"{lib}.kicad_sym").read_text())[0]
    return {node[1]: node for node in sexpr.find_all(tree, "symbol")}


_cache: dict[str, dict] = {}


def kicad_symbol(lib: str, name: str) -> list:
    """Return a flattened copy of a KiCad library symbol renamed to lib:name."""
    if lib not in _cache:
        _cache[lib] = load_lib(lib)
    syms = _cache[lib]
    node = syms[name]
    ext = sexpr.find(node, "extends")
    if ext:
        parent = kicad_symbol(lib, ext[1])
        merged = [Sym("symbol"), f"{lib}:{name}"]
        # take parent's body but child's properties
        child_props = {p[1]: p for p in sexpr.find_all(node, "property")}
        for item in parent[2:]:
            if isinstance(item, list) and item and item[0] == "property" and item[1] in child_props:
                merged.append(child_props[item[1]])
            elif isinstance(item, list) and item and item[0] == "symbol":
                sub = list(item)
                sub[1] = sub[1].replace(ext[1], name, 1)
                merged.append(sub)
            else:
                merged.append(item)
        return merged
    out = [Sym("symbol"), f"{lib}:{name}"] + [c for c in node[2:]]
    return out


def pin_positions(sym: list) -> dict[str, tuple[float, float, float]]:
    """pin number -> (x, y, angle) in symbol coordinates (y up), unit 1 / common."""
    out = {}

    def walk(n):
        for c in n:
            if isinstance(c, list) and c:
                if c[0] == "pin":
                    at = sexpr.find(c, "at")
                    num = sexpr.find(c, "number")[1]
                    out[num] = (float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0)
                elif c[0] == "symbol":
                    walk(c)
    walk(sym)
    return out


# ---------------------------------------------------------------- custom
def _prop(name, value, x, y, hide=False, size=1.27):
    p = [Sym("property"), name, value, [Sym("at"), x, y, 0],
         [Sym("effects"), [Sym("font"), [Sym("size"), size, size]]] + ([[Sym("hide"), Sym("yes")]] if hide else [])]
    return p


def _pin(num, name, etype, x, y, angle, length=2.54):
    return [Sym("pin"), Sym(etype), Sym("line"), [Sym("at"), x, y, angle], [Sym("length"), length],
            [Sym("name"), name, [Sym("effects"), [Sym("font"), [Sym("size"), 1.016, 1.016]]]],
            [Sym("number"), num, [Sym("effects"), [Sym("font"), [Sym("size"), 1.016, 1.016]]]]]


def box_symbol(key: str, left, right, ref="U", width=None, value="") -> list:
    rows = max(len(left), len(right))
    longest = max([len(n) for _, n, _ in left + right] + [4])
    if width is None:
        width = max(10.16, round((longest * 1.0 * 2 + 4) / 2.54) * 2.54)
    height = (rows + 1) * 2.54
    top = height / 2
    top = round(top / 1.27) * 1.27
    pins = []
    for i, (num, name, et) in enumerate(left):
        pins.append(_pin(num, name, et, -width / 2 - 2.54, top - 2.54 * (i + 1), 0))
    for i, (num, name, et) in enumerate(right):
        pins.append(_pin(num, name, et, width / 2 + 2.54, top - 2.54 * (i + 1), 180))
    bottom = top - 2.54 * (rows + 1)
    body = [Sym("symbol"), f"{key}_0_1",
            [Sym("rectangle"), [Sym("start"), -width / 2, top], [Sym("end"), width / 2, bottom],
             [Sym("stroke"), [Sym("width"), 0.254], [Sym("type"), Sym("default")]],
             [Sym("fill"), [Sym("type"), Sym("background")]]]]
    unit = [Sym("symbol"), f"{key}_1_1"] + pins
    sym = [Sym("symbol"), f"{LIBNAME}:{key}",
           [Sym("pin_names"), [Sym("offset"), 1.016]],
           [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("yes")], [Sym("on_board"), Sym("yes")],
           _prop("Reference", ref, 0, top + 1.27),
           _prop("Value", value or key, 0, bottom - 1.27),
           _prop("Footprint", "", 0, 0, hide=True),
           _prop("Datasheet", "", 0, 0, hide=True),
           _prop("Description", "", 0, 0, hide=True),
           body, unit]
    return sym


def custom_symbol(kind: str, key: str) -> list:
    if kind == "ic":
        d = IC[key]
        return box_symbol(key, d["left"], d["right"], d.get("ref", "U"), d.get("width"))
    if kind == "conn":
        d = CONN[key]
        right = [(n, nm, P) for n, nm in zip(d["pins"], d["names"])]
        return box_symbol("CONN_" + key, [], right, "J")
    if kind == "dev" and key in DIODE3:
        d = DIODE3[key]
        return box_symbol(key, d["left"], d["right"], "D", width=10.16)
    raise KeyError(kind + ":" + key)


def symbol_for(part_symbol: str) -> tuple[str, list]:
    """Map a design symbol key to (lib_id, symbol s-expr)."""
    kind, key = part_symbol.split(":", 1)
    if kind == "dev" and key in DEVICE:
        lib, name = DEVICE[key]
        return f"{lib}:{name}", kicad_symbol(lib, name)
    sym = custom_symbol(kind, key)
    return sym[1], sym


def write_library(path: Path, keys: list[str]) -> None:
    syms = []
    for k in keys:
        lib_id, s = symbol_for(k)
        if lib_id.startswith(LIBNAME + ":"):
            s = list(s)
            s[1] = lib_id.split(":", 1)[1]
            syms.append(s)
    root = [Sym("kicad_symbol_lib"), [Sym("version"), 20241209], [Sym("generator"), "landyheater_rebuild"],
            [Sym("generator_version"), "1.0"]] + syms
    path.write_text(sexpr.dump(root) + "\n")
