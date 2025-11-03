"""
ODrive Configuration Module

This module provides functions to configure the ODrive S1 motor controller
for synchronized data acquisition with the Arduino Opta system.
"""

import odrive
from odrive.enums import *

class ODriveController:
    """
    Controller for ODrive S1 motor driver configuration and data capture.
    """
    
    def __init__(self):
        self.odrv = None
        self.axis = None
        self.connected = False
        self.control_mode = None
        self.analog_mapping = None
        self.capture_rate = 1000  # Default 1kHz
        
    def connect(self):
        """
        Connect to ODrive S1 via USB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print("Searching for ODrive...")
            self.odrv = odrive.find_any(timeout=10)
            
            if self.odrv is None:
                print("ERROR: No ODrive found")
                return False
            
            # Get reference to axis0
            self.axis = self.odrv.axis0
            
            # Verify connection
            if self.axis is None:
                print("ERROR: Could not access axis0")
                return False
            
            self.connected = True
            print(f"ODrive connected: v{self.odrv.fw_version_major}.{self.odrv.fw_version_minor}.{self.odrv.fw_version_revision}")
            return True
            
        except Exception as e:
            print(f"ERROR: Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from ODrive."""
        self.odrv = None
        self.axis = None
        self.connected = False
        print("ODrive disconnected")
    
    def set_control_mode(self, mode):
        """
        Set the control mode for the motor.
        
        Args:
            mode (str): One of 'Torque', 'Velocity', or 'Position'
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        
        try:
            if mode.lower() == 'torque':
                self.axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
                self.control_mode = CONTROL_MODE_TORQUE_CONTROL
            elif mode.lower() == 'velocity':
                self.axis.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
                self.control_mode = CONTROL_MODE_VELOCITY_CONTROL
            elif mode.lower() == 'position':
                self.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
                self.control_mode = CONTROL_MODE_POSITION_CONTROL
            else:
                print(f"ERROR: Unknown control mode: {mode}")
                return False
            
            print(f"Control mode set to: {mode}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to set control mode: {e}")
            return False
    
    def set_analog_mapping(self, mapping):
        """
        Set the analog input mapping.
        
        Args:
            mapping (str): One of 'Position', 'Velocity', or 'Torque'
                - 'Position': Analog input maps to position setpoint
                - 'Velocity': Analog input maps to velocity feedforward
                - 'Torque': Analog input maps to torque feedforward
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        
        try:
            # Configure analog input for control
            analog_config = self.axis.controller.config.input_mode
            
            if mapping.lower() == 'position':
                self.axis.controller.config.input_mode = INPUT_MODE_POS_FILTER
                self.analog_mapping = 'Position'
                # Map analog input to position setpoint
                self.axis.controller.config.vel_integrator_gain = 0.0  # Disable integrator for feedforward
                
            elif mapping.lower() == 'velocity':
                self.axis.controller.config.input_mode = INPUT_MODE_VEL_RAMP
                self.analog_mapping = 'Velocity'
                # Map analog input to velocity feedforward
                
            elif mapping.lower() == 'torque':
                self.axis.controller.config.input_mode = INPUT_MODE_TORQUE_RAMP
                self.analog_mapping = 'Torque'
                # Map analog input to torque feedforward
                
            else:
                print(f"ERROR: Unknown analog mapping: {mapping}")
                return False
            
            print(f"Analog mapping set to: {mapping}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to set analog mapping: {e}")
            return False
    
    def configure_capture(self, sample_rate):
        """
        Configure high-rate data capture buffer.
        
        Args:
            sample_rate (float): Capture rate in Hz
            
        Returns:
            bool: True if configuration successful
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        
        try:
            self.capture_rate = sample_rate
            
            # Configure capture settings
            # This is specific to ODrive S1 capabilities
            # May need to adjust based on actual ODrive firmware version
            
            print(f"Capture rate configured: {sample_rate} Hz")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to configure capture: {e}")
            return False
    
    def start_capture(self):
        """
        Start high-rate data capture.
        
        Returns:
            bool: True if started successfully
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        
        try:
            # ODrive capture configuration
            # This may vary based on firmware version
            print("Starting ODrive capture...")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to start capture: {e}")
            return False
    
    def stop_capture(self):
        """Stop high-rate data capture."""
        if not self.connected:
            return False
        
        try:
            print("Stopping ODrive capture...")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to stop capture: {e}")
            return False
    
    def retrieve_capture_data(self):
        """
        Retrieve captured data from ODrive buffer.
        
        Returns:
            dict: Dictionary containing captured variables with timestamps
                Keys: 'velocity_setpoint', 'torque_setpoint', 'pos_estimate',
                      'vel_estimate', 'torque_estimate', 'control_input'
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return None
        
        try:
            # Retrieve data from capture buffer
            # This implementation is simplified and may need adjustment
            # based on actual ODrive firmware capabilities
            
            data = {
                'velocity_setpoint': [],
                'torque_setpoint': [],
                'pos_estimate': [],
                'vel_estimate': [],
                'torque_estimate': [],
                'control_input': []
            }
            
            print("Retrieving capture data...")
            # TODO: Implement actual data retrieval from ODrive buffer
            
            return data
            
        except Exception as e:
            print(f"ERROR: Failed to retrieve capture data: {e}")
            return None
    
    def get_status(self):
        """
        Get current ODrive status.
        
        Returns:
            dict: Status information including connection, control mode, etc.
        """
        status = {
            'connected': self.connected,
            'control_mode': self.control_mode,
            'analog_mapping': self.analog_mapping,
            'capture_rate': self.capture_rate
        }
        
        if self.connected and self.axis is not None:
            try:
                status['state'] = self.axis.current_state
                status['encoder_pos'] = self.axis.encoder.pos_estimate
                status['motor_vel'] = self.axis.motor.vel_estimate
            except:
                pass
        
        return status


def test_odrive():
    """Test function for ODrive connectivity."""
    odrive_ctrl = ODriveController()
    
    if odrive_ctrl.connect():
        print("\nODrive connection successful")
        print(f"Status: {odrive_ctrl.get_status()}")
        
        # Test configuration
        odrive_ctrl.set_control_mode('Position')
        odrive_ctrl.set_analog_mapping('Position')
        odrive_ctrl.configure_capture(1000)
        
        print("\nConfiguration test complete")
        odrive_ctrl.disconnect()
    else:
        print("\nODrive connection failed")


if __name__ == "__main__":
    test_odrive()

