// The compact stage: its requirements, its parts, and the interfaces between
// its parts.
//
// Requirements: STG-01 to STG-14 hold for the whole stage: its size, its
// accuracy, its speed, its force and its load. A design review or a
// measurement campaign can cite each one by its short name. The servo drive
// has its own requirements in motor-drive.sysml.
//
// Rule for a pass or a fail: a bought part (a guide, a motor, an encoder)
// passes only on the deciding number in the maker's own data sheet or
// manual. A trade article, a shop page or a search result is not enough.
// See docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md.
//
// Every error value is a half band: "5 µm" means "within +/- 5 µm".
//
// Structure:
//
// The compact stage is one assembly of five parts that we make:
//
//   compact-stage
//     base             the fixed body; it mounts on the machine
//     carriage-bottom  the moving part inside the base
//     carriage-top     the moving part above the base; the load mounts on it
//     sealing-strip    a strip that closes the slot in the top of the base
//     sealing-clamp    holds one end of the strip on the base (two of them)
//
// The CAD of each part is in cad/parts/<part>/. The assembly is in
// cad/assemblies/compact-stage/.
//
// Rule: every pair of parts that touch has an interface. The interface is a
// port def below, a port on each part (the plain port on one side, the
// conjugate ~ port on the other), and a connection in CompactStage. The
// version is part of the name: a change that no longer fits the old part is
// a new version (_v2), not an edit of _v1.
//
// Bought parts come from the parts library in modules/stoq/. The two guide
// rails and the two magnet tracks (stators) of the linear motor are in this
// file, with their interfaces to the base. The four guide blocks and the
// forcer (the coil part of the motor) are in this file, with their
// interfaces to carriage-bottom. The linear encoder is in this file too: the
// read head on carriage-bottom, the scale on the base.
// Not modelled yet: the rollers and the screws. When they enter this file,
// they bring their own interfaces: for example roller to sealing strip.
//
// Not modelled yet either: the interface between a guide block and its
// rail. It needs a choice first: which row of blocks (a or b) runs on the
// reference rail.
//
// The interfaces below say what joins what. Most hold no dimensions yet.
// Add a dimension when the CAD fixes it, and keep it the same in both.
package CompactStage {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;

    // ---------------------------------------------------------------------
    // Interfaces to the outside. These are the interfaces of the whole
    // module, and okh.toml lists them too, under [[provides-interface]].
    // ---------------------------------------------------------------------

    port def BaseMountInterface_v1 {
        doc /*
         * The bottom face of the base, where the stage screws onto the
         * machine. The screw holes follow the grid of STG-14.
         */
        attribute holePitch : LengthValue;
    }

    port def CarriageMountInterface_v1 {
        doc /*
         * The top face of carriage-top, where the load screws onto the
         * stage. The screw holes follow the grid of STG-14.
         */
        attribute holePitch : LengthValue;
    }

    // ---------------------------------------------------------------------
    // Interfaces between the parts of the stage
    // ---------------------------------------------------------------------

    port def CarriageJointInterface_v1 {
        doc /*
         * carriage-bottom and carriage-top screw together, and move as one
         * body. carriage-bottom is screwed onto the guide blocks. It has no
         * connection with the base.
         *
         * The sealing strip runs through the carriage, over carriage-bottom
         * and under carriage-top. The strip never touches either carriage
         * half, so the strip has no interface with them. Only the rollers
         * in the carriage touch the strip. They are bought parts and come
         * later.
         *
         * The two side strips of carriage-bottom (11 mm wide) sit in the
         * two side pockets under carriage-top. The top of each strip
         * touches the ceiling of its pocket. Over the middle of
         * carriage-bottom, carriage-top stays 2 mm higher. The ends of
         * carriage-top stay 0.5 mm above the base.
         *
         * Six M4 screws go down through carriage-top into carriage-bottom:
         * three in the middle of each side strip, 74.1 mm apart along the
         * travel, the middle one at the centre of the carriage. Each hole
         * in carriage-top has a counterbore for the screw head. In
         * carriage-bottom the holes are threaded and blind, 9 mm deep,
         * because the base is only 0.5 mm under the strips. Use M4x12
         * screws (ISO 4762): about 8 mm of the screw goes into the thread.
         * A screw longer than 12 mm can touch the bottom of the hole.
         *
         * There is no screw in the middle of the carriage. The sealing
         * strip runs there, in the 2 mm gap between the two halves.
         *
         * In the CAD, the frame IF_carriage_joint sits on the contact
         * plane, at the centre of the carriage, in both parts. Z points
         * up, from carriage-bottom into carriage-top. X runs along the
         * travel, towards the start of the carriage. The two frames are
         * the same place, so the joint needs no offset.
         */
        attribute holePitch : LengthValue = 74.1 [mm];      // along the travel
        attribute screwCount : Natural = 6;
    }

    port def BlockMountInterface_v1 {
        doc /*
         * A guide block screws to the bottom face of carriage-bottom. The
         * block sits in a pocket. Its top face touches the floor of the
         * pocket. Two M4 screws go down through the carriage into the
         * threaded holes of the block. Each hole has a counterbore on the
         * top face of the carriage for the screw head.
         *
         * The carriage has four blocks, in two rows along the travel.
         * Row a is at x = 35 mm in the carriage, row b at x = 173 mm.
         * "Start" is the end of the carriage where the motor cable leaves
         * (y = 21 mm), "end" is the other end (y = 159 mm). The names do
         * not say which row runs on the reference rail.
         *
         * The lubrication unit (E2) of each block points out of the
         * carriage, away from its centre.
         *
         * In the CAD, the frames IF_block_a_start_mount,
         * IF_block_b_start_mount, IF_block_a_end_mount and
         * IF_block_b_end_mount sit on the floor of each pocket, at the
         * centre of the two holes. Z points down, into the block. X runs
         * along the rail, from the end of the carriage towards its
         * centre. They join the frame IF_mount_top of the block.
         */
        attribute holePitch : LengthValue = 26 [mm];        // across the rail
        attribute holesPerBlock : Natural = 2;
    }

    port def ForcerMountInterface_v1 {
        doc /*
         * The forcer of the linear motor screws to the bottom face of
         * carriage-bottom. It sits in a pocket between the rows of guide
         * blocks, with its coils facing down, towards the magnet tracks.
         * The hole pattern sits 16 mm off the centre of the carriage,
         * away from the cable end. That leaves room for a slot for the
         * motor cable.
         * Six M4 screws go down through the carriage into the threaded
         * holes of the forcer. The screw length is not chosen yet.
         *
         * The holes are in two rows along the travel. The cable end of
         * the forcer points to the start of the carriage, where the cable
         * slot is.
         *
         * In the CAD, the frame IF_forcer_mount sits on the floor of the
         * pocket, on the middle hole, halfway between the rows. Z points
         * down, into the forcer. X runs along the travel, away from the
         * cable end. It joins the frame IF_mount_top of the forcer.
         */
        attribute holePitch : LengthValue = 35 [mm];        // along the travel
        attribute rowSpacing : LengthValue = 50 [mm];
        attribute holesPerRow : Natural = 3;
    }

    port def SlotSealInterface_v1 {
        doc /*
         * The sealing strip lies on the top of the base and closes the slot
         * along the whole travel.
         */
    }

    port def StripClampInterface_v1 {
        doc /* A sealing clamp holds one end of the sealing strip. */
    }

    port def ClampMountInterface_v1 {
        doc /* A sealing clamp screws onto one end of the base. */
    }

    port def RailMountInterface_v1 {
        doc /*
         * A guide rail lies on the floor of the base. The floor is 3 mm
         * below the tops of the tabs. M4 screws go through the rail from
         * above into threaded holes in the base. The holes go through the
         * 10 mm floor. Use M4 x 16 screws: they engage 6.3 mm of thread.
         * The M4 x 20 screw that HIWIN lists would come out of the bottom
         * face by 0.3 mm.
         *
         * The tabs stand out from the side walls of the base, and each rail
         * lies against them with its outer side. Its inner side touches
         * nothing. Each tab is 20 mm long and starts 19 mm in from the end
         * of the rail, so it never touches the rail end. The rounded
         * corners at the foot of each tab stay 4.5 mm away from the rail.
         *
         * The reference rail (y = 174 mm) lies against two tabs, one near
         * each end. The tabs set its position and its direction.
         *
         * The second rail (y = 36 mm) lies against one tab, near one end.
         * The tab sets its position at that end only. To set its
         * direction, put the carriage on both rails and move it from end
         * to end while you tighten the screws of the second rail, one after
         * the other. HIWIN calls this "alignment on the reference rail".
         *
         * The y positions are rail centres, measured from the long side of
         * the base. The rails are 138 mm apart, the same as the rows of
         * guide blocks in carriage-bottom. The first hole is 40 mm from
         * the end of the base.
         *
         * The base is 210 mm wide. The pocket between the side walls is
         * 176 mm wide, so each wall is 17 mm thick. Each guide block has
         * 2 mm of space to the wall. The tabs follow the rails:
         * in the CAD, their depth is a formula of the rail position.
         *
         * In the CAD, the base has the frames IF_reference_rail_mount and
         * IF_second_rail_mount. Each sits on the floor (z = 10 mm), on the
         * first hole of its rail. X runs along the rail, Z points up. A
         * Fixed joint to the frame IF_mount_bottom of the rail puts the
         * rail from x = 11 mm to x = 429 mm.
         */
        attribute holePitch : LengthValue = 60 [mm];
        attribute firstHoleOffset : LengthValue = 40 [mm];
        attribute railSpacing : LengthValue = 138 [mm];
        attribute holesPerRail : Natural = 7;
        attribute screwLength : LengthValue = 16 [mm];   // M4 x 16
    }

    port def StatorMountInterface_v1 {
        doc /*
         * A magnet track (stator) of the linear motor lies with its bottom
         * face on the floor of the base, between the two guide rails.
         * Screws go through the 5.5 mm holes of the stator into threaded
         * M5 holes in the base. The holes go through the 10 mm floor.
         *
         * Each stator has two rows of three holes. The rows are 74 mm
         * apart, on both sides of the centre line of the base. In a row,
         * the holes are 60 mm apart. The Maxwell data sheet drawing says
         * "A x 120" here. That is wrong: the holes are 60 mm apart.
         *
         * The two stators lie end to end, both with their N end towards
         * the start of the base. Their ends are cut at a slant, and they
         * fit into each other. The first hole of the first stator is
         * 70 mm from the start of the base. The second stator starts
         * 180 mm further on, the length LC of one stator.
         *
         * The stators are aligned with locating pins, not with milled
         * edges, so that stators of other lengths fit too. The pin holes
         * are not modelled yet. The screw length is not chosen yet.
         *
         * In the CAD, the frame IF_mount_bottom of the stator sits on its
         * first hole, at the N end, halfway between the rows.
         */
        attribute holePitch : LengthValue = 60 [mm];
        attribute rowSpacing : LengthValue = 74 [mm];
        attribute holesPerRow : Natural = 3;
        attribute statorPitch : LengthValue = 180 [mm];
    }

    port def ReadheadMountInterface_v2 {
        doc /*
         * The read head of the linear encoder screws to the bottom of
         * carriage-bottom. It hangs in a pocket on the side of the second
         * rail, with its scanning face towards the side wall of the base.
         * The 13.5 mm side face of the head touches the ceiling of the
         * pocket. The cable leaves the head towards the end of the base
         * (-X), the way the pocket leaves room for it.
         *
         * The pocket is 16 mm deep and the head is 13.5 mm, so the head
         * sits 2.5 mm inside the carriage. It stays 1 mm away from the
         * base and 4 mm away from the second rail. The pocket is 38 mm
         * long, and the head is 36 mm long and centred in it: 1 mm of
         * space at each end.
         *
         * Two M3 screws go down through the carriage into the head. The
         * two holes of the head are M3 threads through its full 13.5 mm.
         * Each hole in the carriage has a counterbore on its top face.
         * The screw passes 8.1 mm of carriage, so an M3 x 16 screw has
         * about 7.9 mm of thread in the head. RSF allows at most 1.2 Nm
         * (AK MC 15 mounting instructions, page 9). The parts library
         * reads at least 4 mm of thread from page 10; that page is a
         * drawing and was not checked again here.
         *
         * The holes are 26 mm apart, as in the head (RSF drawing
         * D1158017-04). Their axes are 3.0 mm from the step face of the
         * carriage at x = 17 mm (Sketch031 readhead_hole_inset). In the
         * head they are 3 mm from the scanning face, so the scanning face
         * is flush with the step face. That gives the gap of
         * ScaleReadInterface_v2. Along the travel, the midpoint of the
         * holes is 1 mm from the middle of the pocket, because the holes
         * are 4 mm and 6 mm from the two ends of the head. The holes are
         * 3.4 mm, so the head can move 0.2 mm each way: set the gap with
         * the 0.55 mm gap foil that comes with the head before you
         * tighten the screws.
         *
         * In the CAD, the frame IF_readhead_mount sits on the ceiling of
         * the pocket, midway between the two holes. Z points down, into
         * the head. X runs along the travel, towards the start of the
         * carriage. It joins the frame IF_mount_top of the head, with the
         * joint turned 180 degrees about Z, so the cable points to -X.
         */
        attribute holePitch : LengthValue = 26 [mm];
        attribute screwCount : Natural = 2;
    }

    port def ScaleMountInterface_v2 {
        doc /*
         * The steel tape scale of the linear encoder sticks with its
         * adhesive tape to the inside face of the side wall of the base,
         * on the side of the second rail (y = 17 mm). It needs no end
         * clamps. Stick it on with the RSF TMT Mx 15 MK mounting tool.
         * The wall face must be flat within 0.1 mm and parallel to the
         * guide rails within 0.2 mm (RSF drawing D1158017-04).
         *
         * The tape runs towards -X: its ascending positions point to the
         * end of the base, the same way as the head cable.
         *
         * In the CAD, the frame IF_scale_mount sits on the wall face, at
         * the start of the tape. Z points out of the wall, into the
         * scale. X points to -X. It joins the frame IF_mount_bottom of
         * the scale.
         *
         * Two values of the frame are in the Params sheet of the base.
         * They follow other parts, so change them when those parts
         * change:
         *
         * - x = Params.scale_start_x (361 mm): centres the 240 mm
         *   measuring length on the path of the head sensor between the
         *   two damper contacts (x = 120.8 to 342.8 mm). The tape then
         *   lies from x = 101 to 361 mm, and the measuring length from
         *   x = 111.8 to 351.8 mm.
         * - z = Params.scale_centre_z (34 mm): the sensor line of the
         *   head, 6 mm below the ceiling of its pocket in the carriage.
         *   The tape lies from z = 30 to 38 mm, under the top of the wall
         *   at 40 mm.
         */
    }

    port def ScaleReadInterface_v2 {
        doc /*
         * The read head reads the scale without touching it. The RSF
         * drawing D1158017-04 gives the limits:
         *
         * - the air gap from the top of the tape to the scanning face of
         *   the head is 0.55 +/- 0.25 mm;
         * - the sideways offset of the tape is within +/- 1 mm;
         * - roll, pitch and yaw are each within +/- 20 mrad.
         *
         * In the CAD, the frame IF_scale of the head and the frames
         * IF_ml_start and IF_ml_end of the scale have the same height and
         * the same direction. They differ only along the travel. The
         * assembly gives a gap of 0.55 mm and no sideways offset.
         *
         * Over the travel between the two damper contacts (222 mm), the
         * sensor stays 9 mm inside each end of the 240 mm measuring
         * length. With the dampers fully pressed (236 mm), it stays 2 mm
         * inside each end. The head reads over the full travel.
         */
        attribute gap : LengthValue = 0.55 [mm];
        attribute gapTolerance : LengthValue = 0.25 [mm];
        attribute measuringLength : LengthValue = 240 [mm];
    }

    port def DamperMountInterface_v1 {
        doc /*
         * End face of carriage-bottom where one TA17-7 damper screws on. M4
         * stud through a 4.5 mm slot into an M4 square nut. The damper axis is
         * Params.damper_axis_z above the bottom face.
         */
    }

    port def DamperStopInterface_v1 {
        doc /*
         * The impact face of one TA17-7 damper hits the back face of a
         * pocket in an end wall of the base. Each pocket is milled from the
         * top of the base: 7 mm deep into the 10 mm wall, 24 mm wide (the
         * damper grows to 22 mm across when fully pressed, ACE manual page
         * 3), inside corners R4 mm, floor at z = 17.5 mm. The sizes are in
         * the Params sheet of the base.
         *
         * In the CAD, the frames IF_damper_a_start_stop and so on sit on
         * the back face of each pocket, on the damper axis. Z points out of
         * the wall, towards the damper.
         */
    }

    // ---------------------------------------------------------------------
    // Parts. Each port says which side of an interface a part is on.
    // ---------------------------------------------------------------------

    part def Base {
        doc /* The fixed body of the stage. CAD: cad/parts/base/. */
        port machineMount : BaseMountInterface_v1;
        port slotSeal : SlotSealInterface_v1;
        port clampMountStart : ClampMountInterface_v1;
        port clampMountEnd : ClampMountInterface_v1;
        port referenceRailMount : RailMountInterface_v1;
        port secondRailMount : RailMountInterface_v1;
        port firstStatorMount : StatorMountInterface_v1;
        port secondStatorMount : StatorMountInterface_v1;
        port scaleMount : ScaleMountInterface_v2;
        port damperAStartStop : DamperStopInterface_v1;
        port damperBStartStop : DamperStopInterface_v1;
        port damperAEndStop : DamperStopInterface_v1;
        port damperBEndStop : DamperStopInterface_v1;
    }

    part def GuideRail {
        doc /*
         * A bought profile rail: HIWIN EGR15U, 418 mm long (EGR15U418H).
         * It takes the M4 screws of the base. It comes from the parts
         * library in modules/stoq/. The stage has two.
         */
        port baseMount : ~RailMountInterface_v1;
    }

    part def MagnetTrack {
        doc /*
         * A bought magnet track (stator) of the linear motor: Maxwell
         * MK2-180, 180 mm long. It comes from the parts library in
         * modules/stoq/. The stage has two, end to end.
         */
        port mountBottom : ~StatorMountInterface_v1;
    }

    part def CarriageBottom {
        doc /* The moving part inside the base. CAD: cad/parts/carriage-bottom/. */
        port carriageJoint : CarriageJointInterface_v1;
        port blockAStartMount : BlockMountInterface_v1;
        port blockAEndMount : BlockMountInterface_v1;
        port blockBStartMount : BlockMountInterface_v1;
        port blockBEndMount : BlockMountInterface_v1;
        port forcerMount : ForcerMountInterface_v1;
        port readheadMount : ReadheadMountInterface_v2;
        port damperAStartMount : DamperMountInterface_v1;
        port damperBStartMount : DamperMountInterface_v1;
        port damperAEndMount : DamperMountInterface_v1;
        port damperBEndMount : DamperMountInterface_v1;
    }

    part def GuideBlock {
        doc /*
         * A bought guide block: HIWIN QEH15SAZAP+E2, a light load block
         * with the E2 lubrication unit. It runs on the EGR15U rail. It
         * comes from the parts library in modules/stoq/. The stage has
         * four.
         */
        port mountTop : ~BlockMountInterface_v1;
    }

    part def Forcer {
        doc /*
         * The bought forcer (the coil part) of the linear motor: Maxwell
         * MK21. It runs over the MK2 magnet tracks. It comes from the
         * parts library in modules/stoq/. The stage has one.
         */
        port mountTop : ~ForcerMountInterface_v1;
    }

    part def ReadHead {
        doc /*
         * The bought read head of the linear encoder: RSF AK MC 15 B,
         * absolute, BiSS C, 0.1 um, 36 x 13.5 x 14.8 mm, with a 0.5 m
         * cable out of the end and a 15-pin D-sub connector. Bought:
         * stoq:rsf/mc15-readhead#AK-MC15-B-0.5M-SUBD15. The stage has one.
         */
        port carriageMount : ~ReadheadMountInterface_v2;
        port scaleRead : ~ScaleReadInterface_v2;
    }

    part def Scale {
        doc /*
         * The bought steel tape scale of the linear encoder: RSF MC 15 MK,
         * 240 mm measuring length, 260 mm long, with adhesive tape.
         * Bought: stoq:rsf/mc15-mk-scale#MB-MC15-MK-ML240. The stage has
         * one.
         */
        port baseMount : ~ScaleMountInterface_v2;
        port headRead : ScaleReadInterface_v2;
    }

    part def CarriageTop {
        doc /*
         * The moving part above the base. The load mounts on it.
         * CAD: cad/parts/carriage-top/.
         */
        port loadMount : CarriageMountInterface_v1;
        port carriageJoint : ~CarriageJointInterface_v1;
    }

    part def SealingStrip {
        doc /* Closes the slot in the top of the base. CAD: cad/parts/sealing-strip/. */
        port slotSeal : ~SlotSealInterface_v1;
        port clampStart : ~StripClampInterface_v1;
        port clampEnd : ~StripClampInterface_v1;
    }

    part def SealingClamp {
        doc /*
         * Holds one end of the sealing strip on the base. The stage has two,
         * one at each end. CAD: cad/parts/sealing-clamp/.
         */
        port strip : StripClampInterface_v1;
        port baseMount : ~ClampMountInterface_v1;
    }

    // ---------------------------------------------------------------------
    // The assembly
    // ---------------------------------------------------------------------

    part def CompactStage {
        doc /*
         * The whole compact stage: one design, or one built stage. Fill in
         * the attributes from the CAD model, the data sheets and the
         * measurements. CompactStageSpecification checks them.
         * CAD: cad/assemblies/compact-stage/.
         */

        // Size
        attribute travel : LengthValue;      // usable stroke of the carriage
        attribute width : LengthValue;       // across the direction of motion
        attribute height : LengthValue;      // from the mounting face to the top of the carriage
        attribute length : LengthValue;      // largest length in the direction of motion

        // Accuracy (each value is a half band: +/- this value)
        attribute positioningError : LengthValue;           // systematic and random, uncalibrated
        attribute straightnessError : LengthValue;          // linear error motion across the motion
        attribute flatnessError : LengthValue;              // linear error motion across the motion
        attribute rollError : Real;                         // rad
        attribute pitchError : Real;                        // rad
        attribute yawError : Real;                          // rad
        attribute unidirectionalRepeatability : LengthValue;
        attribute bidirectionalRepeatability : LengthValue;

        // Motion and drive
        attribute maxSpeed : SpeedValue;
        attribute continuousForce : ForceValue;   // driving force along the motion
        attribute peakForce : ForceValue;         // driving force along the motion
        attribute maxOutputPower : PowerValue;    // mechanical: force times speed

        // Load and interfaces
        attribute lateralLoadCapacity : ForceValue;  // at the centre, in either direction
        attribute interfaceHolePitch : LengthValue;  // pitch of the screw holes at each interface

        part base : Base;
        part carriageBottom : CarriageBottom;
        part carriageTop : CarriageTop;
        part sealingStrip : SealingStrip;
        part sealingClampStart : SealingClamp;
        part sealingClampEnd : SealingClamp;
        part referenceRail : GuideRail;
        part secondRail : GuideRail;
        part firstStator : MagnetTrack;
        part secondStator : MagnetTrack;
        part blockAStart : GuideBlock;
        part blockAEnd : GuideBlock;
        part blockBStart : GuideBlock;
        part blockBEnd : GuideBlock;
        part forcer : Forcer;
        part readHead : ReadHead;
        part scale : Scale;
        part damperAStart : EndStopDamper;
        part damperBStart : EndStopDamper;
        part damperAEnd : EndStopDamper;
        part damperBEnd : EndStopDamper;

        // Interfaces of the whole stage
        port machineMount : BaseMountInterface_v1;
        port loadMount : CarriageMountInterface_v1;
        bind machineMount = base.machineMount;
        bind loadMount = carriageTop.loadMount;

        // The carriage
        connect carriageBottom.carriageJoint to carriageTop.carriageJoint;

        // The seal
        connect base.slotSeal to sealingStrip.slotSeal;
        connect sealingClampStart.strip to sealingStrip.clampStart;
        connect sealingClampEnd.strip to sealingStrip.clampEnd;
        connect sealingClampStart.baseMount to base.clampMountStart;
        connect sealingClampEnd.baseMount to base.clampMountEnd;

        // The guide rails
        connect base.referenceRailMount to referenceRail.baseMount;
        connect base.secondRailMount to secondRail.baseMount;

        // The magnet tracks of the linear motor
        connect base.firstStatorMount to firstStator.mountBottom;
        connect base.secondStatorMount to secondStator.mountBottom;

        // The guide blocks and the forcer, under the carriage
        connect carriageBottom.blockAStartMount to blockAStart.mountTop;
        connect carriageBottom.blockAEndMount to blockAEnd.mountTop;
        connect carriageBottom.blockBStartMount to blockBStart.mountTop;
        connect carriageBottom.blockBEndMount to blockBEnd.mountTop;
        connect carriageBottom.forcerMount to forcer.mountTop;

        // The linear encoder: the head on the carriage, the scale on the base
        connect carriageBottom.readheadMount to readHead.carriageMount;
        connect base.scaleMount to scale.baseMount;
        connect scale.headRead to readHead.scaleRead;

        // DamperMount: one TA17-7 damper at each corner of the carriage ends
        connect carriageBottom.damperAStartMount to damperAStart.mount;
        connect carriageBottom.damperBStartMount to damperBStart.mount;
        connect carriageBottom.damperAEndMount to damperAEnd.mount;
        connect carriageBottom.damperBEndMount to damperBEnd.mount;

        // DamperStop: each damper hits a pocket in an end wall of the base
        connect base.damperAStartStop to damperAStart.stop;
        connect base.damperBStartStop to damperBStart.stop;
        connect base.damperAEndStop to damperAEnd.stop;
        connect base.damperBEndStop to damperBEnd.stop;
    }

    part def EndStopDamper {
        doc /*
         * End Stop Damper, bought: stoq:ace/ta-damper#TA17-7. From the parts
         * library in modules/stoq/.
         */
        port mount : ~DamperMountInterface_v1;
        port stop : ~DamperStopInterface_v1;
    }

    // ---------------------------------------------------------------------
    // Hard requirements. A design that fails one of these is rejected.
    // ---------------------------------------------------------------------

    package Mandatory {

        // --- Size ------------------------------------------------------------

        requirement def <'STG-01'> Width {
            doc /* The stage is at most 210 mm wide. */
            subject stage : CompactStage;
            require constraint { stage.width <= 210 [mm] }
        }

        requirement def <'STG-02'> Height {
            doc /* The stage is at most 60 mm high. */
            subject stage : CompactStage;
            require constraint { stage.height <= 60 [mm] }
        }

        requirement def <'STG-03'> Length {
            doc /*
             * The stage is at most (travel + 340 mm - 2 x height) long.
             *
             * The limit grows with the travel. A lower stage may be longer.
             * Example: a stage with 200 mm travel and 60 mm height may be
             * at most 200 + 340 - 120 = 420 mm long.
             */
            subject stage : CompactStage;
            require constraint {
                stage.length <= stage.travel + 340 [mm] - 2 * stage.height
            }
        }

        // --- Accuracy --------------------------------------------------------

        requirement def <'STG-04'> PositioningError {
            doc /*
             * The total positioning error along the motion is within
             * +/- 5 µm over the full travel. This counts the systematic and
             * the random part together, without any calibration or error
             * table in the controller.
             */
            subject stage : CompactStage;
            require constraint { stage.positioningError <= 5 [µm] }
        }

        requirement def <'STG-05'> LinearErrorMotion {
            doc /*
             * The carriage moves along a straight line within +/- 2 µm, in
             * both directions across the motion. This is the straightness
             * (sideways) and the flatness (up and down) over the full
             * travel. The positioning error along the motion is not part of
             * this requirement: see STG-04.
             */
            subject stage : CompactStage;
            require constraint {
                stage.straightnessError <= 2 [µm] and stage.flatnessError <= 2 [µm]
            }
        }

        requirement def <'STG-06'> RotationalErrorMotion {
            doc /*
             * The carriage tilts and turns by at most +/- 20 µrad over the
             * full travel, about each of the three axes: roll (about the
             * direction of motion), pitch and yaw.
             */
            subject stage : CompactStage;
            require constraint {
                stage.rollError <= 20.0E-6
                and stage.pitchError <= 20.0E-6
                and stage.yawError <= 20.0E-6
            }
        }

        requirement def <'STG-07'> UnidirectionalRepeatability {
            doc /*
             * The carriage returns to the same position within +/- 0.1 µm
             * when it always comes from the same direction.
             */
            subject stage : CompactStage;
            require constraint { stage.unidirectionalRepeatability <= 0.1 [µm] }
        }

        requirement def <'STG-08'> BidirectionalRepeatability {
            doc /*
             * The carriage returns to the same position within +/- 0.3 µm
             * when it comes from either direction. This includes the
             * backlash and the hysteresis of the stage.
             */
            subject stage : CompactStage;
            require constraint { stage.bidirectionalRepeatability <= 0.3 [µm] }
        }

        // --- Motion and drive -------------------------------------------------

        requirement def <'STG-09'> MaxSpeed {
            doc /*
             * The carriage reaches at least 3 m/s.
             *
             * The drive requirements in motor-drive.sysml use this speed.
             * The encoder frequency (DRV-08) and the bus voltage (DRV-04)
             * follow from it.
             */
            subject stage : CompactStage;
            require constraint { stage.maxSpeed >= 3 [m/s] }
        }

        requirement def <'STG-10'> ContinuousForce {
            doc /*
             * The stage pushes the carriage with at least 180 N without a
             * time limit.
             */
            subject stage : CompactStage;
            require constraint { stage.continuousForce >= 180 [N] }
        }

        requirement def <'STG-11'> PeakForce {
            doc /* The stage pushes the carriage with at least 500 N at its peak. */
            subject stage : CompactStage;
            require constraint { stage.peakForce >= 500 [N] }
        }

        requirement def <'STG-12'> OutputPower {
            doc /*
             * The stage gives at least 100 W of mechanical output power:
             * driving force times speed.
             */
            subject stage : CompactStage;
            require constraint { stage.maxOutputPower >= 100 [W] }
        }

        // --- Load and interfaces ----------------------------------------------

        requirement def <'STG-13'> LateralLoad {
            doc /*
             * The carriage carries a sideways load of at least 500 N at the
             * centre of the carriage, in either direction across the motion.
             */
            subject stage : CompactStage;
            require constraint { stage.lateralLoadCapacity >= 500 [N] }
        }

        requirement def <'STG-14'> InterfaceGrid {
            doc /*
             * The screw holes at each mechanical interface fit a grid of
             * 20 mm, 40 mm or 80 mm. The hole pitch is a whole multiple of
             * 20 mm, so the stage mounts on the same grid as other parts.
             */
            subject stage : CompactStage;
            require constraint {
                stage.interfaceHolePitch == 20 [mm]
                or stage.interfaceHolePitch == 40 [mm]
                or stage.interfaceHolePitch == 80 [mm]
            }
        }
    }

    // ---------------------------------------------------------------------
    // The full set, for one stage
    // ---------------------------------------------------------------------

    requirement def CompactStageSpecification {
        doc /*
         * All requirements for one compact stage. A design passes
         * when it meets every mandatory requirement.
         */
        subject stage : CompactStage;

        requirement width : Mandatory::Width;
        requirement height : Mandatory::Height;
        requirement length : Mandatory::Length;
        requirement positioningError : Mandatory::PositioningError;
        requirement linearErrorMotion : Mandatory::LinearErrorMotion;
        requirement rotationalErrorMotion : Mandatory::RotationalErrorMotion;
        requirement unidirectionalRepeatability : Mandatory::UnidirectionalRepeatability;
        requirement bidirectionalRepeatability : Mandatory::BidirectionalRepeatability;
        requirement maxSpeed : Mandatory::MaxSpeed;
        requirement continuousForce : Mandatory::ContinuousForce;
        requirement peakForce : Mandatory::PeakForce;
        requirement outputPower : Mandatory::OutputPower;
        requirement lateralLoad : Mandatory::LateralLoad;
        requirement interfaceGrid : Mandatory::InterfaceGrid;
    }
}
