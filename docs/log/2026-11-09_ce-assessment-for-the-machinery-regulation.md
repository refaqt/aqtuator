# 2026-11-09 — CE assessment updated for the Machinery Regulation

**Role(s):** engineering, safety

## Goal

Niels answered the first CE assessment of 2026-11-06. He asked four things: whether payload and
speed are only a text for the customer, whether no limit signal is a safety problem, that the
analysis follows the rules after 20 January 2027, and when Safe Torque Off must work and how to
make it compliant.

## Short answer

- The assessment now follows the Machinery Regulation (EU) 2023/1230.
- Payload and top speed are design limits. A new stage requirement, STG-15, says the end stops
  must stop the worst case. The largest payload has no number yet.
- The limit switches are removed from the parts list. This is acceptable for safety, because they
  never protected people. The reasons are in the assessment.
- New section: when Safe Torque Off must work, and the six steps to make the stop circuit
  compliant.
- New danger H13: water from the new forcer cooling near parts at about 325 V.
- Full text: [the CE assessment](../compact-stage-ce-assessment.md). Decision:
  [partly completed machinery, without limit switches](../decisions/2026-11-09_compact-stage-is-partly-completed-machinery.md).

## Next Steps

1. Niels sets the largest payload and the top speed.
2. Measure the stopping distance after STO and after a braked stop, once the drive is chosen.
3. A specialist checks the annex numbers in the full text of the Regulation.

<details>
<summary>Technical notes</summary>

- `compact-stage.sysml`: STG-15 `EndStopEnergy`, attributes `movingMass`, `maxPayload`,
  `motorPushEnergy`, `endStopEnergy`, without numbers.
- `motor-drive.sysml`: DRV-13 text only.
- `bom.csv`: `SW-001` and `ELC-001` removed after a search of the whole repository (mistake rule
  of 2026-11-04). `bash doqs.sh generate` and `bash doqs.sh check` pass.
- The full EUR-Lex text could not be downloaded here. Annex numbers come from the EUR-Lex summary
  and published Declarations of Incorporation.
- `origin/main` (forcer water cooling) was merged into the branch first.

</details>
