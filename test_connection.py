"""
Simple test script to verify Arduino Due connection with StandardFirmataPlus
"""

import serial
import serial.tools.list_ports
import time
import sys

# Fix inspect.getargspec issue with newer Python versions
import inspect
if not hasattr(inspect, 'getargspec'):
    import types
    class ArgSpec:
        def __init__(self, args, varargs, keywords, defaults):
            self.args = args
            self.varargs = varargs
            self.keywords = keywords
            self.defaults = defaults
    
    def getargspec(func):
        if isinstance(func, types.MethodType):
            func = func.__func__
        args = inspect.getfullargspec(func)
        return ArgSpec(
            args=args.args,
            varargs=args.varargs,
            keywords=args.varkw,
            defaults=args.defaults
        )
    inspect.getargspec = getargspec

import pyfirmata

def test_arduino_connection():
    """Test basic connection to Arduino Due"""
    print("Arduino Due Connection Test")
    print("=" * 40)
    
    # List available ports
    print("\n1. Scanning for serial ports...")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No serial ports found!")
        return False
    
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} - {port.description}")
    
    # Try to connect to each port
    print("\n2. Testing connections...")
    
    for port in ports:
        print(f"\nTesting {port.device} - {port.description}:")
        
        # Skip non-arduino ports if possible
        if "arduino" not in port.description.lower() and "due" not in port.description.lower():
            print("  (Skipping - doesn't look like an Arduino)")
            continue
        
        # Try different baud rates that Arduino Due might use
        baud_rates = [115200, 57600, 9600]
        
        for baud in baud_rates:
            try:
                print(f"  Trying {baud} baud...")
                
                # Try to create a board instance
                board = pyfirmata.Arduino(port.device, baudrate=baud)
                
                # Give it a moment to initialize
                time.sleep(2)
                
                # Try to get firmware info
                try:
                    firmware = board.get_firmware()
                    if firmware:
                        print(f"  ✓ Connected! Firmware: {firmware}")
                        
                        # Try a simple pin test
                        print("  Testing pin control...")
                        board.pin_mode(13, 'o')  # Set pin 13 to output
                        board.digital[13].write(1)  # Turn LED on
                        time.sleep(1)
                        board.digital[13].write(0)  # Turn LED off
                        
                        print("  ✓ Pin control test successful!")
                        
                        # Clean up
                        board.exit()
                        return True
                except Exception as e:
                    print(f"  ⚠ Connected but firmware test failed: {e}")
                    board.exit()
                    
            except Exception as e:
                print(f"  ✗ Failed at {baud}: {e}")
    
    print("\nNo successful connections found.")
    return False

if __name__ == "__main__":
    try:
        success = test_arduino_connection()
        if success:
            print("\n✓ Arduino Due connection test PASSED!")
            print("You can now run the main application with: python src/main.py")
        else:
            print("\n✗ Arduino Due connection test FAILED!")
            print("\nTroubleshooting tips:")
            print("1. Make sure Arduino Due is connected via USB")
            print("2. Ensure StandardFirmataPlus sketch is uploaded")
            print("3. Close Arduino IDE (it keeps the port open)")
            print("4. Try running as administrator on Windows")
            print("5. Check if the correct drivers are installed")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)