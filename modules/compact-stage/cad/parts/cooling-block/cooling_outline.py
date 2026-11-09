"""Constrained sketches shared by the cooling block and its pocket in carriage-bottom.

The block and the pocket have the same outline. The block is smaller by
`cooling_block_gap` on every side. So one function draws both: `inset` is the
expression of that gap ("0" for the pocket).

Every sketch here uses carriage-bottom coordinates (x, y in mm, from the
carriage-bottom origin). A part that has another origin moves the sketch with
its attachment offset, so the numbers in the sketch stay the same as in
carriage-bottom. Every sketch is fully constrained: relations first, then
dimensions bound to the `Params` sheet. No dimension is a typed number.
"""

import math

P = "Params."


def _line_dir(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return dx / n, dy / n


def _fillet(p_prev, corner, p_next, r):
    """Tangent points and centre of a fillet of radius r at `corner`.

    Returns (t1, t2, centre, convex) where t1 lies on the segment from
    p_prev and t2 on the segment to p_next. `convex` is True for a left turn
    (counter-clockwise outline).
    """
    d1 = _line_dir(p_prev, corner)
    d2 = _line_dir(corner, p_next)
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    dot = d1[0] * d2[0] + d1[1] * d2[1]
    turn = math.atan2(cross, dot)
    t = r * math.tan(abs(turn) / 2)
    t1 = (corner[0] - d1[0] * t, corner[1] - d1[1] * t)
    t2 = (corner[0] + d2[0] * t, corner[1] + d2[1] * t)
    side = 1 if cross > 0 else -1
    centre = (t1[0] - side * d1[1] * r, t1[1] + side * d1[0] * r)
    return t1, t2, centre, cross > 0


def _intersect(p1, d1, p2, d2):
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    s = ((p2[0] - p1[0]) * (-d2[1]) - (p2[1] - p1[1]) * (-d2[0])) / det
    return p1[0] + d1[0] * s, p1[1] + d1[1] * s


def _closed_fillet_loop(sk, lines, radii, constrain_line):
    """Draw a closed loop of lines with a fillet at every corner and constrain it.

    `lines` is a list of (point, direction) for each infinite line, in
    counter-clockwise order. `radii` holds (value, expression) per corner,
    where corner k joins line k and line k+1. `constrain_line(i, geo_id)`
    adds the two constraints that place line i.
    """
    import FreeCAD
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    n = len(lines)
    corners = [_intersect(lines[k][0], lines[k][1], lines[(k + 1) % n][0], lines[(k + 1) % n][1])
               for k in range(n)]
    fil = []
    for k in range(n):
        prev_c = corners[k - 1]
        next_c = corners[(k + 1) % n]
        fil.append(_fillet(prev_c, corners[k], next_c, radii[k][0]))

    line_ids = []
    for i in range(n):
        start = fil[i - 1][1]   # tangent point of the corner before, on line i
        end = fil[i][0]         # tangent point of the corner after, on line i
        line_ids.append(sk.addGeometry(Part.LineSegment(V(*start, 0), V(*end, 0)), False))
    arc_ids = []
    for k in range(n):
        t1, t2, c, convex = fil[k]
        a1 = math.atan2(t1[1] - c[1], t1[0] - c[0])
        a2 = math.atan2(t2[1] - c[1], t2[0] - c[0])
        circle = Part.Circle(V(*c, 0), V(0, 0, 1), radii[k][0])
        if convex:
            while a2 < a1:
                a2 += 2 * math.pi
            arc = Part.ArcOfCircle(circle, a1, a2)
        else:
            while a1 < a2:
                a1 += 2 * math.pi
            arc = Part.ArcOfCircle(circle, a2, a1)
        arc_ids.append((sk.addGeometry(arc, False), convex))

    for i, gid in enumerate(line_ids):
        constrain_line(i, gid)
    for k, (aid, convex) in enumerate(arc_ids):
        before, after = line_ids[k], line_ids[(k + 1) % n]
        # A convex arc runs from line k to line k+1; a concave one the other way.
        if convex:
            sk.addConstraint(Sketcher.Constraint("Tangent", before, 2, aid, 1))
            sk.addConstraint(Sketcher.Constraint("Tangent", aid, 2, after, 1))
        else:
            sk.addConstraint(Sketcher.Constraint("Tangent", before, 2, aid, 2))
            sk.addConstraint(Sketcher.Constraint("Tangent", aid, 1, after, 1))
        _dim(sk, Sketcher.Constraint("Radius", aid, radii[k][0]), radii[k][1])
    return line_ids


def _dim(sk, constraint, expr, name=None):
    index = sk.addConstraint(constraint)
    if name:
        sk.renameConstraint(index, name)
    sk.setExpression(f"Constraints[{index}]", expr)
    return index


def _centre_line(sk, v):
    """Construction line along the diagonal part of the arm centre line."""
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    a = (v("cooling_arm_x0"), v("cooling_arm_y0"))
    b = (v("cooling_arm_bend_x"), v("cooling_arm_y"))
    cl = sk.addGeometry(Part.LineSegment(V(*a, 0), V(*b, 0)), True)
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, cl, 1, a[0]), f"{P}cooling_arm_x0")
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, cl, 1, a[1]), f"{P}cooling_arm_y0")
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, cl, 2, b[0]), f"{P}cooling_arm_bend_x")
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, cl, 2, b[1]), f"{P}cooling_arm_y")
    return cl, a, b


def outline(sk, v, inset, inset_expr, end_x, end_x_expr):
    """The outline of the block (inset = gap) or of its pocket (inset = 0).

    Eight lines, counter-clockwise from the bottom of the wide part: bottom,
    lower diagonal, lower arm side, arm end, upper arm side, upper diagonal,
    top, left end. A fillet joins every pair. `v(alias)` reads a parameter.
    """
    import Sketcher

    cl, a, b = _centre_line(sk, v)
    d = _line_dir(a, b)
    nrm = (-d[1], d[0])
    half = v("cooling_arm_w") / 2 - inset
    e_half = f"({P}cooling_arm_w / 2 - {inset_expr})"
    y0 = v("cooling_body_y0") + inset
    y1 = v("cooling_body_y1") - inset
    x0 = v("cooling_body_x0") + inset
    ya = v("cooling_arm_y")
    lines = [
        ((0, y0), (1, 0)),
        ((a[0] - nrm[0] * half, a[1] - nrm[1] * half), d),
        ((0, ya - half), (1, 0)),
        ((end_x, 0), (0, 1)),
        ((0, ya + half), (-1, 0)),
        ((a[0] + nrm[0] * half, a[1] + nrm[1] * half), (-d[0], -d[1])),
        ((0, y1), (-1, 0)),
        ((x0, 0), (0, -1)),
    ]
    r_arm, r_end, r_body = v("cooling_arm_r"), v("cooling_end_r"), v("cooling_body_r")
    convex = lambda r, e: (r - inset, f"{P}{e} - {inset_expr}")
    concave = lambda r, e: (r + inset, f"{P}{e} + {inset_expr}")
    radii = [convex(r_arm, "cooling_arm_r"), concave(r_arm, "cooling_arm_r"),
             convex(r_end, "cooling_end_r"), convex(r_end, "cooling_end_r"),
             convex(r_arm, "cooling_arm_r"), concave(r_arm, "cooling_arm_r"),
             convex(r_body, "cooling_body_r"), convex(r_body, "cooling_body_r")]

    def place(i, gid):
        if i in (0, 2, 4, 6):
            sk.addConstraint(Sketcher.Constraint("Horizontal", gid))
            expr = {0: f"{P}cooling_body_y0 + {inset_expr}",
                    2: f"{P}cooling_arm_y - {e_half}",
                    4: f"{P}cooling_arm_y + {e_half}",
                    6: f"{P}cooling_body_y1 - {inset_expr}"}[i]
            value = {0: y0, 2: ya - half, 4: ya + half, 6: y1}[i]
            _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, gid, 1, value), expr)
        elif i in (3, 7):
            sk.addConstraint(Sketcher.Constraint("Vertical", gid))
            expr = end_x_expr if i == 3 else f"{P}cooling_body_x0 + {inset_expr}"
            value = end_x if i == 3 else x0
            _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, gid, 1, value), expr)
        else:
            sk.addConstraint(Sketcher.Constraint("Parallel", gid, cl))
            _dim(sk, Sketcher.Constraint("Distance", cl, 1, gid, half), e_half)

    return _closed_fillet_loop(sk, lines, radii, place)


def rounded_rect(sk, x0, x1, y0, y1, r, e):
    """A rectangle with four equal fillets. `e` maps 'x0','x1','y0','y1','r' to expressions."""
    import Sketcher

    lines = [((0, y0), (1, 0)), ((x1, 0), (0, 1)), ((0, y1), (-1, 0)), ((x0, 0), (0, -1))]
    radii = [(r, e["r"])] * 4

    def place(i, gid):
        if i in (0, 2):
            sk.addConstraint(Sketcher.Constraint("Horizontal", gid))
            _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, gid, 1, y0 if i == 0 else y1),
                 e["y0"] if i == 0 else e["y1"])
        else:
            sk.addConstraint(Sketcher.Constraint("Vertical", gid))
            _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, gid, 1, x1 if i == 1 else x0),
                 e["x1"] if i == 1 else e["x0"])

    return _closed_fillet_loop(sk, lines, radii, place)


def circles(sk, points):
    """Circles at fixed centres. `points` holds ((x, y, r), (ex, ey, er))."""
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    ids = []
    for (x, y, r), (ex, ey, er) in points:
        g = sk.addGeometry(Part.Circle(V(x, y, 0), V(0, 0, 1), r), False)
        _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, g, 3, x), ex)
        _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, g, 3, y), ey)
        _dim(sk, Sketcher.Constraint("Radius", g, r), er)
        ids.append(g)
    return ids


def passage_spine(sk, v, side):
    """Path of one water passage in the plan view, from its port to its fitting.

    side = -1: port A, the lower passage. side = +1: port B, the upper one.
    Five lines: along X from the port, parallel to the arm diagonal, along X in
    the arm, a short jog to the fitting axis, along X to the fitting.
    """
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    cl, a, b = _centre_line(sk, v)
    d = _line_dir(a, b)
    nrm = (-d[1], d[0])
    off = v("cooling_passage_offset")
    port = "port_a" if side < 0 else "port_b"
    px, py = v(f"{port}_x"), v(f"{port}_y")
    ya = v("cooling_arm_y")
    y_arm = ya + side * off
    y_fit = ya + side * v("fit_pitch") / 2
    x_j0, x_j1 = v("fit_jog_x0"), v("fit_jog_x1")
    x_end = (v("carriage_edge_x") + v("cooling_block_gap") + v("fit_head_l")
             - v("fit_tap_depth") + v("cooling_passage_d") / 2)
    diag_p = (a[0] + side * nrm[0] * off, a[1] + side * nrm[1] * off)
    k1 = _intersect((px, py), (1, 0), diag_p, d)
    k2 = _intersect(diag_p, d, (0, y_arm), (1, 0))
    pts = [(px, py), k1, k2, (x_j0, y_arm), (x_j1, y_fit), (x_end, y_fit)]
    ids = [sk.addGeometry(Part.LineSegment(V(*pts[i], 0), V(*pts[i + 1], 0)), False) for i in range(5)]
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", ids[i], 2, ids[i + 1], 1))
    sign = "-" if side < 0 else "+"
    sk.addConstraint(Sketcher.Constraint("Horizontal", ids[0]))
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, ids[0], 1, px), f"{P}{port}_x")
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, ids[0], 1, py), f"{P}{port}_y")
    sk.addConstraint(Sketcher.Constraint("Parallel", ids[1], cl))
    _dim(sk, Sketcher.Constraint("Distance", cl, 1, ids[1], off), f"{P}cooling_passage_offset")
    sk.addConstraint(Sketcher.Constraint("Horizontal", ids[2]))
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, ids[2], 1, y_arm),
         f"{P}cooling_arm_y {sign} {P}cooling_passage_offset")
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, ids[2], 2, x_j0), f"{P}fit_jog_x0")
    sk.addConstraint(Sketcher.Constraint("Horizontal", ids[4]))
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, ids[4], 1, y_fit),
         f"{P}cooling_arm_y {sign} {P}fit_pitch / 2")
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, ids[4], 1, x_j1), f"{P}fit_jog_x1")
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, ids[4], 2, x_end),
         f"{P}carriage_edge_x + {P}cooling_block_gap + {P}fit_head_l - {P}fit_tap_depth"
         f" + {P}cooling_passage_d / 2")
    return ids


def rect(sk, x0, x1, y0, y1, e):
    """A rectangle with square corners. `e` maps 'x0','x1','y0','y1' to expressions."""
    import Part
    import Sketcher
    from FreeCAD import Vector as V

    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    ids = [sk.addGeometry(Part.LineSegment(V(*pts[i], 0), V(*pts[(i + 1) % 4], 0)), False)
           for i in range(4)]
    for i in range(4):
        sk.addConstraint(Sketcher.Constraint("Coincident", ids[i], 2, ids[(i + 1) % 4], 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", ids[0]))
    sk.addConstraint(Sketcher.Constraint("Horizontal", ids[2]))
    sk.addConstraint(Sketcher.Constraint("Vertical", ids[1]))
    sk.addConstraint(Sketcher.Constraint("Vertical", ids[3]))
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, ids[0], 1, x0), e["x0"])
    _dim(sk, Sketcher.Constraint("DistanceX", -1, 1, ids[0], 2, x1), e["x1"])
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, ids[0], 1, y0), e["y0"])
    _dim(sk, Sketcher.Constraint("DistanceY", -1, 1, ids[2], 1, y1), e["y1"])
    return ids
