// Requirements for the servo drive of the linear motor stages.
//
// The drive is a job, not a brand. These requirements hold for any drive we
// buy for this job. A drive search checks each candidate against them and
// cites each requirement by its short name, for example DRV-03.
//
// Rule for a pass or a fail: read the deciding number in the maker's own
// data sheet or manual. A trade article, a shop page or a search result is
// not enough. If the manual cannot be opened, the drive is "not confirmed".
// See docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md.
//
// The research behind these requirements is in docs/log/, in the drive
// entries from 2026-09-25 and 2026-09-29.
package MotorDriveRequirements {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;

    // ---------------------------------------------------------------------
    // The motor the drive must run
    // ---------------------------------------------------------------------

    part def MaxwellMK21 {
        doc /*
         * MAXWELL MK21 iron core linear motor, bought through Saho
         * (Dongguan Shihai Automation). Three phase, permanent magnet,
         * synchronous. Every value below is from the MAXWELL MK2 data sheet:
         * modules/stoq/modules/maxwell/docs/datasheets/maxwell-mk2-iron-core-linear-motor.pdf
         * Currents are rms values. Electrical values are line to line.
         */
        attribute continuousForce : ForceValue = 181 [N];
        attribute continuousCurrent : ElectricCurrentValue = 2.0 [A];
        attribute peakForce : ForceValue = 512 [N];              // for 1 s
        attribute peakCurrent : ElectricCurrentValue = 5.9 [A];  // for 1 s
        attribute limitingForce : ForceValue = 670 [N];          // for 0.5 s
        attribute limitingCurrent : ElectricCurrentValue = 9.8 [A];  // for 0.5 s
        attribute forceConstant : Real = 92.5;             // N per A rms
        attribute backEmfConstant : Real = 53.4;           // V rms per m/s
        attribute resistanceAt25C : Real = 13.8;           // ohm
        attribute resistanceAt120C : Real = 19.0;          // ohm
        attribute inductance : Real = 64.0E-3;             // henry
        attribute electricalTimeConstant : Real = 4.6E-3;  // second
        attribute polePitch : LengthValue = 30 [mm];       // one full electrical period
        attribute maxCoilTemperature : Real = 120;         // degree Celsius
        attribute maxBusVoltage : Real = 600;              // V DC
        attribute moverMass : MassValue = 1.1 [kg];
        attribute thermalSensor : String = "3 PNC SNM120 in series";
    }

    // ---------------------------------------------------------------------
    // What we know about a candidate drive
    // ---------------------------------------------------------------------

    part def MotorDrive {
        doc /*
         * One candidate drive, as its maker's data sheet and manual describe
         * it. Fill in one of these per drive in a search.
         */
        attribute continuousCurrent : ElectricCurrentValue;  // rms
        attribute peakCurrent : ElectricCurrentValue;        // rms, for at least 1 s
        attribute busVoltage : Real;                         // V DC, at the supply we use
        attribute canLimitPeakCurrent : Boolean;
        attribute hasMotorThermalModel : Boolean;            // an i2t or similar current limit
        attribute supportsLinearSynchronousMotor : Boolean;
        attribute supportsElectricalPeriod30mm : Boolean;
        attribute findsCommutationAngle : Boolean;
        attribute readsMotorThermalSensor : Boolean;        // directly, or on an input that stops the drive
        attribute hasEtherCAT : Boolean;
        attribute hasCiA402Profile : Boolean;
        attribute readsSinCos1Vpp : Boolean;
        attribute readsBissC : Boolean;
        attribute positionLoopRate : FrequencyValue;
        attribute freeBiquadFilterCount : Natural;
        attribute publishesLoopDiagram : Boolean;
    }

    // ---------------------------------------------------------------------
    // Hard requirements. A drive that fails one of these is rejected.
    // ---------------------------------------------------------------------

    package Mandatory {

        // --- The drive runs the MAXWELL MK21 --------------------------------

        requirement def <'DRV-01'> ContinuousCurrent {
            doc /*
             * The drive gives at least 2.0 A rms without a time limit. This is
             * the continuous current of the MK21, which gives 181 N.
             */
            subject drive : MotorDrive;
            require constraint { drive.continuousCurrent >= 2.0 [A] }
        }

        requirement def <'DRV-02'> PeakCurrent {
            doc /*
             * The drive gives at least 5.9 A rms for at least 1 s. This is the
             * peak current of the MK21, which gives 512 N.
             *
             * Many makers give current as a peak value, not an rms value.
             * 2.0 A rms is 2.8 A peak. 5.9 A rms is 8.3 A peak. Convert
             * before you compare.
             */
            subject drive : MotorDrive;
            require constraint { drive.peakCurrent >= 5.9 [A] }
        }

        requirement def <'DRV-03'> MotorCurrentProtection {
            doc /*
             * The drive can be set so that it never harms the motor. It lets
             * us set the peak current limit, and it has a thermal model of
             * the motor (an i2t limit or similar) set from the continuous
             * current.
             *
             * This matters because a strong drive can give far more current
             * than the MK21 takes. The MK21 takes at most 9.8 A rms, and only
             * for 0.5 s.
             */
            subject drive : MotorDrive;
            require constraint { drive.canLimitPeakCurrent and drive.hasMotorThermalModel }
        }

        requirement def <'DRV-04'> BusVoltage {
            doc /*
             * The DC bus of the drive (the internal supply voltage) is at
             * least 160 V and at most 600 V.
             *
             * The lower limit comes from a hand calculation in the drive
             * survey of 2026-09-25. The MK21 needs about 158 V to give
             * 512 N at 10 000 mm/min with a hot coil (120 °C). It assumes
             * sine commutation and 90 % use of the bus voltage. The upper
             * limit is the highest voltage the MK21 allows.
             *
             * A drive fed from 230 VAC single phase has about 325 V, so it
             * meets this. A drive of 48 V or 80 V does not.
             */
            subject drive : MotorDrive;
            require constraint { drive.busVoltage >= 160 and drive.busVoltage <= 600 }
        }

        requirement def <'DRV-05'> LinearMotorCommutation {
            doc /*
             * The drive runs a three phase permanent magnet linear motor
             * (a linear synchronous motor) with an electrical period of
             * 30 mm, which is the pole pitch of the MK21.
             *
             * It finds the commutation angle (the position of the coil
             * against the magnets) at start-up from the encoder, without
             * Hall sensors. Check with MAXWELL whether the MK21 we buy has
             * Hall sensors. If it has, a drive that reads them also passes.
             */
            subject drive : MotorDrive;
            require constraint {
                drive.supportsLinearSynchronousMotor
                and drive.supportsElectricalPeriod30mm
                and drive.findsCommutationAngle
            }
        }

        requirement def <'DRV-06'> MotorThermalSensor {
            doc /*
             * The drive reads the thermal sensor in the MK21 coil and stops
             * the motor when the sensor trips. The data sheet names the
             * sensor "3 PNC SNM120 in series". Confirm the sensor type with
             * MAXWELL before you check a drive against it.
             *
             * A drive without such an input still passes if the sensor can
             * be wired to a digital input that stops the drive.
             */
            subject drive : MotorDrive;
            require constraint { drive.readsMotorThermalSensor }
        }

        // --- Fieldbus ----------------------------------------------------------

        requirement def <'DRV-07'> EtherCAT {
            doc /*
             * The drive connects to the motion controller over EtherCAT, as
             * an EtherCAT slave. It follows the CiA 402 drive profile (the
             * standard set of commands and states for a servo drive over
             * CANopen and EtherCAT). The motion controller is a PC with
             * LinuxCNC as the EtherCAT master.
             */
            subject drive : MotorDrive;
            require constraint { drive.hasEtherCAT and drive.hasCiA402Profile }
        }

        // --- Position feedback -------------------------------------------------

        requirement def <'DRV-08'> EncoderInput {
            doc /*
             * The drive reads the linear encoder directly, with no converter
             * box in between. It reads at least one of these two signals:
             *
             * - 1 Vpp sine and cosine, incremental (analog signals of 1 V
             *   peak to peak), or
             * - BiSS-C, absolute (a digital serial encoder signal).
             *
             * The drive must accept the highest signal frequency the stage
             * makes: the top speed divided by the signal period of the
             * encoder we choose. For BiSS-C, it must read the full data frame
             * of that encoder.
             */
            subject drive : MotorDrive;
            require constraint { drive.readsSinCos1Vpp or drive.readsBissC }
        }

        // --- Control loop ------------------------------------------------------

        requirement def <'DRV-09'> PositionLoopRate {
            doc /*
             * The position loop inside the drive runs at 8 kHz or faster.
             * This means an update period of 125 µs or shorter.
             *
             * Read this number in the maker's own manual. Do not use the
             * current loop rate, the velocity loop rate or the shortest
             * EtherCAT cycle instead. They are different numbers, and they
             * are often faster. For example, a position loop of 128 µs
             * (7.8 kHz) fails.
             */
            subject drive : MotorDrive;
            require constraint { drive.positionLoopRate >= 8000 [Hz] }
        }
    }

    // ---------------------------------------------------------------------
    // Preferences. A drive that meets these is better, but a drive that
    // does not is not rejected.
    // ---------------------------------------------------------------------

    package Preferred {

        requirement def <'DRV-P1'> CustomLoopFilters {
            doc /*
             * We can put our own filters in the control loop of the drive.
             * The best case is a general second order filter (a biquad):
             * we set the numerator and the denominator freely, for example
             * as a frequency and a damping ratio for each. More than one such
             * filter active at the same time is better than one.
             *
             * Fixed filter types (a low-pass or a notch with only a frequency
             * to set) count less. They do not meet this preference on their
             * own.
             */
            subject drive : MotorDrive;
            require constraint { drive.freeBiquadFilterCount >= 1 }
        }

        requirement def <'DRV-P2'> PublishedLoopStructure {
            doc /*
             * The maker publishes a block diagram of the control loop, and
             * says what each gain and each filter does in it. Without this,
             * we cannot model the drive or tune it on purpose.
             */
            subject drive : MotorDrive;
            require constraint { drive.publishesLoopDiagram }
        }
    }

    // ---------------------------------------------------------------------
    // The full set, for one drive
    // ---------------------------------------------------------------------

    requirement def MotorDriveSpecification {
        doc /*
         * All requirements for the servo drive of one linear motor stage.
         * A candidate passes when it meets every mandatory requirement.
         * The preferred requirements rank the candidates that pass.
         */
        subject drive : MotorDrive;

        requirement continuousCurrent : Mandatory::ContinuousCurrent;
        requirement peakCurrent : Mandatory::PeakCurrent;
        requirement motorCurrentProtection : Mandatory::MotorCurrentProtection;
        requirement busVoltage : Mandatory::BusVoltage;
        requirement linearMotorCommutation : Mandatory::LinearMotorCommutation;
        requirement motorThermalSensor : Mandatory::MotorThermalSensor;
        requirement etherCAT : Mandatory::EtherCAT;
        requirement encoderInput : Mandatory::EncoderInput;
        requirement positionLoopRate : Mandatory::PositionLoopRate;
    }
}
