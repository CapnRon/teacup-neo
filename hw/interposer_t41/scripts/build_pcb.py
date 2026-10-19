"""Initial T41 interposer PCB -- J1 (DDR4 card edge) only, no SoC yet.
Same netlist-driven placement approach as the T31ZX interposer's own
build_pcb.py. Board outline is NOT drawn separately -- the DIMM-DDR4
footprint's own Edge.Cuts geometry (the real JEDEC UDIMM card outline,
notch + latch cutouts included) IS the board outline once J1 is placed
at the origin. Per explicit user direction, 2026-07-19.

Run with the real KiCad 10.0.4 install:
    LD_LIBRARY_PATH=/opt/kicad10/AppDir/shared/lib:/opt/kicad10/AppDir/usr/lib \
        /opt/kicad10/AppDir/bin/python3.11 build_pcb.py
"""
import re
import pcbnew

REPO = "/home/administrator/projects/teacup-neo/hw/interposer_t41"
NETLIST = "/tmp/interposer_t41.net"
OUT = f"{REPO}/teacup-interposer-t41.kicad_pcb"

def parse_fp_lib_table(path, kiprjmod):
    text = open(path).read()
    libs = {}
    for m in re.finditer(r'\(lib \(name "([^"]+)"\)\(type "[^"]*"\)\(uri "([^"]+)"\)', text):
        name, uri = m.group(1), m.group(2)
        uri = uri.replace("${KIPRJMOD}", kiprjmod)
        uri = uri.replace("${KICAD10_FOOTPRINT_DIR}", "/usr/share/kicad/footprints")
        libs[name] = uri
    return libs

LIBS = parse_fp_lib_table(f"{REPO}/fp-lib-table", REPO)

def paren_block(t, i):
    depth = 0; instr = False; start = i; n = len(t)
    while i < n:
        c = t[i]
        if c == '"' and t[i-1] != '\\':
            instr = not instr
        elif not instr:
            if c == '(': depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0: return t[start:i+1]
        i += 1
    raise ValueError("unterminated")

def parse_components(text):
    comps = {}
    i = text.find('(components')
    block = paren_block(text, i)
    for m in re.finditer(r'\(comp\s', block):
        cb = paren_block(block, m.start())
        ref_m = re.search(r'\(ref "([^"]+)"\)', cb)
        val_m = re.search(r'\(value "([^"]*)"\)', cb)
        fp_m = re.search(r'\(footprint "([^"]*)"\)', cb)
        if ref_m and fp_m:
            comps[ref_m.group(1)] = {
                "footprint": fp_m.group(1),
                "value": val_m.group(1) if val_m else "",
            }
    return comps

def parse_nets(text):
    nets = {}
    i = text.find('(nets')
    block = paren_block(text, i)
    for m in re.finditer(r'\(net\s', block):
        nb = paren_block(block, m.start())
        name_m = re.search(r'\(name "([^"]*)"\)', nb)
        name = name_m.group(1) if name_m else "?"
        pins = []
        for pm in re.finditer(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', nb):
            pins.append((pm.group(1), pm.group(2)))
        nets[name] = pins
    return nets

net_text = open(NETLIST).read()
components = parse_components(net_text)
nets = parse_nets(net_text)
print(f"parsed {len(components)} components, {len(nets)} nets")

# ---------------------------------------------------------------- board setup
board = pcbnew.CreateEmptyBoard()
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(4)  # matches the T31ZX interposer's stackup
ds.SetBoardThickness(pcbnew.FromMM(1.0))
# J1's own gold fingers are DESIGNED to sit at the physical board edge --
# that's how a card-edge connector works. KiCad's 0.5mm default copper-
# to-edge clearance would flag every one of those 288 pads. Matches the
# T31ZX interposer's own board, which has this same override.
ds.m_CopperEdgeClearance = pcbnew.FromMM(0.0)

def mm(v):
    return pcbnew.FromMM(v)

def load_fp(fp_id):
    lib, name = fp_id.split(":", 1)
    if lib not in LIBS:
        raise ValueError(f"library '{lib}' not in fp-lib-table")
    fp = pcbnew.FootprintLoad(LIBS[lib], name)
    if fp is None:
        raise ValueError(f"footprint '{name}' not found in {LIBS[lib]}")
    return fp

# J1 (DIMM-DDR4): placed at the origin, unrotated -- its own Edge.Cuts
# geometry becomes the board outline. Real UDIMM card, 133.35 x 31.25mm.
J1_X, J1_Y = 0.0, 0.0

# U11 (T41 QFN96, ~13.2x12.9mm courtyard) centered in the available
# component strip, roughly under the middle of the card -- same rough
# placement convention as T31ZX's own IC1.
U11_X, U11_Y = 0.0, -16.0

# Local support passives, clustered near U11 -- rough scatter, not a
# considered layout (matches the T31ZX interposer's own "rough first
# pass, user refines by hand" convention).
PASSIVE_POS = {
    "Y1": (-25.0, -8.0), "C77": (-20.0, -8.0), "C80": (-15.0, -8.0),
    "R24": (-10.0, -8.0), "R23": (-5.0, -8.0),
    "R16": (-25.0, -24.0), "R18": (-20.0, -24.0), "R20": (-15.0, -24.0), "C69": (-10.0, -24.0),
    "C43": (15.0, -6.0), "C44": (19.0, -6.0), "C45": (23.0, -6.0), "C46": (27.0, -6.0),
    "C47": (31.0, -6.0), "C48": (35.0, -6.0), "C49": (39.0, -6.0), "C50": (43.0, -6.0),
    "C24": (15.0, -26.0), "C25": (19.0, -26.0), "C26": (23.0, -26.0), "C27": (27.0, -26.0),
    "C51": (31.0, -26.0), "C52": (35.0, -26.0), "C53": (39.0, -26.0), "C54": (43.0, -26.0),
    "C55": (48.0, -6.0), "C56": (52.0, -6.0), "C57": (56.0, -6.0),
    "U7": (48.0, -22.0),
    "#PWR91": (10.0, -2.0), "#PWR92": (13.0, -2.0), "#PWR93": (16.0, -2.0), "#PWR94": (19.0, -2.0),
}

footprints = {}
load_errors = []
for ref, info in sorted(components.items()):
    try:
        fp = load_fp(info["footprint"])
    except Exception as e:
        load_errors.append((ref, info["footprint"], str(e)))
        continue
    fp.SetReference(ref)
    fp.SetValue(info["value"])
    footprints[ref] = fp

    if ref == "J1":
        fp.SetPosition(pcbnew.VECTOR2I(mm(J1_X), mm(J1_Y)))
    elif ref == "U11":
        fp.SetPosition(pcbnew.VECTOR2I(mm(U11_X), mm(U11_Y)))
    elif ref in PASSIVE_POS:
        x, y = PASSIVE_POS[ref]
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    else:
        print(f"WARNING: {ref} has no placement rule -- parked at (0,10)")
        fp.SetPosition(pcbnew.VECTOR2I(mm(0), mm(10)))
    board.Add(fp)

if load_errors:
    print(f"FOOTPRINT LOAD ERRORS ({len(load_errors)}):")
    for ref, fpid, err in load_errors:
        print(f"  {ref}: {fpid} -- {err}")

# ---------------------------------------------------------------- net assignment
net_assign_errors = []
for netname, pins in nets.items():
    if not pins:
        continue
    ninfo = pcbnew.NETINFO_ITEM(board, netname)
    board.Add(ninfo)
    for ref, pin in pins:
        fp = footprints.get(ref)
        if fp is None:
            continue
        matched = [p for p in fp.Pads() if p.GetNumber() == pin]
        if not matched:
            net_assign_errors.append((ref, pin, netname))
            continue
        for pad in matched:
            pad.SetNet(ninfo)

if net_assign_errors:
    print(f"NET ASSIGNMENT ERRORS ({len(net_assign_errors)}), first 20:")
    for ref, pin, netname in net_assign_errors[:20]:
        print(f"  {ref} pin {pin} -> {netname}: pad not found")

pcbnew.SaveBoard(OUT, board)
print(f"wrote {OUT}")
print(f"footprints placed: {len(footprints)} / {len(components)}")
print(f"nets created: {board.GetNetCount()}")
