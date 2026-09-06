#!/usr/bin/env python3
"""Generate the Revision-A KiCad hierarchy from the reviewed hardware definition.

The generator deliberately uses only Python's standard library.  It keeps the
large, repetitive symbol/pin metadata reviewable in one place and produces
ordinary, editable KiCad schematic files plus the project-local symbol library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import uuid


ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hardware"
SYMLIB = HW / "libraries" / "symbols" / "LandyHeater.kicad_sym"
NS = uuid.UUID("83b760b8-4caf-4aa1-8e08-cd4c5ec23917")


def uid(*parts: object) -> str:
    return str(uuid.uuid5(NS, "|".join(str(p) for p in parts)))


def q(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def symbol_key(value: str, pins: list[tuple[str, str, str | None]]) -> str:
    raw = value + "_" + "_".join(number + name for number, name, _ in pins)
    return re.sub(r"[^A-Za-z0-9_]+", "_", raw).strip("_")[:90]


@dataclass
class Part:
    ref: str
    value: str
    footprint: str
    pins: list[tuple[str, str, str | None]]
    mpn: str = ""
    manufacturer: str = ""
    datasheet: str = ""
    assembly: str = "SMT"
    note: str = ""
    dnp: bool = False
    x: float = 0
    y: float = 0
    key: str = field(init=False)

    def __post_init__(self) -> None:
        self.key = symbol_key(self.value, self.pins)


def P(ref: str, value: str, footprint: str, nets: tuple[str | None, ...], **kwargs: str | bool) -> Part:
    pins = [(str(index + 1), str(index + 1), net) for index, net in enumerate(nets)]
    return Part(ref, value, footprint, pins, **kwargs)


R0603 = "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"
C0603 = "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
C0805 = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
SOD123 = "Diode_SMD:D_SOD-123"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
SOT236 = "Package_TO_SOT_SMD:SOT-23-6"
SC706 = "Package_TO_SOT_SMD:SOT-363_SC-70-6"


def passive(ref: str, value: str, a: str | None, b: str | None, footprint: str, **kw: str | bool) -> Part:
    return P(ref, value, footprint, (a, b), **kw)


def connector(ref: str, value: str, footprint: str, nets: list[str | None], **kw: str | bool) -> Part:
    return P(ref, value, footprint, tuple(nets), **kw)


def pages() -> list[tuple[str, str, list[Part], list[str]]]:
    power: list[Part] = [
        connector("J1", "1053131302 / 12V INPUT", "Connector_Molex:Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal", ["BATT_12V", "GND"], mpn="1053131302", manufacturer="Molex", assembly="THT"),
        passive("D1", "TPSMB18CA-VR", "BATT_12V", "GND", "Diode_SMD:D_SMB", mpn="TPSMB18CA-VR", manufacturer="STMicroelectronics", datasheet="https://www.st.com/resource/en/datasheet/tpsmb.pdf"),
        Part("U1", "LM74720QDRRRQ1", "Package_SON:WSON-12-1EP_3x3mm_P0.5mm_EP1.5x2.5mm_ThermalVias", [
            ("1", "GATE", "Q1_GATE"), ("2", "A", "BATT_12V"), ("3", "VSNS", "BATT_12V"),
            ("4", "SW", "OV_TOP"), ("5", "OV", "OV_SENSE"), ("6", "EN", "BATT_12V"),
            ("7", "GND", "GND"), ("8", "PD", "Q2_GATE"), ("9", "LX", "BOOST_LX"),
            ("10", "CAP", "BOOST_CAP"), ("11", "VS", "FET_COMMON"), ("12", "C", "FET_COMMON"),
            ("13", "RTN/EP", None)], mpn="LM74720QDRRRQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/lm74720-q1.pdf", note="RTN/EP MUST FLOAT"),
        Part("Q1", "IPG20N06S4L-26", "LandyHeater:PROVISIONAL_Infineon_PG-TDSON-8-4_Dual", [
            ("1", "S1", "BATT_12V"), ("2", "G1", "Q1_GATE"), ("3", "S2", "VIN_12V_PROTECTED"),
            ("4", "G2", "Q2_GATE_FET"), ("5", "D2", "FET_COMMON"), ("6", "D2", "FET_COMMON"),
            ("7", "D1", "FET_COMMON"), ("8", "D1", "FET_COMMON")], mpn="IPG20N06S4L-26", manufacturer="Infineon", datasheet="https://www.infineon.com/assets/row/public/documents/10/49/infineon-ipg20n06s4l-26-datasheet-en.pdf", note="Provisional 8-pad footprint; replace with official split-exposed-pad PG-TDSON-8-4 land pattern before layout freeze"),
        passive("L1", "100uH >175mA XPL2010-104ML", "FET_COMMON", "BOOST_LX", "Inductor_SMD:L_0805_2012Metric_Pad1.05x1.20mm_HandSolder", mpn="XPL2010-104ML", manufacturer="Coilcraft"),
        passive("C1", "1uF 50V X7R", "BOOST_CAP", "FET_COMMON", C0805),
        passive("C2", "1uF 50V X7R", "FET_COMMON", "GND", C0805),
        passive("C3", "100nF 50V X7R", "BATT_12V", "GND", C0603),
        passive("R1", "100k 1%", "OV_TOP", "OV_SENSE", R0603),
        passive("R2", "7.15k 1%", "OV_SENSE", "GND", R0603, note="OV cut-off nominal 18.45V"),
        passive("R3", "0R", "Q2_GATE", "Q2_GATE_FET", R0603),
        passive("C4", "10nF 50V", "Q2_GATE_FET", "VIN_12V_PROTECTED", C0603, note="PD slew; validate inrush"),
        passive("FB1", "220R@100MHz 3A", "VIN_12V_PROTECTED", "VIN_SYS", "Inductor_SMD:L_0805_2012Metric_Pad1.05x1.20mm_HandSolder", mpn="MPZ2012S221A", manufacturer="TDK"),
        passive("C5", "4.7uF 50V X7R", "VIN_12V_PROTECTED", "GND", C0805),
        passive("C6", "22uF 25V X7R", "VIN_SYS", "GND", "Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder"),
        Part("J5", "USB4105-GF-A-120", "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", [
            ("A1", "GND", "GND"), ("A4", "VBUS", "USB_VBUS"), ("A5", "CC1", "CC1"), ("A6", "D+", "USB_D_P_CONN"),
            ("A7", "D-", "USB_D_N_CONN"), ("A8", "SBU1", None), ("A9", "VBUS", "USB_VBUS"), ("A12", "GND", "GND"),
            ("B1", "GND", "GND"), ("B4", "VBUS", "USB_VBUS"), ("B5", "CC2", "CC2"), ("B6", "D+", "USB_D_P_CONN"),
            ("B7", "D-", "USB_D_N_CONN"), ("B8", "SBU2", None), ("B9", "VBUS", "USB_VBUS"), ("B12", "GND", "GND"),
            ("SH", "SHIELD", "USB_SHIELD")], mpn="USB4105-GF-A-120", manufacturer="GCT"),
        passive("R68", "0R", "USB_SHIELD", "GND", R0603, note="USB shield bond; placement directly at J5"),
        passive("D2", "ESD5Z5.0T1G", "USB_VBUS", "GND", "Diode_SMD:D_SOD-523", mpn="ESD5Z5.0T1G", manufacturer="onsemi"),
        Part("U2", "TUSB321AIRWBR", "Package_DFN_QFN:Texas_X2QFN-12_1.6x1.6mm_P0.4mm", [
            ("1", "CC1", "CC1"), ("2", "CC2", "CC2"), ("3", "CURRENT_MODE", "GND"), ("4", "PORT", "GND"),
            ("5", "VBUS_DET", "USB_VBUS_DET"), ("6", "VCONN_FAULT", None), ("7", "OUT1", "USB_HIGH_CURRENT_N"),
            ("8", "OUT2", "USB_CURRENT_3A_N"), ("9", "ID", None), ("10", "GND", "GND"), ("11", "DIR", None), ("12", "VDD", "USB_VBUS")],
            mpn="TUSB321AIRWBR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tusb321ai.pdf"),
        passive("R4", "900k 1%", "USB_VBUS", "USB_VBUS_DET", R0603),
        passive("R5", "220k", "3V3_CORE", "USB_HIGH_CURRENT_N", R0603),
        passive("R6", "220k", "3V3_CORE", "USB_CURRENT_3A_N", R0603),
        passive("C7", "100nF", "USB_VBUS", "GND", C0603),
        Part("U3", "TPS259470LRPWR", "Package_DFN_QFN:LQFN-10-1EP_2x2mm_P0.5mm_EP0.7x0.7mm", [
            ("1", "EN/UVLO", "USB_VBUS"), ("2", "OVLO", "USB_OVLO"), ("3", "AUXOFF", None), ("4", "FLT", "USB_EFUSE_FAULT_N"),
            ("5", "IN", "USB_VBUS"), ("6", "OUT", "USB_PROTECTED"), ("7", "DVDT", "USB_DVDT"), ("8", "GND", "GND"),
            ("9", "ILM", "USB_ILM"), ("10", "ITIMER", None), ("11", "EP", "GND")], mpn="TPS259470LRPWR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps25947.pdf"),
        passive("R7", "100k 1%", "USB_VBUS", "USB_OVLO", R0603),
        passive("R8", "26.1k 1%", "USB_OVLO", "GND", R0603, note="OVLO approx 5.95V"),
        passive("R9", "3.32k 1%", "USB_ILM", "GND", R0603, note="ILIM nominal 1.0A"),
        passive("C8", "10nF", "USB_DVDT", "GND", C0603),
        Part("NT1", "USB POWER OR NET-TIE", "NetTie:NetTie-2_SMD_Pad0.5mm", [("1", "USB_SIDE", "USB_PROTECTED"), ("2", "SYSTEM_SIDE", "VIN_SYS")], assembly="SMT", note="Logical boundary after true reverse-blocking eFuse"),
        Part("U4", "LMR43620MSC3RPERQ1", "LandyHeater:Texas_RPE0009A_VQFN-HR-9_2x2mm", [
            ("1", "MODE/SYNC", "GND"), ("2", "PGOOD", "BUCK_PGOOD"), ("3", "EN/UVLO", "VIN_SYS"),
            ("4", "VIN", "VIN_SYS"), ("5", "SW", "BUCK_SW"), ("6", "BOOT", "BUCK_BOOT"),
            ("7", "VCC", "BUCK_VCC"), ("8", "VOUT/FB", "3V3_CORE"), ("9", "GND/EP", "GND")],
            mpn="LMR43620MSC3RPERQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/lmr43620-q1.pdf"),
        passive("L2", "3.3uH 3A", "BUCK_SW", "3V3_CORE", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", mpn="XAL4020-332MEB", manufacturer="Coilcraft"),
        passive("C9", "100nF 10V", "BUCK_BOOT", "BUCK_SW", C0603),
        passive("C10", "1uF 10V", "BUCK_VCC", "GND", C0603),
        passive("C11", "4.7uF 50V", "VIN_SYS", "GND", C0805),
        passive("C12", "100nF 50V", "VIN_SYS", "GND", C0603),
        passive("C13", "22uF 10V", "3V3_CORE", "GND", C0805),
        passive("C14", "22uF 10V", "3V3_CORE", "GND", C0805),
        passive("R10", "100k", "3V3_CORE", "BUCK_PGOOD", R0603),
        connector("TP1", "TP_BATT_12V", "TestPoint:TestPoint_Pad_D1.5mm", ["BATT_12V"], assembly="DNP", dnp=True),
        connector("TP2", "TP_USB_VBUS", "TestPoint:TestPoint_Pad_D1.5mm", ["USB_VBUS"], assembly="DNP", dnp=True),
        connector("TP3", "TP_VIN_SYS", "TestPoint:TestPoint_Pad_D1.5mm", ["VIN_SYS"], assembly="DNP", dnp=True),
        connector("TP4", "TP_3V3", "TestPoint:TestPoint_Pad_D1.5mm", ["3V3_CORE"], assembly="DNP", dnp=True),
        connector("TP5", "TP_GND", "TestPoint:TestPoint_Pad_D1.5mm", ["GND"], assembly="DNP", dnp=True),
    ]

    esp: list[Part] = [
        Part("U5", "ESP32-S3-WROOM-1U-N16R8", "RF_Module:ESP32-S3-WROOM-1U", [
            ("1", "GND", "GND"), ("2", "3V3", "3V3_CORE"), ("3", "EN", "CHIP_PU"), ("4", "IO4", "1WIRE_DQ"),
            ("5", "IO5", "I2C_SDA"), ("6", "IO6", "I2C_SCL"), ("7", "IO7", "TOUCH_RESET_RELEASE"), ("8", "IO15", "SENSOR_EN"),
            ("9", "IO16", "AUTOTERM_TX_3V3"), ("10", "IO17", "AUTOTERM_RX_3V3"), ("11", "IO18", "LATCH_CLR_GPIO_N"), ("12", "IO8", "EPD_BUSY_GPIO"),
            ("13", "IO19/USB_D-", "USB_D_N_ESP"), ("14", "IO20/USB_D+", "USB_D_P_ESP"), ("15", "IO3", None), ("16", "IO46", None),
            ("17", "IO9", "EPD_SCLK_GPIO"), ("18", "IO10", "EPD_SDIO_GPIO"), ("19", "IO11", "EPD_CS_GPIO_N"), ("20", "IO12", "EPD_DC_GPIO"),
            ("21", "IO13", "EPD_RESET_GPIO_N"), ("22", "IO14", "DISPLAY_EN"), ("23", "IO21", "FRONTLIGHT_PWM"), ("24", "IO47", "AUTOTERM_OE"),
            ("25", "IO48", None), ("26", "IO45", None), ("27", "IO0", "BOOT_N"), ("28", "IO35/PSRAM", None),
            ("29", "IO36/PSRAM", None), ("30", "IO37/PSRAM", None), ("31", "IO38", "BUTTON_LED_PWM"), ("32", "IO39", "DIAG_RUN"),
            ("33", "IO40", "USB_HIGH_CURRENT_N"), ("34", "IO41", "STATUS_LED_1"), ("35", "IO42", "STATUS_LED_2"),
            ("36", "U0RXD/IO44", "U0RXD_TEST"), ("37", "U0TXD/IO43", "U0TXD_RAW"), ("38", "IO2", "TOUCH_INT_N"),
            ("39", "IO1", "BUTTON_N"), ("40", "GND", "GND"), ("41", "EPAD", "GND")],
            mpn="ESP32-S3-WROOM-1U-N16R8", manufacturer="Espressif", datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf"),
        passive("C15", "10uF 10V", "3V3_CORE", "GND", C0805),
        passive("C16", "1uF 10V", "3V3_CORE", "GND", C0603),
        passive("C17", "100nF", "3V3_CORE", "GND", C0603),
        Part("U6", "TPS3808G33QDBVRQ1", SOT236, [("1", "RESET_N", "CHIP_PU"), ("2", "GND", "GND"), ("3", "MR_N", "RESET_MR_N"), ("4", "CT", None), ("5", "SENSE", "3V3_CORE"), ("6", "VDD", "3V3_CORE")], mpn="TPS3808G33QDBVRQ1", manufacturer="Texas Instruments"),
        passive("R11", "10k", "3V3_CORE", "CHIP_PU", R0603),
        passive("C18", "1uF", "CHIP_PU", "GND", C0603, note="Espressif EN RC"),
        passive("C19", "100nF", "3V3_CORE", "GND", C0603),
        Part("SW1", "RESET KMR221GLFS", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", [("1", "A", "RESET_MR_N"), ("2", "B", "GND")], mpn="KMR221GLFS", manufacturer="C&K"),
        passive("R12", "10k", "3V3_CORE", "RESET_MR_N", R0603),
        Part("SW2", "BOOT KMR221GLFS", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", [("1", "A", "BOOT_N"), ("2", "B", "GND")], mpn="KMR221GLFS", manufacturer="C&K"),
        passive("R13", "10k", "3V3_CORE", "BOOT_N", R0603),
        Part("U7", "TPD2EUSB30DRTR", "Package_TO_SOT_SMD:SOT-23-5", [("1", "D1_IN", "USB_D_N_CONN"), ("2", "GND", "GND"), ("3", "D2_IN", "USB_D_P_CONN"), ("4", "D2_OUT", "USB_D_P_PROT"), ("5", "D1_OUT", "USB_D_N_PROT")], mpn="TPD2EUSB30DRTR", manufacturer="Texas Instruments"),
        passive("R14", "22R", "USB_D_N_PROT", "USB_D_N_ESP", R0603),
        passive("R15", "22R", "USB_D_P_PROT", "USB_D_P_ESP", R0603),
        passive("R16", "499R", "U0TXD_RAW", "U0TXD_TEST", R0603),
        passive("R54", "33R", "EPD_SCLK_GPIO", "EPD_SCLK", R0603),
        passive("R55", "33R", "EPD_SDIO_GPIO", "EPD_SDIO_MOSI", R0603),
        passive("R56", "33R", "EPD_CS_GPIO_N", "EPD_CS_N", R0603),
        passive("R57", "33R", "EPD_DC_GPIO", "EPD_DC", R0603),
        passive("R58", "33R", "EPD_RESET_GPIO_N", "EPD_RESET_N", R0603),
        passive("R59", "33R", "EPD_BUSY", "EPD_BUSY_GPIO", R0603),
        connector("TP6", "U0TXD", "TestPoint:TestPoint_Pad_D1.0mm", ["U0TXD_TEST"], assembly="DNP", dnp=True),
        connector("TP7", "U0RXD", "TestPoint:TestPoint_Pad_D1.0mm", ["U0RXD_TEST"], assembly="DNP", dnp=True),
        connector("TP8", "USB_EFUSE_FAULT", "TestPoint:TestPoint_Pad_D1.0mm", ["USB_EFUSE_FAULT_N"], assembly="DNP", dnp=True),
        connector("TP9", "USB_CURRENT_3A", "TestPoint:TestPoint_Pad_D1.0mm", ["USB_CURRENT_3A_N"], assembly="DNP", dnp=True),
    ]

    display: list[Part] = [
        Part("U8", "TPS22919QDCKRQ1", SC706, [("1", "IN", "3V3_CORE"), ("2", "GND", "GND"), ("3", "ON", "DISPLAY_EN"), ("4", "NC", None), ("5", "QOD", "3V3_DISPLAY_SW"), ("6", "VOUT", "3V3_DISPLAY_SW")], mpn="TPS22919QDCKRQ1", manufacturer="Texas Instruments"),
        passive("R17", "100k", "DISPLAY_EN", "GND", R0603),
        passive("C20", "1uF", "3V3_CORE", "GND", C0603),
        passive("C21", "4.7uF 25V", "3V3_DISPLAY_SW", "GND", C0805, note="Good Display C4 input bypass"),
        Part("U9", "SN74AXC8T245PWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", [
            ("1", "VCCA", "3V3_CORE"), ("2", "DIR1", "3V3_CORE"), ("3", "A1", "EPD_SCLK"), ("4", "A2", "EPD_SDIO_MOSI"),
            ("5", "A3", "EPD_CS_N"), ("6", "A4", "EPD_DC"), ("7", "A5", "EPD_RESET_N"), ("8", "A6", None), ("9", "A7", None), ("10", "A8", None),
            ("11", "DIR2", "3V3_CORE"), ("12", "GND", "GND"), ("13", "GND", "GND"), ("14", "B8", None), ("15", "B7", None), ("16", "B6", None),
            ("17", "B5", "EPD_RESET_PANEL_N"), ("18", "B4", "EPD_DC_PANEL"), ("19", "B3", "EPD_CS_PANEL_N"), ("20", "B2", "EPD_SDIO_PANEL"),
            ("21", "B1", "EPD_SCLK_PANEL"), ("22", "OE_N", "EPD_LEVEL_OE_N"), ("23", "VCCB", "3V3_DISPLAY_SW"), ("24", "VCCB", "3V3_DISPLAY_SW")], mpn="SN74AXC8T245PWR", manufacturer="Texas Instruments"),
        passive("R18", "100k", "3V3_CORE", "EPD_LEVEL_OE_N", R0603),
        Part("Q2", "2N7002KQ-13", SOT23, [("1", "G", "DISPLAY_EN"), ("2", "S", "GND"), ("3", "D", "EPD_LEVEL_OE_N")], mpn="2N7002KQ-13", manufacturer="Diodes Inc."),
        Part("U10", "SN74AXC1T45DCKR", SC706, [("1", "VCCA", "3V3_CORE"), ("2", "GND", "GND"), ("3", "A", "EPD_BUSY"), ("4", "B", "EPD_BUSY_PANEL"), ("5", "DIR", "GND"), ("6", "VCCB", "3V3_DISPLAY_SW")], mpn="SN74AXC1T45DCKR", manufacturer="Texas Instruments"),
        passive("R19", "100k", "EPD_BUSY", "GND", R0603),
        connector("J6", "FH12-24S-0.5SH(55) E-PAPER", "Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal", [None, "EPD_GDR", "EPD_RESE", None, "EPD_VSH2", None, None, "GND", "EPD_BUSY_PANEL", "EPD_RESET_PANEL_N", "EPD_DC_PANEL", "EPD_CS_PANEL_N", "EPD_SCLK_PANEL", "EPD_SDIO_PANEL", "3V3_DISPLAY_SW", "3V3_DISPLAY_SW", "GND", "EPD_VDD", None, "EPD_VSH1", "EPD_PREVGH", "EPD_VSL", "EPD_PREVGL", "EPD_VCOM"], mpn="FH12-24S-0.5SH(55)", manufacturer="Hirose", note="PROVISIONAL bottom-contact; verify original display"),
        passive("R20", "1M 1%", "EPD_GDR", "GND", R0603, note="Good Display chapter 12"),
        passive("R21", "2.2R 1%", "EPD_RESE", "GND", R0603, note="Good Display chapter 12"),
        passive("C22", "1uF 25V", "EPD_VSH2", "GND", C0805),
        passive("C23", "1uF 25V", "3V3_DISPLAY_SW", "GND", C0805),
        passive("C24", "1uF 25V", "EPD_VDD", "GND", C0805),
        passive("C25", "1uF 25V", "EPD_VSH1", "GND", C0805),
        Part("Q3", "SI1308EDL-T1-GE3", "Package_TO_SOT_SMD:SOT-323_SC-70", [("1", "G", "EPD_GDR"), ("2", "S", "EPD_RESE"), ("3", "D", "EPD_BOOST_SW")], mpn="SI1308EDL-T1-GE3", manufacturer="Vishay"),
        passive("L3", "47uH 500mA", "3V3_DISPLAY_SW", "EPD_BOOST_SW", "Inductor_SMD:L_Changjiang_FNR3015S", note="Good Display chapter 12; NR3015 class"),
        Part("D3", "MBR0530T1G", SOD123, [("1", "K", "EPD_PREVGH"), ("2", "A", "EPD_BOOST_SW")], mpn="MBR0530T1G", manufacturer="onsemi", note="Good Display D3; KiCad diode pad 1 is K"),
        Part("D4", "MBR0530T1G", SOD123, [("1", "K", "EPD_NEG_PUMP"), ("2", "A", "EPD_PREVGL")], mpn="MBR0530T1G", manufacturer="onsemi", note="Good Display D1; KiCad diode pad 1 is K"),
        Part("D5", "MBR0530T1G", SOD123, [("1", "K", "GND"), ("2", "A", "EPD_NEG_PUMP")], mpn="MBR0530T1G", manufacturer="onsemi", note="Good Display D2; KiCad diode pad 1 is K"),
        passive("C26", "4.7uF 25V", "EPD_BOOST_SW", "EPD_NEG_PUMP", C0805),
        passive("C27", "1uF 25V", "EPD_PREVGH", "GND", C0805),
        passive("C36", "1uF 25V", "EPD_PREVGH", "EPD_VSL", C0805),
        passive("C37", "1uF 25V", "EPD_VSL", "EPD_PREVGL", C0805),
        passive("C38", "1uF 25V", "EPD_VCOM", "GND", C0805),
        passive("R60", "100k", "EPD_SCLK_PANEL", "GND", R0603),
        passive("R61", "100k", "EPD_SDIO_PANEL", "GND", R0603),
        passive("R62", "100k", "3V3_DISPLAY_SW", "EPD_CS_PANEL_N", R0603),
        passive("R63", "100k", "EPD_DC_PANEL", "GND", R0603),
        passive("R64", "100k", "EPD_RESET_PANEL_N", "GND", R0603),
        connector("TP13", "EPD_3V3", "TestPoint:TestPoint_Pad_D1.0mm", ["3V3_DISPLAY_SW"], assembly="DNP", dnp=True),
        connector("TP14", "EPD_SCLK", "TestPoint:TestPoint_Pad_D1.0mm", ["EPD_SCLK_PANEL"], assembly="DNP", dnp=True),
        connector("TP15", "EPD_SDIO", "TestPoint:TestPoint_Pad_D1.0mm", ["EPD_SDIO_PANEL"], assembly="DNP", dnp=True),
        connector("TP16", "EPD_CS", "TestPoint:TestPoint_Pad_D1.0mm", ["EPD_CS_PANEL_N"], assembly="DNP", dnp=True),
        connector("TP17", "EPD_DC", "TestPoint:TestPoint_Pad_D1.0mm", ["EPD_DC_PANEL"], assembly="DNP", dnp=True),
        connector("TP18", "EPD_RESET", "TestPoint:TestPoint_Pad_D1.0mm", ["EPD_RESET_PANEL_N"], assembly="DNP", dnp=True),
        connector("TP19", "EPD_BUSY", "TestPoint:TestPoint_Pad_D1.0mm", ["EPD_BUSY_PANEL"], assembly="DNP", dnp=True),
    ]

    touch_rtc: list[Part] = [
        Part("U11", "TPS7A0230PDBVR", SOT235, [("1", "IN", "3V3_CORE"), ("2", "GND", "GND"), ("3", "EN", "3V3_CORE"), ("4", "NC", None), ("5", "OUT", "3V0_TOUCH_AON")], mpn="TPS7A0230PDBVR", manufacturer="Texas Instruments"),
        passive("C28", "1uF", "3V3_CORE", "GND", C0603),
        passive("C29", "1uF", "3V0_TOUCH_AON", "GND", C0603),
        passive("R24", "4.7k", "3V0_TOUCH_AON", "I2C_SDA", R0603),
        passive("R25", "4.7k", "3V0_TOUCH_AON", "I2C_SCL", R0603),
        Part("U12", "SN74LVC1G07QDBVRQ1", SOT235, [("1", "NC", None), ("2", "A", "TOUCH_RESET_RELEASE"), ("3", "GND", "GND"), ("4", "Y_OD", "TOUCH_RESET_N"), ("5", "VCC", "3V0_TOUCH_AON")], mpn="SN74LVC1G07QDBVRQ1", manufacturer="Texas Instruments"),
        passive("R26", "100k", "TOUCH_RESET_RELEASE", "GND", R0603),
        passive("R27", "10k", "3V0_TOUCH_AON", "TOUCH_RESET_N", R0603),
        connector("J7", "FH12-6S-0.5SH(55) TOUCH", "Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal", ["GND", "TOUCH_INT_PANEL_N", "TOUCH_RESET_N", "3V0_TOUCH_AON", "I2C_SCL", "I2C_SDA"], mpn="FH12-6S-0.5SH(55)", manufacturer="Hirose", note="PROVISIONAL pin/contact orientation; verify display"),
        passive("R28", "100R", "TOUCH_INT_PANEL_N", "TOUCH_INT_N", R0603),
        passive("R29", "10k", "3V0_TOUCH_AON", "TOUCH_INT_N", R0603),
        passive("R71", "10k DNP", "TOUCH_INT_N", "GND", R0603, assembly="DNP", dnp=True, note="Measurement-only pull-down option; never populate with R29"),
        passive("R30", "0R DNP", "TOUCH_INT_PANEL_N", "TOUCH_INT_N", R0603, assembly="DNP", dnp=True, note="Optional direct bypass of R28"),
        Part("U13", "SN74LVC1G74-Q1 WAKE LATCH OPTION", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", [("1", "CLR_N", "LATCH_CLR_N"), ("2", "D", "3V0_TOUCH_AON"), ("3", "CLK", "GND"), ("4", "PRE_N", "TOUCH_INT_PANEL_N"), ("5", "Q", None), ("6", "Q_N", "LATCH_Q_N"), ("7", "GND", "GND"), ("8", "VCC", "3V0_TOUCH_AON")], mpn="SN74LVC1G74QDCURQ1", manufacturer="Texas Instruments", assembly="DNP", dnp=True, note="DNP option: active-low touch INT asynchronously drives Q_N low; firmware clears after INT release"),
        passive("R31", "100k DNP", "3V0_TOUCH_AON", "LATCH_CLR_N", R0603, assembly="DNP", dnp=True),
        passive("C39", "100nF DNP", "LATCH_CLR_N", "GND", C0603, assembly="DNP", dnp=True, note="Power-on clear for optional wake latch"),
        passive("R69", "100R DNP", "LATCH_CLR_GPIO_N", "LATCH_CLR_N", R0603, assembly="DNP", dnp=True, note="Populate only with U13 latch; GPIO18 pulses low after touch INT releases"),
        passive("R70", "0R DNP", "LATCH_Q_N", "TOUCH_INT_N", R0603, assembly="DNP", dnp=True, note="Populate only with U13 latch; remove R28, R29 and R30"),
        Part("U14", "RV-3028-C7", "LandyHeater:RV-3028-C7", [("1", "CLKOUT", None), ("2", "INT_N", "RTC_INT_N"), ("3", "SCL", "I2C_SCL"), ("4", "SDA", "I2C_SDA"), ("5", "VSS", "GND"), ("6", "VBACKUP", "RTC_VBACKUP"), ("7", "VDD", "3V3_CORE"), ("8", "EVI", "GND")], mpn="RV-3028-C7-32.768kHz-1ppm-TA-QC", manufacturer="Micro Crystal"),
        passive("C30", "100nF", "3V3_CORE", "GND", C0603),
        Part("BT1", "BR1225 HOLDER", "Battery:BatteryHolder_Keystone_500", [("1", "+", "RTC_BAT_RAW"), ("2", "-", "GND")], mpn="500", manufacturer="Keystone", assembly="THT; cell fitted after assembly", note="Panasonic BR1225 primary cell"),
        Part("D6", "BAS116,215", SOT23, [("1", "A", "RTC_BAT_RAW"), ("2", "NC", None), ("3", "K", "RTC_VBACKUP")], mpn="BAS116,215", manufacturer="Nexperia"),
        connector("TP10", "RTC_INT", "TestPoint:TestPoint_Pad_D1.0mm", ["RTC_INT_N"], assembly="DNP", dnp=True),
    ]

    external: list[Part] = [
        connector("J2", "1053131304 / AUTOTERM", "Connector_Molex:Molex_Nano-Fit_105313-xx04_1x04_P2.50mm_Horizontal", ["AUTOTERM_5V_IN", "AUTOTERM_TX_WIRE", "AUTOTERM_RX_WIRE", "GND"], mpn="1053131304", manufacturer="Molex", assembly="THT"),
        Part("U15", "TPS22945DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5", [("1", "VOUT", "AUTOTERM_5V"), ("2", "GND", "GND"), ("3", "OC_N", None), ("4", "ON", "AUTOTERM_5V_IN"), ("5", "VIN", "AUTOTERM_5V_IN")], mpn="TPS22945DCKR", manufacturer="Texas Instruments", note="100mA-class protected heater supply; OC_N intentionally unused"),
        passive("C31", "1uF", "AUTOTERM_5V_IN", "GND", C0603),
        passive("C32", "100nF", "AUTOTERM_5V", "GND", C0603),
        Part("U16", "TXU0202QDCURQ1", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", [("1", "B2", "AUTOTERM_RX_PROT"), ("2", "GND", "GND"), ("3", "VCCA", "3V3_CORE"), ("4", "A2Y", "AUTOTERM_RX_3V3"), ("5", "A1", "AUTOTERM_TX_3V3"), ("6", "OE", "AUTOTERM_OE"), ("7", "VCCB", "AUTOTERM_5V"), ("8", "B1Y", "AUTOTERM_TX_PROT")], mpn="TXU0202QDCURQ1", manufacturer="Texas Instruments"),
        passive("R32", "100k", "AUTOTERM_OE", "GND", R0603),
        passive("R33", "100R", "AUTOTERM_TX_PROT", "AUTOTERM_TX_WIRE", R0603),
        passive("R34", "100R", "AUTOTERM_RX_WIRE", "AUTOTERM_RX_PROT", R0603),
        Part("D7", "PESD5V2S2UT-Q", SOT23, [("1", "IO1", "AUTOTERM_TX_WIRE"), ("2", "GND", "GND"), ("3", "IO2", "AUTOTERM_RX_WIRE")], mpn="PESD5V2S2UT-Q", manufacturer="Nexperia"),
        connector("J3", "1053131303 / 1-WIRE", "Connector_Molex:Molex_Nano-Fit_105313-xx03_1x03_P2.50mm_Horizontal", ["3V3_SENSOR_SW", "1WIRE_WIRE", "GND"], mpn="1053131303", manufacturer="Molex", assembly="THT"),
        Part("U17", "TPS22945DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5", [("1", "VOUT", "3V3_SENSOR_SW"), ("2", "GND", "GND"), ("3", "OC_N", None), ("4", "ON", "SENSOR_EN"), ("5", "VIN", "3V3_CORE")], mpn="TPS22945DCKR", manufacturer="Texas Instruments", note="OC_N intentionally unused"),
        passive("R35", "100k", "SENSOR_EN", "GND", R0603),
        passive("C33", "1uF", "3V3_CORE", "GND", C0603),
        passive("C34", "100nF", "3V3_SENSOR_SW", "GND", C0603),
        passive("R36", "4.7k", "3V3_SENSOR_SW", "1WIRE_DQ", R0603),
        passive("R37", "100R", "1WIRE_DQ", "1WIRE_WIRE", R0603),
        Part("D8", "PESD3V3S2UT-Q", SOT23, [("1", "IO1", "1WIRE_WIRE"), ("2", "GND", "GND"), ("3", "IO2", "3V3_SENSOR_SW")], mpn="PESD3V3S2UT-Q", manufacturer="Nexperia"),
        connector("TP11", "AUTOTERM_5V", "TestPoint:TestPoint_Pad_D1.0mm", ["AUTOTERM_5V"], assembly="DNP", dnp=True),
        connector("TP12", "1WIRE_DQ", "TestPoint:TestPoint_Pad_D1.0mm", ["1WIRE_DQ"], assembly="DNP", dnp=True),
    ]

    controls: list[Part] = [
        connector("J4", "1053131305 / BUTTON+LED", "Connector_Molex:Molex_Nano-Fit_105313-xx05_1x05_P2.50mm_Horizontal", ["BUTTON_WIRE", "BUTTON_LED_A", "BUTTON_LED_K", "GND", None], mpn="1053131305", manufacturer="Molex", assembly="THT", note="APEM AV970220000700 cable assembly; pin 5 reserve NC"),
        passive("R38", "1k", "BUTTON_WIRE", "BUTTON_N", R0603),
        passive("R39", "10k", "3V3_CORE", "BUTTON_N", R0603),
        passive("C35", "10nF", "BUTTON_N", "GND", C0603, note="3m cable debounce/EMI; validate wake"),
        Part("D9", "PESD3V3S1BA", "Diode_SMD:D_SOD-323", [("1", "IO", "BUTTON_WIRE"), ("2", "GND", "GND")], mpn="PESD3V3S1BA", manufacturer="Nexperia", note="Bidirectional 3.3V ESD protection for 3m button wire"),
        Part("D16", "PESD24VL1BA,115", "Diode_SMD:D_SOD-323", [("1", "IO", "BUTTON_LED_K"), ("2", "GND", "GND")], mpn="PESD24VL1BA,115", manufacturer="Nexperia", note="Bidirectional 24V ESD protection; LED cathode may rise to VIN_SYS when off"),
        Part("U18", "BCR420UW6Q-7", SOT236, [("1", "EN", "VIN_SYS"), ("2", "OUT", "BUTTON_LED_SINK"), ("3", "OUT", "BUTTON_LED_SINK"), ("4", "GND", "GND"), ("5", "OUT", "BUTTON_LED_SINK"), ("6", "REXT", None)], mpn="BCR420UW6Q-7", manufacturer="Diodes Inc."),
        Part("Q4", "2N7002KQ-13", SOT23, [("1", "G", "BUTTON_LED_GATE"), ("2", "S", "BUTTON_LED_SINK"), ("3", "D", "BUTTON_LED_K")], mpn="2N7002KQ-13", manufacturer="Diodes Inc."),
        passive("R40", "100R", "BUTTON_LED_PWM", "BUTTON_LED_GATE", R0603),
        passive("R41", "100k", "BUTTON_LED_GATE", "GND", R0603),
        passive("R65", "0R", "VIN_SYS", "BUTTON_LED_A", R0603),
        Part("U19", "AL8861QMP-13", "Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm", [("1", "ISENSE", "FL_ISENSE"), ("2", "GND", "GND"), ("3", "GND", "GND"), ("4", "VSET", "FRONTLIGHT_PWM"), ("5", "LX", "FL_LX"), ("6", "LX", "FL_LX"), ("7", "NC", None), ("8", "VIN", "VIN_SYS"), ("9", "EP", "GND")], mpn="AL8861QMP-13", manufacturer="Diodes Inc."),
        passive("R42", "100k", "FRONTLIGHT_PWM", "GND", R0603),
        passive("L4", "47uH >=0.5A", "FL_LED_K", "FL_LX", "Inductor_SMD:L_Coilcraft_XAL4020-XXX"),
        Part("D10", "SS14", "Diode_SMD:D_SMA", [("1", "K", "VIN_SYS"), ("2", "A", "FL_LX")], note="AL8861 freewheel diode; KiCad diode pad 1 is K"),
        passive("R43", "2.0R 1% 0.25W", "VIN_SYS", "FL_ISENSE", "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"),
        connector("J8", "FH12-6S-0.5SH(55) FRONTLIGHT", "Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal", ["FL_LED_A", "FL_LED_A", None, None, "FL_LED_K", "FL_LED_K"], mpn="FH12-6S-0.5SH(55)", manufacturer="Hirose", note="PROVISIONAL pin/contact orientation; verify display"),
        passive("R44", "0R", "FL_ISENSE", "FL_LED_A", R0603),
        connector("TP20", "FRONTLIGHT_CURRENT", "TestPoint:TestPoint_Pad_D1.0mm", ["FL_ISENSE"], assembly="DNP", dnp=True),
        Part("SW3", "DIAG KMR221GLFS", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", [("1", "A", "DIAG_N"), ("2", "B", "GND")], mpn="KMR221GLFS", manufacturer="C&K"),
        passive("R45", "100k", "DIAG_GATE", "GND", R0603),
        passive("R66", "100k", "VIN_SYS", "DIAG_N", R0603),
        passive("R67", "47k", "DIAG_N", "DIAG_BASE", R0603),
        Part("Q7", "BC857BQ-13-F", SOT23, [("1", "B", "DIAG_BASE"), ("2", "E", "VIN_SYS"), ("3", "C", "DIAG_GATE")], mpn="BC857BQ-13-F", manufacturer="Diodes Inc."),
        Part("Q5", "2N7002KQ-13", SOT23, [("1", "G", "DIAG_GATE"), ("2", "S", "GND"), ("3", "D", "DIAG_CATHODE")], mpn="2N7002KQ-13", manufacturer="Diodes Inc."),
        Part("LED1", "12V RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LED12_K"), ("2", "A", "VIN_12V_PROTECTED")], mpn="LTST-C190KRKT", manufacturer="Lite-On"),
        passive("R46", "12k", "LED12_K", "LED12_ISO", R0603),
        Part("D11", "BAS116,215", SOT23, [("1", "A", "LED12_ISO"), ("2", "NC", None), ("3", "K", "DIAG_CATHODE")], mpn="BAS116,215", manufacturer="Nexperia"),
        Part("LED2", "USB RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LEDUSB_K"), ("2", "A", "USB_PROTECTED")], mpn="LTST-C190KRKT", manufacturer="Lite-On"),
        passive("R47", "3.3k", "LEDUSB_K", "LEDUSB_ISO", R0603),
        Part("D12", "BAS116,215", SOT23, [("1", "A", "LEDUSB_ISO"), ("2", "NC", None), ("3", "K", "DIAG_CATHODE")], mpn="BAS116,215", manufacturer="Nexperia"),
        Part("LED3", "3V3 RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LED3V3_K"), ("2", "A", "3V3_CORE")], mpn="LTST-C190KRKT", manufacturer="Lite-On"),
        passive("R48", "1.2k", "LED3V3_K", "LED3V3_ISO", R0603),
        Part("D13", "BAS116,215", SOT23, [("1", "A", "LED3V3_ISO"), ("2", "NC", None), ("3", "K", "DIAG_CATHODE")], mpn="BAS116,215", manufacturer="Nexperia"),
        Part("LED4", "HEAT RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LEDHEAT_K"), ("2", "A", "AUTOTERM_5V")], mpn="LTST-C190KRKT", manufacturer="Lite-On"),
        passive("R49", "3.3k", "LEDHEAT_K", "LEDHEAT_ISO", R0603),
        Part("D14", "BAS116,215", SOT23, [("1", "A", "LEDHEAT_ISO"), ("2", "NC", None), ("3", "K", "DIAG_CATHODE")], mpn="BAS116,215", manufacturer="Nexperia"),
        Part("LED5", "RUN RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LEDRUN_K"), ("2", "A", "3V3_CORE")], mpn="LTST-C190KRKT", manufacturer="Lite-On"),
        passive("R50", "1.2k", "LEDRUN_K", "RUN_DRAIN", R0603),
        Part("Q6", "2N7002KQ-13", SOT23, [("1", "G", "DIAG_RUN"), ("2", "S", "RUN_ISO"), ("3", "D", "RUN_DRAIN")], mpn="2N7002KQ-13", manufacturer="Diodes Inc."),
        Part("D15", "BAS116,215", SOT23, [("1", "A", "RUN_ISO"), ("2", "NC", None), ("3", "K", "DIAG_CATHODE")], mpn="BAS116,215", manufacturer="Nexperia"),
        passive("R51", "100k", "DIAG_RUN", "GND", R0603),
        passive("R52", "2.7k DNP", "STATUS_LED_1", "STATUS1_A", R0603, assembly="DNP", dnp=True),
        Part("LED6", "STATUS1 RED OPTIONAL", "LED_SMD:LED_0603_1608Metric", [("1", "K", "GND"), ("2", "A", "STATUS1_A")], mpn="LTST-C190KRKT", manufacturer="Lite-On", assembly="DNP", dnp=True),
        passive("R53", "2.7k DNP", "STATUS_LED_2", "STATUS2_A", R0603, assembly="DNP", dnp=True),
        Part("LED7", "STATUS2 RED OPTIONAL", "LED_SMD:LED_0603_1608Metric", [("1", "K", "GND"), ("2", "A", "STATUS2_A")], mpn="LTST-C190KRKT", manufacturer="Lite-On", assembly="DNP", dnp=True),
        connector("TP21", "DIAG", "TestPoint:TestPoint_Pad_D1.0mm", ["DIAG_N"], assembly="DNP", dnp=True),
        connector("TP22", "DIAG_GND", "TestPoint:TestPoint_Pad_D1.0mm", ["GND"], assembly="DNP", dnp=True),
    ]

    return [
        ("Power input, USB-C and 3.3 V", "01_Power_Input_USB.kicad_sch", power, ["12 V protected input", "USB-C sink and reverse blocking", "3.3 V automotive buck"]),
        ("ESP32-S3, native USB, reset and boot", "02_ESP32_USB_Reset.kicad_sch", esp, ["N16R8 octal-PSRAM pins reserved", "Native USB GPIO19/20", "Manual BOOT and RESET"]),
        ("E-paper power and interface", "03_Display_EPaper.kicad_sch", display, ["Write-only SPI", "Power-off isolation", "FPC orientation remains a physical sample gate"]),
        ("Touch always-on rail and RTC", "04_Touch_RTC.kicad_sch", touch_rtc, ["Touch can wake in comfort standby", "Wake-latch option DNP pending pulse measurement", "BR1225 is non-rechargeable"]),
        ("AUTOTERM UART and 1-Wire", "05_AUTOTERM_1Wire.kicad_sch", external, ["Heater-side 5 V powers level shifter B side", "Three parallel DS18B20 on one 2-5 m trunk"]),
        ("External controls, lighting and diagnostics", "06_Controls_Diagnostics.kicad_sch", controls, ["3 m external pushbutton cable", "PWM white ring and frontlight", "Energy-flow LEDs only while DIAG is pressed"]),
    ]


def pin_positions(pins: list[tuple[str, str, str | None]]) -> tuple[float, list[tuple[float, float, int]]]:
    left_count = (len(pins) + 1) // 2
    rows = max(left_count, len(pins) - left_count)
    height = max(10.16, (rows - 1) * 2.54 + 5.08)
    positions: list[tuple[float, float, int]] = []
    for index in range(len(pins)):
        if index < left_count:
            row = index
            positions.append((-10.16, (rows - 1) * 1.27 - row * 2.54, 0))
        else:
            row = index - left_count
            positions.append((10.16, (rows - 1) * 1.27 - row * 2.54, 180))
    return height, positions


def lib_symbol(name: str, pins: list[tuple[str, str, str | None]], embedded: bool) -> str:
    height, positions = pin_positions(pins)
    shown_name = f"LandyHeater:{name}" if embedded else name
    lines = [f"    (symbol {q(shown_name)} (pin_names (offset 1.0)) (in_bom yes) (on_board yes)",
             '      (property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27))))',
             f'      (property "Value" {q(name)} (at 0 0 0) (effects (font (size 1.27 1.27))))',
             '      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
             '      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
             '      (property "Description" "Project-controlled symbol; verify pinout against cited manufacturer document" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
             f'      (symbol {q(name + "_0_1")}',
             f'        (rectangle (start -7.62 {-height/2:.3f}) (end 7.62 {height/2:.3f}) (stroke (width 0.254) (type default)) (fill (type background)))',
             "      )",
             f'      (symbol {q(name + "_1_1")}']
    for (number, pin_name, _), (x, y, angle) in zip(pins, positions):
        lines += [f"        (pin passive line (at {x:.2f} {y:.2f} {angle}) (length 2.54)",
                  f"          (name {q(pin_name)} (effects (font (size 1.0 1.0))))",
                  f"          (number {q(number)} (effects (font (size 1.0 1.0))))",
                  "        )"]
    lines += ["      )", "    )"]
    return "\n".join(lines)


def part_instance(part: Part, page_file: str, sheet_id: str) -> tuple[str, list[str], str]:
    height, positions = pin_positions(part.pins)
    u = uid(page_file, part.ref)
    x, y = part.x, part.y
    prop_values = [
        ("Reference", part.ref), ("Value", part.value), ("Footprint", part.footprint),
        ("Datasheet", part.datasheet), ("Manufacturer", part.manufacturer), ("MPN", part.mpn),
        ("Assembly", part.assembly), ("Notes", part.note),
    ]
    lines = [f"  (symbol (lib_id {q('LandyHeater:' + part.key)}) (at {x:.2f} {y:.2f} 0) (unit 1)",
             "    (exclude_from_sim no) (in_bom yes) (on_board yes)",
             f"    (dnp {'yes' if part.dnp else 'no'})",
             f"    (uuid {u})"]
    for idx, (name, value) in enumerate(prop_values):
        hide = " hide" if idx >= 2 else ""
        px = x
        py = y - height / 2 - 3.5 + idx * 1.5 if idx < 2 else y
        lines.append(f"    (property {q(name)} {q(value)} (id {idx}) (at {px:.2f} {py:.2f} 0) (effects (font (size 1.0 1.0)){hide}))")
    label_lines: list[str] = []
    for (number, _pin_name, net), (px, py, angle) in zip(part.pins, positions):
        pu = uid(page_file, part.ref, "pin", number)
        lines.append(f'    (pin {q(number)} (uuid {pu}))')
        ax = x + px
        ay = y - py
        if net is None:
            label_lines.append(f"  (no_connect (at {ax:.2f} {ay:.2f}) (uuid {uid(page_file, part.ref, 'nc', number)}))")
        else:
            label_angle = 180 if angle == 0 else 0
            label_lines += [f"  (global_label {q(net)} (shape passive) (at {ax:.2f} {ay:.2f} {label_angle}) (fields_autoplaced)",
                            "    (effects (font (size 0.8 0.8)) (justify left))",
                            f"    (uuid {uid(page_file, part.ref, 'label', number)})",
                            "  )"]
    lines += ["    (instances", '      (project "LandyHeater-Board"',
              f'        (path "/{uid("root")}/{sheet_id}" (reference {q(part.ref)}) (unit 1))',
              "      )", "    )", "  )"]
    instance = f'    (path "/{sheet_id}/{u}" (reference {q(part.ref)}) (unit 1) (value {q(part.value)}) (footprint {q(part.footprint)}))'
    return "\n".join(lines), label_lines, instance


def place(parts: list[Part]) -> None:
    # Six columns on A2 landscape.  Keeping every anchor on KiCad's 50 mil
    # grid prevents ambiguous label/pin joins and leaves room for dense pages.
    grid = 1.27
    columns = [36 * grid, 108 * grid, 180 * grid, 252 * grid, 324 * grid, 396 * grid]
    row_y = 36 * grid
    col = 0
    row_height = 0.0
    for part in parts:
        height, _ = pin_positions(part.pins)
        needed = max(22.0, height + 12.0)
        if col >= len(columns):
            row_y += row_height
            col = 0
            row_height = 0.0
        part.x = columns[col]
        part.y = round((row_y + needed / 2) / grid) * grid
        row_height = max(row_height, needed)
        col += 1


def child_schematic(title: str, filename: str, parts: list[Part], notes: list[str], page_number: int) -> str:
    place(parts)
    sheet_id = uid("sheet", filename)
    defs: dict[str, Part] = {}
    for part in parts:
        defs.setdefault(part.key, part)
    content = ["(kicad_sch (version 20250114) (generator eeschema)",
               f"  (uuid {uid(filename, 'root')})", '  (paper "A2")',
               "  (title_block", f"    (title {q(title)})", '    (date "2026-09-06")', '    (rev "A / Phase 2")',
               '    (company "LandyHeater")', '    (comment 1 "Review schematic - NOT RELEASED FOR PRODUCTION")',
               f"    (comment 2 {q(' | '.join(notes))})", "  )", "  (lib_symbols"]
    for key, exemplar in sorted(defs.items()):
        content.append(lib_symbol(key, exemplar.pins, embedded=True))
    content.append("  )")
    labels: list[str] = []
    instances: list[str] = []
    for part in parts:
        sexpr, these_labels, instance = part_instance(part, filename, sheet_id)
        content.append(sexpr)
        labels.extend(these_labels)
        instances.append(instance)
    content.extend(labels)
    # Instance data lives inside every symbol in current KiCad.  Sub-sheets do
    # not carry a root-sheet or legacy symbol_instances section.
    content += [")", ""]
    return "\n".join(content)


def root_schematic(page_defs: list[tuple[str, str, list[Part], list[str]]]) -> str:
    root_uuid = uid("root")
    lines = ["(kicad_sch (version 20250114) (generator eeschema)", f"  (uuid {root_uuid})", '  (paper "A4")',
             "  (title_block", '    (title "Landy Heater Controller - Hierarchy")', '    (date "2026-09-06")',
             '    (rev "A / Phase 2")', '    (company "LandyHeater")',
             '    (comment 1 "Review schematic - NOT RELEASED FOR PRODUCTION")',
             '    (comment 2 "ESP32-S3-WROOM-1U-N16R8 / 10-14V vehicle auxiliary battery / USB-C")', "  )",
             "  (lib_symbols)"]
    sheet_ids: list[str] = []
    for index, (title, filename, _parts, _notes) in enumerate(page_defs):
        sx = 25.4 if index % 2 == 0 else 120.65
        sy = 35.56 + (index // 2) * 50.8
        su = uid("sheet", filename)
        sheet_ids.append(su)
        lines += [f"  (sheet (at {sx:.2f} {sy:.2f}) (size 76.20 30.48) (fields_autoplaced)",
                  "    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
                  "    (stroke (width 0) (type solid) (color 0 0 0 0))", "    (fill (color 0 0 0 0.0000))",
                  f"    (uuid {su})", f"    (property \"Sheet name\" {q(title)} (id 0) (at {sx:.2f} {sy-0.84:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))",
                  f"    (property \"Sheet file\" {q(filename)} (id 1) (at {sx:.2f} {sy+31.32:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))",
                  "    (instances", '      (project "LandyHeater-Board"',
                  f'        (path "/{root_uuid}" (page {q(str(index + 2))}))',
                  "      )", "    )", "  )"]
    lines += ["  (sheet_instances", '    (path "/" (page "1"))', "  )", ")", ""]
    return "\n".join(lines)


def symbol_library(all_pages: list[tuple[str, str, list[Part], list[str]]]) -> str:
    defs: dict[str, Part] = {}
    for _title, _filename, parts, _notes in all_pages:
        for part in parts:
            defs.setdefault(part.key, part)
    lines = ["(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)"]
    for key, exemplar in sorted(defs.items()):
        lines.append(lib_symbol(key, exemplar.pins, embedded=False))
    lines += [")", ""]
    return "\n".join(lines)


def validate_definition(page_defs: list[tuple[str, str, list[Part], list[str]]]) -> None:
    all_parts = [part for _title, _filename, parts, _notes in page_defs for part in parts]
    refs = [part.ref for part in all_parts]
    duplicates = sorted({ref for ref in refs if refs.count(ref) > 1})
    if duplicates:
        raise ValueError(f"Duplicate references: {duplicates}")
    for part in all_parts:
        if not part.footprint:
            raise ValueError(f"Missing footprint: {part.ref}")
        numbers = [number for number, _name, _net in part.pins]
        if len(numbers) != len(set(numbers)):
            raise ValueError(f"Duplicate symbol pin numbers on {part.ref}: {numbers}")

    by_ref = {part.ref: part for part in all_parts}
    expected_esp = {
        "4": "1WIRE_DQ", "5": "I2C_SDA", "6": "I2C_SCL", "7": "TOUCH_RESET_RELEASE",
        "8": "SENSOR_EN", "9": "AUTOTERM_TX_3V3", "10": "AUTOTERM_RX_3V3", "11": "LATCH_CLR_GPIO_N",
        "12": "EPD_BUSY_GPIO", "13": "USB_D_N_ESP", "14": "USB_D_P_ESP",
        "17": "EPD_SCLK_GPIO", "18": "EPD_SDIO_GPIO", "19": "EPD_CS_GPIO_N",
        "20": "EPD_DC_GPIO", "21": "EPD_RESET_GPIO_N", "22": "DISPLAY_EN",
        "23": "FRONTLIGHT_PWM", "24": "AUTOTERM_OE", "27": "BOOT_N",
        "31": "BUTTON_LED_PWM", "32": "DIAG_RUN", "33": "USB_HIGH_CURRENT_N",
        "34": "STATUS_LED_1", "35": "STATUS_LED_2", "38": "TOUCH_INT_N", "39": "BUTTON_N",
    }
    actual_esp = {number: net for number, _name, net in by_ref["U5"].pins}
    for pad, net in expected_esp.items():
        if actual_esp.get(pad) != net:
            raise ValueError(f"ESP32 pad {pad}: expected {net}, found {actual_esp.get(pad)}")

    expected_epd = [None, "EPD_GDR", "EPD_RESE", None, "EPD_VSH2", None, None, "GND",
                    "EPD_BUSY_PANEL", "EPD_RESET_PANEL_N", "EPD_DC_PANEL", "EPD_CS_PANEL_N",
                    "EPD_SCLK_PANEL", "EPD_SDIO_PANEL", "3V3_DISPLAY_SW", "3V3_DISPLAY_SW",
                    "GND", "EPD_VDD", None, "EPD_VSH1", "EPD_PREVGH", "EPD_VSL", "EPD_PREVGL", "EPD_VCOM"]
    if [net for _number, _name, net in by_ref["J6"].pins] != expected_epd:
        raise ValueError("J6 E-paper pinout no longer matches GDEY029T94-FT01 Rev. 1.0")
    if [net for _number, _name, net in by_ref["J7"].pins] != ["GND", "TOUCH_INT_PANEL_N", "TOUCH_RESET_N", "3V0_TOUCH_AON", "I2C_SCL", "I2C_SDA"]:
        raise ValueError("J7 touch pinout mismatch")
    if [net for _number, _name, net in by_ref["J8"].pins] != ["FL_LED_A", "FL_LED_A", None, None, "FL_LED_K", "FL_LED_K"]:
        raise ValueError("J8 frontlight pinout mismatch")

    expected_polarity = {
        "D3": {"1": "EPD_PREVGH", "2": "EPD_BOOST_SW"},
        "D4": {"1": "EPD_NEG_PUMP", "2": "EPD_PREVGL"},
        "D5": {"1": "GND", "2": "EPD_NEG_PUMP"},
        "D10": {"1": "VIN_SYS", "2": "FL_LX"},
        "LED1": {"1": "LED12_K", "2": "VIN_12V_PROTECTED"},
        "LED2": {"1": "LEDUSB_K", "2": "USB_PROTECTED"},
        "LED3": {"1": "LED3V3_K", "2": "3V3_CORE"},
        "LED4": {"1": "LEDHEAT_K", "2": "AUTOTERM_5V"},
        "LED5": {"1": "LEDRUN_K", "2": "3V3_CORE"},
        "LED6": {"1": "GND", "2": "STATUS1_A"},
        "LED7": {"1": "GND", "2": "STATUS2_A"},
    }
    for ref, expected in expected_polarity.items():
        actual = {number: net for number, _name, net in by_ref[ref].pins}
        if actual != expected:
            raise ValueError(f"Polarity mismatch on {ref}: expected {expected}, found {actual}")


def main() -> None:
    page_defs = pages()
    validate_definition(page_defs)
    HW.mkdir(parents=True, exist_ok=True)
    SYMLIB.parent.mkdir(parents=True, exist_ok=True)
    (HW / "LandyHeater-Board.kicad_sch").write_text(root_schematic(page_defs), encoding="utf-8")
    for page_number, (title, filename, parts, notes) in enumerate(page_defs, start=2):
        (HW / filename).write_text(child_schematic(title, filename, parts, notes, page_number), encoding="utf-8")
    SYMLIB.write_text(symbol_library(page_defs), encoding="utf-8")
    print(f"Generated {1 + len(page_defs)} schematics and {SYMLIB.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
