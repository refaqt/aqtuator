# SPDX-FileCopyrightText: 2026 Refaqt (BE 0804.145.539) and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the pictures of the compact stage for the module README.

Run from the repository root, with the FreeCAD 1.1 window program (not freecadcmd):

    freecad modules/compact-stage/docs/images/render_views.py

On Linux without a screen, put `xvfb-run -a -s "-screen 0 2400x1600x24"` in front.
The parts library in modules/stoq/ must hold the real CAD files, not Git LFS pointers.

The script opens the assembly, gives each part a colour by its role, hides the datum frames,
and writes two PNG files next to itself. It changes the colours only in memory and never saves
a CAD file.
  compact-stage-iso.png     the whole stage, isometric view, every part solid
  compact-stage-inside.png  the same view without carriage-top, the seal strip, its clamps
                            and the top rollers; the base is see-through, as in its CAD file
"""
import os

import FreeCAD as App
import FreeCADGui as Gui
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ASSEMBLY = os.path.join(HERE, "..", "..", "cad", "assemblies", "compact-stage", "compact-stage.FCStd")
RENDER_W, RENDER_H = 4800, 3000   # rendered size, before the white border is cut off
OUT_W = 2000                      # width of the saved picture
MARGIN = 40                       # white border kept round the stage, in output pixels

# Colour per document (part file). Made parts: metal tones; printed parts: orange.
COLOURS = {
    "base": (0.62, 0.66, 0.72),
    "carriage_bottom": (0.42, 0.58, 0.80),
    "carriage_top": (0.78, 0.82, 0.88),
    "sealing_strip": (0.86, 0.86, 0.88),
    "sealing_strip_clamp": (0.95, 0.55, 0.18),
    "cooling_block": (0.95, 0.55, 0.18),
    "motor_cable_clamp": (0.95, 0.55, 0.18),
    "read_head_cable_clamp": (0.95, 0.55, 0.18),
    "roller_sleeve": (0.95, 0.55, 0.18),
    "EGR15U418H": (0.80, 0.80, 0.82),
    "QEH15SAZAP_E2": (0.75, 0.12, 0.12),
    "MK21": (0.18, 0.18, 0.20),
    "MK2_180": (0.30, 0.30, 0.34),
    "AK_MC15_B_0_5M_SUBD15": (0.22, 0.22, 0.24),
    "MB_MC15_MK_ML230": (0.85, 0.72, 0.35),
    "TA17_7": (0.12, 0.12, 0.12),
}
SCREW_COLOUR = (0.30, 0.30, 0.32)
DATUM_TYPES = ("App::Line", "App::Plane", "App::Point", "App::Origin",
               "Part::LocalCoordinateSystem", "PartDesign::Line", "PartDesign::Plane",
               "PartDesign::Point", "PartDesign::CoordinateSystem", "Part::DatumPlane",
               "App::FeaturePython", "Assembly::JointGroup")   # the last two: joint markers

# Objects of the assembly to hide for the view inside the stage.
INSIDE_HIDE = ("carriage_top", "sealing_strip", "clamp_start", "clamp_end", "roller_top_",
               "preload_screw_start0")


def colour_and_clean(assembly):
    """Colour the parts, hide the datums, and return the transparency each object had."""
    transparency = {}
    for doc in App.listDocuments().values():
        colour = COLOURS.get(doc.Name)
        for obj in doc.Objects:
            vo = obj.ViewObject
            if vo is None:
                continue
            if obj.TypeId in DATUM_TYPES:
                vo.Visibility = False
            elif hasattr(vo, "ShapeColor"):
                if getattr(vo, "Transparency", 0):
                    transparency[vo] = vo.Transparency
                    vo.Transparency = 0      # the whole stage solid in the first view
                if colour:
                    vo.ShapeColor = colour
                elif doc is assembly and obj.TypeId == "Part::FeaturePython":
                    vo.ShapeColor = SCREW_COLOUR   # the screws placed in the assembly
    return transparency


def save(view, name):
    Gui.updateGui()
    view.fitAll()
    Gui.updateGui()
    path = os.path.join(HERE, name)
    view.saveImage(path, RENDER_W, RENDER_H, "White")
    img = Image.open(path).convert("RGB")
    box = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    img = img.crop(box)
    scale = (OUT_W - 2 * MARGIN) / img.width
    img = img.resize((OUT_W - 2 * MARGIN, round(img.height * scale)), Image.LANCZOS)
    out = Image.new("RGB", (OUT_W, img.height + 2 * MARGIN), (255, 255, 255))
    out.paste(img, (MARGIN, MARGIN))
    out.save(path, optimize=True)


def main():
    doc = App.openDocument(os.path.normpath(ASSEMBLY))
    gdoc = Gui.getDocument(doc.Name)
    Gui.ActiveDocument = gdoc
    view = gdoc.ActiveView
    view.setAxisCross(False)
    view.setCameraType("Orthographic")
    transparency = colour_and_clean(doc)
    view.viewIsometric()
    save(view, "compact-stage-iso.png")
    for vo, value in transparency.items():
        vo.Transparency = value   # the base as drawn: see-through, so the inside shows
    for obj in doc.Objects:
        if obj.ViewObject and obj.Name.startswith(INSIDE_HIDE):
            obj.ViewObject.Visibility = False
    save(view, "compact-stage-inside.png")
    App.closeDocument(doc.Name)


try:
    main()
except Exception:
    import traceback
    traceback.print_exc()
    os._exit(1)
os._exit(0)
