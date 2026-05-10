# Arduino Due Connection Troubleshooting Guide

## Current Status
Your Arduino Due is detected on COM4, but we're encountering permission issues. This is usually because the Arduino IDE is keeping the port open.

## Step-by-Step Solution

### 1. Close Arduino IDE Completely
- **Important**: The Arduino IDE keeps the serial port open even when not actively uploading
- Close the Arduino IDE completely (don't just minimize it)
- Also close any Serial Monitor windows that might be open

### 2. Check for Other Applications Using the Port
- Open Windows Task Manager (Ctrl+Shift+Esc)
- Look for any other applications that might be using COM4
- End any processes that might be accessing the Arduino

### 3. Run the Test as Administrator
- Right-click on Command Prompt or PowerShell
- Select "Run as administrator"
- Navigate to your project directory: `cd E:\ArduinoFirmataController`
- Run the test: `python test_connection.py`

### 4. If Still Failing - Try Another Port
The Arduino Due has two USB ports:
- **Programming Port**: Used for uploading sketches (currently showing as COM4)
- **Native USB Port**: Can be used for serial communication

Try:
1. Unplug the USB cable from the Programming Port
2. Plug it into the Native USB Port (the one closest to the center of the board)
3. Run the port detection again: `python test_connection.py`
4. Look for a new COM port for the Native USB connection

### 5. Verify StandardFirmataPlus is Uploaded
Make sure the Arduino Due is running the StandardFirmataPlus sketch:
1. Open Arduino IDE (temporary)
2. Select Tools > Board > Arduino Due (Programming Port)
3. Select the correct COM port
4. Open File > Examples > Firmata > StandardFirmataPlus
5. Upload the sketch
6. Close Arduino IDE completely
7. Try the connection test again

## Python Compatibility Fix Applied
I've already fixed the Python compatibility issue with `inspect.getargspec` in both the test script and main application.

## Next Steps
Once the connection test passes:
1. Run the main application: `python src/main.py`
2. Select "Arduino Due" from the board type dropdown
3. Select COM4 (or the Native USB port if that's what you're using)
4. Click Connect

## Common Issues and Solutions

### "Access is denied" Error
- Run as administrator
- Close Arduino IDE completely
- Check for other applications using the port

### "No response from board" Error
- Ensure StandardFirmataPlus sketch is uploaded
- Try the Native USB port instead of Programming Port
- Check USB cable (some cables only provide power)

### "Port not found" Error
- Refresh the port list in the application
- Try a different USB cable
- Check if Arduino is powered (LED should be on)

## Additional Resources
- Arduino Due documentation: https://docs.arduino.cc/hardware/arduino-due
- Firmata protocol: https://github.com/firmata/protocol
- pyfirmata library: https://github.com/firmata/pyfirmata