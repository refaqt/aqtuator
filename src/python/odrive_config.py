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

    def _gpio1_mode_is_analog_in(self):
        if not self.connected or self.odrv is None:
            return False
        try:
            gpio1_mode = self.odrv.config.gpio1_mode
            try:
                return int(gpio1_mode) == int(GpioMode.ANALOG_IN)
            except Exception:
                return str(gpio1_mode) == str(GpioMode.ANALOG_IN)
        except Exception:
            return False

    def ensure_gpio1_analog_in(self):
        """
        Ensure ODrive GPIO1 remains configured as ANALOG_IN.

        Returns:
            bool: True if GPIO1 is confirmed ANALOG_IN, False otherwise.
        """
        if not self.connected or self.odrv is None:
            print("ERROR: Not connected to ODrive")
            return False
        try:
            if not self._gpio1_mode_is_analog_in():
                self.odrv.config.gpio1_mode = GpioMode.ANALOG_IN
            return self._gpio1_mode_is_analog_in()
        except Exception as e:
            print(f"ERROR: Failed to ensure GPIO1 ANALOG_IN mode: {e}")
            return False

    def get_gpio1_state(self):
        """
        Read the ODrive GPIO1 analog-input state used by this workflow.

        Returns:
            dict: Best-effort snapshot of GPIO1-related configuration.
        """
        state = {
            'gpio1_mode': None,
            'gpio1_mode_is_analog_in': False,
            'gpio1_mapping_min': None,
            'gpio1_mapping_max': None,
            'gpio1_mapping_endpoint': None,
            'control_mode': None,
            'input_mode': None,
        }
        if not self.connected or self.odrv is None or self.axis is None:
            return state

        try:
            state['gpio1_mode'] = self.odrv.config.gpio1_mode
            state['gpio1_mode_is_analog_in'] = self._gpio1_mode_is_analog_in()
        except Exception:
            pass
        try:
            state['gpio1_mapping_min'] = self.odrv.config.gpio1_analog_mapping.min
            state['gpio1_mapping_max'] = self.odrv.config.gpio1_analog_mapping.max
            state['gpio1_mapping_endpoint'] = self.odrv.config.gpio1_analog_mapping.endpoint
        except Exception:
            pass
        try:
            state['control_mode'] = self.axis.controller.config.control_mode
            state['input_mode'] = self.axis.controller.config.input_mode
        except Exception:
            pass
        return state

    def print_gpio1_state(self, label="GPIO1 state"):
        """
        Print a concise GPIO1/analog-mapping status snapshot.
        """
        state = self.get_gpio1_state()
        print(f"{label}:")
        print(f"  gpio1_mode={state['gpio1_mode']}")
        print(f"  gpio1_mode_is_analog_in={state['gpio1_mode_is_analog_in']}")
        print(f"  gpio1_mapping_min={state['gpio1_mapping_min']}")
        print(f"  gpio1_mapping_max={state['gpio1_mapping_max']}")
        print(f"  gpio1_mapping_endpoint={state['gpio1_mapping_endpoint']}")
        print(f"  control_mode={state['control_mode']}")
        print(f"  input_mode={state['input_mode']}")
        
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

    def set_enable_step_dir(self, enabled):
        """
        Set axis0 step/dir mode enable flag.

        Args:
            enabled (bool): True to enable step/dir mode, False to disable it

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False

        try:
            self.axis.config.enable_step_dir = bool(enabled)
            state = "enabled" if enabled else "disabled"
            print(f"ODrive step/dir mode {state}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to set step/dir mode: {e}")
            return False

    def get_enable_step_dir(self):
        """
        Read axis0 step/dir mode enable flag.

        Returns:
            bool | None: Current enable_step_dir state, or None on error
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return None

        try:
            return bool(self.axis.config.enable_step_dir)
        except Exception as e:
            print(f"ERROR: Failed to read step/dir mode: {e}")
            return None
    
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
    
    def set_torque_control_mode(self):
        """
        Configure ODrive for torque control via CAN.
        This sets the control mode to torque and configures appropriate settings.
        
        Returns:
            bool: True if configuration successful
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        # Minimal implementation: set control mode only.
        return self.set_control_mode("Torque")

    def configure_gpio1_analog_torque_mapping(self,
                                              analog_min=-3.874,
                                              analog_max=2.0,
                                              enable_gpio_num=7,
                                              control_mode='Position'):
        """
        Configure ODrive so GPIO1 analog input maps to controller input_torque,
        while the axis runs in POSITION_CONTROL with INPUT_MODE_PASSTHROUGH.

        This mirrors the parameters shown in the ODrive UI screenshots provided
        for this project.
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False

        try:
            axis = self.axis
            odrv = self.odrv

            # Core controller mode (user-selectable: Position default or Torque).
            if str(control_mode).lower() == 'torque':
                axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
                self.control_mode = CONTROL_MODE_TORQUE_CONTROL
            else:
                axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
                self.control_mode = CONTROL_MODE_POSITION_CONTROL

            # Input mode: prefer typed enum if present, fallback to constant.
            try:
                from odrive.enums import InputMode
                axis.controller.config.input_mode = InputMode.PASSTHROUGH
            except Exception:
                axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH

            # Enable pin config (axis0.enable_pin.config.*)
            try:
                axis.enable_pin.config.enabled = True
                axis.enable_pin.config.gpio_num = int(enable_gpio_num)
                axis.enable_pin.config.is_active_high = False
            except Exception as e:
                print(f"ERROR: Failed to configure enable pin: {e}")
                return False

            # GPIO modes (odrv.config.gpio*_mode)
            # Use direct constants from odrive.enums; these exist across ODrive fw variants.
            try:
                odrv.config.gpio5_mode = GPIO_MODE_DIGITAL
                odrv.config.gpio7_mode = GPIO_MODE_DIGITAL_PULL_UP
                odrv.config.gpio8_mode = GPIO_MODE_DIGITAL_PULL_UP
            except Exception as e:
                print(f"ERROR: Failed to set gpio*_mode: {e}")
                return False

            # Circular setpoints / mapping (axis0.controller + axis0.pos_vel_mapper)
            try:
                axis.controller.config.circular_setpoints = True
                axis.controller.config.circular_setpoint_range = 200
                axis.pos_vel_mapper.config.circular = True
                axis.pos_vel_mapper.config.circular_output_range = 200
                axis.controller.config.steps_per_circular_range = 819200
                axis.controller.config.vel_limit = 20
            except Exception as e:
                print(f"ERROR: Failed to set circular/limit parameters: {e}")
                return False

            # GPIO1 analog mapping
            try:
                odrv.config.gpio1_mode = GpioMode.ANALOG_IN
                odrv.config.gpio1_analog_mapping.min = float(analog_min)
                odrv.config.gpio1_analog_mapping.max = float(analog_max)
                # Endpoint must be torque input property (per user instruction)
                odrv.config.gpio1_analog_mapping.endpoint = axis.controller._input_torque_property
            except Exception as e:
                print(f"ERROR: Failed to configure gpio1_analog_mapping: {e}")
                return False

            if not self.ensure_gpio1_analog_in():
                print("ERROR: GPIO1 failed to remain in ANALOG_IN mode after configuration")
                return False

            print(f"ODrive configured for PWM->GPIO1 analog torque mapping ({control_mode.upper()} / PASSTHROUGH).")
            return True

        except Exception as e:
            print(f"ERROR: Failed to configure GPIO1 analog mapping: {e}")
            return False

    def _set_gpio1_analog_endpoint_none_best_effort(self):
        if not self.connected or self.odrv is None:
            return False
        try:
            self.odrv.config.gpio1_analog_mapping.endpoint = None
            return True
        except Exception:
            return False

    def _set_gpio1_analog_endpoint_torque_best_effort(self):
        if not self.connected or self.odrv is None or self.axis is None:
            return False
        try:
            self.odrv.config.gpio1_analog_mapping.endpoint = self.axis.controller._input_torque_property
            return True
        except Exception:
            return False
    
    def enter_closed_loop(self):
        """
        Enter closed-loop control state on ODrive.
        This must be called before sending torque commands via CAN.
        
        Returns:
            bool: True if successful
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        
        try:
            if not self.ensure_gpio1_analog_in():
                print("ERROR: GPIO1 is not in ANALOG_IN mode before entering closed-loop")
                return False
            # Safety: only listen to analog command when entering closed-loop.
            self._set_gpio1_analog_endpoint_torque_best_effort()
            if not self.ensure_gpio1_analog_in():
                print("ERROR: GPIO1 is not in ANALOG_IN mode after restoring analog endpoint")
                return False

            # Request closed-loop control state
            self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            
            # Wait for state transition (with timeout)
            import time
            timeout = 2.0  # 2 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.axis.current_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
                    self.ensure_gpio1_analog_in()
                    print("ODrive entered closed-loop control state")
                    return True
                time.sleep(0.1)
            
            # Check final state
            if self.axis.current_state == AXIS_STATE_CLOSED_LOOP_CONTROL:
                self.ensure_gpio1_analog_in()
                print("ODrive entered closed-loop control state")
                return True
            else:
                print(f"WARNING: ODrive state is {self.axis.current_state}, expected {AXIS_STATE_CLOSED_LOOP_CONTROL}")
                return False
            
        except Exception as e:
            print(f"ERROR: Failed to enter closed-loop control: {e}")
            return False
    
    def exit_closed_loop(self):
        """
        Exit closed-loop control state and return to IDLE.
        This should be called after acquisition completes.
        
        Returns:
            bool: True if successful
        """
        if not self.connected:
            print("ERROR: Not connected to ODrive")
            return False
        
        try:
            # Request IDLE state
            self.axis.requested_state = AXIS_STATE_IDLE
            
            # Wait for state transition (with timeout)
            import time
            timeout = 2.0  # 2 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.axis.current_state == AXIS_STATE_IDLE:
                    print("ODrive returned to IDLE state")
                    # Safety: stop listening to analog command while idle.
                    self._set_gpio1_analog_endpoint_none_best_effort()
                    self.ensure_gpio1_analog_in()
                    return True
                time.sleep(0.1)
            
            # Check final state
            if self.axis.current_state == AXIS_STATE_IDLE:
                print("ODrive returned to IDLE state")
                # Safety: stop listening to analog command while idle.
                self._set_gpio1_analog_endpoint_none_best_effort()
                self.ensure_gpio1_analog_in()
                return True
            else:
                print(f"WARNING: ODrive state is {self.axis.current_state}, expected {AXIS_STATE_IDLE}")
                return False
            
        except Exception as e:
            print(f"ERROR: Failed to exit closed-loop control: {e}")
            return False
    
    def configure_capture(self, sample_rate):
        """
        Configure high-rate data capture buffer.
        NOTE: Not used for Controllino implementation (no position feedback retrieved).
        
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
            
            print(f"Capture rate configured: {sample_rate} Hz (not used - no position feedback)")
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
            try:
                status.update(self.get_gpio1_state())
            except Exception:
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

