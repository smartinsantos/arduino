"""RFID music box enclosure (phase 3). Writes the STL files next to this script.

Run:   python3 make_box.py
Needs: pip install manifold3d trimesh numpy

All sizes are in millimetres. Change a number in PARAMETERS and run it again: every
part that depends on it moves with it. `check_fit()` at the bottom fails loudly if a
change makes the parts inside the box collide.

Coordinates: X runs left to right (190 mm), Y from the front edge (the child's side)
to the back (140 mm), Z up from the table. The lid is modelled where it sits on the
box and flipped upside down only when it is written out, ready to print.
"""

import os

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold, set_min_circular_angle, set_min_circular_edge_length

set_min_circular_angle(4)
set_min_circular_edge_length(0.4)

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- PARAMETERS

W, D = 190.0, 140.0       # box outside, X by Y
CORNER_R = 10.0           # rounded outside corners
WALL = 2.4                # side walls
FLOOR = 2.4               # base floor
INSIDE_H = 50.0           # floor to the lid's underside
BASE_H = FLOOR + INSIDE_H
LID_T = 3.0               # lid plate
FIT = 0.3                 # gap between the lid's lip and the base walls, per side
LIP_T, LIP_H = 1.6, 4.0   # lip under the lid that keys it into the base

# Corner pillars in the base: an M3 heat-set insert at the top of each, the lid screws into them.
PILLAR_D = 10.0
PILLAR_INSET = 8.0
INSERT_HOLE_D, INSERT_HOLE_DEPTH = 4.0, 7.0   # ruthex M3x5.7: 4.0 mm hole
SCREW_CLEAR_D = 3.4                           # M3 clearance through the lid

PILOT_M3 = 2.6    # M3 screw cuts its own thread in a 2.6 mm hole
PILOT_M25 = 2.2   # M2.5 screw in a 2.2 mm hole

# Arduino Uno: USB-B jack pokes through the left wall, flush with the outside.
UNO_W, UNO_D = 68.6, 53.3
UNO_USB_OUT = 6.2                       # jack sticks out past the board edge
UNO_X, UNO_Y = UNO_USB_OUT, 45.0        # board's lower-left corner in the box
UNO_HOLES = [(13.97, 2.54), (15.24, 50.8), (66.04, 7.62), (66.04, 35.56)]
UNO_POST_H, UNO_POST_D = 6.0, 6.5
UNO_USB_Y = (32.0, 44.0)                # jack edges, measured on the board
UNO_USB_H = 11.0
UNO_STACK_H = 36.0                      # Uno + proto shield + DFPlayer + plugs, above the board

# Lid layout (centres, in box X/Y).
BUTTON_Y = 31.0
BUTTON_XS = (40.0, 78.0, 116.0)        # previous, play/pause, next
BUTTON_HOLE_D = 24.2                    # 24 mm snap-in arcade button
BUTTON_PANEL_T = 2.0                    # the snap clips want a thin panel: counterbored to this
BUTTON_RECESS_D = 31.0
BUTTON_DEPTH = 35.0                     # button + microswitch + plug under the lid

READER_C = (55.0, 72.0)                 # RC522 board centre; its pin header points to +X
READER_W, READER_D = 60.0, 39.5
READER_SKIN = 1.5                       # plastic left over the reader's antenna
READER_DEPTH = 6.0                      # board + parts under the lid (pins point sideways)

SPEAKER_C = (146.0, 90.0)               # Dayton Audio PC68-4, 2.5", square steel frame
SPEAKER_FRAME = 68.1                    # frame, side to side
SPEAKER_DEPTH = 37.1                    # front of the frame to the back of the magnet
SPEAKER_BOLT_CIRCLE = 73.4              # 4 holes, on the diagonals of the frame
SPEAKER_GAP = 0.4
SPEAKER_RIM_H = 5.0                     # square rim under the lid that locates the frame
GRILLE_D = 58.0                         # cone + surround
GRILLE_HOLE_D, GRILLE_PITCH = 3.0, 5.0

LCD_C = (65.0, 117.0)                   # LCD1602 + I2C backpack, PCB 80 x 36, pins at the back
LCD_PCB = (80.0, 36.0)
LCD_HOLES = (75.0, 31.0)                # hole spacing
LCD_BEZEL = (72.5, 26.0)                # pocket for the metal bezel (bezel is about 71 x 24)
LCD_WINDOW = (66.0, 18.0)               # visible glass
LCD_POCKET_DEPTH = 1.5
LCD_BEZEL_H = 7.0                       # bezel height above the PCB; short standoffs are fixed with washers
LCD_DEPTH = 9.0                         # bezel pocket to the back of the PCB
LCD_BACKPACK = (46.0, 22.0, 24.0)       # backpack + plug behind the pin row: width, depth, height under the lid
LCD_STANDOFF_D = 5.5

KNOB_C = (162.0, 31.0)                  # WH148 potentiometer, M7 thread
POT_HOLE_D = 7.4
POT_DEPTH = 26.0
KNOB_D, KNOB_H = 36.0, 18.0             # printed knob, glued over the pot's own 15 x 17 mm knob
KNOB_POCKET_D, KNOB_POCKET_H = 15.6, 15.0

ENGRAVE = 0.8                           # icon depth on the lid's top

# ---------------------------------------------------------------- helpers


def rrect(w, d, r):
    """Rounded rectangle centred on the origin."""
    r = max(min(r, w / 2 - 0.01, d / 2 - 0.01), 0.01)
    return CrossSection.square([w - 2 * r, d - 2 * r], center=True).offset(r, JoinType.Round)


def block(x, y, z, w, d, h):
    return Manifold.cube([w, d, h]).translate([x, y, z])


def block_c(cx, cy, z, w, d, h):
    return Manifold.cube([w, d, h]).translate([cx - w / 2, cy - d / 2, z])


def cyl(cx, cy, z, dia, h):
    return Manifold.cylinder(h, dia / 2).translate([cx, cy, z])


def poly(points):
    return CrossSection([points])


def union(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out + p
    return out


def pillar_centres():
    i = PILLAR_INSET
    return [(i, i), (W - i, i), (i, D - i), (W - i, D - i)]


# ---------------------------------------------------------------- icons (2D, centred on the origin)


def tri(x0, x1, h):
    """Triangle pointing from x0 to x1, h tall."""
    return poly([(x0, -h / 2), (x1, 0), (x0, h / 2)]) if x1 > x0 else poly([(x0, -h / 2), (x0, h / 2), (x1, 0)])


def icon_prev():
    return union2([CrossSection.square([1.6, 8], center=True).translate([-6.2, 0]), tri(-1.0, -5.4, 8), tri(4.4, 0.0, 8)])


def icon_next():
    return icon_prev().mirror([1, 0])


def icon_play_pause():
    return union2([tri(-6.5, -0.5, 8), CrossSection.square([1.6, 8], center=True).translate([2.6, 0]),
                   CrossSection.square([1.6, 8], center=True).translate([5.8, 0])])


def arc(r_out, r_in, half_angle_deg):
    ring = CrossSection.circle(r_out) - CrossSection.circle(r_in)
    a = np.radians(half_angle_deg)
    big = r_out * 2
    wedge = poly([(0, 0), (big * np.cos(-a), big * np.sin(-a)), (big, 0), (big * np.cos(a), big * np.sin(a))])
    return ring ^ wedge


def icon_waves(n=3, start=4.0, step=3.6, width=1.3, half_angle=45):
    return union2([arc(start + i * step + width, start + i * step, half_angle) for i in range(n)])


def icon_tap():
    # A card leaning into radio waves.
    card = rrect(13, 18, 2) - rrect(10.6, 15.6, 1)
    return union2([card.rotate(-15).translate([-7, 0]), icon_waves().translate([1, 0])])


def union2(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out + p
    return out


def engrave(cs, cx, cy):
    """Cut a 2D icon into the lid's top face."""
    cs = cs.simplify(0.02)  # drop near-duplicate points so the cut stays watertight
    return cs.translate([cx, cy]).extrude(ENGRAVE + 1).translate([0, 0, LID_T - ENGRAVE])


# ---------------------------------------------------------------- parts


def base():
    outline = rrect(W, D, CORNER_R).translate([W / 2, D / 2])
    outer = outline.extrude(BASE_H)
    cavity = rrect(W - 2 * WALL, D - 2 * WALL, CORNER_R - WALL).translate([W / 2, D / 2]).extrude(BASE_H).translate([0, 0, FLOOR])
    b = outer - cavity

    # Corner pillars, clipped to the rounded outline, with an insert hole on top.
    pillars = union([cyl(x, y, 0, PILLAR_D, BASE_H) for x, y in pillar_centres()]) ^ outer
    b = b + pillars
    for x, y in pillar_centres():
        b = b - cyl(x, y, BASE_H - INSERT_HOLE_DEPTH, INSERT_HOLE_D, INSERT_HOLE_DEPTH + 1)

    # Uno posts.
    for hx, hy in UNO_HOLES:
        x, y = UNO_X + hx, UNO_Y + hy
        b = b + cyl(x, y, FLOOR - 0.1, UNO_POST_D, UNO_POST_H + 0.1)
        b = b - cyl(x, y, FLOOR, PILOT_M3, UNO_POST_H + 1)

    # USB-B jack opening in the left wall, 1 mm bigger than the jack all round.
    pcb_top = FLOOR + UNO_POST_H + 1.6
    y0, y1 = UNO_Y + UNO_USB_Y[0] - 1, UNO_Y + UNO_USB_Y[1] + 1
    b = b - block(-1, y0, pcb_top - 1, WALL + 3, y1 - y0, UNO_USB_H + 2)

    # Shallow pads underneath for stick-on rubber feet (10 mm).
    for x, y in [(20, 20), (W - 20, 20), (20, D - 20), (W - 20, D - 20)]:
        b = b - cyl(x, y, -1, 11, 1.6)
    return b


def lid():
    plate = rrect(W, D, CORNER_R).translate([W / 2, D / 2]).extrude(LID_T)

    lip_o = rrect(W - 2 * (WALL + FIT), D - 2 * (WALL + FIT), CORNER_R - WALL - FIT)
    lip_i = rrect(W - 2 * (WALL + FIT + LIP_T), D - 2 * (WALL + FIT + LIP_T), CORNER_R - WALL - FIT - LIP_T)
    lip = (lip_o - lip_i).translate([W / 2, D / 2]).extrude(LIP_H).translate([0, 0, -LIP_H])
    for x, y in pillar_centres():
        lip = lip - cyl(x, y, -LIP_H - 1, PILLAR_D + 1.2, LIP_H + 1.1)
    l = plate + lip

    # Corner screws.
    for x, y in pillar_centres():
        l = l - cyl(x, y, -1, SCREW_CLEAR_D, LID_T + 2)

    # Buttons: through hole, counterbored from below so the snap clips see a thin panel.
    for x in BUTTON_XS:
        l = l - cyl(x, BUTTON_Y, -1, BUTTON_HOLE_D, LID_T + 2)
        l = l - cyl(x, BUTTON_Y, -1, BUTTON_RECESS_D, 1 + LID_T - BUTTON_PANEL_T)

    # Reader: pocket from below leaves a thin skin; a low rim, open on the pin side, holds it.
    rx, ry = READER_C
    pw, pd = READER_W + 1.0, READER_D + 1.0
    l = l - block_c(rx, ry, -1, pw, pd, 1 + LID_T - READER_SKIN)
    rim = block_c(rx, ry, -4, pw + 3.2, pd + 3.2, 4) - block_c(rx, ry, -5, pw, pd, 6)
    rim = rim - block(rx + pw / 2 - 1, ry - pd / 2 - 5, -5, 10, pd + 10, 6)  # pin side open
    l = l + rim

    # Speaker: round grille through the plate, a square rim that locates the frame, and four
    # M3 screws through the lid into the frame's corner holes (nuts on the back of the frame).
    sx, sy = SPEAKER_C
    holes = []
    row = 0
    y = sy - GRILLE_D / 2
    while y <= sy + GRILLE_D / 2:
        off = (GRILLE_PITCH / 2) if row % 2 else 0
        x = sx - GRILLE_D / 2 + off
        while x <= sx + GRILLE_D / 2:
            holes.append(CrossSection.circle(GRILLE_HOLE_D / 2).translate([x, y]))
            x += GRILLE_PITCH
        y += GRILLE_PITCH * 0.866
        row += 1
    grille = union2(holes) ^ CrossSection.circle(GRILLE_D / 2 - GRILLE_HOLE_D / 2).translate([sx, sy])
    l = l - grille.extrude(LID_T + 2).translate([0, 0, -1])
    inner = SPEAKER_FRAME + 2 * SPEAKER_GAP
    srim = block_c(sx, sy, -SPEAKER_RIM_H, inner + 3.2, inner + 3.2, SPEAKER_RIM_H) - block_c(sx, sy, -SPEAKER_RIM_H - 1, inner, inner, SPEAKER_RIM_H + 2)
    srim = srim - block_c(sx + inner / 2 + 1.6, sy, -SPEAKER_RIM_H - 1, 6, 14, SPEAKER_RIM_H - 1)  # gap for the wires
    l = l + srim
    r = SPEAKER_BOLT_CIRCLE / 2
    for ax, ay in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        l = l - cyl(sx + ax * r / 2 ** 0.5, sy + ay * r / 2 ** 0.5, -1, SCREW_CLEAR_D, LID_T + 2)

    # LCD: window, bezel pocket, four standoffs.
    cx, cy = LCD_C
    l = l - block_c(cx, cy, -1, LCD_WINDOW[0], LCD_WINDOW[1], LID_T + 2)
    l = l - block_c(cx, cy, -1, LCD_BEZEL[0], LCD_BEZEL[1], 1 + LCD_POCKET_DEPTH)
    standoff = LCD_BEZEL_H - LCD_POCKET_DEPTH
    for dx in (-1, 1):
        for dy in (-1, 1):
            x, y = cx + dx * LCD_HOLES[0] / 2, cy + dy * LCD_HOLES[1] / 2
            l = l + cyl(x, y, -standoff, LCD_STANDOFF_D, standoff + 0.1)
            l = l - cyl(x, y, -standoff - 1, PILOT_M25, standoff + 1 + LID_T - 1)

    # Volume knob.
    l = l - cyl(KNOB_C[0], KNOB_C[1], -1, POT_HOLE_D, LID_T + 2)

    # Icons on top.
    icons = [
        (icon_prev(), BUTTON_XS[0], BUTTON_Y - 21),
        (icon_play_pause(), BUTTON_XS[1], BUTTON_Y - 21),
        (icon_next(), BUTTON_XS[2], BUTTON_Y - 21),
        (icon_tap().scale([1.3, 1.3]), READER_C[0] - 4, READER_C[1]),
    ]
    tap_ring = rrect(READER_W + 10, READER_D + 10, 6) - rrect(READER_W + 7.6, READER_D + 7.6, 4.8)
    icons.append((tap_ring, READER_C[0], READER_C[1]))
    for cs, x, y in icons:
        l = l - engrave(cs, x, y)
    return l


def knob():
    body = Manifold.cylinder(KNOB_H - 2, KNOB_D / 2) + Manifold.cylinder(2, KNOB_D / 2, KNOB_D / 2 - 2).translate([0, 0, KNOB_H - 2])
    for i in range(16):  # grip bumps around the edge
        a = np.radians(i * 360 / 16)
        body = body + Manifold.cylinder(KNOB_H - 3, 2.0).translate([np.cos(a) * KNOB_D / 2, np.sin(a) * KNOB_D / 2, 0])
    body = body - Manifold.cylinder(KNOB_POCKET_H + 1, KNOB_POCKET_D / 2).translate([0, 0, -1])
    pointer = block(-1.2, KNOB_D / 2 - 11, KNOB_H - 0.8, 2.4, 9, 2)  # line on top
    return body - pointer


def fit_test():
    """A small plate with one of each critical hole, to check fits before the big prints."""
    p = rrect(90, 44, 4).translate([45, 22]).extrude(LID_T)
    p = p - cyl(18, 22, -1, BUTTON_HOLE_D, LID_T + 2)
    p = p - cyl(18, 22, BUTTON_PANEL_T, BUTTON_RECESS_D, LID_T)  # recess on top here, so it prints without bridges
    p = p - cyl(42, 22, -1, POT_HOLE_D, LID_T + 2)
    p = p + cyl(56, 12, LID_T - 0.1, 8, 8.1)
    p = p - cyl(56, 12, LID_T + 8 - INSERT_HOLE_DEPTH, INSERT_HOLE_D, INSERT_HOLE_DEPTH + 1)
    p = p + cyl(56, 32, LID_T - 0.1, 6.5, 6.1)
    p = p - cyl(56, 32, LID_T, PILOT_M3, 7)
    p = p + cyl(68, 32, LID_T - 0.1, LCD_STANDOFF_D, 5.6)
    p = p - cyl(68, 32, LID_T, PILOT_M25, 6)
    p = p - block_c(80, 15, -1, 14, 13, LID_T + 2)  # USB-B opening
    return p


# ---------------------------------------------------------------- stand-ins for the electronics (fit check and pictures)


def lid_hangers():
    """What hangs under the lid, in box coordinates."""
    z0 = BASE_H
    parts = {}
    parts["buttons"] = union([cyl(x, BUTTON_Y, z0 - BUTTON_DEPTH, 24, BUTTON_DEPTH) for x in BUTTON_XS])
    parts["reader"] = block_c(READER_C[0], READER_C[1], z0 - READER_DEPTH, READER_W, READER_D, READER_DEPTH)
    parts["speaker"] = block_c(SPEAKER_C[0], SPEAKER_C[1], z0 - SPEAKER_DEPTH - 1, SPEAKER_FRAME + 4, SPEAKER_FRAME + 4, SPEAKER_DEPTH + 1)
    lcd = block_c(LCD_C[0], LCD_C[1], z0 - LCD_DEPTH, LCD_PCB[0], LCD_PCB[1], LCD_DEPTH)
    bw, bd, bh = LCD_BACKPACK
    lcd = lcd + block(LCD_C[0] - LCD_PCB[0] / 2 + 4, LCD_C[1] + LCD_PCB[1] / 2 - bd, z0 - bh, bw, bd, bh)
    parts["lcd"] = lcd
    parts["pot"] = cyl(KNOB_C[0], KNOB_C[1], z0 - POT_DEPTH, 18, POT_DEPTH)
    return parts


def base_stuff():
    z = FLOOR + UNO_POST_H
    return {"uno stack": block(UNO_X, UNO_Y, z, UNO_W, UNO_D, 1.6 + UNO_STACK_H)}


def check_fit():
    hang, low = lid_hangers(), base_stuff()
    for hn, h in hang.items():
        for ln, b in low.items():
            v = (h ^ b).volume()
            assert v < 1e-6, f"{hn} hits {ln} ({v:.0f} mm3): move it or raise INSIDE_H"
        assert h.bounding_box()[2] > FLOOR + 3, f"{hn} reaches the floor"
    names = list(hang)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = (hang[a] ^ hang[b]).volume()
            assert v < 1e-6, f"{a} hits {b}"
    print("fit check: OK")


# ---------------------------------------------------------------- output


def save(m, name):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts))
    path = os.path.join(OUT, name)
    t.export(path)
    bb = t.bounds
    print(f"{name:22s} {bb[1][0]-bb[0][0]:6.1f} x {bb[1][1]-bb[0][1]:6.1f} x {bb[1][2]-bb[0][2]:5.1f} mm  {len(t.faces):6d} triangles")


def print_ready_lid():
    """Upside down, top face on the bed."""
    l = lid().rotate([180, 0, 0])
    return l.translate([0, 0, -l.bounding_box()[2]])


if __name__ == "__main__":
    check_fit()
    save(base(), "base.stl")
    save(print_ready_lid(), "lid.stl")
    save(knob(), "knob.stl")
    save(fit_test(), "fit_test.stl")
