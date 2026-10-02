// Requirements for the linear encoder of the compact stage.
//
// The encoder is a job, not a brand. These requirements hold for any
// encoder we buy for this job. A search checks each candidate against them
// and cites each requirement by its short name, for example ENC-03.
//
// An encoder has two parts: a scale (a strip fixed to the base) and a
// reading head (fixed to the carriage). The size limits apply to each.
//
// Rule for a pass or a fail: read the deciding number in the maker's own
// data sheet or manual. A trade article, a shop page or a search result is
// not enough. If the data sheet cannot be opened, the encoder is "not
// confirmed". See docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md.
//
// Every error value is a half band: "5 µm" means "within +/- 5 µm".
//
// Links to the rest of the stage:
//
// - ENC-03 uses the top speed of the stage (STG-09). Both say 3 m/s.
// - ENC-04 matches the signal that the servo drive reads (DRV-08,
//   EncoderSignal::bissC in motor-drive.sysml).
// - ENC-02 is the same size as the positioning error of the stage (STG-04).
//   The encoder alone uses the whole budget. See the log entry of
//   2026-10-02.
package LinearEncoderRequirements {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;

    // ---------------------------------------------------------------------
    // What we know about a candidate encoder
    // ---------------------------------------------------------------------

    enum def EncoderOutput {
        doc /* The kinds of output signal an encoder may have. */
        enum sinCos1Vpp;   // 1 Vpp sine and cosine, incremental (analog)
        enum bissC;        // BiSS-C, absolute (digital, serial)
        enum other;
    }

    part def EncoderCandidate {
        doc /*
         * One candidate encoder, as its maker's data sheet describes it.
         * Fill in one of these per encoder in a search.
         */

        // Measuring performance
        attribute resolution : LengthValue;            // smallest step it reports
        attribute accuracy : LengthValue;              // half band, over accuracyLength
        attribute accuracyLength : LengthValue;        // the length that the accuracy holds for
        attribute periodicError : LengthValue;         // half band, within one signal period
        attribute maxSpeed : SpeedValue;               // highest speed at which it still reports
        attribute output : EncoderOutput;
        attribute isAbsolute : Boolean;

        // Reading head size
        attribute headWidth : LengthValue;             // across the direction of motion
        attribute headHeight : LengthValue;            // from the scale to the top of the head
        attribute headLength : LengthValue;            // in the direction of motion

        // Scale size
        attribute scaleHeight : LengthValue;           // thickness, with any carrier or tape
        attribute scaleWidth : LengthValue;            // across the direction of motion

        // Allowed angle of the reading head against the scale (half bands, rad)
        attribute allowedRoll : Real;                  // about the direction of motion
        attribute allowedPitch : Real;                 // about the axis across the motion, in the plane of the scale
        attribute allowedYaw : Real;                   // about the axis normal to the scale
    }

    part def HeadMounting {
        doc /*
         * How far the reading head can sit out of line with the scale in our
         * stage. It is the sum of the mounting error and the rotational
         * error motion of the carriage (STG-06). The three values have no
         * number yet. Fill them in from the CAD tolerances, or from a
         * measurement. Half bands, in radians.
         */
        attribute rollDeviation : Real;
        attribute pitchDeviation : Real;
        attribute yawDeviation : Real;
    }

    // ---------------------------------------------------------------------
    // Hard requirements. An encoder that fails one of these is rejected.
    // ---------------------------------------------------------------------
    package Mandatory {

        // --- Measuring performance --------------------------------------------

        requirement def <'ENC-01'> Resolution {
            doc /*
             * The encoder reports steps smaller than 0.2 µm.
             *
             * Resolution is the step size of the output. It is not the
             * accuracy. Use the resolution at the output we use (the
             * BiSS-C frame), not the resolution of an interpolation box.
             */
            subject encoder : EncoderCandidate;
            require constraint { encoder.resolution < 0.2 [µm] }
        }

        requirement def <'ENC-02'> Accuracy {
            doc /*
             * The position error of the encoder is within +/- 5 µm over a
             * length of 200 mm, without any error table in the controller.
             * The data sheet must state the accuracy for 200 mm, or for a
             * longer scale that includes it.
             */
            subject encoder : EncoderCandidate;
            require constraint {
                encoder.accuracy <= 5 [µm] and encoder.accuracyLength >= 200 [mm]
            }
        }

        requirement def <'ENC-03'> MaxSpeed {
            doc /*
             * The encoder keeps reporting the position at speeds above
             * 3 m/s. Read the speed that holds at the resolution of ENC-01.
             * A data sheet often gives a lower speed at a finer resolution.
             */
            subject encoder : EncoderCandidate;
            require constraint { encoder.maxSpeed > 3 [m/s] }
        }

        requirement def <'ENC-04'> AbsoluteBissC {
            doc /*
             * The encoder gives the absolute position over BiSS-C. It needs
             * no reference run after power on. The servo drive must read the
             * full data frame (DRV-08). Check this by hand against both data
             * sheets.
             */
            subject encoder : EncoderCandidate;
            require constraint {
                encoder.isAbsolute and encoder.output == EncoderOutput::bissC
            }
        }

        requirement def <'ENC-05'> PeriodicError {
            doc /*
             * The error that repeats with every signal period is within
             * +/- 0.3 µm. Some makers call it subdivisional error (SDE) or
             * interpolation error. It limits the smoothness of the speed
             * and the stiffness of the position loop.
             */
            subject encoder : EncoderCandidate;
            require constraint { encoder.periodicError <= 0.3 [µm] }
        }

        // --- Reading head size ------------------------------------------------

        requirement def <'ENC-06'> HeadWidth {
            doc /* The reading head is less than 15 mm wide. */
            subject encoder : EncoderCandidate;
            require constraint { encoder.headWidth < 15 [mm] }
        }

        requirement def <'ENC-07'> HeadHeight {
            doc /* The reading head is less than 18 mm high. */
            subject encoder : EncoderCandidate;
            require constraint { encoder.headHeight < 18 [mm] }
        }

        requirement def <'ENC-08'> HeadLength {
            doc /* The reading head is less than 40 mm long. */
            subject encoder : EncoderCandidate;
            require constraint { encoder.headLength < 40 [mm] }
        }

        // --- Scale size -------------------------------------------------------

        requirement def <'ENC-09'> ScaleHeight {
            doc /*
             * The scale is less than 1 mm high, including any carrier or
             * adhesive tape that comes with it.
             */
            subject encoder : EncoderCandidate;
            require constraint { encoder.scaleHeight < 1 [mm] }
        }

        requirement def <'ENC-10'> ScaleWidth {
            doc /* The scale is less than 12 mm wide. */
            subject encoder : EncoderCandidate;
            require constraint { encoder.scaleWidth < 12 [mm] }
        }

        // --- Angle of the reading head against the scale ------------------------

        requirement def <'ENC-11'> AngularTolerance {
            doc /*
             * The reading head may sit out of line with the scale by the
             * angle that our stage gives, in all three directions. The
             * encoder data sheet gives the allowed angle for each:
             *
             * - roll: rotation about the direction of motion
             * - pitch: rotation about the axis across the motion, in the
             *   plane of the scale
             * - yaw: rotation about the axis normal to the scale
             *
             * Makers use other names for the same angles. Map them by the
             * axis, not by the name. Each allowed angle must be at least
             * the angle that the stage gives (HeadMounting).
             *
             * No number is set yet. The stage values in HeadMounting are
             * open. Until they are filled in, this requirement cannot
             * pass or fail: write "not confirmed" and keep the data sheet
             * values for later.
             */
            subject encoder : EncoderCandidate;
            in part mounting : HeadMounting;
            require constraint {
                encoder.allowedRoll >= mounting.rollDeviation
                and encoder.allowedPitch >= mounting.pitchDeviation
                and encoder.allowedYaw >= mounting.yawDeviation
            }
        }
    }

    // ---------------------------------------------------------------------
    // The full set, for one encoder
    // ---------------------------------------------------------------------

    requirement def LinearEncoderSpecification {
        doc /*
         * All requirements for the linear encoder of one compact stage. A
         * candidate passes when it meets every mandatory requirement.
         */
        subject encoder : EncoderCandidate;

        requirement resolution : Mandatory::Resolution;
        requirement accuracy : Mandatory::Accuracy;
        requirement maxSpeed : Mandatory::MaxSpeed;
        requirement absoluteBissC : Mandatory::AbsoluteBissC;
        requirement periodicError : Mandatory::PeriodicError;
        requirement headWidth : Mandatory::HeadWidth;
        requirement headHeight : Mandatory::HeadHeight;
        requirement headLength : Mandatory::HeadLength;
        requirement scaleHeight : Mandatory::ScaleHeight;
        requirement scaleWidth : Mandatory::ScaleWidth;
        requirement angularTolerance : Mandatory::AngularTolerance;
    }
}
