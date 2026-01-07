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
# Configuration: Hard-coded variable lists for plotting
# ============================================================================

# Time series variables to plot (all in one window, synced x-axes)
TIME_SERIES_VARIABLES = [
    'output_voltage',  # Voltage output (multisine) as output by Controllino
    'A0', 'A1', 'A2', 'A3', 'A4', 'A5',  # Analog input voltages
    'acc0', 'acc1', 'acc2', 'acc3', 'acc4', 'acc5',  # Accelerations (calculated)
    'x', 'y', 'theta_x', 'theta_y',  # Geometric calculations
    # ODrive variables (will be added if ODrive is connected)
    'odrive_Axis_pos_estimate',
    'odrive_Axis_vel_estimate',
    'odrive_Motor_torque_estimate',
    'odrive_Rs485Encoder_raw32',
    'odrive_EncoderEstimator_pos_estimate',
    'odrive_EncoderEstimator_vel_estimate',
    'odrive_Controller_input_pos',
    'odrive_Controller_input_vel',
    'odrive_Controller_input_torque',
    'odrive_Controller_pos_setpoint',
    'odrive_Controller_vel_setpoint',
    'odrive_Controller_torque_setpoint',
    'odrive_Controller_vel_integrator_torque',
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
#   - output_voltage: Voltage output (multisine) as recorded by Controllino
#   - A0, A1, A2, A3, A4, A5: Analog input voltages
#   - acc0, acc1, acc2, acc3, acc4, acc5: Accelerations (calculated)
#   - x, y, theta_x, theta_y: Geometric calculations
#   - ODrive variables (if ODrive is connected): odrive_* variables
#
# To modify Bode plots, edit the list below:
# ============================================================================

BODE_PLOT_CONFIGS = [
    ('output_voltage', 'A0'),
    ('output_voltage', 'theta_y'),
    ('output_voltage', 'x'),
    ('output_voltage', 'y'),
    ('A0', 'theta_x'),
    ('A0', 'x'),
]

# ============================================================================
# Configuration: Hardware ports (hard-coded)
# ============================================================================

CONTROLLINO_PORT = 'COM3'  # Hard-coded Controllino port (change as needed)

# ============================================================================
# Geometric calculation constants
# ============================================================================

L1 = 0.02  # (m) Length parameter 1 - from tool tip to impact point
L2 = 0.078  # (m) Length parameter 2 - from impact point to bottom accelerometers
L3 = 0.160  # (m) Length parameter 3 - from bottom to top accelerometers
ALPHA = 20.123 * np.pi / 180  # Angle in radians (20 degrees)
R_A = 5 * 9.81 / 10     # m/s²/V accelerometer sensitivity

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
    
    def upload_csv(self, csv_path):
        """Upload CSV file to Controllino."""
        if not self.serial_port or not self.serial_port.is_open:
            return (False, "Serial port not connected")
        
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
                    data_lines.append(line)
            
            if len(data_lines) == 0:
                return (False, "CSV file has no data lines")
            
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
                max_timeout = 200  # 2 seconds
                
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
        data_array: numpy array with shape (num_samples, 8)
                   Columns: [A0, A1, A2, A3, A4, A5, torque_command, position_feedback]
        sample_rate: Sample rate in Hz
        odrive_data: Optional dict with ODrive variables (if ODrive connected) - not used for Controllino
    """
    num_samples = data_array.shape[0]
    num_channels = data_array.shape[1]
    
    # Verify we have 8 channels (6 inputs + torque_command + position_feedback)
    if num_channels != 8:
        raise ValueError(f"Expected 8 channels (6 inputs + torque_command + position_feedback), got {num_channels}")
    
    # Create time vector
    t = np.arange(num_samples) / sample_rate
    
    # Extract input channels (A0-A5) - indices 0-5
    A0 = data_array[:, 0]
    A1 = data_array[:, 1]
    A2 = data_array[:, 2]
    A3 = data_array[:, 3]
    A4 = data_array[:, 4]
    A5 = data_array[:, 5]
    
    # Extract torque command - index 6 (sent to ODrive via CAN)
    torque_command = data_array[:, 6]
    
    # Extract position feedback - index 7 (always 0 for Controllino - not retrieved from ODrive)
    position_feedback = data_array[:, 7]
    
    # For compatibility with existing code, also store as output_voltage
    # (though it's actually torque command)
    output_voltage = torque_command
    
    # Calculate accelerations (acc0-acc5) - these are the raw analog inputs
    # In this system, the analog inputs ARE the accelerometer readings
    acc0 = A0
    acc1 = A1
    acc2 = A2
    acc3 = A3
    acc4 = A4
    acc5 = A5
    
    # Calculate theta_x and theta_y
    theta_x = -(A0 + A1 - A2 - A3) / np.sin(ALPHA) / (2 * L3)
    theta_y = -(A0 - A1 - A2 + A3) / np.cos(ALPHA) / (2 * L3)
    
    # Calculate x and y accelerations
    x = (-(A0 - A1 + A2 - A3) / np.cos(ALPHA) / 4 -
         theta_y * (L1 + L2 + L3 / 2) - A4) * R_A
    y = ((A0 + A1 + A2 + A3) / np.sin(ALPHA) / 4 +
         theta_x * (L1 + L2 + L3 / 2) - A5) * R_A
    
    # Store processed data
    data = {
        'time': t,
        'output_voltage': output_voltage,  # For compatibility (actually torque command)
        'torque_command': torque_command,
        'position_feedback': position_feedback,
        'A0': A0,
        'A1': A1,
        'A2': A2,
        'A3': A3,
        'A4': A4,
        'A5': A5,
        'acc0': acc0,
        'acc1': acc1,
        'acc2': acc2,
        'acc3': acc3,
        'acc4': acc4,
        'acc5': acc5,
        'theta_x': theta_x,
        'theta_y': theta_y,
        'x': x,
        'y': y,
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

def plot_bode_plots(data, bode_configs, active_figures=None):
    """Plot 6 Bode plots in 2x3 grid.
    
    Args:
        data: Dictionary containing time series data
        bode_configs: List of (input_var, output_var) tuples for Bode plots
        active_figures: Optional list to track active figure references
    
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
    
    # Create 2x3 grid (or adjust if fewer than 6)
    num_plots = min(len(valid_configs), 6)
    rows = 2
    cols = 3
    
    fig, axes = plt.subplots(rows * 2, cols, figsize=(15, 10))  # 2 rows per plot (magnitude + phase)
    fig.suptitle('Bode Plots', fontsize=14)
    
    sample_rate = data['sample_rate']
    
    for idx, (input_var, output_var) in enumerate(valid_configs[:num_plots]):
        if idx >= 6:
            break
        
        row = idx // cols
        col = idx % cols
        
        input_signal = data[input_var]
        output_signal = data[output_var]
        
        # Compute transfer function using Welch's method
        f, Pxy = signal.csd(output_signal, input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
        f, Pxx = signal.welch(input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
        
        # Calculate transfer function H = Pxy / Pxx
        H = Pxy / (Pxx + 1e-10)
        
        # Magnitude and phase
        magnitude = np.abs(H)
        phase = np.angle(H)
        phase = np.unwrap(phase) * 180 / np.pi  # Unwrap and convert to degrees
        
        # Magnitude plot (top row)
        ax_mag = axes[row * 2, col]
        ax_mag.loglog(f, magnitude)
        ax_mag.set_ylabel(f'{output_var} / {input_var}')
        ax_mag.set_title(f'{output_var} / {input_var}')
        ax_mag.grid(True)
        
        # Phase plot (bottom row)
        ax_phase = axes[row * 2 + 1, col]
        ax_phase.semilogx(f, phase)
        ax_phase.set_xlabel('Frequency (Hz)')
        ax_phase.set_ylabel('Phase (degrees)')
        ax_phase.grid(True)
    
    # Hide unused subplots
    for idx in range(num_plots, 6):
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
            # Configure ODrive for torque control via CAN
            odrive_ctrl.set_control_mode('Torque')
            # Enter closed-loop control state (will be done before starting torque)
            print("ODrive configured for torque control via CAN.")
        else:
            print("ODrive connection failed. Continuing without ODrive.")
        
        # Step 3: Select CSV file
        print("\nStep 3: Select CSV multisine file")
        csv_path, _ = QFileDialog.getOpenFileName(None, "Select CSV Multisine File", "", "CSV Files (*.csv)")
        if not csv_path:
            print("No CSV file selected. Exiting.")
            serial_helper.disconnect()
            return 1
        
        print(f"CSV file selected: {os.path.basename(csv_path)}")
        
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
        success, message = serial_helper.upload_csv(csv_path)
        if not success:
            print(f"CSV upload failed: {message}")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        print(f"CSV uploaded: {message}")
        
        # Step 4: Get acquisition parameters
        print("\nStep 4: Acquisition parameters")
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
        
        # Step 5 (Optional): Test output first
        print("\nStep 5: Optional test output")
        test_response = input("Test torque output first? (y/n, default=n): ").strip().lower()
        if test_response == 'y':
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
            
            print(f"Starting test output for {test_duration} seconds...")
            success, response, error = serial_helper.send_command_and_wait_response(
                f"START_OUTPUT,{test_duration}", "ACK: Output started", timeout=2
            )
            if not success:
                print(f"Failed to start test output: {error}")
                serial_helper.disconnect()
                if odrive_connected:
                    odrive_ctrl.disconnect()
                return 1
            print("Test output started. Waiting for completion...")
            
            # Wait for test output to complete (serial will be blocked, then unblocked)
            time.sleep(test_duration + 1)  # Wait a bit longer to ensure completion
            print("Test output completed.")
        
        # Step 6: Enter ODrive closed-loop control (before starting identification)
        if odrive_connected:
            print("\nStep 6: Entering ODrive closed-loop control...")
            if not odrive_ctrl.enter_closed_loop():
                print("Warning: Failed to enter closed-loop control. Continuing anyway.")
            else:
                print("ODrive entered closed-loop control state.")
            time.sleep(0.5)  # Give ODrive time to transition
        
        # Step 7: Start identification (torque output + acquisition)
        print("\nStep 7: Start identification")
        start_dialog = StartOutputDialog()
        if start_dialog.exec_() != QDialog.Accepted:
            print("Start identification cancelled. Exiting.")
            if odrive_connected:
                odrive_ctrl.exit_closed_loop()
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        
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
        
        # Step 8: Wait for acquisition completion
        print("\nStep 8: Waiting for acquisition to complete...")
        print("Note: Serial communication is blocked during operation.")
        print(f"Estimated completion time: {duration + delay + 1} seconds")
        
        # Calculate estimated completion time
        estimated_completion = duration + delay + 1
        acquisition_complete = False
        
        # Wait for serial to become available again (acquisition completes automatically)
        print("Waiting for serial communication to resume...")
        timeout = 0
        max_timeout = int((estimated_completion + 5) * 10)  # Wait a bit longer than estimated
        
        while timeout < max_timeout:
            if serial_helper.serial_port and serial_helper.serial_port.is_open:
                if serial_helper.serial_port.in_waiting > 0:
                    line = serial_helper.serial_port.readline().decode().strip()
                    if line == "ACK: Acquisition complete":
                        acquisition_complete = True
                        print("Acquisition completed successfully.")
                        break
                    elif line.startswith("ERROR:"):
                        print(f"Error received: {line}")
                        break
            time.sleep(0.1)
            timeout += 1
            
            # Progress indicator
            if timeout % 10 == 0:
                elapsed = timeout * 0.1
                print(f"  Elapsed: {elapsed:.1f}s / Estimated: {estimated_completion:.1f}s")
        
        if not acquisition_complete:
            print("Warning: Acquisition completion not confirmed. Continuing anyway...")
        
        # Exit ODrive closed-loop control
        if odrive_connected:
            print("\nExiting ODrive closed-loop control...")
            odrive_ctrl.exit_closed_loop()
            time.sleep(0.5)
        
        # Step 9: Retrieve data
        print("\nStep 9: Retrieving data from Controllino...")
        data_result = serial_helper.get_data()
        if data_result is None:
            print("Failed to retrieve data from Controllino.")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        
        print(f"Retrieved {len(data_result['samples'])} samples at {data_result['sample_rate']:.1f} Hz")
        
        # Verify data format (should be 8 channels: A0-A5, torque_command, position_feedback)
        if len(data_result['samples']) > 0:
            num_channels = len(data_result['samples'][0])
            if num_channels != 8:
                print(f"Warning: Expected 8 channels, got {num_channels}")
        
        # Note: ODrive data is not retrieved during operation to avoid interrupting torque signals
        # Position feedback in data will be zeros
        
        # Step 10: Process data
        print("\nStep 10: Processing data...")
        processed_data = process_data(
            data_result['samples'],
            data_result['sample_rate'],
            odrive_data=None  # No ODrive data retrieved
        )
        
        # Step 11: Display time series plots
        print("\nStep 11: Displaying time series plots...")
        
        # Track active figures for close detection
        active_figures = []
        
        time_series_fig = plot_time_series(processed_data, TIME_SERIES_VARIABLES, active_figures)
        
        # Step 12: Display Bode plots
        print("\nStep 12: Displaying Bode plots...")
        bode_fig = plot_bode_plots(processed_data, BODE_PLOT_CONFIGS, active_figures)
        
        print("\n" + "=" * 60)
        print("Acquisition complete!")
        print("=" * 60)
        
        # Cleanup serial and ODrive connections
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

