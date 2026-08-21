# 2026-01-07 — Multisine upload CAN torque

- Implemented multisine csv upload on Controllino and CAN torque commands.

- Issue with Controllino:

  - Controllino Micro only has 4 AI’s that can be sampled up to 66kHz. The others can only be sampled at 1.15 kHz.

  - Try to implement the analog reads at 8kHz and see if the methods are blocking or not.

- Analog inputs example:

  - [<u>https://github.com/CONTROLLINO-PLC/controllino_rp2/blob/master/examples/arduino/micro/IoTest/IoTest.ino</u>](https://github.com/CONTROLLINO-PLC/controllino_rp2/blob/master/examples/arduino/micro/IoTest/IoTest.ino)

  - 
