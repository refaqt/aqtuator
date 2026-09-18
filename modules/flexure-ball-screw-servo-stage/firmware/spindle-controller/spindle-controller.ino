/*
 * Controllino MICRO (RP2040) — 8 kHz spindle controller (standalone)
 *
 * - Reads analog inputs A0, A1, A3 (A2 unused) and computes x_spindle.
 * - Runs x_spindle through: lead-lag -> 2nd order low-pass -> notch1 -> notch2.
 * - Converts controller output torque to PWM on GPIO0 (Arduino D0), using the same
 *   ODrive GPIO1 analog mapping and pull-up compensation as main-controllino.ino.
 * - Control loop runs at 8 kHz.
 * - Control is enabled when GPIO1 (Arduino D1) reads HIGH, otherwise PWM is set to 0.
 */

// NOTE: This struct is placed before includes because the Arduino build system may
// auto-generate function prototypes that reference `Biquad` before its first definition.
struct Biquad {
  // Direct Form 1:
  // y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
  float b0 = 1.0f, b1 = 0.0f, b2 = 0.0f;
  float a1 = 0.0f, a2 = 0.0f;
  float x1 = 0.0f, x2 = 0.0f;
  float y1 = 0.0f, y2 = 0.0f;

  void reset() {
    x1 = x2 = 0.0f;
    y1 = y2 = 0.0f;
  }

  float step(float x) {
    const float y = (b0 * x) + (b1 * x1) + (b2 * x2) - (a1 * y1) - (a2 * y2);
    x2 = x1;
    x1 = x;
    y2 = y1;
    y1 = y;
    return y;
  }
};
 
#ifdef ARDUINO_ARCH_RP2040
  #include <hardware/timer.h>
  #include <hardware/adc.h>
#endif
 
#include <math.h>
 
// ============================================================================
// Pin configuration (Controllino MICRO header labels)
// ============================================================================
 
// Controllino MICRO header GPIO0 maps to RP2040 GPIO0 / Arduino D0.
#define PWM_OUTPUT_PIN D0
// Controllino MICRO header GPIO1 maps to RP2040 GPIO1 / Arduino D1.
#define ENABLE_INPUT_PIN D1
 
// ============================================================================
// Timing
// ============================================================================
 
static constexpr float CONTROL_FS_HZ = 8000.0f;
static constexpr float CONTROL_TS_S = 1.0f / CONTROL_FS_HZ;
static constexpr int64_t CONTROL_PERIOD_US = -125; // -1e6/fs = -125 us (repeating timer)
 
// ============================================================================
// PWM configuration (mirrors src/controllino/main-controllino/main-controllino.ino)
// ============================================================================
 
#define SYS_CLOCK_HZ 125000000UL
#define PWM_RESOLUTION_BITS 9
#define PWM_TOP ((1u << PWM_RESOLUTION_BITS) - 1u)
#define PWM_FREQ_HZ (SYS_CLOCK_HZ / ((uint32_t)PWM_TOP + 1u))
#define PWM_MAX_FRAC 0.84f
 
// ============================================================================
// ODrive GPIO1 analog mapping and pull-up compensation (reuse from main-controllino.ino)
// ============================================================================
 
#define ODRIVE_GPIO1_MIN_TORQUE (-3.874f)
#define ODRIVE_GPIO1_MAX_TORQUE (2.0f)
#define ODRIVE_GPIO1_VREF (3.3f)
 
#define ODRIVE_GPIO1_PULLUP_OHMS (2700.0f)
#define RC_SERIES_OHMS (720.0f)
#define ODRIVE_GPIO1_PULLUP_V (5.0f)
 
static inline float clampf(float x, float lo, float hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}
 
static inline float torqueToOdriveGpio1Voltage(float torque) {
  const float span = (ODRIVE_GPIO1_MAX_TORQUE - ODRIVE_GPIO1_MIN_TORQUE);
  if (span == 0.0f) return 0.0f;
  float norm = (torque - ODRIVE_GPIO1_MIN_TORQUE) / span;
  norm = clampf(norm, 0.0f, 1.0f);
  return norm * ODRIVE_GPIO1_VREF;
}
 
static inline float odriveGpio1VoltageToPwmVoltage(float v_pin) {
  const float Rs = RC_SERIES_OHMS;
  const float Rp = ODRIVE_GPIO1_PULLUP_OHMS;
  const float Vp = ODRIVE_GPIO1_PULLUP_V;
 
  v_pin = clampf(v_pin, 0.0f, ODRIVE_GPIO1_VREF);
 
  if (Rs <= 0.0f || Rp <= 0.0f) {
    return v_pin;
  }
 
  const float g_sum = (1.0f / Rs) + (1.0f / Rp);
  if (g_sum <= 0.0f) return 0.0f;
 
  // Invert divider: V_pin = (V_pwm/Rs + Vp/Rp) / (1/Rs + 1/Rp)
  float v_pwm = Rs * (v_pin * g_sum - (Vp / Rp));
  return clampf(v_pwm, 0.0f, ODRIVE_GPIO1_VREF);
}
 
static inline uint16_t voltageToPwmDuty(float v) {
  v = clampf(v, 0.0f, ODRIVE_GPIO1_VREF);
  float duty_f = (v / ODRIVE_GPIO1_VREF) * (float)PWM_TOP;
  float max_duty = PWM_MAX_FRAC * (float)PWM_TOP;
  if (duty_f > max_duty) duty_f = max_duty;
  if (duty_f < 0.0f) duty_f = 0.0f;
  return (uint16_t)(duty_f + 0.5f);
}
 
// ============================================================================
// ADC configuration (RP2040)
// ============================================================================
 
// Controllino Micro A0-A3 mapping: RP2040 GPIO26-29 -> ADC0-3
#define ADC_PIN_A0 26
#define ADC_PIN_A1 27
#define ADC_PIN_A2 28
#define ADC_PIN_A3 29
 
static constexpr float RP2040_ADC_MAX_COUNTS = 4095.0f;
 
// ============================================================================
// Sensor mapping and x_spindle computation
// ============================================================================
 
static constexpr float A0A3_FULL_SCALE_V = 25.8f;
static constexpr float SENSOR_SENSITIVITY_V_PER_G = 0.2f;
static constexpr float G_TO_MPS2 = 9.81f;
static constexpr float COUNTS_TO_V = (A0A3_FULL_SCALE_V / RP2040_ADC_MAX_COUNTS);
static constexpr float V_TO_MPS2 = (G_TO_MPS2 / SENSOR_SENSITIVITY_V_PER_G);
static constexpr float COUNTS_TO_MPS2 = COUNTS_TO_V * V_TO_MPS2;
 
static constexpr float ALPHA1_DEG = 57.1715f;
static float inv_cos_alpha1 = 1.0f; // computed in setup()
 
// ============================================================================
// Discrete filters
// ============================================================================
 
struct LeadLag1 {
  // Discrete y[n] = (K*(b0*x[n] + b1*x[n-1]) - a1*y[n-1]) / a0
  float K = 0.0f;
  float b0 = 0.0f;
  float b1 = 0.0f;
  float a0 = 1.0f;
  float a1 = 0.0f;
  float x1 = 0.0f;
  float y1 = 0.0f;
  float i1 = 0.0f;
 
  void reset() {
    x1 = 0.0f;
    y1 = 0.0f;
    i1 = 0.0f;
  }
 
  void configureBilinear(float K_in, float z1_rad_s, float p1_rad_s, float Ts) {
    // Continuous: K*(s+z1)/(s+p1), with s = (2/Ts)*(1 - z^-1)/(1 + z^-1)
    K = K_in;
    const float c = 2.0f / Ts;
    b0 = c + z1_rad_s;
    b1 = -c + z1_rad_s;
    a0 = c + p1_rad_s;
    a1 = -c + p1_rad_s;
 
    if (!isfinite(a0) || fabsf(a0) < 1e-12f) {
      a0 = 1.0f;
      a1 = 0.0f;
      b0 = 0.0f;
      b1 = 0.0f;
      K = 0.0f;
    }
  }
 
  float step(float x) {
    const float y = (K * (b0 * x + b1 * x1) - a1 * y1) / a0;
    x1 = x;
    y1 = y;
    return y;
  }

  float integrateAndClamp(float u_in, float clamp_min, float clamp_max) {
    // Pure-integrated output:
    //   i_candidate = i1 + u_in           (raw z/(z-1))
    //   torque_cmd  = clamp(i_candidate)
    // Anti-windup: hold i1 constant while clamped.
    if (!isfinite(u_in) || !isfinite(i1)) {
      return 0.0f;
    }

    const float i_candidate = i1 + u_in;
    const bool saturated = (i_candidate <= clamp_min) || (i_candidate >= clamp_max);
    if (!saturated && isfinite(i_candidate)) {
      i1 = i_candidate;
    }

    return clampf(i_candidate, clamp_min, clamp_max);
  }
};
 
static inline void biquad_set_identity(Biquad &q) {
  q.b0 = 1.0f; q.b1 = 0.0f; q.b2 = 0.0f;
  q.a1 = 0.0f; q.a2 = 0.0f;
}
 
static inline void biquad_config_lowpass_butterworth(Biquad &q, float fs_hz, float fc_hz) {
  if (!(fc_hz > 0.0f) || !(fs_hz > 0.0f) || fc_hz >= (0.5f * fs_hz)) {
    biquad_set_identity(q);
    return;
  }
 
  const float Q = 0.70710678118f; // Butterworth
  const float w0 = 2.0f * (float)M_PI * (fc_hz / fs_hz);
  const float cosw0 = cosf(w0);
  const float sinw0 = sinf(w0);
  const float alpha = sinw0 / (2.0f * Q);
 
  float b0 = (1.0f - cosw0) * 0.5f;
  float b1 = 1.0f - cosw0;
  float b2 = (1.0f - cosw0) * 0.5f;
  float a0 = 1.0f + alpha;
  float a1 = -2.0f * cosw0;
  float a2 = 1.0f - alpha;
 
  if (!isfinite(a0) || fabsf(a0) < 1e-12f) {
    biquad_set_identity(q);
    return;
  }
 
  q.b0 = b0 / a0;
  q.b1 = b1 / a0;
  q.b2 = b2 / a0;
  q.a1 = a1 / a0;
  q.a2 = a2 / a0;
}
 
static inline void biquad_config_notch(Biquad &q, float fs_hz, float f0_hz, float Q) {
  if (!(f0_hz > 0.0f) || !(fs_hz > 0.0f) || !(Q > 0.0f) || f0_hz >= (0.5f * fs_hz)) {
    biquad_set_identity(q);
    return;
  }
 
  const float w0 = 2.0f * (float)M_PI * (f0_hz / fs_hz);
  const float cosw0 = cosf(w0);
  const float sinw0 = sinf(w0);
  const float alpha = sinw0 / (2.0f * Q);
 
  float b0 = 1.0f;
  float b1 = -2.0f * cosw0;
  float b2 = 1.0f;
  float a0 = 1.0f + alpha;
  float a1 = -2.0f * cosw0;
  float a2 = 1.0f - alpha;
 
  if (!isfinite(a0) || fabsf(a0) < 1e-12f) {
    biquad_set_identity(q);
    return;
  }
 
  q.b0 = b0 / a0;
  q.b1 = b1 / a0;
  q.b2 = b2 / a0;
  q.a1 = a1 / a0;
  q.a2 = a2 / a0;
}
 
// ============================================================================
// Controller configuration (PLACEHOLDERS — tune these)
// ============================================================================
 
// Lead-lag: K * (s + z1) / (s + p1)
static constexpr float LL_K = 0.10f;
static constexpr float LL_Z1_RAD_S = 2.0f * (float)M_PI * 20.0f;
static constexpr float LL_P1_RAD_S = 2.0f * (float)M_PI * 200.0f;
 
// 2nd order low-pass cutoff ("bandwidth") in Hz. Set <=0 to bypass.
static constexpr float LP_CUTOFF_HZ = 800.0f;
 
// Notch filters. Set f0<=0 or Q<=0 to bypass.
static constexpr float NOTCH1_F0_HZ = 0.0f;
static constexpr float NOTCH1_Q = 0.0f;
static constexpr float NOTCH2_F0_HZ = 0.0f;
static constexpr float NOTCH2_Q = 0.0f;
 
// Safety clamps
static constexpr float TORQUE_CLAMP_MIN = ODRIVE_GPIO1_MIN_TORQUE;
static constexpr float TORQUE_CLAMP_MAX = ODRIVE_GPIO1_MAX_TORQUE;
 
// ============================================================================
// Globals
// ============================================================================
 
static struct repeating_timer control_timer;
static volatile bool pwm_update_pending = false;
static volatile uint16_t pwm_duty_pending = 0;
 
static LeadLag1 leadlag;
static Biquad lpf2;
static Biquad notch1;
static Biquad notch2;
 
static inline void resetControllerState() {
  leadlag.reset();
  lpf2.reset();
  notch1.reset();
  notch2.reset();
}
 
// ============================================================================
// Control ISR
// ============================================================================
 
#ifdef ARDUINO_ARCH_RP2040
static inline uint16_t adc_read_gpio(uint8_t gpio) {
  adc_select_input((uint)(gpio - 26u));
  return adc_read(); // 12-bit 0..4095
}
 
static bool controlTimerCallback(struct repeating_timer *t) {
  (void)t;
 
  const bool enabled = (digitalRead(ENABLE_INPUT_PIN) == HIGH);
  if (!enabled) {
    resetControllerState();
    pwm_duty_pending = 0;
    pwm_update_pending = true;
    return true;
  }
 
  // Read raw ADC counts
  const uint16_t a0 = adc_read_gpio(ADC_PIN_A0);
  const uint16_t a1 = adc_read_gpio(ADC_PIN_A1);
  const uint16_t a3 = adc_read_gpio(ADC_PIN_A3);
 
  // Convert to accelerations [m/s^2] according to requirement:
  // acc = (counts/4095 * 25.8 / 0.2 * 9.81)
  const float acc_spindle_left = (float)a0 * COUNTS_TO_MPS2;
  const float acc_spindle_right = (float)a1 * COUNTS_TO_MPS2;
  const float acc_workbed_x = (float)a3 * COUNTS_TO_MPS2;
 
  const float x_spindle =
      ((acc_spindle_right - acc_spindle_left) * inv_cos_alpha1) - acc_workbed_x;
 
  float u = x_spindle;
  u = leadlag.step(u);
  u = lpf2.step(u);
  u = notch1.step(u);
  u = notch2.step(u);
 
  // Interpret filter output as desired torque (placeholder convention).
  float torque_cmd = leadlag.integrateAndClamp(u, TORQUE_CLAMP_MIN, TORQUE_CLAMP_MAX);
 
  float v_pin = torqueToOdriveGpio1Voltage(torque_cmd);
  float v_pwm = odriveGpio1VoltageToPwmVoltage(v_pin);
  uint16_t duty = voltageToPwmDuty(v_pwm);
 
  pwm_duty_pending = duty;
  pwm_update_pending = true;
  return true;
}
#endif
 
// ============================================================================
// Setup / loop
// ============================================================================
 
void setup() {
  // GPIO
  pinMode(PWM_OUTPUT_PIN, OUTPUT);
  pinMode(ENABLE_INPUT_PIN, INPUT);
 
  // PWM carrier
  analogWriteFreq(PWM_FREQ_HZ);
  analogWriteRange(PWM_TOP);
  analogWrite(PWM_OUTPUT_PIN, 0);
  pwm_update_pending = false;
  pwm_duty_pending = 0;
 
  // Precompute geometry constant
  const float alpha1_rad = ALPHA1_DEG * ((float)M_PI / 180.0f);
  const float c = cosf(alpha1_rad);
  inv_cos_alpha1 = (fabsf(c) > 1e-6f) ? (1.0f / c) : 0.0f;
 
  // Configure filters
  leadlag.configureBilinear(LL_K, LL_Z1_RAD_S, LL_P1_RAD_S, CONTROL_TS_S);
  biquad_config_lowpass_butterworth(lpf2, CONTROL_FS_HZ, LP_CUTOFF_HZ);
  biquad_config_notch(notch1, CONTROL_FS_HZ, NOTCH1_F0_HZ, NOTCH1_Q);
  biquad_config_notch(notch2, CONTROL_FS_HZ, NOTCH2_F0_HZ, NOTCH2_Q);
  resetControllerState();
 
  // ADC + timer
  #ifdef ARDUINO_ARCH_RP2040
    adc_init();
    adc_gpio_init(ADC_PIN_A0);
    adc_gpio_init(ADC_PIN_A1);
    adc_gpio_init(ADC_PIN_A2);
    adc_gpio_init(ADC_PIN_A3);
 
    add_repeating_timer_us(CONTROL_PERIOD_US, controlTimerCallback, NULL, &control_timer);
  #endif
}
 
void loop() {
  if (pwm_update_pending) {
    noInterrupts();
    const uint16_t duty = pwm_duty_pending;
    pwm_update_pending = false;
    interrupts();
 
    analogWrite(PWM_OUTPUT_PIN, (int)duty);
  }
 
  delay(1);
}

