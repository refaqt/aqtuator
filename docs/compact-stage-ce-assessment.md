# Compact stage: preliminary CE assessment

This is a first check of the compact stage design against the EU safety rules for machines. It
lists what must change or be added to make the stage safer, and which safety features the servo
drive must have. It is not a full risk assessment, and it does not replace one.

Date: 2026-11-06, updated 2026-11-09. Design state: the CAD and the architecture of
[`modules/compact-stage/`](../modules/compact-stage/) on 2026-11-09, with the water-cooled forcer.

This assessment follows the **Machinery Regulation (EU) 2023/1230**, which applies from
20 January 2027. The stage will be sold after that date.

## Short answer

- **Legal route: the stage is "partly completed machinery"** under the Machinery Regulation (EU)
  2023/1230. A customer always builds it into a larger setup. So the stage gets technical
  documentation, a Declaration of Incorporation and assembly instructions, not a CE mark under
  the machinery rules. The customer makes the CE assessment of the whole machine. The drive keeps
  its own CE mark. This holds also when we sell a drive with the stage, as long as the customer
  connects and sets it up in their own machine.
- **The Regulation replaces the Machinery Directive 2006/42/EC on 20 January 2027.** Everything
  below is written for the Regulation. It also asks that safety settings in software are
  protected against changes, so drive limits that we pre-set must be documented and locked.
- **Most important design point: the end stops are too weak for the top speed.** The two TA17-7
  dampers per end take 12 J per stroke, 18 J in an emergency. At 3 m/s (STG-09) and 5 kg, the
  carriage brings 22.5 J. If the motor keeps pushing during the crash, it adds about 4.7 J. With
  no safety-rated limit switch, the dampers are the last protection. Choose: a lower declared top
  speed, a declared largest payload, stronger end stops, or a combination. A table gives the
  speed limit to lock in the drive for each payload: see
  [Largest payload against the speed limit](#largest-payload-against-the-speed-limit). **This is a design
  limit, not only a text for the customer**: see
  [Payload and top speed are design limits](#payload-and-top-speed-are-design-limits).
- **The limit switches are removed, and that is acceptable for safety.** The RSF read head has no
  limit signal (its own manual, and confirmed by Niels on 2026-11-06). The drive stops the
  carriage at software position limits, from the absolute position. Limit switches were never a
  safety function for people: guards and Safe Torque Off protect people. The dampers must hold
  the worst case. See [Without limit switches](#without-limit-switches).
- **The water-cooled forcer adds one danger**: water close to parts at about 325 V. The leak test
  that is already planned, the protective earth of the carriage and a leak check in the
  instructions cover it (H13).
- **Safe Torque Off is the customer's main stop.** See
  [When the STO must work, and how to make it compliant](#when-the-sto-must-work-and-how-to-make-it-compliant).
- **None of your drive options passes all safety features yet in its own documents.** The Copley
  XEL fails: it has no certified Safe Torque Off. Delta ASDA-A3 has the best documented one. For
  the others, the Declaration of Conformity or the safety certificate is missing. See
  [the drive table](#the-drives-on-your-list).
- **The drive needs three safety features**: the CE mark (Low Voltage, EMC and RoHS directives),
  a certified Safe Torque Off at SIL 2 / PL d or better, and motor stops on a following error, an
  encoder fault and at software limits. These are now hard requirements DRV-11 to DRV-13 in
  [`motor-drive.sysml`](../modules/compact-stage/architecture/motor-drive.sysml).
- **Other points to add**: warnings and assembly steps for the strong magnets (963 N attraction),
  a protective earth point on the base, a flex-rated motor cable with strain relief, a "horizontal
  only" rule, and the data an integrator needs to design the guards.

## What this means

The stage moves a carriage with up to 670 N at up to 3 m/s. It has strong magnets and parts at
mains voltage. Those are the three main dangers: crushing at the travel ends, magnets during
assembly, and electric shock.

The customer guards the stage (covers, doors, light curtains). That is fine for partly completed
machinery. But we must make the stage itself as safe as we reasonably can, and we must tell the
customer every danger that is left and what they must do about it.

## The rule

### Which law applies

| Topic | Rule from 20 January 2027 |
| --- | --- |
| The stage, built into a customer machine | Machinery Regulation (EU) 2023/1230, as partly completed machinery. We must: meet the essential health and safety requirements (Annex III) that apply to the stage; write the technical documentation (Annex IV, Part B); sign a Declaration of Incorporation (Annex V, Part B); and give assembly instructions (Annex XI). The Declaration and the instructions go with every stage. They may be in digital form |
| The drive | Its maker's CE mark: Low Voltage Directive 2014/35/EU, EMC Directive 2014/30/EU, RoHS Directive 2011/65/EU. The STO safety function falls under the machinery rules as a safety function of the drive |
| The encoder | RSF declares the EMC and RoHS directives in its mounting instructions |
| The motor | The motor maker's declaration. Ask MAXWELL (through Saho) for it |

The annex numbers come from summaries that agree with each other, including the
[EUR-Lex summary](https://eur-lex.europa.eu/EN/legal-content/summary/machinery-safety-requirements.html).
Check them in the full text on EUR-Lex before the technical file is final. Our network blocked
the full text.

Notes:

- **Research use is not an exception for us.** The machinery rules leave out machines "specially
  designed and constructed for research purposes for temporary use in laboratories". That fits a
  one-off machine that a lab builds for itself. It does not fit a product line that we sell to
  many customers. A specialist should confirm this.
- **If we ever deliver a ready-to-run axis** (stage, drive, wiring, controller and stop circuit,
  set up by us), it becomes a complete machine. Then we must put the CE mark on it, and the full
  risk assessment and the guards become our job.
- **Partly completed machinery must still meet the essential safety requirements that we can
  meet.** The Declaration of Incorporation lists which ones we applied. The rest go to the
  customer through the assembly instructions.
- **New in the Regulation: protection against changes ("corruption").** Safety settings in
  software and parameters must be protected against changes by accident or on purpose. For us
  this means: if we deliver a drive with pre-set limits (current, speed, software position
  limits, following error), we write them down in the technical file and lock them with a
  password.
- **A big change by the customer can make them the manufacturer.** If a customer changes the
  stage in a way we did not plan (a heavier payload, a higher speed, vertical mounting without a
  brake), the Regulation can treat that as a substantial modification. The assembly instructions
  must state the limits clearly, so this line is easy to see.
- **Standards give a presumption of conformity only when they are listed in the Official Journal
  under the Regulation.** Check the list for each standard below before the technical file is
  final.

### Standards to use

| Standard | What for |
| --- | --- |
| EN ISO 12100 | Risk assessment and risk reduction (the method for this whole document) |
| EN ISO 13849-1 | Safety level (Performance Level, PL) of the stop functions |
| EN 61800-5-2 | Safety functions of the drive (STO, SS1, SBC) |
| EN 60204-1 | Electrical equipment of machines: protective earth, cables, stop categories |
| EN ISO 13857 and EN ISO 13854 | Safety distances and smallest gaps, for the guard design of the integrator |
| EN ISO 13732-1 | Hot surfaces that people can touch |
| EN ISO 7010 and ISO 3864 | Warning signs |

## Hazards and what to do

Severity: **high** means a serious injury is possible (broken bones, lost finger). **Medium**
means an injury that heals. **Low** means a small injury or only damage to the stage.

| No. | Danger | Where and when | Severity | What the design does today | What to change or add |
| --- | --- | --- | --- | --- | --- |
| H1 | Crushing of hands at the travel ends | Between the carriage ends and the base end walls, and between the carriage top and parts the customer adds. In operation and during set-up | High | Nothing on the stage. Guarding is left to the integrator | State in the instructions: the force (670 N for 0.5 s), the speed (3 m/s), the crush zones, and the stop distance with STO. Require guards and an STO stop circuit in the instructions. Put a crush warning sign (ISO 7010 W019 or W024) on both ends of the base |
| H2 | Crash into the end stops | Carriage runs away (wrong set-point, tuning error, encoder fault) | Medium for people (parts fly off), high for the stage | Two ACE TA17-7 per end: 12 J per stroke, 18 J emergency. Enough for 5 kg at about 2.2 m/s | See [End stop energy](#end-stop-energy). Fix the largest payload and the declared top speed so the dampers hold the worst case. Or choose stronger end stops |
| H3 | No hardware end of travel signal | The limit switches were removed on 2026-11-09. The RSF head has no limit signal | Low for people, medium for the stage | Software limits in the drive, from the absolute position (DRV-13) | Set the software limits inside the damper contacts. The dampers must hold the worst case (H2). See [Without limit switches](#without-limit-switches) |
| H4 | The carriage falls when power is off | Only if the stage is mounted vertically or on a slope. The linear motor has no brake | High | Nothing | State "horizontal mounting only" in the instructions and on the label. For other positions the customer adds a brake or a holding device. A drive with a brake output (DRV-P5) makes this easy |
| H5 | Magnet attraction: crushed fingers | When the carriage is lifted off or put on the base. The MK21 forcer pulls on the magnet tracks with 963 N. Steel tools jump onto the tracks | High | Nothing | Assembly and service steps: lower the carriage along the guide rails only, never by hand onto the magnets. Consider a simple mounting aid (two threaded jacking screws, or a plastic spacer). Warning sign "magnetic field" (ISO 7010 W006) on the base |
| H6 | Magnetic field: medical implants and data | Near the open magnet tracks, mainly during service and shipping | High for people with a pacemaker | Nothing | Warning sign (ISO 7010 P007 "no access for people with pacemakers") and a text in the instructions. Check the air transport rule for magnetised material before shipping by air |
| H7 | Electric shock | Motor cable and plug (bus about 325 V DC). Also when the carriage is pushed by hand: the motor makes 53.4 V rms per m/s at its open plug | High | The motor cable runs through a channel in the bottom carriage | A protective earth point on the base, with a symbol (IEC 60417-5019). The carriage is earthed through the forcer and the earth wire of the motor cable: see [Earthing of the carriage](#earthing-of-the-carriage). A motor cable rated for constant flexing, with its earth wire. Strain relief at the forcer and at the base. Instructions: never open the motor plug while the carriage moves, wait for the drive's bus discharge time |
| H8 | Hot surface | The coil may reach 120 °C. The forcer sits under the carriage | Low to medium | The PTC sensor in the coil, read by the drive (DRV-06), and the motor current protection (DRV-03) | Measure the outside temperature of the carriage at the continuous force. If it goes above the touch limit of EN ISO 13732-1, add a "hot surface" sign (ISO 7010 W017) |
| H9 | Cuts from the steel seal strip | 0.15 mm strip under 270 N pull. During assembly and service | Medium | Six M4 screws hold it. The preload screw sets the pull | Instructions for fitting and removing the strip: gloves, release the pull with the preload screw first. Deburr the strip edges |
| H10 | Parts come loose from a crash | Damper, read head, payload screws, after an impact of about 53 g | Low to medium | The read head is rated for 1000 m/s² (about 100 g) shock in the RSF manual. The damper study gave about 53 g at 2 m/s | Use thread locker on the damper and payload screws. Tell the customer to check the dampers after every crash, and to change them as ACE asks |
| H11 | Unexpected start | A fault or a set-point at power-on | High (same as H1) | Depends on the drive | The customer's stop circuit uses STO (DRV-12). The drive must not start the motor by itself after power returns. Put this in the instructions |
| H13 | Water near live parts | The forcer is water cooled. The cooling channel is closed by the forcer face and an O-ring. A printed block with hose barbs connects the hoses. A leak can wet the motor (about 325 V) and the cable opening | High (electric shock if the carriage is not earthed), medium for the motor | The O-ring seal, and a leak test of the block at 2 bar for 1 hour before the motor is powered (decision of 2026-11-06) | Earth the carriage, not only the base (H7, [Earthing of the carriage](#earthing-of-the-carriage)). Make the leak test a fixed step of assembly, and write it down for each stage. In the instructions: the allowed water pressure and temperature, a check for leaks before the motor is powered, and switch off the drive before the hoses are taken off. The customer's supply must have a residual current device that suits a servo drive (ask the drive maker which type) |
| H12 | Wrong use of the encoder signal for safety | An integrator uses the RSF position for a safety function | High | Nothing | RSF says the MC 15 may only be used for length and position information. State in the instructions that the stage has no safety-rated position or speed signal |

### Earthing of the carriage

The carriage carries the forcer, and it is close to the motor cable and the cooling water. So it
needs a protective earth, like the base (EN 60204-1).

**The carriage can be earthed through the forcer, under three conditions:**

1. **The earth wire of the motor cable must connect to the metal body of the forcer.** The MAXWELL
   MK2 data sheet does not show the cable wiring. This is **not confirmed**: ask MAXWELL (through
   Saho) for the wiring of the MK21 cable and how the earth wire is connected.
2. **Bare metal contact between the forcer and the bottom carriage.** Anodising insulates. If the
   bottom carriage is anodised, leave the forcer face bare, or use toothed lock washers under the
   forcer screws, or add a short earth wire from the forcer to the carriage.
3. **The same between the top and the bottom carriage.** The top carriage needs its own good
   contact, in the same way.

**The guide blocks are not an earth path.** The balls run in grease, so the contact is not
reliable. The base therefore needs its own earth terminal to the earth of the machine.

**After assembly, measure the earth path** from the top carriage to the earth terminal of the
drive (continuity test, EN 60204-1). Write the result in the assembly record of each stage.

### End stop energy

The kinetic energy is E = ½ m v². The motor can also push while the damper is pressed in: at most
670 N over the 7 mm stroke, about 4.7 J. If the drive's peak current is locked at 5.9 A (512 N),
the push is about 3.6 J.

Two TA17-7 per end take 12 J per stroke and 18 J in an emergency (ACE TUBUS TA instructions, page
3, as in the [end bumper study](log/2026-10-21_space-for-end-bumpers.md)). A runaway crash is a
rare event, so the emergency rating applies. After such a crash the dampers must be checked or
changed.

**Moving mass without payload: about 4.2 kg (estimate).** Bottom carriage 1.19 kg and top
carriage 1.13 kg (CAD volumes, aluminium at 2.7 g/cm³), forcer 1.10 kg, four guide blocks
0.60 kg, read head 0.05 kg, dampers 0.02 kg, screws, cables, hoses and water about 0.15 kg. Weigh
the first real carriage and correct the table if needed.

#### Largest payload against the speed limit

The speed to set in the drive is the highest safe impact speed divided by 1.1. A runaway carriage
can reach the overspeed trip of the drive before the drive stops it, and that trip is usually 10 %
above the speed limit.

| Payload on the carriage | Speed limit to set (motor push 670 N) | Speed limit to set (peak current locked at 5.9 A) |
| --- | --- | --- |
| 0 kg | 2.28 m/s | 2.37 m/s |
| 1 kg | 2.05 m/s | 2.13 m/s |
| 2 kg | 1.88 m/s | 1.95 m/s |
| 3 kg | 1.74 m/s | 1.81 m/s |
| 5 kg | 1.54 m/s | 1.61 m/s |
| 7.5 kg | 1.37 m/s | 1.42 m/s |
| 10 kg | 1.24 m/s | 1.29 m/s |
| 15 kg | 1.07 m/s | 1.11 m/s |
| 20 kg | 0.95 m/s | 0.99 m/s |

- **3 m/s (STG-09) is not possible at any payload with today's dampers.** It needs stronger end
  stops. The end bumper study shows the TA21-9 and the TA22-10 do not fit the 20.4 mm free height
  today, so a different damper type or a changed base would be needed.
- **How to use the table.** Take the row at or above the customer's real payload, including
  grippers, fixtures and a second stage on top. Set and lock in the drive: the speed limit, the
  peak current limit (5.9 A for the right column), and the overspeed trip (at most 10 % above
  the limit). Write the payload and the speed on the type plate and in the delivery record.
- **The locked speed limit is a protective measure, not a safety function.** The encoder is not
  safety rated (H12), so the end stops must still hold the worst case. The table is made so that
  they do.
- **The drive must also stop the motor on the crash** (following error, DRV-13). That makes the
  real impact milder than the table assumes.

### What happens when the dampers are overloaded

If the carriage hits the end faster than the table allows, the damper is pressed in fully (7 mm).
The rest of the energy then goes into a hard metal hit between the damper body and the base end
wall. For a very short time the force becomes much higher than the 2.6 kN of a normal damper
stop.

**Damage to the stage (likely):**

- the damper is destroyed;
- dents in the carriage end and the end wall;
- the M4 damper screws or square nuts tear out;
- ball marks on the guide blocks and rails;
- the read head gets a shock above its 1000 m/s² rating;
- the forcer screws and the payload screws take a large load.

**Danger to people (possible, but limited):** parts can be thrown off. Most likely is the
customer's payload, if it is not held well, or pieces of a broken damper or screw. The energy
above the damper rating is about 5 to 10 J, about the same as a 1 kg part falling from 1 m. That
can hurt an eye or a hand. It cannot break a proper guard.

**A hand at the end of the travel is crushed in any case** (H1), with or without overload. People
are protected by the guards and by Safe Torque Off, not by the dampers.

**Conclusion:** an overload is mainly damage to the stage, with a small danger from thrown parts.
The measures:

1. the locked speed table above;
2. the payload held with screws and thread locker, as the assembly instructions say;
3. guards that can hold small thrown parts (the customer's job, stated in the instructions);
4. an inspection of the dampers, the guides and the read head after every crash.

**Crash simulation of 2026-11-10.** A model of a crash at 2 m/s with the motor pushing confirms
this picture. With no payload, the read head gets about its 1000 m/s² rating. From 1 kg it gets more.
With a second stage on top, the guide blocks are dented, the screws between the two carriage halves
shear off, and the upper stage and the base slide on their screws. Thread locker does not stop a
joint from slipping. Dowel pins or a stop edge do. The base itself keeps a dent of 0.004 mm at most.
See the [crash results](../modules/compact-stage/simulation/results/end-stop-crash/summary.md).

### Payload and top speed are design limits

Telling the customer is not enough on its own. The risk assessment standard EN ISO 12100 sets a
fixed order:

1. **Safe design first.** We choose the largest payload and the top speed, and we make sure the
   end stops can stop that worst case. The stage requirement STG-15 now holds this rule, and the
   attribute `maxPayload` waits for a number.
2. **Then protection.** If we deliver the drive, we pre-set its current limit, its speed limit and
   its software position limits, and we lock them (see the protection against changes above).
3. **Then information.** The limits go on the type plate, in the technical data and in the
   assembly instructions.

Information alone is only allowed for the danger that design and protection cannot remove. A
customer who goes over the limits changes the stage beyond what we planned. The clear limits make
that easy to see.

### Without limit switches

The RSF read head has no limit signal, so the two inductive switches are removed from the parts
list. This is acceptable for safety, for these reasons:

- **Limit switches protect the machine, not people.** A normal limit switch has no safety level
  (no Performance Level). People are protected by the customer's guards and by Safe Torque Off.
  That is the same with or without limit switches.
- **Software limits do the same job.** The drive stops the carriage at a set position. With an
  absolute encoder this works at once after power-on, without a homing run.
- **The weak point is a position that is wrong but looks right**, for example when the scale
  moved or was stuck on in the wrong place. A separate switch would catch that, software limits
  do not. Then the carriage hits the dampers. So the dampers must hold the worst case (H2), and
  the assembly instructions must include a check of the software limits after assembly and after
  every change of the scale or the read head.
- **The drive still stops on an encoder fault** (lost data or a bad check sum, DRV-13).

If a customer controller needs a hardware end signal, the customer can add switches. The base
has no fixed place for them now.

## Safety features the drive must have

The drive is not chosen yet. These features are now in
[`motor-drive.sysml`](../modules/compact-stage/architecture/motor-drive.sysml).

| Short name | Feature | Kind | Why |
| --- | --- | --- | --- |
| DRV-11 | CE mark and an EU Declaration of Conformity: Low Voltage Directive (EN 61800-5-1), EMC Directive (EN 61800-3), RoHS Directive. Note the EMC category (C2 or C3) and whether an extra mains filter is needed | Hard | The stage is partly completed machinery, so the drive must bring its own CE mark |
| DRV-12 | Safe Torque Off (STO), certified by a testing body, at least SIL 2 and PL d | Hard | The customer's emergency stop and door switches act through it (H1, H11) |
| DRV-13 | Stops the motor on a following error, on an encoder fault, and at software position limits | Hard | Replaces the limit switches (H3), and stops the motor push in a crash (H2) |
| DRV-P4 | STO at SIL 3 and PL e | Preferred | A customer whose risk assessment asks for PL e can use the drive directly |
| DRV-P5 | Safe Stop 1 (braked stop, then STO), a brake output, and dynamic braking (the drive shorts the motor phases on a fault) | Preferred | Shorter stops, less coasting into the dampers (H2), and a brake for vertical use (H4) |
| DRV-P6 | The settings can be locked with a password: speed limit, peak current, overspeed trip, software position limits | Preferred | We lock the speed limit for each customer from the payload table. The Regulation asks to protect safety settings against changes |

Already required for the motor: a current limit with a thermal model (DRV-03) and the PTC input
(DRV-06). They protect the motor from overheating (H8).

**Why PL d as the floor.** With the risk graph of EN ISO 13849-1: a crushed hand can be a serious
injury (S2). Access is rare when the stage is guarded (F1), and a person cannot get out of the way
of a 3 m/s carriage (P2). That gives PL d. When people often work near the moving carriage, for
example during set-up in a lab (F2), it gives PL e. The customer makes the final choice in their
own risk assessment.

### The drives on your list

Checked on 2026-11-06 in the makers' own manuals and data sheets. **Pass** and **Fail** mean the
maker's document gives the answer. **NC** (not confirmed) means we could not read it in a maker's
document. NC never counts as a pass. We did not open an EU Declaration of Conformity or an STO
certificate for any drive. Ask for both with every quotation.

Elmo, Servotronix and Agito Akribis are checked because you asked. They stay excluded by the
recorded rule that we do not buy from Israeli suppliers
([decision of 2026-10-06](decisions/2026-10-06_kollmorgen-akd-and-copley-xenus-plus-as-candidates.md)).

| Drive | DRV-11 CE (LVD, EMC, RoHS) | DRV-12 STO, SIL 2 / PL d, certified | DRV-13 Fault stops | DRV-P4 SIL 3 / PL e | DRV-P5 SS1, brake output, dynamic braking | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Kollmorgen AKD-x00306, EtherCAT | Pass. Machinery, LVD, EMC and RoHS directives listed. Needs an external filter: C2 with a motor cable under 10 m, C3 above | SIL 2, PL d, Cat 3, one STO input. The manual names no testing body: **NC** | Pass. Following error, feedback fault, software limit | No | No safe SS1. Brake output yes. Dynamic braking yes | **Close.** Ask for the STO certificate |
| Kollmorgen AKD2G-SPE-6V03S-A1F3-0000-A | **NC.** The only manual we could open (beta, 2018) says approvals are pending. Needs an external filter for C2 | Option 1: two channels, SIL 2, PL d, Cat 3. Approval pending in that edition: **NC** | NC (not read in the manual) | No. Options 2 and 3 (other order codes) give SIL 3 with SS1, SBC and SLS | Brake output yes (2.5 A). Dynamic braking yes | **Not confirmed.** Ask for the current manual, the Declaration of Conformity and the STO certificate |
| Copley Xenus Plus XEL-230-18 | NC. EMC and LVD listed, but with the standards IEC 61010-1 and EN 55011, not EN 61800. Line filter required for CE. RoHS not read | **Fail.** The XEL has "Motor Torque Off", which Copley says "does not have the certifications of STO" | Pass for following error and feedback error. Software limits NC | No | Brake output yes (1 A). Dynamic braking NC | **Fails DRV-12.** The two-axis XE2 has a TÜV SÜD STO (SIL 3, PL d) |
| Delta ASD-A3-0421-E | NC. The STO table lists the machinery and LVD standards. The full Declaration was not opened. Filter recommended for C2 | **Pass.** Two channels, certified by TÜV SÜD. SIL 3 / PL e with the monitor output wired, SIL 2 / PL d without | Pass. Position error, encoder fault, software limits | Pass, with the monitor output wired | No SS1. Brake signal only through a relay. Dynamic braking yes | **Best on STO.** Still the converter and loop rate problems from the drive page |
| HIWIN E1 ED1F-EN-0422-01-00 (safety version 1) | Pass. CE mark, LVD, EMC and RoHS. **EMC category C3** | SIL 3, PL e, Cat 3, two inputs and a monitor output. The manual names no testing body: **NC** | Pass for position error and encoder faults. Software limits NC | Pass on paper | No SS1. Brake output yes. Dynamic braking yes | **Close.** C3 means it is not meant for a public low-voltage network (many labs) without extra filtering. HIWIN cannot deliver it in Europe today (drive page) |
| DGSMARTWIN AKS-4D52AECAB | **NC.** The manual only says the drive is tested to the standards. Its table is almost word for word the Servotronix table, with an old EMC directive. No Declaration seen | SIL 3, PL e, Cat 3 claimed, two inputs. No testing body named: **NC** | Pass. Following error, encoder faults, soft limits from the absolute encoder | Pass on paper | Brake output yes. Dynamic braking yes (emergency stop only). No SS1 | **Not confirmed.** Ask for the Declaration of Conformity and the STO certificate before you trust the CE mark |
| Elmo Gold Oboe 6/230 (excluded) | NC. Only the old LVD 2006/95/EC. Elmo leaves EMC to the maker of the end product | SIL 3, PL e, Cat 3, certificate Z10 13 08 84596 001 (issuer not named): **Pass on level, issuer NC** | NC | Pass | No SS1. Brake output yes. Dynamic braking NC | Excluded |
| Servotronix CDHD2S-0032AEC2 (excluded) | NC. "Will be tested and certified". Filter required | **Fail.** "STO certification for all CDHD2S models is currently pending", and one input pair only | Pass | No (not certified) | Brake through a relay. Dynamic braking yes | Excluded |
| Agito Akribis AGD155-EC-2A06 (excluded) | NC. Only IEC 61800-5-1 and IEC 61800-3 named, no directive | **Fail.** Two inputs, "pending certification", no SIL or PL | Pass | No | Brake output yes. Dynamic braking NC | Excluded |

What this means for the choice:

- **No drive on the list passes all three new hard requirements in its maker's own documents.**
  The missing piece is almost always the paper: the Declaration of Conformity and the STO
  certificate. Ask for both in every quotation request.
- **The Copley Xenus Plus XEL fails.** It has no certified STO. If you want Copley, ask about the
  XE2 (two axes, certified STO), or add a certified safety contactor in the motor cable.
- **Delta ASDA-A3** has the best documented STO (TÜV SÜD, up to SIL 3 / PL e).
- **Kollmorgen AKD** reaches SIL 2 / PL d. That is enough for DRV-12, but not for a customer who
  needs PL e.
- **No drive on the list has a certified Safe Stop 1** in these order codes. A customer can build
  SS1 with a safety relay that has a time delay: it first stops the drive by command, then opens
  STO.
- **No drive documents a limit switch signal from BiSS-C.** Software limits from the absolute
  position are the way to go.

## When the STO must work, and how to make it compliant

Safe Torque Off (STO) cuts the power that makes the motor push. It does not brake the carriage,
and it does not cut the mains.

### When it must work

| Situation | What STO does | Standard |
| --- | --- | --- |
| Someone presses the emergency stop | Stop category 0: STO at once. Or stop category 1: a braked stop, then STO (Safe Stop 1) | EN ISO 13850, EN 60204-1 |
| A guard door opens, or a light curtain is broken | The motor cannot push while a person can reach the carriage | EN ISO 14119, EN ISO 13855 |
| A person works in the danger zone: set-up, loading a part, cleaning | Prevents an unexpected start. After a reset, the motor must not start by itself | EN ISO 14118 |
| Electrical work on the motor, the cable or the drive | **STO is not enough.** The DC bus stays charged. Use the main switch, lock it, and wait for the discharge time | EN 60204-1 |

**The stopping distance matters.** After STO alone, a linear motor coasts: it has no brake and
little friction. At 3 m/s the carriage may run into the end stop. The guard distance of the
customer (EN ISO 13855) depends on this time and distance. A braked stop first (Safe Stop 1)
makes both much shorter. That is why DRV-P5 prefers it.

### How to make it compliant

The customer builds the stop circuit, because it belongs to their machine. The steps:

1. **Set the required level.** The customer's risk assessment sets the required Performance
   Level (PLr). We advise PL d, or PL e when people often work close to the moving carriage.
2. **Use certified parts only.** An emergency stop button or a door switch, then a safety relay
   or a safety controller, then the two STO inputs of the drive. Each part has its own safety
   rating from its maker.
3. **Wire it as the drive's safety manual says.** Two channels. The safety relay reads the
   drive's STO feedback output (Delta needs this for PL e). A 24 V safety supply (PELV). The
   wiring stays inside the cabinet, or is protected against short circuits.
4. **Calculate the level of the whole chain** with EN ISO 13849-1, for example with the free tool
   SISTEMA from the German institute IFA. The result must reach the PLr.
5. **Validate it on the real machine** (EN ISO 13849-2). Test every stop function, measure the
   stopping time and distance, and write it all down.
6. **Test it again** at the interval in the drive's safety manual.

What we give the customer, in the assembly instructions:

- the drive's safety manual and its STO certificate (when we supply the drive),
- the measured stopping time and distance of the stage, after STO and after Safe Stop 1, at the
  top speed and the largest payload,
- a suggested wiring diagram for the stop circuit,
- our advice on the required level, and the reason for it.

## What to do next

1. **Fix the payload and the top speed** (H2). Put the largest payload in `maxPayload` and check
   STG-15. Either lower STG-09 or plan stronger end stops.
2. **Measure the stopping distance** after STO and after a braked stop, once the drive is chosen.
   The customer needs it for the guard design.
3. **Choose the drive with DRV-11 to DRV-13 included.** Ask each maker in the quotation request
   for the EU Declaration of Conformity and the STO certificate.
4. **Add to the CAD**: a protective earth point on the base, strain relief for the motor cable,
   and places for the warning signs (H5, H6, H7, H1).
5. **Measure** the carriage surface temperature at the continuous force (H8).
6. **Ask MAXWELL (through Saho)** for the Declaration of Conformity of the MK21 and the MK2
   magnet tracks, and for their advice on handling the magnets.
7. **Write the technical file** for the Regulation: the full risk assessment (EN ISO 12100), the
   technical documentation (Annex IV, Part B), the Declaration of Incorporation (Annex V, Part B),
   and the assembly instructions (Annex XI) with every point from the table above.
8. **Make the cooling leak test a fixed assembly step** with a written record per stage (H13).

## When to get a human specialist

Ask a machine safety consultant or a notified body (an official testing body) to check the full
risk assessment, the Declaration of Incorporation and the assembly instructions before the first
sale. Ask them also to confirm the annex numbers of the Regulation and the list of harmonised
standards on that date. This document is
a first engineering check, not legal advice.

<details>
<summary>Technical notes</summary>

- Motor values: MAXWELL MK2 data sheet, through
  `modules/stoq/modules/maxwell/modules/mk2-mover/bom/parts.csv` (attraction 963 N, back EMF
  53.4 V rms per m/s, 670 N for 0.5 s) and `MaxwellMK21` in `motor-drive.sysml`.
- Damper ratings: ACE TUBUS TA operating and mounting instructions 21_22_0019, page 3, as cited in
  `docs/log/2026-10-21_space-for-end-bumpers.md`. Motor push: 670 N × 0.007 m = 4.69 J, or
  512 N × 0.007 m = 3.58 J.
- Speed table: v_impact = √(2 × (18 J − push) / (4.24 kg + payload)); speed limit = v_impact / 1.1.
  Moving mass 4.24 kg = 1.19 + 1.13 + 1.10 + 0.60 + 0.05 + 0.02 + 0.15 kg. Carriage volumes
  441 660 mm³ and 417 780 mm³ from `cad/parts/*/carriage-*.fingerprint.json`. Guide block 150 g
  from `modules/stoq/modules/hiwin/` parts list. Forcer 1.1 kg from the MAXWELL data sheet.
- MAXWELL MK2 data sheet (`modules/stoq/modules/maxwell/docs/datasheets/`): no cable wiring or
  earth connection given.
- RSF AK MC 15 mounting instructions
  (`modules/stoq/modules/rsf/modules/mc15-readhead/docs/datasheets/rsf-ak-mc15-mounting-instructions.pdf`):
  section 1.2 (EMC 2014/30/EU, RoHS 2011/65/EU), section 1.4 (intended use: length and path
  information only), section 2.1.1 (shock 1000 m/s², 6 ms), section 8.1 (BiSS C pins: UP, sensor
  UP, 0 V, sensor 0 V, SLO+, SLO−, MA+, MA−; no limit lines).
- Drive sources (PDF pages):
  [AKD installation manual, edition AG 2022](https://www.kml-technology.com/wp-content/uploads/2024/05/Kollmorgen_AKD_Installation_EN.pdf) p. 28 to 30, 46, 58, 196 to 198;
  [AKD2G with safety option 1, beta 2018](https://inmoco.co.uk/wp-content/uploads/2022/01/AKD2G-Installation-Manual-with-FS1.pdf) p. 29 to 32, 36 to 42, 127 to 129;
  [Copley XEL data sheet](https://s3.amazonaws.com/www.motionusa.com/copley/XenusPlus_XEL-ds.pdf) p. 2, 3, 7, 17 to 19 and
  [Xenus Plus user guide rev 06](https://www.aoyamasteel.co.jp/wp-content/uploads/2024/11/AmpManual-XEL.pdf) p. 5, 11, 50 to 59, 65;
  [Delta ASDA-A3 manual 2025](https://www.damencnc.com/userdata/file/7617-5_Delta_ASDA_A3_Manual_English_2025.pdf) p. 68, 69, 76, 77, 130, 131, 181, 183, 635, 695, 696;
  HIWIN E1 manual MD09UE01 V3.3 from [hiwinmikro.tw](https://www.hiwinmikro.tw/Downloads/ManualOverview_EN.htm), printed page vii, p. 12-5, 12-17, 13-7;
  DGSMARTWIN AKS manual, local copy `docs/documentation/AKS Drive Manual.pdf`, sections 2.8, 4.7, 5.2.6, 10.2.3;
  [Elmo Gold Oboe installation guide](https://inelso.ru/upload//specs/MAN-G-OBOEIG-EC.pdf) p. 7, 12, 16;
  [Servotronix CDHD2S manual V1.12](https://e-motors.tech/wp-content/uploads/2024/07/CDHD2S-Manual-V1.12-20231101-en.pdf) p. 20, 29, 52, 91, 242;
  [Agito AGD155 product manual rev 3.4](https://agito-akribis.com/wp-content/uploads/2026/10/Agito-AGD155-Product-Manual-Rev.3.4.pdf) p. 17, 22, 30 to 33.
- Limit switches: `SW-001` and `ELC-001` removed from `modules/compact-stage/bom/bom.csv` on
  2026-11-09. They appear elsewhere only in old log entries.
- Regulation (EU) 2023/1230: application date and annexes from the
  [EUR-Lex summary](https://eur-lex.europa.eu/EN/legal-content/summary/machinery-safety-requirements.html),
  [EU-OSHA](https://osha.europa.eu/es/legislation/directive/regulation-20231230eu-machinery) and
  published Declarations of Incorporation. The full EUR-Lex text was blocked by the network.
- Water cooling: `docs/decisions/2026-11-06_forcer-cooling-sealed-with-standard-o-rings.md`.
- Mistake rules applied: deciding values only from the maker's own document
  (`docs/mistakes/2026-09-29_loop-rate-from-a-trade-article.md`), and search the whole repository
  when a bought part is removed (`docs/mistakes/2026-11-04_drive-check-used-the-old-encoder.md`).

</details>
