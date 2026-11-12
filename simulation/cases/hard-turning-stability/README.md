# hard-turning-stability

A web page that answers one question: can we turn hardened steel (61 to 63 HRC) with the tool on a
cross slide made of two stacked compact stages? It works out the stiffness at the tool tip and draws
the stability lobes: the depth of cut where chatter starts, against the spindle speed. The lathe bed
and the spindle count as rigid.

It is derived from the [cutting force page](../cutting-force-rejection/). It reuses that page's
linear motor loop, its exact compliance at the samples and its lobe function, and adds the second
stage, the guide blocks, the tool shank, three force directions and the turning forces.

**Open it:** <https://refaqt.github.io/aqtuator/hard-turning/> (after the next Pages run on `main`).
To run it from a local clone, open `index.html` in the browser. No server is needed.

**Tool:** plain HTML and JavaScript. The checks need Node 18 or newer, no packages.

```bash
node simulation/cases/hard-turning-stability/check_model.mjs
```

Log: [2026-11-11](../../../docs/log/2026-11-11_hard-turning-stability.md). Results:
[summary](../../results/hard-turning-stability/summary.md).

## The machine

- **Lower stage:** a compact stage on the lathe bed. It moves along the spindle axis (Z).
- **Upper stage:** a second compact stage on the lower carriage, turned by 90°. It moves the tool
  into the part (X).
- **Tool holder:** on the upper carriage. The tool tip points at the part along +X.
- Each stage: MAXWELL MK21 linear motor, four HIWIN QEH15SA blocks with medium preload (ZA) on two
  EGR15U rails, 200 mm travel.

Axes on the page: X into the part, Y up, Z along the spindle. The cutting force pushes the tool
down (−Y). The feed runs along −Z.

## Inputs

| Input | Default | Source |
| --- | --- | --- |
| Depth of cut | 0.2 mm | Finish hard turning, chosen with the user |
| Feed | 0.1 mm/turn | Same |
| Cutting speed | 150 m/min | Same. On 50 mm this is 955 rev/min |
| Part diameter | 50 mm | Same |
| Nose radius | 0.8 mm | Same, CBN insert |
| Entering angle | 95° | CNMG or DNMG style holder |
| k<sub>c1</sub>, m<sub>c</sub> | 4700 N/mm², 0.25 | [ISCAR material table](https://www.iscar.com/eCatalog/Ecat/datafileENM/INFO/5092.pdf), hardened steel 60 HRC ("specific cutting force for 1 mm² chip section"). The 55 HRC row is 4600 and 0.25. No row for 62 HRC |
| F<sub>t</sub>/F<sub>c</sub> | 1.5 | An estimate. A search summary of [Grzesik et al.](https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-5e593c41-e62b-41de-972f-3f85802ce301/c/5_Grzesik_et_al._Energy-Based_54-62.pdf) gives 1.10 at 0.4 mm nose radius and 1.45 to 1.55 at 0.8 mm, for chamfered CBN in hardened 41Cr4 (55 HRC). Not confirmed: the paper could not be opened. Worn tools give more. Range 1.1 to 2.5 |
| Loop rate | 10 kHz | As on the cutting force page. DRV-09 asks for at least 4 kHz |
| Moving mass of one stage | 4.24 kg | Carriage halves, forcer, blocks, read head, small parts: the end stop crash case of the compact stage |
| Fixed mass of one stage | 6.71 kg | Base, rails, stators, strip: same source |
| Tool holder | 1.5 kg | An estimate |
| Block stiffness | 115 N/µm | HIWIN catalogue GW-13-1-EN-2606-K, Table 3.44, QE15S with ZA preload (radial) |
| Sideways over radial | 1.0 | Not in the catalogue. The blocks have a 45° contact angle and are sold as "highly resilient in all loading directions". An estimate, range 0.5 to 1 |
| Block positions | 124.2 mm along, 138 mm across, 18 mm up | Compact stage CAD, as in the end stop crash case |
| Damping ratio of the guides | 0.03 | An estimate, range 0.02 to 0.05 |
| Tool tip | 25 mm above the upper carriage, 130 mm ahead of its centre | An estimate of the holder |
| Shank | 20 × 20 mm, 25 mm overhang, damping ratio 0.03 | Shank size common for this work. Damping is an estimate |

## What the model does

- **Two parts in series.** The tip compliance is the motor loops plus the structure:
  - **Motor loops.** The linear motor case of the cutting force page, one rigid mass each, with the
    same robust tuning (sensitivity peak at most 6 dB, phase margin at least 30°, gain margin at
    least 6 dB). The X motor moves the upper carriage and the holder (5.74 kg). The Z motor moves
    everything on the lower blocks (16.69 kg). Its exact compliance at the samples is used up to
    0.98 of half the loop rate. Above that, the bare mass, −1/(m ω²).
  - **Structure.** Two rigid bodies with 6 degrees of freedom each, and a tip mass. Body 1 is the
    lower carriage with the base of the upper stage. Body 2 is the upper carriage with the holder.
    Each block is a spring up/down and a spring sideways. Along its travel each body is held by a
    very stiff spring at the forcer, because the motor loop already holds that part. The shank is a
    cantilever (3EI/L³ in Y and Z, EA/L along X) with a quarter of its free mass plus the insert at
    the tip. Damping is a loss of 2ζ on each spring.
- **Turning forces.** Kienzle, F<sub>c</sub> = k<sub>c1</sub> · b · h<sup>1 − m<sub>c</sub></sup>.
  The chip width b is the engaged edge: on the nose, r<sub>ε</sub>(θ₁ + θ₂) with
  θ₁ = acos(1 − a<sub>p</sub>/r<sub>ε</sub>) and θ₂ = asin(f/2r<sub>ε</sub>), plus the straight edge
  when the depth goes past the nose. The chip thickness is h = a<sub>p</sub> · f / b. The thrust
  acts at right angles to the chord between the two ends of the engaged edge (Colwell).
- **Chatter.** 1 + b · K<sub>t</sub> · (1 − e<sup>−jωT</sup>) · Φ = 0, with T one spindle turn,
  K<sub>t</sub> = (1 − m<sub>c</sub>) · k<sub>c1</sub> · h<sup>−m<sub>c</sub></sup> (the slope of
  Kienzle), and Φ = u<sub>h</sub>ᵀ · G · w. u<sub>h</sub> is the direction in which the chip gets
  thicker; w is the force per newton of F<sub>c</sub>. G is the full 3 × 3 tip compliance, so the
  tilt that turns a downward force into an X motion counts. So b<sub>lim</sub> = −1/(2 · K<sub>t</sub> ·
  Re Φ). The lobes come from `lobes()` of the cutting force page with one tooth. The chip width is
  turned back into a depth of cut through the edge shape. The force direction and the chip
  thickness are taken at the chosen cut.
- **The limit at the chosen speed** is the lowest lobe that passes that speed, found directly from
  the phase of Φ. At 955 rev/min the lobes lie about 16 Hz apart, so this is almost the floor.
- **Which part sets the limit.** The page also gives the floor with the motor loops alone and with
  the structure alone.

`check_model.mjs` checks that both loops meet the robustness rules; that a very stiff structure
gives back the motor loop of the cutting force page; that the static structure equals the two
block sets and the shank worked out one by one, and is symmetric; that the shank alone peaks at
√(k/m) with height 1/(2ζk); the low and high frequency limits; that the step at the end of the
sampled range is negligible; that chip width and edge normal are continuous where the nose meets
the straight edge, and the forces match a hand calculation; that the limit at the chosen speed
solves the chatter equation and agrees with the lobe envelope; that the lobes never go below the
floor; and that one direction alone gives the floor of the cutting force page.

## What it shows

See the [results summary](../../results/hard-turning-stability/summary.md). In short, at the
defaults:

- **The tip is about 82, 43 and 29 N/µm stiff (X, Y, Z) for a steady force,** set by the guide
  blocks and the tilt of the carriages. The motors hold a steady force with no error.
- **The weakest point is 2.3 N/µm, at about 450 Hz,** where the whole stack rocks on the lower blocks.
- **The finish cut (0.2 mm, 0.1 mm/turn, 150 m/min) is just stable.** Chatter starts at
  0.22 mm. That margin is too small for a model with estimated damping and force ratio.
- **The thrust is 316 N, 1.7 times the continuous force of the MK21.** The X motor cannot hold it
  for long. The Kienzle force at 30 µm chip thickness is uncertain; measure it.

## Limits

- The motor loops and the structure add in series. The loop does not see the guide modes, and the
  guide modes do not see the loop. Both are weak near 400 to 500 Hz, so the real answer may differ.
- Inertia of the carriages from boxes of about their size.
- No process damping. In hard turning at low speed it helps, so the page is on the safe side.
- Kienzle far below its 1 mm reference chip thickness.
- The shank clamp, the holder screws and the stage screws are rigid. A tap test at the tool tip
  would replace all the estimates at once.
- The damping ratios and F<sub>t</sub>/F<sub>c</sub> are estimates, and they decide the answer.
