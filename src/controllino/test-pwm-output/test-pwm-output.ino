/*
 * PWM Sine Wave Output Test — Controllino Micro (RP2040)
 *
 * Generates a sine wave on a GPIO pin via PWM + RC filter.
 *
 * PWM FREQUENCY vs. RESOLUTION TRADE-OFF (RP2040 @ 125 MHz, 1st-order RC at 4 kHz):
 *
 *   Ripple spec: 3.3 V / 2^12 ≈ 0.81 mV
 *   Required:    f_pwm ≥ (2/π) × 4000 Hz × 4096 ≈ 10.4 MHz
 *
 *   PWM_RESOLUTION_BITS | f_pwm     | TOP   | Duty levels | Ripple (worst case)
 *   12                  | 30.5 kHz  | 4095  | 4096        | 274 mV
 *   10                  | 122 kHz   | 1023  | 1024        |  69 mV
 *    8                  | 488 kHz   |  255  |  256        |  17 mV   ← default
 *    6                  | 1.95 MHz  |   63  |   64        | 4.3 mV
 *    4                  | 7.8 MHz   |   15  |   16        | 1.1 mV
 *   ~3.6 (TOP=11)       | 10.4 MHz  |   11  |   12        | 0.81 mV  ← spec met, only 12 levels!
 *
 *   To simultaneously meet the ripple spec AND have fine amplitude resolution, use a
 *   2nd-order (or higher) RC filter. With a 2nd-order 4 kHz filter, the same 0.81 mV
 *   ripple is achievable at f_pwm ≈ 320 kHz (~8.5-bit duty cycle resolution).
 *
 * CONFIGURATION (edit the #defines below):
 *   PWM_OUTPUT_PIN      — RP2040 GPIO number; verify against your Controllino Micro pinout
 *   SINE_FREQ_HZ        — Sine wave frequency [Hz]
 *   SINE_AMPLITUDE_FRAC — Output amplitude as fraction of full 0–3.3 V range (0.0–1.0)
 *   SINE_OFFSET_FRAC    — DC offset as fraction of full range (0.5 = 1.65 V midpoint)
 *   PWM_RESOLUTION_BITS — PWM counter bits (4–12); trades ripple vs. amplitude resolution
 *   SINE_TABLE_SIZE     — Samples per sine period; more samples = smoother waveform
 *
 * NOTE: The RP2040 timer has 1 µs resolution, so the actual sine frequency may differ
 *       slightly from SINE_FREQ_HZ. The actual frequency is printed at startup.
 */

#include <hardware/timer.h>   // for add_repeating_timer_us()
#include <math.h>

// ============================================================================
// Configuration — edit here
// ============================================================================

// GPIO0 screw terminal on the Controllino Micro = RP2040 GPIO2 = Arduino pin 2.
// The controllino_rp2 BSP does not define a CONTROLLINO_MICRO_GPIO0 alias,
// so we define it here. (PIN_WIRE0_SDA also maps to pin 2 but that is just
// the alternate I2C function; the pin is freely usable as GPIO/PWM.)
#define CONTROLLINO_MICRO_GPIO0     (2u)
#define PWM_OUTPUT_PIN              CONTROLLINO_MICRO_GPIO0

// Sine wave parameters
#define SINE_FREQ_HZ        0.2f   // [Hz] Sine frequency
#define SINE_AMPLITUDE_FRAC 0.9f     // Fraction of full range (0.0–1.0); 0.9 → 0.165–3.135 V
#define SINE_OFFSET_FRAC    0.5f     // DC center as fraction; 0.5 → 1.65 V

// PWM resolution. Lower value → higher f_pwm → lower RC-filter ripple.
// See trade-off table above.
#define PWM_RESOLUTION_BITS 9        // Default: 8 bits (≈ 488 kHz, ≈ 17 mV ripple)

// Sine lookup table size (samples per period).
// Actual sine frequency = 1 / (SINE_TABLE_SIZE × round(1e6/(SINE_FREQ_HZ×SINE_TABLE_SIZE)) µs)
#define SINE_TABLE_SIZE     100

// ============================================================================
// Derived constants (do not edit)
// ============================================================================

#define SYS_CLOCK_HZ        125000000UL
#define PWM_TOP             ((1u << PWM_RESOLUTION_BITS) - 1u)
#define PWM_FREQ_HZ         (SYS_CLOCK_HZ / ((uint32_t)PWM_TOP + 1u))

// Ideal timer period in µs for the sine update ISR
static const uint32_t SINE_UPDATE_US =
    (uint32_t)(1000000.0f / (SINE_FREQ_HZ * (float)SINE_TABLE_SIZE) + 0.5f);

// Actual sine frequency after integer rounding of the timer period
static const float SINE_FREQ_ACTUAL_HZ =
    1000000.0f / ((float)SINE_TABLE_SIZE * (float)SINE_UPDATE_US);

// ============================================================================
// Globals
// ============================================================================

static uint16_t sine_table[SINE_TABLE_SIZE];
static volatile uint32_t sine_index = 0;
static struct repeating_timer sine_timer;

// ============================================================================
// Build sine lookup table
// ============================================================================

static void buildSineTable() {
    float amplitude = SINE_AMPLITUDE_FRAC * 0.5f * (float)PWM_TOP;
    float offset    = SINE_OFFSET_FRAC * (float)PWM_TOP;

    for (int i = 0; i < SINE_TABLE_SIZE; i++) {
        float angle = 2.0f * (float)M_PI * (float)i / (float)SINE_TABLE_SIZE;
        float val   = offset + amplitude * sinf(angle);
        if (val < 0.0f)              val = 0.0f;
        if (val > (float)PWM_TOP)    val = (float)PWM_TOP;
        sine_table[i] = (uint16_t)(val + 0.5f);
    }
}

// ============================================================================
// Timer ISR — updates PWM duty cycle at each sine table step
// ============================================================================

static bool sineTimerCallback(struct repeating_timer *t) {
    analogWrite(PWM_OUTPUT_PIN, (int)sine_table[sine_index]);
    sine_index = (sine_index + 1 < SINE_TABLE_SIZE) ? sine_index + 1 : 0;
    return true;  // Keep repeating
}

// ============================================================================
// Setup
// ============================================================================

void setup() {
    Serial.begin(115200);
    delay(1500);

    // --- Print configuration ---
    Serial.println("=========================================");
    Serial.println("  PWM Sine Wave Output Test");
    Serial.println("=========================================");
    Serial.print  ("Output pin (CONTROLLINO_MICRO_GPIO0, RP2040 GPIO2): "); Serial.println(PWM_OUTPUT_PIN);
    Serial.println();

    Serial.println("--- Sine wave ---");
    Serial.print  ("  Requested frequency : "); Serial.print(SINE_FREQ_HZ, 1);      Serial.println(" Hz");
    Serial.print  ("  Actual frequency    : "); Serial.print(SINE_FREQ_ACTUAL_HZ, 2); Serial.println(" Hz (after 1 µs timer rounding)");
    Serial.print  ("  Amplitude fraction  : "); Serial.println(SINE_AMPLITUDE_FRAC, 2);
    Serial.print  ("  DC offset fraction  : "); Serial.println(SINE_OFFSET_FRAC, 2);
    Serial.print  ("  Amplitude (peak-peak): ");
    Serial.print  (SINE_AMPLITUDE_FRAC * 3.3f, 3); Serial.println(" V");
    Serial.print  ("  Output range        : ");
    Serial.print  ((SINE_OFFSET_FRAC - SINE_AMPLITUDE_FRAC * 0.5f) * 3.3f, 3);
    Serial.print  (" V  to  ");
    Serial.print  ((SINE_OFFSET_FRAC + SINE_AMPLITUDE_FRAC * 0.5f) * 3.3f, 3);
    Serial.println(" V");
    Serial.println();

    Serial.println("--- PWM carrier ---");
    Serial.print  ("  Resolution          : "); Serial.print(PWM_RESOLUTION_BITS); Serial.println(" bits");
    Serial.print  ("  TOP value           : "); Serial.println(PWM_TOP);
    Serial.print  ("  Duty cycle levels   : "); Serial.println(PWM_TOP + 1u);
    Serial.print  ("  Clock divider       : 1  (maximum speed)");  Serial.println();
    Serial.print  ("  PWM frequency       : "); Serial.print(PWM_FREQ_HZ); Serial.println(" Hz");
    Serial.println();

    Serial.println("--- Ripple estimate (1st-order RC, 4000 Hz cutoff) ---");
    float ripple_v = (2.0f / (float)M_PI) * 3.3f * (4000.0f / (float)PWM_FREQ_HZ);
    Serial.print  ("  Worst-case ripple   : "); Serial.print(ripple_v * 1000.0f, 2); Serial.println(" mV");
    Serial.print  ("  Target (3.3V/2^12)  : "); Serial.print(3.3f / 4096.0f * 1000.0f, 3); Serial.println(" mV");
    if (ripple_v > 3.3f / 4096.0f) {
        Serial.println("  NOTE: Ripple exceeds spec. Increase PWM freq (lower PWM_RESOLUTION_BITS)");
        Serial.println("        or use a 2nd-order RC filter.");
    } else {
        Serial.println("  Ripple within spec.");
    }
    Serial.println();

    Serial.println("--- Sine update ISR ---");
    Serial.print  ("  Table size          : "); Serial.println(SINE_TABLE_SIZE);
    Serial.print  ("  Update period       : "); Serial.print(SINE_UPDATE_US); Serial.println(" µs");
    Serial.print  ("  Update rate         : ");
    Serial.print  (1000000.0f / (float)SINE_UPDATE_US, 1); Serial.println(" Hz");
    Serial.println("=========================================");
    Serial.println();

    // --- Build sine table ---
    buildSineTable();

    // --- Configure PWM via arduino-pico core API ---
    pinMode(PWM_OUTPUT_PIN, OUTPUT);
    analogWriteFreq(PWM_FREQ_HZ);                      // Set once here — do NOT call from loop or ISR
    analogWriteRange(PWM_TOP);                         // Duty levels: 0 … PWM_TOP
    analogWrite(PWM_OUTPUT_PIN, (int)sine_table[0]);   // Initialises PWM for this pin (divider = 1)

    // --- Start repeating timer for sine duty cycle updates ---
    if (!add_repeating_timer_us(-(int64_t)SINE_UPDATE_US,
                                sineTimerCallback, NULL, &sine_timer)) {
        Serial.println("ERROR: Failed to start sine update timer!");
        while (1) delay(100);
    }

    Serial.print("Sine wave output started on GPIO ");
    Serial.println(PWM_OUTPUT_PIN);
}

// ============================================================================
// Main loop — nothing to do; sine update runs entirely from the timer ISR
// ============================================================================

void loop() {
    delay(1000);
}
