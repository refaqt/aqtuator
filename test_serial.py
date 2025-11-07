#!/usr/bin/env python3
"""
Minimal CSV upload test script for Arduino.
Uploads multisine_optimized.csv to test serial communication.
"""

import serial
import serial.tools.list_ports
import time
import sys
import os
import threading

# CSV file path
CSV_FILE = "src/python/multisine_optimized.csv"

def find_csv_file():
    """Find the CSV file in common locations."""
    # Try current directory first
    if os.path.exists(CSV_FILE):
        return CSV_FILE
    
    # Try relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, CSV_FILE)
    if os.path.exists(csv_path):
        return csv_path
    
    # Try just the filename
    if os.path.exists("multisine_optimized.csv"):
        return "multisine_optimized.csv"
    
    return None

def read_csv_data(csv_path):
    """Read CSV file and extract data lines (excluding comments/headers)."""
    data_lines = []
    with open(csv_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Skip comment lines and header row
            if line.startswith('#') or line.lower() == 'time_s,signal':
                continue
            data_lines.append(line)
    return data_lines

def upload_csv(port_name, csv_path, baud_rate=115200):
    """Upload CSV file to Arduino."""
    print(f"CSV Upload Test Script")
    print(f"{'='*60}")
    print(f"Port: {port_name}")
    print(f"CSV File: {csv_path}")
    print(f"{'='*60}\n")
    
    # Read CSV data
    print("Reading CSV file...")
    data_lines = read_csv_data(csv_path)
    print(f"Found {len(data_lines)} data lines")
    
    if len(data_lines) == 0:
        print("ERROR: No data lines found in CSV file")
        return False
    
    try:
        # Connect to serial port
        print(f"\nConnecting to {port_name} at {baud_rate} baud...")
        ser = serial.Serial(port_name, baud_rate, timeout=1, write_timeout=30)
        time.sleep(2)  # Wait for Arduino to initialize
        print("✓ Connected\n")
        
        # Clear input buffer
        print("Clearing input buffer...")
        if ser.in_waiting > 0:
            stale_data = ser.read(ser.in_waiting)
            print(f"  Cleared {len(stale_data)} bytes")
        else:
            print("  Buffer already clean")
        
        # Send UPLOAD_CSV command
        print(f"\nSending UPLOAD_CSV command ({len(data_lines)} lines)...")
        cmd = f"UPLOAD_CSV,{len(data_lines)}\n"
        try:
            bytes_written = ser.write(cmd.encode())
            print(f"✓ Command sent ({bytes_written} bytes)")
        except Exception as e:
            print(f"✗ Failed to send command: {e}")
            ser.close()
            return False
        
        # Try to flush (ignore timeout)
        try:
            ser.flush()
        except:
            pass
        
        # Wait for READY, skipping DEBUG messages
        print("Waiting for READY...")
        ready_received = False
        timeout_count = 0
        max_timeout = 200  # 2 seconds
        
        while timeout_count < max_timeout and not ready_received:
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response == "READY":
                    ready_received = True
                    print("✓ READY received")
                elif response.startswith("DEBUG:"):
                    print(f"  [DEBUG] {response}")
                    continue
                else:
                    print(f"  Unexpected: {response}")
            else:
                timeout_count += 1
                time.sleep(0.01)
        
        if not ready_received:
            print("✗ Timeout waiting for READY")
            ser.close()
            return False
        
        # Send CSV data lines
        print(f"\nSending {len(data_lines)} CSV lines...")
        for i, line in enumerate(data_lines):
            try:
                ser.write((line + '\n').encode())
                if (i + 1) % 100 == 0:
                    print(f"  Sent {i + 1}/{len(data_lines)} lines...")
            except Exception as e:
                print(f"✗ Failed to send line {i+1}: {e}")
                ser.close()
                return False
        
        # Flush output
        try:
            ser.flush()
        except:
            pass
        print("✓ All lines sent")
        
        # Wait for ACK/NACK, skipping DEBUG/INFO messages
        print("\nWaiting for ACK/NACK...")
        ack_received = False
        timeout_count = 0
        max_timeout = 500  # 5 seconds
        
        while timeout_count < max_timeout and not ack_received:
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response == "ACK: CSV loaded":
                    ack_received = True
                    print("✓ ACK received - CSV uploaded successfully!")
                elif response.startswith("NACK:"):
                    ack_received = True
                    error_msg = response[6:] if len(response) > 6 else "CSV load failed"
                    print(f"✗ NACK received: {error_msg}")
                elif response.startswith("DEBUG:") or response.startswith("INFO:"):
                    print(f"  [{response.split(':')[0]}] {response}")
                    continue
                else:
                    print(f"  Unexpected: {response}")
            else:
                timeout_count += 1
                time.sleep(0.01)
        
        if not ack_received:
            print("✗ Timeout waiting for ACK/NACK")
            ser.close()
            return False
        
        ser.close()
        print("\n✓ Upload complete!")
        return True
        
    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# ============================================================================
# Diagnostic Tests
# ============================================================================

def test_with_threading(port_name, csv_path, baud_rate=115200):
    """Test CSV upload in a separate thread (simulate QThread behavior)."""
    print(f"\n{'='*60}")
    print("TEST: Threading Simulation")
    print(f"{'='*60}\n")
    
    result = {'success': False, 'error': None}
    
    def upload_in_thread():
        try:
            result['success'] = upload_csv(port_name, csv_path, baud_rate)
        except Exception as e:
            result['error'] = str(e)
    
    thread = threading.Thread(target=upload_in_thread)
    thread.start()
    thread.join(timeout=60)  # 60 second timeout
    
    if thread.is_alive():
        print("✗ Thread still running after timeout")
        return False
    
    if result['error']:
        print(f"✗ Thread error: {result['error']}")
        return False
    
    return result['success']

def test_buffer_states(port_name, csv_path, baud_rate=115200):
    """Test buffer states during CSV upload."""
    print(f"\n{'='*60}")
    print("TEST: Buffer State Monitoring")
    print(f"{'='*60}\n")
    
    data_lines = read_csv_data(csv_path)
    if len(data_lines) == 0:
        print("ERROR: No data lines found")
        return False
    
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=1, write_timeout=30)
        time.sleep(2)
        
        # Check initial buffer state
        print(f"Initial state:")
        print(f"  in_waiting: {ser.in_waiting}")
        print(f"  out_waiting: {getattr(ser, 'out_waiting', 'N/A')}")
        
        # Clear buffer
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
        
        # Send command and monitor
        cmd = f"UPLOAD_CSV,{len(data_lines)}\n"
        bytes_written = ser.write(cmd.encode())
        print(f"\nAfter command write:")
        print(f"  bytes_written: {bytes_written}")
        print(f"  in_waiting: {ser.in_waiting}")
        
        # Wait for READY
        ready_received = False
        timeout_count = 0
        while timeout_count < 200 and not ready_received:
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response == "READY":
                    ready_received = True
                    print(f"  READY received, in_waiting: {ser.in_waiting}")
                elif response.startswith("DEBUG:"):
                    continue
            else:
                timeout_count += 1
                time.sleep(0.01)
        
        if not ready_received:
            print("✗ READY not received")
            ser.close()
            return False
        
        # Monitor buffer during CSV sending
        print(f"\nSending CSV lines, monitoring buffer...")
        buffer_samples = []
        for i, line in enumerate(data_lines):
            if i % 100 == 0:
                buffer_samples.append((i, ser.in_waiting))
            
            try:
                ser.write((line + '\n').encode())
            except Exception as e:
                print(f"✗ Failed at line {i+1}: {e}")
                print(f"  in_waiting: {ser.in_waiting}")
                ser.close()
                return False
        
        print(f"\nBuffer samples during send:")
        for line_num, in_waiting in buffer_samples:
            print(f"  Line {line_num}: in_waiting={in_waiting}")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_write_timeout(port_name, csv_path, baud_rate=115200):
    """Test write timeout behavior."""
    print(f"\n{'='*60}")
    print("TEST: Write Timeout Behavior")
    print(f"{'='*60}\n")
    
    data_lines = read_csv_data(csv_path)
    if len(data_lines) == 0:
        print("ERROR: No data lines found")
        return False
    
    try:
        # Test with different write_timeout values
        for write_timeout in [1, 5, 10, 30]:
            print(f"\nTesting with write_timeout={write_timeout}s...")
            try:
                ser = serial.Serial(port_name, baud_rate, timeout=1, write_timeout=write_timeout)
                time.sleep(2)
                
                # Clear buffer
                if ser.in_waiting > 0:
                    ser.read(ser.in_waiting)
                
                # Send command
                cmd = f"UPLOAD_CSV,{len(data_lines)}\n"
                start_time = time.time()
                try:
                    bytes_written = ser.write(cmd.encode())
                    write_time = time.time() - start_time
                    print(f"  Command write: {bytes_written} bytes in {write_time:.3f}s")
                except serial.SerialTimeoutException as e:
                    print(f"  ✗ Command write timeout: {e}")
                    ser.close()
                    continue
                
                # Wait for READY
                ready_received = False
                timeout_count = 0
                while timeout_count < 200 and not ready_received:
                    if ser.in_waiting > 0:
                        response = ser.readline().decode().strip()
                        if response == "READY":
                            ready_received = True
                        elif response.startswith("DEBUG:"):
                            continue
                    else:
                        timeout_count += 1
                        time.sleep(0.01)
                
                if not ready_received:
                    print(f"  ✗ READY not received")
                    ser.close()
                    continue
                
                # Try sending a few lines to test timeout
                print(f"  Testing line writes...")
                timeout_occurred = False
                for i in range(min(10, len(data_lines))):
                    start_time = time.time()
                    try:
                        ser.write((data_lines[i] + '\n').encode())
                        write_time = time.time() - start_time
                        if write_time > 0.1:
                            print(f"    Line {i+1}: {write_time:.3f}s (slow!)")
                    except serial.SerialTimeoutException as e:
                        print(f"    ✗ Line {i+1} timeout: {e}")
                        timeout_occurred = True
                        break
                
                ser.close()
                if timeout_occurred:
                    print(f"  ✗ Timeout occurred with write_timeout={write_timeout}s")
                else:
                    print(f"  ✓ No timeout with write_timeout={write_timeout}s")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_line_820(port_name, csv_path, baud_rate=115200):
    """Test specifically around line 820 where timeout occurs."""
    print(f"\n{'='*60}")
    print("TEST: Line 820 Specific Test")
    print(f"{'='*60}\n")
    
    data_lines = read_csv_data(csv_path)
    if len(data_lines) == 0:
        print("ERROR: No data lines found")
        return False
    
    if len(data_lines) < 820:
        print(f"WARNING: Only {len(data_lines)} lines, cannot test line 820")
        return False
    
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=1, write_timeout=30)
        time.sleep(2)
        
        # Clear buffer
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
        
        # Send command
        cmd = f"UPLOAD_CSV,{len(data_lines)}\n"
        ser.write(cmd.encode())
        try:
            ser.flush()
        except:
            pass
        
        # Wait for READY
        ready_received = False
        timeout_count = 0
        while timeout_count < 200 and not ready_received:
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response == "READY":
                    ready_received = True
                elif response.startswith("DEBUG:"):
                    continue
            else:
                timeout_count += 1
                time.sleep(0.01)
        
        if not ready_received:
            print("✗ READY not received")
            ser.close()
            return False
        
        # Monitor around line 820
        print(f"Monitoring around line 820...")
        print(f"  Checking buffer state before line 815...")
        
        # Send lines up to 815
        for i in range(815):
            try:
                ser.write((data_lines[i] + '\n').encode())
            except Exception as e:
                print(f"✗ Failed at line {i+1}: {e}")
                ser.close()
                return False
        
        print(f"  in_waiting before line 820: {ser.in_waiting}")
        
        # Test lines 815-825 specifically
        print(f"  Testing lines 815-825...")
        for i in range(815, min(825, len(data_lines))):
            start_time = time.time()
            try:
                ser.write((data_lines[i] + '\n').encode())
                write_time = time.time() - start_time
                if write_time > 0.1:
                    print(f"    Line {i+1}: {write_time:.3f}s (slow!)")
                if i == 819:
                    print(f"    Line 820: {write_time:.3f}s, in_waiting: {ser.in_waiting}")
            except serial.SerialTimeoutException as e:
                print(f"    ✗ Line {i+1} timeout: {e}")
                print(f"      in_waiting: {ser.in_waiting}")
                ser.close()
                return False
            except Exception as e:
                print(f"    ✗ Line {i+1} error: {e}")
                ser.close()
                return False
        
        ser.close()
        print("✓ Line 820 test passed")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_serial_port_state(port_name, baud_rate=115200):
    """Test serial port configuration and state."""
    print(f"\n{'='*60}")
    print("TEST: Serial Port State")
    print(f"{'='*60}\n")
    
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=1, write_timeout=30)
        time.sleep(2)
        
        print("Serial port configuration:")
        print(f"  port: {ser.port}")
        print(f"  baudrate: {ser.baudrate}")
        print(f"  timeout: {ser.timeout}")
        print(f"  write_timeout: {ser.write_timeout}")
        print(f"  bytesize: {ser.bytesize}")
        print(f"  parity: {ser.parity}")
        print(f"  stopbits: {ser.stopbits}")
        print(f"  is_open: {ser.is_open}")
        
        print(f"\nInitial buffer state:")
        print(f"  in_waiting: {ser.in_waiting}")
        
        # Try to get more info if available
        try:
            print(f"  out_waiting: {getattr(ser, 'out_waiting', 'N/A')}")
        except:
            pass
        
        # Test write capability
        print(f"\nTesting write capability...")
        test_data = b"TEST\n"
        start_time = time.time()
        try:
            bytes_written = ser.write(test_data)
            write_time = time.time() - start_time
            print(f"  Write test: {bytes_written} bytes in {write_time:.3f}s")
            
            # Try flush
            start_time = time.time()
            try:
                ser.flush()
                flush_time = time.time() - start_time
                print(f"  Flush test: {flush_time:.3f}s")
            except Exception as e:
                print(f"  Flush error (expected): {e}")
        except Exception as e:
            print(f"  ✗ Write error: {e}")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main function."""
    # Find CSV file
    csv_path = find_csv_file()
    if not csv_path:
        print("ERROR: Could not find multisine_optimized.csv")
        print("  Tried:")
        print(f"    - {CSV_FILE}")
        print(f"    - multisine_optimized.csv")
        return
    
    # List available ports
    ports = serial.tools.list_ports.comports()
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    if len(ports) == 0:
        print("\n✗ No serial ports found!")
        return
    
    # Get port name
    if len(sys.argv) > 1:
        port_name = sys.argv[1]
    else:
        if len(ports) == 1:
            port_name = ports[0].device
            print(f"\nUsing only available port: {port_name}")
        else:
            print("\nEnter port number or name:")
            choice = input("> ").strip()
            try:
                port_idx = int(choice) - 1
                if 0 <= port_idx < len(ports):
                    port_name = ports[port_idx].device
                else:
                    print("Invalid port number")
                    return
            except ValueError:
                port_name = choice
    
    # Run diagnostic tests
    if len(sys.argv) > 2:
        test_name = sys.argv[2]
        if test_name == "threading":
            success = test_with_threading(port_name, csv_path)
        elif test_name == "buffer":
            success = test_buffer_states(port_name, csv_path)
        elif test_name == "timeout":
            success = test_write_timeout(port_name, csv_path)
        elif test_name == "line820":
            success = test_line_820(port_name, csv_path)
        elif test_name == "portstate":
            success = test_serial_port_state(port_name)
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: threading, buffer, timeout, line820, portstate")
            return
    else:
        # Default: run normal upload
        success = upload_csv(port_name, csv_path)
    
    if success:
        print("\n✓ Test passed!")
    else:
        print("\n✗ Test failed!")
    
    print("\nTo run diagnostic tests:")
    print("  python test_serial.py <port> threading   - Test with threading")
    print("  python test_serial.py <port> buffer      - Test buffer states")
    print("  python test_serial.py <port> timeout    - Test write timeout")
    print("  python test_serial.py <port> line820    - Test line 820")
    print("  python test_serial.py <port> portstate  - Test port state")

if __name__ == "__main__":
    main()
