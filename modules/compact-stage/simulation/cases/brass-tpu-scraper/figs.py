"""Figures of the brass and TPU scraper. All views use mm from the carriage end face along x."""
import math
from design import *  # noqa: F401,F403
from render import section_poly, draw          # scraper-fit: sections of OCP shapes
from raster import render as zbuffer           # scraper-fit: z-buffer 3D views
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle, Rectangle
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

C = {'base': '#c9ced6', 'strip': '#333333', 'carriage-bottom': '#9fb7d9', 'carriage-top': '#b9c9a8',
     'brass': '#d9a521', 'TPU': '#e05a47', 'bolt': '#4b5263', 'plunger': '#2e8b8b', 'pull screw': '#7a5c99',
     'roller': '#1f5fa8', 'corner screw': '#8a8a8a'}


def build():
    S = {'top2': carriage_top_new(), 'brass': brass(), 'tpu': tpu(), 'bolts': bolts(), 'plungers': plungers(),
         'pulls': pull_screws(), 'rollers': rollers()}
    S['heads'] = {case: head_at(case) for case in CARRIAGE_END_X}
    return S


def parts(S, head_case=DESIGN_CASE):
    p = [('base', BASE), ('strip', STRIP), ('carriage-bottom', BOT), ('carriage-top', S['top2']),
         ('brass', S['brass']), ('TPU', S['tpu'])]
    p += [('bolt', b) for b in S['bolts']] + [('plunger', b) for b in S['plungers']]
    p += [('pull screw', b) for b in S['pulls']] + [('roller', r) for r in S['rollers']]
    if head_case:
        p.append(('corner screw', S['heads'][head_case]))
    return p


def side(ax, S, y, xlim=(-5, 24), zlim=(38.6, 61), title='', head_case=DESIGN_CASE, legend=False):
    used = set()
    for name, s in parts(S, head_case):
        g = section_poly(s, (0, y, 0), (0, 1, 0), 0, 2)
        if g is None or g.is_empty:
            continue
        g = affinity.translate(g, -X0, 0)
        if not g.intersects(sbox(xlim[0], zlim[0], xlim[1], zlim[1])):
            continue
        draw(ax, g, C[name], lw=0.5)
        if name not in used:
            ax.plot([], [], 's', color=C[name], label=name, ms=7, mec='k'); used.add(name)
    ax.set_xlim(*xlim); ax.set_ylim(*zlim); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_title(title, fontsize=9); ax.set_xlabel('x from the carriage end face [mm]', fontsize=8)
    ax.set_ylabel('z [mm]', fontsize=8); ax.tick_params(labelsize=7)
    if legend:
        ax.legend(fontsize=7, loc='upper right', framealpha=0.9)


def note(ax, xy, text, xytext, fs=7):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, arrowprops=dict(arrowstyle='->', lw=0.6),
                bbox=dict(fc='white', ec='none', alpha=0.85, pad=1))


# ---------------------------------------------------------------- 1. side sections
def fig_sections(S, out):
    fig, axs = plt.subplots(3, 2, figsize=(15, 17))
    a = axs[0, 0]
    side(a, S, BOLT_Y[0], title=f'A. y = {BOLT_Y[0]:.0f} mm: horizontal M3 locking bolt', legend=True)
    note(a, (-1.5, BOLT_Z), 'ISO 4762 M3x16:\nlocks the brass', (-4.6, 55.5))
    note(a, (3, BOLT_Z + 1.9), f'vertical slot {SLOT_W} x {SLOT_W + 2 * SLOT_PLAY} mm\nin the brass: ±{SLOT_PLAY} mm play', (4, 56.5))
    note(a, (14, BOLT_Z), f'M3 tapped hole,\n{TAP_DEPTH:.0f} mm deep', (14, 52.5))
    note(a, (0.5, Z_RIB), f'rib {GAP} mm\nabove the strip', (-4.6, 42.2))
    note(a, (7.8, 40.1), 'TPU: two lips\npress on the strip', (9.5, 42.0))
    a = axs[0, 1]
    side(a, S, PLUNGER_Y[0], title=f'B. y = {PLUNGER_Y[0]:.0f} mm: MISUMI spring plunger M4 pushes the brass down')
    note(a, (PLUNGER_XR, 55), 'spring plunger M4,\nin a tapped hole\nfrom the top', (8, 55.5))
    note(a, (PLUNGER_XR, Z_BR_TOP + 0.5), 'pin on the brass;\n1 mm room above\nthe brass', (8, 50.5))
    a = axs[1, 0]
    side(a, S, PULL_Y[0], title=f'C. y = {PULL_Y[0]:.0f} mm: M2.5 pull screw holds the brass up')
    note(a, (PULL_XR, 58.5), 'ISO 4762 M2.5x12 in a\nØ5 counterbore', (8, 56.5))
    note(a, (PULL_XR, 47), 'thread in\nthe brass', (8, 50.5))
    a = axs[1, 1]
    side(a, S, ROLLER_Y[0], title=f'D. y = {ROLLER_Y[0]} mm: in front of a top roller, brass and TPU are thinner')
    note(a, (1.5, 47), f'brass {BR_L_NOTCH:.0f} mm', (-4.6, 55))
    note(a, (5, 47), f'TPU {TPU_X_NOTCH[1] - TPU_X_NOTCH[0]:.1f} mm', (2, 57.5))
    note(a, (ROLLER_XR - 4.5, 45), 'top roller', (15, 56))
    a = axs[2, 0]
    side(a, S, 105.0, title='E. y = 105 mm: the middle M5 hole for a cross table; the pocket stays 4.5 mm deep here')
    note(a, (5, 52), 'M5 hole, 13 mm drill\n(cross-table interface)', (9, 56.5))
    note(a, (5, 44.5), 'brass and TPU are lower here,\nthe ceiling is the old 4.5 mm', (8, 50.0))
    a = axs[2, 1]
    side(a, S, HEAD_Y, title=f'F. y = {HEAD_Y:.0f} mm: corner screw head at the {DESIGN_CASE}', head_case=DESIGN_CASE)
    note(a, (HEAD_X - CARRIAGE_END_X[DESIGN_CASE], HEAD_TOP), 'ISO 7380-2 M4 corner screw\nof the strip', (-4.6, 53))
    note(a, (RIB_DIAG - HEAD_Y + 0.7, Z_RIB), 'angled rib, behind the head', (10, 43.5))
    note(a, (5, Z_RELIEF), f'brass raised to z {Z_RELIEF}\nin front of the angled rib', (6, 52.0))
    fig.suptitle('Brass and TPU scraper at the start end of carriage-top: side sections (sketch, 2026-11-10)\n'
                 'The strip is the real preloaded strip from the CAD. The other end is the same, turned 180°.', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig(out, dpi=130); plt.close(fig)


# ---------------------------------------------------------------- 2. bottom view
def add_poly(ax, g, fc, ec='k', lw=0.6, alpha=1.0, hatch=None, ls='-', zorder=2):
    for p in getattr(g, 'geoms', [g]):
        if p.is_empty or p.geom_type != 'Polygon':
            continue
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha,
                           hatch=hatch, ls=ls, zorder=zorder))


def bottom(ax, ylim, xlim=(-6, 24)):
    add_poly(ax, pocket_plan().intersection(sbox(-0.01, 0, 40, 210)), 'none', ec='#556b2f', lw=1.0, ls='--', zorder=1)
    add_poly(ax, brass_plan(), C['brass'], zorder=2)
    add_poly(ax, brass_plan().intersection(relief_plan()), '#f3dc9a', hatch='////', zorder=3)
    add_poly(ax, rib_plan(), '#8a5a00', zorder=4)
    add_poly(ax, tpu_plan().intersection(pocket_plan().buffer(-PLAY, join_style=1)), C['TPU'], alpha=0.85, zorder=2)
    # lip tip lines
    k = math.tan(math.radians(LIP_LEAN)); h = Z_TPU_BODY - Z_LIP_TIP
    edges = sorted({TPU_Y[0], TPU_Y[1]} | {v for ab in NOTCHES for v in ab})
    for y0, y1 in zip(edges[:-1], edges[1:]):
        lips = LIPS_NOTCH if in_notch((y0 + y1) / 2) else LIPS
        y0 = max(y0, RIB_DIAG + 2) if y0 < 30 else y0
        y1 = min(y1, 210 - RIB_DIAG - 2) if y1 > 180 else y1
        for xa, d in lips:
            ax.plot([xa + LIP_T / 2 + d * k * h] * 2, [y0, y1], color='white', lw=0.8, zorder=5)
    for y in ROLLER_Y:
        ax.add_patch(Rectangle((ROLLER_XR - ROLLER_R, y - ROLLER_L / 2), 2 * ROLLER_R, ROLLER_L, fc=C['roller'],
                               ec='k', lw=0.6, zorder=2))
    for case, ls in [(DESIGN_CASE, '-'), ('dampers fully pressed', ':')]:
        add_poly(ax, head_swept_plan(case).intersection(sbox(-6, 0, 40, 210)), 'none', ec='#333', lw=1.0, ls=ls, zorder=6)
        xc = HEAD_X - CARRIAGE_END_X[case]
        for yc in (HEAD_Y, 210 - HEAD_Y):
            ax.add_patch(Circle((xc, yc), HEAD_R, fc=C['corner screw'], ec='k', lw=0.6, alpha=0.7, zorder=6))
    for y in BOLT_Y:
        ax.add_patch(Rectangle((-BOLT_HEAD_K, y - BOLT_HEAD_D / 2), BOLT_HEAD_K, BOLT_HEAD_D, fc=C['bolt'], ec='k', lw=0.5))
    for yy in STRIP_Y:
        ax.axhline(yy, color=C['strip'], lw=0.8, ls='-.', zorder=7)
    ax.axvline(0, color='k', lw=0.8)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=.25)
    ax.set_xlabel('x from the carriage end face [mm]', fontsize=8); ax.set_ylabel('y [mm]', fontsize=8)
    ax.tick_params(labelsize=7)


def fig_bottom(out):
    fig = plt.figure(figsize=(15, 14))
    a1 = fig.add_axes([0.04, 0.05, 0.16, 0.86]); bottom(a1, (0, 210))
    a1.set_title('Whole width', fontsize=9)
    a2 = fig.add_axes([0.25, 0.05, 0.72, 0.86]); bottom(a2, (0, 60), xlim=(-6, 44))
    a2.set_title('Corner at y = 0 (the corner at y = 210 is its mirror image)', fontsize=9)
    note(a2, (0.5, 40), 'rib, 1 mm wide,\n0.15 mm above the strip', (-5.5, 50))
    note(a2, (RIB_DIAG - 9 + 0.5, 9), 'the rib turns 45° inward\nand reaches the side', (27, 2.5))
    note(a2, (2, 13), 'brass raised over the\nscrew head (hatched)', (-5.5, 25))
    note(a2, (8, 40), 'TPU wiper; white lines:\nthe two lip tips', (27, 54))
    note(a2, (8, 13.2), 'TPU ends at y 12.5, inside\nthe strip edge (y 12.2)', (27, 19))
    note(a2, (HEAD_X - CARRIAGE_END_X[DESIGN_CASE] + 3, 6), f'corner screw head and its path + {CLEAR} mm,\n'
         f'carriage at the {DESIGN_CASE}', (27, 12.5))
    note(a2, (HEAD_X - CARRIAGE_END_X['dampers fully pressed'] + 4, 4), 'dotted: dampers fully pressed (crash)',
         (27, 7.5))
    note(a2, (ROLLER_XR, 30), 'top roller', (27, 44))
    note(a2, (-1.5, BOLT_Y[0]), 'M3 bolt head', (-5.5, 57.5))
    a2.text(-5.5, 12.6, 'strip edge', fontsize=7, color=C['strip'])
    fig.suptitle('Scraper seen from below (sketch). Front of the carriage on the left. Dashed green: the milled pocket '
                 'in carriage-top.', fontsize=11)
    fig.savefig(out, dpi=130); plt.close(fig)


# ---------------------------------------------------------------- 3. top view
def fig_top(S, out):
    fig, axs = plt.subplots(1, 2, figsize=(15, 11), gridspec_kw={'width_ratios': [1, 2.3]})
    for ax, ylim in zip(axs, [(0, 210), (40, 170)]):
        g = affinity.translate(section_poly(S['top2'], (0, 0, 59.9), (0, 0, 1), 0, 1), -X0, 0)
        draw(ax, g, C['carriage-top'])
        add_poly(ax, pocket_plan().intersection(sbox(-0.01, 0, 40, 210)), 'none', ec='#556b2f', lw=0.9, ls='--')
        add_poly(ax, bridge_plan().intersection(sbox(-0.01, 0, 40, 210)), 'none', ec='#556b2f', lw=0.6, ls=':')
        for y in PLUNGER_Y:
            ax.add_patch(Circle((PLUNGER_XR, y), PLUNGER_D / 2, fc=C['plunger'], ec='k', lw=0.6))
        for y in PULL_Y:
            ax.add_patch(Circle((PULL_XR, y), PULL_HEAD_D / 2, fc=C['pull screw'], ec='k', lw=0.6))
        for y in BOLT_Y:
            ax.plot([-BOLT_HEAD_K, POCKET_L + TAP_DEPTH], [y, y], color=C['bolt'], lw=2.5, alpha=0.6)
        ax.axvline(0, color='k', lw=0.8)
        ax.set_xlim(-4, 32); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.grid(alpha=.25)
        ax.set_xlabel('x from the carriage end face [mm]', fontsize=8); ax.set_ylabel('y [mm]', fontsize=8)
        ax.tick_params(labelsize=7)
    a = axs[1]
    note(a, (PLUNGER_XR, PLUNGER_Y[0]), f'spring plunger M4 (teal), y = {PLUNGER_Y[0]:.0f} and {PLUNGER_Y[1]:.0f}', (9, 66))
    note(a, (PULL_XR, PULL_Y[0]), f'M2.5 pull screw (purple), y = {PULL_Y[0]:.0f} and {PULL_Y[1]:.0f}', (9, 82))
    note(a, (8, BOLT_Y[1]), 'M3 locking bolts, horizontal (grey lines), y = ' + ', '.join(f'{y:.0f}' for y in BOLT_Y),
         (12, 96))
    note(a, (5, 105), 'M5 cross-table hole: the pocket stays\n4.5 mm deep around it (dotted)', (12, 112))
    note(a, (9.5, 160), 'dashed: the pocket underneath,\n9.5 mm deep', (14, 150))
    axs[0].set_title('Whole width', fontsize=9); axs[1].set_title('Middle part', fontsize=9)
    fig.suptitle('Top of carriage-top at the start end: where the adjusting parts go in (sketch)', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(out, dpi=130); plt.close(fig)


# ---------------------------------------------------------------- 4. TPU lip detail
def fig_lips(S, out):
    fig, axs = plt.subplots(1, 2, figsize=(15, 7.5))
    side(axs[0], S, 65.0, xlim=(-1, 12), zlim=(39.0, 51), title='Middle, y = 65 mm', legend=True)
    side(axs[1], S, 30.0, xlim=(-1, 12), zlim=(39.0, 51), title='In front of a top roller, y = 30 mm')
    k = math.tan(math.radians(LIP_LEAN)); h = Z_TPU_BODY - Z_LIP_TIP
    for ax, lips, (x0, x1) in [(axs[0], LIPS, TPU_X), (axs[1], LIPS_NOTCH, TPU_X_NOTCH)]:
        note(ax, (lips[0][0] + d_off(lips[0], k, h), Z_LIP_TIP + 0.4),
             f'front lip leans out,\n{LIP_T} mm thick', (lips[0][0] - 5.0, 42.6))
        note(ax, (lips[1][0] + LIP_T + d_off(lips[1], k, h), Z_LIP_TIP + 0.4),
             f'rear lip leans in;\n{LIP_LEAN:.0f}° from vertical', (lips[1][0] + 1.4, 42.2))
        ax.annotate('', xy=(x1 + 0.6, Z_STRIP), xytext=(x1 + 0.6, Z_LIP_TIP), arrowprops=dict(arrowstyle='<->', lw=0.6))
        ax.text(x1 + 0.8, 39.05, f'{INTERF} mm press-in (free tip)', fontsize=7)
        ax.annotate('', xy=(x0, 50.4), xytext=(x1, 50.4), arrowprops=dict(arrowstyle='<->', lw=0.6))
        ax.text((x0 + x1) / 2 - 1, 50.55, f'TPU {x1 - x0:.1f} mm', fontsize=7)
        ax.axhline(Z_STRIP, color=C['strip'], lw=0.4)
    fig.suptitle(f'TPU wiper: two thin lips that lean apart. Lip length {h / math.cos(math.radians(LIP_LEAN)):.1f} mm, '
                 f'{LIP_T} mm thick (length/thickness = {h / math.cos(math.radians(LIP_LEAN)) / LIP_T:.1f}). '
                 'Lips drawn free, before they touch the strip.', fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out, dpi=130); plt.close(fig)


def d_off(lip, k, h):
    return lip[1] * k * h


# ---------------------------------------------------------------- 5. the roller zone explained
def fig_roller_zone(S, out):
    fig = plt.figure(figsize=(15, 10))
    a = fig.add_axes([0.05, 0.08, 0.42, 0.82])
    g = affinity.translate(section_poly(TOP, (0, 0, Z_UNDER + 0.3), (0, 0, 1), 0, 1), -X0, 0)
    draw(a, g, C['carriage-top'])
    add_poly(a, pocket_plan().intersection(sbox(-0.01, 0, 40, 210)), '#fff5c2', ec='#556b2f', lw=1.0, ls='--', alpha=0.7)
    for y in ROLLER_Y:
        a.add_patch(Rectangle((ROLLER_XR - ROLLER_R, y - ROLLER_L / 2), 2 * ROLLER_R, ROLLER_L, fc=C['roller'], ec='k', lw=0.6))
    a.axvline(0, color='k', lw=0.8)
    a.set_xlim(-3, 30); a.set_ylim(0, 75); a.set_aspect('equal'); a.grid(alpha=.25)
    a.set_xlabel('x from the carriage end face [mm]', fontsize=8); a.set_ylabel('y [mm]', fontsize=8)
    a.annotate('', xy=(0, 63), xytext=(POCKET_L, 63), arrowprops=dict(arrowstyle='<->', lw=0.8))
    a.text(1.0, 64.2, f'{POCKET_L:.0f} mm: brass {BR_L:.0f} + TPU {TPU_X[1] - TPU_X[0]:.1f}', fontsize=8)
    a.annotate('', xy=(0, 34.5), xytext=(NOTCH_L, 34.5), arrowprops=dict(arrowstyle='<->', lw=0.8))
    a.text(0.4, 36.0, f'only {NOTCH_L} mm:\nbrass {BR_L_NOTCH:.0f}\n+ TPU {TPU_X_NOTCH[1] - TPU_X_NOTCH[0]:.1f}',
           fontsize=8)
    note(a, (ROLLER_XR, 40), 'top roller in its\npocket (blue)', (19, 58))
    note(a, (11.5, 20), 'roller pocket and axle\nslots in carriage-top', (19, 12))
    note(a, (6, 5), 'pocket for the scraper\n(dashed, light yellow)', (14, 2.5))
    a.set_title('Seen from below: the top roller sits close behind the end face.\n'
                f'In front of it (y = {NOTCHES[0][0]:.0f} to {NOTCHES[0][1]:.0f} mm) there is less room.', fontsize=9)
    b = fig.add_axes([0.53, 0.53, 0.45, 0.38]); side(b, S, 65.0, xlim=(-4, 20), zlim=(38.6, 52), title='Middle, y = 65 mm')
    c = fig.add_axes([0.53, 0.07, 0.45, 0.38]); side(c, S, 34.5, xlim=(-4, 20), zlim=(38.6, 52), title='In front of the roller, y = 34.5 mm')
    fig.suptitle('Why the brass and the TPU are thinner in front of the top rollers', fontsize=11)
    fig.savefig(out, dpi=130); plt.close(fig)


# ---------------------------------------------------------------- 6. 3D views
def tris(shape):
    BRepMesh_IncrementalMesh(shape, 0.05, False, 0.3, True)
    ex = TopExp_Explorer(shape, TopAbs_FACE); out = []
    while ex.More():
        f = TopoDS.Face(ex.Current()); ex.Next(); loc = TopLoc_Location()
        t = BRep_Tool.Triangulation_s(f, loc)
        if t is None:
            continue
        tr = loc.Transformation(); rev = f.Orientation() == TopAbs_REVERSED
        P = [t.Node(i).Transformed(tr) for i in range(1, t.NbNodes() + 1)]
        P = [(p.X(), p.Y(), p.Z()) for p in P]
        for i in range(1, t.NbTriangles() + 1):
            a, b, c = t.Triangle(i).Get()
            tri = [P[a - 1], P[b - 1], P[c - 1]]
            out.append(tri[::-1] if rev else tri)
    return np.array(out)


def picture(items, elev, azim, title, path, size=(1500, 950)):
    img = zbuffer([(tris(sh), matplotlib.colors.to_rgb(c)) for sh, c in items if vol(sh) > 1e-6], elev, azim, size)
    fig = plt.figure(figsize=(size[0] / 150, size[1] / 150 + 0.5))
    ax = fig.add_axes([0, 0, 1, size[1] / (size[1] + 75)]); ax.imshow(img); ax.axis('off')
    fig.suptitle(title, fontsize=10); fig.savefig(path, dpi=150); plt.close(fig)


def fig_3d(S, out_below, out_above):
    clip = box(X0 - 6, -1, 38, X0 + 26, 90, 61)
    hw = S['bolts'][:1] + S['plungers'][:1] + S['pulls'][:1]
    items = [(common(S['brass'], clip), C['brass']), (common(S['tpu'], clip), C['TPU'])] + \
            [(common(s, clip), C['bolt']) for s in S['bolts'][:1]] + [(S['rollers'][0], C['roller'])] + \
            [(common(S['heads'][DESIGN_CASE], clip), C['corner screw'])]
    picture(items, -35, -130, 'Brass (yellow) and TPU (red) from below, first 90 mm, with a top roller (blue) and the strip '
            f'corner screw (grey) at the {DESIGN_CASE}.\nCarriage-top, base and strip hidden.', out_below)
    items = [(common(S['brass'], clip), C['brass']), (common(S['tpu'], clip), C['TPU'])] + \
            [(common(s, clip), C['bolt']) for s in S['bolts'][:2]] + [(s, C['plunger']) for s in S['plungers'][:1]] + \
            [(s, C['pull screw']) for s in S['pulls'][:1]]
    picture(items, 35, -130, 'Brass and TPU from above, first 90 mm: spring plunger (teal), pull screw (purple), '
            'locking bolts (dark grey)', out_above)
