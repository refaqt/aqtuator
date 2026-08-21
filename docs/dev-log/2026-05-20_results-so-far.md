# 2026-05-20 — Results so far

## Results so far

The results of the project so far are measurements of the FRFs of three configuration of the Mekanika Pro Upgraded machine:

- Stepper motors

- Rotary encoder feedback

- Linear encoder feedback

The measurements and results can be found here [<u>here (measurements and results)</u>](https://drive.google.com/drive/folders/14QnuRQOed2eDg-8ACwVJPWeeMFG2zp-p?usp=sharing) and [<u>here (comparison of FRFs)</u>](https://drive.google.com/open?id=1cvbGA7mEm5c1LC6KVc1z8i3lJ0X2izfw&usp=drive_fs).

The results were obtained using [<u>https://github.com/refaqt/cnc-frf-estimation</u>](https://github.com/refaqt/cnc-frf-estimation).

## Conclusions

From the results, we can conclude that there is **no significant difference between using a stepper motor or servo drive (with rotary encoder) on the stability of the machine**. Using **linear encoder feedback**, the accuracy is expected to be higher because errors from the ball screw and its bearings are eliminated. However, the **stability is slightly lower** due to the decreased bandwidth, caused by **non-collocated control**.

## Next actions

The developments will focus next on the **use of linear motors**, because they allow linear encoder feedback in combination with collocated control.
