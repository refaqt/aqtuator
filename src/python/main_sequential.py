"""
Sequential Phase 1 Control Application

Simplified sequential workflow for synchronized data acquisition and motor control system.
Integrates Arduino Giga R1 WiFi and ODrive S1.
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
    'output_voltage',  # Voltage output (multisine) as output by Arduino
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
#   - output_voltage: Voltage output (multisine) as recorded by Arduino
#   - A0, A1, A2, A3, A4, A5: Analog input voltages
#   - acc0, acc1, acc2, acc3, acc4, acc5: Accelerations (calculated)
#   - x, y, theta_x, theta_y: Geometric calculations
#   - ODrive variables (if ODrive is connected): odrive_* variables
#
# To modify Bode plots, edit the list below:
# ============================================================================

BODE_PLOT_CONFIGS = [
    ('output_voltage', 'theta_x'),
    ('output_voltage', 'theta_y'),
    ('output_voltage', 'x'),
    ('output_voltage', 'y'),
    ('A0', 'theta_x'),
    ('A0', 'x'),
]

# ============================================================================
# Configuration: Hardware ports (hard-coded)
# ============================================================================

ARDUINO_PORT = 'COM10'  # Hard-coded Arduino port

# ============================================================================
# Geometric calculation constants
# ============================================================================

L1 = 0.01    # m
L2 = 0.05    # m
L3 = 0.2     # m
ALPHA = np.deg2rad(20)  # Convert to radians
R_A = 5 * 9.81 / 10     # m/s²/V accelerometer sensitivity

# ============================================================================
# Serial Communication Helper Class
# ============================================================================

class SerialHelper:
    """Helper class for serial communication with Arduino (non-threaded version)."""
    
    def __init__(self, port, baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_port = None
        self.serial_lock = threading.Lock()
        
    def connect(self):
        """Connect to Arduino serial port."""
        try:
            self.serial_port = serial.Serial(self.port, self.baud_rate, timeout=1, write_timeout=30)
            print(f"Connected to Arduino on {self.port}")
            return True
        except Exception as e:
            print(f"Serial connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self.serial_port = None
            print("Disconnected from Arduino")
    
    def send_command(self, cmd):
        """Send command to Arduino."""
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
        """Upload CSV file to Arduino."""
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
        """Retrieve acquired data from Arduino."""
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
        data_array: numpy array with shape (num_samples, 7)
                   Columns: [A0, A1, A2, A3, A4, A5, output_voltage]
        sample_rate: Sample rate in Hz
        odrive_data: Optional dict with ODrive variables (if ODrive connected)
    """
    num_samples = data_array.shape[0]
    num_channels = data_array.shape[1]
    
    # Verify we have 7 channels (6 inputs + 1 output voltage)
    if num_channels != 7:
        raise ValueError(f"Expected 7 channels (6 inputs + output voltage), got {num_channels}")
    
    # Create time vector
    t = np.arange(num_samples) / sample_rate
    
    # Extract input channels (A0-A5) - indices 0-5
    A0 = data_array[:, 0]
    A1 = data_array[:, 1]
    A2 = data_array[:, 2]
    A3 = data_array[:, 3]
    A4 = data_array[:, 4]
    A5 = data_array[:, 5]
    
    # Extract output voltage - index 6 (recorded by Arduino during acquisition)
    output_voltage = data_array[:, 6]
    
    # Calculate accelerations (acc0-acc5) - these are the raw analog inputs
    # In this system, the analog inputs ARE the accelerometer readings
    acc0 = A0
    acc1 = A1
    acc2 = A2
    acc3 = A3
    acc4 = A4
    acc5 = A5
    
    # Calculate theta_x and theta_y
    theta_x = -(A0 + A1 - A2 - A3) * np.sin(ALPHA) / (2 * L3)
    theta_y = -(A0 - A1 - A2 + A3) * np.cos(ALPHA) / (2 * L3)
    
    # Calculate x and y accelerations
    x = (-(A0 - A1 + A2 - A3) * np.cos(ALPHA) / 4 - 
         theta_y * (L1 + L2 + L3 / 2) - A5) * R_A
    y = ((A0 + A1 + A2 + A3) * np.sin(ALPHA) / 4 + 
         theta_x * (L1 + L2 + L3 / 2) - A4) * R_A
    
    # Store processed data
    data = {
        'time': t,
        'output_voltage': output_voltage,
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

def plot_time_series(data, variables_to_plot):
    """Plot time series data - all plots in one window with synced x-axes."""
    # Filter variables that exist in data
    available_vars = [v for v in variables_to_plot if v in data]
    
    if len(available_vars) == 0:
        print("No variables available to plot")
        return
    
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
    plt.show()

def plot_bode_plots(data, bode_configs):
    """Plot 6 Bode plots in 2x3 grid."""
    # Filter configs where both input and output exist
    valid_configs = []
    for input_var, output_var in bode_configs:
        if input_var in data and output_var in data:
            valid_configs.append((input_var, output_var))
        else:
            print(f"Warning: Skipping Bode plot ({input_var} -> {output_var}): variable not found")
    
    if len(valid_configs) == 0:
        print("No valid Bode plot configurations")
        return
    
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
    plt.show()

def main():
    """Main sequential flow."""
    print("=" * 60)
    print("Sequential Phase 1 Data Acquisition System")
    print("=" * 60)
    
    # Initialize Qt application (needed for dialogs and matplotlib)
    app = QApplication(sys.argv)
    
    try:
        # Step 1: Connect to Arduino (hard-coded COM10)
        print(f"\nStep 1: Connecting to Arduino on {ARDUINO_PORT}...")
        serial_helper = SerialHelper(ARDUINO_PORT)
        if not serial_helper.connect():
            print("Failed to connect to Arduino. Exiting.")
            return 1
        print("Arduino connected successfully.")
        
        # Step 2: Prompt for ODrive connection
        print("\nStep 2: ODrive connection")
        odrive_connected = False
        odrive_ctrl = None
        response = input("Connect to ODrive? (y/n, default=n): ").strip().lower()
        if response == 'y':
            print("Connecting to ODrive via USB...")
            odrive_ctrl = ODriveController()
            if odrive_ctrl.connect():
                odrive_connected = True
                print("ODrive connected successfully.")
                # Configure ODrive (default settings)
                odrive_ctrl.set_control_mode('Position')
                odrive_ctrl.set_analog_mapping('Position')
            else:
                print("ODrive connection failed. Continuing without ODrive.")
        else:
            print("Skipping ODrive connection.")
        
        # Step 3: Select CSV file
        print("\nStep 3: Select CSV multisine file")
        csv_path, _ = QFileDialog.getOpenFileName(None, "Select CSV Multisine File", "", "CSV Files (*.csv)")
        if not csv_path:
            print("No CSV file selected. Exiting.")
            serial_helper.disconnect()
            return 1
        
        print(f"CSV file selected: {os.path.basename(csv_path)}")
        
        # Parse CSV file to extract sample rate (needed for ODrive configuration)
        # Note: Voltage values will be read from Arduino acquisition data, not from CSV
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
        
        # Upload CSV to Arduino
        print("Uploading CSV to Arduino...")
        success, message = serial_helper.upload_csv(csv_path)
        if not success:
            print(f"CSV upload failed: {message}")
            serial_helper.disconnect()
            return 1
        print(f"CSV uploaded: {message}")
        
        # Configure ODrive capture rate if connected
        if odrive_connected and sample_rate is not None:
            odrive_ctrl.configure_capture(sample_rate)
        
        # Step 4: Get acquisition duration
        print("\nStep 4: Acquisition duration")
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
        
        print(f"Acquisition duration set to {duration} seconds.")
        
        # Step 5: Start Output dialog
        print("\nStep 5: Start Output")
        start_dialog = StartOutputDialog()
        if start_dialog.exec_() != QDialog.Accepted:
            print("Start Output cancelled. Exiting.")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        
        # Start output
        print("Starting output...")
        success, response, error = serial_helper.send_command_and_wait_response(
            "START_OUTPUT", "ACK: Output started", timeout=2
        )
        if not success:
            print(f"Failed to start output: {error}")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        print("Output started successfully.")
        
        # Step 6: Control dialog (Stop Output / Start Acquisition)
        print("\nStep 6: Control")
        control_dialog = ControlDialog()
        if control_dialog.exec_() != QDialog.Accepted:
            print("Control dialog cancelled. Stopping output and exiting.")
            serial_helper.send_command("STOP_OUTPUT")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        
        if control_dialog.action == 'stop_output':
            print("Stopping output...")
            serial_helper.send_command("STOP_OUTPUT")
            print("Output stopped. Exiting.")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 0
        
        # Start acquisition
        print("Starting acquisition...")
        delay = 0.0  # No delay for Phase 1
        success, response, error = serial_helper.send_command_and_wait_response(
            f"START_ACQUISITION,{duration},{delay}", "ACK: Acquisition started", timeout=2
        )
        if not success:
            print(f"Failed to start acquisition: {error}")
            serial_helper.send_command("STOP_OUTPUT")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        print("Acquisition started.")
        
        # Step 7: Stop Acquisition dialog (monitor acquisition)
        print("\nStep 7: Acquisition in progress")
        stop_dialog = StopAcquisitionDialog()
        
        # Monitor acquisition progress
        acquisition_complete = False
        timer = QTimer()
        
        def check_acquisition():
            nonlocal acquisition_complete
            if serial_helper.serial_port and serial_helper.serial_port.is_open:
                if serial_helper.serial_port.in_waiting > 0:
                    line = serial_helper.serial_port.readline().decode().strip()
                    if line == "ACK: Acquisition complete":
                        acquisition_complete = True
                        stop_dialog.accept()
        
        timer.timeout.connect(check_acquisition)
        timer.start(100)  # Check every 100ms
        
        # Show dialog (blocks until closed or acquisition completes)
        stop_dialog.exec_()
        timer.stop()
        
        # Check if user stopped or acquisition completed
        if stop_dialog.stopped or not acquisition_complete:
            print("Stopping acquisition...")
            serial_helper.send_command("STOP_ACQUISITION")
            time.sleep(0.5)  # Wait for Arduino to stop
        
        # Stop output
        print("Stopping output...")
        serial_helper.send_command("STOP_OUTPUT")
        
        # Wait for acquisition to complete if not already
        if not acquisition_complete:
            print("Waiting for acquisition to complete...")
            timeout = 0
            while timeout < 100:  # 10 seconds timeout
                if serial_helper.serial_port.in_waiting > 0:
                    line = serial_helper.serial_port.readline().decode().strip()
                    if line == "ACK: Acquisition complete":
                        acquisition_complete = True
                        break
                time.sleep(0.1)
                timeout += 1
        
        if not acquisition_complete:
            print("Warning: Acquisition may not have completed properly")
        
        # Step 8: Retrieve data
        print("\nStep 8: Retrieving data from Arduino...")
        data_result = serial_helper.get_data()
        if data_result is None:
            print("Failed to retrieve data from Arduino.")
            serial_helper.disconnect()
            if odrive_connected:
                odrive_ctrl.disconnect()
            return 1
        
        print(f"Retrieved {len(data_result['samples'])} samples at {data_result['sample_rate']:.1f} Hz")
        
        # Retrieve ODrive data if connected
        odrive_data = None
        if odrive_connected:
            print("Retrieving ODrive data...")
            # TODO: Implement proper ODrive data retrieval from capture buffer
            # For now, create placeholder structure with current values
            # In practice, you'd retrieve time-series data from ODrive capture buffer
            odrive_data = {}
            num_samples = len(data_result['samples'])
            try:
                axis = odrive_ctrl.axis
                # Map ODrive variables to match user requirements
                # ODrive.Axis.pos_estimate
                odrive_data['Axis_pos_estimate'] = np.full(num_samples, axis.pos_estimate)
                # ODrive.Axis.vel_estimate
                odrive_data['Axis_vel_estimate'] = np.full(num_samples, axis.vel_estimate)
                # ODrive.Motor.torque_estimate
                odrive_data['Motor_torque_estimate'] = np.full(num_samples, axis.motor.torque_estimate)
                # ODrive.Rs485Encoder.raw32 (if available)
                try:
                    odrive_data['Rs485Encoder_raw32'] = np.full(num_samples, axis.encoder.config.rs485_encoder.raw32 if hasattr(axis.encoder.config, 'rs485_encoder') else 0)
                except:
                    odrive_data['Rs485Encoder_raw32'] = np.zeros(num_samples)
                # ODrive.EncoderEstimator.pos_estimate
                odrive_data['EncoderEstimator_pos_estimate'] = np.full(num_samples, axis.encoder.pos_estimate)
                # ODrive.EncoderEstimator.vel_estimate
                odrive_data['EncoderEstimator_vel_estimate'] = np.full(num_samples, axis.encoder.vel_estimate)
                # ODrive.Controller.input_pos
                odrive_data['Controller_input_pos'] = np.full(num_samples, axis.controller.input_pos)
                # ODrive.Controller.input_vel
                odrive_data['Controller_input_vel'] = np.full(num_samples, axis.controller.input_vel)
                # ODrive.Controller.input_torque
                odrive_data['Controller_input_torque'] = np.full(num_samples, axis.controller.input_torque)
                # ODrive.Controller.pos_setpoint
                odrive_data['Controller_pos_setpoint'] = np.full(num_samples, axis.controller.pos_setpoint)
                # ODrive.Controller.vel_setpoint
                odrive_data['Controller_vel_setpoint'] = np.full(num_samples, axis.controller.vel_setpoint)
                # ODrive.Controller.torque_setpoint
                odrive_data['Controller_torque_setpoint'] = np.full(num_samples, axis.controller.torque_setpoint)
                # ODrive.Controller.vel_integrator_torque
                odrive_data['Controller_vel_integrator_torque'] = np.full(num_samples, axis.controller.vel_integrator_torque)
            except Exception as e:
                print(f"Warning: Could not retrieve ODrive data: {e}")
                import traceback
                traceback.print_exc()
        
        # Step 9: Process data
        print("\nStep 9: Processing data...")
        processed_data = process_data(
            data_result['samples'],
            data_result['sample_rate'],
            odrive_data=odrive_data
        )
        
        # Step 10: Display time series plots
        print("\nStep 10: Displaying time series plots...")
        plot_time_series(processed_data, TIME_SERIES_VARIABLES)
        
        # Step 11: Display Bode plots
        print("\nStep 11: Displaying Bode plots...")
        plot_bode_plots(processed_data, BODE_PLOT_CONFIGS)
        
        print("\n" + "=" * 60)
        print("Acquisition complete!")
        print("=" * 60)
        
        # Cleanup
        serial_helper.disconnect()
        if odrive_connected:
            odrive_ctrl.disconnect()
        
        # Keep application running to show plots
        print("\nPlots are displayed. Close plot windows to exit.")
        sys.exit(app.exec_())
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Cleaning up...")
        if 'serial_helper' in locals():
            serial_helper.send_command("STOP_OUTPUT")
            serial_helper.send_command("STOP_ACQUISITION")
            serial_helper.disconnect()
        if 'odrive_connected' in locals() and odrive_connected and 'odrive_ctrl' in locals():
            odrive_ctrl.disconnect()
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        if 'serial_helper' in locals():
            serial_helper.disconnect()
        if 'odrive_connected' in locals() and odrive_connected and 'odrive_ctrl' in locals():
            odrive_ctrl.disconnect()
        return 1

if __name__ == "__main__":
    sys.exit(main())

