"""
ODrive Servo System Identification Script

Performs frequency sweep system identification of an ODrive motor by sending
sinusoidal torque commands at increasing frequencies and measuring the position response.
Uses ODrive Autotuning API and on-device high-rate capture (8 kHz).
"""

import sys
import os
import csv
import time
import threading
from datetime import datetime

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

from odrive.enums import (
    INPUT_MODE_PASSTHROUGH,
    INPUT_MODE_TUNING,
)

try:
    from odrive.utils import high_rate_capture_start, TimestampFmt
except ImportError:
    try:
        from importlib.metadata import version as _pkg_version
        _odrive_ver = _pkg_version("odrive")
    except Exception:
        _odrive_ver = "unknown"
    print(
        "ERROR: high-rate capture requires odrive>=0.6.11.post0.\n"
        f"  Installed: odrive {_odrive_ver}\n"
        "  Upgrade:  pip install -r src/python/requirements.txt"
    )
    sys.exit(1)

from .odrive_config import ODriveController

# ============================================================================
# Configuration Parameters
# ============================================================================

fmin = 120.0  # Minimum frequency in Hz
fmax = 400.0  # Maximum frequency in Hz
df = 20.0  # Frequency step in Hz
duration = 0.25  # Measurement duration in seconds
t_delay = 1.0  # Settling time before acquisition in seconds
# control_mode is set via ODriveController.set_control_mode()
torque_amplitude = 2  # Torque amplitude in Nm
show_measurements = False  # Show time-domain plots of each measurement

# High-rate capture: 2 variables -> 1024 ms max window (ODrive firmware 0.6.12+)
CAPTURE_MAX_DURATION_S = 1.0
CAPTURE_PROPERTIES = [
    "axis0.controller.torque_setpoint",
    "axis0.pos_estimate",
]
TORQUE_FIELD = "axis0.controller.torque_setpoint"
POS_FIELD = "axis0.pos_estimate"

# ============================================================================
# Global Variables
# ============================================================================

stop_identification = False
user_input_thread = None

# ============================================================================
# High-rate capture helpers
# ============================================================================

def check_firmware_support(odrv):
    """
    Verify ODrive firmware supports high-rate capture (0.6.12+).

    Returns:
        tuple: (ok: bool, message: str)
    """
    try:
        major = int(odrv.fw_version_major)
        minor = int(odrv.fw_version_minor)
        revision = int(odrv.fw_version_revision)
    except Exception as e:
        return False, f"Could not read firmware version: {e}"

    if (major, minor) < (0, 6) or (major == 0 and minor == 6 and revision < 12):
        return False, (
            f"Firmware {major}.{minor}.{revision} does not support high-rate capture. "
            "Update to ODrive firmware 0.6.12 or newer."
        )
    return True, f"{major}.{minor}.{revision}"


def slice_capture_to_duration(data, duration_s):
    """
    Keep samples in the last duration_s seconds before the trigger.

    Timestamps are nanoseconds relative to the trigger (trigger_point=1.0).
    """
    timestamps_ns = np.asarray(data["timestamps"], dtype=np.float64)
    t_end_ns = 0.0
    t_start_ns = -duration_s * 1e9
    mask = (timestamps_ns >= t_start_ns) & (timestamps_ns <= t_end_ns)
    if not np.any(mask):
        raise ValueError(
            f"No capture samples in [{t_start_ns/1e9:.3f}, {t_end_ns/1e9:.3f}] s relative to trigger"
        )

    time_s = timestamps_ns[mask] / 1e9
    torque_setpoint = np.asarray(data[TORQUE_FIELD], dtype=np.float64)[mask]
    pos_estimate = np.asarray(data[POS_FIELD], dtype=np.float64)[mask]
    return torque_setpoint, pos_estimate, time_s


def estimate_sample_rate(timestamps_s, odrv):
    """Estimate sample rate from timestamps or fall back to control_loop_hz."""
    if len(timestamps_s) > 1:
        dt = np.diff(timestamps_s)
        dt = dt[dt > 0]
        if len(dt) > 0:
            return 1.0 / float(np.median(dt))
    try:
        return float(odrv.control_loop_hz)
    except Exception:
        return 8000.0


def acquire_identification_window(odrv, duration_s, trigger_timeout_s=None):
    """
    Record torque_setpoint and pos_estimate for duration_s at control-loop rate.

    Returns:
        dict with keys: torque_setpoint, pos_estimate, time_s, sample_rate
    """
    capturer = high_rate_capture_start(odrv, CAPTURE_PROPERTIES)
    time.sleep(duration_s)
    data = capturer.trigger_and_download_sync(
        trigger_point=1.0,
        trigger_timeout=trigger_timeout_s or (duration_s + 2.0),
        return_as=np.recarray,
        t_fmt=TimestampFmt.NANOSECONDS,
    )
    torque_setpoint, pos_estimate, time_s = slice_capture_to_duration(data, duration_s)
    sample_rate = estimate_sample_rate(time_s, odrv)
    return {
        "torque_setpoint": torque_setpoint,
        "pos_estimate": pos_estimate,
        "time_s": time_s,
        "sample_rate": sample_rate,
    }


# ============================================================================
# Helper Functions
# ============================================================================

def check_user_input():
    """Check for user input to stop identification (non-blocking)."""
    global stop_identification
    while not stop_identification:
        try:
            user_input = input()
            if user_input.lower() == "q":
                stop_identification = True
                print("\nStopping identification...")
                break
        except (EOFError, KeyboardInterrupt):
            break
        except Exception:
            pass


def calculate_transfer_function(input_signal, output_signal, sample_rate, excitation_freq):
    """
    Calculate transfer function gain and phase at excitation frequency using Welch/CSD method.

    Args:
        input_signal: Input signal (torque_setpoint)
        output_signal: Output signal (pos_estimate, turns)
        sample_rate: Sampling rate in Hz
        excitation_freq: Excitation frequency in Hz

    Returns:
        gain: Magnitude at excitation frequency
        phase: Phase in radians at excitation frequency
    """
    nperseg = max(len(input_signal) // 4, 8)
    f, Pxy = signal.csd(output_signal, input_signal, fs=sample_rate, nperseg=nperseg)
    f, Pxx = signal.welch(input_signal, fs=sample_rate, nperseg=nperseg)

    H = Pxy / (Pxx + 1e-10)
    freq_idx = np.argmin(np.abs(f - excitation_freq))
    magnitude = np.abs(H[freq_idx])
    phase = np.angle(H[freq_idx])
    return magnitude, phase


def set_autotuning(axis, freq, amplitude):
    """Set autotuning frequency and torque amplitude (multiple API patterns)."""
    autotuning_set = False

    if hasattr(axis.controller, "autotuning"):
        try:
            axis.controller.autotuning.frequency = freq
            axis.controller.autotuning.torque_amplitude = amplitude
            autotuning_set = True
        except Exception:
            pass

    if not autotuning_set and hasattr(axis.controller.config, "autotuning"):
        try:
            axis.controller.config.autotuning.frequency = freq
            axis.controller.config.autotuning.torque_amplitude = amplitude
            autotuning_set = True
        except Exception:
            pass

    if not autotuning_set:
        try:
            axis.controller.config.autotuning_frequency = freq
            axis.controller.config.autotuning_torque_amplitude = amplitude
            autotuning_set = True
        except Exception:
            pass

    if not autotuning_set:
        raise RuntimeError("Could not set autotuning parameters with any known API pattern")


def plot_measurement(time_s, torque_setpoint, pos_estimate, freq, sample_rate):
    """Plot time-domain and FFT views for one frequency."""
    fft_torque = np.fft.fft(torque_setpoint)
    fft_position = np.fft.fft(pos_estimate)
    fft_torque[0] = 0
    fft_position[0] = 0

    gain_torque = np.abs(fft_torque)
    phase_torque = np.angle(fft_torque)
    gain_position = np.abs(fft_position)
    phase_position = np.angle(fft_position)

    freqs = np.fft.fftfreq(len(torque_setpoint), 1.0 / sample_rate)
    n_half = len(freqs) // 2
    freqs_positive = freqs[:n_half]
    gain_torque_positive = gain_torque[:n_half]
    phase_torque_positive = phase_torque[:n_half]
    gain_position_positive = gain_position[:n_half]
    phase_position_positive = phase_position[:n_half]

    fig, ax = plt.subplots(3, 2, figsize=(12, 10))

    ax[0, 0].plot(time_s, torque_setpoint, "b-", linewidth=1)
    ax[0, 0].set_xlabel("Time (s)")
    ax[0, 0].set_ylabel("Torque Setpoint (Nm)")
    ax[0, 0].set_title(f"Torque Time-Domain at {freq:.1f} Hz")
    ax[0, 0].grid(True, alpha=0.3)

    ax[0, 1].plot(time_s, pos_estimate, "r-", linewidth=1)
    ax[0, 1].set_xlabel("Time (s)")
    ax[0, 1].set_ylabel("Position Estimate (turns)")
    ax[0, 1].set_title(f"Position Time-Domain at {freq:.1f} Hz")
    ax[0, 1].grid(True, alpha=0.3)

    ax[1, 0].plot(freqs_positive, gain_torque_positive, "b-", linewidth=1)
    ax[1, 0].set_xlabel("Frequency (Hz)")
    ax[1, 0].set_ylabel("Gain")
    ax[1, 0].set_title("Torque FFT Gain")
    ax[1, 0].grid(True, alpha=0.3)

    ax[1, 1].plot(freqs_positive, gain_position_positive, "r-", linewidth=1)
    ax[1, 1].set_xlabel("Frequency (Hz)")
    ax[1, 1].set_ylabel("Gain")
    ax[1, 1].set_title("Position Estimate FFT Gain")
    ax[1, 1].grid(True, alpha=0.3)

    ax[2, 0].plot(freqs_positive, phase_torque_positive, "b-", linewidth=1)
    ax[2, 0].set_xlabel("Frequency (Hz)")
    ax[2, 0].set_ylabel("Phase (radians)")
    ax[2, 0].set_title("Torque FFT Phase")
    ax[2, 0].grid(True, alpha=0.3)

    ax[2, 1].plot(freqs_positive, phase_position_positive, "r-", linewidth=1)
    ax[2, 1].set_xlabel("Frequency (Hz)")
    ax[2, 1].set_ylabel("Phase (radians)")
    ax[2, 1].set_title("Position Estimate FFT Phase")
    ax[2, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show(block=True)
    plt.close(fig)


# ============================================================================
# Main Identification Function
# ============================================================================

def main():
    """Main identification function."""
    global stop_identification, user_input_thread

    if duration > CAPTURE_MAX_DURATION_S:
        print(
            f"WARNING: duration={duration}s exceeds recommended max "
            f"{CAPTURE_MAX_DURATION_S}s for 2-variable high-rate capture."
        )

    print("=" * 60)
    print("ODrive Servo System Identification")
    print("=" * 60)
    print("Parameters:")
    print(f"  Frequency range: {fmin} - {fmax} Hz (step: {df} Hz)")
    print(f"  Measurement duration: {duration} s")
    print(f"  Settling time: {t_delay} s")
    print(f"  Torque amplitude: {torque_amplitude} Nm")
    print(f"  Capture: high-rate ({', '.join(CAPTURE_PROPERTIES)})")
    print("=" * 60)

    print("\nConnecting to ODrive...")
    odrive_ctrl = ODriveController()
    if not odrive_ctrl.connect():
        print("ERROR: Failed to connect to ODrive. Exiting.")
        return 1

    odrv = odrive_ctrl.odrv
    axis = odrive_ctrl.axis

    ok, fw_msg = check_firmware_support(odrv)
    if not ok:
        print(f"ERROR: {fw_msg}")
        odrive_ctrl.disconnect()
        return 1
    print(f"ODrive connected (firmware {fw_msg}).")

    try:
        capture_hz = float(odrv.control_loop_hz)
    except Exception:
        capture_hz = 8000.0
    print(f"  Control-loop capture rate: {capture_hz:.0f} Hz")

    print("\nConfiguring ODrive for torque control...")
    if not odrive_ctrl.set_control_mode("Torque"):
        print("ERROR: Failed to set control mode. Exiting.")
        odrive_ctrl.disconnect()
        return 1

    print("Setting input mode to PASSTHROUGH...")
    try:
        from odrive.enums import InputMode

        axis.controller.config.input_mode = InputMode.PASSTHROUGH
        print("Input mode set to PASSTHROUGH.")
    except Exception as e:
        print(f"ERROR: Failed to set input mode to PASSTHROUGH: {e}")
        try:
            axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH
            print("Input mode set to PASSTHROUGH (using direct enum).")
        except Exception as e2:
            print(f"ERROR: Failed to set input mode: {e2}")
            odrive_ctrl.disconnect()
            return 1

    print("\nEntering closed-loop control...")
    if not odrive_ctrl.enter_closed_loop():
        print("WARNING: Failed to enter closed-loop control. Continuing anyway...")

    time.sleep(0.5)

    print("\n" + "=" * 60)
    response = input("Start identification? (y/n): ").strip().lower()
    if response != "y":
        print("Identification cancelled by user.")
        odrive_ctrl.exit_closed_loop()
        odrive_ctrl.disconnect()
        return 0

    print("\nSetting input mode to TUNING...")
    try:
        from odrive.enums import InputMode

        axis.controller.config.input_mode = InputMode.TUNING
        print("Input mode set to TUNING.")
    except Exception as e:
        print(f"ERROR: Failed to set input mode to TUNING: {e}")
        try:
            axis.controller.config.input_mode = INPUT_MODE_TUNING
            print("Input mode set to TUNING (using direct enum).")
        except Exception as e2:
            print(f"ERROR: Failed to set input mode: {e2}")
            odrive_ctrl.exit_closed_loop()
            odrive_ctrl.disconnect()
            return 1

    print("\nStarting identification...")
    print("Type 'q' or 'Q' and press Enter to stop at any time.")
    print("=" * 60)

    stop_identification = False
    user_input_thread = threading.Thread(target=check_user_input, daemon=True)
    user_input_thread.start()

    frequencies = np.arange(fmin, fmax + df, df)
    num_frequencies = len(frequencies)
    results = []

    for idx, freq in enumerate(frequencies):
        if stop_identification:
            print(f"\nIdentification stopped by user at frequency {freq:.1f} Hz")
            break

        print(f"\n[{idx+1}/{num_frequencies}] Testing frequency: {freq:.1f} Hz", end="", flush=True)

        try:
            set_autotuning(axis, freq, torque_amplitude)

            print(" [settling...]", end="", flush=True)
            time.sleep(t_delay)

            print(" [acquiring...]", end="", flush=True)
            data_result = acquire_identification_window(odrv, duration)

            torque_setpoint = data_result["torque_setpoint"]
            pos_estimate = data_result["pos_estimate"]
            time_s = data_result["time_s"]
            actual_sample_rate = data_result["sample_rate"]

            if len(torque_setpoint) < 10 or len(pos_estimate) < 10:
                print(" [FAILED - insufficient data]")
                continue

            if show_measurements:
                plot_measurement(time_s, torque_setpoint, pos_estimate, freq, actual_sample_rate)

            print(" [processing...]", end="", flush=True)
            gain, phase = calculate_transfer_function(
                torque_setpoint, pos_estimate, actual_sample_rate, freq
            )

            results.append({"frequency": freq, "gain": gain, "phase": phase})
            print(f" [gain={gain:.4e}, phase={phase:.4f} rad, fs={actual_sample_rate:.0f} Hz]")

        except Exception as e:
            print(f" [ERROR: {e}]")
            import traceback

            traceback.print_exc()
            continue

    stop_identification = True

    print("\nExiting closed-loop control...")
    odrive_ctrl.exit_closed_loop()
    odrive_ctrl.disconnect()

    if len(results) == 0:
        print("\nERROR: No valid measurements collected. Exiting.")
        return 1

    frequencies_result = np.array([r["frequency"] for r in results])
    gains = np.array([r["gain"] for r in results])
    phases = np.array([r["phase"] for r in results])

    phases_unwrapped = np.unwrap(phases)
    phases_unwrapped_deg = np.degrees(phases_unwrapped)

    print("\nGenerating Bode plot...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.loglog(frequencies_result, gains, "b-", linewidth=2)
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("Gain (turns/Nm)")
    ax1.set_title("Bode Plot: Torque to Position (turns) Transfer Function")
    ax1.grid(True, which="both", alpha=0.3)

    ax2.semilogx(frequencies_result, phases_unwrapped_deg, "r-", linewidth=2)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Phase (degrees)")
    ax2.grid(True, which="both", alpha=0.3)

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f"tf_torque_pos_{timestamp}.png"
    plt.savefig(plot_filename, dpi=150)
    print(f"Bode plot saved to: {plot_filename}")

    plt.show(block=True)
    plt.close(fig)

    csv_filename = f"tf_torque_pos_{timestamp}.csv"
    print(f"\nSaving results to: {csv_filename}")
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["frequency", "gain", "phase"])
        for freq, gain, phase in zip(frequencies_result, gains, phases_unwrapped_deg):
            writer.writerow([freq, gain, phase])

    print("Results saved successfully.")
    print(f"\nTotal measurements: {len(results)}")
    print("=" * 60)
    print("Identification complete!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        os._exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up...")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
