"""DDR4 UDIMM-288 card edge (T41 interposer side) -- connectivity by
label, same convention as the T31ZX interposer this was cloned from.
Every one of the 288 fingers gets a global label matching
pinout_288.csv's carrier_net column verbatim -- an exact copy of the
completed T31ZX interposer's finalized pinout, per explicit user
direction, so this module's fingers land on the same nets the carrier's
own J1 socket expects regardless of which SoC module is seated. No SoC
sheet exists yet (T41 pin-to-finger assignment is deferred), so every
finger's label currently has nothing else on this sheet to connect to --
that's the intended state until the SoC sheet is added. Per explicit
user direction, 2026-07-19.
"""
import sys, uuid, csv
sys.path.insert(0, '.')
from schgen import Sheet, GRID

TI = "/home/administrator/projects/teacup-neo/hw/interposer_t41/teacup-interposer-t41.kicad_sym"
PWR = "/usr/share/kicad/symbols/power.kicad_sym"
PINOUT_CSV = "/home/administrator/projects/teacup-neo/hw/interposer_t41/pinout_288.csv"

def S(n):
    return round(n * GRID, 2)

s = Sheet()
s.ensure_symbol(TI, "DIMM-DDR4", "teacup-interposer-t41:DIMM-DDR4")
s.ensure_symbol(PWR, "GND", "power:GND")
s.ensure_symbol(PWR, "PWR_FLAG", "power:PWR_FLAG")

LABEL_ANGLE = {"right": 0, "left": 180, "up": 90, "down": 270}

J1 = "teacup-interposer-t41:DIMM-DDR4"
jx, jy = S(80), S(400)
s.place(J1, "J1", "DIMM-DDR4", jx, jy, 0,
        footprint="teacup-interposer-t41:DIMM-DDR4",
        ref_at=(jx, jy - S(155), 0), value_at=(jx, jy + S(155), 0))

rows = list(csv.DictReader(open(PINOUT_CSV)))
assert len(rows) == 288

for row in rows:
    num = row["finger"]
    net = row["carrier_net"]
    p = s.pin_pos(J1, jx, jy, 0, num)
    d = s.pin_dir(J1, num)
    if net == "GND":
        s.flag("GND", p, "D", d)
    else:
        s.label(net, p[0], p[1], LABEL_ANGLE[d], global_=True)

# PWR_FLAG for GND -- there's no SoC sheet yet to host one (that's where
# T31ZX's equivalent flags live), and ERC needs an explicit "trust this
# is driven" marker on GND since nothing on this sheet is a power-output
# pin. Same idiom as the T31ZX interposer's SoC sheet; move here alongside
# the SoC sheet's own flags once T41's pin assignment exists.
PWRFLAG = "power:PWR_FLAG"
gx, gy = S(60), S(390)
s.place(PWRFLAG, "#PWR1", "PWR_FLAG", gx, gy, 0)
gp = s.pin(PWRFLAG, gx, gy, 0, "1")
s.flag("GND", gp, "S", s.pin_dir(PWRFLAG, "1"))

out = s.render("DDR4 UDIMM-288 Card Edge (T41 interposer)", str(uuid.uuid4()), "/f3a4b5c6-0001-4000-8000-000000000001", "1", paper="A2")
open("/home/administrator/projects/teacup-neo/hw/interposer_t41/sheets/ddr4_edge.kicad_sch", "w").write(out)
print("wrote ddr4_edge.kicad_sch,", len(out), "bytes")
