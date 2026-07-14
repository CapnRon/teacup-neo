"""Upgrade J38 (external amplifier tap) to a 3-pin header so an external mic
can also be tapped -- pin1=HPOUTL, pin2=GND (middle, acting as an isolation
strip), pin3=MICLP. Same position/orientation as the existing 2-pin part;
swaps PinHeader_1x02 for PinHeader_1x03 (KiCad doesn't support resizing a
header's pad count in place via scripting, so the old footprint is removed
and a new one added at the identical anchor). Nothing else on the board
touched or moved. Per explicit user direction, 2026-07-14.

Run with the real KiCad 10.0.4 install (see build_pcb.py for why):
    LD_LIBRARY_PATH=/opt/kicad10/AppDir/shared/lib:/opt/kicad10/AppDir/usr/lib \
        /opt/kicad10/AppDir/bin/python3.11 upgrade_j38_3pin_real_board.py
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

old_j38 = None
for fp in board.GetFootprints():
    if fp.GetReference() == "J38":
        old_j38 = fp
        break
if old_j38 is None:
    raise SystemExit("J38 not found on this board")
if str(old_j38.GetFPID().GetLibItemName()) != "PinHeader_1x02_P2.54mm_Vertical":
    raise SystemExit(f"J38 is not the expected 2-pin part ({old_j38.GetFPID().GetLibItemName()}) -- aborting")

pos = old_j38.GetPosition()
orient = old_j38.GetOrientationDegrees()
board.Remove(old_j38)

fp = pcbnew.FootprintLoad(LIBS["Connector_PinHeader_2.54mm"], "PinHeader_1x03_P2.54mm_Vertical")
fp.SetReference("J38")
fp.SetValue("AMP_MIC_TAP")
fp.SetOrientationDegrees(orient)
fp.SetPosition(pos)
board.Add(fp)

pin_to_net = {"1": "HPOUTL", "2": "GND", "3": "MICLP"}
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

# Update the "AMP" silkscreen label in place (text + recentered over the
# now-longer 3-pin body), rather than adding a second stray text object.
bb = fp.GetBoundingBox()
label_x = pcbnew.ToMM(bb.GetCenter().x)
label_y = pcbnew.ToMM(bb.GetTop()) - 2.0
updated = False
for d in board.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetText() == "AMP":
        d.SetText("AMP/MIC")
        d.SetPosition(pcbnew.VECTOR2I(mm(label_x), mm(label_y)))
        updated = True
        break
if not updated:
    print("WARNING: existing 'AMP' silkscreen text not found -- not adding a new one")

pcbnew.SaveBoard(BOARD_PATH, board)
print(f"wrote {BOARD_PATH}")
for pad in fp.Pads():
    print(" pad", pad.GetNumber(), "->", pad.GetNetname())
