# 2026-10-21 — The two carriage halves screw together in the compact stage

**Role(s):** cad, architecture

## Goal

Join carriage-top and carriage-bottom in the compact-stage assembly with a mounting frame on each
part. Add the M4 threaded holes in carriage-bottom for the six screws that come down through
carriage-top.

## Work Done

- **How the halves fit.** The two side strips of carriage-bottom sit in the two side pockets under
  carriage-top. The top of each strip touches the ceiling of its pocket. Over the middle of
  carriage-bottom, carriage-top stays 2 mm higher. The ends of carriage-top stay 0.5 mm above the
  base.
- **Each part now has a frame for the joint.** Both frames sit on the contact plane, at the centre
  of the carriage. They follow the size of the parts, so they move when the parts change.
- **Six threaded M4 holes in carriage-bottom.** They sit under the six counterbored holes that
  carriage-top already had: three in the middle of each side strip, 74.1 mm apart. The holes are
  blind, 9 mm deep, because the base wall is only 0.5 mm under the strips. A through hole would let
  a long screw touch the base and stop the carriage.
- **Use M4x12 screws.** About 8 mm of the screw goes into the thread. That is about two times the
  screw size, which is the usual length for a thread in aluminium.
- **No screw in the middle.** carriage-top had a countersunk hole in its centre. Niels removed it,
  because the sealing strip runs there, in the 2 mm gap between the two halves.
- **The base is now see-through in its own file.** The base Body is saved at 70% transparency. This
  changes how the base looks in every assembly, not only in compact-stage.
- **The assembly is checked.** carriage-top is now fixed to carriage-bottom with a joint. The two
  halves do not overlap, and carriage-top does not touch the base, the forcer or the read head.
  The holes in the two parts line up.

## Open Questions

- **The six screws must hold carriage-top flat on their own.** Over the middle, carriage-top
  rests on nothing. No stress check of carriage-top has been done yet.

<details>
<summary>Technical notes</summary>

- Port: `CarriageJointInterface_v1` in `modules/compact-stage/architecture/compact-stage.sysml`,
  with `holePitch = 74.1 mm` and `screwCount = 6`. Frame name `IF_carriage_joint` follows the port
  `carriageJoint`.
- carriage-bottom: `Frame006` (`IF_carriage_joint`) on `XY_Plane001`, offset
  `x = Sketch.Constraints.w_carrier / 2`, `y = Sketch.Constraints.l_carrier / 2`, `z = Pad.Length`,
  rotated -90° about Z so X points to the start end (y = 0).
- carriage-top: `Frame` (`IF_carriage_joint`) on `XY_Plane001`, offset `z = Pocket001.Length`
  (the 11 mm side pockets), no rotation.
- Holes: `Sketch032` on the Body XY plane at `Pad.Length`, zero degrees of freedom. Named
  constraints `joint_hole_x = Pad001.Length / 2`, `joint_hole_mid_y = Sketch.Constraints.l_carrier / 2`,
  `joint_hole_pitch = 74.1 mm` (typed, copied from `Sketch004` of carriage-top),
  `joint_hole_span = w_carrier - 2 * joint_hole_x`. `Hole004`: M4x0.7, threaded, not modelled,
  3.3 mm, 9 mm deep, angled point, so 1 mm of material stays under each hole.
- carriage-top: the countersunk centre hole (`Sketch005`, `Hole001`) is deleted. carriage-top
  in compact-stage uses its own 70% transparency (Override Material on the link).
- Typed numbers left: `joint_hole_pitch` and the 4 mm sketch circle (the Hole sets the size), and
  the 9 mm depth.
- Joint: `Fixed_carriage_joint` in the compact-stage `Joints` group, `Frame006.XY_Plane008` on
  carriage-bottom to `Frame.XY_Plane002` on carriage-top, no offset. After solving, carriage-top
  sits at z = 40.5 to 60 mm. Overlap volume with carriage-bottom and base: 0. Distance to base: 0.5 mm.

</details>
