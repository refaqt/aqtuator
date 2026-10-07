# 2026-10-07 — How to mount the encoder scale tape in the pocket of the base

**Role(s):** engineering, hardware

## Goal

The steel scale tape of the linear encoder sticks to the side wall of the pocket in the base of
the compact stage. It is laid with an applicator: a dummy reading head that rides with the
carriage and presses the tape down. Two problems came up:

- The applicator is bolted to the carriage, between two guide blocks. At the end of the travel,
  part of the tape is still not laid, and the applicator cannot come out while the tape is still
  in it.
- There is almost no room between the guide blocks and the wall for a finger. The maker says to
  press the tape down with a finger in a clean, lint-free cloth.

We looked for a way to lay the whole tape, and for other ways to press it down.

## Work Done

- **The maker expects a short end of tape to stay unlaid.** We read the Renishaw installation
  guide for the TONiC reading head with the RTLC20-S tape. Step 10 says: "Remove the applicator
  and, if necessary, adhere the remaining scale manually." So the trapped applicator is a problem
  of how we mount the applicator, not of the tape.
- **The tape is only a little longer than the travel.** The measuring length is the tape length
  minus 17 mm. That leaves about 8.5 mm at each end. The part that is still unlaid is about half
  the length of the applicator.
- **What the maker asks for, in order:**
  1. Let the tape reach room temperature. Clean and degrease the wall.
  2. Bolt the applicator to the reading head bracket. Set its height with the green shim that
     comes with the reading head.
  3. Press the start of the tape down firmly, through a clean, dry, lint-free cloth.
  4. Move the applicator slowly and smoothly through the whole travel. Pull the backing paper
     off by hand, so it does not catch under the applicator.
  5. Press the whole tape down firmly again after the pass.
  6. Wait 24 hours, then fit the datum clamp. The datum clamp fixes the tape to the base at one
     point. The guide warns that the accuracy suffers without it.
- **The finger is not required.** The cloth keeps the tape clean and free of scratches. Any clean
  tool that gives the same pressure and does not scratch the tape does the same job. Five ways
  that fit a narrow gap:
  1. Run the applicator back and forth two or three times. Its own pad presses the tape down.
  2. Bolt a small pressing block with a felt or silicone pad and a light spring in the place of
     the applicator, and run it along the tape.
  3. Use a narrow roller: a small bearing with a soft tyre, 5 to 6 mm wide, on an L-shaped
     handle.
  4. Use a plastic or wooden rod with a rounded end, wrapped in the lint-free cloth.
  5. Push a strip of soft foam into the gap with a steel rule. Keep it away from the seals of
     the guide blocks.
- **Three ways to lay the whole tape, best first:**
  1. **A dummy carriage with the applicator hanging out at the front.** A plate bolts onto the
     guide blocks of the rail next to the tape. The applicator is bolted to this plate so it sits
     outside the blocks, in front of them in the direction of laying. The applicator then reaches
     the end of the tape before the blocks reach the end of the rail. It lifts off easily,
     because nothing sits beside it. The real carriage goes on afterwards. This is the idea the
     user proposed, with one change: the overhang.
  2. **An applicator that rides on the rail, before the guide blocks go on.** A small saddle
     sits on the top face of the rail and carries the applicator at the right height. It runs
     the full length of the rail. The order is: fit the rails, lay the tape, slide the blocks on
     from the end of the rail, then fit the carriage.
  3. **Tape on a separate bar.** Lay the tape on a ground steel or aluminium bar on the bench,
     then bolt the bar to the pocket wall. This removes every space problem. It costs one more
     part, a wider pocket, and care with the straightness of the bar. This is the fallback.
- **Two points for the design of the base.**
  - The pocket wall under the tape is the mounting face of the tape. Mill it in the same set-up
    as the rail floor and the alignment tabs, so it is parallel to the reference rail. The
    Renishaw drawing asks for Ra 3.2 and shows a parallelism of 0.05 mm to the axis of motion.
    Check that number on page 14 of the guide before it goes on a drawing.
  - Keep the tape clear of the 3 mm alignment tabs of the rails, above them or between them.

## Decisions Made

No decision yet. The dummy carriage with an overhanging applicator is the preferred method. The
rail-riding applicator is the second choice.

## Open Questions

- Which guide blocks does the stage use, and how wide is the gap between a block and the pocket
  wall? The block type is not in the repository yet.
- Does Renishaw accept an applicator that overhangs a dummy carriage, or that rides on the rail?
- What exact flatness and parallelism does the mounting face of the tape need?

## Next Steps

1. Ask the Renishaw application engineer the two questions above about the applicator and the
   mounting face.
2. Model the tape mounting face in the pocket wall of the base, in the same set-up as the rail
   floor.
3. Design the dummy carriage plate with the overhanging applicator, once the guide blocks are in
   the architecture.

<details>
<summary>Technical notes and sources</summary>

- Mistake rules applied:
  [loop rate from a trade article](../mistakes/2026-09-29_loop-rate-from-a-trade-article.md) and
  [fatigue estimate without a data sheet](../mistakes/2026-09-22_fatigue-estimate-without-a-datasheet.md).
  Every number here was read in the Renishaw documents below, not in a secondary source.
- Installation guide M-9589-9013-04-A, pages 14 to 18. Scale drawing: overall length L + 37,
  measuring length L − 17 (L − 32 with two limits), ride height 0.8 mm, Ra 3.2, 0.05 to axis F,
  0.2/100. Equipment: side mount applicator A-9589-0115 or top mount applicator A-9589-0094,
  datum clamp A-9585-0028, Loctite 435 P-AD03-0012, end cover kit A-9585-0035, green shim,
  lint-free cloth. Application steps 1 to 14 on page 17.
- The finger-pressure text in the guide: step 7 "Apply firm finger pressure via a clean, dry,
  lint-free cloth to ensure the scale end adheres", step 9 "light finger pressure", step 11 "firm
  finger pressure ... along the length of the scale after application".
- Base geometry from
  [the rail mounting log](2026-10-02_rail-mounting-holes-in-the-base.md): base 440 mm, rail
  floor 420 mm, HIWIN HGR15R rail 418 mm, tabs 3 mm high and 20 mm long at x = 30 to 50 and
  x = 390 to 410.
- The pressing tools, the overhang and the rail-riding saddle are engineering judgement. They are
  not in the Renishaw guide.
- Sources:
  - [TONiC T1x3x RTLC20-S installation guide, M-9589-9013-04-A (PDF)](https://www.renishaw.com/media/pdf/en/4964d870374346d8994ea57e3bf6ebf7.pdf)
  - [RTLC incremental linear scale data sheet, L-9517-9417-07-A (PDF)](https://www.renishaw.com/media/pdf/en/faaf7389f06b4e39baf4c2673cee55d9.pdf)

</details>
