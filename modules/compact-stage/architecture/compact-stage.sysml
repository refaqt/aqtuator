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
// rails are in this file, with their interface to the base. Not modelled
// yet: the guide blocks, the motor (magnet track and coil), the encoder, the
// rollers and the screws. When they enter this file, they bring their own
// interfaces: for example block to carriage-bottom, magnet track to base,
// coil to carriage-bottom, and roller to sealing strip.
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
         */
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
         * The reference rail (y = 169 mm) lies against two tabs, one near
         * each end. The tabs set its position and its direction.
         *
         * The second rail (y = 41 mm) lies against one tab, near one end.
         * The tab sets its position at that end only. To set its
         * direction, put the carriage on both rails and move it from end
         * to end while you tighten the screws of the second rail, one after
         * the other. HIWIN calls this "alignment on the reference rail".
         *
         * The y positions are rail centres, measured from the long side of
         * the base. The first hole is 40 mm from the end of the base.
         */
        attribute holePitch : LengthValue = 60 [mm];
        attribute firstHoleOffset : LengthValue = 40 [mm];
        attribute holesPerRail : Natural = 7;
        attribute screwLength : LengthValue = 16 [mm];   // M4 x 16
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
    }

    part def GuideRail {
        doc /*
         * A bought profile rail: HIWIN HGR15R, 418 mm long. It comes from
         * the parts library in modules/stoq/. The stage has two.
         */
        port baseMount : ~RailMountInterface_v1;
    }

    part def CarriageBottom {
        doc /* The moving part inside the base. CAD: cad/parts/carriage-bottom/. */
        port carriageJoint : CarriageJointInterface_v1;
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
