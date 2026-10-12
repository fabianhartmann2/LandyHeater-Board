"""LandyHeater-Board Revision A (rebuild) – canonical circuit definition.

Every part, pin-to-net assignment, footprint, manufacturer part number and
LCSC number lives here.  Schematic, BOM and PCB are generated from this file,
so the three views cannot drift apart.

Sources for each functional block are named in the block comments; deviations
from the original specification (v1.6) are tagged with "DEV-xx" and collected
in docs/Rebuild_Abweichungen_RevA.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Footprints
# --------------------------------------------------------------------------
R0603 = "Resistor_SMD:R_0603_1608Metric"
R1206 = "Resistor_SMD:R_1206_3216Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
LED0603 = "LED_SMD:LED_0603_1608Metric"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
SOT236 = "Package_TO_SOT_SMD:SOT-23-6"
SC705 = "Package_TO_SOT_SMD:SOT-353_SC-70-5"
SC706 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"
SOT323 = "Package_TO_SOT_SMD:SOT-323_SC-70"
SOD123 = "Diode_SMD:D_SOD-123"
SOD323 = "Diode_SMD:D_SOD-323"
SOD523 = "Diode_SMD:D_SOD-523"
SMA = "Diode_SMD:D_SMA"
SMB = "Diode_SMD:D_SMB"
TP10 = "TestPoint:TestPoint_Pad_D1.0mm"
TP15 = "TestPoint:TestPoint_Pad_D1.5mm"
SW_TACT = "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A"
LIB = "LandyHeater_RevA"  # project-local footprint library (generated)


@dataclass
class Part:
    ref: str
    value: str
    symbol: str                 # "dev:<name>" for generic device symbols, else custom symbol key
    footprint: str
    pins: dict[str, str | None]  # pin number -> net (None = no connect)
    mpn: str = ""
    mfr: str = ""
    lcsc: str = ""
    dnp: bool = False
    note: str = ""
    sheet: str = ""
    block: str = ""
    pin_names: dict[str, str] = field(default_factory=dict)


PARTS: list[Part] = []
_sheet = ""
_block = ""


def sheet(name: str) -> None:
    global _sheet
    _sheet = name


def block(name: str) -> None:
    global _block
    _block = name


def add(ref, value, symbol, footprint, pins, **kw) -> Part:
    p = Part(ref, value, symbol, footprint, pins, sheet=_sheet, block=_block, **kw)
    PARTS.append(p)
    return p


def R(ref, value, a, b, mpn, lcsc, fp=R0603, mfr="", **kw):
    return add(ref, value, "dev:R", fp, {"1": a, "2": b}, mpn=mpn, lcsc=lcsc, mfr=mfr, **kw)


def C(ref, value, a, b, mpn, lcsc, fp=C0603, mfr="", **kw):
    return add(ref, value, "dev:C", fp, {"1": a, "2": b}, mpn=mpn, lcsc=lcsc, mfr=mfr, **kw)


def TP(ref, label, net, fp=TP10):
    return add(ref, label, "dev:TestPoint", fp, {"1": net}, note="Bare test pad, no part fitted")


# Frequently used passives (manufacturer, MPN, LCSC) – all checked for stock 2026-10-12
P = {
    "0R": ("UNI-ROYAL", "0603WAF0000T5E", "C21189"),
    "22R": ("UNI-ROYAL", "0603WAF220JT5E", "C23345"),
    "33R": ("UNI-ROYAL", "0603WAF330JT5E", "C23140"),
    "100R": ("UNI-ROYAL", "0603WAF1000T5E", "C22775"),
    "499R": ("UNI-ROYAL", "0603WAF4990T5E", "C23065"),
    "1k": ("UNI-ROYAL", "0603WAF1001T5E", "C21190"),
    "1.2k": ("UNI-ROYAL", "0603WAF1201T5E", "C22765"),
    "2.7k": ("UNI-ROYAL", "0603WAF2701T5E", "C13167"),
    "3.3k": ("UNI-ROYAL", "0603WAF3301T5E", "C22978"),
    "3.32k": ("YAGEO", "RC0603FR-073K32L", "C137731"),
    "4.7k": ("UNI-ROYAL", "0603WAF4701T5E", "C23162"),
    "7.15k": ("UNI-ROYAL", "0603WAF7151T5E", "C25980"),
    "10k": ("YAGEO", "RC0603FR-0710KL", "C98220"),
    "10.7k": ("UNI-ROYAL", "0603WAF1072T5E", "C22857"),
    "12k": ("UNI-ROYAL", "0603WAF1202T5E", "C22790"),
    "30.1k": ("UNI-ROYAL", "0603WAF3012T5E", "C23000"),
    "43.2k": ("UNI-ROYAL", "0603WAF4322T5E", "C23053"),
    "47k": ("YAGEO", "RC0603FR-0747KL", "C105579"),
    "100k": ("YAGEO", "RC0603FR-07100KL", "C14675"),
    "105k": ("YAGEO", "RC0603FR-07105KL", "C141685"),
    "220k": ("UNI-ROYAL", "0603WAF2203T5E", "C22961"),
    "1M": ("UNI-ROYAL", "0603WAF1004T5E", "C22935"),
    "2.2R": ("YAGEO", "RC0603FR-072R2L", "C112307"),
    "10pF": ("Samsung", "CL10C100JB8NNNC", "C1634"),
    "10nF": ("FH", "0603B103K500NT", "C57112"),
    "100nF": ("FH", "0603B104K500NT", "C30926"),
    "1uF": ("Samsung", "CL10A105KB8NNNC", "C15849"),
    "1uF50": ("Samsung", "CL21B105KBFNNNE", "C28323"),
    "4.7uF25": ("Samsung", "CL21A475KAQNNNE", "C1779"),
    "4.7uF50": ("Samsung", "CL31B475KBHNNNE", "C51205"),
    "4.7uF50_1210": ("Murata", "GCJ32ER71H475KA12L", "C417122"),
    "22uF10": ("Murata", "GCJ31CR71A226KE01L", "C6565118"),
}


def RP(ref, key, a, b, **kw):
    m, mpn, lcsc = P[key]
    return R(ref, key.replace("R", "Ω") if key.endswith("R") else key, a, b, mpn, lcsc, mfr=m, **kw)


def CP(ref, key, a, b, fp=None, value=None, **kw):
    m, mpn, lcsc = P[key]
    if fp is None:
        fp = {"1uF50": C0805, "4.7uF25": C0805, "4.7uF50": C1206, "4.7uF50_1210": C1210, "22uF10": C1206}.get(key, C0603)
    if value is None:
        value = {"1uF50": "1µF 50V X7R", "4.7uF25": "4.7µF 25V X5R", "4.7uF50": "4.7µF 50V X7R",
                 "4.7uF50_1210": "4.7µF 50V X7R", "22uF10": "22µF 10V X7R", "100nF": "100nF 50V X7R",
                 "10nF": "10nF 50V X7R", "1uF": "1µF 50V X5R", "10pF": "10pF C0G"}.get(key, key)
    return C(ref, value, a, b, mpn, lcsc, fp=fp, mfr=m, **kw)


# ==========================================================================
# Sheet 1 – Power input, USB-C and 3.3 V
# ==========================================================================
sheet("Power")

block("12 V input: TVS + LM74720-Q1 ideal diode/load-dump cut-off (TI SLVSFH8B Fig. 9-1)")
add("J1", "12V IN", "conn:J1", "Connector_Molex:Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal",
    {"1": "BATT_12V_IN", "2": "GND"}, mpn="1053131302", mfr="Molex", lcsc="C17345480",
    note="Nano-Fit 2p RA THT, Au; not stocked at LCSC – PCBWay global sourcing")
add("D1", "TPSMB36CA", "dev:D_TVS", SMB, {"1": "BATT_12V_IN", "2": "GND"},
    mpn="TPSMB36CA", mfr="Littelfuse", lcsc="C413569",
    note="DEV-01: 36 V bidirectional TVS per TI reference (was 18 V)")
CP("C1", "100nF", "BATT_12V_IN", "GND")
add("U1", "LM74720QDRRRQ1", "ic:LM74720", f"{LIB}:TI_DRR0012F_WSON-12_3x3mm_RTN-float",
    {"1": "Q1_GATE", "2": "BATT_12V_IN", "3": "BATT_12V_IN", "4": "OV_TOP", "5": "OV_SENSE",
     "6": "BATT_12V_IN", "7": "GND", "8": "Q2_PD", "9": "BOOST_LX", "10": "BOOST_CAP",
     "11": "FET_DRAIN", "12": "FET_DRAIN", "13": None},
    mpn="LM74720QDRRRQ1", mfr="Texas Instruments", lcsc="C5219205",
    note="RTN thermal pad (13) MUST stay unconnected")
add("Q1", "BUK7K17-60E", "ic:DUALNFET", f"{LIB}:Nexperia_LFPAK56D_SOT1205",
    {"1": "BATT_12V_IN", "2": "Q1_GATE", "3": "VIN_12V_PROT", "4": "Q2_GATE",
     "5": "FET_DRAIN", "6": "FET_DRAIN", "7": "FET_DRAIN", "8": "FET_DRAIN"},
    mpn="BUK7K17-60EX", mfr="Nexperia", lcsc="C478237",
    note="DEV-02: dual 60 V, VGS ±20 V, AEC-Q101 (replaces IPG20N06S4L-26, not stocked)")
add("L1", "100µH", "dev:L", "Inductor_SMD:L_APV_ANR3015", {"1": "FET_DRAIN", "2": "BOOST_LX"},
    mpn="ANR3015T101M", mfr="APV", lcsc="C6364791",
    note="LM74720 boost inductor, Isat 250 mA > 175 mA required; alt. Bourns SRN3015-101M (C3223904)")
CP("C2", "1uF50", "FET_DRAIN", "GND")
CP("C3", "1uF50", "BOOST_CAP", "FET_DRAIN")
RP("R1", "100k", "OV_TOP", "OV_SENSE", note="OV cut-off 18.4 V nominal (16.5…20.4 V worst case)")
RP("R2", "7.15k", "OV_SENSE", "GND")
RP("R3", "0R", "Q2_PD", "Q2_GATE")
add("D2", "18V", "dev:D_Zener", SOD123, {"1": "Q2_GATE", "2": "VIN_12V_PROT"},
    mpn="SZMMSZ5248BT1G", mfr="onsemi", lcsc="C604812", note="Q2 VGS clamp, AEC-Q101")
RP("R4", "100R", "Q2_GATE", "Q2_SLEW")
CP("C4", "10nF", "Q2_SLEW", "GND", note="Q2 turn-on slew → inrush limit")
CP("C5", "4.7uF50", "VIN_12V_PROT", "GND")
add("FB1", "220Ω@100MHz", "dev:FerriteBead", "Inductor_SMD:L_0805_2012Metric",
    {"1": "VIN_12V_PROT", "2": "VIN_SYS"}, mpn="MPZ2012S221AT000", mfr="TDK", lcsc="C76818")
add("C6", "47µF 35V", "dev:C_Polarized", "Capacitor_SMD:CP_Elec_6.3x7.7", {"1": "VIN_SYS", "2": "GND"},
    mpn="EEE-FK1V470P", mfr="Panasonic", lcsc="C178565",
    note="DEV-03: hold-up for micro-interruptions (LV124 E-10) and ESR damping of the input filter")
TP("TP1", "BATT_12V", "BATT_12V_IN", TP15)
TP("TP2", "12V_PROT", "VIN_12V_PROT", TP15)
TP("TP3", "VIN_SYS", "VIN_SYS", TP15)
TP("TP4", "GND", "GND", TP15)

block("USB-C sink: CC detection (TUSB321AI), ESD, eFuse with reverse blocking (TPS259470L)")
add("J5", "USB-C", "conn:USBC", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
    {"A1": "GND", "A4": "USB_VBUS", "A5": "USB_CC1", "A6": "USB_DP_CONN", "A7": "USB_DN_CONN", "A8": None,
     "A9": "USB_VBUS", "A12": "GND", "B1": "GND", "B4": "USB_VBUS", "B5": "USB_CC2", "B6": "USB_DP_CONN",
     "B7": "USB_DN_CONN", "B8": None, "B9": "USB_VBUS", "B12": "GND", "SH": "USB_SHIELD"},
    mpn="TYPE-C-31-M-12", mfr="Korean Hroparts", lcsc="C165948",
    note="DEV-04: replaces GCT USB4105-GF-A-120 (not stocked)")
RP("R5", "0R", "USB_SHIELD", "GND", note="Shield bond at J5")
add("D3", "ESD5Z5.0T1G", "dev:D_TVS_uni", SOD523, {"1": "USB_VBUS", "2": "GND"},
    mpn="ESD5Z5.0T1G", mfr="onsemi", lcsc="C82044")
add("U2", "USBLC6-2SC6", "ic:USBLC6", SOT236,
    {"1": "USB_DN_CONN", "2": "GND", "3": "USB_DP_CONN", "4": "USB_DP_CONN", "5": "USB_VBUS", "6": "USB_DN_CONN"},
    mpn="USBLC6-2SC6", mfr="STMicroelectronics", lcsc="C7519",
    note="DEV-05: replaces TPD2EUSB30 (old 5-pin wiring did not match the 3-pin DRT package)")
CP("C7", "1uF", "USB_VBUS", "GND")
add("U3", "TUSB321AIRWBR", "ic:TUSB321", "Package_DFN_QFN:Texas_X2QFN-12_1.6x1.6mm_P0.4mm",
    {"1": "USB_CC1", "2": "USB_CC2", "3": "GND", "4": "GND", "5": "USB_VBUS_DET", "6": None,
     "7": "USB_OUT1", "8": "USB_OUT2", "9": None, "10": "GND", "11": None, "12": "USB_VBUS"},
    mpn="TUSB321AIRWBR", mfr="Texas Instruments", lcsc="C2674046", note="UFP, internal Rd")
CP("C8", "100nF", "USB_VBUS", "GND")
R("R6", "910k 1%", "USB_VBUS", "USB_VBUS_DET", "0603WAF9103T5E", "C23263", mfr="UNI-ROYAL",
  note="TI asks for 900 kΩ; nearest stocked value")
RP("R7", "220k", "USB_VBUS", "USB_OUT1")
RP("R8", "220k", "USB_VBUS", "USB_OUT2")
RP("R9", "1M", "USB_OUT1", "GND", note="defines Q2 gate when USB is absent")
add("Q2", "2N7002K", "dev:Q_NMOS", SOT23, {"1": "USB_OUT1", "2": "GND", "3": "USB_HIGH_CURRENT"},
    mpn="2N7002K-7", mfr="Diodes Inc.", lcsc="C85047", note="isolates 3V3 from unpowered TUSB321")
RP("R10", "100k", "3V3", "USB_HIGH_CURRENT")
add("U4", "TPS259470LRPWR", "ic:TPS25947", f"{LIB}:TI_RPW0010A_VQFN-HR-10_2x2mm",
    {"1": "USB_EN", "2": "USB_OVLO", "3": None, "4": "USB_FLT_N", "5": "USB_VBUS", "6": "VIN_SYS",
     "7": "USB_DVDT", "8": "GND", "9": "USB_ILM", "10": None},
    mpn="TPS259470LRPWR", mfr="Texas Instruments", lcsc="C3662793",
    note="RPW has no exposed pad (old footprint had one)")
RP("R11", "105k", "USB_VBUS", "USB_EN", note="DEV-06: UVLO 4.3 V / OVLO 5.8 V ladder, EN pin stays < 5 V")
RP("R12", "10.7k", "USB_EN", "USB_OVLO")
RP("R13", "30.1k", "USB_OVLO", "GND")
RP("R14", "3.32k", "USB_ILM", "GND", note="ILIM 0.85…1.15 A")
CP("C9", "10nF", "USB_DVDT", "GND", note="≈0.2 V/ms output slew")
RP("R15", "100k", "USB_VBUS", "USB_FLT_N")
TP("TP5", "USB_VBUS", "USB_VBUS")
TP("TP6", "USB_FLT", "USB_FLT_N")
TP("TP7", "USB_3A", "USB_OUT2")

block("3.3 V buck LMR33630C (2.1 MHz, outside AM band; TI SNVSAN3F Table 9-2)")
add("U5", "LMR33630CDDAR", "ic:LMR33630", "Package_SO:Texas_HSOP-8-1EP_3.9x4.9mm_P1.27mm",
    {"1": "GND", "2": "VIN_SYS", "3": "VIN_SYS", "4": "BUCK_PG", "5": "BUCK_FB", "6": "BUCK_VCC",
     "7": "BUCK_BOOT", "8": "BUCK_SW", "9": "GND"},
    mpn="LMR33630CDDAR", mfr="Texas Instruments", lcsc="C2071423",
    note="DEV-07: replaces LMR43620MSC3 (not stocked); 3.8–36 V, runs in dropout during cold crank")
CP("C10", "4.7uF50_1210", "VIN_SYS", "GND")
CP("C11", "4.7uF50", "VIN_SYS", "GND")
CP("C12", "100nF", "VIN_SYS", "GND", note="HF bypass right at VIN/PGND")
add("L2", "1.2µH", "dev:L", "Inductor_SMD:L_Sunlord_MWSA0402S", {"1": "BUCK_SW", "2": "3V3"},
    mpn="MMPC0402-1R2MT", mfr="MetalLions", lcsc="C48579552", note="Isat 7.8 A, 25 mΩ")
CP("C13", "100nF", "BUCK_BOOT", "BUCK_SW")
CP("C14", "1uF", "BUCK_VCC", "GND")
RP("R16", "100k", "3V3", "BUCK_FB", note="RFBT")
RP("R17", "43.2k", "BUCK_FB", "GND", note="RFBB → 3.31 V")
C("C15", "DNP", "3V3", "BUCK_FB", "", "", dnp=True, note="optional CFF")
CP("C16", "22uF10", "3V3", "GND")
CP("C17", "22uF10", "3V3", "GND")
RP("R18", "100k", "3V3", "BUCK_PG")
TP("TP8", "3V3", "3V3", TP15)
TP("TP9", "BUCK_PG", "BUCK_PG")

# ==========================================================================
# Sheet 2 – ESP32-S3, reset, boot, native USB
# ==========================================================================
sheet("MCU")
block("ESP32-S3-WROOM-1U-N16R8 (Espressif datasheet v1.8 + HW design guidelines)")
esp_pins = {
    "1": "GND", "2": "3V3", "3": "CHIP_PU", "4": "1WIRE_DQ_MCU", "5": "I2C_SDA", "6": "I2C_SCL",
    "7": "TOUCH_RST_REL", "8": "SENSOR_EN", "9": "AUTOTERM_TX_3V3", "10": "AUTOTERM_RX_3V3",
    "11": "LATCH_CLR_MCU", "12": "EPD_BUSY_MCU", "13": "USB_DN_MCU", "14": "USB_DP_MCU", "15": None,
    "16": None, "17": "EPD_SCLK_MCU", "18": "EPD_MOSI_MCU", "19": "EPD_CS_MCU", "20": "EPD_DC_MCU",
    "21": "EPD_RST_MCU", "22": "DISPLAY_EN", "23": "FRONTLIGHT_PWM", "24": "AUTOTERM_OE", "25": None,
    "26": None, "27": "BOOT_N", "28": None, "29": None, "30": None, "31": "BUTTON_LED_PWM",
    "32": "DIAG_RUN", "33": "USB_HIGH_CURRENT", "34": "STATUS_LED_1", "35": "STATUS_LED_2",
    "36": "U0RXD", "37": "U0TXD_MCU", "38": "TOUCH_INT_N", "39": "BUTTON_N", "40": "GND", "41": "GND",
}
add("U6", "ESP32-S3-WROOM-1U-N16R8", "ic:ESP32S3", "RF_Module:ESP32-S3-WROOM-1U", esp_pins,
    mpn="ESP32-S3-WROOM-1U-N16R8", mfr="Espressif", lcsc="C3013946",
    note="MSL3, exactly one reflow: place on the second (final) reflow side")
CP("C18", "22uF10", "3V3", "GND")
CP("C19", "22uF10", "3V3", "GND")
CP("C20", "100nF", "3V3", "GND")
add("U7", "TPS3808G33-Q1", "ic:TPS3808", SOT236,
    {"1": "CHIP_PU", "2": "GND", "3": "RESET_MR_N", "4": None, "5": "3V3", "6": "3V3"},
    mpn="TPS3808G33QDBVRQ1", mfr="Texas Instruments", lcsc="C414616", note="CT open → 20 ms delay")
CP("C21", "100nF", "3V3", "GND")
RP("R19", "10k", "3V3", "CHIP_PU")
CP("C22", "1uF", "CHIP_PU", "GND")
RP("R20", "10k", "3V3", "RESET_MR_N")
add("SW1", "RESET", "dev:SW_Push", SW_TACT, {"1": "RESET_MR_N", "2": "GND"},
    mpn="TS-1187A-B-A-B", mfr="XKB", lcsc="C318884", note="DEV-08: replaces KMR221G (not stocked)")
RP("R21", "10k", "3V3", "BOOT_N")
add("SW2", "BOOT", "dev:SW_Push", SW_TACT, {"1": "BOOT_N", "2": "GND"},
    mpn="TS-1187A-B-A-B", mfr="XKB", lcsc="C318884")
RP("R22", "22R", "USB_DN_CONN", "USB_DN_MCU")
RP("R23", "22R", "USB_DP_CONN", "USB_DP_MCU")
CP("C23", "10pF", "USB_DN_MCU", "GND", dnp=True, note="USB SI tuning, DNP")
CP("C24", "10pF", "USB_DP_MCU", "GND", dnp=True, note="USB SI tuning, DNP")
RP("R24", "499R", "U0TXD_MCU", "U0TXD")
RP("R25", "33R", "EPD_SCLK_MCU", "EPD_SCLK")
RP("R26", "33R", "EPD_MOSI_MCU", "EPD_MOSI")
RP("R27", "33R", "EPD_CS_MCU", "EPD_CS_N")
RP("R28", "33R", "EPD_DC_MCU", "EPD_DC")
RP("R29", "33R", "EPD_RST_MCU", "EPD_RST_N")
RP("R30", "33R", "EPD_BUSY", "EPD_BUSY_MCU")
CP("C25", "10pF", "EPD_SCLK", "GND", dnp=True, note="SPI edge tuning, DNP")
TP("TP10", "U0TXD", "U0TXD")
TP("TP11", "U0RXD", "U0RXD")
TP("TP12", "CHIP_PU", "CHIP_PU")
TP("TP13", "BOOT", "BOOT_N")
TP("TP14", "USB_D-", "USB_DN_MCU")
TP("TP15", "USB_D+", "USB_DP_MCU")

# ==========================================================================
# Sheet 3 – E-paper power, isolation and booster
# ==========================================================================
sheet("Display")
block("Switched display rail and power-off isolation")
add("U8", "TPS22919DCKR", "ic:TPS22919", SC706,
    {"1": "3V3", "2": "GND", "3": "DISPLAY_EN", "4": None, "5": "3V3_DISP", "6": "3V3_DISP"},
    mpn="TPS22919DCKR", mfr="Texas Instruments", lcsc="C2149796",
    note="DEV-09: commercial-grade sibling of TPS22919-Q1 (Q1 not stocked), −40…125 °C")
RP("R31", "100k", "DISPLAY_EN", "GND")
CP("C26", "1uF", "3V3", "GND")
add("U9", "SN74AXC8T245PWR", "ic:AXC8T245", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
    {"1": "3V3", "2": "3V3", "3": "EPD_SCLK", "4": "EPD_MOSI", "5": "EPD_CS_N", "6": "EPD_DC",
     "7": "EPD_RST_N", "8": "GND", "9": "GND", "10": "GND", "11": "3V3", "12": "GND", "13": "GND",
     "14": None, "15": None, "16": None, "17": "EPD_RST_P", "18": "EPD_DC_P", "19": "EPD_CS_P",
     "20": "EPD_MOSI_P", "21": "EPD_SCLK_P", "22": "EPD_OE_N", "23": "3V3_DISP", "24": "3V3_DISP"},
    mpn="SN74AXC8T245PWR", mfr="Texas Instruments", lcsc="C882718")
CP("C27", "100nF", "3V3", "GND")
CP("C28", "100nF", "3V3_DISP", "GND")
RP("R32", "100k", "3V3", "EPD_OE_N", note="/OE high = isolated until DISPLAY_EN")
add("Q3", "2N7002K", "dev:Q_NMOS", SOT23, {"1": "DISPLAY_EN", "2": "GND", "3": "EPD_OE_N"},
    mpn="2N7002K-7", mfr="Diodes Inc.", lcsc="C85047")
add("U10", "SN74AXC1T45DCKR", "ic:AXC1T45", SC706,
    {"1": "3V3", "2": "GND", "3": "EPD_BUSY", "4": "EPD_BUSY_P", "5": "GND", "6": "3V3_DISP"},
    mpn="SN74AXC1T45DCKR", mfr="Texas Instruments", lcsc="C2677392", note="DIR low: B→A")
CP("C29", "100nF", "3V3", "GND")
CP("C30", "100nF", "3V3_DISP", "GND")
RP("R33", "100k", "EPD_BUSY", "GND")
RP("R34", "100k", "EPD_SCLK_P", "GND")
RP("R35", "100k", "EPD_MOSI_P", "GND")
RP("R36", "100k", "3V3_DISP", "EPD_CS_P")
RP("R37", "100k", "EPD_DC_P", "GND")
RP("R38", "100k", "EPD_RST_P", "GND")

block("GDEY029T94-FT01 24-pin FPC + booster (Good Display spec Rev 1.0, chapter 12)")
add("J6", "E-PAPER 24p", "conn:FPC24", "Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal",
    {"1": None, "2": "EPD_GDR", "3": "EPD_RESE", "4": None, "5": "EPD_VSH2", "6": None, "7": None,
     "8": "GND", "9": "EPD_BUSY_P", "10": "EPD_RST_P", "11": "EPD_DC_P", "12": "EPD_CS_P",
     "13": "EPD_SCLK_P", "14": "EPD_MOSI_P", "15": "3V3_DISP", "16": "3V3_DISP", "17": "GND",
     "18": "EPD_VDD", "19": None, "20": "EPD_VSH1", "21": "EPD_PREVGH", "22": "EPD_VSL",
     "23": "EPD_PREVGL", "24": "EPD_VCOM", "MP": "GND"},
    mpn="FH12-24S-0.5SH(55)", mfr="Hirose", lcsc="C202112",
    note="Bottom contact – contact side still to be confirmed on the original display")
CP("C31", "4.7uF25", "3V3_DISP", "GND", note="GD C4")
add("L3", "47µH", "dev:L", "Inductor_SMD:L_Taiyo-Yuden_NR-40xx", {"1": "3V3_DISP", "2": "EPD_BOOST_SW"},
    mpn="NRS4018T470MDGJV", mfr="Taiyo Yuden", lcsc="C5355142", note="GD L1: 47 µH, Isat 0.6 A, AEC-Q200")
add("Q4", "Si1308EDL", "dev:Q_NMOS", SOT323, {"1": "EPD_GDR", "2": "EPD_RESE", "3": "EPD_BOOST_SW"},
    mpn="SI1308EDL-T1-GE3", mfr="Vishay", lcsc="C469327", note="GD Q1")
R("R39", "1M 1%", "EPD_GDR", "GND", *P["1M"][1:], mfr=P["1M"][0], note="GD R1")
R("R40", "2.2Ω 1%", "EPD_RESE", "GND", *P["2.2R"][1:], mfr=P["2.2R"][0], note="GD R2")
add("D4", "MBR0530", "dev:D_Schottky", SOD123, {"1": "EPD_PREVGH", "2": "EPD_BOOST_SW"},
    mpn="MBR0530-TP", mfr="MCC", lcsc="C42388518", note="GD D3")
add("D5", "MBR0530", "dev:D_Schottky", SOD123, {"1": "EPD_NEGPUMP", "2": "EPD_PREVGL"},
    mpn="MBR0530-TP", mfr="MCC", lcsc="C42388518", note="GD D1")
add("D6", "MBR0530", "dev:D_Schottky", SOD123, {"1": "GND", "2": "EPD_NEGPUMP"},
    mpn="MBR0530-TP", mfr="MCC", lcsc="C42388518", note="GD D2")
CP("C32", "4.7uF25", "EPD_BOOST_SW", "EPD_NEGPUMP", note="GD C3")
CP("C33", "1uF50", "EPD_PREVGH", "GND", value="1µF 50V X7R", note="GD C5")
CP("C34", "1uF50", "EPD_VSH2", "GND", note="GD C2")
CP("C35", "1uF50", "3V3_DISP", "GND", note="GD C6")
CP("C36", "1uF50", "EPD_VDD", "GND", note="GD C7")
CP("C37", "1uF50", "EPD_VSH1", "GND", note="GD C9")
CP("C38", "1uF50", "EPD_VSL", "GND", note="GD C10 – old design wrongly had PREVGH–VSL")
CP("C39", "1uF50", "EPD_PREVGL", "GND", note="GD C11")
CP("C40", "1uF50", "EPD_VCOM", "GND", note="GD C12")
TP("TP16", "EPD_3V3", "3V3_DISP")
TP("TP17", "EPD_SCLK", "EPD_SCLK_P")
TP("TP18", "EPD_MOSI", "EPD_MOSI_P")
TP("TP19", "EPD_CS", "EPD_CS_P")
TP("TP20", "EPD_DC", "EPD_DC_P")
TP("TP21", "EPD_RST", "EPD_RST_P")
TP("TP22", "EPD_BUSY", "EPD_BUSY_P")

# ==========================================================================
# Sheet 4 – Touch (always-on 3.0 V) and RTC
# ==========================================================================
sheet("Touch_RTC")
block("3.0 V always-on rail, I2C pull-ups, touch FPC")
add("U11", "TPS7A0230PDBVR", "ic:TPS7A02", SOT235,
    {"1": "3V3", "2": "GND", "3": "3V3", "4": None, "5": "3V0_AON"},
    mpn="TPS7A0230PDBVR", mfr="Texas Instruments", lcsc="C3747031")
CP("C41", "1uF", "3V3", "GND")
CP("C42", "1uF", "3V0_AON", "GND")
RP("R41", "4.7k", "3V0_AON", "I2C_SDA")
RP("R42", "4.7k", "3V0_AON", "I2C_SCL")
add("U12", "74LVC1G07", "ic:LVC1G07", SOT235,
    {"1": None, "2": "TOUCH_RST_REL", "3": "GND", "4": "TOUCH_RST_N", "5": "3V0_AON"},
    mpn="SN74LVC1G07DBVR", mfr="UMW", lcsc="C7394020",
    note="DEV-10: UMW second source of SN74LVC1G07 (TI -Q1 not stocked), −40…85 °C")
CP("C43", "100nF", "3V0_AON", "GND")
RP("R43", "100k", "TOUCH_RST_REL", "GND", note="reset asserted until firmware releases")
RP("R44", "10k", "3V0_AON", "TOUCH_RST_N")
add("J7", "TOUCH 6p", "conn:FPC6", "Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal",
    {"1": "GND", "2": "TOUCH_INT_P", "3": "TOUCH_RST_N", "4": "3V0_AON", "5": "I2C_SCL", "6": "I2C_SDA", "MP": "GND"},
    mpn="FH12-6S-0.5SH(55)", mfr="Hirose", lcsc="C202118")
RP("R45", "100R", "TOUCH_INT_P", "TOUCH_INT_N")
RP("R46", "10k", "3V0_AON", "TOUCH_INT_N")
RP("R47", "10k", "TOUCH_INT_N", "GND", dnp=True, note="measurement option only, never with R46")
TP("TP23", "I2C_SDA", "I2C_SDA")
TP("TP24", "I2C_SCL", "I2C_SCL")
TP("TP25", "TOUCH_INT", "TOUCH_INT_N")
TP("TP26", "TOUCH_RST", "TOUCH_RST_N")
TP("TP27", "3V0_AON", "3V0_AON")

block("Optional wake latch (DNP until touch-INT measurement)")
add("U13", "74LVC1G74", "ic:LVC1G74", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
    {"1": "LATCH_CLR_N", "2": "3V0_AON", "3": "GND", "4": "TOUCH_INT_P", "5": None, "6": "LATCH_QN",
     "7": "GND", "8": "3V0_AON"},
    mpn="SN74LVC1G74DCUR", mfr="Texas Instruments", lcsc="C70285", dnp=True)
RP("R48", "100k", "3V0_AON", "LATCH_CLR_N", dnp=True)
CP("C44", "100nF", "LATCH_CLR_N", "GND", dnp=True)
RP("R49", "100R", "LATCH_CLR_MCU", "LATCH_CLR_N", dnp=True)
RP("R50", "0R", "LATCH_QN", "TOUCH_INT_N", dnp=True, note="fit only with U13; then remove R45/R46")

block("RTC RV-3028-C7 with BR1225 backup")
add("U14", "RV-3028-C7", "ic:RV3028", f"{LIB}:MicroCrystal_RV-3028-C7",
    {"1": None, "2": "RTC_INT_N", "3": "I2C_SCL", "4": "I2C_SDA", "5": "GND", "6": "RTC_VBACKUP",
     "7": "3V3", "8": "GND"},
    mpn="RV-3028-C7-32.768kHz-1ppm-TA-QC", mfr="Micro Crystal", lcsc="C3019759",
    note="Not stocked at LCSC – PCBWay global sourcing. Footprint corrected (old one was mirrored)")
CP("C45", "100nF", "3V3", "GND")
add("BT1", "BR1225", "dev:Battery_Cell", "Battery:BatteryHolder_LINX_BAT-HLD-012-SMT",
    {"1": "RTC_BAT", "2": "GND"}, mpn="BAT-HLD-012-SMT", mfr="TE Connectivity", lcsc="C5189234",
    note="DEV-11: SMT 12 mm holder (Keystone 500 not stocked); cell Panasonic BR1225 inserted after assembly")
add("D7", "BAS116", "dev:D_SOT23", SOT23, {"1": "RTC_BAT", "2": None, "3": "RTC_VBACKUP"},
    mpn="BAS116,215", mfr="Nexperia", lcsc="C48502", note="blocks any charge current into the primary cell")
TP("TP28", "RTC_INT", "RTC_INT_N")

# ==========================================================================
# Sheet 5 – AUTOTERM UART and 1-Wire
# ==========================================================================
sheet("IO")
block("AUTOTERM 5 V UART (TXU0202-Q1, B side powered only by the heater)")
add("J2", "AUTOTERM", "conn:J2", "Connector_Molex:Molex_Nano-Fit_105313-xx04_1x04_P2.50mm_Horizontal",
    {"1": "AUTOTERM_5V", "2": "GND", "3": "CTRL_TX_TO_HEATER", "4": "CTRL_RX_FROM_HEATER"},
    mpn="1053131304", mfr="Molex", lcsc="C17554326", note="PCBWay global sourcing")
add("D8", "PESD5V0S1BA", "dev:D_TVS", SOD323, {"1": "AUTOTERM_5V", "2": "GND"},
    mpn="PESD5V0S1BA,115", mfr="Nexperia", lcsc="C19224", note="DEV-12: ESD on AUTOTERM_5V (was missing)")
CP("C46", "1uF", "AUTOTERM_5V", "GND")
add("U15", "TPS22945DCKR", "ic:TPS22945", SC705,
    {"1": "AUTOTERM_5V_P", "2": "GND", "3": None, "4": "AUTOTERM_5V", "5": "AUTOTERM_5V"},
    mpn="TPS22945DCKR", mfr="Texas Instruments", lcsc="C47507", note="100 mA current limit")
CP("C47", "100nF", "AUTOTERM_5V_P", "GND")
add("U16", "TXU0202QDCURQ1", "ic:TXU0202", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm",
    {"1": "AT_RX_B", "2": "GND", "3": "3V3", "4": "AUTOTERM_RX_3V3", "5": "AUTOTERM_TX_3V3",
     "6": "AUTOTERM_OE", "7": "AUTOTERM_5V_P", "8": "AT_TX_B"},
    mpn="TXU0202QDCURQ1", mfr="Texas Instruments", lcsc="C7372013")
CP("C48", "100nF", "3V3", "GND")
RP("R51", "100k", "AUTOTERM_OE", "GND", note="TX to heater Hi-Z until firmware enables")
RP("R52", "100R", "AT_TX_B", "CTRL_TX_TO_HEATER")
RP("R53", "100R", "CTRL_RX_FROM_HEATER", "AT_RX_B")
add("D9", "PESD5V0S2BT", "dev:D_Dual_CA", SOT23, {"1": "CTRL_TX_TO_HEATER", "2": "CTRL_RX_FROM_HEATER", "3": "GND"},
    mpn="PESD5V0S2BT,215", mfr="Nexperia", lcsc="C49338",
    note="DEV-13: bidirectional dual (PESD5V2S2UT-Q not stocked)")
TP("TP29", "AT_5V", "AUTOTERM_5V_P")
TP("TP30", "AT_TX_3V3", "AUTOTERM_TX_3V3")
TP("TP31", "AT_RX_3V3", "AUTOTERM_RX_3V3")
TP("TP32", "AT_TX_5V", "CTRL_TX_TO_HEATER")
TP("TP33", "AT_RX_5V", "CTRL_RX_FROM_HEATER")
TP("TP34", "AT_OE", "AUTOTERM_OE")

block("1-Wire: 3 × DS18B20 on one trunk, switched current-limited supply")
add("J3", "1-WIRE", "conn:J3", "Connector_Molex:Molex_Nano-Fit_105313-xx03_1x03_P2.50mm_Horizontal",
    {"1": "3V3_SENSOR", "2": "1WIRE_DQ", "3": "GND"}, mpn="1053131303", mfr="Molex", lcsc="C17198650",
    note="PCBWay global sourcing")
add("U17", "TPS22945DCKR", "ic:TPS22945", SC705,
    {"1": "3V3_SENSOR", "2": "GND", "3": None, "4": "SENSOR_EN", "5": "3V3"},
    mpn="TPS22945DCKR", mfr="Texas Instruments", lcsc="C47507")
RP("R54", "100k", "SENSOR_EN", "GND")
CP("C49", "1uF", "3V3", "GND")
CP("C50", "100nF", "3V3_SENSOR", "GND")
RP("R55", "4.7k", "3V3_SENSOR", "1WIRE_DQ")
RP("R56", "0R", "1WIRE_DQ_MCU", "1WIRE_DQ", note="tuning link")
add("D10", "PESD3V3S2UT", "dev:D_Dual_CA", SOT23, {"1": "1WIRE_DQ", "2": "3V3_SENSOR", "3": "GND"},
    mpn="PESD3V3S2UT-QR", mfr="Nexperia", lcsc="C7508770")
TP("TP35", "1WIRE", "1WIRE_DQ")
TP("TP36", "3V3_SENS", "3V3_SENSOR")
TP("TP37", "SENSOR_EN", "SENSOR_EN")

# ==========================================================================
# Sheet 6 – External button, lighting, diagnostics
# ==========================================================================
sheet("Controls")
block("External APEM button + ring LED (J4, 3 m cable)")
add("J4", "BUTTON+LED", "conn:J4", "Connector_Molex:Molex_Nano-Fit_105313-xx05_1x05_P2.50mm_Horizontal",
    {"1": "BUTTON_N_EXT", "2": "GND", "3": "LED_CC_PLUS", "4": "LED_PWM_MINUS", "5": None},
    mpn="1053131305", mfr="Molex", lcsc="C17316840", note="PCBWay global sourcing; pin 5 NC")
RP("R57", "1k", "BUTTON_N_EXT", "BUTTON_N")
RP("R58", "10k", "3V3", "BUTTON_N")
CP("C51", "10nF", "BUTTON_N", "GND")
add("D11", "PESD3V3S1BA", "dev:D_TVS", SOD323, {"1": "BUTTON_N_EXT", "2": "GND"},
    mpn="PESD3V3S1BA", mfr="Nexperia", lcsc="C7472904")
add("F1", "50mA PTC", "dev:Polyfuse", "Fuse:Fuse_1210_3225Metric", {"1": "VIN_SYS", "2": "LED_CC_PLUS"},
    mpn="MF-USMF005-2", mfr="Bourns", lcsc="C118758",
    note="DEV-14: short-circuit protection of the 3 m LED wire (was 0 Ω)")
add("U18", "BCR421UW6", "ic:BCR421", SOT236,
    {"1": "BTN_LED_EN", "2": "LED_PWM_MINUS", "3": "LED_PWM_MINUS", "4": "GND", "5": "LED_PWM_MINUS", "6": None},
    mpn="BCR421UW6-7", mfr="Diodes Inc.", lcsc="C194382",
    note="DEV-15: non-Q sibling of BCR421UW6Q-7 (not stocked); 10 mA preset")
RP("R59", "100R", "BUTTON_LED_PWM", "BTN_LED_EN")
RP("R60", "100k", "BTN_LED_EN", "GND")
add("D12", "PESD24VL1BA", "dev:D_TVS", SOD323, {"1": "LED_PWM_MINUS", "2": "GND"},
    mpn="PESD24VL1BA,115", mfr="Nexperia", lcsc="C69324")
add("D13", "PESD24VL1BA", "dev:D_TVS", SOD323, {"1": "LED_CC_PLUS", "2": "GND"},
    mpn="PESD24VL1BA,115", mfr="Nexperia", lcsc="C69324", note="ESD on the LED supply wire")
TP("TP38", "BUTTON", "BUTTON_N")
TP("TP39", "BTN_PWM", "BUTTON_LED_PWM")

block("Front light AL8861Q buck LED driver (Diodes DS41798 Rev 4-2)")
add("U19", "AL8861QMP-13", "ic:AL8861", "Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.68x1.88mm",
    {"1": "FL_ISENSE", "2": "GND", "3": "GND", "4": "FRONTLIGHT_PWM", "5": "FL_LX", "6": "FL_LX",
     "7": None, "8": "VIN_SYS", "9": "GND"},
    mpn="AL8861QMP-13", mfr="Diodes Inc.", lcsc="C2678638")
CP("C52", "4.7uF50_1210", "VIN_SYS", "GND", note="AL8861 input, C52+C53 ≥ 9.4 µF X7R (10 µF/50 V 1210 not stocked)")
CP("C53", "4.7uF50", "VIN_SYS", "GND")
R("R61", "2.0Ω 1%", "VIN_SYS", "FL_ISENSE", "1206W4F200LT5E", "C25335", fp=R1206, mfr="UNI-ROYAL",
  note="ILED = 0.1 V / 2.0 Ω = 50 mA (47…53 mA)")
RP("R62", "4.7k", "FRONTLIGHT_PWM", "GND", note="DEV-16: VSET has an internal pull-up; 4.7 kΩ forces OFF")
add("L4", "47µH", "dev:L", "Inductor_SMD:L_Taiyo-Yuden_NR-40xx", {"1": "FL_LED_K", "2": "FL_LX"},
    mpn="NRS4018T470MDGJV", mfr="Taiyo Yuden", lcsc="C5355142")
add("D14", "B140Q", "dev:D_Schottky", SMA, {"1": "VIN_SYS", "2": "FL_LX"},
    mpn="B140Q-13-F", mfr="Diodes Inc.", lcsc="C134430")
add("J8", "FRONTLIGHT 6p", "conn:FPC6L", "Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal",
    {"1": "FL_LED_A", "2": "FL_LED_A", "3": None, "4": None, "5": "FL_LED_K", "6": "FL_LED_K", "MP": "GND"},
    mpn="FH12-6S-0.5SH(55)", mfr="Hirose", lcsc="C202118")
RP("R63", "0R", "FL_ISENSE", "FL_LED_A", note="current measurement link")
TP("TP40", "FL_ISENSE", "FL_ISENSE")
TP("TP41", "FL_PWM", "FRONTLIGHT_PWM")

block("Energy-flow diagnostics: 12V/USB → 3V3 → RUN → HEAT, lit only while DIAG is pressed")
add("SW3", "DIAG", "dev:SW_Push", SW_TACT, {"1": "DIAG_N", "2": "GND"},
    mpn="TS-1187A-B-A-B", mfr="XKB", lcsc="C318884")
RP("R64", "100k", "VIN_SYS", "DIAG_N")
RP("R65", "47k", "DIAG_N", "DIAG_BASE")
add("Q5", "BC857B", "dev:Q_PNP", SOT23, {"1": "DIAG_BASE", "2": "VIN_SYS", "3": "DIAG_DRIVE"},
    mpn="BC857BLT1G", mfr="onsemi", lcsc="C111644")
RP("R66", "47k", "DIAG_DRIVE", "DIAG_GATE")
RP("R67", "100k", "DIAG_GATE", "GND")
add("Q6", "2N7002K", "dev:Q_NMOS", SOT23, {"1": "DIAG_GATE", "2": "GND", "3": "DIAG_CATHODE"},
    mpn="2N7002K-7", mfr="Diodes Inc.", lcsc="C85047")
for i, (name, src, rv) in enumerate([("12V", "VIN_12V_PROT", "12k"), ("USB", "USB_VBUS", "3.3k"),
                                     ("3V3", "3V3", "1.2k"), ("HEAT", "AUTOTERM_5V", "3.3k")]):
    led, res, dio = f"LED{i + 1}", f"R{68 + i}", f"D{15 + i}"
    add(led, f"{name} red", "dev:LED", LED0603, {"1": f"LED_{name}_K", "2": src},
        mpn="LTST-C190KRKT", mfr="Lite-On", lcsc="C94869")
    RP(res, rv, f"LED_{name}_K", f"LED_{name}_ISO")
    add(dio, "BAS116", "dev:D_SOT23", SOT23, {"1": f"LED_{name}_ISO", "2": None, "3": "DIAG_CATHODE"},
        mpn="BAS116,215", mfr="Nexperia", lcsc="C48502")
add("LED5", "RUN red", "dev:LED", LED0603, {"1": "LED_RUN_K", "2": "3V3"},
    mpn="LTST-C190KRKT", mfr="Lite-On", lcsc="C94869")
RP("R72", "1.2k", "LED_RUN_K", "RUN_DRAIN")
add("Q7", "2N7002K", "dev:Q_NMOS", SOT23, {"1": "DIAG_RUN", "2": "RUN_ISO", "3": "RUN_DRAIN"},
    mpn="2N7002K-7", mfr="Diodes Inc.", lcsc="C85047")
add("D19", "BAS116", "dev:D_SOT23", SOT23, {"1": "RUN_ISO", "2": None, "3": "DIAG_CATHODE"},
    mpn="BAS116,215", mfr="Nexperia", lcsc="C48502")
RP("R73", "100k", "DIAG_RUN", "GND")
RP("R74", "2.7k", "STATUS_LED_1", "STATUS1_A", dnp=True)
add("LED6", "STATUS1 red", "dev:LED", LED0603, {"1": "GND", "2": "STATUS1_A"},
    mpn="LTST-C190KRKT", mfr="Lite-On", lcsc="C94869", dnp=True)
RP("R75", "2.7k", "STATUS_LED_2", "STATUS2_A", dnp=True)
add("LED7", "STATUS2 red", "dev:LED", LED0603, {"1": "GND", "2": "STATUS2_A"},
    mpn="LTST-C190KRKT", mfr="Lite-On", lcsc="C94869", dnp=True)
TP("TP42", "DIAG", "DIAG_N")
TP("TP43", "DIAG_GND", "GND")
TP("TP44", "RUN", "DIAG_RUN")

# --------------------------------------------------------------------------
SHEETS = [
    ("Power", "01_Power.kicad_sch", "Power input, USB-C and 3.3 V"),
    ("MCU", "02_MCU.kicad_sch", "ESP32-S3, reset, boot and native USB"),
    ("Display", "03_Display.kicad_sch", "E-paper rail, isolation and booster"),
    ("Touch_RTC", "04_Touch_RTC.kicad_sch", "Touch always-on rail and RTC"),
    ("IO", "05_IO.kicad_sch", "AUTOTERM UART and 1-Wire"),
    ("Controls", "06_Controls.kicad_sch", "Button, lighting and diagnostics"),
]

POWER_NETS = {"GND", "3V3", "3V0_AON", "3V3_DISP", "3V3_SENSOR", "VIN_SYS", "USB_VBUS",
              "BATT_12V_IN", "VIN_12V_PROT", "AUTOTERM_5V", "AUTOTERM_5V_P"}


def by_ref() -> dict[str, Part]:
    return {p.ref: p for p in PARTS}


def nets() -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {}
    for p in PARTS:
        for pin, net in p.pins.items():
            if net:
                out.setdefault(net, []).append((p.ref, pin))
    return out


def check() -> list[str]:
    errs = []
    refs = [p.ref for p in PARTS]
    dup = {r for r in refs if refs.count(r) > 1}
    if dup:
        errs.append(f"duplicate refs: {sorted(dup)}")
    for net, members in nets().items():
        if len(members) < 2:
            only = members[0]
            part = by_ref()[only[0]]
            if part.symbol != "dev:TestPoint" and not part.dnp:
                errs.append(f"single-pin net {net}: {members}")
    return errs


if __name__ == "__main__":
    problems = check()
    print(f"{len(PARTS)} parts, {len(nets())} nets")
    for line in problems:
        print("WARN", line)
