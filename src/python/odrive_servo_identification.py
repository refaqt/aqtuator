"""
ODrive Servo System Identification Script

Performs frequency sweep system identification of an ODrive motor by sending
sinusoidal torque commands at increasing frequencies and measuring the position response.
Uses ODrive Autotuning API and Controllino CAN-based data acquisition.
"""

import sys
import os
import csv
import time
import threading
import serial
import json
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

import odrive
from odrive.enums import (
    CONTROL_MODE_TORQUE_CONTROL,
    INPUT_MODE_PASSTHROUGH,
    INPUT_MODE_TUNING
)

from odrive_config import ODriveController

# ============================================================================
# Configuration Parameters
# ============================================================================

fmin = 20.0  # Minimum frequency in Hz
fmax = 200.0  # Maximum frequency in Hz
fs = 1000.0  # Sampling rate in Hz (used for both Controllino acquisition and transfer function calculation)
df = 20.0  # Frequency step in Hz
duration = 0.25  # Measurement duration in seconds
t_delay = 1.0  # Settling time before acquisition in seconds
# control_mode is set via ODriveController.set_control_mode()
torque_amplitude = 0.1  # Torque amplitude in Nm
show_measurements = True  # Show time-domain plots of each measurement

# Controllino serial port (hardcoded, can be changed)
CONTROLLINO_PORT = 'COM3'  # Change as needed

# ============================================================================
# Global Variables
# ============================================================================

stop_identification = False
user_input_thread = None

# ============================================================================
# Serial Communication Helper Class
# ============================================================================

class SerialHelper:
    """Helper class for serial communication with Controllino."""
    
    def __init__(self, port, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_port = None
        self.serial_lock = threading.Lock()
        
    def connect(self):
        """Connect to Controllino serial port."""
        try:
            self.serial_port = serial.Serial(self.port, self.baud_rate, timeout=1, write_timeout=30)
            print(f"Connected to Controllino on {self.port}")
            return True
        except Exception as e:
            print(f"Serial connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
            print("Disconnected from Controllino")
    
    def send_command_and_wait_response(self, cmd, expected_ack, timeout=2):
        """Send command and wait for expected ACK or ERROR response."""
        if not self.serial_port or not self.serial_port.is_open:
            return (False, "", "Serial port not connected")
        
        with self.serial_lock:
            try:
                # Clear input buffer
                while self.serial_port.in_waiting > 0:
                    self.serial_port.read(self.serial_port.in_waiting)
                
                # Write command
                bytes_written = self.serial_port.write((cmd + '\n').encode())
                if bytes_written == 0:
                    return (False, "", "Send command failed: No bytes written")
                
                try:
                    self.serial_port.flush()
                except:
                    pass
                
                # Wait for response
                ack_received = False
                timeout_count = 0
                max_timeout = int(timeout * 100)  # 10ms increments
                response_received = ""
                error_received = ""
                
                while timeout_count < max_timeout and not ack_received:
                    if self.serial_port.in_waiting > 0:
                        response = self.serial_port.readline().decode().strip()
                        if response == expected_ack or response.startswith(expected_ack):
                            ack_received = True
                            response_received = response
                        elif response.startswith("ERROR:"):
                            error_received = response[6:] if len(response) > 6 else "Unknown error"
                            return (False, response, error_received)
                        elif response == "" or response.startswith("DEBUG:") or response.startswith("INFO:"):
                            continue
                        else:
                            response_received = response
                    else:
                        timeout_count += 1
                        time.sleep(0.01)
                
                if ack_received:
                    return (True, response_received, "")
                else:
                    if response_received:
                        return (False, response_received, f"Expected '{expected_ack}', got '{response_received}'")
                    else:
                        return (False, "", f"Timeout waiting for '{expected_ack}'")
                        
            except Exception as e:
                return (False, "", f"Send command failed: {e}")
    
    def get_data(self):
        """Retrieve acquired data from Controllino."""
        if not self.serial_port or not self.serial_port.is_open:
            return None
        
        with self.serial_lock:
            try:
                # Clear input buffer
                while self.serial_port.in_waiting > 0:
                    self.serial_port.read(self.serial_port.in_waiting)
                
                # Send GET_DATA command
                self.serial_port.write("GET_DATA\n".encode())
                try:
                    self.serial_port.flush()
                except:
                    pass
                
                # Wait for DATA: header
                header_received = False
                timeout_count = 0
                max_timeout = 200
                header_line = ""
                
                while timeout_count < max_timeout and not header_received:
                    if self.serial_port.in_waiting > 0:
                        response = self.serial_port.readline().decode().strip()
                        if response.startswith("DATA:"):
                            header_received = True
                            header_line = response
                        elif response.startswith("ERROR:"):
                            error_msg = response[6:] if len(response) > 6 else "Unknown error"
                            print(f"Error: {error_msg}")
                            return None
                        elif response == "" or response.startswith("DEBUG:") or response.startswith("INFO:"):
                            continue
                    else:
                        timeout_count += 1
                        time.sleep(0.01)
                
                if not header_received:
                    print("Timeout waiting for DATA header")
                    return None
                
                # Parse header: DATA:<sample_count>,<sample_period>,<num_channels>
                parts = header_line[5:].split(',')
                if len(parts) < 3:
                    print("Invalid DATA header format")
                    return None
                
                sample_count = int(parts[0])
                sample_period = float(parts[1])
                num_channels = int(parts[2])
                
                # Read data samples
                data_array = []
                samples_received = 0
                timeout_count = 0
                max_timeout = 10000  # 100 seconds for large datasets
                
                while samples_received < sample_count and timeout_count < max_timeout:
                    if self.serial_port.in_waiting > 0:
                        line = self.serial_port.readline().decode().strip()
                        if line == "DATA_END":
                            break
                        if line == "" or line.startswith("DEBUG:") or line.startswith("INFO:"):
                            continue
                        
                        try:
                            values = [float(x) for x in line.split(',')]
                            if len(values) == num_channels:
                                data_array.append(values)
                                samples_received += 1
                        except ValueError:
                            continue
                    else:
                        timeout_count += 1
                        time.sleep(0.01)
                
                if samples_received < sample_count:
                    print(f"Warning: Only received {samples_received} of {sample_count} samples")
                
                return {
                    'samples': np.array(data_array),
                    'sample_rate': 1.0 / sample_period,
                    'sample_period': sample_period
                }
                
            except Exception as e:
                print(f"Error retrieving data: {e}")
                return None

# ============================================================================
# Helper Functions
# ============================================================================

def check_user_input():
    """Check for user input to stop identification (non-blocking)."""
    global stop_identification
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:238","message":"check_user_input thread started","data":{"thread_id":threading.get_ident()},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    while not stop_identification:
        try:
            # #region agent log
            with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:245","message":"About to call input()","data":{"stop_identification":stop_identification,"stdin_closed":sys.stdin.closed if sys.stdin else None},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            user_input = input()
            # #region agent log
            with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:250","message":"input() returned","data":{"user_input":user_input},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            if user_input.lower() == 'q':
                stop_identification = True
                print("\nStopping identification...")
                # #region agent log
                with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:255","message":"User requested stop, setting stop_identification","data":{},"timestamp":int(time.time()*1000)}) + '\n')
                # #endregion
                break
        except (EOFError, KeyboardInterrupt) as e:
            # #region agent log
            with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:260","message":"Exception in input() - stdin closed","data":{"exception_type":type(e).__name__,"exception_str":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            break
        except Exception as e:
            # #region agent log
            with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:265","message":"Unexpected exception in check_user_input","data":{"exception_type":type(e).__name__,"exception_str":str(e)},"timestamp":int(time.time()*1000)}) + '\n')
            # #endregion
            pass
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:270","message":"check_user_input thread exiting","data":{"stop_identification":stop_identification},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion

def calculate_transfer_function(input_signal, output_signal, sample_rate, excitation_freq):
    """
    Calculate transfer function gain and phase at excitation frequency using Welch/CSD method.
    
    Args:
        input_signal: Input signal (torque_setpoint)
        output_signal: Output signal (pos_estimate)
        sample_rate: Sampling rate in Hz
        excitation_freq: Excitation frequency in Hz
    
    Returns:
        gain: Magnitude at excitation frequency
        phase: Phase in radians at excitation frequency
    """
    # Compute transfer function using Welch's method
    f, Pxy = signal.csd(output_signal, input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
    f, Pxx = signal.welch(input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
    
    # Calculate transfer function H = Pxy / Pxx
    H = Pxy / (Pxx + 1e-10)
    
    # Find index closest to excitation frequency
    freq_idx = np.argmin(np.abs(f - excitation_freq))
    
    # Extract magnitude and phase at excitation frequency
    magnitude = np.abs(H[freq_idx])
    phase = np.angle(H[freq_idx])
    
    return magnitude, phase

def configure_cyclic_can_messages(axis, enable=True, interval_ms=1.0):
    """
    Configure ODrive cyclic CAN messages for Get_Encoder_Estimates and Get_Torques.
    
    Based on ODrive CAN protocol docs: https://docs.odriverobotics.com/v/latest/manual/can-protocol.html#can-msg-get-encoder-estimates
    
    The correct API paths are:
    - axis.config.can.encoder_msg_rate_ms = interval_ms
    - axis.config.can.torques_msg_rate_ms = interval_ms
    
    Args:
        axis: ODrive axis object
        enable: If True, enable cyclic messages; if False, disable them
        interval_ms: Interval in milliseconds (default 1.0 ms = 1000 Hz)
    
    Returns:
        bool: True if configuration successful, False otherwise
    """
    try:
        if enable:
            # Configure cyclic messages to send Get_Encoder_Estimates and Get_Torques at specified interval
            # The interval is in milliseconds (not seconds)
            axis.config.can.encoder_msg_rate_ms = interval_ms
            axis.config.can.torques_msg_rate_ms = interval_ms
            print(f"Cyclic CAN messages enabled: Get_Encoder_Estimates and Get_Torques at {interval_ms} ms interval ({1000.0/interval_ms:.1f} Hz)")
        else:
            # Disable cyclic messages by setting interval to 0
            axis.config.can.encoder_msg_rate_ms = 0.0
            axis.config.can.torques_msg_rate_ms = 0.0
            print("Cyclic CAN messages disabled")
        return True
    except AttributeError as e:
        print(f"ERROR: Failed to configure cyclic CAN messages: {e}")
        print("Available attributes in axis.config.can:")
        try:
            if hasattr(axis.config, 'can'):
                attrs = [attr for attr in dir(axis.config.can) if not attr.startswith('_')]
                print(f"  {', '.join(attrs)}")
        except:
            pass
        return False
    except Exception as e:
        print(f"ERROR: Failed to configure cyclic CAN messages: {e}")
        return False

# ============================================================================
# Main Identification Function
# ============================================================================

def main():
    """Main identification function."""
    global stop_identification, user_input_thread
    
    print("=" * 60)
    print("ODrive Servo System Identification")
    print("=" * 60)
    print(f"Parameters:")
    print(f"  Frequency range: {fmin} - {fmax} Hz (step: {df} Hz)")
    print(f"  Sampling rate: {fs} Hz")
    print(f"  Measurement duration: {duration} s")
    print(f"  Settling time: {t_delay} s")
    print(f"  Torque amplitude: {torque_amplitude} Nm")
    print("=" * 60)
    
    # Connect to ODrive
    print("\nConnecting to ODrive...")
    odrive_ctrl = ODriveController()
    if not odrive_ctrl.connect():
        print("ERROR: Failed to connect to ODrive. Exiting.")
        return 1
    
    odrv = odrive_ctrl.odrv
    axis = odrive_ctrl.axis
    
    print("ODrive connected successfully.")
    
    # Set control mode to torque control
    print("\nConfiguring ODrive for torque control...")
    if not odrive_ctrl.set_control_mode('Torque'):
        print("ERROR: Failed to set control mode. Exiting.")
        odrive_ctrl.disconnect()
        return 1
    
    # Set input mode to PASSTHROUGH initially
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
    
    # Connect to Controllino
    print(f"\nConnecting to Controllino on {CONTROLLINO_PORT}...")
    serial_helper = SerialHelper(CONTROLLINO_PORT)
    if not serial_helper.connect():
        print("ERROR: Failed to connect to Controllino. Exiting.")
        odrive_ctrl.disconnect()
        return 1
    
    print("Controllino connected successfully.")
    
    # Enter closed-loop control
    print("\nEntering closed-loop control...")
    if not odrive_ctrl.enter_closed_loop():
        print("WARNING: Failed to enter closed-loop control. Continuing anyway...")
    
    # Configure cyclic CAN messages (always enabled)
    print("\nConfiguring cyclic CAN messages...")
    if configure_cyclic_can_messages(axis, enable=True, interval_ms=1.0):
        print("Cyclic CAN messages configured successfully.")
        # Wait a bit for ODrive to process the configuration
        time.sleep(0.2)
    else:
        print("ERROR: Failed to configure cyclic CAN messages.")
        print("Please check ODrive firmware version and CAN protocol documentation.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            odrive_ctrl.exit_closed_loop()
            odrive_ctrl.disconnect()
            serial_helper.disconnect()
            return 1
    
    # Wait a bit for system to stabilize
    time.sleep(0.5)
    
    # User confirmation
    print("\n" + "=" * 60)
    response = input("Start identification? (y/n): ").strip().lower()
    if response != 'y':
        print("Identification cancelled by user.")
        odrive_ctrl.exit_closed_loop()
        odrive_ctrl.disconnect()
        serial_helper.disconnect()
        return 0
    
    # Switch input mode to TUNING at start of identification
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
            serial_helper.disconnect()
            return 1
    
    print("\nStarting identification...")
    print("Type 'q' or 'Q' and press Enter to stop at any time.")
    print("=" * 60)
    
    # Start user input thread for non-blocking quit
    # Use non-daemon thread so we can properly join it before shutdown
    stop_identification = False
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"odrive_servo_identification.py:392","message":"Starting user_input_thread","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    user_input_thread = threading.Thread(target=check_user_input, daemon=True)
    user_input_thread.start()
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"odrive_servo_identification.py:395","message":"user_input_thread started","data":{"thread_id":user_input_thread.ident,"is_alive":user_input_thread.is_alive()},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    # Generate frequency list
    frequencies = np.arange(fmin, fmax + df, df)
    num_frequencies = len(frequencies)
    
    # Storage for results
    results = []
    
    # Frequency sweep loop
    for idx, freq in enumerate(frequencies):
        if stop_identification:
            print(f"\nIdentification stopped by user at frequency {freq:.1f} Hz")
            break
        
        print(f"\n[{idx+1}/{num_frequencies}] Testing frequency: {freq:.1f} Hz", end='', flush=True)
        
        try:
            # Set autotuning parameters
            try:
                # Try different API patterns for autotuning
                autotuning_set = False
                
                # Pattern 1: axis.controller.autotuning (as per ODrive docs)
                if hasattr(axis.controller, 'autotuning'):
                    try:
                        axis.controller.autotuning.frequency = freq
                        axis.controller.autotuning.torque_amplitude = torque_amplitude
                        autotuning_set = True
                    except:
                        pass
                
                # Pattern 2: axis.controller.config.autotuning
                if not autotuning_set and hasattr(axis.controller.config, 'autotuning'):
                    try:
                        axis.controller.config.autotuning.frequency = freq
                        axis.controller.config.autotuning.torque_amplitude = torque_amplitude
                        autotuning_set = True
                    except:
                        pass
                
                # Pattern 3: Direct config attributes
                if not autotuning_set:
                    try:
                        axis.controller.config.autotuning_frequency = freq
                        axis.controller.config.autotuning_torque_amplitude = torque_amplitude
                        autotuning_set = True
                    except:
                        pass
                
                if not autotuning_set:
                    raise Exception("Could not set autotuning parameters with any known API pattern")
                    
            except Exception as e:
                print(f"\nERROR: Failed to set autotuning parameters: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            # Wait for settling time
            print(" [settling...]", end='', flush=True)
            time.sleep(t_delay)
            
            # Command Controllino to start acquisition (always cyclic mode)
            print(" [acquiring...]", end='', flush=True)
            cmd = f"START_ACQUISITION,{duration},{fs},cyclic"
            success, response, error = serial_helper.send_command_and_wait_response(
                cmd, "ACK: Acquisition started", timeout=2
            )
            
            if not success:
                print(f" [FAILED - {error}]")
                continue
            
            # Wait for acquisition to complete
            acquisition_complete = False
            timeout = 0
            max_timeout = int((duration + 2) * 100)  # Wait a bit longer than duration (0.1s increments)
            
            while timeout < max_timeout:
                if serial_helper.serial_port and serial_helper.serial_port.is_open:
                    if serial_helper.serial_port.in_waiting > 0:
                        line = serial_helper.serial_port.readline().decode().strip()
                        if line == "ACK: Acquisition complete":
                            acquisition_complete = True
                            break
                        elif line.startswith("ERROR:"):
                            print(f" [ERROR: {line}]")
                            break
                time.sleep(0.01)
                timeout += 1
            
            if not acquisition_complete:
                print(" [FAILED - timeout waiting for acquisition]")
                continue
            
            # Retrieve data from Controllino
            print(" [retrieving...]", end='', flush=True)
            data_result = serial_helper.get_data()
            
            if data_result is None:
                print(" [FAILED - no data]")
                continue
            
            # Parse data (always 2 channels: torque and position)
            data_array = data_result['samples']
            if data_array.shape[1] != 2:
                print(f" [FAILED - expected 2 channels, got {data_array.shape[1]}]")
                continue
            
            torque_setpoint = data_array[:, 0]
            pos_estimate = data_array[:, 1]
            
            if len(torque_setpoint) < 10 or len(pos_estimate) < 10:
                print(" [FAILED - insufficient data]")
                continue
            
            # Get actual sample rate from Controllino
            actual_sample_rate = data_result['sample_rate']
            
            # Plot measurement data if enabled
            if show_measurements:
                time_array = np.arange(len(torque_setpoint)) / actual_sample_rate
                
                # Compute FFT of both signals
                fft_torque = np.fft.fft(torque_setpoint)
                fft_position = np.fft.fft(pos_estimate)
                
                # Set DC component to 0 for both signals
                fft_torque[0] = 0
                fft_position[0] = 0
                
                # Extract magnitude (gain) and phase for each signal
                gain_torque = np.abs(fft_torque)
                phase_torque = np.angle(fft_torque)
                gain_position = np.abs(fft_position)
                phase_position = np.angle(fft_position)
                
                # Create frequency array
                freqs = np.fft.fftfreq(len(torque_setpoint), 1.0 / actual_sample_rate)
                
                # Use only positive frequencies (first half)
                n_half = len(freqs) // 2
                freqs_positive = freqs[:n_half]
                gain_torque_positive = gain_torque[:n_half]
                phase_torque_positive = phase_torque[:n_half]
                gain_position_positive = gain_position[:n_half]
                phase_position_positive = phase_position[:n_half]
                
                # Plot in 3x2 layout: 3 rows, 2 columns
                # Row 0: time-domain signals
                # Row 1: FFT gain
                # Row 2: FFT phase
                # Column 0: torque, Column 1: position estimate
                fig, ax = plt.subplots(3, 2, figsize=(12, 10))
                
                # Top row: Time-domain signals
                # Left: Torque time-domain
                ax[0, 0].plot(time_array, torque_setpoint, 'b-', linewidth=1)
                ax[0, 0].set_xlabel('Time (s)')
                ax[0, 0].set_ylabel('Torque Setpoint (Nm)')
                ax[0, 0].set_title(f'Torque Time-Domain at {freq:.1f} Hz')
                ax[0, 0].grid(True, alpha=0.3)
                
                # Right: Position time-domain
                ax[0, 1].plot(time_array, pos_estimate, 'r-', linewidth=1)
                ax[0, 1].set_xlabel('Time (s)')
                ax[0, 1].set_ylabel('Position Estimate (rad)')
                ax[0, 1].set_title(f'Position Time-Domain at {freq:.1f} Hz')
                ax[0, 1].grid(True, alpha=0.3)
                
                # Middle row: FFT gain
                # Left: Torque FFT gain (linear scale)
                ax[1, 0].plot(freqs_positive, gain_torque_positive, 'b-', linewidth=1)
                ax[1, 0].set_xlabel('Frequency (Hz)')
                ax[1, 0].set_ylabel('Gain')
                ax[1, 0].set_title('Torque FFT Gain')
                ax[1, 0].grid(True, alpha=0.3)
                
                # Right: Position estimate FFT gain (linear scale)
                ax[1, 1].plot(freqs_positive, gain_position_positive, 'r-', linewidth=1)
                ax[1, 1].set_xlabel('Frequency (Hz)')
                ax[1, 1].set_ylabel('Gain')
                ax[1, 1].set_title('Position Estimate FFT Gain')
                ax[1, 1].grid(True, alpha=0.3)
                
                # Bottom row: FFT phase
                # Left: Torque FFT phase
                ax[2, 0].plot(freqs_positive, phase_torque_positive, 'b-', linewidth=1)
                ax[2, 0].set_xlabel('Frequency (Hz)')
                ax[2, 0].set_ylabel('Phase (radians)')
                ax[2, 0].set_title('Torque FFT Phase')
                ax[2, 0].grid(True, alpha=0.3)
                
                # Right: Position estimate FFT phase
                ax[2, 1].plot(freqs_positive, phase_position_positive, 'r-', linewidth=1)
                ax[2, 1].set_xlabel('Frequency (Hz)')
                ax[2, 1].set_ylabel('Phase (radians)')
                ax[2, 1].set_title('Position Estimate FFT Phase')
                ax[2, 1].grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.show(block=True)
                plt.close(fig)
            
            # Calculate transfer function using Welch/CSD method
            print(" [processing...]", end='', flush=True)
            gain, phase = calculate_transfer_function(torque_setpoint, pos_estimate, actual_sample_rate, freq)
            
            # Store results
            results.append({
                'frequency': freq,
                'gain': gain,
                'phase': phase
            })
            
            print(f" [gain={gain:.4e}, phase={phase:.4f} rad]")
            
        except Exception as e:
            print(f" [ERROR: {e}]")
            import traceback
            traceback.print_exc()
            continue
    
    # Stop user input thread
    # #region agent log



    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:566","message":"Setting stop_identification=True","data":{"thread_alive":user_input_thread.is_alive() if user_input_thread else None,"thread_ident":user_input_thread.ident if user_input_thread else None},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    stop_identification = True

    # Don't wait for thread - on Windows, closing stdin doesn't immediately unblock input()
    # Since we use os._exit() later, the thread will be terminated anyway
    # The thread will exit when it processes the EOFError or when user types 'q'
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:593","message":"Skipping thread join - will use os._exit() which terminates all threads","data":{"thread_alive":user_input_thread.is_alive() if user_input_thread else None},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    # Disable cyclic CAN messages
    print("\nDisabling cyclic CAN messages...")
    try:
        configure_cyclic_can_messages(axis, enable=False)
    except Exception as e:
        print(f"WARNING: Failed to disable cyclic CAN messages: {e}")
    
    # Exit closed-loop control
    print("\nExiting closed-loop control...")
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:617","message":"About to exit closed-loop control","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    odrive_ctrl.exit_closed_loop()
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:621","message":"Closed-loop control exited","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    # Disconnect from ODrive and Controllino
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:625","message":"About to disconnect ODrive and Controllino","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    odrive_ctrl.disconnect()
    serial_helper.disconnect()
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:629","message":"Disconnected from ODrive and Controllino","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    if len(results) == 0:
        print("\nERROR: No valid measurements collected. Exiting.")
        return 1
    
    # Extract results
    frequencies_result = np.array([r['frequency'] for r in results])
    gains = np.array([r['gain'] for r in results])
    phases = np.array([r['phase'] for r in results])
    
    # Unwrap phase
    phases_unwrapped = np.unwrap(phases)
    
    # Generate Bode plot
    print("\nGenerating Bode plot...")
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:640","message":"About to generate Bode plot","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Gain plot (log-log)
    ax1.loglog(frequencies_result, gains, 'b-', linewidth=2)
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Gain')
    ax1.set_title('Bode Plot: Torque to Position Transfer Function')
    ax1.grid(True, which='both', alpha=0.3)
    
    # Phase plot (semilogx)
    ax2.semilogx(frequencies_result, phases_unwrapped, 'r-', linewidth=2)
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Phase (radians)')
    ax2.grid(True, which='both', alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_filename = f'tf_torque_pos_{timestamp}.png'
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:661","message":"About to save plot","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    plt.savefig(plot_filename, dpi=150)
    print(f"Bode plot saved to: {plot_filename}")
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:665","message":"Plot saved","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:668","message":"About to call plt.show()","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    # Use block=True so plot stays open until user closes it, then we can exit cleanly
    plt.show(block=True)
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:672","message":"plt.show() returned (user closed plot)","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    # Close the figure after user closes the window
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:676","message":"About to close matplotlib figure","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    plt.close(fig)
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:680","message":"Matplotlib figure closed","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    # Save to CSV
    csv_filename = f'tf_torque_pos_{timestamp}.csv'
    print(f"\nSaving results to: {csv_filename}")
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:677","message":"About to save CSV","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['frequency', 'gain', 'phase'])
        for freq, gain, phase in zip(frequencies_result, gains, phases_unwrapped):
            writer.writerow([freq, gain, phase])
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:684","message":"CSV saved","data":{},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    print(f"Results saved successfully.")
    print(f"\nTotal measurements: {len(results)}")
    print("=" * 60)
    print("Identification complete!")
    print("=" * 60)
    
    # #region agent log
    with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"F","location":"odrive_servo_identification.py:608","message":"main() returning, about to exit","data":{"thread_alive":user_input_thread.is_alive() if user_input_thread else None},"timestamp":int(time.time()*1000)}) + '\n')
    # #endregion
    
    return 0

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        exit_code = main()
        # #region agent log
        with open(r'c:\Users\niels\Documents\Github\aqtuator-control\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run2","hypothesisId":"G","location":"odrive_servo_identification.py:695","message":"About to call os._exit()","data":{"exit_code":exit_code},"timestamp":int(time.time()*1000)}) + '\n')
        # #endregion
        
        # Use os._exit() instead of sys.exit() to bypass interpreter shutdown cleanup
        # This prevents hangs from daemon threads or matplotlib cleanup
        # Since we've already closed the plot and cleaned up, this is safe
        os._exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up...")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
