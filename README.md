# Arduino Firmata Controller - Optimized Version

## Overview

This is an optimized version of the Arduino Firmata Controller with enhanced GUI capabilities for different Arduino board types. The application provides a configurable interface for controlling Arduino boards via the Firmata protocol.

## Key Improvements

### 1. Board Type Configuration
- **Support for Multiple Boards**: Added configurations for Arduino Uno, Mega, Due, ESP32 Dev, and ESP8266 (NodeMCU)
- **Dynamic Pin Configuration**: The interface automatically adapts to the selected board type, showing only the relevant pins
- **Board Information Display**: Shows detailed information about the selected board including pin counts and capabilities

### 2. Enhanced Pin Configuration
- **Per-Pin Mode Selection**: Each pin now has a dropdown menu to select its mode (Digital Input/Output, PWM, Analog Input, Servo, Disabled)
- **Mode-Specific Controls**: Appropriate controls are dynamically created based on the selected pin mode
- **Real-time Value Display**: Shows current values for input pins and output states

### 3. Improved GUI Organization
- **Tabbed Interface**: Separated digital and analog pins into organized tabs
- **Pin Values Monitor**: Added a dedicated monitor to track all pin values in real-time
- **Scrollable Pin Lists**: Allows for boards with many pins (like Mega and ESP32)

### 4. Code Optimization
- **Better Error Handling**: Improved exception handling throughout the application
- **Resource Management**: Proper cleanup of resources and threads
- **Type Hints**: Added type annotations for better code maintainability
- **Data Structures**: Used enums and dataclasses for cleaner, more maintainable code

## Installation

1. Install the required dependencies:
```
pip install pyserial pyfirmata PyQt6
```

Or if you prefer PyQt5:
```
pip install pyserial pyfirmata PyQt5
```

2. Upload the StandardFirmata sketch to your Arduino board:
   - Open the Arduino IDE
   - Go to File > Examples > Firmata > StandardFirmata
   - Upload the sketch to your board

## Usage

1. Run the application:
```
python guimata_optimized.py
```

2. Connect your Arduino board to your computer

3. In the application:
   - Click "Refresh" to scan for available ports
   - Select your board type from the dropdown
   - Select the correct port
   - Click "Connect"

4. Configure your pins:
   - Each pin has a dropdown to select its mode
   - Switch between the Digital and Analog tabs to access all pins
   - The interface will automatically create appropriate controls based on your selection

## Supported Boards

### Arduino Uno
- Digital pins: 0-13
- PWM pins: 3, 5, 6, 9, 10, 11
- Analog pins: A0-A5

### Arduino Mega
- Digital pins: 0-53
- PWM pins: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 44, 45, 46
- Analog pins: A0-A15

### Arduino Due
- Digital pins: 0-53
- PWM pins: 2-13
- Analog pins: A0-A11

### ESP32 Dev
- Digital pins: 0-39
- PWM pins: 2-39 (most pins support PWM)
- Analog pins: 0, 2, 4, 12, 13, 14, 15, 25, 26, 27, 32, 33, 34, 35, 36, 39

### ESP8266 (NodeMCU)
- Digital pins: 0-16
- PWM pins: 0-16 (all pins support PWM)
- Analog pins: A0 only

## Pin Modes

- **Digital Input**: Reads digital state (HIGH/LOW)
- **Digital Output**: Controls digital state with a toggle button
- **PWM**: Controls analog output with a slider (0-255)
- **Analog Input**: Reads analog voltage (0-5V)
- **Servo**: Controls servo angle with a slider (0-180°)
- **Disabled**: Pin is not used

## Troubleshooting

If you encounter connection issues:

1. Make sure your Arduino is running the StandardFirmata sketch
2. Check that the correct port is selected
3. Ensure the board type matches your hardware
4. Try unplugging and reconnecting the Arduino

## Future Enhancements

Potential improvements for future versions:

1. **Save/Load Configurations**: Ability to save and load pin configurations
2. **I2C/SPI Support**: Add support for I2C and SPI communication protocols
3. **Scripting Interface**: Add a scripting interface for automated control
4. **Visual Pin Status**: Add visual indicators for pin states
5. **Custom Pin Groups**: Allow users to create custom pin groups for easier management