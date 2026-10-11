"""A nail, built from the dimensions a standard states for it.

Every nail of this repository, imperial and metric, is this one script with
different parameters: 'imperial.j2' and 'metric.j2' say what the standard sizes
are, and this says what a nail of a given size looks like. Nothing here is a
table.

The frame is the one the interfaces in 'partcad.yaml' are placed in:

* the nail's axis is Z, and the point is at the bottom;
* z = 0 is the plane that is flush with the surface once the nail is driven
  home - the underside of a flat head, the top of every other head;
* so the head is above z = 0 for a flat head and below it for the others, and
  the tip is at z = -L, where L is how far the nail goes in.

ASTM F1667 measures a nail with a flat head "from under the head", and every
other nail overall (its section 8). That is why 'length' comes with 'measured':
the two coincide everywhere except on a flat head measured overall, which is
the cooler nail, and there the head's own thickness is taken off.
"""

import math

from build123d import Align, Axis, Cone, Cylinder, Face, Pos, Shell, Solid, Sphere, Vector, Wire, extrude, revolve

# What PartCAD hands this script, and what it builds when nothing is handed: a
# 16d common nail. Lengths are millimetres, as everywhere in PartCAD;
# 'imperial.yaml' converts the standard's inches before they get here.
d = 4.1148  # shank diameter: the wire, before any deformation is rolled in
length = 88.9  # as the standard states it - see 'measured'
measured = "under-head"  # "under-head" or "overall"
head = "flat"  # flat | countersunk | casing | brad
head_d = 8.7376  # head diameter; 0 means 2 * d, the head EN 1995-1-1 assumes
shank = "smooth"  # smooth | ring | screw
point = "diamond"  # diamond | long-diamond | needle | blunt | chisel
coating = "bright"  # what the nail is finished with; it changes no geometry
material = "//pub/std/manufacturing/material/metal:steel-1018"  # nor does this

_C, _MIN = Align.CENTER, Align.MIN

r = d / 2.0
head_r = (head_d if head_d > 0 else 2.0 * d) / 2.0

# The thickness of a flat head. No table in ASTM F1667 or FF-N-105B states one,
# so it is a proportion: about a third of the wire, which is what a common nail's
# head is, and never thinner than a sheet of paper's worth of steel. The same
# formula is in the 'implements' of every part (the head port sits on it), so the
# two cannot disagree as long as this line and that one change together.
flat_t = max(0.4, 0.35 * d)

# How far the nail goes in: from z = 0 to the tip.
L = length - (flat_t if head == "flat" and measured == "overall" else 0.0)
z_tip = -L

# The point, by how long it is in diameters of the wire.
POINT_LENGTH = {
    "diamond": 1.4,
    "long-diamond": 2.4,
    "needle": 2.6,
    "blunt": 1.0,
    "chisel": 1.2,
}
p = POINT_LENGTH[point] * d
z_point_top = z_tip + p


def polygon_face(points):
    return Face(Wire.make_polygon([Vector(*xyz) for xyz in points], close=True))


def pyramid(apex_z, top_z, half_width):
    """A square pyramid standing on its apex, its top a square 'half_width' wide."""
    apex = (0.0, 0.0, apex_z)
    w = half_width
    corners = [(w, w, top_z), (-w, w, top_z), (-w, -w, top_z), (w, -w, top_z)]
    faces = [polygon_face(corners)]
    for index in range(4):
        faces.append(polygon_face([apex, corners[index], corners[(index + 1) % 4]]))
    return Solid(Shell(faces))


def build_point():
    """The sharp end, from the tip up to where the shank is round again.

    A diamond point is four facets cut into round wire, so it is the wire
    intersected with a square pyramid. The pyramid is a few percent wider than
    the wire where the point ends, so that its facets cut the cylinder rather
    than graze it - a facet tangent to the cylinder is a degenerate edge for the
    kernel, and real facets do run out a little short of the full diameter.
    """
    wire = Pos(0, 0, z_tip) * Cylinder(r, p, align=(_C, _C, _MIN))
    widen = 1.04
    if point in ("diamond", "long-diamond"):
        return wire & pyramid(z_tip, z_point_top, widen * r)
    if point == "blunt":
        # A diamond whose apex would have been a third of the point below the
        # tip: what is left at the tip is a small square flat.
        virtual_apex = z_tip - p / 3.0
        slope = widen * r / (z_point_top - virtual_apex)
        return wire & pyramid(virtual_apex, z_point_top, slope * (z_point_top - virtual_apex))
    if point == "needle":
        return Pos(0, 0, z_tip) * Cone(0.0, r, p, align=(_C, _C, _MIN))
    if point == "chisel":
        wedge = polygon_face([(-widen * r, 0.0, z_point_top), (widen * r, 0.0, z_point_top), (0.0, 0.0, z_tip)])
        return wire & extrude(wedge, amount=1.5 * r, both=True)
    raise ValueError("unknown point: %s" % point)


def build_shank():
    """The wire from the top of the point to z = 0, deformed where 'shank' says.

    A ring or screw shank is deformed over the part of the nail that is in the
    wood longest: from just above the point to a quarter of the length below the
    head, which leaves the top of the shank round for a gripper to hold.
    """
    top = 0.0
    if shank == "smooth":
        return Pos(0, 0, z_point_top) * Cylinder(r, top - z_point_top, align=(_C, _C, _MIN))

    zone_bottom = z_point_top + 0.5 * d
    zone_top = -0.25 * L
    if zone_top <= zone_bottom:
        # Too short to deform: a nail this stubby is sold smooth.
        return Pos(0, 0, z_point_top) * Cylinder(r, top - z_point_top, align=(_C, _C, _MIN))

    if shank == "ring":
        # Annular rings, rolled into the wire: a long cone facing the point,
        # which is what lets the nail in, and a short step facing the head, which
        # is what keeps it there. The crest is above the wire and the root below
        # it, since rolling moves metal rather than adding any.
        pitch = max(0.8, 0.45 * d)
        root, crest = 0.94 * r, 1.08 * r
        profile = [(0.0, z_point_top), (r, z_point_top), (r, zone_bottom), (root, zone_bottom)]
        z = zone_bottom
        while z + pitch <= zone_top:
            profile += [(crest, z + 0.8 * pitch), (root, z + 0.85 * pitch), (root, z + pitch)]
            z += pitch
        profile += [(r, z + 0.1 * pitch), (r, top), (0.0, top)]
        return revolve(polygon_face([(x, 0.0, z) for x, z in profile]), Axis.Z)

    if shank == "screw":
        # Helical: F1667 makes it by twisting square wire, and so does this - a
        # square whose corners stand proud of the round wire, a quarter turn
        # every two diameters.
        side = 0.9 * d
        zone = zone_top - zone_bottom
        square = polygon_face(
            [(side / 2, side / 2, 0), (-side / 2, side / 2, 0), (-side / 2, -side / 2, 0), (side / 2, -side / 2, 0)]
        )
        twisted = Solid.extrude_linear_with_rotation(
            Pos(0, 0, zone_bottom) * square, (0, 0, zone_bottom), (0, 0, zone), 45.0 * zone / d
        )
        below = Pos(0, 0, z_point_top) * Cylinder(r, zone_bottom - z_point_top, align=(_C, _C, _MIN))
        above = Pos(0, 0, zone_top) * Cylinder(r, top - zone_top, align=(_C, _C, _MIN))
        return below + twisted + above

    raise ValueError("unknown shank: %s" % shank)


def build_head():
    """The head, standing on z = 0 if it is flat and sunk below it otherwise."""
    if head == "flat":
        return Cylinder(head_r, flat_t, align=(_C, _C, _MIN))

    # The others are a cone from the wire up to a short rim, with the top flush
    # at z = 0. How steep the cone is, is what tells them apart: a sinker's
    # countersunk head is the 90 degree cone of a countersunk screw, a casing
    # nail's a narrow one, and a finishing nail's brad head barely wider than
    # its wire.
    half_angle = {"countersunk": 45.0, "casing": 20.0, "brad": 12.0}[head]
    rim = max(0.15, 0.04 * head_r * 2)
    cone_h = max(head_r - r, 0.05 * d) / math.tan(math.radians(half_angle))
    solid = Pos(0, 0, -rim) * Cylinder(head_r, rim, align=(_C, _C, _MIN))
    solid += Pos(0, 0, -rim - cone_h) * Cone(r, head_r, cone_h, align=(_C, _C, _MIN))
    if head in ("casing", "brad"):
        # Cupped, so that a nail set finds the middle of it.
        depth, radius = 0.12 * head_r * 2, 0.35 * head_r * 2
        sphere_r = (radius**2 + depth**2) / (2 * depth)
        solid -= Pos(0, 0, sphere_r - depth) * Sphere(sphere_r)
    return solid


nail = (build_head() + build_shank() + build_point()).clean()

if "show_object" in locals():
    show_object(nail.wrapped, name="nail")  # noqa: F821 - injected by PartCAD
