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
        // Thermal sensor: three PTC thermistors in series, two wires. The
        // data sheet prints "3 PNC SNM120 in series"; PNC is a misprint.
        // Resistance values are from the MAXWELL PTC table, column "three
        // PTC in series", measured at 2.5 V or less. They are stated against
        // the rated response temperature Tk, so they hold for any Tk. See
        // modules/stoq/modules/maxwell/modules/mk2-mover/docs/mk21-thermal-sensor.md
        attribute thermalSensor : String = "3 PTC SNM120 in series";
        attribute thermalSensorResponseTemperature : Real = 120;  // degree Celsius, Tk. From the name SNM120, not confirmed by MAXWELL
        attribute thermalSensorResistanceAt25C : Real = 300;      // ohm, at most
        attribute thermalSensorResistanceCold : Real = 750;       // ohm, at most, from -20 degree Celsius to Tk - 20 K
        attribute thermalSensorResistanceBelowTk : Real = 1650;   // ohm, at most, at Tk - 5 K
        attribute thermalSensorResistanceAboveTk : Real = 3990;   // ohm, at least, at Tk + 5 K
        attribute thermalSensorResistanceHot : Real = 12000;      // ohm, at least, at Tk + 15 K
        attribute thermalSensorMaxVoltage : Real = 30;            // V, highest voltage without damage
        attribute thermalSensorResponseTime : Real = 5;           // second, at most
    }

    // ---------------------------------------------------------------------
    // The encoder and the stage the drive must work with
    // ---------------------------------------------------------------------

    enum def EncoderSignal {
        doc /* The kinds of encoder signal a drive may have to read. */
        enum sinCos1Vpp;   // 1 Vpp sine and cosine, incremental (analog)
        enum bissC;        // BiSS-C, absolute (digital, serial)
        enum endat22;      // EnDat 2.2, absolute (digital, serial)
        enum otherSerial;  // another serial protocol (digital), named in protocol
    }

    part def LinearEncoder {
        doc /*
         * The linear encoder of the stage. The encoder requirement (DRV-08)
         * reads its values from here. If we change the encoder, we change
         * this part, and the requirement follows.
         */
        attribute signal : EncoderSignal;
        attribute signalPeriod : LengthValue;  // for sine and cosine: one signal period
        attribute protocol : String;           // for otherSerial: the name of the protocol
    }

    part def LinearMotorStage {
        doc /* One linear motor stage: its encoder and its top speed. */
        part encoder : LinearEncoder;
        attribute maxSpeed : SpeedValue;
    }

    part currentStage : LinearMotorStage {
        doc /*
         * The stage as it is today. Change the values here when the encoder
         * or the top speed changes. Every requirement that depends on them
         * then changes with them.
         *
         * Today (since 2026-10-27): the RSF AK MC 15 B read head on an
         * MC 15 MK steel tape. It is an absolute encoder with a BiSS C
         * unidirectional output (RSF order code BiSS/Cu) and a 0.1 µm
         * measuring step. It is the ReadHead in compact-stage.sysml. The
         * top speed is 3 m/s (STG-09 in compact-stage.sysml).
         *
         * Until 2026-11-04 this part still described an older 1 Vpp
         * encoder with a 20 µm grating pitch (150 kHz at 3 m/s). Drive
         * checks before that date used the old encoder.
         */
        part :>> encoder {
            attribute :>> signal = EncoderSignal::bissC;
        }
        attribute :>> maxSpeed = 3 [m/s];
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
        attribute maxSinCosFrequency : FrequencyValue;       // highest 1 Vpp input frequency
        attribute readsBissC : Boolean;
        attribute readsEnDat22 : Boolean;
        attribute readsOtherSerialProtocol : Boolean;        // reads the protocol named in the stage encoder
        attribute positionLoopRate : FrequencyValue;
        attribute freeBiquadFilterCount : Natural;
        attribute publishesLoopDiagram : Boolean;
        attribute tuningToolShowsBodePlot : Boolean;         // in the maker's own setup software
        // Safety and CE (DRV-11 to DRV-13, DRV-P4, DRV-P5). Read each value
        // in the maker's Declaration of Conformity, safety certificate or
        // manual. See docs/compact-stage-ce-assessment.md.
        attribute declaresLowVoltageDirective : Boolean;     // 2014/35/EU, with EN 61800-5-1
        attribute declaresEmcDirective : Boolean;            // 2014/30/EU, with EN 61800-3
        attribute declaresRohsDirective : Boolean;           // 2011/65/EU
        attribute stoSafetyIntegrityLevel : Natural;         // SIL of Safe Torque Off (IEC 61800-5-2, IEC 61508); 0 when there is no certified STO
        attribute stoPerformanceLevel : Natural;             // PL of Safe Torque Off (EN ISO 13849-1): 1 = PL a ... 4 = PL d, 5 = PL e; 0 when none
        attribute stoCertifiedByTestingBody : Boolean;       // a certificate from a testing body such as TUV
        attribute stopsOnFollowingError : Boolean;           // position error too large: the drive disables the motor
        attribute stopsOnEncoderFault : Boolean;             // lost or wrong encoder data: the drive disables the motor
        attribute hasSoftwarePositionLimits : Boolean;       // the drive stops at a set position, without a switch
        attribute hasSafeStop1 : Boolean;                    // SS1: braked stop, then STO; built in or with the maker's safety relay
        attribute hasBrakeOutput : Boolean;                  // controls a holding brake that the customer adds
        attribute hasDynamicBraking : Boolean;               // shorts the motor phases to brake on a fault
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
             * least 320 V and at most 600 V.
             *
             * The lower limit comes from a hand calculation, done in the
             * same way as in the drive survey of 2026-09-25. The MK21 needs
             * about 320 V to give 180 N (STG-10) at 3 m/s (STG-09) with a
             * hot coil (120 °C). It assumes sine commutation and 90 % use of
             * the bus voltage. The full peak force of 500 N (STG-11) is only
             * needed at lower speed, while the stage speeds up. 500 N at
             * 3 m/s would need about 490 V. The upper limit is the highest
             * voltage the MK21 allows.
             *
             * A drive fed from 230 VAC single phase has about 325 V, so it
             * just meets this, with no margin when the mains voltage is low.
             * It then gives 500 N up to about 1.7 m/s. A drive of 48 V or
             * 80 V does not meet this.
             */
            subject drive : MotorDrive;
            require constraint { drive.busVoltage >= 320 and drive.busVoltage <= 600 }
        }

        requirement def <'DRV-05'> LinearMotorCommutation {
            doc /*
             * The drive runs a three phase permanent magnet linear motor
             * (a linear synchronous motor) with an electrical period of
             * 30 mm, which is the pole pitch of the MK21.
             *
             * It finds the commutation angle (the position of the coil
             * against the magnets) at start-up from the encoder, without
             * Hall sensors.
             *
             * Not known yet: whether the MK21 has Hall sensors. Until we
             * know, a drive must work without them. If MAXWELL confirms
             * Hall sensors, a drive that reads them also passes.
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
             * the motor when the sensor trips.
             *
             * Known: the sensor is three PTC thermistors in series (a
             * switching sensor, not a measuring one like a KTY or PT1000).
             * It reads 1650 ohm or less at Tk - 5 K and 3990 ohm or more at
             * Tk + 5 K. A PTC input passes when its trip resistance can be
             * set, or is fixed, between these two values. The input must
             * never put more than 30 V on the sensor. All values are in
             * MaxwellMK21 above. Tk is probably 120 degree Celsius; MAXWELL
             * has not confirmed it yet.
             *
             * A KTY, PT100 or PT1000 input alone does not pass. It expects
             * a sensor whose resistance rises in a straight line.
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
             * The drive reads the encoder of the stage directly, with no
             * converter box in between. The requirement depends on the
             * encoder, so it takes the stage as an input:
             *
             * - For a 1 Vpp sine and cosine encoder, the drive reads 1 Vpp,
             *   and it accepts the highest signal frequency: the top speed
             *   divided by the signal period.
             * - For a serial encoder (BiSS-C, EnDat 2.2 or another
             *   protocol), the drive reads that protocol. It must also read
             *   the full data frame of that encoder. Check this by hand
             *   against the encoder data sheet.
             *
             * The encoder protocol is not fixed to BiSS-C. Any protocol
             * that the chosen drive reads is allowed (ENC-04).
             *
             * When the encoder changes, change currentStage, not this text.
             */
            subject drive : MotorDrive;
            in part stage : LinearMotorStage;
            require constraint {
                (stage.encoder.signal == EncoderSignal::sinCos1Vpp implies
                    (drive.readsSinCos1Vpp and
                     drive.maxSinCosFrequency >= stage.maxSpeed / stage.encoder.signalPeriod))
                and
                (stage.encoder.signal == EncoderSignal::bissC implies drive.readsBissC)
                and
                (stage.encoder.signal == EncoderSignal::endat22 implies drive.readsEnDat22)
                and
                (stage.encoder.signal == EncoderSignal::otherSerial implies drive.readsOtherSerialProtocol)
            }
        }

        // --- Control loop ------------------------------------------------------

        requirement def <'DRV-09'> PositionLoopRate {
            doc /*
             * The position loop inside the drive runs at 4 kHz or faster.
             * This means an update period of 250 µs or shorter. A drive
             * below 4 kHz fails. Above 4 kHz, faster is better: see DRV-P3.
             *
             * Read this number in the maker's own manual. Do not use the
             * current loop rate, the velocity loop rate or the shortest
             * EtherCAT cycle instead. They are different numbers, and they
             * are often faster.
             */
            subject drive : MotorDrive;
            require constraint { drive.positionLoopRate >= 4000 [Hz] }
        }

        // --- Tuning --------------------------------------------------------------

        requirement def <'DRV-10'> BodePlotTuning {
            doc /*
             * The maker's own setup software for the drive has a tuning
             * function that shows Bode plots of the transfer function: the
             * gain and the phase against the frequency.
             *
             * The software measures the frequency response on the real
             * machine. The drive excites the axis itself, for example with
             * a sine sweep or with noise. The software then shows at least
             * one loop as a Bode plot: the plant (the mechanics seen from the
             * current loop), the open loop or the closed loop.
             *
             * A frequency response that the software only uses inside an
             * automatic tuning step, and never shows, does not pass. A plain
             * oscilloscope view of the signals over time does not pass.
             *
             * Read this in the maker's own manual for the software or the
             * drive.
             */
            subject drive : MotorDrive;
            require constraint { drive.tuningToolShowsBodePlot }
        }

        // --- Safety and CE marking ---------------------------------------------

        requirement def <'DRV-11'> CeMarking {
            doc /*
             * The drive carries the CE mark (the EU product safety mark),
             * and the maker gives an EU Declaration of Conformity. It
             * declares the Low Voltage Directive 2014/35/EU (with
             * EN 61800-5-1), the EMC Directive 2014/30/EU (with EN 61800-3)
             * and the RoHS Directive 2011/65/EU.
             *
             * Note the EMC category in the declaration (C2 or C3) and
             * whether it needs an extra mains filter. A drive of category
             * C3 alone is not meant for a public low-voltage network, such
             * as many labs and offices.
             *
             * The stage is partly completed machinery. The customer builds
             * it into a machine and makes the final CE assessment. The
             * drive must therefore bring its own CE marking.
             */
            subject drive : MotorDrive;
            require constraint {
                drive.declaresLowVoltageDirective
                and drive.declaresEmcDirective
                and drive.declaresRohsDirective
            }
        }

        requirement def <'DRV-12'> SafeTorqueOff {
            doc /*
             * The drive has Safe Torque Off (STO): a certified input that
             * cuts the motor force, so the motor cannot push. It meets at
             * least SIL 2 (IEC 61800-5-2) and PL d (EN ISO 13849-1), and a
             * testing body certifies it.
             *
             * Why: the motor pushes up to 670 N and the carriage moves at up
             * to 3 m/s. A hand at the end of the travel can be crushed. The
             * customer stops the machine through STO, from an emergency stop
             * or a door switch. The first estimate of the required level is
             * PL d, and PL e when people often work near the moving carriage.
             * See docs/compact-stage-ce-assessment.md.
             *
             * A linear motor has no brake and holds nothing without power.
             * STO alone lets the carriage coast. This is acceptable only for
             * a horizontal stage.
             */
            subject drive : MotorDrive;
            require constraint {
                drive.stoSafetyIntegrityLevel >= 2
                and drive.stoPerformanceLevel >= 4
                and drive.stoCertifiedByTestingBody
            }
        }

        requirement def <'DRV-13'> FaultStops {
            doc /*
             * The drive disables the motor on a following error (the
             * position error grows too large), on an encoder fault (lost
             * data or a bad check sum), and at software position limits.
             *
             * The stage has no limit switches that the drive can read. The
             * RSF AK MC 15 B read head gives only power and BiSS data on its
             * connector. The software limits use the absolute position. The
             * end stop dampers are the last protection. None of these is a
             * safety function with a Performance Level.
             */
            subject drive : MotorDrive;
            require constraint {
                drive.stopsOnFollowingError
                and drive.stopsOnEncoderFault
                and drive.hasSoftwarePositionLimits
            }
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

        requirement def <'DRV-P3'> FasterPositionLoop {
            doc /*
             * Above the 4 kHz of DRV-09, a faster position loop is better.
             * It adds less delay, so the loop can have more gain before it
             * becomes unstable. Rank the drives that pass by this rate.
             * The constraint below marks a clearly faster drive: 8 kHz or
             * more, which is 125 µs or shorter.
             */
            subject drive : MotorDrive;
            require constraint { drive.positionLoopRate >= 8000 [Hz] }
        }

        requirement def <'DRV-P4'> HigherSafeTorqueOff {
            doc /*
             * STO at SIL 3 and PL e. A customer whose risk assessment needs
             * PL e can then use the drive without an extra contactor.
             */
            subject drive : MotorDrive;
            require constraint {
                drive.stoSafetyIntegrityLevel >= 3
                and drive.stoPerformanceLevel >= 5
            }
        }

        requirement def <'DRV-P5'> SaferStopping {
            doc /*
             * Features that make a stop shorter or safer:
             *
             * - Safe Stop 1 (SS1): the drive brakes the carriage first, and
             *   then switches to STO. The carriage then does not coast into
             *   the end stop.
             * - A brake output, for a customer who mounts the stage
             *   vertically and adds a holding brake.
             * - Dynamic braking: on a fault the drive shorts the motor
             *   phases, and the motor brakes itself.
             */
            subject drive : MotorDrive;
            require constraint {
                drive.hasSafeStop1
                and drive.hasBrakeOutput
                and drive.hasDynamicBraking
            }
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
        in part stage : LinearMotorStage;

        requirement continuousCurrent : Mandatory::ContinuousCurrent;
        requirement peakCurrent : Mandatory::PeakCurrent;
        requirement motorCurrentProtection : Mandatory::MotorCurrentProtection;
        requirement busVoltage : Mandatory::BusVoltage;
        requirement linearMotorCommutation : Mandatory::LinearMotorCommutation;
        requirement motorThermalSensor : Mandatory::MotorThermalSensor;
        requirement etherCAT : Mandatory::EtherCAT;
        requirement encoderInput : Mandatory::EncoderInput {
            in part :>> stage = MotorDriveSpecification::stage;
        }
        requirement positionLoopRate : Mandatory::PositionLoopRate;
        requirement bodePlotTuning : Mandatory::BodePlotTuning;
        requirement ceMarking : Mandatory::CeMarking;
        requirement safeTorqueOff : Mandatory::SafeTorqueOff;
        requirement faultStops : Mandatory::FaultStops;
    }

    requirement currentDriveSpecification : MotorDriveSpecification {
        doc /* The drive requirements for the stage as it is today. */
        in part :>> stage = currentStage;
    }
}
