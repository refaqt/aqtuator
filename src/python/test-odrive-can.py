#!/usr/bin/env python3
"""
Simple ODrive S1 CAN Torque Control Example
Sends torque commands to ODrive via CAN bus
"""

import can
import struct
import time

# ============= CONFIGURATION =============
CAN_INTERFACE = 'gs_usb'  # For Linux with SocketCAN
CAN_CHANNEL = 0         # Your CAN interface name
CAN_BITRATE = 250000         # Must match ODrive's configured baud rate

ODRIVE_NODE_ID = 0           # Must match your ODrive's node_id
TORQUE_NM = 0.05            # Torque to apply in Newton-meters (start small!)

# CAN Command IDs
CMD_SET_AXIS_STATE = 0x07
CMD_SET_INPUT_TORQUE = 0x0E
CMD_GET_ENCODER_ESTIMATES = 0x09

# Axis States
AXIS_STATE_IDLE = 1
AXIS_STATE_CLOSED_LOOP_CONTROL = 8

# ============= MAIN PROGRAM =============

def main():
    # Initialize CAN bus
    print(f"Connecting to CAN bus: {CAN_CHANNEL} @ {CAN_BITRATE} bps")
    try:
        bus = can.Bus(interface=CAN_INTERFACE, 
                      channel=CAN_CHANNEL, 
                      bitrate=CAN_BITRATE)
    except Exception as e:
        print(f"Error connecting to CAN bus: {e}")
        print("\nOn Linux, you may need to set up the interface first:")
        print(f"  sudo ip link set {CAN_CHANNEL} type can bitrate {CAN_BITRATE}")
        print(f"  sudo ip link set {CAN_CHANNEL} up")
        return

    print("CAN bus connected successfully!\n")

    # Step 1: Enter CLOSED_LOOP_CONTROL state
    print(f"Step 1: Commanding ODrive (node {ODRIVE_NODE_ID}) to enter CLOSED_LOOP_CONTROL...")
    msg = can.Message(
        arbitration_id=(ODRIVE_NODE_ID << 5) | CMD_SET_AXIS_STATE,
        data=struct.pack('<I', AXIS_STATE_CLOSED_LOOP_CONTROL),
        is_extended_id=False
    )
    
    try:
        bus.send(msg)
        print("  ✓ Closed loop control command sent")
        time.sleep(0.5)  # Give ODrive time to transition
    except can.CanError as e:
        print(f"  ✗ Failed to send command: {e}")
        bus.shutdown()
        return

    # Step 2: Send torque command
    print(f"\nStep 2: Sending torque command: {TORQUE_NM} Nm")
    msg = can.Message(
        arbitration_id=(ODRIVE_NODE_ID << 5) | CMD_SET_INPUT_TORQUE,
        data=struct.pack('<f', TORQUE_NM),  # 32-bit float, little-endian
        is_extended_id=False
    )
    
    try:
        bus.send(msg)
        print(f"  ✓ Torque command sent: {TORQUE_NM} Nm")
    except can.CanError as e:
        print(f"  ✗ Failed to send torque: {e}")
        bus.shutdown()
        return

    # Step 3: Monitor feedback for a few seconds
    print("\nStep 3: Monitoring encoder feedback (Ctrl+C to stop)...")
    print("Position [turns] | Velocity [turns/s]")
    print("-" * 40)
    
    try:
        timeout = time.time() + 5  # Monitor for 5 seconds
        while time.time() < timeout:
            msg = bus.recv(timeout=0.1)
            if msg and msg.arbitration_id == ((ODRIVE_NODE_ID << 5) | CMD_GET_ENCODER_ESTIMATES):
                pos, vel = struct.unpack('<ff', bytes(msg.data))
                print(f"{pos:15.3f} | {vel:15.3f}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    # Step 4: Stop the motor (set torque to 0 and return to IDLE)
    print("\nStep 4: Stopping motor...")
    
    # Zero torque
    msg = can.Message(
        arbitration_id=(ODRIVE_NODE_ID << 5) | CMD_SET_INPUT_TORQUE,
        data=struct.pack('<f', 0.0),
        is_extended_id=False
    )
    bus.send(msg)
    time.sleep(0.1)
    
    # Return to IDLE
    msg = can.Message(
        arbitration_id=(ODRIVE_NODE_ID << 5) | CMD_SET_AXIS_STATE,
        data=struct.pack('<I', AXIS_STATE_IDLE),
        is_extended_id=False
    )
    bus.send(msg)
    print("  ✓ Motor stopped and returned to IDLE")
    
    # Cleanup
    bus.shutdown()
    print("\nDone!")


if __name__ == "__main__":
    print("=" * 50)
    print("ODrive S1 CAN Torque Control Example")
    print("=" * 50)
    print()
    main()