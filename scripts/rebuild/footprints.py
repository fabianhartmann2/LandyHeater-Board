"""Project-local footprints, transcribed from the manufacturers' land patterns.

Each footprint states its source drawing.  Coordinates are top view, mm,
package centre at the origin.
"""
from __future__ import annotations

import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "hardware" / "libraries" / "LandyHeater_RevA.pretty"


def _u(*parts) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "landyheater-fp/" + "/".join(map(str, parts))))


def f(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class FP:
    def __init__(self, name: str, descr: str, attr: str = "smd"):
        self.name, self.descr, self.attr = name, descr, attr
        self.items: list[str] = []
        self.n = 0

    def _id(self):
        self.n += 1
        return _u(self.name, self.n)

    def rect_pad(self, num, x, y, w, h, layers='"F.Cu" "F.Paste" "F.Mask"', rr=0.0):
        shape = f"roundrect (roundrect_rratio {f(rr)})" if rr else "rect"
        if rr:
            self.items.append(f'(pad "{num}" smd roundrect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) '
                              f'(layers {layers}) (roundrect_rratio {f(rr)}) (uuid "{self._id()}"))')
        else:
            self.items.append(f'(pad "{num}" smd rect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) '
                              f'(layers {layers}) (uuid "{self._id()}"))')

    def poly_pad(self, num, rects, layers='"F.Cu" "F.Paste" "F.Mask"'):
        """Custom pad as union of rectangles [(x0, y0, x1, y1), ...]; anchor = centre of first rect."""
        x0, y0, x1, y1 = rects[0]
        ax, ay = (x0 + x1) / 2, (y0 + y1) / 2
        aw, ah = min(x1 - x0, y1 - y0) * 0.9, min(x1 - x0, y1 - y0) * 0.9
        prims = []
        for (a, b, c, d) in rects:
            pts = [(a, b), (c, b), (c, d), (a, d)]
            pts_s = " ".join(f"(xy {f(px - ax)} {f(py - ay)})" for px, py in pts)
            prims.append(f"(gr_poly (pts {pts_s}) (width 0) (fill yes))")
        self.items.append(
            f'(pad "{num}" smd custom (at {f(ax)} {f(ay)}) (size {f(aw)} {f(ah)}) (layers {layers}) '
            f'(options (clearance outline) (anchor rect)) (primitives {" ".join(prims)}) (uuid "{self._id()}"))')

    def line(self, layer, x1, y1, x2, y2, w=0.12):
        self.items.append(f'(fp_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width {f(w)}) (type solid)) '
                          f'(layer "{layer}") (uuid "{self._id()}"))')

    def box(self, layer, x1, y1, x2, y2, w=0.12):
        for a in [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]:
            self.line(layer, *a, w=w)

    def circle(self, layer, x, y, r, w=0.12, fill=False):
        self.items.append(f'(fp_circle (center {f(x)} {f(y)}) (end {f(x + r)} {f(y)}) (stroke (width {f(w)}) (type solid)) '
                          f'(fill {"yes" if fill else "no"}) (layer "{layer}") (uuid "{self._id()}"))')

    def write(self, body_w, body_h, court=0.25):
        hw, hh = body_w / 2, body_h / 2
        self.box("F.Fab", -hw, -hh, hw, hh, 0.1)
        # courtyard from pads + body
        self.box("F.CrtYd", -hw - court, -hh - court, hw + court, hh + court, 0.05)
        text = [
            f'(footprint "{self.name}"',
            '\t(version 20241229)', '\t(generator "landyheater_rebuild")', '\t(generator_version "1.0")',
            '\t(layer "F.Cu")',
            f'\t(descr "{self.descr}")',
            f'\t(attr {self.attr})',
            f'\t(property "Reference" "REF**" (at 0 {f(-hh - 1.2)} 0) (layer "F.SilkS") (uuid "{_u(self.name, "ref")}") '
            '(effects (font (size 0.8 0.8) (thickness 0.12))))',
            f'\t(property "Value" "{self.name}" (at 0 {f(hh + 1.2)} 0) (layer "F.Fab") (uuid "{_u(self.name, "val")}") '
            '(effects (font (size 0.8 0.8) (thickness 0.12))))',
            f'\t(fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") (uuid "{_u(self.name, "reftxt")}") '
            '(effects (font (size 0.5 0.5) (thickness 0.08))))',
        ]
        text += ["\t" + it for it in self.items]
        text.append(")")
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{self.name}.kicad_mod").write_text("\n".join(text) + "\n")


def ti_rpw0010a():
    fp = FP("TI_RPW0010A_VQFN-HR-10_2x2mm",
            "TI RPW0010A VQFN-HR-10 2x2 mm (TPS25947). Land pattern from TI SLVSFC9C p.73 (4225183/A). No exposed pad.")
    L = [  # pin: list of rects (x0,y0,x1,y1)
        ("1", [(-1.2, -0.85, -0.6, -0.55), (-0.85, -1.2, -0.6, -0.55)]),
        ("2", [(-1.2, -0.35, -0.6, -0.1)]),
        ("3", [(-1.2, 0.1, -0.6, 0.35)]),
        ("4", [(-1.2, 0.55, -0.6, 0.85), (-0.85, 0.55, -0.6, 1.2)]),
        ("5", [(-0.4, -1.2, -0.1, 1.2)]),
        ("6", [(0.1, -1.2, 0.4, 1.2)]),
        ("7", [(0.6, 0.55, 1.2, 0.85), (0.6, 0.55, 0.85, 1.2)]),
        ("8", [(0.6, 0.1, 1.2, 0.35)]),
        ("9", [(0.6, -0.35, 1.2, -0.1)]),
        ("10", [(0.6, -0.85, 1.2, -0.55), (0.6, -1.2, 0.85, -0.55)]),
    ]
    for num, rects in L:
        if len(rects) == 1:
            x0, y0, x1, y1 = rects[0]
            fp.rect_pad(num, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, rr=0.15)
        else:
            fp.poly_pad(num, rects)
    fp.circle("F.SilkS", -1.45, -1.35, 0.1, fill=True)
    fp.line("F.SilkS", -1.1, 1.35, 1.1, 1.35)
    fp.write(2.0, 2.0)


def ti_drr0012f():
    fp = FP("TI_DRR0012F_WSON-12_3x3mm_RTN-float",
            "TI DRR0012F WSON-12 3x3 mm (LM74720-Q1). TI SLVSFH8B land pattern 4225797/A. "
            "Exposed pad = RTN, must NOT be connected (no vias).")
    for i in range(6):
        y = -1.25 + i * 0.5
        fp.rect_pad(str(i + 1), -1.39, y, 0.62, 0.25, rr=0.2)
        fp.rect_pad(str(12 - i), 1.39, y, 0.62, 0.25, rr=0.2)
    fp.rect_pad("13", 0, 0, 1.06, 2.5, rr=0.04)
    fp.circle("F.SilkS", -1.95, -1.6, 0.1, fill=True)
    fp.line("F.SilkS", -1.0, -1.65, 1.0, -1.65)
    fp.line("F.SilkS", -1.0, 1.65, 1.0, 1.65)
    fp.write(3.0, 3.0)


def lfpak56d():
    fp = FP("Nexperia_LFPAK56D_SOT1205",
            "Nexperia LFPAK56D dual (SOT1205). Reflow footprint from Nexperia SOT1205 package information Fig.2 "
            "(sot1205_fr, 2020-04-20). Drain islands: copper without paste + separate paste apertures.")
    # leads 1..4, 0.65 x 1.1, centre y = +3.3
    for i, x in enumerate([-1.905, -0.635, 0.635, 1.905]):
        fp.rect_pad(str(i + 1), x, 3.3, 0.65, 1.1)
    # drain islands (copper + mask), notch 0.57 wide x 1.2 deep at top centre of each island
    for num_a, num_b, cx in (("8", "7", -1.27), ("5", "6", 1.27)):
        x0, x1 = cx - 0.985, cx + 0.985
        rects = [(x0, -2.0, x1, 2.1), (x0, -3.2, cx - 0.285, -2.0), (cx + 0.285, -3.2, x1, -2.0)]
        fp.poly_pad(num_a, rects, layers='"F.Cu" "F.Mask"')
        # second pin number of the same island as tiny pad overlapping (KiCad treats as same net)
        fp.rect_pad(num_b, cx + 0.5 if cx > 0 else cx - 0.5, 0.5, 0.5, 0.5, layers='"F.Cu"')
        # paste apertures
        for px in (cx - 0.5 + (0 if cx < 0 else 0), cx + 0.5):
            pass
        fp.rect_pad("", cx - 0.5, -2.225, 0.62, 1.85, layers='"F.Paste"')
        fp.rect_pad("", cx + 0.5, -2.225, 0.62, 1.85, layers='"F.Paste"')
        fp.rect_pad("", cx, -0.44, 1.1, 1.0, layers='"F.Paste"')
        fp.rect_pad("", cx, 1.36, 1.1, 1.0, layers='"F.Paste"')
    fp.circle("F.SilkS", -2.6, 4.0, 0.12, fill=True)
    fp.line("F.SilkS", -2.55, -3.45, 2.55, -3.45)
    fp.write(4.7, 5.3 + 1.6, court=0.3)


def rv3028():
    fp = FP("MicroCrystal_RV-3028-C7",
            "Micro Crystal RV-3028-C7 3.2x1.5 mm. Recommended pad layout from Application Manual Rev 1.4 §8.1; "
            "pin numbering converted from the bottom-view drawing to top view (pin 1 bottom-left).")
    xs = [-1.35, -0.45, 0.45, 1.35]
    for i, x in enumerate(xs):  # pins 1..4 bottom row, left to right
        fp.rect_pad(str(i + 1), x, 0.6, 0.5, 0.8)
    for i, x in enumerate(reversed(xs)):  # pins 5..8 top row, right to left
        fp.rect_pad(str(i + 5), x, -0.6, 0.5, 0.8)
    fp.circle("F.SilkS", -1.85, 1.15, 0.1, fill=True)
    fp.write(3.2, 1.5)


def main():
    ti_rpw0010a()
    ti_drr0012f()
    lfpak56d()
    rv3028()
    print("footprints written to", OUT)


if __name__ == "__main__":
    main()
