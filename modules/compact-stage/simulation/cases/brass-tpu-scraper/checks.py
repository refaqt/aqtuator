"""Fit checks for the brass and TPU scraper. Returns a dict of values and a list of failures."""
from design import *  # noqa: F401,F403


def overlap(a, b):
    c = common(a, b)
    return round(vol(c), 3)


def void_near(shape, x0, y0, z0, x1, y1, z1):
    """Empty space of a part inside a box: the box minus the part."""
    return cut(box(x0, y0, z0, x1, y1, z1), shape)


def run():
    top2 = carriage_top_new()
    br, tp, tpb = brass(), tpu(), tpu_body_only()
    bl, pl, ps, rol = bolts(), plungers(), pull_screws(), rollers()
    v, fail = {}, []

    def check(name, value, ok):
        v[name] = value
        if not ok:
            fail.append(f'{name} = {value}')

    # Overlaps that must be zero
    for name, a in [('brass', br), ('TPU', tp)]:
        check(f'{name} overlaps carriage-top (with the new pocket and holes)', overlap(a, top2), overlap(a, top2) < 1e-3)
        check(f'{name} overlaps carriage-bottom', overlap(a, BOT), overlap(a, BOT) < 1e-3)
        a_b = tpb if name == 'TPU' else a      # the free lip tips reach below the strip: that is the press-in
        check(f'{name}{" body" if name == "TPU" else ""} overlaps the base', overlap(a_b, BASE), overlap(a_b, BASE) < 1e-3)
        check(f'{name} overlaps a top roller', sum(overlap(a, r) for r in rol), sum(overlap(a, r) for r in rol) < 1e-3)
    check('brass overlaps the TPU', overlap(br, tp), overlap(br, tp) < 1e-3)
    check('brass overlaps the strip', overlap(br, STRIP), overlap(br, STRIP) < 1e-3)
    check('TPU body (without lips) overlaps the strip', overlap(tpb, STRIP), overlap(tpb, STRIP) < 1e-3)
    hw = sum(overlap(s, top2) for s in bl + pl + ps)
    check('bolts, plungers and pull screws overlap carriage-top', round(hw, 3), hw < 1e-3)
    hw = sum(overlap(s, tp) for s in bl + pl + ps) + sum(overlap(s, br) for s in bl + pl + ps)
    check('bolts, plungers and pull screws overlap the brass or the TPU', round(hw, 3), hw < 1e-3)

    # Distances
    v['rib tip above the strip [mm]'] = round(dist(br, STRIP), 3)
    v['TPU lip interference, free tip below the strip top [mm]'] = INTERF
    v['brass to a top roller [mm]'] = round(min(dist(br, r) for r in rol), 2)
    v['TPU to a top roller [mm]'] = round(min(dist(tp, r) for r in rol), 2)
    v['brass to carriage-bottom [mm]'] = round(dist(br, BOT), 2)
    v['TPU to carriage-bottom [mm]'] = round(dist(tp, BOT), 2)

    # The corner screw heads, with the carriage at each end position
    for case in CARRIAGE_END_X:
        hd = head_at(case)
        sw = head_swept(case)
        for name, a in [('brass', br), ('TPU', tp), ('carriage-top', top2)]:
            o = overlap(a, sw)
            key = f'{name} over the swept corner screw head (+{CLEAR} mm), {case} [mm³]'
            if CARRIAGE_END_X[case] >= CARRIAGE_END_X[DESIGN_CASE]:
                check(key, o, o < 1e-3)
            else:
                v[key] = o
        v[f'brass to the corner screw head, {case} [mm]'] = round(dist(br, hd), 2) if overlap(br, hd) < 1e-3 else 'touches'

    # Walls next to the new holes
    v['M4 plunger hole to the end face [mm]'] = round(PLUNGER_XR - 3.3 / 2, 2)
    v['M2.5 counterbore to the end face [mm]'] = round(PULL_XR - PULL_CB_D / 2, 2)
    walls = []
    for y in BOLT_Y:
        hole = cyl_x(POCKET_L, y, BOLT_Z, TAP_D / 2, TAP_DEPTH)
        vd = void_near(TOP, X(POCKET_L + 0.05), y - 6, Z_UNDER - 2, X(POCKET_L + 25), y + 6, Z_CEIL + 6)
        walls.append(dist(hole, vd))
    v['M3 tapped hole to the slope opening, smallest wall [mm]'] = round(min(walls), 2)
    walls = []
    for y in (25.0, 105.0, 185.0):
        z0 = Z_CEIL_BRIDGE + 0.05 if BRIDGE_Y[0] < y < BRIDGE_Y[1] else 51.6   # above the roller pockets (z 51.5)
        vd = void_near(TOP, X(1.5), y - 3.5, z0, X(8.5), y + 3.5, 59.9)
        pk = prism(pocket_plan(), Z_UNDER - 1.0, Z_CEIL_BRIDGE)
        pk = fuse(pk, prism(pocket_plan().difference(bridge_plan()), Z_CEIL_BRIDGE - 0.01, Z_CEIL))
        walls.append((y, round(dist(pk, vd), 2)))
    for y, w in walls:
        check(f'pocket to the M5 cross-table hole at y = {y:.0f} mm [mm]', w, w > 0.5)
    v['brass mass [g] (typical density 8.5 g/cm³)'] = round(vol(br) * BRASS_DENSITY / 1000, 1)
    v['brass weight [N]'] = round(vol(br) * BRASS_DENSITY / 1000 * 9.81 / 1000, 2)
    v['TPU volume [cm³]'] = round(vol(tp) / 1000, 2)
    return v, fail


if __name__ == '__main__':
    import json
    v, fail = run()
    print(json.dumps(v, indent=1, ensure_ascii=False))
    print('FAILED' if fail else 'all checks pass', fail)
