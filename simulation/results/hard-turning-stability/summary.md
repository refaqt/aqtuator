# hard-turning-stability — results

Can the two stacked compact stages hard turn steel at 61 to 63 HRC? Results of
[the hard turning page](../../cases/hard-turning-stability/), calculated on 2026-11-11 with:

```bash
node simulation/cases/hard-turning-stability/check_model.mjs
```

The lathe bed and the spindle are rigid. Cut: CBN insert, 0.8 mm nose radius, depth of cut 0.2 mm,
feed 0.1 mm per turn, 150 m/min on a 50 mm part (955 rev/min). Loop rate 10 kHz. Estimates are
marked; the inputs and their sources are in the case README.

## Short answer

- **Yes, but only just, and only for a light finish cut.** At the defaults chatter starts at a
  depth of 0.22 mm. The cut asks for 0.20 mm. A margin of 1.1 is too small, because the damping
  and the force ratio are estimates.
- **The X motor is too weak for the steady thrust.** The model gives 316 N into the part. The MK21
  gives 181 N continuous. This number is uncertain (see the limits), but it is the first thing to
  measure.
- **Two changes make it work on paper:** a 20 kHz position loop and the longer QEH15CA blocks
  together allow 0.94 mm at mid travel and 0.41 mm at the worst end of the travel.

## Stiffness at the tool tip

| Direction | Static (guides and shank) | Lowest dynamic (with the motor loops) | At |
| --- | ---: | ---: | ---: |
| X, into the part | 82 N/µm | 4.9 N/µm | 471 Hz |
| Y, up | 43 N/µm | 4.8 N/µm | 463 Hz |
| Z, along the spindle | 29 N/µm | 2.3 N/µm | 447 Hz |

- The motors hold a steady force with no error, so the static stiffness is that of the guide blocks
  and the shank alone.
- The lowest dynamic stiffness comes from the whole stack above the lower blocks (about 17 kg)
  rocking on them. A lighter upper base moves this mode up (544 Hz with 0.5 kg in place of 6.7 kg),
  a heavier holder moves it down (346 Hz with 6 kg). The tool tip is 127 mm above those blocks, so a small tilt is a large motion.
- A downward cutting force also moves the tip along X (the coupling term is as large as the X term
  itself). The chatter model counts that.
- The steady forces bend the guides by 1.2 µm along X. That is a 2.3 µm error on the diameter.

## Depth of cut before chatter

| Case | At 955 rev/min | At every speed | Motor loops alone | Guides and shank alone |
| --- | ---: | ---: | ---: | ---: |
| Defaults | 0.219 mm | 0.200 mm | 0.435 mm | 0.715 mm |
| Loop rate 4 kHz (DRV-09 minimum) | 0.007 mm | 0.007 mm | 0.006 mm | 0.715 mm |
| Loop rate 20 kHz | 0.842 mm | 0.771 mm | 3.20 mm | 0.715 mm |
| Loop rate 40 kHz | 1.12 mm | 1.02 mm | 14.3 mm | 0.715 mm |
| QEH15CA blocks (187 N/µm) | 0.595 mm | 0.573 mm | 0.435 mm | 1.50 mm |
| 20 kHz and QEH15CA | 0.943 mm | 0.907 mm | 3.20 mm | 1.50 mm |
| 20 kHz and QEH15CA, upper carriage at +100 mm | 0.756 mm | 0.745 mm | 3.20 mm | 0.611 mm |
| 20 kHz and QEH15CA, upper carriage at −100 mm | 0.411 mm | 0.408 mm | 3.20 mm | 0.565 mm |
| Upper carriage at +100 mm | 0.076 mm | 0.073 mm | 0.435 mm | 0.238 mm |
| Upper carriage at −100 mm | 0.088 mm | 0.085 mm | 0.435 mm | 0.217 mm |
| Sideways block stiffness half of radial | 0.141 mm | 0.132 mm | 0.435 mm | 0.454 mm |
| Guide damping 0.02 | 0.143 mm | 0.135 mm | 0.435 mm | 0.396 mm |
| Guide damping 0.05 | 0.323 mm | 0.312 mm | 0.435 mm | 1.40 mm |
| F<sub>t</sub>/F<sub>c</sub> = 1.1 (sharp tool) | 0.423 mm | 0.423 mm | 0.759 mm | 1.60 mm |
| F<sub>t</sub>/F<sub>c</sub> = 2.5 (worn tool) | 0.037 mm | 0.031 mm | 0.155 mm | 0.083 mm |

- **At 955 rev/min the lobes lie 16 Hz apart, so the speed hardly matters.** The depth that is
  stable at every speed decides. Changing the spindle speed is not a way out.
- **The motor loops and the guides are weak at nearly the same frequency (about 370 Hz and
  480 Hz).** Their weak points add up, so together they allow less than either alone.
- **4 kHz is not enough.** The loop then has a 115 Hz bandwidth and a 1.1 N/µm weak point at 34 Hz.
- **Above about 20 kHz the guides decide.** The QE15 blocks with ZA preload are then the limit, and
  the position of the upper carriage on its travel matters by a factor of two.
- **A worn tool can make any setup chatter.** The thrust grows with wear, and the limit falls with it.

## Forces at the defaults

| Force | Value | Against the MK21 (181 N continuous, 512 N for 1 s) |
| --- | ---: | --- |
| Cutting force, down | 223 N | Carried by the guide blocks |
| Thrust into the part, X motor | 316 N | 175 % of continuous |
| Feed force, Z motor | 108 N | 60 % of continuous |

Chip: 0.63 mm wide, 32 µm thick, all on the nose. Cutting power 0.56 kW.

## What to do next

1. **Measure the forces of a real hard turning cut** with this insert, or ask the insert maker for
   them. The Kienzle constants are for 1 mm chips, and the force ratio is an estimate. Both decide
   the motor size and the chatter limit.
2. **Tap test the tool tip** on the first stack. One measurement replaces the damping and stiffness
   estimates, and the page can take the measured values.
3. **Check if a drive can run the position loop at 20 kHz** (DRV-P3 asks for 8 kHz today).
4. **Price the QEH15CA blocks**, or a larger block size, for the lower stage first.
