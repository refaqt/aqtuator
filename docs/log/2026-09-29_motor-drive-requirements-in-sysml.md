# 2026-09-29 — The motor drive requirements are now in the SysML model

**Role(s):** engineering, hardware, purchasing

## Goal

Write down the requirements for the servo drive of the linear motor stages in one place, as SysML.
Future drive searches can then cite each requirement by a short name instead of repeating the list.

## Work Done

The requirements are in [`architecture/motor-drive.sysml`](../../architecture/motor-drive.sysml).
They say what the job needs, not which brand fills it.

| Short name | Requirement | Kind |
| --- | --- | --- |
| DRV-01 | At least 2.0 A rms continuous | Hard |
| DRV-02 | At least 5.9 A rms for 1 s | Hard |
| DRV-03 | A settable peak current limit and a thermal model of the motor | Hard |
| DRV-04 | A DC bus of 160 V to 600 V | Hard |
| DRV-05 | Runs a linear synchronous motor with a 30 mm electrical period, and finds the commutation angle | Hard |
| DRV-06 | Reads the motor thermal sensor, or stops on it through an input | Hard |
| DRV-07 | EtherCAT with the CiA 402 drive profile | Hard |
| DRV-08 | Reads a 1 Vpp sine and cosine encoder or a BiSS-C encoder directly | Hard |
| DRV-09 | Position loop at 8 kHz or faster (125 µs or shorter) | Hard |
| DRV-P1 | Our own filters in the loop, best as a free second order filter (a biquad) | Preferred |
| DRV-P2 | A published block diagram of the control loop | Preferred |

DRV-01 to DRV-06 together mean "the drive can run the MAXWELL MK21". The motor values were read
again in the MAXWELL MK2 data sheet in the parts library, and they match the earlier drive survey.
The model also holds those motor values, with the data sheet as the source.

DRV-04 comes from the hand calculation in the
[drive survey of 2026-09-25](2026-09-25_linear-stage-drive-and-motion-controller-survey.md): 512 N at
10 000 mm/min with a hot coil needs about 158 V. A drive fed from 230 VAC single phase meets it.

Each hard requirement also says how to check it. The rule from
[the loop rate mistake](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md) is written into
the model: read the deciding number in the maker's own manual, or call the drive "not confirmed".

## Decisions Made

- The file sits in the top level `architecture/` folder, not inside a stage family. No stage family
  owns the MK21 stages yet.
- The earlier limits on price, on new units only, and on suppliers are not in the model. They are
  buying rules that change with each search, not technical requirements of the drive.

## Open Questions

- Does the MK21 we buy have Hall sensors? If yes, DRV-05 also passes a drive that reads them.
- What exactly is the thermal sensor "3 PNC SNM120 in series"? Ask MAXWELL before DRV-06 is checked.
- Which linear encoder do we use? Its signal period and top speed set the input frequency DRV-08
  asks for.

## Next Steps

- In the next drive search, check each candidate against DRV-01 to DRV-09 and rank the ones that
  pass with DRV-P1 and DRV-P2.
- Open the file once in SysON to confirm that it imports without errors. It was written by hand and
  was not checked by a SysML parser.
