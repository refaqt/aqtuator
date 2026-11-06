"""Rebuild the printed cooling block from `cad/params/default.csv`, in the GUI or headless.

The cooling block takes the water from the two ends of the cooling channel in
carriage-bottom and gives it to two 4 x 2.5 mm PU hoses. It lies in a 5 mm
pocket in the top of carriage-bottom (Pocket024). Two hose barbs are part of
the print. They stick out into the opening for the motor cable, and the hoses
push over them. From there the hoses cross over the motor cable and run in the
hose slot (Pocket027) to the side of the carriage.

Seals:

* Two standard 5 x 1.5 NBR 70 O-rings, as face seals in the bottom of the
  block, one around each port. Two countersunk M2.5 screws come up from below
  and pull the block onto the pocket floor.
* The hoses seal on the barb rings. The clamp at the side exit holds the hoses,
  so they cannot be pulled off the barbs.

Print it in SLA resin (for example a tough resin), bottom face down. The
passages inside are closed, so a resin print is needed: an FDM print is not
water-tight. Tap the two screw holes M2.5 in the resin.

Run headless with:

    FreeCADCmd modules/compact-stage/cad/parts/cooling-block/build_model.py

See `doqs/docs/agent-cad.md` for why the interactive path never saves.
"""

import sys
from pathlib import Path

try:
    _HERE = Path(__file__).resolve().parent
except NameError:  # exec()'d from the FreeCAD console
    _HERE = Path.cwd() / "cad"


def _doqs_scripts(start):
    """Find `doqs/scripts/` by walking up from this module's `cad/`."""
    for base in [start, *start.parents]:
        candidate = base / "doqs" / "scripts"
        if (candidate / "cad_build.py").is_file():
            return candidate
    raise RuntimeError(
        f"doqs/scripts/cad_build.py not found above {start} — "
        "run from inside a machine repository with the doqs submodule checked out."
    )


sys.path.insert(0, str(_doqs_scripts(_HERE)))

from cad_build import body, frame, main, part  # noqa: E402


#: The axes and origin of this part.
AXES = (
    "Origin on the bottom face of the block, on the axis of screw A. "
    "X and Y run the same way as in carriage-bottom, Z up. "
    "In carriage-bottom the origin sits at x = 128, y = 89, z = 22.5 mm."
)

# Where things sit, in carriage-bottom coordinates (mm). These come from
# carriage-bottom: the pocket Sketch037, the ports Sketch039 and the screw
# holes Hole006 and Hole007. Change them together with that part.
ORIGIN = (128.0, 89.0, 22.5)          # screw A axis on the pocket floor
POCKET = (108.5, 78.5, 150.0, 100.5)  # Sketch037: x0, y0, x1, y1
POCKET_R = 3.0                        # corner radius of the pocket
TOP_Z = 27.5                          # top face of carriage-bottom
OPENING_X = 147.25                    # wall of the motor cable opening (Sketch023)
PORT_A = (118.35, 84.5)               # end of the port lead (Sketch036)
PORT_B = (114.25, 94.5)               # on the second channel pass
SCREW_B = (140.0, 89.0)               # Hole007
TAP_D = 2.05                          # tap drill for M2.5 in resin
TAP_DEPTH = 4.0


def _rounded_box(x0, y0, x1, y1, z0, z1, r):
    import Part
    from FreeCAD import Vector as V

    box = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    vertical = [e for e in box.Edges
                if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6
                and e.Vertexes[0].X < x0 + 1e-6]
    return box.makeFillet(r, vertical)


def _cyl(r, p0, p1):
    import Part

    d = p1 - p0
    return Part.makeCylinder(r, d.Length, p0, d)


def barb(p, root):
    """One hose barb along +X, starting at `root` on the end face of the block.

    A short collar, then `barb_rings` rings. Each ring grows from the small
    diameter at its tip side to the large diameter at its root side, so the
    hose slides on easily and grips when it is pulled back.
    """
    import Part
    from FreeCAD import Vector as V

    r_small = p["barb_d_min"] / 2
    r_large = p["barb_d_max"] / 2
    ring_l = (p["barb_l"] - p["barb_collar_l"]) / p["barb_rings"]
    shape = _cyl(r_small, root, root + V(p["barb_l"], 0, 0))
    shape = shape.fuse(_cyl(r_large, root, root + V(p["barb_collar_l"], 0, 0)))
    for i in range(int(p["barb_rings"])):
        start = root + V(p["barb_collar_l"] + i * ring_l, 0, 0)
        cone = Part.makeCone(r_large, r_small, ring_l, start, V(1, 0, 0))
        shape = shape.fuse(cone)
    return shape.removeSplitter()


def block_shape(p):
    """The block as one solid, in part coordinates."""
    import Part
    from FreeCAD import Vector as V

    ox, oy, oz = ORIGIN
    g = p["cooling_block_gap"]

    def L(x, y, z):
        return V(x - ox, y - oy, z - oz)

    top = TOP_Z - p["cooling_block_top_gap"] - oz
    x0, y0, x1, y1 = POCKET
    end_x = OPENING_X - g
    solid = _rounded_box(x0 + g - ox, y0 + g - oy, end_x - ox, y1 - g - oy,
                         0, top, POCKET_R - g)

    # Port O-ring grooves in the bottom face. The groove outer wall is the
    # O-ring outside diameter, so water pressure pushes the ring onto it.
    ring_od = p["port_oring_id"] + 2 * p["port_oring_cs"]
    for px, py in (PORT_A, PORT_B):
        c = L(px, py, oz)
        outer = Part.makeCylinder(ring_od / 2, p["port_groove_depth"], c)
        inner = Part.makeCylinder(ring_od / 2 - p["port_groove_w"], p["port_groove_depth"], c)
        solid = solid.cut(outer.cut(inner))

    # Half way between the bottom of the port grooves and the top face.
    pz = (p["port_groove_depth"] + top) / 2
    # Barbs first, so the bore through them is cut together with the passages.
    for px, py in (PORT_A, PORT_B):
        solid = solid.fuse(barb(p, V(end_x - ox, py - oy, pz)))
    solid = solid.removeSplitter()

    # Water passages: up from each port, then straight along X through the
    # barb. Each port and its barb lie on one line, so the block is the same
    # for both.
    rp = p["cooling_passage_d"] / 2
    tip_x = end_x - ox + p["barb_l"]
    for px, py in (PORT_A, PORT_B):
        a = L(px, py, oz)
        b = V(a.x, a.y, pz)
        c = V(end_x - ox, a.y, pz)
        for piece in (_cyl(rp, a - V(0, 0, 0.1), b), _cyl(rp, b, c), Part.makeSphere(rp, b)):
            solid = solid.cut(piece)
        solid = solid.cut(_cyl(p["barb_bore_d"] / 2, c - V(0.5, 0, 0), V(tip_x + 0.1, a.y, pz)))

    # Two tapped holes for the M2.5 screws that come up from below.
    for sx, sy in ((ORIGIN[0], ORIGIN[1]), SCREW_B):
        solid = solid.cut(Part.makeCylinder(TAP_D / 2, TAP_DEPTH, L(sx, sy, oz)))
    return solid


def build(doc, params):
    """The printed cooling block between the cooling channel and the hoses."""
    container = part(doc, "cooling-block")
    block_body = body(doc, "Body", container=container)
    for obj in list(block_body.Group):
        if obj.TypeId.startswith("PartDesign::") and obj.TypeId != "PartDesign::CoordinateSystem":
            block_body.removeObject(obj)
            doc.removeObject(obj.Name)
    old = doc.getObject("BlockShape")
    if old is not None:
        block_body.BaseFeature = None
        doc.removeObject(old.Name)
    shape = doc.addObject("Part::Feature", "BlockShape")
    shape.Label = "BlockShape (printed cooling block)"
    shape.Shape = block_shape(params)
    container.addObject(shape)
    block_body.BaseFeature = shape
    shape.Visibility = False

    # Frame on the bottom face, on the axis of screw A. It joins the frame
    # IF_cooling_block of carriage-bottom.
    frame(doc, "IF_carriage", x="0", y="0", z="0", container=container)


main(build, globals(), cad_dir=_HERE)
