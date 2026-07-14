"""Add the new J38 (external amplifier tap) footprint to the real board --
schematic-only until now (build_io.py). Placed in the clear gap just above
J6 (the audio jack it taps), nothing else on the board touched or moved.
Per explicit user direction, 2026-07-14.

Run with the real KiCad 10.0.4 install (see build_pcb.py for why):
    LD_LIBRARY_PATH=/opt/kicad10/AppDir/shared/lib:/opt/kicad10/AppDir/usr/lib \
        /opt/kicad10/AppDir/bin/python3.11 add_j38_real_board.py
"""
import re
import pcbnew

HW = "/home/administrator/projects/teacup-neo/hw"
BOARD_PATH = f"{HW}/teacup-carrier.kicad_pcb"


def mm(v):
    return pcbnew.FromMM(v)


def parse_fp_lib_table(path):
    text = open(path).read()
    libs = {}
    for m in re.finditer(r'\(lib \(name "([^"]+)"\)\(type "[^"]*"\)\(uri "([^"]+)"\)', text):
        name, uri = m.group(1), m.group(2)
        libs[name] = uri.replace("${KIPRJMOD}", HW)
    return libs


LIBS = parse_fp_lib_table(f"{HW}/fp-lib-table")

board = pcbnew.LoadBoard(BOARD_PATH)
if any(fp.GetReference() == "J38" for fp in board.GetFootprints()):
    raise SystemExit("J38 already on this board -- not adding a duplicate")

fp = pcbnew.FootprintLoad(LIBS["Connector_PinHeader_2.54mm"], "PinHeader_1x02_P2.54mm_Vertical")
fp.SetReference("J38")
fp.SetValue("AMP_TAP")
fp.SetOrientationDegrees(90)
fp.SetPosition(pcbnew.VECTOR2I(mm(199.0), mm(118.0)))
board.Add(fp)

pin_to_net = {"1": "HPOUTL", "2": "GND"}
for pad in fp.Pads():
    netname = pin_to_net.get(pad.GetNumber())
    if netname is None:
        continue
    ninfo = None
    for other_fp in board.GetFootprints():
        if other_fp.GetReference() == "J38":
            continue
        for other_pad in other_fp.Pads():
            if other_pad.GetNetname() == netname:
                ninfo = other_pad.GetNet()
                break
        if ninfo is not None:
            break
    if ninfo is None:
        print(f"WARNING: no existing pad found on net {netname} to copy net info from")
        continue
    pad.SetNet(ninfo)

# "AMP" silkscreen label, matching every other header's style.
bb = fp.GetBoundingBox()
label_x = pcbnew.ToMM(bb.GetCenter().x)
label_y = pcbnew.ToMM(bb.GetTop()) - 2.0
t = pcbnew.PCB_TEXT(board)
t.SetText("AMP")
t.SetPosition(pcbnew.VECTOR2I(mm(label_x), mm(label_y)))
t.SetLayer(pcbnew.F_SilkS)
size = 1.4
t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
t.SetTextThickness(mm(size * 0.15))
board.Add(t)

pcbnew.SaveBoard(BOARD_PATH, board)
print(f"wrote {BOARD_PATH}")
for pad in fp.Pads():
    print(" pad", pad.GetNumber(), "->", pad.GetNetname())
