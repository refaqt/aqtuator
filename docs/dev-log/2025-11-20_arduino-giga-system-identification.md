# 2025-11-20 — Arduino Giga system identification

- Programming Arduino Giga for system identification.

- Asked Claude to write a report about using the Giga for control: [<u>https://claude.ai/public/artifacts/4fe0093d-8a4c-4bfb-8c8f-240e3b15534b</u>](https://claude.ai/public/artifacts/4fe0093d-8a4c-4bfb-8c8f-240e3b15534b)

- Key takeaways:

  - Millis() and micros() are not hardware-timed, so shouldn’t be used.

  - Use AdvancedADC library

- Voltage tolerance of 3.3V inputs: [<u>https://claude.ai/share/c973b0a2-39fc-4bfd-8ef9-02f79dcc5dc7</u>](https://claude.ai/share/c973b0a2-39fc-4bfd-8ef9-02f79dcc5dc7)

  - 3.6V is acceptable, so 2.5V inputs with 200mV/g and 5g is 3.5V so this is ok
