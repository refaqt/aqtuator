# 2026-09-23 — The motor field at the encoder, and whether a steel plate can shield it

**Role(s):** engineering, simulation

## What happened

The X axis gets a magnetic linear encoder. Its read head sits about 30 mm beside the MK21
linear motor. The question was how strong the motor's field is at the head, and whether a
2 to 3 mm steel plate between the magnet track and the guide block can lower it.

The limit was first given as 25 mT, then corrected to 1 mT.

**Without a shield**, the field at the head is about 2.4 to 2.9 mT over most of the
stroke. Near the ends of the magnet track it rises to about 7.5 to 8.4 mT. That meets
25 mT easily. It does not meet 1 mT.

The field comes from the magnet track, not from the mover. The magnets alternate every
30 mm, so neighbouring poles cancel and the field falls quickly with distance. At the
track ends there is no opposite neighbour, so the field falls more slowly there.

**With a shield**, the field drops about 2.5 times. The plate must be a magnetic steel. A
403 or 430 stainless works; 304 and 316 do not work because they are not magnetic. Plain
low carbon steel works a little better.

| Shield | Middle of stroke | Near a track end |
| --- | ---: | ---: |
| None | 2.4 to 2.9 mT | 7.5 to 8.4 mT |
| One plate, 403/430 stainless, 3 mm | 1.1 to 1.2 mT | 2.9 to 3.2 mT |
| One plate, low carbon steel, 3 mm | 1.0 to 1.1 mT | 2.6 to 2.9 mT |
| Same plate, 35 mm tall | 0.8 to 1.0 mT | 1.7 to 2.3 mT |
| Two 2 mm low carbon plates, 4 mm air gap | 0.7 to 0.8 mT | 1.8 to 1.9 mT |

These are model results with a worst-case guess for the magnet sizes. The real values can
be about 50 % higher or lower. The full table, the model and its limits are in
[the results summary](../../simulation/results/encoder-stray-field/summary.md) and
[the case notes](../../simulation/cases/encoder-stray-field/README.md).

## Decisions

No design decision yet. The model says what is possible. A measurement has to confirm it
before any part is ordered.

## Open Questions

- The real magnet sizes of the MK2 track. The STEP files in the parts library are not
  downloaded yet.
- Whether the 1 mT limit is a hard limit in the encoder datasheet, and for which field
  direction.
- How much the guide block and the rail pull extra field toward the head. They are not in
  the model.

## Next Steps

1. Measure with a gaussmeter at the head position: in the middle of the track and near
   both ends, with the motor off and at peak current. Measure again with a strip of low
   carbon steel beside the track.
2. If the middle reads well below 1 mT with the strip, plan a two-plate shield with a 3 mm
   inner plate. Make the plate reach above the magnets.
3. Make the magnet track longer than the stroke needs, so the head stays at least 60 mm
   from each track end. For example, MK2-300 + MK2-180 in place of two MK2-180.
4. If that is still not enough, move the head further out (each 10 mm roughly halves the
   field), add a small steel cover around the head, or compare an optical encoder.
5. Fit the scale and the shield before the magnet track. The bare track has about 300 to
   400 mT at its surface and can erase a magnetic scale. The shield plate is pulled toward
   the magnets, so screw it down firmly.
