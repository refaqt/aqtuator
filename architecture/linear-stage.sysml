// Requirements for the linear motor stage.
//
// These requirements hold for the whole stage: its size, its accuracy, its
// speed, its force and its load. Each requirement has a short name, for
// example STG-05, that a design review or a measurement campaign can cite.
//
// The servo drive has its own requirements in motor-drive.sysml.
//
// Rule for a pass or a fail: a bought part (a guide, a motor, an encoder)
// passes only on the deciding number in the maker's own data sheet or
// manual. A trade article, a shop page or a search result is not enough.
// See docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md.
//
// Every error value below is a half band: "5 µm" means "within +/- 5 µm".
package LinearStageRequirements {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;

    // ---------------------------------------------------------------------
    // What we know about one stage design
    // ---------------------------------------------------------------------

    part def LinearStage {
        doc /*
         * One stage design, or one built stage. Fill in one of these per
         * design, from the CAD model, the data sheets and the measurements.
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
    }

    // ---------------------------------------------------------------------
    // Hard requirements. A design that fails one of these is rejected.
    // ---------------------------------------------------------------------

    package Mandatory {

        // --- Size ------------------------------------------------------------

        requirement def <'STG-01'> Width {
            doc /* The stage is at most 210 mm wide. */
            subject stage : LinearStage;
            require constraint { stage.width <= 210 [mm] }
        }

        requirement def <'STG-02'> Height {
            doc /* The stage is at most 60 mm high. */
            subject stage : LinearStage;
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
            subject stage : LinearStage;
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
            subject stage : LinearStage;
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
            subject stage : LinearStage;
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
            subject stage : LinearStage;
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
            subject stage : LinearStage;
            require constraint { stage.unidirectionalRepeatability <= 0.1 [µm] }
        }

        requirement def <'STG-08'> BidirectionalRepeatability {
            doc /*
             * The carriage returns to the same position within +/- 0.3 µm
             * when it comes from either direction. This includes the
             * backlash and the hysteresis of the stage.
             */
            subject stage : LinearStage;
            require constraint { stage.bidirectionalRepeatability <= 0.3 [µm] }
        }

        // --- Motion and drive -------------------------------------------------

        requirement def <'STG-09'> MaxSpeed {
            doc /*
             * The carriage reaches at least 3 m/s.
             *
             * Note: the drive requirements in motor-drive.sysml use a top
             * speed of 10 000 mm/min (0.17 m/s). The encoder frequency
             * (DRV-08) and the bus voltage (DRV-04) follow from that speed.
             * They must be checked again for 3 m/s.
             */
            subject stage : LinearStage;
            require constraint { stage.maxSpeed >= 3 [m/s] }
        }

        requirement def <'STG-10'> ContinuousForce {
            doc /*
             * The stage pushes the carriage with at least 200 N without a
             * time limit.
             */
            subject stage : LinearStage;
            require constraint { stage.continuousForce >= 200 [N] }
        }

        requirement def <'STG-11'> PeakForce {
            doc /* The stage pushes the carriage with at least 550 N at its peak. */
            subject stage : LinearStage;
            require constraint { stage.peakForce >= 550 [N] }
        }

        requirement def <'STG-12'> OutputPower {
            doc /*
             * The stage gives at least 100 W of mechanical output power:
             * driving force times speed.
             */
            subject stage : LinearStage;
            require constraint { stage.maxOutputPower >= 100 [W] }
        }

        // --- Load and interfaces ----------------------------------------------

        requirement def <'STG-13'> LateralLoad {
            doc /*
             * The carriage carries a sideways load of at least 500 N at the
             * centre of the carriage, in either direction across the motion.
             */
            subject stage : LinearStage;
            require constraint { stage.lateralLoadCapacity >= 500 [N] }
        }

        requirement def <'STG-14'> InterfaceGrid {
            doc /*
             * The screw holes at each mechanical interface fit a grid of
             * 20 mm, 40 mm or 80 mm. The hole pitch is a whole multiple of
             * 20 mm, so the stage mounts on the same grid as other parts.
             */
            subject stage : LinearStage;
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

    requirement def LinearStageSpecification {
        doc /*
         * All requirements for one linear motor stage. A design passes
         * when it meets every mandatory requirement.
         */
        subject stage : LinearStage;

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
