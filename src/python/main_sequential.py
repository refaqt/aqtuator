"""
Sequential Phase 1 Control Application

Simplified sequential workflow for synchronized data acquisition and motor control system.
Integrates Controllino MICRO and ODrive S1.
Phase 1: Sequential flow without full GUI - minimal dialog windows for control.
"""

import sys
import os
import csv
from datetime import datetime
from pathlib import Path
import serial
import numpy as np
import pandas as pd
from scipy import signal
import time
import threading

from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from odrive_config import ODriveController

# ============================================================================
# Multisine CSV helpers
# ============================================================================

def _parse_multisine_freq_band_from_csv(csv_path):
    """Extract excited frequency band (Hz) from multisine CSV metadata.

    Prefers fmin_actual/fmax_actual, then falls back to fmin_desired/fmax_desired,
    then (as a last resort) parses filename like: multisine_<fmin>-<fmax>Hz_...
    Returns (fmin, fmax) as floats, or None if not available/invalid.
    """
    def _to_float_or_none(s):
        if s is None:
            return None
        s = str(s).strip()
        if not s or s.upper() == "N/A":
            return None
        try:
            return float(s)
        except ValueError:
            return None

    fmin = None
    fmax = None

    try:
        with open(csv_path, 'r') as f:
            # Only the header is needed; stop when data columns start.
            for _ in range(200):
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                if line.lower() == 'time_s,signal':
                    break
                if not line.startswith('#'):
                    continue

                # Lines look like: "# fmin_actual: 52.000000 Hz"
                content = line.lstrip('#').strip()
                if ':' not in content:
                    continue
                key, rest = content.split(':', 1)
                key = key.strip().lower()
                rest = rest.strip()
                if rest.lower().endswith('hz'):
                    rest = rest[:-2].strip()

                if key == 'fmin_actual':
                    fmin = _to_float_or_none(rest)
                elif key == 'fmax_actual':
                    fmax = _to_float_or_none(rest)
                elif key == 'fmin_desired' and fmin is None:
                    fmin = _to_float_or_none(rest)
                elif key == 'fmax_desired' and fmax is None:
                    fmax = _to_float_or_none(rest)
    except Exception:
        # Fall back to filename parsing below.
        pass

    # Filename fallback: multisine_<fmin>-<fmax>Hz_...
    if (fmin is None or fmax is None) and csv_path:
        import re
        base = os.path.basename(csv_path)
        m = re.search(r"multisine_(?P<fmin>[-+]?\d+(?:\.\d+)?)\-(?P<fmax>[-+]?\d+(?:\.\d+)?)Hz", base)
        if m:
            if fmin is None:
                fmin = _to_float_or_none(m.group('fmin'))
            if fmax is None:
                fmax = _to_float_or_none(m.group('fmax'))

    if fmin is None or fmax is None:
        return None
    if not (np.isfinite(fmin) and np.isfinite(fmax)):
        return None
    if fmin <= 0 or fmax <= fmin:
        return None
    return (float(fmin), float(fmax))

# ============================================================================
# ODrive Cleanup Helper
# ============================================================================

def cleanup_odrive(odrive_ctrl):
    """Best-effort ODrive cleanup: go to IDLE, set Position control, then disconnect.

    This is intentionally defensive: cleanup should never raise and block program exit.
    """
    if odrive_ctrl is None:
        return

    try:
        if getattr(odrive_ctrl, "connected", False):
            # Ensure we leave closed-loop (safe even if already idle).
            try:
                odrive_ctrl.exit_closed_loop()
            except Exception:
                pass

            # Clear GPIO1 analog mapping endpoint after identification/error.
            try:
                odrive_ctrl.odrv.config.gpio1_analog_mapping.endpoint = None
            except Exception:
                pass

            # Ensure final mode is Position (per safety requirement).
            try:
                odrive_ctrl.set_control_mode("Position")
            except Exception:
                pass

            # Restore step/dir mode after run completion/error.
            try:
                odrive_ctrl.set_enable_step_dir(True)
            except Exception:
                pass
    finally:
        try:
            odrive_ctrl.disconnect()
        except Exception:
            pass

# ============================================================================
# Configuration: Hard-coded variable lists for plotting
# ============================================================================

# Time series variables to plot (all in one window, synced x-axes)
TIME_SERIES_VARIABLES = [
    'torque_command',  # Active CSV torque value (Nm) used by firmware for PWM output
    'x_spindle',       # Computed spindle acceleration (m/s^2)
]

# ============================================================================
# Configuration: Bode Plot Settings
# ============================================================================
# 
# Bode plot configurations: List of 6 (input, output) pairs
# Each pair defines one Bode plot showing the transfer function from input to output
# Format: (input_variable_name, output_variable_name)
# 
# Available variables for inputs/outputs:
#   - torque_command: Active CSV torque value (Nm)
#   - x_spindle: Computed spindle acceleration (m/s^2)
#   - ODrive variables (if ODrive is connected): odrive_* variables
#
# To modify Bode plots, edit the list below:
# ============================================================================

BODE_PLOT_CONFIGS = [
    ('torque_command', 'x_spindle'),
]

# ============================================================================
# Configuration: Hardware ports (hard-coded)
# ============================================================================

CONTROLLINO_PORT = 'COM3'  # Hard-coded Controllino port (change as needed)

# ============================================================================
# Configuration: Acquisition limits
# ============================================================================

MAX_ACQ_SAMPLES = 16000  # Maximum acquisition samples (must match Arduino firmware)
MAX_CSV_SAMPLES = 2000  # Maximum CSV samples (must match Arduino firmware)

# ============================================================================
# Serial Communication Helper Class
# ============================================================================

class SerialHelper:
    """Helper class for serial communication with Controllino (non-threaded version)."""
    
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
    
    def send_command(self, cmd):
        """Send command to Controllino."""
        if not self.serial_port or not self.serial_port.is_open:
            print("Serial port not connected")
            return False
        
        with self.serial_lock:
            try:
                bytes_written = self.serial_port.write((cmd + '\n').encode())
                if bytes_written == 0:
                    print("Send command failed: No bytes written")
                    return False
                
                try:
                    self.serial_port.flush()
                except:
                    pass
                
                return True
            except Exception as e:
                print(f"Send command failed: {e}")
                return False
    
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
    
    def upload_csv(self, csv_path, *, max_torque=None):
        """Upload CSV file to Controllino.

        If max_torque is provided, the CSV second column is treated as a normalized
        multisine signal (clamped to ±1) and scaled to torque via:
          torque = max_torque * clamp(signal, -1, 1)
        The scaled torque values are streamed to the Controllino without modifying
        the source file on disk.
        """
        if not self.serial_port or not self.serial_port.is_open:
            return (False, "Serial port not connected")
        
        def clamp(x, lo, hi):
            return lo if x < lo else hi if x > hi else x

        try:
            # Read CSV file and count data lines
            data_lines = []
            with open(csv_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('#') or line.lower() == 'time_s,signal':
                        continue
                    # Parse data row as "time,signal"
                    if ',' not in line:
                        # Skip non-data lines (we expect 2 columns)
                        continue

                    time_str, signal_str = line.split(',', 1)
                    time_str = time_str.strip()
                    signal_str = signal_str.strip()
                    if not time_str or not signal_str:
                        continue

                    try:
                        time_val = float(time_str)
                        signal_val = float(signal_str)
                    except ValueError:
                        continue

                    if max_torque is None:
                        # Backwards compatible: send as-is (already torque)
                        data_lines.append(f"{time_val:.10e},{signal_val:.10e}")
                    else:
                        # Scale normalized multisine to torque (Nm)
                        s = clamp(signal_val, -1.0, 1.0)
                        torque_val = float(max_torque) * s
                        data_lines.append(f"{time_val:.10e},{torque_val:.10e}")
            
            if len(data_lines) == 0:
                return (False, "CSV file has no data lines")
            if len(data_lines) > MAX_CSV_SAMPLES:
                return (False, f"CSV has {len(data_lines)} samples; exceeds Controllino limit MAX_CSV_SAMPLES={MAX_CSV_SAMPLES}")
            
            with self.serial_lock:
                # Clear input buffer
                while self.serial_port.in_waiting > 0:
                    self.serial_port.read(self.serial_port.in_waiting)
                
                # Send UPLOAD_CSV command
                cmd = f"UPLOAD_CSV,{len(data_lines)}\n"
                try:
                    bytes_written = self.serial_port.write(cmd.encode())
                    if bytes_written == 0:
                        return (False, "Failed to send UPLOAD_CSV command")
                except Exception as e:
                    return (False, f"Failed to send command: {e}")
                
                try:
                    self.serial_port.flush()
                except:
                    pass
                
                # Wait for READY
                ready_received = False
                timeout_count = 0
                max_timeout = 400  # 2 seconds
                
                while timeout_count < max_timeout and not ready_received:
                    if self.serial_port.in_waiting > 0:
                        response = self.serial_port.readline().decode().strip()
                        if response == "READY":
                            ready_received = True
                        elif response == "" or response.startswith("DEBUG:") or response.startswith("ERROR:"):
                            continue
                        else:
                            return (False, f"Expected READY, got: {response}")
                    else:
                        timeout_count += 1
                        time.sleep(0.01)
                
                if not ready_received:
                    return (False, "Timeout waiting for READY")
                
                # Send CSV lines
                for i, line in enumerate(data_lines):
                    try:
                        self.serial_port.write((line + '\n').encode())
                    except Exception as e:
                        return (False, f"Failed to send line {i+1}: {e}")
                
                # Flush output
                try:
                    self.serial_port.flush()
                except:
                    pass
                
                # Wait for ACK/NACK
                ack_received = False
                timeout_count = 0
                max_timeout = 500  # 5 seconds
                
                while timeout_count < max_timeout and not ack_received:
                    if self.serial_port.in_waiting > 0:
                        response = self.serial_port.readline().decode().strip()
                        if response == "ACK: CSV loaded":
                            ack_received = True
                            return (True, f"CSV uploaded successfully ({len(data_lines)} lines)")
                        elif response.startswith("NACK:"):
                            error_msg = response[6:] if len(response) > 6 else "CSV load failed"
                            return (False, error_msg)
                        elif response.startswith("DEBUG:") or response.startswith("INFO:"):
                            continue
                        elif response.startswith("Hardware timer initialized"):
                            # Ignore timer initialization message
                            continue
                        else:
                            return (False, f"Unexpected response: {response}")
                    else:
                        timeout_count += 1
                        time.sleep(0.01)
                
                if not ack_received:
                    return (False, "Timeout waiting for ACK/NACK")
                
        except Exception as e:
            return (False, f"CSV upload failed: {e}")
    
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
# Simple Dialog Windows
# ============================================================================

class StartOutputDialog(QDialog):
    """Dialog with Start Output button."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start Output")
        self.setModal(True)
        layout = QVBoxLayout()
        
        label = QLabel("Click to start voltage output:")
        layout.addWidget(label)
        
        self.start_btn = QPushButton("Start Output")
        self.start_btn.clicked.connect(self.accept)
        layout.addWidget(self.start_btn)
        
        self.setLayout(layout)
        self.result = False

class ControlDialog(QDialog):
    """Dialog with Stop Output and Start Acquisition buttons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control")
        self.setModal(True)
        layout = QVBoxLayout()
        
        label = QLabel("Control options:")
        layout.addWidget(label)
        
        self.stop_output_btn = QPushButton("Stop Output")
        self.stop_output_btn.clicked.connect(self.on_stop_output)
        layout.addWidget(self.stop_output_btn)
        
        self.start_acq_btn = QPushButton("Start Acquisition")
        self.start_acq_btn.clicked.connect(self.on_start_acquisition)
        layout.addWidget(self.start_acq_btn)
        
        self.setLayout(layout)
        self.action = None  # 'stop_output' or 'start_acquisition'
    
    def on_stop_output(self):
        self.action = 'stop_output'
        self.accept()
    
    def on_start_acquisition(self):
        self.action = 'start_acquisition'
        self.accept()

class StopAcquisitionDialog(QDialog):
    """Dialog with Stop Acquisition button."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acquisition Running")
        self.setModal(True)
        layout = QVBoxLayout()
        
        label = QLabel("Acquisition in progress. Click to stop:")
        layout.addWidget(label)
        
        self.stop_btn = QPushButton("Stop Acquisition")
        self.stop_btn.clicked.connect(self.accept)
        layout.addWidget(self.stop_btn)
        
        self.setLayout(layout)
        self.stopped = False
    
    def closeEvent(self, event):
        """Handle window close - treat as stop."""
        self.stopped = True
        event.accept()

# ============================================================================
# Main Sequential Flow
# ============================================================================

def process_data(data_array, sample_rate, odrive_data=None):
    """Process acquired data including geometric calculations.
    
    Args:
        data_array: numpy array with shape (num_samples, 2)
                   Columns: [torque_command, x_spindle]
        sample_rate: Sample rate in Hz
        odrive_data: Optional dict with ODrive variables (if ODrive connected) - not used for Controllino
    """
    num_samples = data_array.shape[0]
    num_channels = data_array.shape[1]
    
    # Verify we have 2 channels: torque_command + x_spindle
    if num_channels != 2:
        raise ValueError(f"Expected 2 channels (torque_command, x_spindle), got {num_channels}")
    
    # Create time vector
    t = np.arange(num_samples) / sample_rate
    
    torque_command = data_array[:, 0]
    x_spindle = data_array[:, 1]

    # Remove DC component from x_spindle before any downstream plotting/calculation.
    x_spindle_dc = float(np.mean(x_spindle)) if num_samples > 0 else float("nan")
    if np.isfinite(x_spindle_dc):
        x_spindle = x_spindle - x_spindle_dc
    else:
        print("Warning: x_spindle DC offset is non-finite; skipping DC removal.")
    
    # Store processed data
    data = {
        'time': t,
        'torque_command': torque_command,
        'x_spindle': x_spindle,
        'x_spindle_dc': x_spindle_dc,
        'sample_rate': sample_rate
    }
    
    # Add ODrive data if available
    if odrive_data is not None:
        for key, value in odrive_data.items():
            if isinstance(value, np.ndarray) and len(value) == num_samples:
                data[f'odrive_{key}'] = value
    
    return data

def plot_time_series(data, variables_to_plot, active_figures=None):
    """Plot time series data - all plots in one window with synced x-axes.
    
    Args:
        data: Dictionary containing time series data
        variables_to_plot: List of variable names to plot
        active_figures: Optional list to track active figure references
    
    Returns:
        Figure object or None if no data to plot
    """
    # Filter variables that exist in data
    available_vars = [v for v in variables_to_plot if v in data]
    
    if len(available_vars) == 0:
        print("No variables available to plot")
        return None
    
    # Create figure with subplots
    num_plots = len(available_vars)
    fig, axes = plt.subplots(num_plots, 1, sharex=True, figsize=(12, 2 * num_plots))
    
    if num_plots == 1:
        axes = [axes]
    
    for i, var_name in enumerate(available_vars):
        axes[i].plot(data['time'], data[var_name])
        axes[i].set_ylabel(var_name)
        axes[i].grid(True)
    
    axes[-1].set_xlabel('Time (s)')
    fig.suptitle('Time Series Data', fontsize=14)
    fig.tight_layout()
    
    # Add close event handler to track when window is closed
    if active_figures is not None:
        active_figures.append(fig)
        
        def on_close(event):
            """Handle figure close event."""
            if fig in active_figures:
                active_figures.remove(fig)
        
        fig.canvas.mpl_connect('close_event', on_close)
    
    plt.show(block=False)
    return fig

def plot_bode_plots(data, bode_configs, active_figures=None, freq_band_hz=None):
    """Plot 6 Bode plots in 2x3 grid.
    
    Args:
        data: Dictionary containing time series data
        bode_configs: List of (input_var, output_var) tuples for Bode plots
        active_figures: Optional list to track active figure references
        freq_band_hz: Optional (fmin, fmax) in Hz to limit plots to the excited band
    
    Returns:
        Figure object or None if no valid configs
    """
    # Filter configs where both input and output exist
    valid_configs = []
    for input_var, output_var in bode_configs:
        if input_var in data and output_var in data:
            valid_configs.append((input_var, output_var))
        else:
            print(f"Warning: Skipping Bode plot ({input_var} -> {output_var}): variable not found")
    
    if len(valid_configs) == 0:
        print("No valid Bode plot configurations")
        return None
    
    # Create grid sized to number of requested plots (max 6).
    num_plots = min(len(valid_configs), 6)
    cols = min(3, num_plots)
    rows = int(np.ceil(num_plots / cols))

    # Two sub-rows per plot (magnitude + phase).
    col_width = 5.0
    row_pair_height = 3.2
    fig_w = max(8.0, col_width * cols)
    fig_h = max(5.0, row_pair_height * rows * 2)
    fig, axes = plt.subplots(rows * 2, cols, figsize=(fig_w, fig_h), squeeze=False)
    fig.suptitle('Bode Plots', fontsize=14)
    
    sample_rate = data['sample_rate']
    if freq_band_hz is not None:
        try:
            fmin_band = float(freq_band_hz[0])
            fmax_band = float(freq_band_hz[1])
            if not (np.isfinite(fmin_band) and np.isfinite(fmax_band) and fmin_band > 0 and fmax_band > fmin_band):
                fmin_band = None
                fmax_band = None
        except Exception:
            fmin_band = None
            fmax_band = None
    else:
        fmin_band = None
        fmax_band = None
    
    for idx, (input_var, output_var) in enumerate(valid_configs[:num_plots]):
        row = idx // cols
        col = idx % cols
        
        input_signal = data[input_var]
        output_signal = data[output_var]
        
        # Compute transfer function using Welch's method
        f, Pxy = signal.csd(output_signal, input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
        f, Pxx = signal.welch(input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
        
        # Calculate transfer function H = Pxy / Pxx
        H = Pxy / (Pxx + 1e-10)

        # Limit to multisine excited band (if provided)
        if fmin_band is not None and fmax_band is not None:
            band_mask = (f >= fmin_band) & (f <= fmax_band)
            # Keep at least a few points; otherwise skip masking but still set xlim.
            if np.count_nonzero(band_mask) >= 3:
                f_plot = f[band_mask]
                H_plot = H[band_mask]
            else:
                f_plot = f
                H_plot = H
        else:
            f_plot = f
            H_plot = H
        
        # Magnitude and phase
        magnitude = np.abs(H_plot)
        phase = np.angle(H_plot)
        phase = np.unwrap(phase) * 180 / np.pi  # Unwrap and convert to degrees
        
        # Magnitude plot (top row)
        ax_mag = axes[row * 2, col]
        ax_mag.loglog(f_plot, magnitude)
        ax_mag.set_ylabel(f'{output_var} / {input_var}')
        ax_mag.set_title(f'{output_var} / {input_var}')
        ax_mag.grid(True)
        if fmin_band is not None and fmax_band is not None:
            ax_mag.set_xlim(fmin_band, fmax_band)
        
        # Phase plot (bottom row)
        ax_phase = axes[row * 2 + 1, col]
        ax_phase.semilogx(f_plot, phase)
        ax_phase.set_xlabel('Frequency (Hz)')
        ax_phase.set_ylabel('Phase (degrees)')
        ax_phase.grid(True)
        if fmin_band is not None and fmax_band is not None:
            ax_phase.set_xlim(fmin_band, fmax_band)
    
    # Hide unused subplots
    for idx in range(num_plots, rows * cols):
        row = idx // cols
        col = idx % cols
        axes[row * 2, col].set_visible(False)
        axes[row * 2 + 1, col].set_visible(False)
    
    fig.tight_layout()
    
    # Add close event handler to track when window is closed
    if active_figures is not None:
        active_figures.append(fig)
        
        def on_close(event):
            """Handle figure close event."""
            if fig in active_figures:
                active_figures.remove(fig)
        
        fig.canvas.mpl_connect('close_event', on_close)
    
    plt.show(block=False)
    return fig

def main():
    """Main sequential flow."""
    print("=" * 60)
    print("Sequential Phase 1 Data Acquisition System")
    print("=" * 60)

    # Runtime mode prompt: default to Position for safety.
    while True:
        control_mode_prompt = input("Select ODrive control mode [p/t] (default=p): ").strip().lower()
        if control_mode_prompt in ("", "p", "t"):
            break
        print("Invalid input. Enter 'p' for Position, 't' for Torque, or press Enter for default.")

    selected_control_mode = "Torque" if control_mode_prompt == "t" else "Position"
    print(f"Selected ODrive control mode: {selected_control_mode}")
    
    # Initialize Qt application (needed for dialogs and matplotlib)
    app = QApplication(sys.argv)
    
    try:
        # Step 1: Connect to Controllino (hard-coded COM10)
        print(f"\nStep 1: Connecting to Controllino on {CONTROLLINO_PORT}...")
        serial_helper = SerialHelper(CONTROLLINO_PORT)
        if not serial_helper.connect():
            print("Failed to connect to Controllino. Exiting.")
            return 1
        print("Controllino connected successfully.")
        
        # Step 2: Connect to ODrive automatically
        print("\nStep 2: ODrive connection")
        odrive_connected = False
        odrive_ctrl = None
        print("Connecting to ODrive via USB...")
        odrive_ctrl = ODriveController()
        if odrive_ctrl.connect():
            odrive_connected = True
            print("ODrive connected successfully.")

            # Keep step/dir disabled while running identification so torque path works.
            if not odrive_ctrl.set_enable_step_dir(False):
                print("WARNING: Failed to disable ODrive step/dir mode at startup.")

            # Apply user-selected control mode from startup prompt.
            if not odrive_ctrl.set_control_mode(selected_control_mode):
                print(f"WARNING: Failed to set control mode to {selected_control_mode}.")

            # Configure ODrive for PWM->GPIO1 analog mapping (no CAN)
            if not odrive_ctrl.configure_gpio1_analog_torque_mapping(
                analog_min=-3.874,
                analog_max=2.0,
                enable_gpio_num=7,
                control_mode=selected_control_mode,
            ):
                print("WARNING: Failed to configure ODrive GPIO1 analog mapping. Continuing anyway.")
            else:
                print("ODrive configured for PWM->GPIO1 analog torque mapping.")
        else:
            print("ODrive connection failed. Continuing without ODrive.")
        
        # Step 3: Select CSV file
        print("\nStep 3: Select CSV multisine file")
        csv_path, _ = QFileDialog.getOpenFileName(None, "Select CSV Multisine File", "", "CSV Files (*.csv)")
        if not csv_path:
            print("No CSV file selected. Exiting.")
            serial_helper.disconnect()
            if odrive_connected:
                cleanup_odrive(odrive_ctrl)
            return 1
        
        print(f"CSV file selected: {os.path.basename(csv_path)}")
        multisine_band_hz = _parse_multisine_freq_band_from_csv(csv_path)
        if multisine_band_hz is not None:
            print(f"Detected multisine excited band: {multisine_band_hz[0]:.6g}–{multisine_band_hz[1]:.6g} Hz")
        else:
            print("Warning: Could not detect multisine frequency band from CSV metadata; Bode plots will use full frequency range.")

        # Step 3b: Prompt for max torque scaling (Nm)
        while True:
            try:
                max_torque_str = input("Enter max output torque (Nm, default=2.0): ").strip()
                if not max_torque_str:
                    max_torque = 2.0
                else:
                    max_torque = float(max_torque_str)
                if max_torque > 0:
                    break
                print("Max torque must be > 0. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        print(f"Using max output torque: {max_torque:.6g} Nm (multisine is clamped to ±1)")
        
        # Parse CSV file to extract sample rate (needed for ODrive configuration)
        # Note: Voltage values will be read from Controllino acquisition data, not from CSV
        sample_rate = None
        try:
            with open(csv_path, 'r') as f:
                lines = f.readlines()
            
            time_values = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    # Try to extract sample rate from metadata
                    if 'fs:' in line:
                        try:
                            fs_part = line.split('fs:')[1].split('Hz')[0].strip()
                            fs_value = float(fs_part)
                            if fs_value > 0:
                                sample_rate = fs_value
                        except (ValueError, IndexError):
                            pass
                    continue
                
                if line.lower() == 'time_s,signal':
                    continue
                
                # Extract time values to calculate sample rate if not in metadata
                if ',' in line and sample_rate is None:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        try:
                            time_val = float(parts[0].strip())
                            time_values.append(time_val)
                            # Calculate sample rate from first two time values
                            if len(time_values) == 2:
                                sample_period = time_values[1] - time_values[0]
                                if sample_period > 0:
                                    sample_rate = 1.0 / sample_period
                                    break  # Got what we need
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Warning: Could not parse CSV file: {e}")
        
        if sample_rate is None:
            print("Warning: Could not determine sample rate from CSV. Using default 1000 Hz.")
            sample_rate = 1000.0
        
        # Upload CSV to Controllino
        print("Uploading CSV to Controllino...")
        success, message = serial_helper.upload_csv(csv_path, max_torque=max_torque)
        if not success:
            print(f"CSV upload failed: {message}")
            serial_helper.disconnect()
            if odrive_connected:
                cleanup_odrive(odrive_ctrl)
            return 1
        print(f"CSV uploaded: {message}")
        
        # Step 4: Optional test output
        print("\nStep 4: Optional test output")
        test_response = input("Test PWM output first? (y/n, default=n): ").strip().lower()
        if test_response == 'y':
            # Get test duration once
            while True:
                try:
                    test_duration_str = input("Enter test output duration (seconds): ").strip()
                    test_duration = float(test_duration_str)
                    if test_duration > 0:
                        break
                    else:
                        print("Duration must be positive. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            # Repeat loop for test output
            while True:
                # Enable ODrive closed-loop control
                if odrive_connected:
                    print("Enabling ODrive closed-loop control...")
                    if not odrive_ctrl.enter_closed_loop():
                        print("Warning: Failed to enter closed-loop control. Continuing anyway.")
                    else:
                        print("ODrive entered closed-loop control state.")

                # Wait 0.5s to ensure ODrive is ready before torque commands start
                time.sleep(0.5)

                print(f"Starting test output for {test_duration} seconds...")
                success, response, error = serial_helper.send_command_and_wait_response(
                    f"START_OUTPUT,{test_duration}", "ACK: Output started", timeout=2
                )
                if not success:
                    print(f"Failed to start test output: {error}")
                    if odrive_connected:
                        cleanup_odrive(odrive_ctrl)
                    serial_helper.disconnect()
                    return 1
                print("Test output started. Waiting for completion...")

                # Wait for Controllino serial message that output has finished
                # Controllino will set output to zero at end of duration and send "ACK: Output complete"
                output_complete = False
                timeout = 0
                max_timeout = int((test_duration + 5) * 10)  # Wait a bit longer than duration (0.1s increments)

                while timeout < max_timeout:
                    if serial_helper.serial_port and serial_helper.serial_port.is_open:
                        if serial_helper.serial_port.in_waiting > 0:
                            line = serial_helper.serial_port.readline().decode().strip()
                            if line == "ACK: Output complete":
                                output_complete = True
                                print("Output completed. PWM output set to zero.")
                                # Best-effort safety: force Controllino back to 0 Nm idle duty.
                                # (Firmware implements STOP_OUTPUT; this is safe even if already idle.)
                                serial_helper.send_command("STOP_OUTPUT")
                                time.sleep(0.05)
                                break
                            elif line.startswith("ERROR:"):
                                print(f"Error received: {line}")
                                break
                    time.sleep(0.1)
                    timeout += 1
                    # Progress indicator
                    if timeout % 10 == 0:
                        elapsed = timeout * 0.1
                        print(f"  Elapsed: {elapsed:.1f}s / Expected: {test_duration:.1f}s")

                if not output_complete:
                    print("Warning: Output completion not confirmed. Continuing anyway...")
                    # Best-effort safety: request output stop anyway.
                    serial_helper.send_command("STOP_OUTPUT")
                    time.sleep(0.05)

                # Disable ODrive closed-loop control
                if odrive_connected:
                    print("Disabling ODrive closed-loop control...")
                    odrive_ctrl.exit_closed_loop()

                    # Always ask if test should be repeated
                    while True:
                        repeat_response = input("Repeat test with same duration? (y/n, default=n): ").strip().lower()
                        if repeat_response == 'y':
                            break  # Continue repeat loop
                        elif repeat_response == 'n' or repeat_response == '':
                            break  # Exit repeat loop
                        else:
                            print("Please enter 'y' or 'n'.")

                    if repeat_response != 'y':
                        break  # Exit repeat loop
        
        # Step 5: Acquisition parameters
        print("\nStep 5: Acquisition parameters")
        while True:
            try:
                duration_str = input("Enter acquisition duration (seconds): ").strip()
                duration = float(duration_str)
                if duration > 0:
                    break
                else:
                    print("Duration must be positive. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        while True:
            try:
                delay_str = input("Enter acquisition start delay (seconds, default=0.0): ").strip()
                if not delay_str:
                    delay = 0.0
                    break
                delay = float(delay_str)
                if delay >= 0:
                    break
                else:
                    print("Delay must be non-negative. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        print(f"Acquisition duration: {duration} seconds")
        print(f"Acquisition start delay: {delay} seconds")
        
        # Check if duration exceeds maximum and adjust if necessary
        max_duration = MAX_ACQ_SAMPLES / sample_rate
        if duration > max_duration:
            print(f"\nWarning: Requested acquisition duration ({duration:.2f} s) exceeds maximum possible duration ({max_duration:.2f} s).")
            print(f"Acquisition will proceed with maximum duration: {max_duration:.2f} s")
            duration = max_duration
        
        # Step 6: Start identification directly (no dialog)
        print("\nStep 6: Start identification")
        
        # Enable ODrive closed-loop control
        if odrive_connected:
            print("Enabling ODrive closed-loop control...")
            if not odrive_ctrl.enter_closed_loop():
                print("Warning: Failed to enter closed-loop control. Continuing anyway.")
            else:
                print("ODrive entered closed-loop control state.")
        
        # Wait 0.5s to ensure ODrive is ready before starting identification
        time.sleep(0.5)
        
        print("Starting identification (torque output + acquisition)...")
        success, response, error = serial_helper.send_command_and_wait_response(
            f"START_IDENTIFICATION,{duration},{delay}", "ACK: Identification started", timeout=2
        )
        if not success:
            print(f"Failed to start identification: {error}")
            if odrive_connected:
                odrive_ctrl.exit_closed_loop()
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        print("Identification started. Serial communication will be blocked during operation.")
        
        # Wait as long as delay time (output is running during this time)
        if delay > 0:
            print(f"Waiting for delay period ({delay} seconds)...")
            time.sleep(delay)
        
        # Wait for acquisition to complete
        # Controllino will set output to zero after acquisition and send "ACK: Acquisition complete"
        print(f"\nWaiting for acquisition to complete (duration: {duration} seconds)...")
        acquisition_complete = False
        timeout = 0
        max_timeout = int((duration + 5) * 10)  # Wait a bit longer than acquisition duration (0.1s increments)
        
        while timeout < max_timeout:
            if serial_helper.serial_port and serial_helper.serial_port.is_open:
                if serial_helper.serial_port.in_waiting > 0:
                    line = serial_helper.serial_port.readline().decode().strip()
                    if line == "ACK: Acquisition complete":
                        acquisition_complete = True
                        print("Acquisition completed. PWM output set to zero.")
                        # Best-effort safety: force Controllino back to 0 Nm idle duty.
                        serial_helper.send_command("STOP_OUTPUT")
                        time.sleep(0.05)
                        break
                    elif line.startswith("ERROR:"):
                        print(f"Error received: {line}")
                        break
            time.sleep(0.1)
            timeout += 1
            
            # Progress indicator
            if timeout % 10 == 0:
                elapsed = timeout * 0.1
                print(f"  Elapsed: {elapsed:.1f}s / Expected: {duration:.1f}s")
        
        if not acquisition_complete:
            print("Warning: Acquisition completion not confirmed. Continuing anyway...")
            # Best-effort safety: request output stop anyway.
            serial_helper.send_command("STOP_OUTPUT")
            time.sleep(0.05)
        
        # Stop ODrive closed-loop control
        if odrive_connected:
            print("\nDisabling ODrive closed-loop control...")
            odrive_ctrl.exit_closed_loop()
            # Restore GPIO1 analog mapping to a safe default (no endpoint)
            try:
                odrive_ctrl.odrv.config.gpio1_analog_mapping.endpoint = None
            except Exception:
                pass
            odrive_ctrl.set_control_mode('Position')
            odrive_ctrl.set_enable_step_dir(True)
        
        # Step 7: Retrieve data
        print("\nStep 9: Retrieving data from Controllino...")
        data_result = serial_helper.get_data()
        if data_result is None:
            print("Failed to retrieve data from Controllino.")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        
        print(f"Retrieved {len(data_result['samples'])} samples at {data_result['sample_rate']:.1f} Hz")
        
        # Verify data format (should be 2 channels: torque_command, x_spindle)
        if len(data_result['samples']) > 0:
            num_channels = len(data_result['samples'][0])
            if num_channels != 2:
                print(f"Warning: Expected 2 channels, got {num_channels}")
        
        # Note: ODrive data is not retrieved during operation to avoid interrupting torque signals
        
        # Step 8: Process data
        print("\nStep 10: Processing data...")
        processed_data = process_data(
            data_result['samples'],
            data_result['sample_rate'],
            odrive_data=None  # No ODrive data retrieved
        )

        x_spindle_dc = processed_data.get('x_spindle_dc', None)
        if x_spindle_dc is not None and np.isfinite(x_spindle_dc):
            print(f"Removed DC from x_spindle: {x_spindle_dc:.6g} m/s^2")
        else:
            print("Warning: x_spindle DC value unavailable; no DC value printed.")
        
        # Step 9: Display time series plots
        print("\nStep 11: Displaying time series plots...")
        
        # Track active figures for close detection
        active_figures = []
        
        time_series_fig = plot_time_series(processed_data, TIME_SERIES_VARIABLES, active_figures)
        
        # Step 10: Display Bode plots
        print("\nStep 12: Displaying Bode plots...")
        bode_fig = plot_bode_plots(processed_data, BODE_PLOT_CONFIGS, active_figures, freq_band_hz=multisine_band_hz)
        
        print("\n" + "=" * 60)
        print("Acquisition complete!")
        print("=" * 60)
        
        # Cleanup serial and ODrive connections
        # Best-effort safety: force Controllino back to 0 Nm idle duty before disconnect.
        serial_helper.send_command("STOP_OUTPUT")
        time.sleep(0.05)
        serial_helper.disconnect()
        if odrive_connected:
            odrive_ctrl.disconnect()
        
        # Keep application running to show plots
        print("\nPlots are displayed. Close plot windows to exit.")
        
        # If no figures were created, exit immediately
        if len(active_figures) == 0:
            print("No plots to display. Exiting.")
            return 0
        
        # Set up mechanism to detect when all windows are closed
        def check_figures_closed():
            """Check if all figures are closed and exit if so."""
            # Filter out any figures that are no longer valid
            valid_figures = [fig for fig in active_figures if plt.fignum_exists(fig.number)]
            active_figures[:] = valid_figures
            
            if len(active_figures) == 0:
                # All figures closed - clean up and exit
                plt.close('all')
                app.quit()
        
        # Use QTimer to periodically check if all figures are closed
        check_timer = QTimer()
        check_timer.timeout.connect(check_figures_closed)
        check_timer.start(500)  # Check every 500ms
        
        # Run Qt event loop
        exit_code = app.exec_()
        
        # Cleanup: ensure all figures are closed
        plt.close('all')
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up...")
        # Clean up any open matplotlib figures
        plt.close('all')
        if 'serial_helper' in locals():
            # Stop acquisition first, then output
            serial_helper.send_command("STOP_ACQUISITION")
            time.sleep(0.2)
            serial_helper.send_command("STOP_OUTPUT")
            time.sleep(0.2)
            serial_helper.disconnect()
        if 'odrive_connected' in locals() and odrive_connected and 'odrive_ctrl' in locals():
            odrive_ctrl.disconnect()
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        # Clean up any open matplotlib figures
        plt.close('all')
        if 'serial_helper' in locals():
            # Try to stop acquisition and output before disconnecting
            try:
                serial_helper.send_command("STOP_ACQUISITION")
                time.sleep(0.2)
                serial_helper.send_command("STOP_OUTPUT")
                time.sleep(0.2)
            except:
                pass
            serial_helper.disconnect()
        if 'odrive_connected' in locals() and odrive_connected and 'odrive_ctrl' in locals():
            odrive_ctrl.disconnect()
        return 1

if __name__ == "__main__":
    sys.exit(main())

