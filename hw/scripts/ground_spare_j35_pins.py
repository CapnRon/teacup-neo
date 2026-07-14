"""Ground J35's 6 orphaned pads. J35's PCB footprint is still the old
PinHeader_2x13 (26 pads) from before J1 pins 283-288 were reassigned to
MSC1/J37 -- pads 20-25 (previously SPARE_P283-288) carry stale net names
with nothing else on those nets anymore. Rather than swap the whole
footprint down to 2x10 (disruptive, moves/resizes the part), tie those 6
now-unused pads to GND directly, per explicit user direction, 2026-07-14.
Nothing else on the board touched.

Run with the real KiCad 10.0.4 install (see build_pcb.py for why):
    LD_LIBRARY_PATH=/opt/kicad10/AppDir/shared/lib:/opt/kicad10/AppDir/usr/lib \
        /opt/kicad10/AppDir/bin/python3.11 ground_spare_j35_pins.py
"""
import pcbnew

BOARD_PATH = "/home/administrator/projects/teacup-neo/hw/teacup-carrier.kicad_pcb"
STALE_PADS = {"20", "21", "22", "23", "24", "25"}

board = pcbnew.LoadBoard(BOARD_PATH)

j35 = None
gnd_net = None
for fp in board.GetFootprints():
    if fp.GetReference() == "J35":
        j35 = fp
    for pad in fp.Pads():
        if pad.GetNetname() == "GND" and gnd_net is None:
            gnd_net = pad.GetNet()
if j35 is None or gnd_net is None:
    raise SystemExit("J35 or an existing GND net not found")

for pad in j35.Pads():
    if pad.GetNumber() in STALE_PADS:
        pad.SetNet(gnd_net)

pcbnew.SaveBoard(BOARD_PATH, board)
print(f"wrote {BOARD_PATH}")
for pad in j35.Pads():
    print(" pad", pad.GetNumber(), "->", pad.GetNetname())
