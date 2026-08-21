# 2025-11-26 — ODrive analog input stuck at 4 V

- ODrive analog input constantly gives 4V

  - Discord discussion

    - [<u>Niels Bosmans</u>](mailto:niels@thinkler.be)

      - Hi, I wanted to control the torque using the analog input. I had set the the following parameters for that (used the GUI, but the python code makes it more clear):

      - odrv.config.gpio1_mode = GpioMode.ANALOG_IN

      - odrv.config.gpio1_analog_mapping.min = -0.1

      - odrv.config.gpio1_analog_mapping.max = 0.1

      - odrv.config.gpio1_analog_mapping.endpoint = odrv.axis0.controller.\_input_torque_property

      - 

      - Then I saw that the input torque was at a constant value of 0.1. I then checked the voltage over the analog input with a multimeter and measured 4V. I have this on both the GPIO1 and GPIO11. Is there something wrong with my analog input?

      - And that voltage is there if nothing is connected to it.

    - Solomon

      - [<u>https://docs.odriverobotics.com/v/latest/hardware/s1-datasheet.html#gpio-properties</u>](https://docs.odriverobotics.com/v/latest/hardware/s1-datasheet.html#gpio-properties)

        - G01, G02, G11: The HALL pins have a 2.7kΩ pullup to +5V and low pass filter (τ=4.25us), and cannot be used in DIGITAL_PULL_DOWN mode. When used as an output, the logic low level will be 500mV.

      - This also affects analog inputs

      - Usually I recommend having an op-amp as a buffer

      - But what are you trying to do?

    - [<u>Niels Bosmans</u>](mailto:niels@thinkler.be)

      - I'm generating a voltage in Arduino which I want to use as a reference for the torque in the ODrive S1. Should I configure it as an analog input somewhere? How does that work together with the pullup? I thought the above settings would be enough.

      - And an additional buffer seems overkill to me if the pins can be configured as analog ins

    - Solomon

      - Sorry, how are you generating that voltage? With analogWrite?

      - Or do you have an actual DAC?

      - What Arduino board?

    - [<u>Niels Bosmans</u>](mailto:niels@thinkler.be)

      - Arduino Giga R1. Using AdvancedAnalog DAC.

      - Anyway, if the GPIO1 or 11 are configured as analog in, isn't it strange I see 4V on both of them when there is nothing connected?

      - I mean, that could destroy my DAC as well, no?

    - Solomon

      - If your DAC is buffered (which it is on the Giga R1), it shouldn't have an issue.

      - But I'd generally recommend against analog anyways, especially because it's not isolated, which raises the risk for ground loops, especially in multi-odrive systems

      - Can you use R/C PWM (Arduino servo library) or even better, UART or CAN? [<u>https://docs.odriverobotics.com/v/latest/guides/arduino-uart-guide.html</u>](https://docs.odriverobotics.com/v/latest/guides/arduino-uart-guide.html)

    - [<u>Niels Bosmans</u>](mailto:niels@thinkler.be)

      - PWM is too slow, I want to send signals up to 500Hz and I will run a 5000Hz control loop on the Arduino. Is UART fast enough for that? But in the meantime how can I get the analog input to work?

      - By the way, we were using an Arduino Opta before, which could have put more than 3.3V on the ODrove analog in. I always checked the voltage, but at some point I also noticed discrepancies in the scaling of the Opta's output. Could I have damaged the analog input of the Odrive?

    - Solomon

      - Hmm, yeah there's a possibility.

      - UART is fast enough yeah, if you're just sending torque setpoints. c 0 xyz.abc\r\n is 13 bytes, with 921.6kbaud then that's no problem

      - Just bc also analog is so noisy and prone to ground loops, I'd recommend immediately switching to UART if possible.

      - But you can test the S1 analog inputs, maybe ground the analog input and see if it registers the ~0v?

      - I'd be interested in a quick characterization/LUT between the Arduino DAC output and S1 read analog reading, you can likely do a static scaling/correction factor for the pullup resistor impedance.

- UART should be capable of the speed, although it is not recommended for industrial applications.

- Test 0V connected to analog input of Odrive:

  - 3.3V still measured, which indicates the analog input is broken.

- UART cannot handle more than 115200 baud rate.

  - Troubleshooting: [<u>https://claude.ai/share/7d1066a1-fb01-4e6f-b8a2-a9a62ed059d3</u>](https://claude.ai/share/7d1066a1-fb01-4e6f-b8a2-a9a62ed059d3)

  - Try if baud rate is possible with testing code.

  - If not: switch to CAN?

    - Cannot control more than 2 motors

  - So: UART or Analog or switch to EtherCAT

- Strategy:

  - Try UART

  - If not 5kHz possible: order new ODrive
