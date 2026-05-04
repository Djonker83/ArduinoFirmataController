# Arduino Firmata Controller - Setup Guide

## Quick Start

### Option 1: Using the Batch File (Windows)
Simply double-click the `run.bat` file in the project root directory. This batch file will:
- Check for Python installation
- Install required dependencies (pyserial, pyfirmata, PyQt6)
- Launch the application

### Option 2: Manual Installation

1. **Install Python** (3.7 or higher)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```
   python src/main.py
   ```

### Option 3: Development Setup

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd ArduinoFirmataController
   ```

2. **Create a Virtual Environment** (recommended)
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```
   python src/main.py
   ```

## Arduino Setup

1. **Install Arduino IDE**
   - Download from [arduino.cc](https://www.arduino.cc/en/software)

2. **Upload StandardFirmata Sketch**
   - Open Arduino IDE
   - Go to `File > Examples > Firmata > StandardFirmata`
   - Connect your Arduino board
   - Select the correct board and port from `Tools > Board` and `Tools > Port`
   - Click the Upload button

3. **Verify Connection**
   - The application should automatically detect your Arduino when you click "Refresh"
   - Select the correct board type and port
   - Click "Connect"

## Troubleshooting

### Connection Issues
- Make sure the Arduino is running the StandardFirmata sketch
- Check that the correct port is selected
- Try unplugging and reconnecting the Arduino
- Ensure no other applications are using the same serial port

### Dependency Issues
- Make sure you have Python 3.7 or higher
- Try installing dependencies individually:
  ```
  pip install pyserial
  pip install pyfirmata
  pip install PyQt6
  ```
- If PyQt6 installation fails, try PyQt5 instead:
  ```
  pip install PyQt5
  ```

### GUI Issues
- If the interface doesn't display correctly, try updating your graphics drivers
- On Linux, you may need to install additional Qt packages:
  ```
  sudo apt-get install python3-pyqt6
  ```

## Project Structure

```
ArduinoFirmataController/
├── src/
│   └── main.py                 # Main application file
├── docs/
│   └── SETUP_GUIDE.md          # This setup guide
├── tests/                      # Test files (empty for now)
├── .gitignore                  # Git ignore file
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows batch file for easy execution
└── setup.py                    # Setup script for packaging
```

## Development Notes

- The application supports both PyQt5 and PyQt6
- Board configurations are defined in the `BOARD_CONFIGS` dictionary
- Pin modes are implemented as an enum for better type safety
- The GUI uses a tabbed interface to organize digital and analog pins
- Each pin has a dropdown menu to select its mode
- Real-time pin values are displayed in the monitor panel