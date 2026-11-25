# SPDX-FileCopyrightText: 2025-2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the solids of the thermal model from the CAD, and export them as STEP.

Run it with the Python that comes with FreeCAD, from the repository root:

    freecadcmd modules/compact-stage/simulation/cases/forcer-cooling-thermal/build_geometry.py

It only reads the part files and the assembly. It never changes them.

What it does:

- Reads the placement of every part from the assembly (compact-stage.FCStd).
- Takes the real solids of base, carriage-bottom, carriage-top and the printed
  cooling block from their part files, and puts them where the assembly has
  them.
- The bought parts (forcer, magnet track, rails, guide blocks) are in the stoq
  library as Git LFS files that this script may not be able to read. They are
  built here as simple solids, with the sizes from the stoq parts tables and the
  maker data sheets (case.toml), on the positions from the assembly and from
  the faces of carriage-bottom they mount on.
- Builds the water inside the stage: the serpentine channel, the port lead and
  the two ports in carriage-bottom, and the risers, passages and drops in the
  cooling block. Each one is the volume that its pocket or hole feature takes
  out of the part. The forcer top face closes the channel from below.
- Checks that no two solids overlap, and that the solids touch where they
  should.

Output (not committed): results/forcer-cooling-thermal/exports/geom/
  <body>.step for each body, and geometry.json with the body list, the
  materials, the inlet and outlet of the water, and key sizes.
"""

import functools
import json
import os
import sys
import tomllib

print = functools.partial(print, flush=True)
CASE = "forcer-cooling-thermal"


def module_root():
    here = globals().get("__file__")
    if here:
        return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", ".."))
    return os.path.join(os.getcwd(), "modules", "compact-stage")


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def load_cfg(root):
    with open(os.path.join(root, "simulation", "cases", CASE, "case.toml"), "rb") as f:
        return tomllib.load(f)


def assembly_links(root, cfg):
    """Placement and source file of every link in the assembly."""
    import FreeCAD as App
    doc = App.openDocument(os.path.join(root, cfg["geometry"]["assembly"]), True)
    links = {}
    for o in doc.Objects:
        if o.TypeId != "App::Link":
            continue
        src = ""
        lo = o.LinkedObject
        if lo is not None:
            src = os.path.basename(lo.Document.FileName)
        links[o.Name] = {"label": o.Label, "placement": o.Placement, "file": src}
    App.closeDocument(doc.Name)
    return links


def body_shape(path):
    """The part solid with its screw holes filled, and the volume each
    feature takes out of the part.

    Screw holes and modelled threads do not change the heat flow or the
    thermal growth. Gmsh cannot mesh some of the thread faces. So the volume
    of every Hole feature is put back, except where a later feature cuts the
    same place.
    """
    import FreeCAD as App
    doc = App.openDocument(path, True)
    body = doc.getObject("Body")
    shape = body.Shape.copy()
    feats = [o for o in body.Group if o.TypeId.startswith("PartDesign::")
             and getattr(o, "BaseFeature", None) is not None]
    removed = {}
    tools = {}
    for o in feats:
        try:
            r = o.BaseFeature.Shape.cut(o.Shape)
            if r.Volume > 1e-6:
                removed[o.Name] = r
        except Exception:
            pass
        # The whole cutting tool, also where an earlier hole had already
        # taken the material. A pocket keeps it in body coordinates.
        try:
            t = o.AddSubShape
            if o.TypeId != "PartDesign::Hole" and t.Volume > 1e-6 and o.Name in removed:
                tools[o.Name] = t
        except Exception:
            pass
    holes = [o.Name for o in feats if o.TypeId == "PartDesign::Hole" and o.Name in removed]
    names = [o.Name for o in feats]
    filled = 0.0
    for h in holes:
        fill = removed[h]
        for later in names[names.index(h) + 1:]:
            if later in removed and later not in holes:
                fill = fill.cut(removed[later])
                if later in tools:
                    fill = fill.cut(tools[later])
        if fill.Volume > 1e-6:
            shape = shape.fuse(fill)
            filled += fill.Volume
    # Drill tips: Gmsh cannot mesh some small cone faces after the parts are
    # joined. Fill each small cone, so the drilled hole gets a flat bottom.
    import Part
    tips = 0
    for f in list(shape.Faces):
        b = f.BoundBox
        if isinstance(f.Surface, Part.Cone) and b.DiagonalLength < 8.0:
            ax = f.Surface.Axis
            if abs(abs(ax.z) - 1.0) > 1e-6:
                continue
            r = 0.5 * max(b.XLength, b.YLength)
            plug = Part.makeCylinder(r, b.ZLength, App.Vector(0.5 * (b.XMin + b.XMax),
                                                             0.5 * (b.YMin + b.YMax), b.ZMin))
            shape = shape.fuse(plug)
            tips += 1
    shape = shape.removeSplitter()
    App.closeDocument(doc.Name)
    return {"shape": shape, "removed": removed, "holes_filled": holes, "filled_volume": filled,
            "tips_filled": tips}


def placed(shape, placement):
    s = shape.copy()
    s.Placement = placement.multiply(s.Placement)
    return s


def box(x0, x1, y0, y1, z0, z1):
    import Part
    import FreeCAD as App
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, App.Vector(x0, y0, z0))


def main():
    root = module_root()
    cfg = load_cfg(root)
    out = os.path.join(root, "simulation", "results", CASE, "exports", "geom")
    os.makedirs(out, exist_ok=True)
    links = assembly_links(root, cfg)

    def link(name):
        if name not in links:
            fail("the assembly has no part %s any more" % name)
        return links[name]

    parts = os.path.join(root, "cad", "parts")
    cb_l = link("carriage_bottom001")
    ct_l = link("carriage_top")
    bl_l = link("cooling_block")
    base_l = link("base")
    cb = body_shape(os.path.join(parts, "carriage-bottom", "carriage-bottom.FCStd"))
    ct = body_shape(os.path.join(parts, "carriage-top", "carriage-top.FCStd"))
    bl = body_shape(os.path.join(parts, "cooling-block", "cooling-block.FCStd"))
    base = body_shape(os.path.join(parts, "base", "base.FCStd"))

    s_base = placed(base["shape"], base_l["placement"])
    s_cb = placed(cb["shape"], cb_l["placement"])
    s_ct = placed(ct["shape"], ct_l["placement"])
    s_bl = placed(bl["shape"], bl_l["placement"])
    for name, part in (("base", base), ("carriage-bottom", cb), ("carriage-top", ct),
                       ("cooling-block", bl)):
        print("%s: %d screw holes filled (%.1f mm3), %d drill tips filled"
              % (name, len(part["holes_filled"]), part["filled_volume"], part["tips_filled"]))
    for name, s in (("base", s_base), ("carriage-bottom", s_cb), ("carriage-top", s_ct),
                    ("cooling-block", s_bl)):
        if len(s.Solids) != 1 or not s.isValid():
            fail("%s is not one valid solid" % name)

    # --- Forcer: centred in the forcer pocket of carriage-bottom. The pocket
    # ceiling is the largest flat face that looks down at the mounting face
    # height (stator bottom + installation height).
    m = cfg["motor"]
    tr = cfg["track"]
    rail = cfg["rail"]
    blk = cfg["block"]
    rail_links = [n for n in links if n.startswith("EGR15")]
    block_links = [n for n in links if n.startswith("QEH15")]
    track_links = [n for n in links if n.startswith("MK2_")]
    if len(rail_links) != 2 or len(block_links) != 4 or len(track_links) != 2:
        fail("expected 2 rails, 4 guide blocks and 2 magnet tracks in the assembly")
    z_floor = links[rail_links[0]]["placement"].Base.z      # base pocket floor
    z_face = z_floor + m["install_height"]
    best = None
    for f in s_cb.Faces:
        b = f.BoundBox
        if b.ZLength < 1e-6 and abs(b.ZMin - z_face) < 1e-4 and (best is None or f.Area > best.Area):
            best = f
    if best is None:
        fail("no forcer pocket ceiling at z = %.2f in carriage-bottom" % z_face)
    pb = best.BoundBox
    fx = 0.5 * (pb.XMin + pb.XMax)
    fy = 0.5 * (pb.YMin + pb.YMax)
    # The forcer touches the pocket side wall only at two short pads. That
    # side contact carries little heat, and a face that only touches along an
    # edge breaks the mesh. So the box is 0.25 mm narrower on each long side
    # and touches carriage-bottom only with its mounting face.
    side = m.get("side_inset", 0.25)
    forcer_box = [fx - m["length"] / 2, fx + m["length"] / 2,
                  fy - m["width"] / 2 + side, fy + m["width"] / 2 - side,
                  z_face - m["height"], z_face]
    # The real forcer has a step along one long edge of its mounting face.
    # Carriage-bottom has two short pads that sit in that step. A plain box
    # overlaps those pads, so the box gets the same step over its full
    # length, as wide and as high as the pads.
    s_forcer = box(*forcer_box)
    v_box = s_forcer.Volume
    ov = s_forcer.common(s_cb)
    forcer_step = None
    if ov.Volume > 1e-3:
        ob = ov.BoundBox
        y0 = ob.YMin if ob.YMax > fy else forcer_box[2] - 1
        y1 = forcer_box[3] + 1 if ob.YMax > fy else ob.YMax
        forcer_step = [ob.YMin, ob.YMax, ob.ZMin, ob.ZMax]
        s_forcer = s_forcer.cut(box(forcer_box[0] - 1, forcer_box[1] + 1, y0, y1,
                                    ob.ZMin, forcer_box[5] + 1)).removeSplitter()
    if len(s_forcer.Solids) != 1 or s_forcer.Volume < 0.97 * v_box \
            or s_forcer.common(s_cb).Volume > 1e-3:
        fail("the forcer box does not fit the forcer pocket any more")
    print("Forcer: %.0f mm3 (box %.0f mm3), step y %s z %s" % (
        s_forcer.Volume, v_box, forcer_step and forcer_step[:2], forcer_step and forcer_step[2:]))

    # --- Magnet track: two pieces end to end, centred under the forcer in y.
    xs = sorted(links[n]["placement"].Base.x for n in track_links)
    track_box = [xs[0] - tr["length"] / 2, xs[1] + tr["length"] / 2,
                 fy - tr["width"] / 2, fy + tr["width"] / 2,
                 z_floor, z_floor + tr["height"]]
    s_track = box(*track_box)

    # --- Rails: from their placement (origin at one end, along +x).
    rails = []
    for n in sorted(rail_links, key=lambda n: links[n]["placement"].Base.y):
        p = links[n]["placement"].Base
        rails.append({"name": n, "y": p.y, "box": [p.x, p.x + rail["length"],
                      p.y - rail["width"] / 2, p.y + rail["width"] / 2,
                      p.z, p.z + rail["height"]]})
    s_rails = [box(*r["box"]) for r in rails]

    # --- Guide blocks: the placement origin is at the end of the 56 mm
    # envelope (E2 unit), and the block runs away from the carriage middle.
    # Only the steel body (L1) is modelled, in the middle of the envelope.
    # The rail slot is as wide as the rail and reaches the rail top, so the
    # block touches the rail on its top and both sides (the four ball rows).
    x_mid = 0.5 * (s_cb.BoundBox.XMin + s_cb.BoundBox.XMax)
    blocks = []
    for n in sorted(block_links, key=lambda n: (links[n]["placement"].Base.y,
                                                links[n]["placement"].Base.x)):
        p = links[n]["placement"].Base
        sign = -1.0 if p.x < x_mid else 1.0
        xc = p.x + sign * blk["envelope"] / 2
        yc = min(rails, key=lambda r: abs(r["y"] - p.y))["y"]
        z0 = p.z + blk["H1"]
        z1 = p.z + blk["H"]
        zr = p.z + rail["height"]
        outer = box(xc - blk["L1"] / 2, xc + blk["L1"] / 2, yc - blk["W"] / 2, yc + blk["W"] / 2, z0, z1)
        slot = box(xc - blk["L1"] / 2 - 1, xc + blk["L1"] / 2 + 1,
                   yc - rail["width"] / 2, yc + rail["width"] / 2, z0 - 1, zr)
        blocks.append({"name": n, "xc": xc, "yc": yc, "z": [z0, z1], "shape": outer.cut(slot)})

    # --- Water: the volume each pocket or hole takes out of its part.
    water_tools = []
    for name in ("Pocket008", "Pocket023", "Pocket026"):
        if name not in cb["removed"]:
            fail("carriage-bottom has no feature %s (cooling channel) any more" % name)
        water_tools.append(placed(cb["removed"][name], cb_l["placement"]))
    for name in ("Riser_a", "Riser_b", "Passage_a", "Passage_b", "Drop_a", "Drop_b"):
        if name not in bl["removed"]:
            fail("the cooling block has no feature %s any more" % name)
        water_tools.append(placed(bl["removed"][name], bl_l["placement"]))
    water = water_tools[0]
    for t in water_tools[1:]:
        water = water.fuse(t)
    water = water.cut(s_cb).cut(s_bl).cut(s_forcer).removeSplitter()
    if len(water.Solids) != 1:
        fail("the water is %d pieces, expected one connected volume" % len(water.Solids))
    channel_vol = sum(cb["removed"][n].Volume for n in ("Pocket008",))
    print("Water volume %.1f mm3 (channel %.1f mm3)" % (water.Volume, channel_vol))

    # Inlet and outlet: the passage ends at the fittings.
    fa = link("fitting_a")["placement"].Base
    fb = link("fitting_b")["placement"].Base

    bodies = [
        ("base", s_base, "al7075"),
        ("carriage_bottom", s_cb, "al7075"),
        ("carriage_top", s_ct, "al7075"),
        ("cooling_block", s_bl, "resin"),
        ("forcer", s_forcer, "forcer"),
        ("track", s_track, "track"),
    ]
    for i, r in enumerate(rails):
        bodies.append(("rail_%d" % (i + 1), s_rails[i], "steel"))
    for i, b in enumerate(blocks):
        bodies.append(("block_%d" % (i + 1), b["shape"], "steel"))
    bodies.append(("water", water, "water"))

    # Overlap check: no two solids may share volume.
    bad = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i][1], bodies[j][1]
            if not a.BoundBox.intersect(b.BoundBox):
                continue
            v = a.common(b).Volume
            if v > 1e-3:
                bad.append("%s / %s: %.3f mm3" % (bodies[i][0], bodies[j][0], v))
    if bad:
        fail("solids overlap:\n  " + "\n  ".join(bad))

    info = {"bodies": [], "forcer_box": forcer_box, "forcer_step": forcer_step, "track_box": track_box,
            "rails": [{k: r[k] for k in ("name", "y", "box")} for r in rails],
            "blocks": [{k: b[k] for k in ("name", "xc", "yc", "z")} for b in blocks],
            "pocket_ceiling": [pb.XMin, pb.XMax, pb.YMin, pb.YMax, z_face],
            "z_floor": z_floor,
            "fitting_in": [fa.x, fa.y, fa.z], "fitting_out": [fb.x, fb.y, fb.z],
            "channel_volume": channel_vol,
            "channel_wetted_ceiling": cb["removed"]["Pocket008"].Volume,
            "placements": {k: [links[k]["placement"].Base.x, links[k]["placement"].Base.y,
                               links[k]["placement"].Base.z] for k in links}}
    for name, s, mat in bodies:
        path = os.path.join(out, name + ".step")
        s.exportStep(path)
        bb = s.BoundBox
        info["bodies"].append({"name": name, "material": mat, "volume": s.Volume,
                               "area": s.Area,
                               "bbox": [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax],
                               "step": name + ".step"})
        print("%-16s %-7s volume %10.1f mm3" % (name, mat, s.Volume))
    with open(os.path.join(out, "geometry.json"), "w") as f:
        json.dump(info, f, indent=1)
    print("Done: %s" % out)


main()
