"""T41 interposer SoC section -- connectivity by label, same convention
as the T31ZX interposer. Pin-to-net assignments come from
../pinout_288.csv's t41_pin column, derived from the real
T41_QFN_GC4663_38 reference schematic (verified pin-by-pin against
high-res crops of the actual PDF) and cross-referenced against the
carrier's fixed 288-finger table -- 58 direct matches, 11 pushed to
spares (no matching carrier finger exists for these), 0 conflicts.
Genuine capability difference from T31: T41 has usable MSC1_D0-D3 and
SSI1_DT/DR pins where T31 had to sacrifice those to higher-priority
functions, and T41 has a real dedicated DDR supply rail (VCC_DDR) tied
to J1's VDDR fingers, unlike T31 which folded its DDR domain into
+1V8. Per explicit user direction, 2026-07-19.
"""
import sys, uuid
sys.path.insert(0, '.')
from schgen import Sheet, GRID

TI = "/home/administrator/projects/teacup-neo/hw/interposer_t41/teacup-interposer-t41.kicad_sym"
DEV = "/usr/share/kicad/symbols/Device.kicad_sym"
PWR = "/usr/share/kicad/symbols/power.kicad_sym"
FLASH = "/usr/share/kicad/symbols/Memory_Flash.kicad_sym"

def S(n):
    return round(n * GRID, 2)

s = Sheet()
s.ensure_symbol(TI, "T41", "teacup-interposer-t41:T41")
s.ensure_symbol(DEV, "R", "Device:R")
s.ensure_symbol(DEV, "C", "Device:C")
s.ensure_symbol(DEV, "Crystal_GND24", "Device:Crystal_GND24")
s.ensure_symbol(FLASH, "W25Q32JVSS", "Memory_Flash:W25Q32JVSS")
s.ensure_symbol(PWR, "GND", "power:GND")
s.ensure_symbol(PWR, "PWR_FLAG", "power:PWR_FLAG")

LABEL_ANGLE = {"right": 0, "left": 180, "up": 90, "down": 270}
GNDF = ("flag", "GND")

# ---------- place T41 ----------
IC1 = "teacup-interposer-t41:T41"
icx, icy = S(160), S(180)
s.place(IC1, "U11", "T41", icx, icy, 0,
        footprint="teacup-interposer-t41:T41_QFN96",
        ref_at=(icx, icy - S(80), 0), value_at=(icx, icy + S(80), 0))

# per-pin assignment: ("NET"|"RAIL", net_name) | ("LOCAL", local_net_name) | ("GND",)
PIN_ASSIGN = {
    "1": ("NET", "SSI1_DR"),
    "2": ("NET", "UART0_CTS"),
    "3": ("NET", "SSI1_CLK"),
    "4": ("NET", "SSI1_CE0"),
    "5": ("NET", "SSI1_DT"),
    "6": ("NET", "MSC1_D1"),
    "7": ("NET", "MSC1_D0"),
    "8": ("RAIL", "VCORE"),
    "9": ("RAIL", "+3V3"),
    "10": ("NET", "MSC1_CMD"),
    "11": ("NET", "MSC1_CLK"),
    "12": ("NET", "MSC1_D3_CD"),
    "13": ("NET", "MSC1_D2"),
    "14": ("RAIL", "VCORE"),
    "15": ("LOCAL", "EXCLK_I"),
    "16": ("LOCAL", "EXCLK_O"),
    "17": ("RAIL", "+1V8"),
    "18": ("NET", "SPARE_P175"),
    "19": ("NET", "MIPI0_GPIO"),
    "20": ("NET", "SMB0_SDA"),
    "21": ("NET", "SMB0_SCK"),
    "22": ("RAIL", "+1V8"),
    "23": ("NET", "MIPI0_D0P"),
    "24": ("NET", "MIPI0_D0N"),
    "25": ("NET", "MIPI0_CLKP"),
    "26": ("NET", "MIPI0_CLKN"),
    "27": ("NET", "MIPI0_D1P"),
    "28": ("NET", "MIPI0_D1N"),
    "29": ("NET", "MICLP"),
    "30": ("NET", "SPARE_P182"),
    "31": ("RAIL", "+1V8"),
    "32": ("RAIL", "VCORE"),
    "33": ("LOCAL", "VCM"),
    "34": ("NET", "HPOUTL"),
    "35": ("NET", "USBA_HOST_DM"),
    "36": ("NET", "USBA_HOST_DP"),
    "37": ("RAIL", "+3V3"),
    "38": ("NET", "SSI0_CE0"),
    "39": ("NET", "SSI0_DR"),
    "40": ("RAIL", "+3V3"),
    "41": ("RAIL", "VCORE"),
    "42": ("NET", "SPARE_P183"),
    "43": ("NET", "SSI0_DT"),
    "44": ("NET", "SSI0_CLK"),
    "45": ("NET", "SPARE_P184"),
    "46": ("NET", "GMAC0_PHYCLK"),
    "47": ("NET", "GMAC0_RXDV"),
    "48": ("NET", "GMAC0_MDIO"),
    "49": ("NET", "GMAC0_MDCK"),
    "50": ("RAIL", "+1V8"),
    "51": ("NET", "SAR_AUX0"),
    "52": ("RAIL", "+1V8"),
    "53": ("NET", "GMAC0_TXEN"),
    "54": ("NET", "GMAC0_TXD1"),
    "55": ("NET", "GMAC0_TXD0"),
    "56": ("NET", "GMAC0_TXCLK"),
    "57": ("NET", "GMAC0_RXD1"),
    "58": ("NET", "GMAC0_RXD0"),
    "59": ("RAIL", "VCORE"),
    "60": ("LOCAL", "POR_CTL"),
    "61": ("NET", "MSC0_D1"),
    "62": ("NET", "MSC0_CLK"),
    "63": ("NET", "MSC0_D0"),
    "64": ("NET", "MSC0_D3_CD"),
    "65": ("RAIL", "+3V3"),
    "66": ("RAIL", "VCORE"),
    "67": ("NET", "MSC0_D2"),
    "68": ("NET", "MSC0_CMD"),
    "69": ("NET", "SPARE_P185"),
    "70": ("NET", "SPARE_P186"),
    "71": ("NET", "PWM1"),
    "72": ("NET", "PWM0"),
    "73": ("NET", "SPARE_P187"),
    "74": ("NET", "SPARE_P188"),
    "75": ("NET", "SPARE_P189"),
    "76": ("NET", "SPARE_P190"),
    "77": ("NET", "SMB1_SDA"),
    "78": ("NET", "SMB1_SCK"),
    "79": ("NET", "GPIO0"),
    "80": ("NET", "SPARE_P179"),
    "81": ("RAIL", "VCORE"),
    "82": ("RAIL", "VDDR"),
    "83": ("LOCAL", "DDR_ZQ"),
    "84": ("LOCAL", "RZQ"),
    "85": ("RAIL", "+1V8"),
    "86": ("LOCAL", "DDR_VREF"),
    "87": ("RAIL", "VDDR"),
    "88": ("RAIL", "VCORE"),
    "89": ("NET", "UART2_CTS"),
    "90": ("NET", "UART2_RTS"),
    "91": ("NET", "UART2_RXD"),
    "92": ("NET", "UART2_TXD"),
    "93": ("NET", "SPARE_P191"),
    "94": ("NET", "UART0_RXD"),
    "95": ("NET", "UART0_TXD"),
    "96": ("NET", "UART0_RTS"),
    "97": ("GND",),
}
assert len(PIN_ASSIGN) == 97

for num, entry in PIN_ASSIGN.items():
    p = s.pin_pos(IC1, icx, icy, 0, num)
    d = s.pin_dir(IC1, num)
    kind = entry[0]
    if kind == "GND":
        s.flag("GND", p, "S", d)
    elif kind == "LOCAL":
        s.label(entry[1], p[0], p[1], LABEL_ANGLE[d], global_=False)
    else:  # NET or RAIL -- both cross to the DDR4 edge connector sheet
        s.label(entry[1], p[0], p[1], LABEL_ANGLE[d], global_=True)

# ============ Local support circuitry ============

RAIL_NAMES = {"+1V8", "+3V3", "VCORE", "VDDR"}

def vert2(lib, ref, val, x, y, top, bottom, fp):
    s.place(lib, ref, val, x, y, 0, footprint=fp,
            ref_at=(x + S(4), y - S(1), 0), value_at=(x + S(4), y + S(1), 0))
    for pn, spec, d in (("1", top, "up"), ("2", bottom, "down")):
        p = s.pin(lib, x, y, 0, pn)
        if isinstance(spec, tuple):
            s.flag(spec[1], p, "S", d)
        else:
            s.label(spec, p[0], p[1], LABEL_ANGLE[d], global_=spec in RAIL_NAMES)

# --- Crystal: Y1 (24MHz) + C77/C80 (12pF load) + R23 (1M feedback) +
# R24 (33R series) -- exact topology from the real T41 board's CLK block. ---
CRYSTAL = "Device:Crystal_GND24"
cx, cy = S(20), S(20)
s.place(CRYSTAL, "Y1", "24 MHz", cx, cy, 0,
        footprint="Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm",
        ref_at=(cx, cy - S(6), 0), value_at=(cx, cy + S(6), 0))
for pn, spec in (("1", "EXCLK_I"), ("2", GNDF), ("3", "EXCLK_O_INT")):
    p = s.pin(CRYSTAL, cx, cy, 0, pn)
    d = s.pin_dir(CRYSTAL, pn)
    if isinstance(spec, tuple):
        s.flag(spec[1], p, "S", d)
    else:
        s.label(spec, p[0], p[1], LABEL_ANGLE[d], global_=False)

vert2("Device:C", "C77", "12pF", S(30), S(20), "EXCLK_I", GNDF, "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C80", "12pF", S(38), S(20), "EXCLK_O_INT", GNDF, "Capacitor_SMD:C_0402_1005Metric")
# R24 (33R series) sits between the crystal's own node (EXCLK_O_INT) and
# the pin's actual EXCLK_O net. R23 (1M feedback) spans the FULL loop --
# EXCLK_I straight to the final EXCLK_O, on the far side of R24 -- not to
# the crystal's own intermediate node. Confirmed against a high-res crop
# of the real schematic: R23's bottom terminal lands on the same node as
# R24's output/the EXCLKO label, not on Y1's own pin.
vert2("Device:R", "R24", "33R", S(46), S(20), "EXCLK_O_INT", "EXCLK_O", "Resistor_SMD:R_0402_1005Metric")
vert2("Device:R", "R23", "1M", S(54), S(20), "EXCLK_I", "EXCLK_O", "Resistor_SMD:R_0402_1005Metric")

# --- DDR_ZQ / RZQ calibration resistors (240R/1% to GND each, matches
# the real board's R16/R18). ---
vert2("Device:R", "R16", "240R 1%", S(20), S(35), "DDR_ZQ", GNDF, "Resistor_SMD:R_0402_1005Metric")
vert2("Device:R", "R18", "240R 1%", S(28), S(35), "RZQ", GNDF, "Resistor_SMD:R_0402_1005Metric")

# --- POR_CTL pull-up (R20, 1K to +3V3, matches the real board). ---
vert2("Device:R", "R20", "1K", S(36), S(35), "+3V3", "POR_CTL", "Resistor_SMD:R_0402_1005Metric")

# --- VCM local bypass (matches T31's own audio codec VCM bypass topology). ---
vert2("Device:C", "C69", "4.7uF", S(20), S(45), "VCM", GNDF, "Capacitor_SMD:C_0603_1608Metric")

# --- VCORE decoupling (x8, 100nF/0402, matches T41's 8 VDD pins). ---
for i, ref in enumerate(["C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50"]):
    vert2("Device:C", ref, "100nF", S(20 + i * 6), S(60), "VCORE", GNDF, "Capacitor_SMD:C_0402_1005Metric")

# --- VDDR (DDR rail) decoupling (x4, matches T41's DDRVDD_1/2 bank). ---
for i, ref in enumerate(["C24", "C25", "C26", "C27"]):
    vert2("Device:C", ref, "100nF", S(20 + i * 6), S(70), "VDDR", GNDF, "Capacitor_SMD:C_0402_1005Metric")

# --- +1V8 decoupling (x4, covers DDRPLL_VCCA/CSI_VCCA18/CODEC_USB_AVDD/ADC_AVDD/VDDIO18_1-2). ---
for i, ref in enumerate(["C51", "C52", "C53", "C54"]):
    vert2("Device:C", ref, "100nF", S(20 + i * 6), S(80), "+1V8", GNDF, "Capacitor_SMD:C_0402_1005Metric")

# --- +3V3 decoupling (x3, covers USB_AVD33/VDDIO1_1-2/VDDIO2). ---
for i, ref in enumerate(["C55", "C56", "C57"]):
    vert2("Device:C", ref, "100nF", S(20 + i * 6), S(90), "+3V3", GNDF, "Capacitor_SMD:C_0402_1005Metric")

# --- Optional self-contained NOR flash (SFC0 bus) -- matches the real
# board's U7 (GD25Q127CSIG), same idiom as T31's own optional U4. ---
FLASHLIB = "Memory_Flash:W25Q32JVSS"
fx, fy = S(70), S(45)
s.place(FLASHLIB, "U7", "GD25Q127CSIG", fx, fy, 0,
        footprint="Package_SO:SOIC-8_5.3x5.3mm_P1.27mm",
        ref_at=(fx, fy - S(6), 0), value_at=(fx, fy + S(6), 0))
U7_PINS = {
    "1": "SSI0_CE0", "2": "SSI0_DT", "3": "+1V8", "4": ("flag", "GND"),
    "5": "SSI0_DR", "6": "SSI0_CLK", "7": "+1V8", "8": "+1V8",
}
for pn, spec in U7_PINS.items():
    p = s.pin(FLASHLIB, fx, fy, 0, pn)
    d = s.pin_dir(FLASHLIB, pn)
    if isinstance(spec, tuple):
        s.flag(spec[1], p, "S", d)
    else:
        s.label(spec, p[0], p[1], LABEL_ANGLE[d], global_=True)

# --- PWR_FLAG markers: +1V8/+3V3/VCORE/VDDR are all carrier-sourced (no
# local regulator on this module), so ERC needs an explicit "this is
# externally driven" marker on each. ---
PWRFLAG = "power:PWR_FLAG"
for i, railname in enumerate(["+1V8", "+3V3", "VCORE", "VDDR"]):
    px, py = S(80 + i * 8), S(45)
    s.place(PWRFLAG, f"#PWR9{i+1}", "PWR_FLAG", px, py, 0)
    p = s.pin(PWRFLAG, px, py, 0, "1")
    s.label(railname, p[0], p[1], LABEL_ANGLE[s.pin_dir(PWRFLAG, "1")], global_=True)

out = s.render("SoC (T41 reference)", str(uuid.uuid4()), "/f3a4b5c6-0002-4000-8000-000000000001", "2", paper="A2")
open("/home/administrator/projects/teacup-neo/hw/interposer_t41/sheets/soc.kicad_sch", "w").write(out)
print("wrote soc.kicad_sch,", len(out), "bytes")
