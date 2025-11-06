"""
Main Control Application

PyQt5 GUI application for synchronized data acquisition and motor control system.
Integrates Arduino Opta Lite, A0602 expansion board, and ODrive S1.
"""

import sys
import os
import csv
from datetime import datetime
from pathlib import Path
import serial
import serial.tools.list_ports
import numpy as np
import pandas as pd
from scipy import signal

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QDoubleSpinBox, QComboBox, QCheckBox, QTabWidget,
                             QGridLayout, QMessageBox, QProgressBar, QTextEdit)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QPalette

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from odrive_config import ODriveController

# Geometric calculation constants
L1 = 0.01    # m
L2 = 0.05    # m
L3 = 0.2     # m
ALPHA = np.deg2rad(20)  # Convert to radians
R_A = 5 * 9.81 / 10     # m/s²/V accelerometer sensitivity


class SerialThread(QThread):
    """Thread for serial communication with Arduino."""
    
    data_received = pyqtSignal(dict)  # Emitted when data received
    status_update = pyqtSignal(dict)  # Emitted for status updates
    error_occurred = pyqtSignal(str)  # Emitted on errors
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.command_queue = []
        self.running = True
        
    def connect_serial(self, port, baud_rate=115200):
        """Connect to Arduino serial port."""
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            self.status_update.emit({'connected': True})
            return True
        except Exception as e:
            self.error_occurred.emit(f"Serial connection failed: {e}")
            return False
    
    def disconnect_serial(self):
        """Disconnect from serial port."""
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        self.status_update.emit({'connected': False})
    
    def send_command(self, cmd):
        """Send command to Arduino."""
        if not self.serial_port or not self.serial_port.is_open:
            self.error_occurred.emit("Serial port not connected. Please connect to Arduino first.")
            return False
        
        try:
            self.serial_port.write((cmd + '\n').encode())
            self.serial_port.flush()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Send command failed: {e}")
            return False
    
    def upload_csv(self, csv_path):
        """Upload CSV file to Arduino."""
        try:
            # Read CSV file
            with open(csv_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                self.error_occurred.emit("CSV file too short")
                return False
            
            # Send UPLOAD_CSV command
            self.send_command("UPLOAD_CSV")
            
            # Wait for READY signal
            response = self.serial_port.readline().decode().strip()
            if response != "READY":
                self.error_occurred.emit("No READY signal from Arduino")
                return False
            
            # Send all CSV lines
            for line in lines:
                self.serial_port.write((line.strip() + '\n').encode())
            
            self.serial_port.flush()
            
            # Wait for ACK
            response = self.serial_port.readline().decode().strip()
            if response == "ACK: CSV loaded":
                return True
            else:
                self.error_occurred.emit(response)
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"CSV upload failed: {e}")
            return False
    
    def run(self):
        """Main thread loop."""
        while self.running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    if self.serial_port.in_waiting > 0:
                        line = self.serial_port.readline().decode().strip()
                        
                        if line.startswith("DATA:"):
                            # Parse data header
                            parts = line[5:].split(',')
                            sample_count = int(parts[0])
                            sample_period = float(parts[1])
                            num_channels = int(parts[2])
                            
                            # Read data samples
                            data_array = []
                            for _ in range(sample_count):
                                line = self.serial_port.readline().decode().strip()
                                if line == "DATA_END":
                                    break
                                
                                values = [float(x) for x in line.split(',')]
                                data_array.append(values)
                            
                            # Emit data
                            data = {
                                'samples': data_array,
                                'sample_rate': 1.0 / sample_period,
                                'channels': num_channels
                            }
                            self.data_received.emit(data)
                            
                        elif line.startswith("STATUS:"):
                            # Parse status
                            parts = line[7:].split(',')
                            status = {
                                'state': int(parts[0]),
                                'output_active': parts[1] == '1',
                                'acquisition_active': parts[2] == '1',
                                'csv_samples': int(parts[3]),
                                'csv_period': float(parts[4])
                            }
                            self.status_update.emit(status)
                            
                        elif line.startswith("ERROR:"):
                            self.error_occurred.emit(line[6:])
                            
                except Exception as e:
                    self.error_occurred.emit(f"Read error: {e}")
            
            self.msleep(10)  # Small delay to prevent tight loop
    
    def stop(self):
        """Stop the thread."""
        self.running = False
        self.disconnect_serial()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino ODrive Data Acquisition System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data storage
        self.data = None
        self.csv_path = None
        self.csv_info = {}
        self.csv_time = None
        self.csv_voltage = None
        
        # Controllers
        self.serial_thread = SerialThread()
        self.odrive_ctrl = ODriveController()
        
        # Initialize GUI
        self.init_ui()
        
        # Connect signals
        self.serial_thread.data_received.connect(self.on_data_received)
        self.serial_thread.status_update.connect(self.on_status_update)
        self.serial_thread.error_occurred.connect(self.on_error)
        
        # Start serial thread
        self.serial_thread.start()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.request_status)
        self.status_timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel: Controls
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)
        
        # Right panel: Visualization
        vis_panel = self.create_visualization_panel()
        main_layout.addWidget(vis_panel, stretch=3)
    
    def create_control_panel(self):
        """Create the left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # File Configuration Section
        file_group = QWidget()
        file_layout = QVBoxLayout(file_group)
        file_layout.addWidget(QLabel("<b>File Configuration</b>"))
        
        self.file_label = QLabel("No file loaded")
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)
        
        file_btn_layout = QHBoxLayout()
        self.load_csv_btn = QPushButton("Load CSV File")
        self.load_csv_btn.clicked.connect(self.load_csv_file)
        file_btn_layout.addWidget(self.load_csv_btn)
        file_layout.addLayout(file_btn_layout)
        
        self.csv_info_label = QLabel("")
        file_layout.addWidget(self.csv_info_label)
        
        layout.addWidget(file_group)
        
        # Output Control Section
        output_group = QWidget()
        output_layout = QVBoxLayout(output_group)
        output_layout.addWidget(QLabel("<b>Output Control</b>"))
        
        btn_layout = QHBoxLayout()
        self.start_output_btn = QPushButton("Start Output")
        self.start_output_btn.clicked.connect(self.start_output)
        self.stop_output_btn = QPushButton("Stop Output")
        self.stop_output_btn.clicked.connect(self.stop_output)
        self.stop_output_btn.setEnabled(False)
        btn_layout.addWidget(self.start_output_btn)
        btn_layout.addWidget(self.stop_output_btn)
        output_layout.addLayout(btn_layout)
        
        layout.addWidget(output_group)
        
        # Acquisition Control Section
        acq_group = QWidget()
        acq_layout = QVBoxLayout(acq_group)
        acq_layout.addWidget(QLabel("<b>Acquisition Control</b>"))
        
        # Duration input
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (s):"))
        self.acq_duration = QDoubleSpinBox()
        self.acq_duration.setRange(0.1, 1000.0)
        self.acq_duration.setValue(1.0)
        self.acq_duration.setDecimals(2)
        self.acq_duration.setSuffix(" s")
        duration_layout.addWidget(self.acq_duration)
        acq_layout.addLayout(duration_layout)
        
        # Start delay input
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Start delay (s):"))
        self.acq_delay = QDoubleSpinBox()
        self.acq_delay.setRange(0.0, 100.0)
        self.acq_delay.setValue(0.0)
        self.acq_delay.setDecimals(2)
        self.acq_delay.setSuffix(" s")
        delay_layout.addWidget(self.acq_delay)
        acq_layout.addLayout(delay_layout)
        
        # Buttons
        acq_btn_layout = QHBoxLayout()
        self.start_acq_btn = QPushButton("Start Acquisition")
        self.start_acq_btn.clicked.connect(self.start_acquisition)
        self.stop_acq_btn = QPushButton("Stop Acquisition")
        self.stop_acq_btn.clicked.connect(self.stop_acquisition)
        self.stop_acq_btn.setEnabled(False)
        acq_btn_layout.addWidget(self.start_acq_btn)
        acq_btn_layout.addWidget(self.stop_acq_btn)
        acq_layout.addLayout(acq_btn_layout)
        
        layout.addWidget(acq_group)
        
        # Status Section
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        status_layout.addWidget(QLabel("<b>Status</b>"))
        
        self.status_label = QLabel("Status: IDLE")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
        # Arduino Connection Section
        arduino_group = QWidget()
        arduino_layout = QVBoxLayout(arduino_group)
        arduino_layout.addWidget(QLabel("<b>Arduino Connection</b>"))
        
        # Serial port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Serial port:"))
        self.serial_port_combo = QComboBox()
        self.refresh_ports()
        port_layout.addWidget(self.serial_port_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(refresh_btn)
        arduino_layout.addLayout(port_layout)
        
        # Connection button
        self.arduino_connect_btn = QPushButton("Connect Arduino")
        self.arduino_connect_btn.clicked.connect(self.connect_arduino)
        arduino_layout.addWidget(self.arduino_connect_btn)
        
        self.arduino_status_label = QLabel("Arduino: Not connected")
        arduino_layout.addWidget(self.arduino_status_label)
        
        layout.addWidget(arduino_group)
        
        # ODrive Configuration Section
        odrive_group = QWidget()
        odrive_layout = QVBoxLayout(odrive_group)
        odrive_layout.addWidget(QLabel("<b>ODrive Configuration</b>"))
        
        # Control mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Control mode:"))
        self.odrive_mode = QComboBox()
        self.odrive_mode.addItems(['Torque', 'Velocity', 'Position'])
        mode_layout.addWidget(self.odrive_mode)
        odrive_layout.addLayout(mode_layout)
        
        # Analog mapping
        map_layout = QHBoxLayout()
        map_layout.addWidget(QLabel("Analog mapping:"))
        self.odrive_mapping = QComboBox()
        self.odrive_mapping.addItems(['Position', 'Velocity', 'Torque'])
        map_layout.addWidget(self.odrive_mapping)
        odrive_layout.addLayout(map_layout)
        
        # Connection button
        self.odrive_connect_btn = QPushButton("Connect ODrive")
        self.odrive_connect_btn.clicked.connect(self.connect_odrive)
        odrive_layout.addWidget(self.odrive_connect_btn)
        
        self.odrive_status_label = QLabel("ODrive: Not connected")
        odrive_layout.addWidget(self.odrive_status_label)
        
        layout.addWidget(odrive_group)
        
        layout.addStretch()
        
        return panel
    
    def create_visualization_panel(self):
        """Create the right visualization panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # CSV Signal plot tab
        csv_tab = QWidget()
        csv_layout = QVBoxLayout(csv_tab)
        
        # Plot canvas
        self.csv_figure = Figure(figsize=(10, 6))
        self.csv_canvas = FigureCanvas(self.csv_figure)
        csv_layout.addWidget(self.csv_canvas)
        
        tabs.addTab(csv_tab, "CSV Signal")
        
        # Time domain plot tab
        time_tab = QWidget()
        time_layout = QVBoxLayout(time_tab)
        
        # Signal selection checkboxes
        signal_layout = QHBoxLayout()
        self.signal_checkboxes = {}
        signals = ['Output Voltage', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 
                   'theta_x', 'theta_y', 'x', 'y']
        
        for i, sig in enumerate(signals):
            cb = QCheckBox(sig)
            cb.setChecked(True)
            self.signal_checkboxes[sig] = cb
            signal_layout.addWidget(cb)
        
        time_layout.addLayout(signal_layout)
        
        # Plot canvas
        self.time_figure = Figure(figsize=(10, 6))
        self.time_canvas = FigureCanvas(self.time_figure)
        time_layout.addWidget(self.time_canvas)
        
        tabs.addTab(time_tab, "Time Domain")
        
        # Bode plot tab
        bode_tab = QWidget()
        bode_layout = QVBoxLayout(bode_tab)
        
        # Signal selectors
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Input signal:"))
        self.bode_input = QComboBox()
        self.bode_input.addItems(['Output Voltage'] + [f'A{i}' for i in range(1, 7)])
        selector_layout.addWidget(self.bode_input)
        
        selector_layout.addWidget(QLabel("Output signal:"))
        self.bode_output = QComboBox()
        self.bode_output.addItems(['theta_x', 'theta_y', 'x', 'y'])
        selector_layout.addWidget(self.bode_output)
        
        calculate_btn = QPushButton("Calculate Bode Plot")
        calculate_btn.clicked.connect(self.calculate_bode)
        selector_layout.addWidget(calculate_btn)
        
        bode_layout.addLayout(selector_layout)
        
        # Bode plot canvas
        self.bode_figure = Figure(figsize=(10, 6))
        self.bode_canvas = FigureCanvas(self.bode_figure)
        bode_layout.addWidget(self.bode_canvas)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_png_btn = QPushButton("Export Plot (PNG)")
        export_png_btn.clicked.connect(self.export_bode_png)
        export_csv_btn = QPushButton("Export Bode Data (CSV)")
        export_csv_btn.clicked.connect(self.export_bode_csv)
        export_layout.addWidget(export_png_btn)
        export_layout.addWidget(export_csv_btn)
        bode_layout.addLayout(export_layout)
        
        tabs.addTab(bode_tab, "Bode Plot")
        
        layout.addWidget(tabs)
        
        # Export data button
        export_data_btn = QPushButton("Export All Data to CSV")
        export_data_btn.clicked.connect(self.export_data)
        layout.addWidget(export_data_btn)
        
        return panel
    
    def load_csv_file(self):
        """Load CSV file for voltage output."""
        filename, _ = QFileDialog.getOpenFileName(self, "Load CSV File", "", "CSV Files (*.csv)")
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) < 2:
                    QMessageBox.warning(self, "Error", "CSV file too short")
                    return
                
                # Parse CSV with header comments
                sample_period = None
                sample_rate = None
                voltage_values = []
                time_values = []
                found_header = False
                first_time = None
                second_time = None
                has_time_column = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip header comment lines (starting with #)
                    if line.startswith('#'):
                        # Try to extract sample rate from metadata header
                        # Format: "# fs: 5000.0 Hz"
                        if 'fs:' in line:
                            try:
                                fs_part = line.split('fs:')[1].split('Hz')[0].strip()
                                fs_value = float(fs_part)
                                if fs_value > 0:
                                    sample_rate = fs_value
                                    sample_period = 1.0 / fs_value
                            except (ValueError, IndexError):
                                pass
                        continue
                    
                    # Check for CSV header row
                    if line.lower() == 'time_s,signal':
                        found_header = True
                        has_time_column = True
                        continue
                    
                    # Parse data rows (comma-separated: time, signal)
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            try:
                                time_val = float(parts[0].strip())
                                voltage = float(parts[1].strip())
                                
                                # Store first two time values to calculate sample period if not extracted
                                if first_time is None:
                                    first_time = time_val
                                elif second_time is None and sample_period is None:
                                    second_time = time_val
                                    if second_time > first_time:
                                        sample_period = second_time - first_time
                                        sample_rate = 1.0 / sample_period
                                
                                # Validate voltage range
                                if voltage < 0 or voltage > 3.3:
                                    QMessageBox.warning(self, "Error", f"Voltage out of range: {voltage}V")
                                    return
                                
                                voltage_values.append(voltage)
                                time_values.append(time_val)
                                has_time_column = True
                            except ValueError:
                                continue
                    else:
                        # Fallback: try to parse as single value (for backward compatibility)
                        try:
                            voltage = float(line)
                            if 0 <= voltage <= 3.3:
                                voltage_values.append(voltage)
                        except ValueError:
                            continue
                
                # Calculate sample period from time differences if not extracted from metadata
                if sample_period is None and len(voltage_values) > 1:
                    # Try to extract from time column if available
                    if first_time is not None and second_time is not None:
                        sample_period = second_time - first_time
                        sample_rate = 1.0 / sample_period
                    else:
                        QMessageBox.warning(self, "Error", "Could not determine sample period from CSV")
                        return
                
                if len(voltage_values) == 0:
                    QMessageBox.warning(self, "Error", "No voltage values found")
                    return
                
                if sample_period is None or sample_period <= 0:
                    QMessageBox.warning(self, "Error", "Invalid sample period")
                    return
                
                self.csv_path = filename
                self.csv_info = {
                    'filename': os.path.basename(filename),
                    'sample_rate': sample_rate,
                    'duration': len(voltage_values) * sample_period,
                    'samples': len(voltage_values)
                }
                
                # Store CSV data for visualization
                self.csv_voltage = np.array(voltage_values)
                if has_time_column and len(time_values) > 0:
                    # Use time values from CSV
                    self.csv_time = np.array(time_values)
                else:
                    # Generate time array from sample period
                    self.csv_time = np.arange(len(voltage_values)) * sample_period
                
                self.file_label.setText(f"File: {self.csv_info['filename']}")
                self.csv_info_label.setText(
                    f"Rate: {sample_rate:.1f} Hz\n"
                    f"Duration: {self.csv_info['duration']:.2f} s\n"
                    f"Samples: {self.csv_info['samples']}"
                )
                
                # Update CSV plot
                self.update_csv_plot()
                
                # Upload to Arduino if connected
                if self.serial_thread.serial_port and self.serial_thread.serial_port.is_open:
                    self.serial_thread.upload_csv(filename)
                else:
                    QMessageBox.information(self, "Info", "CSV file loaded but not uploaded. Please connect to Arduino and load the file again to upload.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV: {e}")
    
    def start_output(self):
        """Start voltage output."""
        if not self.csv_path:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not self.serial_thread.serial_port or not self.serial_thread.serial_port.is_open:
            QMessageBox.warning(self, "Warning", "Please connect to Arduino first")
            return
        
        if self.serial_thread.send_command("START_OUTPUT"):
            self.start_output_btn.setEnabled(False)
            self.stop_output_btn.setEnabled(True)
    
    def stop_output(self):
        """Stop voltage output."""
        if not self.serial_thread.serial_port or not self.serial_thread.serial_port.is_open:
            QMessageBox.warning(self, "Warning", "Please connect to Arduino first")
            return
        
        if self.serial_thread.send_command("STOP_OUTPUT"):
            self.start_output_btn.setEnabled(True)
            self.stop_output_btn.setEnabled(False)
    
    def start_acquisition(self):
        """Start data acquisition."""
        if not self.csv_path:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not self.serial_thread.serial_port or not self.serial_thread.serial_port.is_open:
            QMessageBox.warning(self, "Warning", "Please connect to Arduino first")
            return
        
        duration = self.acq_duration.value()
        delay = self.acq_delay.value()
        
        if self.serial_thread.send_command(f"START_ACQUISITION,{duration},{delay}"):
            self.start_acq_btn.setEnabled(False)
            self.stop_acq_btn.setEnabled(True)
    
    def stop_acquisition(self):
        """Stop data acquisition."""
        if not self.serial_thread.serial_port or not self.serial_thread.serial_port.is_open:
            QMessageBox.warning(self, "Warning", "Please connect to Arduino first")
            return
        
        if self.serial_thread.send_command("STOP_ACQUISITION"):
            self.start_acq_btn.setEnabled(True)
            self.stop_acq_btn.setEnabled(False)
    
    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        self.serial_port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_str = f"{port.device} - {port.description}"
            self.serial_port_combo.addItem(port_str, port.device)
    
    def connect_arduino(self):
        """Connect to Arduino serial port."""
        if self.serial_thread.serial_port and self.serial_thread.serial_port.is_open:
            # Disconnect
            self.serial_thread.disconnect_serial()
            self.arduino_connect_btn.setText("Connect Arduino")
            self.arduino_status_label.setText("Arduino: Not connected")
        else:
            # Connect
            if self.serial_port_combo.count() == 0:
                QMessageBox.warning(self, "Warning", "No serial ports available. Please refresh.")
                return
            
            port = self.serial_port_combo.currentData()
            if not port:
                QMessageBox.warning(self, "Warning", "Please select a serial port")
                return
            
            if self.serial_thread.connect_serial(port):
                self.arduino_connect_btn.setText("Disconnect Arduino")
                self.arduino_status_label.setText(f"Arduino: Connected ({port})")
            else:
                QMessageBox.warning(self, "Error", f"Failed to connect to {port}")
    
    def connect_odrive(self):
        """Connect to ODrive."""
        if self.odrive_ctrl.connected:
            self.odrive_ctrl.disconnect()
            self.odrive_connect_btn.setText("Connect ODrive")
            self.odrive_status_label.setText("ODrive: Not connected")
        else:
            if self.odrive_ctrl.connect():
                self.odrive_connect_btn.setText("Disconnect ODrive")
                self.odrive_status_label.setText("ODrive: Connected")
                
                # Apply configuration
                mode = self.odrive_mode.currentText()
                mapping = self.odrive_mapping.currentText()
                self.odrive_ctrl.set_control_mode(mode)
                self.odrive_ctrl.set_analog_mapping(mapping)
                
                if self.csv_info:
                    self.odrive_ctrl.configure_capture(self.csv_info['sample_rate'])
    
    def request_status(self):
        """Request status update from Arduino."""
        if self.serial_thread.serial_port:
            self.serial_thread.send_command("GET_STATUS")
    
    def on_status_update(self, status):
        """Handle status update from Arduino."""
        # Handle connection status
        if 'connected' in status:
            if status['connected']:
                port = self.serial_port_combo.currentData() if self.serial_port_combo.count() > 0 else "Unknown"
                self.arduino_status_label.setText(f"Arduino: Connected ({port})")
            else:
                self.arduino_status_label.setText("Arduino: Not connected")
        
        # Handle state updates
        state_names = ['IDLE', 'OUTPUTTING', 'ACQUIRING', 'TRANSFERRING']
        if status.get('state') is not None:
            state = state_names[status['state']]
            self.status_label.setText(f"Status: {state}")
    
    def on_data_received(self, data):
        """Handle data received from Arduino."""
        try:
            samples = data['samples']
            sample_rate = data['sample_rate']
            
            # Convert to numpy array
            data_array = np.array(samples)
            
            if data_array.shape[1] != 6:
                QMessageBox.warning(self, "Error", "Unexpected number of channels")
                return
            
            # Process data
            self.process_data(data_array, sample_rate)
            
            # Update plots
            self.update_time_plots()
            
            # Save data
            self.save_data()
            
            QMessageBox.information(self, "Success", "Data acquisition complete!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Data processing failed: {e}")
    
    def process_data(self, data_array, sample_rate):
        """Process acquired data including geometric calculations."""
        num_samples = data_array.shape[0]
        
        # Create time vector
        t = np.arange(num_samples) / sample_rate
        
        # Extract input channels
        A1 = data_array[:, 0]
        A2 = data_array[:, 1]
        A3 = data_array[:, 2]
        A4 = data_array[:, 3]
        A5 = data_array[:, 4]
        A6 = data_array[:, 5]
        
        # Calculate theta_x and theta_y
        theta_x = -(A1 + A2 - A3 - A4) * np.sin(ALPHA) / (2 * L3)
        theta_y = -(A1 - A2 - A3 + A4) * np.cos(ALPHA) / (2 * L3)
        
        # Calculate x and y accelerations
        x = (-(A1 - A2 + A3 - A4) * np.cos(ALPHA) / 4 - 
             theta_y * (L1 + L2 + L3 / 2) - A6) * R_A
        y = ((A1 + A2 + A3 + A4) * np.sin(ALPHA) / 4 + 
             theta_x * (L1 + L2 + L3 / 2) - A5) * R_A
        
        # Store processed data
        self.data = {
            'time': t,
            'output_voltage': A1 * 0,  # TODO: Get actual output voltage from Arduino
            'A1': A1,
            'A2': A2,
            'A3': A3,
            'A4': A4,
            'A5': A5,
            'A6': A6,
            'theta_x': theta_x,
            'theta_y': theta_y,
            'x': x,
            'y': y,
            'sample_rate': sample_rate
        }
    
    def update_time_plots(self):
        """Update time domain plots."""
        if self.data is None:
            return
        
        self.time_figure.clear()
        
        # Check which signals to plot
        signals_to_plot = []
        for sig_name, checkbox in self.signal_checkboxes.items():
            if checkbox.isChecked() and sig_name in self.data:
                signals_to_plot.append(sig_name)
        
        if len(signals_to_plot) == 0:
            return
        
        # Create subplots with shared x-axis
        axes = self.time_figure.subplots(len(signals_to_plot), 1, sharex=True)
        
        if len(signals_to_plot) == 1:
            axes = [axes]
        
        for i, sig_name in enumerate(signals_to_plot):
            axes[i].plot(self.data['time'], self.data[sig_name])
            axes[i].set_ylabel(sig_name)
            axes[i].grid(True)
        
        axes[-1].set_xlabel('Time (s)')
        self.time_figure.tight_layout()
        self.time_canvas.draw()
    
    def update_csv_plot(self):
        """Update CSV signal plot."""
        if self.csv_time is None or self.csv_voltage is None:
            return
        
        self.csv_figure.clear()
        ax = self.csv_figure.add_subplot(1, 1, 1)
        ax.plot(self.csv_time, self.csv_voltage)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title('CSV Input Signal')
        ax.grid(True)
        self.csv_figure.tight_layout()
        self.csv_canvas.draw()
    
    def calculate_bode(self):
        """Calculate and plot Bode plot."""
        if self.data is None:
            QMessageBox.warning(self, "Warning", "No data available")
            return
        
        input_signal_name = self.bode_input.currentText()
        output_signal_name = self.bode_output.currentText()
        
        if input_signal_name not in self.data or output_signal_name not in self.data:
            QMessageBox.warning(self, "Warning", "Signal not available")
            return
        
        input_signal = self.data[input_signal_name]
        output_signal = self.data[output_signal_name]
        sample_rate = self.data['sample_rate']
        
        # Compute transfer function using Welch's method
        f, Pxy = signal.csd(output_signal, input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
        f, Pxx = signal.welch(input_signal, fs=sample_rate, nperseg=len(input_signal)//4)
        
        # Calculate transfer function H = Pxy / Pxx
        H = Pxy / (Pxx + 1e-10)  # Add small value to avoid division by zero
        
        # Magnitude and phase
        magnitude = np.abs(H)
        phase = np.angle(H)
        phase = np.unwrap(phase) * 180 / np.pi  # Unwrap and convert to degrees
        
        # Plot
        self.bode_figure.clear()
        
        # Magnitude plot (log-log)
        ax1 = self.bode_figure.add_subplot(2, 1, 1)
        ax1.loglog(f, magnitude)
        ax1.set_ylabel(f'{output_signal_name} / {input_signal_name}')
        ax1.set_title('Bode Plot')
        ax1.grid(True)
        
        # Phase plot (log-linear)
        ax2 = self.bode_figure.add_subplot(2, 1, 2, sharex=ax1)
        ax2.semilogx(f, phase)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.grid(True)
        
        self.bode_figure.tight_layout()
        self.bode_canvas.draw()
        
        # Store for export
        self.bode_data = {
            'frequency': f,
            'magnitude': magnitude,
            'phase': phase,
            'input': input_signal_name,
            'output': output_signal_name
        }
    
    def export_bode_png(self):
        """Export Bode plot as PNG."""
        filename, _ = QFileDialog.getSaveFileName(self, "Export Plot", "", "PNG Files (*.png)")
        if filename:
            self.bode_canvas.figure.savefig(filename, dpi=150)
            QMessageBox.information(self, "Success", "Plot exported successfully")
    
    def export_bode_csv(self):
        """Export Bode data to CSV."""
        if not hasattr(self, 'bode_data'):
            QMessageBox.warning(self, "Warning", "No Bode plot calculated")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Export Bode Data", "", "CSV Files (*.csv)")
        if filename:
            df = pd.DataFrame({
                'frequency': self.bode_data['frequency'],
                'magnitude': self.bode_data['magnitude'],
                'phase': self.bode_data['phase']
            })
            df.to_csv(filename, index=False)
            QMessageBox.information(self, "Success", "Bode data exported successfully")
    
    def export_data(self):
        """Export all acquisition data to CSV."""
        if self.data is None:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/acquisition_{timestamp}.csv"
        
        # Create data directory if it doesn't exist
        Path("data").mkdir(exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        
        QMessageBox.information(self, "Success", f"Data exported to {filename}")
    
    def save_data(self):
        """Save data automatically after acquisition."""
        if self.data is None:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/acquisition_{timestamp}.csv"
        
        # Create data directory if it doesn't exist
        Path("data").mkdir(exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
    
    def on_error(self, error_msg):
        """Handle errors from serial thread."""
        QMessageBox.warning(self, "Error", error_msg)
        print(f"Error: {error_msg}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.serial_thread.stop()
        self.serial_thread.wait()
        if self.odrive_ctrl.connected:
            self.odrive_ctrl.disconnect()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

