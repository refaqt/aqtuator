"""Rebuild the printed cable clamp from `cad/params/default.csv`, in the GUI or headless.

The cable clamp closes the side exit of carriage-bottom around the two cooling
hoses, the motor cable and the read head cable. It sits just outside the side
face, where there is more height than inside: over the base wall,
carriage-bottom has only 9 mm. It also holds the hoses, so they cannot be
pulled off the barbs of the cooling block.

Two halves:

* The lower half has a tower at each end. Two countersunk M3 screws go
  through the towers, sideways into the tapped holes Hole008 in the side face
  of carriage-bottom.
* The upper half lies on the lower half. Two countersunk M3 screws come up
  through the lower half and the upper half, into hex nuts in the top of the
  upper half. They press the halves onto the hoses and cables.

The channels are a little smaller than the hoses and cables, so they grip
them and close the exit. Print both halves in a tough material; they carry
no water.

Run headless with:

    FreeCADCmd modules/compact-stage/cad/parts/cable-clamp/build_model.py

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
    "Origin on the side face of carriage-bottom, at y = 110 and z = 23 mm "
    "(the split plane of the two halves). X points out of the side face, "
    "Y and Z run the same way as in carriage-bottom."
)

# In carriage-bottom coordinates (mm). These come from carriage-bottom: the
# hose slot (Pocket027), the motor cable slot (Pocket014), the encoder slot
# (Pocket019) and the tapped holes Hole008. Change them together.
ORIGIN = (208.0, 110.0, 23.0)
FACE_GAP = 0.1                  # room between the clamp and the side face
LENGTH = 12.0                   # along X, out of the side face
BASE_TOP_Z = 16.0               # top of the base wall under the side strip
LOWER_Z = 16.6                  # bottom of the lower half
UPPER_TOP_Z = 31.0              # top of the upper half and of the towers
SPLIT_GAP = 0.3                 # the screws close this gap when they press
TOWERS = ((78.0, 85.0), (135.0, 142.0))   # y ranges of the two towers
SIDE_SCREW_Y = (81.5, 138.5)    # Hole008 in carriage-bottom
SIDE_SCREW_Z = 23.8
CLAMP_SCREW_Y = (91.0, 130.0)   # the two screws that press the halves
CLAMP_SCREW_X = 214.0
# Channels: (y, diameter). Each one is 0.2 to 0.3 mm smaller than the hose
# or cable it holds.
CHANNELS = ((97.5, 3.8), (103.5, 3.8),   # cooling hoses, 4 mm
            (114.5, 8.0),                # MK21 motor cable, 8.3 mm
            (124.0, 3.5))                # read head cable, 3.7 mm
M3_CLEAR = 3.4
M3_HEAD_D = 6.72                # ISO 10642 M3, largest head diameter
NUT_AF = 5.7                    # M3 hex nut 5.5 mm across flats, with room
NUT_DEPTH = 2.6


def _box(x0, y0, z0, x1, y1, z1):
    import Part
    from FreeCAD import Vector as V

    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _countersunk(axis_point, direction, length):
    """Clearance hole with a 90° countersink at `axis_point`, into `direction`."""
    import Part

    d = direction.normalize()
    hole = Part.makeCylinder(M3_CLEAR / 2, length, axis_point, d)
    sink_h = (M3_HEAD_D - M3_CLEAR) / 2
    sink = Part.makeCone(M3_HEAD_D / 2, M3_CLEAR / 2, sink_h, axis_point, d)
    return hole.fuse(sink)


def _hex_pocket(centre, depth):
    import math
    import Part
    from FreeCAD import Vector as V

    r = NUT_AF / math.sqrt(3)
    pts = [centre + V(r * math.cos(math.pi / 3 * i), r * math.sin(math.pi / 3 * i), 0)
           for i in range(7)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, -depth))


def halves():
    """(lower, upper) in carriage-bottom coordinates."""
    from FreeCAD import Vector as V

    x0 = ORIGIN[0] + FACE_GAP
    x1 = ORIGIN[0] + LENGTH
    z_split = ORIGIN[2]
    y_lo, y_hi = TOWERS[0][0], TOWERS[1][1]

    lower = _box(x0, y_lo, LOWER_Z, x1, y_hi, z_split - SPLIT_GAP / 2)
    for ty0, ty1 in TOWERS:
        lower = lower.fuse(_box(x0, ty0, LOWER_Z, x1, ty1, UPPER_TOP_Z))
    upper = _box(x0, TOWERS[0][1] + 0.2, z_split + SPLIT_GAP / 2,
                 x1, TOWERS[1][0] - 0.2, UPPER_TOP_Z)

    for cy, cd in CHANNELS:
        channel = _cyl(cd / 2, V(x0 - 1, cy, z_split), V(x1 + 1, cy, z_split))
        lower = lower.cut(channel)
        upper = upper.cut(channel)

    for sy in SIDE_SCREW_Y:
        lower = lower.cut(_countersunk(V(x1, sy, SIDE_SCREW_Z), V(-1, 0, 0), LENGTH + 1))
    for sy in CLAMP_SCREW_Y:
        hole = _countersunk(V(CLAMP_SCREW_X, sy, LOWER_Z), V(0, 0, 1), UPPER_TOP_Z - LOWER_Z + 1)
        lower = lower.cut(hole)
        upper = upper.cut(hole)
        upper = upper.cut(_hex_pocket(V(CLAMP_SCREW_X, sy, UPPER_TOP_Z), NUT_DEPTH))
    return lower.removeSplitter(), upper.removeSplitter()


def _cyl(r, p0, p1):
    import Part

    d = p1 - p0
    return Part.makeCylinder(r, d.Length, p0, d)


def build(doc, params):
    """The two halves of the printed cable clamp at the side exit."""
    from FreeCAD import Vector as V

    container = part(doc, "cable-clamp")
    shapes = halves()
    for label, shape in zip(("Lower", "Upper"), shapes):
        b = body(doc, label, container=container)
        for obj in list(b.Group):
            if obj.TypeId.startswith("PartDesign::") and obj.TypeId != "PartDesign::CoordinateSystem":
                b.removeObject(obj)
                doc.removeObject(obj.Name)
        name = f"{label}Shape"
        old = doc.getObject(name)
        if old is not None:
            b.BaseFeature = None
            doc.removeObject(old.Name)
        feature = doc.addObject("Part::Feature", name)
        feature.Label = f"{name} ({label.lower()} half)"
        moved = shape.copy()
        moved.translate(V(-ORIGIN[0], -ORIGIN[1], -ORIGIN[2]))
        feature.Shape = moved
        container.addObject(feature)
        b.BaseFeature = feature
        feature.Visibility = False

    # Frame on the side face of carriage-bottom, on the split plane. It joins
    # the frame IF_cable_clamp of carriage-bottom.
    frame(doc, "IF_carriage", x="0", y="0", z="0", container=container)


main(build, globals(), cad_dir=_HERE)
