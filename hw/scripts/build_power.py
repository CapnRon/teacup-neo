"""POWER section -- rebuilt to the project's BUILD.md core directive:
connectivity by LABEL, not wires. Every pin gets either a power flag
placed directly on it (rotated parallel to the pin, value text kept
horizontal in the pin's own row) or a net label anchored exactly at the
pin. There is not a single drawn wire or junction in this sheet, which
structurally eliminates the wire-pass-through short class entirely.

All coordinates are in 50mil grid steps via S(); schgen asserts grid
alignment on every emitted coordinate.

Internal (single-sheet) nets use local labels named after their IC:
U1_EN, U1_SW, U1_BST, U1_VCC, U1_SS, U2_SW, U2_BST, U2_EN, U7_SW,
U7_BST, U7_EN, P3V3_FB, U4_CT. Board-wide nets keep their existing
global names. Pin-to-net assignments reproduce the pre-rebuild netlist
exactly (verified by component-connectivity diff), including R1 pulling
U1's EN up to +5V_SW (the input rail) as originally designed.
"""
import sys, uuid
sys.path.insert(0, '.')
from schgen import Sheet, GRID

TC = "/home/administrator/projects/teacup-neo/hw/teacup-carrier.kicad_sym"
DEV = "/usr/share/kicad/symbols/Device.kicad_sym"
PWR = "/usr/share/kicad/symbols/power.kicad_sym"
REGLIB = "/usr/share/kicad/symbols/Regulator_Linear.kicad_sym"

def S(n):
    return round(n * GRID, 2)

s = Sheet()
s.ensure_symbol(TC, "AP62600SJ-7", "teacup-carrier:AP62600SJ-7")
s.ensure_symbol(TC, "AP62300WU-7", "teacup-carrier:AP62300WU-7")
s.ensure_symbol(TC, "MCP4661-104E_ST", "teacup-carrier:MCP4661-104E_ST")
s.ensure_symbol(TC, "TPS22990DMLR", "teacup-carrier:TPS22990DMLR")
s.ensure_symbol(DEV, "R", "Device:R")
s.ensure_symbol(DEV, "C", "Device:C")
s.ensure_symbol(DEV, "L", "Device:L")
s.ensure_symbol(PWR, "GND", "power:GND")
s.ensure_symbol(PWR, "+3V3", "power:+3V3")
s.ensure_symbol(REGLIB, "L7805", "Regulator_Linear:L7805")
REG = "Regulator_Linear:L7805"

LABEL_ANGLE = {"right": 0, "left": 180, "up": 90, "down": 270}

def pin_net(pin_xy, net, direction, global_=None):
    """Net label anchored exactly at the pin, extending away from the
    component in the pin's own direction. Globals are auto-detected by
    name unless overridden: internal Ux_* / *_FB nets stay local."""
    if global_ is None:
        global_ = not (net.startswith(("U1_", "U2_", "U4_", "U5_", "U7_", "U14_")) or net.endswith("_FB"))
    s.label(net, pin_xy[0], pin_xy[1], LABEL_ANGLE[direction], global_=global_)

def vert2(lib, ref, val, x, y, top, bottom, fp):
    """Vertical 2-pin passive island: pin1 up, pin2 down; `top`/`bottom`
    are either ("flag", kind) or a net name string. Ref+value are placed
    beside the body (right side) so they never sit on the pins."""
    s.place(lib, ref, val, x, y, 0, footprint=fp,
            ref_at=(x + S(4), y - S(1), 0), value_at=(x + S(4), y + S(1), 0))
    p1 = s.pin(lib, x, y, 0, "1")
    p2 = s.pin(lib, x, y, 0, "2")
    for p, spec, d in ((p1, top, "up"), (p2, bottom, "down")):
        if isinstance(spec, tuple):
            s.flag(spec[1], p, "P", d)
        else:
            pin_net(p, spec, d)
    return p1, p2

def horiz2(lib, ref, val, x, y, left, right, fp):
    """Horizontal 2-pin passive island (placement angle 90 puts pin1 on
    the LEFT): pin1 <- left spec, pin2 -> right spec. Property angle 270
    cancels the symbol's own 90 rotation so ref/value render horizontal."""
    s.place(lib, ref, val, x, y, 90, footprint=fp,
            ref_at=(x, y - S(3), 270), value_at=(x, y + S(3), 270))
    p1 = s.pin(lib, x, y, 90, "1")
    p2 = s.pin(lib, x, y, 90, "2")
    for p, spec, d in ((p1, left, "left"), (p2, right, "right")):
        if isinstance(spec, tuple):
            s.flag(spec[1], p, "P", d)
        else:
            pin_net(p, spec, d)
    return p1, p2

GNDF = ("flag", "GND")
P3V3F = ("flag", "+3V3")

# ============ VCORE buck (U1, AP62600SJ-7) ============
U1 = "teacup-carrier:AP62600SJ-7"
u1x, u1y = S(48), S(24)
s.place(U1, "U1", "AP62600SJ-7", u1x, u1y, 0,
        footprint="teacup-carrier:QFN-12_L3.0-W2.0-P0.50-TL_AP62600SJ-7",
        ref_at=(u1x, u1y - S(9), 0), value_at=(u1x, u1y + S(9), 0))
P1 = lambda n: s.pin(U1, u1x, u1y, 0, str(n))

s.flag("GND", P1(1), "P", "left")            # PGND
pin_net(P1(2), "+5V_SW", "left")             # VIN
pin_net(P1(3), "U1_EN", "left")              # EN
s.flag("GND", P1(4), "P", "left")            # MODE
s.flag("GND", P1(5), "P", "left")            # FSEL
pin_net(P1(6), "PG_VCORE", "left")           # PG (open-drain, R2 pulls up)
pin_net(P1(12), "VCORE_FB", "right")         # FB
s.flag("GND", P1(11), "P", "right")          # GND
pin_net(P1(10), "U1_SS", "right")            # SS/TR
pin_net(P1(9), "U1_VCC", "right")            # VCC
pin_net(P1(8), "U1_SW", "right")             # SW
pin_net(P1(7), "U1_BST", "right")            # BST

# U1 passive islands
py1 = S(48)
vert2("Device:C", "C1", "22uF", S(20), py1, "+5V_SW", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:C", "C2", "100nF", S(29), py1, "+5V_SW", GNDF, "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C4", "1uF", S(38), py1, "U1_VCC", GNDF, "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C5", "4.7nF", S(47), py1, "U1_SS", GNDF, "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C3", "100nF", S(56), py1, "U1_BST", "U1_SW", "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C9", "22uF", S(65), py1, "VCORE", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:C", "C10", "22uF", S(74), py1, "VCORE", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:R", "R1", "100k", S(83), py1, "+5V_SW", "U1_EN", "Resistor_SMD:R_0402_1005Metric")
vert2("Device:R", "R2", "10k", S(92), py1, P3V3F, "PG_VCORE", "Resistor_SMD:R_0402_1005Metric")
horiz2("Device:L", "L1", "2.2uH", S(106), py1, "U1_SW", "VCORE", "Inductor_SMD:L_1210_3225Metric")

# ============ VDDR buck (U2, AP62300WU-7) ============
U2 = "teacup-carrier:AP62300WU-7"
u2x, u2y = S(48), S(64)
s.place(U2, "U2", "AP62300WU-7", u2x, u2y, 0,
        footprint="teacup-carrier:TSOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL",
        ref_at=(u2x, u2y - S(6), 0), value_at=(u2x, u2y + S(6), 0))
P2 = lambda n: s.pin(U2, u2x, u2y, 0, str(n))

s.flag("GND", P2(1), "P", "left")            # GND
pin_net(P2(2), "U2_SW", "left")              # SW
pin_net(P2(3), "+5V_SW", "left")             # VIN
pin_net(P2(4), "VDDR_FB", "right")           # FB
pin_net(P2(5), "U2_EN", "right")             # EN
pin_net(P2(6), "U2_BST", "right")            # BST

py2 = S(84)
vert2("Device:C", "C6", "10uF", S(20), py2, "+5V_SW", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:C", "C7", "100nF", S(29), py2, "U2_BST", "U2_SW", "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C11", "22uF", S(38), py2, "VDDR", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:R", "R3", "100k", S(47), py2, P3V3F, "U2_EN", "Resistor_SMD:R_0402_1005Metric")
horiz2("Device:L", "L2", "2.2uH", S(62), py2, "U2_SW", "VDDR", "Inductor_SMD:L_1210_3225Metric")

# ============ Main +3.3V buck (U7, AP62300WU-7) ============
u7x, u7y = S(48), S(100)
s.place(U2, "U7", "AP62300WU-7", u7x, u7y, 0,
        footprint="teacup-carrier:TSOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL",
        ref_at=(u7x, u7y - S(6), 0), value_at=(u7x, u7y + S(6), 0))
P7 = lambda n: s.pin(U2, u7x, u7y, 0, str(n))

s.flag("GND", P7(1), "P", "left")            # GND
pin_net(P7(2), "U7_SW", "left")              # SW
pin_net(P7(3), "+5V_SW", "left")             # VIN
pin_net(P7(4), "P3V3_FB", "right")           # FB
pin_net(P7(5), "U7_EN", "right")             # EN
pin_net(P7(6), "U7_BST", "right")            # BST

py7 = S(120)
vert2("Device:C", "C16", "10uF", S(20), py7, "+5V_SW", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:C", "C17", "100nF", S(29), py7, "U7_BST", "U7_SW", "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:C", "C18", "22uF", S(38), py7, "+3V3", GNDF, "Capacitor_SMD:C_0805_2012Metric")
vert2("Device:R", "R5", "100k", S(47), py7, P3V3F, "U7_EN", "Resistor_SMD:R_0402_1005Metric")
# fixed 3.3V feedback divider: +3V3 -- R6 -- P3V3_FB -- R7 -- GND
vert2("Device:R", "R6", "31.6k", S(56), py7, P3V3F, "P3V3_FB", "Resistor_SMD:R_0402_1005Metric")
vert2("Device:R", "R7", "10k", S(65), py7, "P3V3_FB", GNDF, "Resistor_SMD:R_0402_1005Metric")
horiz2("Device:L", "L3", "2.2uH", S(80), py7, "U7_SW", "+3V3", "Inductor_SMD:L_1210_3225Metric")

# ============ BMC-alive diode-OR (D1/D2): keep the ESP32 powered on ALT-only ============
# +5V_BMC (J9-only) normally feeds U5 alone; if J9 is unplugged and only
# +5V_ALT is present, the ESP32 would otherwise be fully dead (its own
# isolated domain, by design -- see io.kicad_sch Q1/Q2). D1/D2 diode-OR
# both candidate sources into U5_VIN, a node ONLY U5 sees -- U4 (the
# BMC-branch load switch feeding +5V_SW) still sources strictly from the
# real, undiluted +5V_BMC net, so its behavior stays unambiguous; this
# fix is scoped to "keep the BMC brain alive," not a second path to
# +5V_SW (U14/+5V_ALT is already the correct direct path for that).
# PMEG2010ER: 1A Schottky, 340mV Vf @ 1A (LCSC C82288) -- plenty of
# margin over the WROOM-1's peak draw, low enough drop to stay inside
# the AZ1117-3.3's dropout at that current (reconfirm against real load
# current at bring-up).
DSCH = "Device:D_Schottky"
s.ensure_symbol(DEV, "D_Schottky", "Device:D_Schottky")

d1x, d1y = S(108), S(10)
s.place(DSCH, "D1", "PMEG2010ER", d1x, d1y, 0,
        footprint="Diode_SMD:D_SOD-123W",
        ref_at=(d1x, d1y - S(3), 0), value_at=(d1x, d1y + S(3), 0))
pin_net(s.pin(DSCH, d1x, d1y, 0, "1"), "U5_VIN", "left")     # K
pin_net(s.pin(DSCH, d1x, d1y, 0, "2"), "+5V_BMC", "right")   # A

d2x, d2y = S(108), S(22)
s.place(DSCH, "D2", "PMEG2010ER", d2x, d2y, 0,
        footprint="Diode_SMD:D_SOD-123W",
        ref_at=(d2x, d2y - S(3), 0), value_at=(d2x, d2y + S(3), 0))
pin_net(s.pin(DSCH, d2x, d2y, 0, "1"), "U5_VIN", "left")     # K
pin_net(s.pin(DSCH, d2x, d2y, 0, "2"), "+5V_ALT", "right")   # A

# ============ Always-on 3.3V LDO (U5, AZ1117CH-3.3) ============
u5x, u5y = S(150), S(16)
s.place(REG, "U5", "AZ1117CH-3.3TRG1", u5x, u5y, 0,
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        extra_props={"Datasheet": "https://lcsc.com/product-detail/C92102.html"},
        ref_at=(u5x, u5y - S(6), 0), value_at=(u5x, u5y - S(4), 0))
pin_net(s.pin(REG, u5x, u5y, 0, "1"), "U5_VIN", "left")
s.flag("GND", s.pin(REG, u5x, u5y, 0, "2"), "P", "down")
pin_net(s.pin(REG, u5x, u5y, 0, "3"), "+3V3_ALWAYS", "right")
vert2("Device:C", "C14", "1uF", S(128), S(16), "U5_VIN", GNDF, "Capacitor_SMD:C_0603_1608Metric")
vert2("Device:C", "C15", "10uF", S(178), S(16), "+3V3_ALWAYS", GNDF, "Capacitor_SMD:C_0805_2012Metric")

# ============ +1.8V LDO (U6, AZ1117CH-1.8) ============
u6x, u6y = S(150), S(44)
s.place(REG, "U6", "AZ1117CH-1.8TRG1", u6x, u6y, 0,
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        extra_props={"Datasheet": "https://lcsc.com/product-detail/C95397.html"},
        ref_at=(u6x, u6y - S(6), 0), value_at=(u6x, u6y - S(4), 0))
pin_net(s.pin(REG, u6x, u6y, 0, "1"), "+3V3", "left")
s.flag("GND", s.pin(REG, u6x, u6y, 0, "2"), "P", "down")
pin_net(s.pin(REG, u6x, u6y, 0, "3"), "+1V8", "right")
vert2("Device:C", "C19", "1uF", S(128), S(44), "+3V3", GNDF, "Capacitor_SMD:C_0603_1608Metric")
vert2("Device:C", "C20", "10uF", S(178), S(44), "+1V8", GNDF, "Capacitor_SMD:C_0805_2012Metric")

# ============ BMC-branch load switch (U4, TPS22990DMLR) ============
# Gates +5V_BMC (the ESP32's own dedicated USB-C, isolated from every
# other source) onto the shared +5V_SW rail. EN_SW_BMC is arbitrated
# between GPIO (SW5V_EN_BMC, through R21), its own pulldown (R20), and
# SW2's throw1 on the bmc sheet (crosses in via this same label) -- one
# throw of the same on-off-on switch that forces the ALT branch (U14) on
# the other throw.
U4 = "teacup-carrier:TPS22990DMLR"
u4x, u4y = S(150), S(76)
s.place(U4, "U4", "TPS22990DMLR", u4x, u4y, 0,
        footprint="teacup-carrier:WSON-10_L3.0-W2.0-P0.50-BL-EP_TI_DML",
        ref_at=(u4x, u4y - S(9), 0), value_at=(u4x, u4y + S(9), 0))
P4 = lambda n: s.pin(U4, u4x, u4y, 0, str(n))

pin_net(P4(1), "U4_CT", "left")              # CT
# pin 2 NC -- deliberately unconnected per datasheet
pin_net(P4(3), "+5V_BMC", "left")            # VIN
pin_net(P4(4), "+5V_BMC", "left")            # VBIAS (tied to VIN)
pin_net(P4(5), "EN_SW_BMC", "left")          # ON
s.flag("GND", P4(6), "P", "right")           # GND
pin_net(P4(7), "PG_SW5V", "right")           # PG (open-drain, R4 pulls up)
pin_net(P4(8), "+5V_SW", "right")            # VOUT
pin_net(P4(9), "+5V_SW", "right")            # VOUT
pin_net(P4(10), "+5V_SW", "right")           # VOUT
pin_net(P4(11), "+5V_BMC", "right")          # VIN

vert2("Device:C", "C13", "1nF_TBD", S(132), S(96), "U4_CT", GNDF, "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:R", "R4", "10k", S(150), S(96), P3V3F, "PG_SW5V", "Resistor_SMD:R_0402_1005Metric")

# BMC-branch EN arbitration: GPIO drives through a 1k series resistor,
# a 100k pulldown keeps it safely off when undriven (ESP32 in reset/Hi-Z).
vert2("Device:R", "R21", "1k", S(132), S(60), "SW5V_EN_BMC", "EN_SW_BMC", "Resistor_SMD:R_0402_1005Metric")
vert2("Device:R", "R20", "100k", S(141), S(60), "EN_SW_BMC", GNDF, "Resistor_SMD:R_0402_1005Metric")

# ============ ALT-branch load switch (U14, TPS22990DMLR) ============
# Gates +5V_ALT (the priority-OR'd DC jack / alt USB-C, see io.kicad_sch
# Q1/Q2) onto the same shared +5V_SW rail. EN_SW_ALT is arbitrated the
# same way as EN_SW_BMC (GPIO + pulldown) but is ALSO hard-overridable by
# SW2's throw4 on the bmc sheet, which ties this node to +5V_ALT (SW2's
# pole) when selected -- low-impedance, beats GPIO16's resistor-limited
# drive. Center = neither throw engaged, GPIO has full control.
U14 = "teacup-carrier:TPS22990DMLR"
u14x, u14y = S(210), S(76)
s.place(U14, "U14", "TPS22990DMLR", u14x, u14y, 0,
        footprint="teacup-carrier:WSON-10_L3.0-W2.0-P0.50-BL-EP_TI_DML",
        ref_at=(u14x, u14y - S(9), 0), value_at=(u14x, u14y + S(9), 0))
P14 = lambda n: s.pin(U14, u14x, u14y, 0, str(n))

pin_net(P14(1), "U14_CT", "left")            # CT
# pin 2 NC -- deliberately unconnected per datasheet
pin_net(P14(3), "+5V_ALT", "left")           # VIN
pin_net(P14(4), "+5V_ALT", "left")           # VBIAS (tied to VIN)
pin_net(P14(5), "EN_SW_ALT", "left")         # ON
s.flag("GND", P14(6), "P", "right")          # GND
pin_net(P14(7), "PG_SW5V_ALT", "right")      # PG (open-drain, R24 pulls up)
pin_net(P14(8), "+5V_SW", "right")           # VOUT (same shared rail as U4)
pin_net(P14(9), "+5V_SW", "right")           # VOUT
pin_net(P14(10), "+5V_SW", "right")          # VOUT
pin_net(P14(11), "+5V_ALT", "right")         # VIN

vert2("Device:C", "C23", "1nF_TBD", S(192), S(96), "U14_CT", GNDF, "Capacitor_SMD:C_0402_1005Metric")
vert2("Device:R", "R24", "10k", S(210), S(96), P3V3F, "PG_SW5V_ALT", "Resistor_SMD:R_0402_1005Metric")

# ALT-branch EN arbitration -- same topology as the BMC branch, plus SW2's
# hard override on the bmc sheet (crosses in via the EN_SW_ALT label).
vert2("Device:R", "R23", "1k", S(192), S(60), "SW5V_EN_ALT", "EN_SW_ALT", "Resistor_SMD:R_0402_1005Metric")
vert2("Device:R", "R22", "100k", S(201), S(60), "EN_SW_ALT", GNDF, "Resistor_SMD:R_0402_1005Metric")

# ============ Digipot (U3, MCP4661, both channels) ============
U3 = "teacup-carrier:MCP4661-104E_ST"
u3x, u3y = S(150), S(130)
s.place(U3, "U3", "MCP4661-104E_ST", u3x, u3y, 0,
        footprint="Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        ref_at=(u3x, u3y - S(9), 0), value_at=(u3x, u3y + S(9), 0))
P3 = lambda n: s.pin(U3, u3x, u3y, 0, str(n))

s.flag("GND", P3(1), "P", "left")            # HVC/A0
pin_net(P3(2), "I2C_PWR_SCL", "left")        # SCL
pin_net(P3(3), "I2C_PWR_SDA", "left")        # SDA
s.flag("GND", P3(4), "P", "left")            # VSS
s.flag("GND", P3(5), "P", "left")            # P1B
pin_net(P3(6), "VDDR_FB", "left")            # P1W
pin_net(P3(7), "VDDR", "left")               # P1A
pin_net(P3(8), "VCORE", "right")             # P0A
pin_net(P3(9), "VCORE_FB", "right")          # P0W
s.flag("GND", P3(10), "P", "right")          # P0B
s.flag("+3V3", P3(11), "P", "right")         # WP
s.flag("GND", P3(12), "P", "right")          # A2
s.flag("GND", P3(13), "P", "right")          # A1
s.flag("+3V3", P3(14), "P", "right")         # VDD

vert2("Device:C", "C12", "100nF", S(200), S(130), P3V3F, GNDF, "Capacitor_SMD:C_0402_1005Metric")

out = s.render("Power", str(uuid.uuid4()), "/e91d090e-0b5e-4716-96ce-185f84fa3402", "2", paper="A3")
open("/home/administrator/projects/teacup-neo/hw/sheets/power.kicad_sch", "w").write(out)
print("wrote power.kicad_sch,", len(out), "bytes")
