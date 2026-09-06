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
        Part("J1", "1053131302 / 12V INPUT", "Connector_Molex:Molex_Nano-Fit_105313-xx02_1x02_P2.50mm_Horizontal", [("1", "BATT_12V_IN", "BATT_12V_IN"), ("2", "GND", "GND")], mpn="1053131302", manufacturer="Molex", assembly="THT"),
        passive("D1", "TPSMB18CA-VR", "BATT_12V_IN", "GND", "Diode_SMD:D_SMB", mpn="TPSMB18CA-VR", manufacturer="STMicroelectronics", datasheet="https://www.st.com/resource/en/datasheet/tpsmb.pdf"),
        Part("U1", "LM74720QDRRRQ1", "Package_SON:WSON-12-1EP_3x3mm_P0.5mm_EP1.5x2.5mm", [
            ("1", "GATE", "Q1_GATE"), ("2", "A", "BATT_12V_IN"), ("3", "VSNS", "BATT_12V_IN"),
            ("4", "SW", "OV_TOP"), ("5", "OV", "OV_SENSE"), ("6", "EN", "BATT_12V_IN"),
            ("7", "GND", "GND"), ("8", "PD", "Q2_GATE"), ("9", "LX", "BOOST_LX"),
            ("10", "CAP", "BOOST_CAP"), ("11", "VS", "FET_COMMON"), ("12", "C", "FET_COMMON"),
            ("13", "RTN/EP", None)], mpn="LM74720QDRRRQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/lm74720-q1.pdf", note="RTN/EP MUST FLOAT"),
        Part("Q1", "IPG20N06S4L-26", "LandyHeater:PROVISIONAL_Infineon_PG-TDSON-8-4_Dual", [
            ("1", "S1", "BATT_12V_IN"), ("2", "G1", "Q1_GATE"), ("3", "S2", "VIN_12V_PROTECTED"),
            ("4", "G2", "Q2_GATE_FET"), ("5", "D2", "FET_COMMON"), ("6", "D2", "FET_COMMON"),
            ("7", "D1", "FET_COMMON"), ("8", "D1", "FET_COMMON")], mpn="IPG20N06S4L-26", manufacturer="Infineon", datasheet="https://www.infineon.com/assets/row/public/documents/10/49/infineon-ipg20n06s4l-26-datasheet-en.pdf", note="Provisional 8-pad footprint; replace with official split-exposed-pad PG-TDSON-8-4 land pattern before layout freeze"),
        passive("L1", "100uH >175mA XPL2010-104ML", "FET_COMMON", "BOOST_LX", "Inductor_SMD:L_0805_2012Metric_Pad1.05x1.20mm_HandSolder", mpn="XPL2010-104ML", manufacturer="Coilcraft", datasheet="https://www.coilcraft.com/getmedia/56fc2271-3bce-4dc9-808a-1edf9a322f75/xpl2010.pdf", note="PROVISIONAL generic footprint; verify against Coilcraft land pattern before Phase 3"),
        passive("C1", "1uF 50V X7R", "BOOST_CAP", "FET_COMMON", C0805),
        passive("C2", "1uF 50V X7R", "FET_COMMON", "GND", C0805),
        passive("C3", "100nF 50V X7R", "BATT_12V_IN", "GND", C0603),
        passive("R1", "100k 1%", "OV_TOP", "OV_SENSE", R0603),
        passive("R2", "7.15k 1%", "OV_SENSE", "GND", R0603, note="OV cut-off nominal 18.45V"),
        passive("R3", "0R", "Q2_GATE", "Q2_GATE_FET", R0603, note="TI Figure 9-1 R5"),
        Part("D17", "BZT52H-C18-QX", "Diode_SMD:D_SOD-123F", [("1", "K", "Q2_GATE_FET"), ("2", "A", "VIN_12V_PROTECTED")], mpn="BZT52H-C18-QX", manufacturer="Nexperia", datasheet="https://assets.nexperia.com/documents/data-sheet/BZT52H-Q_SER.pdf", note="18-V Q2 VGS clamp per LM74720-Q1 Figure 9-1"),
        passive("R74", "100R", "Q2_GATE_FET", "Q2_DVDT_CAP", R0603, note="TI Figure 9-1 R4"),
        passive("C4", "10nF 50V", "Q2_DVDT_CAP", "GND", C0603, note="PD slew to GND per LM74720-Q1 Figure 9-1; validate inrush/SOA"),
        passive("FB1", "220R@100MHz 3A", "VIN_12V_PROTECTED", "VIN_SYS", "Inductor_SMD:L_0805_2012Metric_Pad1.05x1.20mm_HandSolder", mpn="MPZ2012S221A", manufacturer="TDK", datasheet="https://product.tdk.com/system/files/dam/doc/product/emc/emc/beads/catalog/beads_commercial_power_mpz2012_en.pdf"),
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
            ("5", "VBUS_DET", "USB_VBUS_DET"), ("6", "VCONN_FAULT", None), ("7", "OUT1", "USB_CURRENT_OUT1"),
            ("8", "OUT2", "USB_CURRENT_3A_N"), ("9", "ID", None), ("10", "GND", "GND"), ("11", "DIR", None), ("12", "VDD", "USB_VBUS")],
            mpn="TUSB321AIRWBR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tusb321ai.pdf"),
        passive("R4", "900k 1%", "USB_VBUS", "USB_VBUS_DET", R0603),
        passive("R5", "220k", "USB_VBUS", "USB_CURRENT_OUT1", R0603, note="TUSB321 OUT1 pull-up; referenced only to TUSB321 VDD"),
        passive("R6", "220k", "USB_VBUS", "USB_CURRENT_3A_N", R0603, note="TUSB321 OUT2 pull-up; test point is 5-V domain"),
        Part("Q8", "2N7002KQ-13 USB CURRENT ISOLATOR", SOT23, [("1", "G", "USB_CURRENT_OUT1"), ("2", "S", "GND"), ("3", "D", "USB_HIGH_CURRENT")], mpn="2N7002KQ-13", manufacturer="Diodes Inc.", datasheet="https://www.diodes.com/assets/Datasheets/2N7002KQ.pdf", note="Prevents 3V3 backfeed into unpowered TUSB321; output is active HIGH for >=1.5 A"),
        passive("R72", "1M", "USB_CURRENT_OUT1", "GND", R0603, note="Defines MOSFET gate when USB is absent"),
        passive("R73", "100k", "3V3_CORE", "USB_HIGH_CURRENT", R0603, note="MCU-side pull-up; active HIGH for >=1.5 A or 12-V-only operation"),
        passive("C7", "100nF", "USB_VBUS", "GND", C0603),
        Part("U3", "TPS259470LRPWR", "Package_DFN_QFN:LQFN-10-1EP_2x2mm_P0.5mm_EP0.7x0.7mm", [
            ("1", "EN/UVLO", "USB_VBUS"), ("2", "OVLO", "USB_OVLO"), ("3", "AUXOFF", None), ("4", "FLT", "USB_EFUSE_FAULT_N"),
            ("5", "IN", "USB_VBUS"), ("6", "OUT", "USB_PROTECTED"), ("7", "DVDT", "USB_DVDT"), ("8", "GND", "GND"),
            ("9", "ILM", "USB_ILM"), ("10", "ITIMER", None), ("11", "EP", "GND")], mpn="TPS259470LRPWR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps25947.pdf", note="PROVISIONAL generic RPW footprint; verify/replace from official TI ECAD before Phase 3"),
        passive("R7", "100k 1%", "USB_VBUS", "USB_OVLO", R0603),
        passive("R8", "26.1k 1%", "USB_OVLO", "GND", R0603, note="OVLO approx 5.95V"),
        passive("R9", "3.32k 1%", "USB_ILM", "GND", R0603, note="ILIM nominal 1.0A"),
        passive("C8", "10nF", "USB_DVDT", "GND", C0603),
        Part("NT1", "USB POWER OR NET-TIE", "NetTie:NetTie-2_SMD_Pad0.5mm", [("1", "USB_SIDE", "USB_PROTECTED"), ("2", "SYSTEM_SIDE", "VIN_SYS")], assembly="SMT", note="Logical boundary after true reverse-blocking eFuse"),
        Part("U4", "LMR43620MSC3RPERQ1", "LandyHeater:Texas_RPE0009A_VQFN-HR-9_2x2mm", [
            ("1", "MODE/SYNC", "GND"), ("2", "PGOOD", "BUCK_PGOOD"), ("3", "EN/UVLO", "VIN_SYS"),
            ("4", "VIN", "VIN_SYS"), ("5", "SW", "BUCK_SW"), ("6", "BOOT", "BUCK_BOOT"),
            ("7", "VCC", "BUCK_VCC"), ("8", "VOUT/FB", "3V3_CORE"), ("9", "GND/EP", "GND")],
            mpn="LMR43620MSC3RPERQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/lmr43620-q1.pdf", note="PROVISIONAL project-local RPE footprint; verify/replace from official TI ECAD before Phase 3"),
        passive("L2", "2.2uH 5.6A Isat", "BUCK_SW", "3V3_CORE", "Inductor_SMD:L_Coilcraft_XAL4020-XXX", mpn="XAL4020-222MEC", manufacturer="Coilcraft", datasheet="https://www.coilcraft.com/getmedia/6adcb47d-8b55-416c-976e-1e22e0d2848c/xal4000.pdf", note="TI Table 8-2 fixed 3.3V/2.2MHz; 20% tolerance"),
        passive("C9", "100nF 10V", "BUCK_BOOT", "BUCK_SW", C0603),
        passive("C10", "1uF 10V", "BUCK_VCC", "GND", C0603),
        passive("C11", "4.7uF 50V X7R 10%", "VIN_SYS", "GND", "Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder", mpn="GCJ32ER71H475KA12", manufacturer="Murata", datasheet="https://www.murata.com/en-us/products/productdetail?partno=GCJ32ER71H475KA12%23", note="LMR43620 local input capacitor; DC-bias effective capacitance must be verified"),
        passive("C12", "100nF 50V", "VIN_SYS", "GND", C0603),
        passive("C13", "22uF 10V X7R 10%", "3V3_CORE", "GND", "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder", mpn="GCJ31CR71A226KE01", manufacturer="Murata", note="Effective capacitance at 3.3V/temperature must be verified"),
        passive("C14", "22uF 10V X7R 10%", "3V3_CORE", "GND", "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder", mpn="GCJ31CR71A226KE01", manufacturer="Murata", note="Effective capacitance at 3.3V/temperature must be verified"),
        passive("R10", "100k", "3V3_CORE", "BUCK_PGOOD", R0603),
        connector("TP1", "TP_BATT_12V", "TestPoint:TestPoint_Pad_D1.5mm", ["BATT_12V_IN"], assembly="DNP", dnp=True),
        connector("TP2", "TP_USB_VBUS", "TestPoint:TestPoint_Pad_D1.5mm", ["USB_VBUS"], assembly="DNP", dnp=True),
        connector("TP3", "TP_VIN_SYS", "TestPoint:TestPoint_Pad_D1.5mm", ["VIN_SYS"], assembly="DNP", dnp=True),
        connector("TP4", "TP_3V3", "TestPoint:TestPoint_Pad_D1.5mm", ["3V3_CORE"], assembly="DNP", dnp=True),
        connector("TP5", "TP_GND", "TestPoint:TestPoint_Pad_D1.5mm", ["GND"], assembly="DNP", dnp=True),
    ]

    esp: list[Part] = [
        Part("U5", "ESP32-S3-WROOM-1U-N16R8", "RF_Module:ESP32-S3-WROOM-1U", [
            ("1", "GND", "GND"), ("2", "3V3", "3V3_CORE"), ("3", "EN", "CHIP_PU"), ("4", "IO4", "1WIRE_DQ_GPIO"),
            ("5", "IO5", "I2C_SDA"), ("6", "IO6", "I2C_SCL"), ("7", "IO7", "TOUCH_RESET_RELEASE"), ("8", "IO15", "SENSOR_EN"),
            ("9", "IO16", "AUTOTERM_TX_3V3"), ("10", "IO17", "AUTOTERM_RX_3V3"), ("11", "IO18", "LATCH_CLR_GPIO_N"), ("12", "IO8", "EPD_BUSY_GPIO"),
            ("13", "IO19/USB_D-", "USB_D_N_ESP"), ("14", "IO20/USB_D+", "USB_D_P_ESP"), ("15", "IO3", None), ("16", "IO46", None),
            ("17", "IO9", "EPD_SCLK_GPIO"), ("18", "IO10", "EPD_SDIO_GPIO"), ("19", "IO11", "EPD_CS_GPIO_N"), ("20", "IO12", "EPD_DC_GPIO"),
            ("21", "IO13", "EPD_RESET_GPIO_N"), ("22", "IO14", "DISPLAY_EN"), ("23", "IO21", "FRONTLIGHT_PWM"), ("24", "IO47", "AUTOTERM_OE"),
            ("25", "IO48", None), ("26", "IO45", None), ("27", "IO0", "BOOT_N"), ("28", "IO35/PSRAM", None),
            ("29", "IO36/PSRAM", None), ("30", "IO37/PSRAM", None), ("31", "IO38", "BUTTON_LED_PWM"), ("32", "IO39", "DIAG_RUN"),
            ("33", "IO40", "USB_HIGH_CURRENT"), ("34", "IO41", "STATUS_LED_1"), ("35", "IO42", "STATUS_LED_2"),
            ("36", "U0RXD/IO44", "U0RXD_TEST"), ("37", "U0TXD/IO43", "U0TXD_RAW"), ("38", "IO2", "TOUCH_INT_N"),
            ("39", "IO1", "BUTTON_N"), ("40", "GND", "GND"), ("41", "EPAD", "GND")],
            mpn="ESP32-S3-WROOM-1U-N16R8", manufacturer="Espressif", datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf"),
        passive("C15", "22uF 10V X7R 10%", "3V3_CORE", "GND", "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder", mpn="GCJ31CR71A226KE01", manufacturer="Murata", note="ESP32 local bulk; effective capacitance must be verified"),
        passive("C16", "22uF 10V X7R 10%", "3V3_CORE", "GND", "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder", mpn="GCJ31CR71A226KE01", manufacturer="Murata", note="ESP32 local bulk; effective capacitance must be verified"),
        passive("C17", "100nF", "3V3_CORE", "GND", C0603),
        Part("U6", "TPS3808G33QDBVRQ1", SOT236, [("1", "RESET_N", "CHIP_PU"), ("2", "GND", "GND"), ("3", "MR_N", "RESET_MR_N"), ("4", "CT", None), ("5", "SENSE", "3V3_CORE"), ("6", "VDD", "3V3_CORE")], mpn="TPS3808G33QDBVRQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps3808.pdf", note="CT intentionally open for fixed nominal 20-ms reset delay"),
        passive("R11", "10k", "3V3_CORE", "CHIP_PU", R0603),
        passive("C18", "1uF", "CHIP_PU", "GND", C0603, note="Espressif EN RC"),
        passive("C19", "100nF", "3V3_CORE", "GND", C0603),
        Part("SW1", "RESET KMR221GLFS", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", [("1", "A", "RESET_MR_N"), ("2", "B", "GND")], mpn="KMR221GLFS", manufacturer="C&K"),
        passive("R12", "10k", "3V3_CORE", "RESET_MR_N", R0603),
        Part("SW2", "BOOT KMR221GLFS", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", [("1", "A", "BOOT_N"), ("2", "B", "GND")], mpn="KMR221GLFS", manufacturer="C&K"),
        passive("R13", "10k", "3V3_CORE", "BOOT_N", R0603),
        Part("U7", "TPD2EUSB30DRTR", "Package_TO_SOT_SMD:SOT-23-5", [("1", "D1_IN", "USB_D_N_CONN"), ("2", "GND", "GND"), ("3", "D2_IN", "USB_D_P_CONN"), ("4", "D2_OUT", "USB_D_P_PROT"), ("5", "D1_OUT", "USB_D_N_PROT")], mpn="TPD2EUSB30DRTR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf"),
        passive("R14", "22R", "USB_D_N_PROT", "USB_D_N_ESP", R0603),
        passive("R15", "22R", "USB_D_P_PROT", "USB_D_P_ESP", R0603),
        passive("C40", "10pF C0G DNP", "USB_D_N_ESP", "GND", C0603, assembly="DNP", dnp=True, note="USB SI tuning only; default DNP"),
        passive("C41", "10pF C0G DNP", "USB_D_P_ESP", "GND", C0603, assembly="DNP", dnp=True, note="USB SI tuning only; default DNP"),
        passive("R16", "499R", "U0TXD_RAW", "U0TXD_TEST", R0603),
        passive("R54", "33R", "EPD_SCLK_GPIO", "EPD_SCLK", R0603),
        passive("R55", "33R", "EPD_SDIO_GPIO", "EPD_SDIO_MOSI", R0603),
        passive("R56", "33R", "EPD_CS_GPIO_N", "EPD_CS_N", R0603),
        passive("R57", "33R", "EPD_DC_GPIO", "EPD_DC", R0603),
        passive("R58", "33R", "EPD_RESET_GPIO_N", "EPD_RESET_N", R0603),
        passive("R59", "33R", "EPD_BUSY", "EPD_BUSY_GPIO", R0603),
        passive("C42", "10pF C0G DNP", "EPD_SCLK", "GND", C0603, assembly="DNP", dnp=True, note="SPI edge-rate tuning; default DNP"),
        passive("C43", "10pF C0G DNP", "EPD_SDIO_MOSI", "GND", C0603, assembly="DNP", dnp=True),
        passive("C44", "10pF C0G DNP", "EPD_CS_N", "GND", C0603, assembly="DNP", dnp=True),
        passive("C45", "10pF C0G DNP", "EPD_DC", "GND", C0603, assembly="DNP", dnp=True),
        passive("C46", "10pF C0G DNP", "EPD_RESET_N", "GND", C0603, assembly="DNP", dnp=True),
        connector("TP6", "U0TXD", "TestPoint:TestPoint_Pad_D1.0mm", ["U0TXD_TEST"], assembly="DNP", dnp=True),
        connector("TP7", "U0RXD", "TestPoint:TestPoint_Pad_D1.0mm", ["U0RXD_TEST"], assembly="DNP", dnp=True),
        connector("TP8", "USB_EFUSE_FAULT", "TestPoint:TestPoint_Pad_D1.0mm", ["USB_EFUSE_FAULT_N"], assembly="DNP", dnp=True),
        connector("TP9", "USB_CURRENT_3A", "TestPoint:TestPoint_Pad_D1.0mm", ["USB_CURRENT_3A_N"], assembly="DNP", dnp=True),
        connector("TP23", "CHIP_PU", "TestPoint:TestPoint_Pad_D1.0mm", ["CHIP_PU"], assembly="DNP", dnp=True),
        connector("TP24", "BOOT_N", "TestPoint:TestPoint_Pad_D1.0mm", ["BOOT_N"], assembly="DNP", dnp=True),
    ]

    display: list[Part] = [
        Part("U8", "TPS22919QDCKRQ1", SC706, [("1", "IN", "3V3_CORE"), ("2", "GND", "GND"), ("3", "ON", "DISPLAY_EN"), ("4", "NC", None), ("5", "QOD", "3V3_DISPLAY_SW"), ("6", "VOUT", "3V3_DISPLAY_SW")], mpn="TPS22919QDCKRQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps22919.pdf"),
        passive("R17", "100k", "DISPLAY_EN", "GND", R0603),
        passive("C20", "1uF", "3V3_CORE", "GND", C0603),
        passive("C21", "4.7uF 25V", "3V3_DISPLAY_SW", "GND", C0805, note="Good Display C4 input bypass"),
        passive("C47", "100nF", "3V3_CORE", "GND", C0603, note="U9 VCCA local bypass"),
        passive("C48", "100nF", "3V3_DISPLAY_SW", "GND", C0603, note="U9 VCCB local bypass"),
        passive("C53", "100nF", "3V3_DISPLAY_SW", "GND", C0603, note="U9 second VCCB-pin local bypass"),
        Part("U9", "SN74AXC8T245PWR", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", [
            ("1", "VCCA", "3V3_CORE"), ("2", "DIR1", "3V3_CORE"), ("3", "A1", "EPD_SCLK"), ("4", "A2", "EPD_SDIO_MOSI"),
            ("5", "A3", "EPD_CS_N"), ("6", "A4", "EPD_DC"), ("7", "A5", "EPD_RESET_N"), ("8", "A6", "GND"), ("9", "A7", "GND"), ("10", "A8", "GND"),
            ("11", "DIR2", "3V3_CORE"), ("12", "GND", "GND"), ("13", "GND", "GND"), ("14", "B8", None), ("15", "B7", None), ("16", "B6", None),
            ("17", "B5", "EPD_RESET_PANEL_N"), ("18", "B4", "EPD_DC_PANEL"), ("19", "B3", "EPD_CS_PANEL_N"), ("20", "B2", "EPD_SDIO_PANEL"),
            ("21", "B1", "EPD_SCLK_PANEL"), ("22", "OE_N", "EPD_LEVEL_OE_N"), ("23", "VCCB", "3V3_DISPLAY_SW"), ("24", "VCCB", "3V3_DISPLAY_SW")], mpn="SN74AXC8T245PWR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf"),
        passive("R18", "100k", "3V3_CORE", "EPD_LEVEL_OE_N", R0603),
        Part("Q2", "2N7002KQ-13", SOT23, [("1", "G", "DISPLAY_EN"), ("2", "S", "GND"), ("3", "D", "EPD_LEVEL_OE_N")], mpn="2N7002KQ-13", manufacturer="Diodes Inc."),
        Part("U10", "SN74AXC1T45DCKR", SC706, [("1", "VCCA", "3V3_CORE"), ("2", "GND", "GND"), ("3", "A", "EPD_BUSY"), ("4", "B", "EPD_BUSY_PANEL"), ("5", "DIR", "GND"), ("6", "VCCB", "3V3_DISPLAY_SW")], mpn="SN74AXC1T45DCKR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf"),
        passive("C49", "100nF", "3V3_CORE", "GND", C0603, note="U10 VCCA local bypass"),
        passive("C50", "100nF", "3V3_DISPLAY_SW", "GND", C0603, note="U10 VCCB local bypass"),
        passive("R19", "100k", "EPD_BUSY", "GND", R0603),
        connector("J6", "FH12-24S-0.5SH(55) E-PAPER", "Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal", [None, "EPD_GDR", "EPD_RESE", None, "EPD_VSH2", None, None, "GND", "EPD_BUSY_PANEL", "EPD_RESET_PANEL_N", "EPD_DC_PANEL", "EPD_CS_PANEL_N", "EPD_SCLK_PANEL", "EPD_SDIO_PANEL", "3V3_DISPLAY_SW", "3V3_DISPLAY_SW", "GND", "EPD_VDD", None, "EPD_VSH1", "EPD_PREVGH", "EPD_VSL", "EPD_PREVGL", "EPD_VCOM"], mpn="FH12-24S-0.5SH(55)", manufacturer="Hirose", note="PROVISIONAL bottom-contact; verify original display"),
        passive("R20", "1M 1%", "EPD_GDR", "GND", R0603, note="Good Display chapter 12"),
        passive("R21", "2.2R 1%", "EPD_RESE", "GND", R0603, note="Good Display chapter 12"),
        passive("C22", "1uF 25V", "EPD_VSH2", "GND", C0805),
        passive("C23", "1uF 25V", "3V3_DISPLAY_SW", "GND", C0805),
        passive("C24", "1uF 25V", "EPD_VDD", "GND", C0805),
        passive("C25", "1uF 25V", "EPD_VSH1", "GND", C0805),
        Part("Q3", "SI1308EDL-T1-GE3", "Package_TO_SOT_SMD:SOT-323_SC-70", [("1", "G", "EPD_GDR"), ("2", "S", "EPD_RESE"), ("3", "D", "EPD_BOOST_SW")], mpn="SI1308EDL-T1-GE3", manufacturer="Vishay"),
        passive("L3", "47uH 570mA", "3V3_DISPLAY_SW", "EPD_BOOST_SW", "LandyHeater:PROVISIONAL_Murata_LQH3NPZ_JR", mpn="LQH3NPZ470MJR", manufacturer="Murata", datasheet="https://www.murata.com/en-us/products/productdetail?partno=LQH3NPZ470MJR%23", note="Good Display chapter 12; footprint is provisional pending official ECAD/land-pattern verification"),
        Part("D3", "MBR0530T1G", SOD123, [("1", "K", "EPD_PREVGH"), ("2", "A", "EPD_BOOST_SW")], mpn="MBR0530T1G", manufacturer="onsemi", note="Good Display D3; KiCad diode pad 1 is K"),
        Part("D4", "MBR0530T1G", SOD123, [("1", "K", "EPD_NEG_PUMP"), ("2", "A", "EPD_PREVGL")], mpn="MBR0530T1G", manufacturer="onsemi", note="Good Display D1; KiCad diode pad 1 is K"),
        Part("D5", "MBR0530T1G", SOD123, [("1", "K", "GND"), ("2", "A", "EPD_NEG_PUMP")], mpn="MBR0530T1G", manufacturer="onsemi", note="Good Display D2; KiCad diode pad 1 is K"),
        passive("C26", "4.7uF 25V", "EPD_BOOST_SW", "EPD_NEG_PUMP", C0805),
        passive("C27", "1uF 25V", "EPD_PREVGH", "GND", C0805),
        passive("C36", "1uF 25V", "EPD_PREVGH", "EPD_VSL", C0805),
        passive("C37", "1uF 25V", "EPD_PREVGL", "GND", C0805, note="Good Display C11; VGL/PREVGL to GND"),
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
        connector("TP34", "DISPLAY_EN", "TestPoint:TestPoint_Pad_D1.0mm", ["DISPLAY_EN"], assembly="DNP", dnp=True),
    ]

    touch_rtc: list[Part] = [
        Part("U11", "TPS7A0230PDBVR", SOT235, [("1", "IN", "3V3_CORE"), ("2", "GND", "GND"), ("3", "EN", "3V3_CORE"), ("4", "NC", None), ("5", "OUT", "3V0_TOUCH_AON")], mpn="TPS7A0230PDBVR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps7a02.pdf"),
        passive("C28", "1uF", "3V3_CORE", "GND", C0603),
        passive("C29", "1uF", "3V0_TOUCH_AON", "GND", C0603),
        passive("R24", "4.7k", "3V0_TOUCH_AON", "I2C_SDA", R0603),
        passive("R25", "4.7k", "3V0_TOUCH_AON", "I2C_SCL", R0603),
        Part("U12", "SN74LVC1G07QDBVRQ1", SOT235, [("1", "NC", None), ("2", "A", "TOUCH_RESET_RELEASE"), ("3", "GND", "GND"), ("4", "Y_OD", "TOUCH_RESET_N"), ("5", "VCC", "3V0_TOUCH_AON")], mpn="SN74LVC1G07QDBVRQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/sn74lvc1g07-q1.pdf"),
        passive("R26", "100k", "TOUCH_RESET_RELEASE", "GND", R0603),
        passive("R27", "10k", "3V0_TOUCH_AON", "TOUCH_RESET_N", R0603),
        connector("J7", "FH12-6S-0.5SH(55) TOUCH", "Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal", ["GND", "TOUCH_INT_PANEL_N", "TOUCH_RESET_N", "3V0_TOUCH_AON", "I2C_SCL", "I2C_SDA"], mpn="FH12-6S-0.5SH(55)", manufacturer="Hirose", note="PROVISIONAL pin/contact orientation; verify display"),
        passive("R28", "100R", "TOUCH_INT_PANEL_N", "TOUCH_INT_N", R0603),
        passive("R29", "10k", "3V0_TOUCH_AON", "TOUCH_INT_N", R0603),
        passive("R71", "10k DNP", "TOUCH_INT_N", "GND", R0603, assembly="DNP", dnp=True, note="Measurement-only pull-down option; never populate with R29"),
        passive("R30", "0R DNP", "TOUCH_INT_PANEL_N", "TOUCH_INT_N", R0603, assembly="DNP", dnp=True, note="Optional direct bypass of R28"),
        Part("U13", "SN74LVC1G74-Q1 WAKE LATCH OPTION", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", [("1", "CLR_N", "LATCH_CLR_N"), ("2", "D", "3V0_TOUCH_AON"), ("3", "CLK", "GND"), ("4", "PRE_N", "TOUCH_INT_PANEL_N"), ("5", "Q", None), ("6", "Q_N", "LATCH_Q_N"), ("7", "GND", "GND"), ("8", "VCC", "3V0_TOUCH_AON")], mpn="SN74LVC1G74QDCURQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/sn74lvc1g74-q1.pdf", assembly="DNP", dnp=True, note="DNP option: active-low touch INT asynchronously drives Q_N low; firmware clears after INT release"),
        passive("R31", "100k DNP", "3V0_TOUCH_AON", "LATCH_CLR_N", R0603, assembly="DNP", dnp=True),
        passive("C39", "100nF DNP", "LATCH_CLR_N", "GND", C0603, assembly="DNP", dnp=True, note="Power-on clear for optional wake latch"),
        passive("R69", "100R DNP", "LATCH_CLR_GPIO_N", "LATCH_CLR_N", R0603, assembly="DNP", dnp=True, note="Populate only with U13 latch; GPIO18 pulses low after touch INT releases"),
        passive("R70", "0R DNP", "LATCH_Q_N", "TOUCH_INT_N", R0603, assembly="DNP", dnp=True, note="Populate only with U13 latch; remove R28, R29 and R30"),
        Part("U14", "RV-3028-C7", "LandyHeater:RV-3028-C7", [("1", "CLKOUT", None), ("2", "INT_N", "RTC_INT_N"), ("3", "SCL", "I2C_SCL"), ("4", "SDA", "I2C_SDA"), ("5", "VSS", "GND"), ("6", "VBACKUP", "RTC_VBACKUP"), ("7", "VDD", "3V3_CORE"), ("8", "EVI", "GND")], mpn="RV-3028-C7-32.768kHz-1ppm-TA-QC", manufacturer="Micro Crystal", datasheet="https://www.microcrystal.com/fileadmin/Media/Products/RTC/App.Manual/RV-3028-C7_App-Manual.pdf", note="PROVISIONAL project-local footprint; verify against current Micro Crystal ECAD before Phase 3"),
        passive("C30", "100nF", "3V3_CORE", "GND", C0603),
        Part("BT1", "BR1225 HOLDER", "Battery:BatteryHolder_Keystone_500", [("1", "+", "RTC_BAT_RAW"), ("2", "-", "GND")], mpn="500", manufacturer="Keystone", assembly="THT; cell fitted after assembly", note="Panasonic BR1225 primary cell"),
        Part("D6", "BAS116,215", SOT23, [("1", "A", "RTC_BAT_RAW"), ("2", "NC", None), ("3", "K", "RTC_VBACKUP")], mpn="BAS116,215", manufacturer="Nexperia"),
        connector("TP10", "RTC_INT", "TestPoint:TestPoint_Pad_D1.0mm", ["RTC_INT_N"], assembly="DNP", dnp=True),
        connector("TP30", "I2C_SDA", "TestPoint:TestPoint_Pad_D1.0mm", ["I2C_SDA"], assembly="DNP", dnp=True),
        connector("TP31", "I2C_SCL", "TestPoint:TestPoint_Pad_D1.0mm", ["I2C_SCL"], assembly="DNP", dnp=True),
        connector("TP32", "TOUCH_INT_N", "TestPoint:TestPoint_Pad_D1.0mm", ["TOUCH_INT_N"], assembly="DNP", dnp=True),
        connector("TP33", "TOUCH_RESET_N", "TestPoint:TestPoint_Pad_D1.0mm", ["TOUCH_RESET_N"], assembly="DNP", dnp=True),
    ]

    external: list[Part] = [
        Part("J2", "1053131304 / AUTOTERM", "Connector_Molex:Molex_Nano-Fit_105313-xx04_1x04_P2.50mm_Horizontal", [("1", "AUTOTERM_5V", "AUTOTERM_5V"), ("2", "GND", "GND"), ("3", "CTRL_TX_TO_HEATER", "CTRL_TX_TO_HEATER"), ("4", "CTRL_RX_FROM_HEATER", "CTRL_RX_FROM_HEATER")], mpn="1053131304", manufacturer="Molex", assembly="THT"),
        Part("U15", "TPS22945DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5", [("1", "VOUT", "AUTOTERM_5V_PROTECTED"), ("2", "GND", "GND"), ("3", "OC_N", None), ("4", "ON", "AUTOTERM_5V"), ("5", "VIN", "AUTOTERM_5V")], mpn="TPS22945DCKR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps22945.pdf", note="100-mA current-limited protection; heater-side supply only"),
        passive("C31", "1uF", "AUTOTERM_5V", "GND", C0603),
        passive("C32", "100nF", "AUTOTERM_5V_PROTECTED", "GND", C0603),
        Part("U16", "TXU0202QDCURQ1", "Package_SO:VSSOP-8_2.3x2mm_P0.5mm", [("1", "B2", "AUTOTERM_RX_PROT"), ("2", "GND", "GND"), ("3", "VCCA", "3V3_CORE"), ("4", "A2Y", "AUTOTERM_RX_3V3"), ("5", "A1", "AUTOTERM_TX_3V3"), ("6", "OE", "AUTOTERM_OE"), ("7", "VCCB", "AUTOTERM_5V_PROTECTED"), ("8", "B1Y", "AUTOTERM_TX_PROT")], mpn="TXU0202QDCURQ1", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/txu0202-q1.pdf"),
        passive("C51", "100nF", "3V3_CORE", "GND", C0603, note="U16 VCCA local bypass"),
        passive("R32", "100k", "AUTOTERM_OE", "GND", R0603),
        passive("R33", "100R", "AUTOTERM_TX_PROT", "CTRL_TX_TO_HEATER", R0603),
        passive("R34", "100R", "CTRL_RX_FROM_HEATER", "AUTOTERM_RX_PROT", R0603),
        Part("D7", "PESD5V2S2UT-Q", SOT23, [("1", "K1", "CTRL_TX_TO_HEATER"), ("2", "K2", "CTRL_RX_FROM_HEATER"), ("3", "A", "GND")], mpn="PESD5V2S2UT-Q", manufacturer="Nexperia", datasheet="https://assets.nexperia.com/documents/data-sheet/PESD5V2S2UT-Q.pdf", note="Pins 1/2 cathodes to signals; pin 3 common anode to GND"),
        Part("J3", "1053131303 / 1-WIRE", "Connector_Molex:Molex_Nano-Fit_105313-xx03_1x03_P2.50mm_Horizontal", [("1", "3V3_SENSOR_SW", "3V3_SENSOR_SW"), ("2", "1WIRE_DQ", "1WIRE_DQ"), ("3", "GND", "GND")], mpn="1053131303", manufacturer="Molex", assembly="THT"),
        Part("U17", "TPS22945DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5", [("1", "VOUT", "3V3_SENSOR_SW"), ("2", "GND", "GND"), ("3", "OC_N", None), ("4", "ON", "SENSOR_EN"), ("5", "VIN", "3V3_CORE")], mpn="TPS22945DCKR", manufacturer="Texas Instruments", datasheet="https://www.ti.com/lit/ds/symlink/tps22945.pdf", note="OC_N intentionally unused"),
        passive("R35", "100k", "SENSOR_EN", "GND", R0603),
        passive("C33", "1uF", "3V3_CORE", "GND", C0603),
        passive("C34", "100nF", "3V3_SENSOR_SW", "GND", C0603),
        passive("R36", "4.7k", "3V3_SENSOR_SW", "1WIRE_DQ", R0603),
        passive("R37", "0R", "1WIRE_DQ_GPIO", "1WIRE_DQ", R0603, note="Required populated 0-ohm tuning link"),
        Part("D8", "PESD3V3S2UT-Q", SOT23, [("1", "K1", "1WIRE_DQ"), ("2", "K2", "3V3_SENSOR_SW"), ("3", "A", "GND")], mpn="PESD3V3S2UT-Q", manufacturer="Nexperia", datasheet="https://assets.nexperia.com/documents/data-sheet/PESD3V3S2UT.pdf", note="Pins 1/2 cathodes to protected lines; pin 3 common anode to GND"),
        connector("TP11", "AUTOTERM_5V_PROTECTED", "TestPoint:TestPoint_Pad_D1.0mm", ["AUTOTERM_5V_PROTECTED"], assembly="DNP", dnp=True),
        connector("TP12", "1WIRE_DQ", "TestPoint:TestPoint_Pad_D1.0mm", ["1WIRE_DQ"], assembly="DNP", dnp=True),
        connector("TP25", "AUTOTERM_TX_3V3", "TestPoint:TestPoint_Pad_D1.0mm", ["AUTOTERM_TX_3V3"], assembly="DNP", dnp=True),
        connector("TP26", "AUTOTERM_RX_3V3", "TestPoint:TestPoint_Pad_D1.0mm", ["AUTOTERM_RX_3V3"], assembly="DNP", dnp=True),
        connector("TP27", "CTRL_TX_TO_HEATER", "TestPoint:TestPoint_Pad_D1.0mm", ["CTRL_TX_TO_HEATER"], assembly="DNP", dnp=True),
        connector("TP28", "CTRL_RX_FROM_HEATER", "TestPoint:TestPoint_Pad_D1.0mm", ["CTRL_RX_FROM_HEATER"], assembly="DNP", dnp=True),
        connector("TP29", "3V3_SENSOR_SW", "TestPoint:TestPoint_Pad_D1.0mm", ["3V3_SENSOR_SW"], assembly="DNP", dnp=True),
    ]

    controls: list[Part] = [
        Part("J4", "1053131305 / BUTTON+LED", "Connector_Molex:Molex_Nano-Fit_105313-xx05_1x05_P2.50mm_Horizontal", [("1", "BUTTON_N", "BUTTON_N_EXT"), ("2", "GND", "GND"), ("3", "LED_CC_PLUS", "LED_CC_PLUS"), ("4", "LED_PWM_MINUS", "LED_PWM_MINUS"), ("5", "NC", None)], mpn="1053131305", manufacturer="Molex", assembly="THT", note="APEM AV970220000700 cable assembly; 3m; twist 1/2 and 3/4; pin 5 NC"),
        passive("R38", "1k", "BUTTON_N_EXT", "BUTTON_N", R0603),
        passive("R39", "10k", "3V3_CORE", "BUTTON_N", R0603),
        passive("C35", "10nF", "BUTTON_N", "GND", C0603, note="3m cable debounce/EMI; validate wake"),
        Part("D9", "PESD3V3S1BA", "Diode_SMD:D_SOD-323", [("1", "IO", "BUTTON_N_EXT"), ("2", "GND", "GND")], mpn="PESD3V3S1BA", manufacturer="Nexperia", note="Bidirectional 3.3V ESD protection for 3m button wire"),
        Part("D16", "PESD24VL1BA,115", "Diode_SMD:D_SOD-323", [("1", "IO", "LED_PWM_MINUS"), ("2", "GND", "GND")], mpn="PESD24VL1BA,115", manufacturer="Nexperia", note="Bidirectional 24V ESD protection; LED cathode may rise to VIN_SYS when off"),
        Part("U18", "BCR421UW6Q-7", SOT236, [("1", "EN", "BUTTON_LED_EN"), ("2", "OUT", "LED_PWM_MINUS"), ("3", "OUT", "LED_PWM_MINUS"), ("4", "GND", "GND"), ("5", "OUT", "LED_PWM_MINUS"), ("6", "REXT", None)], mpn="BCR421UW6Q-7", manufacturer="Diodes Inc.", datasheet="https://www.diodes.com/datasheet/download/BCR420UW6Q.pdf", note="Preset 10mA; native low-side PWM EN <25kHz"),
        passive("R40", "100R", "BUTTON_LED_PWM", "BUTTON_LED_EN", R0603),
        passive("R41", "100k", "BUTTON_LED_EN", "GND", R0603, note="Direct hardware default OFF at BCR421 EN"),
        passive("R65", "0R", "VIN_SYS", "LED_CC_PLUS", R0603),
        Part("U19", "AL8861QMP-13", "Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm", [("1", "ISENSE", "FL_ISENSE"), ("2", "GND", "GND"), ("3", "GND", "GND"), ("4", "VSET", "FRONTLIGHT_PWM"), ("5", "LX", "FL_LX"), ("6", "LX", "FL_LX"), ("7", "NC", None), ("8", "VIN", "VIN_SYS"), ("9", "EP", "GND")], mpn="AL8861QMP-13", manufacturer="Diodes Inc.", datasheet="https://www.diodes.com/datasheet/download/AL8861Q.pdf"),
        passive("C52", "10uF 100V X7R 10%", "VIN_SYS", "GND", "Capacitor_SMD:C_1210_3225Metric_Pad1.33x2.70mm_HandSolder", mpn="CGA6P1X7R2A106K250AC", manufacturer="TDK", datasheet="https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6P1X7R2A106K250AC", note="AL8861 local input capacitor; DC-bias effective capacitance must be verified"),
        passive("R42", "100k", "FRONTLIGHT_PWM", "GND", R0603),
        passive("L4", "47uH 570mA", "FL_LED_K", "FL_LX", "LandyHeater:PROVISIONAL_Murata_LQH3NPZ_JR", mpn="LQH3NPZ470MJR", manufacturer="Murata", datasheet="https://www.murata.com/en-us/products/productdetail?partno=LQH3NPZ470MJR%23", note="AL8861 33..100uH range; footprint provisional pending official ECAD/land-pattern verification"),
        Part("D10", "B140Q-13-F", "Diode_SMD:D_SMA", [("1", "K", "VIN_SYS"), ("2", "A", "FL_LX")], mpn="B140Q-13-F", manufacturer="Diodes Inc.", datasheet="https://www.diodes.com/assets/Datasheets/ds38236.pdf", note="Automotive 1-A/40-V Schottky; KiCad diode pad 1 is K"),
        passive("R43", "2.0R 1% 0.25W", "VIN_SYS", "FL_ISENSE", "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"),
        connector("J8", "FH12-6S-0.5SH(55) FRONTLIGHT", "Connector_FFC-FPC:Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal", ["FL_LED_A", "FL_LED_A", None, None, "FL_LED_K", "FL_LED_K"], mpn="FH12-6S-0.5SH(55)", manufacturer="Hirose", note="PROVISIONAL pin/contact orientation; verify display"),
        passive("R44", "0R", "FL_ISENSE", "FL_LED_A", R0603),
        connector("TP20", "FRONTLIGHT_CURRENT", "TestPoint:TestPoint_Pad_D1.0mm", ["FL_ISENSE"], assembly="DNP", dnp=True),
        Part("SW3", "DIAG KMR221GLFS", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2", [("1", "A", "DIAG_N"), ("2", "B", "GND")], mpn="KMR221GLFS", manufacturer="C&K"),
        passive("R45", "100k", "DIAG_GATE", "GND", R0603),
        passive("R75", "47k", "DIAG_GATE_DRIVE", "DIAG_GATE", R0603, note="With R45 limits Q5 VGS to <14V at maximum OV threshold"),
        passive("R66", "100k", "VIN_SYS", "DIAG_N", R0603),
        passive("R67", "47k", "DIAG_N", "DIAG_BASE", R0603),
        Part("Q7", "BC857BQ-13-F", SOT23, [("1", "B", "DIAG_BASE"), ("2", "E", "VIN_SYS"), ("3", "C", "DIAG_GATE_DRIVE")], mpn="BC857BQ-13-F", manufacturer="Diodes Inc."),
        Part("Q5", "2N7002KQ-13", SOT23, [("1", "G", "DIAG_GATE"), ("2", "S", "GND"), ("3", "D", "DIAG_CATHODE")], mpn="2N7002KQ-13", manufacturer="Diodes Inc."),
        Part("LED1", "12V RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LED12_K"), ("2", "A", "VIN_12V_PROTECTED")], mpn="LTST-C190KRKT", manufacturer="Lite-On"),
        passive("R46", "12k", "LED12_K", "LED12_ISO", R0603),
        Part("D11", "BAS116,215", SOT23, [("1", "A", "LED12_ISO"), ("2", "NC", None), ("3", "K", "DIAG_CATHODE")], mpn="BAS116,215", manufacturer="Nexperia"),
        Part("LED2", "USB RED", "LED_SMD:LED_0603_1608Metric", [("1", "K", "LEDUSB_K"), ("2", "A", "USB_VBUS")], mpn="LTST-C190KRKT", manufacturer="Lite-On", note="Raw connector VBUS: indicates actual USB presence, not common VIN_SYS"),
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
        connector("TP35", "FRONTLIGHT_PWM", "TestPoint:TestPoint_Pad_D1.0mm", ["FRONTLIGHT_PWM"], assembly="DNP", dnp=True),
        connector("TP36", "BUTTON_N", "TestPoint:TestPoint_Pad_D1.0mm", ["BUTTON_N"], assembly="DNP", dnp=True),
        connector("TP37", "BUTTON_LED_PWM", "TestPoint:TestPoint_Pad_D1.0mm", ["BUTTON_LED_PWM"], assembly="DNP", dnp=True),
        connector("TP38", "DIAG_RUN", "TestPoint:TestPoint_Pad_D1.0mm", ["DIAG_RUN"], assembly="DNP", dnp=True),
    ]

    return [
        ("Power input, USB-C and 3.3 V", "01_Power_Input_USB.kicad_sch", power, ["12 V protected input", "USB-C sink and reverse blocking", "3.3 V automotive buck"]),
        ("ESP32-S3, native USB, reset and boot", "02_ESP32_USB_Reset.kicad_sch", esp, ["N16R8 octal-PSRAM pins reserved", "Native USB GPIO19/20", "Manual BOOT and RESET"]),
        ("E-paper power and interface", "03_Display_EPaper.kicad_sch", display, ["Write-only SPI", "Power-off isolation", "FPC orientation remains a physical sample gate"]),
        ("Touch always-on rail and RTC", "04_Touch_RTC.kicad_sch", touch_rtc, ["Touch can wake in comfort standby", "Wake-latch option DNP pending pulse measurement", "BR1225 is non-rechargeable"]),
        ("AUTOTERM UART and 1-Wire", "05_AUTOTERM_1Wire.kicad_sch", external, ["Heater-side 5 V powers level shifter B side", "Three parallel DS18B20 on one 2-5 m trunk"]),
        ("External controls, lighting and diagnostics", "06_Controls_Diagnostics.kicad_sch", controls, ["3 m external pushbutton cable", "PWM white ring and frontlight", "Energy-flow LEDs only while DIAG is pressed"]),
    ]


OUTPUT_PIN_NAMES = {
    "GATE", "PD", "LX", "CAP", "PGOOD", "FLT", "AUXOFF", "OUT1", "OUT2",
    "VOUT", "RESET_N", "A2Y", "B1Y", "Y_OD", "Q", "Q_N", "INT_N",
}


PIN_SIDE_OVERRIDES: dict[str, dict[str, str]] = {
    "U1": {"1": "right", "8": "right", "9": "right", "10": "right", "11": "right", "12": "right"},
    "U2": {"7": "right", "8": "right"},
    "U3": {"3": "right", "4": "right", "6": "right", "7": "right", "9": "right", "10": "right"},
    "U4": {"2": "right", "5": "right", "6": "right", "7": "right", "8": "right"},
    "U5": {str(n): ("left" if n <= 16 else "right") for n in range(1, 42)},
    "U6": {"1": "right"},
    "U7": {"4": "right", "5": "right"},
    "U8": {"5": "right", "6": "right"},
    "U9": {str(n): ("left" if n <= 13 or n in {22, 23, 24} else "right") for n in range(1, 25)},
    "U10": {"3": "left", "4": "right"},
    "U11": {"5": "right"},
    "U12": {"4": "right"},
    "U13": {"4": "right", "6": "left"},
    "U14": {"2": "right"},
    "U15": {"1": "right"},
    "U16": {"1": "right", "4": "left", "5": "left", "8": "right"},
    "U17": {"1": "right"},
    "U18": {"2": "right", "3": "right", "5": "right"},
    "U19": {"5": "right", "6": "right"},
}


def symbol_style(part: Part) -> str:
    if part.ref.startswith("TP"):
        return "testpoint"
    if part.ref.startswith("LED"):
        return "led"
    if part.ref.startswith("SW"):
        return "switch"
    if part.ref.startswith("R") and len(part.pins) == 2:
        return "resistor"
    if part.ref.startswith("C") and len(part.pins) == 2:
        return "capacitor"
    if (part.ref.startswith("L") or part.ref.startswith("FB")) and len(part.pins) == 2:
        return "inductor"
    if part.ref.startswith("D") and len(part.pins) == 2:
        return "diode"
    if part.ref.startswith("Q") and len(part.pins) == 3:
        return "transistor"
    if part.ref.startswith("J"):
        return "connector"
    if part.ref.startswith("BT"):
        return "battery"
    if part.ref.startswith("NT"):
        return "nettie"
    return "ic"


def pin_etype(part: Part, pin_name: str) -> str:
    style = symbol_style(part)
    if style in {"resistor", "capacitor", "inductor", "diode", "led", "switch", "connector", "battery", "nettie", "testpoint", "transistor"}:
        return "passive"
    if part.ref == "U5":
        return "input" if pin_name == "EN" else "bidirectional"
    if part.ref == "U9":
        if pin_name.startswith("A") and pin_name[1:].isdigit():
            return "input"
        if pin_name.startswith("B") and pin_name[1:].isdigit():
            return "tri_state"
    if part.ref == "U10":
        return "input" if pin_name == "B" else ("output" if pin_name == "A" else "passive")
    if part.ref == "U16":
        return "input" if pin_name in {"A1", "B2", "OE"} else ("output" if pin_name in {"A2Y", "B1Y"} else "passive")
    # Parallel power/output pads are one electrical terminal in the package;
    # modelling each pad as a separate output creates a false output/output ERC.
    if part.ref == "U18" and pin_name == "OUT":
        return "passive"
    if part.ref == "U19" and pin_name == "LX":
        return "passive"
    if pin_name in {"SDA", "SCL"}:
        return "bidirectional"
    if pin_name in {"OUT1", "OUT2", "FLT", "AUXOFF", "PGOOD", "INT_N", "OC_N", "Y_OD", "RESET_N"}:
        return "open_collector"
    if pin_name in OUTPUT_PIN_NAMES or pin_name.startswith("OUT"):
        return "output"
    if pin_name in {"A", "B", "A1", "A2", "B1", "B2", "EN", "ON", "OE", "OE_N", "DIR", "DIR1", "DIR2", "OV", "OVLO", "SENSE", "MR_N", "VSET", "ISENSE", "CURRENT_MODE", "PORT", "VBUS_DET"}:
        return "input"
    return "passive"


def pin_positions(part: Part) -> tuple[float, float, list[tuple[float, float, int]]]:
    style = symbol_style(part)
    if style in {"resistor", "capacitor", "inductor", "diode", "led", "switch", "battery", "nettie"}:
        return 5.08, 5.08, [(-2.54, 0.0, 0), (2.54, 0.0, 180)]
    if style == "testpoint":
        return 5.08, 5.08, [(-2.54, 0.0, 0)]
    if style == "transistor":
        return 10.16, 10.16, [(-7.62, 0.0, 0), (7.62, 2.54, 180), (7.62, -2.54, 180)]
    if style == "connector":
        rows = len(part.pins)
        h = max(7.62, (rows - 1) * 2.54 + 5.08)
        side = "left" if part.ref in {"J6", "J7", "J8"} else "right"
        x, angle = (-7.62, 0) if side == "left" else (7.62, 180)
        return 10.16, h, [(x, (rows - 1) * 1.27 - i * 2.54, angle) for i in range(rows)]

    sides = PIN_SIDE_OVERRIDES.get(part.ref, {})
    left: list[int] = []
    right: list[int] = []
    for i, (number, pin_name, _net) in enumerate(part.pins):
        side = sides.get(number)
        if side is None:
            side = "right" if pin_name in OUTPUT_PIN_NAMES or pin_name.startswith("OUT") else "left"
        (right if side == "right" else left).append(i)
    rows = max(len(left), len(right), 2)
    h = max(10.16, (rows - 1) * 2.54 + 5.08)
    result: list[tuple[float, float, int] | None] = [None] * len(part.pins)
    for side_indices, x, angle in ((left, -10.16, 0), (right, 10.16, 180)):
        for row, index in enumerate(side_indices):
            result[index] = (x, (len(side_indices) - 1) * 1.27 - row * 2.54, angle)
    return 15.24, h, [p for p in result if p is not None]


def shape_lines(part: Part, name: str, width: float, height: float) -> list[str]:
    style = symbol_style(part)
    stroke = "(stroke (width 0.254) (type default))"
    fill = "(fill (type none))"
    if style == "resistor":
        return [f"        (rectangle (start -1.27 -1.27) (end 1.27 1.27) {stroke} (fill (type background)))"]
    if style == "capacitor":
        return [f"        (polyline (pts (xy -0.64 -1.52) (xy -0.64 1.52)) {stroke} {fill})", f"        (polyline (pts (xy 0.64 -1.52) (xy 0.64 1.52)) {stroke} {fill})"]
    if style == "inductor":
        return [f"        (polyline (pts (xy -1.52 0) (xy -1.02 -0.76) (xy -0.51 0.76) (xy 0 -0.76) (xy 0.51 0.76) (xy 1.02 -0.76) (xy 1.52 0)) {stroke} {fill})"]
    if style in {"diode", "led"}:
        out = [f"        (polyline (pts (xy -1.27 -1.27) (xy 0.64 0) (xy -1.27 1.27) (xy -1.27 -1.27)) {stroke} {fill})", f"        (polyline (pts (xy 0.64 -1.52) (xy 0.64 1.52)) {stroke} {fill})"]
        if style == "led":
            out += [f"        (polyline (pts (xy 0.25 -1.75) (xy 1.25 -2.75)) {stroke} {fill})", f"        (polyline (pts (xy 0.75 -1.25) (xy 1.75 -2.25)) {stroke} {fill})"]
        return out
    if style == "switch":
        return [f"        (circle (center -1.27 0) (radius 0.25) {stroke} {fill})", f"        (circle (center 1.27 0) (radius 0.25) {stroke} {fill})", f"        (polyline (pts (xy -1.02 -0.25) (xy 0.89 -1.27)) {stroke} {fill})"]
    if style == "testpoint":
        return [f"        (circle (center 0 0) (radius 1.27) {stroke} {fill})"]
    if style == "transistor":
        return [f"        (rectangle (start -5.08 -5.08) (end 5.08 5.08) {stroke} (fill (type background)))", f"        (text {q('MOSFET')} (at 0 0 0) (effects (font (size 0.9 0.9))))"]
    if style == "connector":
        return [f"        (rectangle (start -5.08 {-height/2:.2f}) (end 5.08 {height/2:.2f}) {stroke} (fill (type background)))"]
    if style in {"battery", "nettie"}:
        return [f"        (rectangle (start -1.52 -1.52) (end 1.52 1.52) {stroke} (fill (type background)))"]
    return [f"        (rectangle (start {-width/2:.2f} {-height/2:.2f}) (end {width/2:.2f} {height/2:.2f}) {stroke} (fill (type background)))"]


def lib_symbol(part: Part, embedded: bool) -> str:
    width, height, positions = pin_positions(part)
    name = part.key
    shown_name = f"LandyHeater:{name}" if embedded else name
    ref_prefix = re.match(r"[A-Za-z]+", part.ref).group(0)
    lines = [f"    (symbol {q(shown_name)} (pin_names (offset 0.7)) (in_bom yes) (on_board yes)",
             f'      (property "Reference" {q(ref_prefix)} (at 0 0 0) (effects (font (size 1.0 1.0))))',
             f'      (property "Value" {q(name)} (at 0 0 0) (effects (font (size 0.9 0.9))))',
             '      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.0 1.0)) hide))',
             '      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.0 1.0)) hide))',
             '      (property "Description" "Project-controlled, manufacturer-pinout-reviewed symbol" (at 0 0 0) (effects (font (size 1.0 1.0)) hide))',
             f'      (symbol {q(name + "_0_1")}']
    lines.extend(shape_lines(part, name, width, height))
    lines += ["      )", f'      (symbol {q(name + "_1_1")}']
    for (number, pin_name, _), (x, y, angle) in zip(part.pins, positions):
        lines += [f"        (pin {pin_etype(part, pin_name)} line (at {x:.2f} {y:.2f} {angle}) (length 2.54)",
                  f"          (name {q(pin_name)} (effects (font (size 0.72 0.72))))",
                  f"          (number {q(number)} (effects (font (size 0.72 0.72))))",
                  "        )"]
    lines += ["      )", "    )"]
    return "\n".join(lines)


def endpoint(part: Part, pin_index: int) -> tuple[float, float, int]:
    _w, _h, positions = pin_positions(part)
    px, py, angle = positions[pin_index]
    return part.x + px, part.y - py, angle


def part_instance(part: Part, page_file: str, sheet_id: str) -> tuple[str, list[str], str]:
    _width, height, positions = pin_positions(part)
    u = uid(page_file, part.ref)
    x, y = part.x, part.y
    prop_values = [("Reference", part.ref), ("Value", part.value), ("Footprint", part.footprint), ("Datasheet", part.datasheet), ("Manufacturer", part.manufacturer), ("MPN", part.mpn), ("Assembly", part.assembly), ("Notes", part.note)]
    lines = [f"  (symbol (lib_id {q('LandyHeater:' + part.key)}) (at {x:.2f} {y:.2f} 0) (unit 1)", "    (exclude_from_sim no) (in_bom yes) (on_board yes)", f"    (dnp {'yes' if part.dnp else 'no'})", f"    (uuid {u})"]
    for idx, (name, value) in enumerate(prop_values):
        hide = " hide" if idx >= 2 else ""
        py = y - height / 2 - 3.2 + idx * 1.5 if idx < 2 else y
        size = 0.85 if idx == 1 else 1.0
        lines.append(f"    (property {q(name)} {q(value)} (id {idx}) (at {x:.2f} {py:.2f} 0) (effects (font (size {size} {size})){hide}))")
    auxiliaries: list[str] = []
    for index, ((number, _pin_name, net), _position) in enumerate(zip(part.pins, positions)):
        lines.append(f'    (pin {q(number)} (uuid {uid(page_file, part.ref, "pin", number)}))')
        if net is None:
            ax, ay, _angle = endpoint(part, index)
            auxiliaries.append(f"  (no_connect (at {ax:.2f} {ay:.2f}) (uuid {uid(page_file, part.ref, 'nc', number)}))")
    lines += ["    (instances", '      (project "LandyHeater-Board"', f'        (path "/{uid("root")}/{sheet_id}" (reference {q(part.ref)}) (unit 1))', "      )", "    )", "  )"]
    instance = f'    (path "/{sheet_id}/{u}" (reference {q(part.ref)}) (unit 1) (value {q(part.value)}) (footprint {q(part.footprint)}))'
    return "\n".join(lines), auxiliaries, instance


LAYOUT: dict[str, dict[str, tuple[float, float]]] = {
    "01_Power_Input_USB.kicad_sch": {
        "J1": (25, 50), "D1": (50, 75), "C3": (75, 75), "U1": (90, 48), "Q1": (135, 48),
        "L1": (90, 85), "C1": (120, 85), "C2": (150, 85), "R1": (55, 105), "R2": (85, 105),
        "R3": (130, 105), "D17": (150, 80), "R74": (150, 105), "C4": (175, 105), "FB1": (190, 48), "C5": (210, 75), "C6": (240, 75),
        "TP1": (25, 100), "TP3": (250, 48),
        "J5": (30, 165), "R68": (60, 220), "D2": (85, 220), "U2": (90, 160), "R4": (60, 130),
        "R5": (125, 130), "R6": (155, 130), "Q8": (150, 160), "R72": (150, 190), "R73": (185, 160),
        "C7": (115, 220), "U3": (220, 165), "R7": (210, 130), "R8": (240, 130), "R9": (215, 205),
        "C8": (245, 205), "NT1": (285, 165), "TP2": (30, 125),
        "U4": (330, 160), "L2": (365, 160), "C9": (345, 200), "C10": (315, 210), "C11": (285, 220),
        "C12": (285, 240), "C13": (365, 200), "C14": (395, 200), "R10": (330, 235), "TP4": (395, 160), "TP5": (395, 240),
    },
    "02_ESP32_USB_Reset.kicad_sch": {
        "U5": (205, 135), "C15": (45, 45), "C16": (80, 45), "C17": (115, 45),
        "U6": (60, 95), "R11": (100, 75), "C18": (100, 95), "C19": (100, 115), "SW1": (60, 125), "R12": (25, 95),
        "SW2": (60, 155), "R13": (25, 155), "U7": (75, 205), "R14": (120, 195), "R15": (120, 215),
        "C40": (155, 195), "C41": (155, 215), "R16": (285, 230),
        "R54": (300, 70), "R55": (300, 95), "R56": (300, 120), "R57": (300, 145), "R58": (300, 170), "R59": (300, 195),
        "C42": (345, 70), "C43": (345, 95), "C44": (345, 120), "C45": (345, 145), "C46": (345, 170),
        "TP6": (325, 230), "TP7": (355, 230), "TP8": (385, 230), "TP9": (385, 250), "TP23": (150, 75), "TP24": (100, 155),
    },
    "03_Display_EPaper.kicad_sch": {
        "U8": (45, 50), "R17": (45, 80), "C20": (80, 35), "C21": (80, 55), "C47": (110, 35), "C48": (110, 55), "C53": (110, 75),
        "U9": (100, 115), "R18": (55, 100), "Q2": (55, 125), "U10": (100, 185), "C49": (55, 175), "C50": (55, 195), "R19": (145, 185),
        "J6": (380, 135), "R20": (205, 65), "R21": (205, 85), "C22": (335, 45), "C23": (335, 60), "C24": (335, 75), "C25": (335, 90),
        "Q3": (240, 90), "L3": (275, 65), "D3": (310, 110), "D4": (280, 135), "D5": (310, 150), "C26": (245, 135),
        "C27": (335, 110), "C36": (335, 130), "C37": (335, 150), "C38": (335, 170),
        "R60": (220, 200), "R61": (250, 200), "R62": (280, 200), "R63": (310, 200), "R64": (340, 200),
        "TP13": (205, 230), "TP14": (235, 230), "TP15": (265, 230), "TP16": (295, 230), "TP17": (325, 230), "TP18": (355, 230), "TP19": (385, 230), "TP34": (60, 150),
    },
    "04_Touch_RTC.kicad_sch": {
        "U11": (45, 45), "C28": (80, 35), "C29": (80, 55), "R24": (120, 35), "R25": (150, 35),
        "U12": (230, 65), "R26": (190, 55), "R27": (270, 55), "J7": (375, 70),
        "R28": (305, 100), "R29": (305, 120), "R71": (335, 120), "R30": (335, 100),
        "U13": (230, 155), "R31": (185, 140), "C39": (185, 160), "R69": (185, 180), "R70": (280, 155),
        "U14": (105, 215), "C30": (55, 215), "BT1": (245, 215), "D6": (285, 215),
        "TP10": (145, 245), "TP30": (175, 245), "TP31": (205, 245), "TP32": (310, 245), "TP33": (340, 245),
    },
    "05_AUTOTERM_1Wire.kicad_sch": {
        "J2": (380, 75), "U15": (290, 45), "C31": (245, 35), "C32": (330, 35), "U16": (170, 80), "C51": (130, 45),
        "R32": (130, 110), "R33": (235, 70), "R34": (235, 95), "D7": (300, 85),
        "TP11": (330, 120), "TP25": (110, 70), "TP26": (110, 95), "TP27": (335, 70), "TP28": (335, 95),
        "J3": (380, 195), "U17": (95, 185), "R35": (55, 205), "C33": (55, 165), "C34": (135, 165),
        "R36": (190, 165), "R37": (235, 195), "D8": (300, 195), "TP12": (330, 225), "TP29": (150, 225),
    },
    "06_Controls_Diagnostics.kicad_sch": {
        "J4": (30, 60), "R38": (90, 40), "R39": (130, 30), "C35": (130, 50), "D9": (90, 65),
        "D16": (90, 95), "U18": (150, 95), "R40": (180, 120), "R41": (215, 125), "R65": (90, 110),
        "U19": (140, 155), "C52": (95, 145), "R42": (95, 170), "L4": (205, 145), "D10": (205, 170), "R43": (255, 135), "R44": (295, 135), "J8": (380, 150), "TP20": (325, 125), "TP35": (105, 190),
        "SW3": (285, 205), "R45": (325, 220), "R75": (345, 185), "R66": (245, 185), "R67": (275, 185), "Q7": (325, 185), "Q5": (365, 205),
        "LED1": (55, 205), "R46": (105, 205), "D11": (155, 205),
        "LED2": (55, 220), "R47": (105, 220), "D12": (155, 220),
        "LED3": (55, 235), "R48": (105, 235), "D13": (155, 235),
        "LED4": (55, 250), "R49": (105, 250), "D14": (155, 250),
        "LED5": (55, 265), "R50": (105, 265), "Q6": (145, 265), "D15": (190, 265), "R51": (245, 265),
        "R52": (325, 245), "LED6": (365, 245), "R53": (325, 265), "LED7": (365, 265),
        "TP21": (245, 220), "TP22": (275, 220), "TP36": (165, 40), "TP37": (245, 120), "TP38": (275, 265),
    },
}


def place(filename: str, parts: list[Part]) -> None:
    positions = LAYOUT[filename]
    missing = [part.ref for part in parts if part.ref not in positions]
    extra = sorted(set(positions) - {part.ref for part in parts})
    if missing or extra:
        raise ValueError(f"Layout map mismatch for {filename}: missing={missing}, extra={extra}")
    for part in parts:
        x, y = positions[part.ref]
        # All symbol origins and therefore all pin endpoints stay on KiCad's
        # 50-mil (1.27 mm) electrical grid.
        part.x = round(x / 1.27) * 1.27
        part.y = round(y / 1.27) * 1.27


PER_PIN_LABEL_NETS = {"GND", "3V3_CORE", "3V0_TOUCH_AON", "3V3_DISPLAY_SW", "3V3_SENSOR_SW", "VIN_SYS", "USB_VBUS"}

# These point-to-point signals leave or enter dense multi-pin symbols.  A named
# connection is clearer than a wire that would run across neighbouring pins.
PER_PIN_LABEL_NETS |= {
    "USB_D_N_CONN", "USB_D_P_CONN", "AUTOTERM_TX_3V3", "AUTOTERM_RX_3V3",
}


def wire_segment(filename: str, net: str, index: int, a: tuple[float, float], b: tuple[float, float]) -> str:
    return f"  (wire (pts (xy {a[0]:.2f} {a[1]:.2f}) (xy {b[0]:.2f} {b[1]:.2f})) (stroke (width 0) (type default)) (uuid {uid(filename, net, 'wire', index, a, b)}))"


def global_label(filename: str, net: str, index: int, point: tuple[float, float], justify: str = "left") -> str:
    justification = " (justify right)" if justify == "right" else " (justify left)"
    return "\n".join([f"  (global_label {q(net)} (shape passive) (at {point[0]:.2f} {point[1]:.2f} 0) (fields_autoplaced)", f"    (effects (font (size 0.72 0.72)){justification})", f"    (uuid {uid(filename, net, 'label', index, point)})", "  )"])


def labelled_stub(filename: str, net: str, index: int, endpoint_value: tuple[float, float, int]) -> list[str]:
    x, y, angle = endpoint_value
    # Electrical pin angles 0/180 mean that the free connection end points to
    # the left/right respectively.  Keep the label anchored to the pin (no
    # dangling wire that might intersect another net) while its text grows
    # away from the symbol body.
    return [global_label(filename, net, index, (x, y), "right" if angle == 0 else "left")]


def connect_nets(filename: str, parts: list[Part], net_pages: dict[str, set[str]]) -> list[str]:
    by_net: dict[str, list[tuple[float, float, int]]] = {}
    for part in parts:
        for index, (_number, _name, net) in enumerate(part.pins):
            if net is not None:
                by_net.setdefault(net, []).append(endpoint(part, index))
    out: list[str] = []
    for net, endpoints in sorted(by_net.items()):
        if net in PER_PIN_LABEL_NETS:
            for i, endpoint_value in enumerate(endpoints):
                out.extend(labelled_stub(filename, net, i, endpoint_value))
            continue
        points = [(x, y) for x, y, _angle in endpoints]
        crosses_pages = len(net_pages.get(net, set())) > 1
        # Only draw a wire automatically when all endpoints already form one
        # unambiguous horizontal signal path.  Earlier generic hub routing
        # created unintended T-junctions where unrelated nets crossed.  More
        # complex connections use named labels until they are hand-routed in
        # a reviewed, circuit-specific map.
        same_y = len({round(y, 2) for _, y in points}) == 1
        should_wire = len(points) >= 2 and len(points) <= 4 and same_y and not crosses_pages
        if should_wire:
            ordered = sorted(set(points))
            for wire_index, (a, b) in enumerate(zip(ordered, ordered[1:])):
                out.append(wire_segment(filename, net, wire_index, a, b))
            if len(ordered) > 2:
                for junction_index, point in enumerate(ordered[1:-1]):
                    out.append(f"  (junction (at {point[0]:.2f} {point[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid {uid(filename, net, 'junction', junction_index, point)}))")
        else:
            for i, endpoint_value in enumerate(endpoints):
                out.extend(labelled_stub(filename, net, i, endpoint_value))
    return out


def text_note(filename: str, text_value: str, x: float, y: float, size: float = 1.2) -> str:
    return "\n".join([f"  (text {q(text_value)} (exclude_from_sim no) (at {x:.2f} {y:.2f} 0)", f"    (effects (font (size {size:.2f} {size:.2f}) (thickness 0.22)) (justify left bottom))", f"    (uuid {uid(filename, 'text', text_value, x, y)})", "  )"])


PAGE_NOTES: dict[str, list[tuple[str, float, float, float]]] = {
    "01_Power_Input_USB.kicad_sch": [("12-V INPUT / REVERSE BATTERY / OV CUTOFF", 18, 22, 1.4), ("FLOW: J1 -> TVS + LM74720/Q1 -> FILTER -> VIN_SYS", 18, 28, 1.0), ("USB-C UFP / CURRENT DETECTION / TRUE REVERSE BLOCKING", 18, 120, 1.4), ("FLOW: J5 -> TUSB321 + TPS259470 -> POWER OR -> LMR43620/L2 -> 3V3_CORE", 180, 120, 0.85), ("RTN exposed pad of U1 MUST FLOAT", 105, 115, 1.0)],
    "02_ESP32_USB_Reset.kicad_sch": [("ESP32-S3-WROOM-1U-N16R8 / SAFE RESET AND BOOT", 18, 22, 1.4), ("FLOW: 3V3 -> TPS3808/RESET -> CHIP_PU | USB J5 -> ESD -> R14/R15 -> GPIO19/20 | GPIO -> SPI SERIES PARTS", 18, 28, 0.95), ("CT open = 20 ms reset delay (TPS3808)", 18, 135, 1.0), ("USB tuning capacitors and SPI tuning capacitors: DNP", 270, 45, 1.0)],
    "03_Display_EPaper.kicad_sch": [("DISPLAY POWER-OFF ISOLATION", 18, 22, 1.4), ("FLOW: GPIO SPI -> AXC LEVEL/POWER-OFF ISOLATION -> J6 | 3V3_DISPLAY_SW -> BOOSTER -> PANEL RAILS", 18, 28, 0.95), ("GOOD DISPLAY CHAPTER 12 BOOSTER — DO NOT SUBSTITUTE TOPOLOGY", 190, 22, 1.4), ("FPC contact side / pin-1 orientation: NOT VERIFIED until original sample inspection", 170, 255, 1.0)],
    "04_Touch_RTC.kicad_sch": [("3V0 TOUCH ALWAYS-ON / I2C", 18, 22, 1.4), ("FLOW: 3V3 -> TPS7A02 -> TOUCH + I2C PULL-UPS | TOUCH INT -> GPIO2 WAKE", 18, 28, 0.95), ("DIRECT TOUCH WAKE (DEFAULT)", 280, 88, 1.1), ("WAKE LATCH OPTION — ALL PARTS DNP; mutually exclusive with direct path", 150, 130, 1.0), ("RTC + PRIMARY CELL — internal trickle charger must remain disabled", 18, 190, 1.1)],
    "05_AUTOTERM_1Wire.kicad_sch": [("AUTOTERM UART — 5-V side powered only by heater", 18, 22, 1.4), ("FLOW: ESP32 UART -> TXU0202 -> SERIES + ESD -> J2", 18, 28, 1.0), ("J2 PIN ORDER: 1=5V, 2=GND, 3=TX TO HEATER, 4=RX FROM HEATER", 245, 115, 1.0), ("1-WIRE — THREE DS18B20 / 2–5 m combined harness", 18, 140, 1.4), ("FLOW: 3V3 -> TPS22945 -> SENSOR SUPPLY | GPIO4 -> 0R + ESD -> J3", 18, 146, 1.0)],
    "06_Controls_Diagnostics.kicad_sch": [("EXTERNAL BUTTON + WHITE RING LED / 3 m", 18, 22, 1.4), ("FLOW: J4 BUTTON -> FILTER/ESD -> GPIO1 | GPIO38 -> BCR421 PWM -> J4 RING LED", 18, 28, 0.95), ("FRONTLIGHT 50 mA NOMINAL / <60 mA WORST CASE", 18, 135, 1.2), ("FLOW: VIN_SYS -> AL8861/L4/D10 -> J8 FRONTLIGHT", 18, 141, 0.95), ("ENERGY-FLOW DIAGNOSTICS — LEDs only while DIAG is pressed", 18, 190, 1.2)],
}


def child_schematic(title: str, filename: str, parts: list[Part], notes: list[str], page_number: int, net_pages: dict[str, set[str]]) -> str:
    place(filename, parts)
    sheet_id = uid("sheet", filename)
    defs: dict[str, Part] = {}
    for part in parts:
        defs.setdefault(part.key, part)
    content = ["(kicad_sch (version 20250114) (generator eeschema)",
               f"  (uuid {uid(filename, 'root')})", '  (paper "A3")',
               "  (title_block", f"    (title {q(title)})", '    (date "2026-09-06")', '    (rev "A / Phase 2")',
               '    (company "LandyHeater")', '    (comment 1 "Review schematic - NOT RELEASED FOR PRODUCTION")',
               f"    (comment 2 {q(' | '.join(notes))})", "  )", "  (lib_symbols"]
    for key, exemplar in sorted(defs.items()):
        content.append(lib_symbol(exemplar, embedded=True))
    content.append("  )")
    auxiliaries: list[str] = []
    instances: list[str] = []
    for part in parts:
        sexpr, these_auxiliaries, instance = part_instance(part, filename, sheet_id)
        content.append(sexpr)
        auxiliaries.extend(these_auxiliaries)
        instances.append(instance)
    content.extend(auxiliaries)
    content.extend(connect_nets(filename, parts, net_pages))
    for note, x, y, size in PAGE_NOTES[filename]:
        content.append(text_note(filename, note, x, y, size))
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
        lines.append(lib_symbol(exemplar, embedded=False))
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
        "4": "1WIRE_DQ_GPIO", "5": "I2C_SDA", "6": "I2C_SCL", "7": "TOUCH_RESET_RELEASE",
        "8": "SENSOR_EN", "9": "AUTOTERM_TX_3V3", "10": "AUTOTERM_RX_3V3", "11": "LATCH_CLR_GPIO_N",
        "12": "EPD_BUSY_GPIO", "13": "USB_D_N_ESP", "14": "USB_D_P_ESP",
        "17": "EPD_SCLK_GPIO", "18": "EPD_SDIO_GPIO", "19": "EPD_CS_GPIO_N",
        "20": "EPD_DC_GPIO", "21": "EPD_RESET_GPIO_N", "22": "DISPLAY_EN",
        "23": "FRONTLIGHT_PWM", "24": "AUTOTERM_OE", "27": "BOOT_N",
        "31": "BUTTON_LED_PWM", "32": "DIAG_RUN", "33": "USB_HIGH_CURRENT",
        "34": "STATUS_LED_1", "35": "STATUS_LED_2", "38": "TOUCH_INT_N", "39": "BUTTON_N",
    }
    actual_esp = {number: net for number, _name, net in by_ref["U5"].pins}
    for pad, net in expected_esp.items():
        if actual_esp.get(pad) != net:
            raise ValueError(f"ESP32 pad {pad}: expected {net}, found {actual_esp.get(pad)}")

    expected_connectors = {
        "J1": ["BATT_12V_IN", "GND"],
        "J2": ["AUTOTERM_5V", "GND", "CTRL_TX_TO_HEATER", "CTRL_RX_FROM_HEATER"],
        "J3": ["3V3_SENSOR_SW", "1WIRE_DQ", "GND"],
        "J4": ["BUTTON_N_EXT", "GND", "LED_CC_PLUS", "LED_PWM_MINUS", None],
    }
    for ref, expected in expected_connectors.items():
        actual = [net for _number, _name, net in by_ref[ref].pins]
        if actual != expected:
            raise ValueError(f"Connector pinout mismatch on {ref}: expected {expected}, found {actual}")

    u9_nets = {number: net for number, _name, net in by_ref["U9"].pins}
    for pin in ("8", "9", "10"):
        if u9_nets.get(pin) != "GND":
            raise ValueError(f"U9 unused translator input A{int(pin) - 2} must be tied to GND")

    c37_nets = {net for _number, _name, net in by_ref["C37"].pins}
    if c37_nets != {"EPD_PREVGL", "GND"}:
        raise ValueError("C37 must connect EPD_PREVGL to GND per the display reference circuit")

    if {net for _number, _name, net in by_ref["R5"].pins} != {"USB_VBUS", "USB_CURRENT_OUT1"}:
        raise ValueError("TUSB321 OUT1 pull-up must return to USB_VBUS")
    if {net for _number, _name, net in by_ref["Q8"].pins} != {"USB_CURRENT_OUT1", "GND", "USB_HIGH_CURRENT"}:
        raise ValueError("Q8 USB-current-domain isolator wiring mismatch")

    expected_esd_arrays = {
        "D7": {"1": "CTRL_TX_TO_HEATER", "2": "CTRL_RX_FROM_HEATER", "3": "GND"},
        "D8": {"1": "1WIRE_DQ", "2": "3V3_SENSOR_SW", "3": "GND"},
    }
    for ref, expected in expected_esd_arrays.items():
        actual = {number: net for number, _name, net in by_ref[ref].pins}
        if actual != expected:
            raise ValueError(f"Common-anode ESD-array pinout mismatch on {ref}: {actual}")

    u18 = {number: net for number, _name, net in by_ref["U18"].pins}
    if u18.get("1") != "BUTTON_LED_EN" or any(u18.get(pin) != "LED_PWM_MINUS" for pin in ("2", "3", "5")):
        raise ValueError("BCR421 native PWM/output topology mismatch")

    for ref in ("C40", "C41", "C42", "C43", "C44", "C45", "C46"):
        if not by_ref[ref].dnp:
            raise ValueError(f"{ref} must remain DNP until signal-integrity validation")

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
        "D17": {"1": "Q2_GATE_FET", "2": "VIN_12V_PROTECTED"},
        "D10": {"1": "VIN_SYS", "2": "FL_LX"},
        "LED1": {"1": "LED12_K", "2": "VIN_12V_PROTECTED"},
        "LED2": {"1": "LEDUSB_K", "2": "USB_VBUS"},
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
    net_pages: dict[str, set[str]] = {}
    for _title, filename, parts, _notes in page_defs:
        for part in parts:
            for _number, _name, net in part.pins:
                if net:
                    net_pages.setdefault(net, set()).add(filename)
    HW.mkdir(parents=True, exist_ok=True)
    SYMLIB.parent.mkdir(parents=True, exist_ok=True)
    (HW / "LandyHeater-Board.kicad_sch").write_text(root_schematic(page_defs), encoding="utf-8")
    for page_number, (title, filename, parts, notes) in enumerate(page_defs, start=2):
        (HW / filename).write_text(child_schematic(title, filename, parts, notes, page_number, net_pages), encoding="utf-8")
    SYMLIB.write_text(symbol_library(page_defs), encoding="utf-8")
    print(f"Generated {1 + len(page_defs)} schematics and {SYMLIB.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
