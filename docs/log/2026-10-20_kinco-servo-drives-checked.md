# 2026-10-20 — Kinco servo drives checked against the drive requirements

**Role(s):** engineering, purchasing

## Goal

Check every servo drive on the Kinco website against the drive requirements for the MAXWELL MK21
linear motor stage (DRV-01 to DRV-10). Find out if one Kinco drive meets all of them.

## Work Done

### Short answer

- **No Kinco drive meets all hard requirements.** No drive on the website reads a 1 Vpp stage
  encoder (DRV-08) and also has EtherCAT (DRV-07). No Kinco document says that the drives run a
  third-party linear motor without Hall sensors (DRV-05).
- **The closest drive is the new FD6P.** It has EtherCAT with the CiA 402 profile, 230 VAC, a
  position loop of 8 kHz, and 2.9 A rms continuous and 10.61 A rms peak (model L2R9). It reads only
  Kinco's own serial ("communication type") motor encoder, so it fails DRV-08.
- **Only the JD series has a sine and cosine input.** It reads Hiperface encoders and has a motor
  temperature (PTC) input. It has no EtherCAT, so it fails DRV-07.
- Kinco stays out of the candidate list. The candidates do not change.

### Each Kinco series

Pass and Fail come from the Kinco website or a Kinco manual. NC means not confirmed.

| Series | Supply (DRV-04) | Current (DRV-01, 02) | EtherCAT CiA 402 (DRV-07) | Stage encoder (DRV-08) | Position loop (DRV-09) | Result |
| --- | --- | --- | --- | --- | --- | --- |
| FD6P (EA version) | 1 phase 200 to 240 VAC. Pass | L2R9: 2.9 / 10.61 A. Pass | Yes. Pass | Kinco serial encoder only. **Fail** | 8 kHz (website). Pass | Fails DRV-08. Linear motor, thermal input and Bode tool (DRV-05, 06, 10) are not stated |
| FD5P PRO (E version) | 200 to 240 VAC. Pass | L2R9: 2.9 / 10.61 A. Pass | Yes. Pass | Kinco serial encoder. A second encoder only as A/B pulses on the pulse input, up to 4 MHz. **Fail** | 8 kHz on the website, 4 kHz in the 2023 manual. Pass either way | Fails DRV-08. No linear motor in the manual |
| FD2S (FD412S, FD422S, FD432S, E version) | 220 VAC. Pass | FD412S: 2 / 7 A. Pass | Yes. Pass | 2500 lines per turn incremental, or resolver. **Fail** | NP. NC | Fails DRV-08 |
| CD2S | 220 VAC. Pass | 2 / 7 A. Pass | No fieldbus. **Fail** | 2500 lines per turn incremental, or resolver. **Fail** | 1 kHz. **Fail** | Fails three hard requirements |
| JD | 220 VAC (JD430). Pass | JD430: 10 / 27.5 A. Pass, but much larger than the motor | RS232, RS485 and CANopen only. **Fail** | Hiperface sine and cosine. A plain 1 Vpp scale is NC | NP. NC | Fails DRV-07. The "AA" version is sold for direct drive motors |
| FD3 and CD3 (older) | 220 VAC. Pass | Not checked | Yes on the FD3 | BiSS, Nikon and Tamagawa serial encoders. **Fail** | 1 kHz. **Fail** | Fails DRV-08 and DRV-09 |
| DC drives (FD1X4S, FD1X5, FD1X5S, FD2X5, OD1X4S, OD1X5S) | Low voltage DC. **Fail** | Not checked | Some versions | Not checked | Not checked | Fails DRV-04 |

## Decisions

- Kinco is not a candidate. No new decision record is needed, because the candidate list does not
  change.

## Open Questions

- The FD5P PRO website gives an 8 kHz position loop, but the FD5P manual from 2023 gives 4 kHz.
  This does not matter here, because the drive fails DRV-08 either way.
- Kinco's company page says its drives "can drive all kinds of servo motors, including linear
  motors". No Kinco manual we found shows how. Ask Kinco only if the FD6P ever gets a 1 Vpp input.

## Next Steps

1. No action on Kinco.
2. Keep waiting for the Kollmorgen and Copley prices.

<details>
<summary>Sources</summary>

- Kinco website, product list: <https://www.kincoautomation.com>
- FD6P product page: <https://www.kincoautomation.com/product/automation/fd6p>
- FD5P PRO product page: <https://www.kincoautomation.com/product/automation/fd5p>
- FD2S product page: <https://www.kincoautomation.com/product/automation/fd2s>
- CD2S product page: <https://www.kincoautomation.com/product/automation/cd2s>
- JD product page: <https://www.kincoautomation.com/product/automation/jd>
- FD5P manual (2023), 4 kHz position loop p. 10 to 11, full closed loop section 6.6: <https://aiq-robotics.com/wp-content/uploads/2024/01/Kinco-FD5P-series-AC-servo-system-manual-EN-23125.pdf>
- JD, FD2S and CD2S catalogue, JD encoder pins with Hiperface and PTC: <https://aiq-robotics.com/wp-content/uploads/2023/12/KincoCatalog_JDFD2SCD2S_Servo_K1E05_20231102-2.pdf>
- CD3 and FD3 catalogue, 1 kHz position loop, BiSS, Nikon and Tamagawa: <https://sigbi.se/wp-content/uploads/KincoCatalog_CD3FD3_K1C15_190719.pdf>

</details>
