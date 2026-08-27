# 2025-11-14 — Opta analog bandwidth limit

**Role(s):** engineering

- Arduino Opta cannot output analog voltage at more than 20 Hz

- Requirements for alternatives:

<!-- -->

- 5KHz

- 8 in, 4 out

- screw terminals

- 0-5V at least, +/-10V desired.

- Sufficient onboard memory to temporarily store data \> 262kB

<!-- -->

- Alternatives:

  - Arduino Giga R1 Wifi + PWM to analog circuits

    - https://store.arduino.cc/products/giga-r1-wifi?queryID=undefined

    - [<u>https://www.amazon.com/Terminal-Adapter-Arduino-Breakout-Standard/dp/B0DJGPCCNM</u>](https://www.amazon.com/Terminal-Adapter-Arduino-Breakout-Standard/dp/B0DJGPCCNM)

    - PWM to analog:

      - [<u>https://eletechsup.com/products/arduiuo-dac-expansion-module-diy-kit-pwm-to-0-5v-0-10v-voltage-converter-for-nano-pro-mega-esp8266-esp32#:~:text=Working%20voltage%3A%20DC%2012V,2ms</u>](https://eletechsup.com/products/arduiuo-dac-expansion-module-diy-kit-pwm-to-0-5v-0-10v-voltage-converter-for-nano-pro-mega-esp8266-esp32#:~:text=Working%20voltage%3A%20DC%2012V,2ms)

      - [<u>https://eletechsup.com/products/0-5v-0-10v-frequency-to-voltage-module-pwm-to-dac-converter-plc-mcu-fpga-analog-io-expansion-board-signal-generator#:~:text=Working%20voltage%3A%2010V,2ms</u>](https://eletechsup.com/products/0-5v-0-10v-frequency-to-voltage-module-pwm-to-dac-converter-plc-mcu-fpga-analog-io-expansion-board-signal-generator#:~:text=Working%20voltage%3A%2010V,2ms)

  - Arduino Giga R1 Wifi + CAN bus shield (and CAN to Odrive)

    - [<u>https://store.arduino.cc/products/can-bus-shield-v2?srsltid=AfmBOooGt218BtZqY2SfYpNxlM4lxUCnngq2fqetc3kg07-EcjgU_IfT</u>](https://store.arduino.cc/products/can-bus-shield-v2?srsltid=AfmBOooGt218BtZqY2SfYpNxlM4lxUCnngq2fqetc3kg07-EcjgU_IfT)

- Shields

  - Terminal blocks

    - [<u>https://www.kiwi-electronics.com/nl/arduino-boards-shields-en-accessoires-147/terminal-hat-voor-arduino-mega2560-11278</u>](https://www.kiwi-electronics.com/nl/arduino-boards-shields-en-accessoires-147/terminal-hat-voor-arduino-mega2560-11278)

    - [<u>https://www.digikey.be/nl/products/detail/dfrobot/DFR0921/16678687</u>](https://www.digikey.be/nl/products/detail/dfrobot/DFR0921/16678687)

    - [<u>https://nl.grandado.com/products/din-rail-mount-schroef-terminal-block-adapter-module-voor-mega-2560-r3-1?variant=UHJvZHVjdFZhcmlhbnQ6NzM4NDQzMzM1&msclkid=6c4013239e461080e7727a34daa7769e&utm_source=bing&utm_medium=cpc&utm_campaign=NLD%20%7C%20Shopping%20%7C%20All%20products%20-%20From%20our%20catalogue&utm_term=4576236131381665&utm_content=All%20Items</u>](https://nl.grandado.com/products/din-rail-mount-schroef-terminal-block-adapter-module-voor-mega-2560-r3-1?variant=UHJvZHVjdFZhcmlhbnQ6NzM4NDQzMzM1&msclkid=6c4013239e461080e7727a34daa7769e&utm_source=bing&utm_medium=cpc&utm_campaign=NLD%20%7C%20Shopping%20%7C%20All%20products%20-%20From%20our%20catalogue&utm_term=4576236131381665&utm_content=All%20Items)

    - [<u>https://www.digikey.be/nl/products/detail/dfrobot/DFR0191-R/18069248</u>](https://www.digikey.be/nl/products/detail/dfrobot/DFR0191-R/18069248)
