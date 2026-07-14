"""Fix up MSC1 net assignment on the real board: J1 pins 283-288 still carry
the old SPARE_P283-288 net names (this board predates the MSC1 schematic
change), and J37 (just added) has its signal pads unassigned since no
existing pad had the new net names to copy from. Creates the 6 new
MSC1_* nets and assigns them to both J1's pads and J37's pads. Nothing
else on the board touched. Per explicit user direction, 2026-07-14.

Run with the real KiCad 10.0.4 install (see build_pcb.py for why):
    LD_LIBRARY_PATH=/opt/kicad10/AppDir/shared/lib:/opt/kicad10/AppDir/usr/lib \
        /opt/kicad10/AppDir/bin/python3.11 fix_msc1_nets_real_board.py
"""
import pcbnew

BOARD_PATH = "/home/administrator/projects/teacup-neo/hw/teacup-carrier.kicad_pcb"

PIN_NET = {
    "283": "MSC1_CLK", "284": "MSC1_CMD", "285": "MSC1_D0",
    "286": "MSC1_D1", "287": "MSC1_D2", "288": "MSC1_D3_CD",
}
J37_PIN_NET = {
    "2": "MSC1_CLK", "3": "MSC1_CMD", "4": "MSC1_D0",
    "5": "MSC1_D1", "6": "MSC1_D2", "7": "MSC1_D3_CD",
}

board = pcbnew.LoadBoard(BOARD_PATH)

footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
j1 = footprints["J1"]
j37 = footprints["J37"]

net_objs = {}
for netname in set(PIN_NET.values()):
    ninfo = pcbnew.NETINFO_ITEM(board, netname)
    board.Add(ninfo)
    net_objs[netname] = ninfo

for pad in j1.Pads():
    netname = PIN_NET.get(pad.GetNumber())
    if netname:
        pad.SetNet(net_objs[netname])

for pad in j37.Pads():
    netname = J37_PIN_NET.get(pad.GetNumber())
    if netname:
        pad.SetNet(net_objs[netname])

pcbnew.SaveBoard(BOARD_PATH, board)
print(f"wrote {BOARD_PATH}")
print("J1 283-288:")
for pad in j1.Pads():
    if pad.GetNumber() in PIN_NET:
        print(" ", pad.GetNumber(), "->", pad.GetNetname())
print("J37:")
for pad in j37.Pads():
    print(" ", pad.GetNumber(), "->", pad.GetNetname())
