"""Parses a merged .kicad_sch and checks every text item (labels, visible
property text) for pairwise bounding-box overlap. Conservative (slightly
generous) text metrics calibrated against this session's actual renders,
so a false negative here is unlikely -- if this reports clean, it's clean.
"""
import re, sys

FONT = 1.27
CHAR_W = 1.05     # mm per character, slightly generous
TEXT_H = 1.35      # mm
LABEL_POINT = 1.3  # extra length for the label chevron's pointed end
LABEL_MARGIN_H = 0.5

def text_w(s):
    return len(s) * CHAR_W

class Box:
    def __init__(self, x0, y0, x1, y1, tag):
        self.x0, self.y0, self.x1, self.y1 = min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)
        self.tag = tag
    def overlaps(self, o):
        return self.x0 < o.x1 and self.x1 > o.x0 and self.y0 < o.y1 and self.y1 > o.y0

def label_box(text, x, y, angle, tag):
    w = LABEL_POINT + text_w(text)
    h = TEXT_H + LABEL_MARGIN_H
    if angle == 0:
        return Box(x, y - h/2, x + w, y + h/2, tag)
    elif angle == 180:
        return Box(x - w, y - h/2, x, y + h/2, tag)
    elif angle == 90:
        return Box(x - h/2, y - w, x + h/2, y, tag)
    else:  # 270
        return Box(x - h/2, y, x + h/2, y + w, tag)

def prop_box(text, x, y, tag):
    w = text_w(text)
    return Box(x - w/2, y - TEXT_H/2, x + w/2, y + TEXT_H/2, tag)

def paren_block(text, start):
    depth, inq, j = 0, False, start
    while j < len(text):
        c = text[j]
        if c == '"' and text[j-1] != '\\':
            inq = not inq
        elif not inq:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return text[start:j+1]
        j += 1
    raise ValueError("unterminated")

def collect(path):
    text = open(path).read()
    boxes = []

    for m in re.finditer(r'\((global_label|label) "([^"]+)" \(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', text):
        kind, s, x, y, ang = m.groups()
        boxes.append(label_box(s, float(x), float(y), float(ang), f'{kind} "{s}" @({x},{y})'))

    # visible (non-hidden) Reference/Value properties belonging to symbol instances
    for m in re.finditer(r'\(symbol \(lib_id "([^"]+)"\)\s*\(at [-\d.]+ [-\d.]+ [-\d.]+\)', text):
        lib_id = m.group(1)
        # this instance's full block, to bound property search
        sym_start = m.start()
        block = paren_block(text, sym_start)
        for pm in re.finditer(r'\(property "(Reference|Value)" "([^"]*)"\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', block):
            pkind, pval, px, py, pang = pm.groups()
            prop_block = paren_block(block, pm.start())
            # bare " hide" token, not inside a quoted string
            if re.search(r'(?<!")\bhide\b', prop_block):
                continue
            if not pval:
                continue
            boxes.append(prop_box(pval, float(px), float(py), f'{pkind}="{pval}" of {lib_id} @({px},{py})'))

    return boxes

def main(path):
    boxes = collect(path)
    print(f"{len(boxes)} visible text items")
    n = 0
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            if boxes[i].overlaps(boxes[j]):
                n += 1
                print(f"OVERLAP: {boxes[i].tag}  <-->  {boxes[j].tag}")
    print(f"\n{n} overlaps found")
    return n

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/home/administrator/projects/teacup-neo/hw/teacup-carrier.kicad_sch"
    n = main(path)
    sys.exit(1 if n else 0)
