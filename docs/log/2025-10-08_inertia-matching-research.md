# 2025-10-08 — Inertia matching research

**Role(s):** engineering

[<u>Joppe Verboven</u>](mailto:joppe.verboven2003@gmail.com)

- Research inertia-matching

  - 

|  |
|----|
| Moscrop, J., Cook, C., & Moll, P. (2001, November). Control of servo systems in the presence of motor-load inertia mismatch. In *IECON'01. 27th Annual Conference of the IEEE Industrial Electronics Society (Cat. No. 37243)* (Vol. 1, pp. 351-356). IEEE. |
|  |

- Inertia matching is not super important, reducing the flex in the motor-load coupling is more important

<!-- -->

- Research deceleration with the Odrive module

  - Odrive S1 has a built-in Brake resistor circuit (resistor value has to be calculated). Power can also be regenerated but reverse current is limited by the specs of the power supply.

- Research suitable motor for original ballscrew(10mm pitch)

  - Required torque = 0.16-0.64Nm (100-400N cutting force) (at 500rpm)

  - [<u>https://www.igus.be/product/MOT-EC-56-C-I-A</u>](https://www.igus.be/product/MOT-EC-56-C-I-A)

  - (0.6 Nm, encoder: 1000 puls/rev, 260euro)

  - [<u>https://teknic.com/hudson-model/M-2311P-QN-08D/?model_voltage=300</u>](https://teknic.com/hudson-model/M-2311P-QN-08D/?model_voltage=300)

  - (0.4 Nm, encoder: 8000 puls/rev, 325 dollar)

  - [<u>https://www.nanotec.com/eu/en/products/1811-db59-brushless-dc-motor</u>](https://www.nanotec.com/eu/en/products/1811-db59-brushless-dc-motor)

  - (0.2-.0.6 Nm, encoder:4000 puls/rev, 280 euro

<!-- -->

- <span class="mark">New ballscrew SFU1605 (pitch: 5mm)</span>

  - [<span class="mark"><u>https://vallder.com/nl/product-category/cnc-mechanical-components/ball-screws/</u></span>](https://vallder.com/nl/product-category/cnc-mechanical-components/ball-screws/)

  - <span class="mark">Is compatible with original hardware, only screw and nut are required (54euro)</span>
