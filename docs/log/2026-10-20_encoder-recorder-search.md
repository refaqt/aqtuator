# 2026-10-20 — Systems that record three encoders at the same time

**Role(s):** engineering, purchasing

## Goal

Find a system that reads at least three position encoders at the same time and records each
position against time. The encoders send 1 Vpp sine and cosine, or an absolute position over
EnDat 2.2 or BiSS-C. The record must be exported to a file on a PC. A data logger, a PLC or an
industrial PC are all fine.

## Work Done

We searched three groups: encoder interface boxes from encoder makers, data loggers from test and
measurement makers, and PLCs and motion controllers. All candidates are in
[`encoder-recorder-selection.md`](../encoder-recorder-selection.md).

- No single product reads 1 Vpp, EnDat 2.2 and BiSS-C, records them and exports a file with no
  programming. The ADDI-DATA APCIe-1711 card reads all three, but its rate and shared trigger are
  not confirmed, and it has drivers only.
- **Beckhoff EtherCAT terminals** cover every signal type in one row, with a shared clock and CSV
  export from TwinCAT Scope View. The rate is about 10 kHz.
- **HEIDENHAIN EIB 741 / EIB 742** reads four 1 Vpp or EnDat encoders on one trigger, up to
  50 kHz. It has no BiSS-C and no ready CSV export.
- **S.E.A. 9510 / 9521 in an NI CompactRIO** reads three EnDat 2.2 or three BiSS-C encoders at the
  same time, at about 20 kHz. You must write the LabVIEW program yourself.
- **imc HRENC-4** is a ready data logger for four 1 Vpp encoders, up to 50 kHz.
- Most data loggers (Dewesoft, HBK, NI) only count digital pulses. They do not read 1 Vpp,
  EnDat or BiSS-C directly.

## Decisions Made

- Israeli suppliers and the ODrive are left out.
- Reseller and shop prices are shown as such. No maker in the list publishes a list price,
  except the S.E.A. web shop.

## Open Questions

- Which encoder signal will the test use? This decides between the HEIDENHAIN EIB and the
  Beckhoff set.
- What record rate is needed? It depends on the fastest motion we want to see.
- HEIDENHAIN blocked the download of its newer EIB 700 product sheet. The numbers come from the
  2013 sheet and the user manual. Check them in the current sheet.
- The shortest cycle of the EL5032 and of the EL5042 with two channels is not confirmed.

## Next Steps

- Ask HEIDENHAIN for a quote and the current data sheet of the EIB 741.
- Ask a Beckhoff office for a quote for the terminals that match the chosen encoders, plus an
  EtherCAT coupler and a TwinCAT licence.
