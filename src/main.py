"""
Arduino Firmata Controller with Qt GUI - Optimized Version
Detects Arduino boards automatically and provides configurable Firmata control for different board types
"""

import sys
import serial
import serial.tools.list_ports
import importlib
import importlib.util
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Dynamic PyQt import
if importlib.util.find_spec("PyQt6.QtWidgets"):
    qt_widgets = importlib.import_module("PyQt6.QtWidgets")
    qt_core = importlib.import_module("PyQt6.QtCore")
    qt_gui = importlib.import_module("PyQt6.QtGui")
    PYQT6 = True
else:
    qt_widgets = importlib.import_module("PyQt5.QtWidgets")
    qt_core = importlib.import_module("PyQt5.QtCore")
    qt_gui = importlib.import_module("PyQt5.QtGui")
    PYQT6 = False

# Import Qt classes
QApplication = qt_widgets.QApplication
QMainWindow = qt_widgets.QMainWindow
QWidget = qt_widgets.QWidget
QVBoxLayout = qt_widgets.QVBoxLayout
QHBoxLayout = qt_widgets.QHBoxLayout
QPushButton = qt_widgets.QPushButton
QComboBox = qt_widgets.QComboBox
QLabel = qt_widgets.QLabel
QTextEdit = qt_widgets.QTextEdit
QSpinBox = qt_widgets.QSpinBox
QSlider = qt_widgets.QSlider
QGroupBox = qt_widgets.QGroupBox
QGridLayout = qt_widgets.QGridLayout
QMessageBox = qt_widgets.QMessageBox
QTimer = qt_core.QTimer
Qt = qt_core.Qt
pyqtSignal = qt_core.pyqtSignal
QThread = qt_core.QThread
QFont = qt_gui.QFont
QTabWidget = qt_widgets.QTabWidget
QCheckBox = qt_widgets.QCheckBox

# Install with: pip install pyserial pyfirmata PyQt6
import pyfirmata


class PinMode(Enum):
    """Enumeration for pin modes"""
    DIGITAL_INPUT = "i"
    DIGITAL_OUTPUT = "o"
    PWM = "p"
    ANALOG = "a"
    SERVO = "s"
    I2C = "I2C"
    DISABLED = "d"


@dataclass
class BoardConfig:
    """Configuration for different Arduino board types"""
    name: str
    digital_pins: List[int]
    pwm_pins: List[int]
    analog_pins: List[int]
    total_pins: int
    description: str


# Board configurations for different Arduino types
BOARD_CONFIGS = {
    "Arduino Uno": BoardConfig(
        name="Arduino Uno",
        digital_pins=list(range(0, 14)),
        pwm_pins=[3, 5, 6, 9, 10, 11],
        analog_pins=[0, 1, 2, 3, 4, 5],
        total_pins=14,
        description="Standard Arduino Uno with ATmega328P"
    ),
    "Arduino Mega": BoardConfig(
        name="Arduino Mega",
        digital_pins=list(range(0, 54)),
        pwm_pins=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 44, 45, 46],
        analog_pins=list(range(0, 16)),
        total_pins=54,
        description="Arduino Mega with ATmega2560"
    ),
    "Arduino Due": BoardConfig(
        name="Arduino Due",
        digital_pins=list(range(0, 54)),
        pwm_pins=list(range(2, 14)),
        analog_pins=list(range(0, 12)),
        total_pins=54,
        description="Arduino Due with SAM3X8E"
    ),
    "ESP32 Dev": BoardConfig(
        name="ESP32 Dev",
        digital_pins=list(range(0, 40)),
        pwm_pins=list(range(2, 40)),  # ESP32 supports PWM on many pins
        analog_pins=[0, 2, 4, 12, 13, 14, 15, 25, 26, 27, 32, 33, 34, 35, 36, 39],
        total_pins=40,
        description="ESP32 Development Board"
    ),
    "ESP8266 (NodeMCU)": BoardConfig(
        name="ESP8266 (NodeMCU)",
        digital_pins=list(range(0, 17)),
        pwm_pins=list(range(0, 17)),  # ESP8266 supports PWM on all pins
        analog_pins=[0],
        total_pins=17,
        description="ESP8266 NodeMCU Development Board"
    ),
    "Auto-detect": BoardConfig(
        name="Auto-detect",
        digital_pins=list(range(0, 14)),
        pwm_pins=[3, 5, 6, 9, 10, 11],
        analog_pins=[0, 1, 2, 3, 4, 5],
        total_pins=14,
        description="Auto-detect board type (default to Uno)"
    ),
}


class PinConfigWidget(QWidget):
    """Widget for configuring individual pins"""
    
    config_changed = pyqtSignal(int, str)  # pin_number, mode
    
    def __init__(self, pin_number: int, board_config: BoardConfig):
        super().__init__()
        self.pin_number = pin_number
        self.board_config = board_config
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Pin label
        pin_label = QLabel(f"Pin {self.pin_number}")
        pin_label.setMinimumWidth(50)
        layout.addWidget(pin_label)
        
        # Mode selection dropdown
        self.mode_combo = QComboBox()
        available_modes = self.get_available_modes()
        for mode_name, mode_value in available_modes:
            self.mode_combo.addItem(mode_name, mode_value)
        
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        layout.addWidget(self.mode_combo)
        
        # Value display/controls based on mode
        self.value_display = QLabel("---")
        self.value_display.setMinimumWidth(50)
        layout.addWidget(self.value_display)
        
        # Set initial mode based on board configuration
        self.set_default_mode()
        
    def get_available_modes(self) -> List[Tuple[str, str]]:
        """Get available modes for this pin based on board configuration"""
        modes = [("Disabled", PinMode.DISABLED.value)]
        
        if self.pin_number in self.board_config.digital_pins:
            modes.extend([
                ("Digital Input", PinMode.DIGITAL_INPUT.value),
                ("Digital Output", PinMode.DIGITAL_OUTPUT.value)
            ])
        
        if self.pin_number in self.board_config.pwm_pins:
            modes.append(("PWM", PinMode.PWM.value))
            
        if self.pin_number in self.board_config.analog_pins:
            modes.append(("Analog Input", PinMode.ANALOG.value))
            
        # Add servo mode for PWM capable pins
        if self.pin_number in self.board_config.pwm_pins:
            modes.append(("Servo", PinMode.SERVO.value))
        
        return modes
    
    def set_default_mode(self):
        """Set default mode based on pin capabilities"""
        if self.pin_number in self.board_config.analog_pins:
            self.mode_combo.setCurrentText("Analog Input")
        elif self.pin_number in self.board_config.pwm_pins:
            self.mode_combo.setCurrentText("PWM")
        elif self.pin_number in self.board_config.digital_pins:
            self.mode_combo.setCurrentText("Digital Output")
        else:
            self.mode_combo.setCurrentText("Disabled")
    
    def on_mode_changed(self, mode_text):
        """Handle mode change for this pin"""
        mode_value = self.mode_combo.currentData()
        self.config_changed.emit(self.pin_number, mode_value)
        
        # Update value display based on mode
        self.update_value_display(mode_value)
    
    def update_value_display(self, mode_value):
        """Update the value display based on the selected mode"""
        if mode_value == PinMode.DISABLED.value:
            self.value_display.setText("---")
        elif mode_value == PinMode.DIGITAL_INPUT.value:
            self.value_display.setText("Read")
        elif mode_value == PinMode.DIGITAL_OUTPUT.value:
            self.value_display.setText("0")
        elif mode_value == PinMode.PWM.value:
            self.value_display.setText("0/255")
        elif mode_value == PinMode.ANALOG.value:
            self.value_display.setText("0.0V")
        elif mode_value == PinMode.SERVO.value:
            self.value_display.setText("90°")


class OptimizedSerialWorker(QThread):
    """Optimized worker thread for serial communication with better error handling and resource management"""
    
    data_received = pyqtSignal(str)
    connected = pyqtSignal(bool, str)
    pin_state_changed = pyqtSignal(int, str, object)  # pin, mode, value
    
    def __init__(self):
        super().__init__()
        self.board = None
        self.port = None
        self.board_type = None
        self.running = False
        self.iterator = None
        self.pin_modes = {}  # Track pin modes
        self.pin_values = {}  # Track pin values
        self.servo_angles = {}  # Track servo angles
        
    def connect_board(self, port: str, board_type: str = 'auto') -> bool:
        """Attempt to connect to Arduino on specified port with improved error handling"""
        try:
            self.port = port
            self.board_type = board_type
            
            # Check if port is available
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if port not in available_ports:
                self.connected.emit(False, f"Port {port} not found. Available ports: {', '.join(available_ports)}")
                return False
            
            # Try to open the port first to check accessibility
            test_serial = None
            try:
                test_serial = serial.Serial(port, 57600, timeout=2)
                test_serial.close()
            except serial.SerialException as e:
                if "Permission denied" in str(e):
                    self.connected.emit(False, f"Permission denied accessing {port}. Try running as administrator or check port permissions.")
                    return False
                elif "could not open port" in str(e).lower():
                    self.connected.emit(False, f"Port {port} is in use by another application. Close Arduino IDE or other serial monitoring tools.")
                    return False
                else:
                    self.connected.emit(False, f"Serial port error: {str(e)}")
                    return False
            
            # Create appropriate board instance
            try:
                # Monkey patch to fix inspect.getargspec issue with newer Python versions
                import inspect
                if not hasattr(inspect, 'getargspec'):
                    import types
                    def getargspec(func):
                        if isinstance(func, types.MethodType):
                            func = func.__func__
                        args = inspect.getfullargspec(func)
                        return inspect.ArgSpec(
                            args=args.args,
                            varargs=args.varargs,
                            keywords=args.varkw,
                            defaults=args.defaults
                        )
                    inspect.getargspec = getargspec
                
                if board_type == 'mega' or board_type == 'arduino mega':
                    self.board = pyfirmata.ArduinoMega(port)
                elif board_type == 'due' or board_type == 'arduino due':
                    self.board = pyfirmata.Arduino(port)  # Due uses same base class
                elif board_type == 'esp32' or board_type == 'esp32 dev':
                    self.board = pyfirmata.Arduino(port)  # ESP32 uses same base class
                elif board_type == 'esp8266' or board_type == 'nodeMCU':
                    self.board = pyfirmata.Arduino(port)  # ESP8266 uses same base class
                else:
                    self.board = pyfirmata.Arduino(port)  # Default to Arduino
            except Exception as e:
                error_msg = str(e)
                if "getargspec" in error_msg:
                    self.connected.emit(False, f"Python compatibility issue with pyfirmata library. This is a known issue with newer Python versions. Try updating pyfirmata: pip install --upgrade pyfirmata")
                else:
                    self.connected.emit(False, f"Error creating board instance: {error_msg}. Make sure Arduino is running StandardFirmata or ConfigurableFirmata sketch.")
                return False
            
            # Start iterator thread for analog inputs
            try:
                self.iterator = pyfirmata.util.Iterator(self.board)
                self.iterator.start()
                
                # Wait a moment for the board to initialize
                import time
                time.sleep(0.5)
                
                # Test basic communication
                if hasattr(self.board, 'get_firmware'):
                    try:
                        firmware = self.board.get_firmware()
                        if not firmware:
                            self.connected.emit(False, "No response from board. Make sure it's running StandardFirmata sketch.")
                            self.disconnect()
                            return False
                    except:
                        # Some boards might not support get_firmware, continue anyway
                        pass
                
            except Exception as e:
                self.connected.emit(False, f"Error initializing board communication: {str(e)}. The board might not be running StandardFirmata.")
                self.disconnect()
                return False
            
            self.running = True
            self.connected.emit(True, f"Connected to {port} as {board_type}")
            return True
            
        except serial.SerialException as e:
            self.connected.emit(False, f"Serial error: {str(e)}")
            return False
        except Exception as e:
            self.connected.emit(False, f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Safely disconnect from board with proper cleanup"""
        self.running = False
        
        if self.iterator:
            try:
                self.iterator.stop()
            except:
                pass
            self.iterator = None
            
        if self.board:
            try:
                self.board.exit()
            except:
                pass
            self.board = None
            
        self.pin_modes.clear()
        self.pin_values.clear()
        self.servo_angles.clear()
    
    def set_pin_mode(self, pin: int, mode: str):
        """Set pin mode with improved error handling and state tracking"""
        if not self.board:
            return False
            
        try:
            self.board.pin_mode(pin, mode)
            self.pin_modes[pin] = mode
            
            # Initialize pin value based on mode
            if mode == PinMode.DIGITAL_OUTPUT.value:
                self.digital_write(pin, 0)
            elif mode == PinMode.PWM.value:
                self.analog_write(pin, 0)
            elif mode == PinMode.SERVO.value:
                self.servo_write(pin, 90)
                
            self.pin_state_changed.emit(pin, mode, self.pin_values.get(pin, 0))
            self.data_received.emit(f"Pin {pin} set to {mode} mode")
            return True
            
        except Exception as e:
            self.data_received.emit(f"Error setting pin {pin} to {mode}: {e}")
            return False
    
    def digital_write(self, pin: int, value: int):
        """Write digital value (0 or 1) with error handling"""
        if not self.board:
            return False
            
        try:
            self.board.digital[pin].write(value)
            self.pin_values[pin] = value
            self.pin_state_changed.emit(pin, self.pin_modes.get(pin, ""), value)
            return True
        except Exception as e:
            self.data_received.emit(f"Error writing digital to pin {pin}: {e}")
            return False
    
    def analog_write(self, pin: int, value: int):
        """Write PWM value (0-255) with error handling"""
        if not self.board:
            return False
            
        try:
            self.board.analog[pin].write(value / 255.0)
            self.pin_values[pin] = value
            self.pin_state_changed.emit(pin, self.pin_modes.get(pin, ""), value)
            return True
        except Exception as e:
            self.data_received.emit(f"Error writing analog to pin {pin}: {e}")
            return False
    
    def servo_write(self, pin: int, angle: int):
        """Write servo angle (0-180)"""
        if not self.board:
            return False
            
        try:
            # Convert angle to PWM value (approximately 1000-2000 microseconds)
            pulse_width = 1000 + (angle * 1000 / 180)
            self.board.analog[pin].write(pulse_width / 255.0)
            self.servo_angles[pin] = angle
            self.pin_state_changed.emit(pin, self.pin_modes.get(pin, ""), angle)
            return True
        except Exception as e:
            self.data_received.emit(f"Error writing servo to pin {pin}: {e}")
            return False
    
    def digital_read(self, pin: int) -> Optional[int]:
        """Read digital pin with error handling"""
        if not self.board:
            return None
            
        try:
            value = self.board.digital[pin].read()
            if value is not None:
                self.pin_values[pin] = value
                self.pin_state_changed.emit(pin, self.pin_modes.get(pin, ""), value)
            return value
        except Exception as e:
            self.data_received.emit(f"Error reading digital pin {pin}: {e}")
            return None
    
    def analog_read(self, pin: int) -> Optional[float]:
        """Read analog pin with error handling"""
        if not self.board:
            return None
            
        try:
            value = self.board.analog[pin].read()
            if value is not None:
                self.pin_values[pin] = value
                self.pin_state_changed.emit(pin, self.pin_modes.get(pin, ""), value)
            return value
        except Exception as e:
            self.data_received.emit(f"Error reading analog pin {pin}: {e}")
            return None


class OptimizedArduinoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Firmata Controller - Optimized")
        self.setGeometry(100, 100, 1200, 800)
        
        # Worker thread for serial comms
        self.worker = OptimizedSerialWorker()
        self.worker.connected.connect(self.on_connection_result)
        self.worker.data_received.connect(self.log_message)
        self.worker.pin_state_changed.connect(self.on_pin_state_changed)
        
        self.current_board_config = BOARD_CONFIGS["Auto-detect"]
        self.pin_widgets = {}  # Track pin configuration widgets
        self.control_widgets = {}  # Track control widgets for pins
        
        self.init_ui()
        self.refresh_ports()
        
        # Timer to update readings
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_readings)
        
    def init_ui(self):
        """Initialize the optimized user interface"""
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        
        # Left panel - Connection & Configuration
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Connection Group
        conn_group = QGroupBox("Connection")
        conn_layout = QGridLayout(conn_group)
        
        conn_layout.addWidget(QLabel("Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        conn_layout.addWidget(self.port_combo, 0, 1)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(self.refresh_btn, 0, 2)
        
        conn_layout.addWidget(QLabel("Board Type:"), 1, 0)
        self.board_type = QComboBox()
        self.board_type.addItems(BOARD_CONFIGS.keys())
        self.board_type.currentTextChanged.connect(self.on_board_type_changed)
        conn_layout.addWidget(self.board_type, 1, 1)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_board)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        conn_layout.addWidget(self.connect_btn, 2, 0, 1, 3)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_board)
        self.disconnect_btn.setEnabled(False)
        conn_layout.addWidget(self.disconnect_btn, 3, 0, 1, 3)
        
        left_layout.addWidget(conn_group)
        
        # Board info display
        self.board_info = QLabel("No board selected")
        self.board_info.setWordWrap(True)
        self.board_info.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border: 1px solid #ccc; }")
        left_layout.addWidget(self.board_info)
        
        # Pin configuration tabs
        self.pin_tabs = QTabWidget()
        self.create_pin_tabs()
        left_layout.addWidget(self.pin_tabs)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel, 2)
        
        # Right panel - Status & Log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Status Group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        right_layout.addWidget(status_group)
        
        # Pin values monitor
        monitor_group = QGroupBox("Pin Values Monitor")
        monitor_layout = QVBoxLayout(monitor_group)
        
        self.pin_monitor = QTextEdit()
        self.pin_monitor.setReadOnly(True)
        self.pin_monitor.setFont(QFont("Consolas", 9))
        self.pin_monitor.setMaximumHeight(200)
        monitor_layout.addWidget(self.pin_monitor)
        
        right_layout.addWidget(monitor_group)
        
        # Troubleshooting Guide
        troubleshoot_group = QGroupBox("Troubleshooting Guide")
        troubleshoot_layout = QVBoxLayout(troubleshoot_group)
        
        self.troubleshoot_text = QTextEdit()
        self.troubleshoot_text.setReadOnly(True)
        self.troubleshoot_text.setFont(QFont("Arial", 8))
        self.troubleshoot_text.setMaximumHeight(150)
        self.troubleshoot_text.setHtml("""
        <b>Common Connection Issues:</b><br>
        1. <b>Arduino not running StandardFirmata:</b> Upload StandardFirmata sketch from Arduino IDE<br>
        2. <b>Port in use:</b> Close Arduino IDE and other serial monitors<br>
        3. <b>Permission denied:</b> Try running as administrator (Windows) or check port permissions<br>
        4. <b>Wrong board type:</b> Ensure board type matches your Arduino hardware<br>
        5. <b>USB connection:</b> Try different cable or USB port
        """)
        troubleshoot_layout.addWidget(self.troubleshoot_text)
        
        more_info_btn = QPushButton("More Help")
        more_info_btn.clicked.connect(self.show_troubleshooting_details)
        troubleshoot_layout.addWidget(more_info_btn)
        
        right_layout.addWidget(troubleshoot_group)
        
        # Log output
        log_group = QGroupBox("Communication Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log)
        
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.log.clear)
        log_layout.addWidget(clear_btn)
        
        right_layout.addWidget(log_group, 1)
        
        main_layout.addWidget(right_panel, 1)
        
        # Update board info display
        self.on_board_type_changed()
        
    def create_pin_tabs(self):
        """Create tabs for different pin types"""
        self.pin_tabs.clear()
        self.pin_widgets.clear()
        
        # Digital pins tab
        digital_tab = QWidget()
        digital_layout = QVBoxLayout(digital_tab)
        
        digital_scroll = QWidget()
        digital_scroll_layout = QVBoxLayout(digital_scroll)
        
        for pin in self.current_board_config.digital_pins:
            pin_widget = PinConfigWidget(pin, self.current_board_config)
            pin_widget.config_changed.connect(self.on_pin_config_changed)
            self.pin_widgets[pin] = pin_widget
            digital_scroll_layout.addWidget(pin_widget)
        
        digital_scroll_layout.addStretch()
        
        scroll_area = qt_widgets.QScrollArea()
        scroll_area.setWidget(digital_scroll)
        scroll_area.setWidgetResizable(True)
        
        digital_layout.addWidget(scroll_area)
        
        self.pin_tabs.addTab(digital_tab, "Digital Pins")
        
        # Analog pins tab
        analog_tab = QWidget()
        analog_layout = QVBoxLayout(analog_tab)
        
        analog_scroll = QWidget()
        analog_scroll_layout = QVBoxLayout(analog_scroll)
        
        for pin in self.current_board_config.analog_pins:
            pin_widget = PinConfigWidget(pin, self.current_board_config)
            pin_widget.config_changed.connect(self.on_pin_config_changed)
            self.pin_widgets[f"A{pin}"] = pin_widget
            analog_scroll_layout.addWidget(pin_widget)
        
        analog_scroll_layout.addStretch()
        
        scroll_area = qt_widgets.QScrollArea()
        scroll_area.setWidget(analog_scroll)
        scroll_area.setWidgetResizable(True)
        
        analog_layout.addWidget(scroll_area)
        self.pin_tabs.addTab(analog_tab, "Analog Pins")
        
    def on_board_type_changed(self):
        """Handle board type selection change"""
        board_name = self.board_type.currentText()
        self.current_board_config = BOARD_CONFIGS.get(board_name, BOARD_CONFIGS["Auto-detect"])
        
        # Update board info
        info_text = f"<b>{self.current_board_config.name}</b><br>"
        info_text += f"{self.current_board_config.description}<br>"
        info_text += f"Digital pins: {len(self.current_board_config.digital_pins)}<br>"
        info_text += f"PWM pins: {len(self.current_board_config.pwm_pins)}<br>"
        info_text += f"Analog pins: {len(self.current_board_config.analog_pins)}"
        self.board_info.setText(info_text)
        
        # Recreate pin tabs
        if not self.worker.running:  # Only update if not connected
            self.create_pin_tabs()
    
    def on_pin_config_changed(self, pin_number: int, mode_value: str):
        """Handle pin configuration change"""
        if self.worker.running:
            self.worker.set_pin_mode(pin_number, mode_value)
            self.create_control_widget(pin_number, mode_value)
    
    def create_control_widget(self, pin_number: int, mode_value: str):
        """Create appropriate control widget for pin mode"""
        # Remove existing control widget if any
        if pin_number in self.control_widgets:
            widget = self.control_widgets[pin_number]
            if widget and hasattr(widget, 'deleteLater'):
                widget.deleteLater()
            del self.control_widgets[pin_number]
        
        # Create new control widget based on mode
        if mode_value == PinMode.DIGITAL_OUTPUT.value:
            btn = QPushButton(f"Pin {pin_number}: OFF")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    padding: 10px;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                    color: white;
                }
            """)
            btn.toggled.connect(lambda checked: self.toggle_digital(pin_number, checked))
            self.control_widgets[pin_number] = btn
            
            # Add to appropriate layout (you could organize this better)
            # For now, we'll just update the pin widget's value display
            if pin_number in self.pin_widgets:
                self.pin_widgets[pin_number].value_display.setText("Button")
                
        elif mode_value == PinMode.PWM.value:
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 255)
            slider.valueChanged.connect(lambda value: self.set_pwm(pin_number, value))
            self.control_widgets[pin_number] = slider
            
            if pin_number in self.pin_widgets:
                self.pin_widgets[pin_number].value_display.setText("0/255")
                
        elif mode_value == PinMode.SERVO.value:
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 180)
            slider.setValue(90)
            slider.valueChanged.connect(lambda value: self.set_servo(pin_number, value))
            self.control_widgets[pin_number] = slider
            
            if pin_number in self.pin_widgets:
                self.pin_widgets[pin_number].value_display.setText("90°")
    
    def on_pin_state_changed(self, pin: int, mode: str, value: object):
        """Handle pin state change from worker"""
        if pin in self.pin_widgets:
            widget = self.pin_widgets[pin]
            if mode == PinMode.DIGITAL_INPUT.value:
                widget.value_display.setText(f"{'HIGH' if value == 1 else 'LOW'}")
            elif mode == PinMode.DIGITAL_OUTPUT.value:
                widget.value_display.setText(f"{value}")
            elif mode == PinMode.PWM.value:
                widget.value_display.setText(f"{value}/255")
            elif mode == PinMode.ANALOG.value:
                if value is not None:
                    voltage = value * 5.0  # Assuming 5V reference
                    widget.value_display.setText(f"{voltage:.2f}V")
            elif mode == PinMode.SERVO.value:
                widget.value_display.setText(f"{value}°")
        
        # Update pin monitor
        self.update_pin_monitor(pin, mode, value)
    
    def update_pin_monitor(self, pin: int, mode: str, value: object):
        """Update the pin values monitor"""
        if mode:
            mode_name = mode.upper()
            if mode == PinMode.DIGITAL_INPUT.value or mode == PinMode.DIGITAL_OUTPUT.value:
                value_str = f"{'HIGH' if value == 1 else 'LOW'}"
            elif mode == PinMode.PWM.value:
                value_str = f"{value}/255"
            elif mode == PinMode.ANALOG.value:
                if value is not None:
                    voltage = value * 5.0  # Assuming 5V reference
                    value_str = f"{voltage:.2f}V"
                else:
                    value_str = "N/A"
            elif mode == PinMode.SERVO.value:
                value_str = f"{value}°"
            else:
                value_str = str(value)
                
            # Update monitor text (simplified - in a real app you might maintain a structured view)
            monitor_text = self.pin_monitor.toPlainText()
            lines = monitor_text.split('\n')
            
            # Find or create line for this pin
            pin_line = f"Pin {pin}: {mode_name} = {value_str}"
            found = False
            for i, line in enumerate(lines):
                if line.startswith(f"Pin {pin}:"):
                    lines[i] = pin_line
                    found = True
                    break
            
            if not found:
                lines.append(pin_line)
            
            self.pin_monitor.setText('\n'.join(lines))
    
    def refresh_ports(self):
        """Scan for available serial ports with improved detection"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        
        # Enhanced Arduino descriptors for better detection
        arduino_descriptors = [
            "Arduino", "USB-SERIAL", "CH340", "CP210", "FTDI", 
            "USB Serial Port", "USB2.0-Serial", "USB-SERIAL CH340",
            "Arduino Uno", "Arduino Mega", "Arduino Due", "Leonardo"
        ]
        
        found_arduino = False
        
        for port in ports:
            desc = f"{port.device} - {port.description}"
            if any(keyword in port.description for keyword in arduino_descriptors):
                desc += " [LIKELY ARDUINO]"
                found_arduino = True
            self.port_combo.addItem(desc, port.device)
            
        if not found_arduino:
            self.log_message("No Arduino detected automatically. Check connection.")
            
        # Add manual entry option
        self.port_combo.addItem("Enter manually...", "manual")
    
    def connect_to_board(self):
        """Initiate connection to selected port with improved error handling"""
        port_data = self.port_combo.currentData()
        
        if port_data == "manual":
            self.log_message("Manual port entry not implemented in this demo")
            return
            
        port = port_data or self.port_combo.currentText().split(" - ")[0]
        board_name = self.board_type.currentText()
        board_type = board_name.lower().replace("arduino ", "").replace("-detect", "auto").replace(" ", "_")
        
        self.log_message(f"Connecting to {port} as {board_name}...")
        self.connect_btn.setEnabled(False)
        
        # Connection happens in worker thread
        if self.worker.connect_board(port, board_type):
            # If connection succeeded, configure pins according to current settings
            self.apply_pin_configurations()
    
    def apply_pin_configurations(self):
        """Apply current pin configurations to the board"""
        for pin_number, widget in self.pin_widgets.items():
            if isinstance(pin_number, str) and pin_number.startswith('A'):
                # Handle analog pin
                analog_pin = int(pin_number[1:])
                mode_value = widget.mode_combo.currentData()
                self.worker.set_pin_mode(analog_pin, mode_value)
            else:
                # Handle digital pin
                mode_value = widget.mode_combo.currentData()
                self.worker.set_pin_mode(pin_number, mode_value)
    
    def on_connection_result(self, success: bool, message: str):
        """Handle connection result from worker thread"""
        if success:
            self.status_label.setText(f"Connected: {message}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.log_message(f"Success! {message}")
            
            # Enable controls
            self.disconnect_btn.setEnabled(True)
            self.board_type.setEnabled(False)  # Lock board type during connection
            
            # Start update timer
            self.update_timer.start(100)  # 100ms updates
            
            # Apply current pin configurations
            self.apply_pin_configurations()
            
        else:
            self.status_label.setText("Connection Failed")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.log_message(f"Connection failed: {message}")
            self.connect_btn.setEnabled(True)
            QMessageBox.critical(self, "Connection Error", message)
    
    def disconnect_board(self):
        """Disconnect from Arduino with proper cleanup"""
        self.worker.disconnect()
        self.update_timer.stop()
        
        self.status_label.setText("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.log_message("Disconnected from board")
        
        # Disable controls and reset state
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.board_type.setEnabled(True)
        
        # Clear control widgets
        for widget in self.control_widgets.values():
            if hasattr(widget, 'deleteLater'):
                widget.deleteLater()
        self.control_widgets.clear()
        
        # Reset pin widgets
        for widget in self.pin_widgets.values():
            widget.set_default_mode()
    
    def toggle_digital(self, pin: int, checked: bool):
        """Toggle digital pin HIGH/LOW"""
        value = 1 if checked else 0
        self.worker.digital_write(pin, value)
        self.log_message(f"Digital pin {pin} set to {value}")
    
    def set_pwm(self, pin: int, value: int):
        """Set PWM value for pin"""
        self.worker.analog_write(pin, value)
        self.log_message(f"PWM pin {pin} set to {value}/255")
        
        # Update display if widget exists
        if pin in self.pin_widgets:
            self.pin_widgets[pin].value_display.setText(f"{value}/255")
    
    def set_servo(self, pin: int, angle: int):
        """Set servo angle for pin"""
        self.worker.servo_write(pin, angle)
        self.log_message(f"Servo on pin {pin} set to {angle}°")
        
        # Update display if widget exists
        if pin in self.pin_widgets:
            self.pin_widgets[pin].value_display.setText(f"{angle}°")
    
    def update_readings(self):
        """Update readings from input pins"""
        # Read digital inputs
        for pin in self.current_board_config.digital_pins:
            if pin in self.worker.pin_modes and self.worker.pin_modes[pin] == PinMode.DIGITAL_INPUT.value:
                self.worker.digital_read(pin)
        
        # Read analog inputs
        for pin in self.current_board_config.analog_pins:
            if pin in self.worker.pin_modes and self.worker.pin_modes[pin] == PinMode.ANALOG.value:
                self.worker.analog_read(pin)
    
    def log_message(self, message: str):
        """Add message to log"""
        self.log.append(f">>> {message}")
    
    def show_troubleshooting_details(self):
        """Show detailed troubleshooting dialog"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Arduino Connection Troubleshooting")
        dialog.setIcon(QMessageBox.Information)
        dialog.setStandardButtons(QMessageBox.Ok)
        
        details_html = """
<h3>Arduino Connection Troubleshooting Guide</h3>

<h4>1. Arduino Not Running StandardFirmata</h4>
<p>The most common issue is that the Arduino isn't running the required StandardFirmata sketch.</p>
<p><b>Solution:</b></p>
<ul>
<li>Open Arduino IDE</li>
<li>Go to File > Examples > Firmata > StandardFirmata</li>
<li>Connect your Arduino</li>
<li>Select the correct board and port from Tools > Board and Tools > Port</li>
<li>Upload the sketch to your board</li>
</ul>

<h4>2. Port In Use Error</h4>
<p>The serial port is being used by another application, typically the Arduino IDE.</p>
<p><b>Solution:</b></p>
<ul>
<li>Close Arduino IDE completely (it keeps the port open)</li>
<li>Close any other serial monitoring tools</li>
<li>Try connecting again</li>
</ul>

<h4>3. Permission Denied</h4>
<p>The application doesn't have permission to access the serial port.</p>
<p><b>Solution:</b></p>
<ul>
<li><b>Windows:</b> Right-click the application and select "Run as administrator"</li>
<li><b>Linux:</b> Add your user to the dialout group: <code>sudo usermod -a -G dialout $USER</code> then logout and login again</li>
<li><b>macOS:</b> Try running with sudo: <code>sudo python src/main.py</code></li>
</ul>

<h4>4. Incorrect Board Type</h4>
<p>The board type selected in the application doesn't match your actual Arduino hardware.</p>
<p><b>Solution:</b></p>
<ul>
<li>Verify your Arduino model (Uno, Mega, Due, ESP32, etc.)</li>
<li>Select the matching board type in the application's dropdown</li>
<li>If unsure, try "Auto-detect" first</li>
</ul>

<h4>5. USB Connection Issues</h4>
<p>Physical connection problems or driver issues.</p>
<p><b>Solution:</b></p>
<ul>
<li>Try a different USB cable (some cables only provide power)</li>
<li>Try a different USB port on your computer</li>
<li>If using a clone Arduino, ensure you have the correct drivers (CH340, CP210, FTDI)</li>
<li>Check if the Arduino's power LED is on</li>
</ul>

<h4>6. Port Detection Issues</h4>
<p>The application might not be detecting your Arduino port correctly.</p>
<p><b>Solution:</b></p>
<ul>
<li>Click the "Refresh" button in the application</li>
<li>Check if your Arduino appears in the port list with "[LIKELY ARDUINO]" tag</li>
<li>If not detected, check Device Manager (Windows) or ls /dev/tty* (Linux/macOS)</li>
</ul>

<h4>7. pyfirmata Compatibility Issues</h4>
<p>Different versions of pyfirmata might have compatibility issues with certain Arduino boards.</p>
<p><b>Solution:</b></p>
<ul>
<li>Try updating pyfirmata: <code>pip install --upgrade pyfirmata</code></li>
<li>If issues persist, try a specific version: <code>pip install pyfirmata==2.0.0</code></li>
</ul>

<h4>8. Baud Rate Issues</h4>
<p>The Arduino's Firmata sketch might be configured for a different baud rate.</p>
<p><b>Solution:</b></p>
<ul>
<li>The default baud rate for StandardFirmata is 57600</li>
<li>If you modified the sketch, ensure it matches the application's expectations</li>
</ul>
"""
        
        dialog.setText("If you're still having issues after trying these solutions, check the log window for specific error messages.")
        dialog.setDetailedText(details_html)
        dialog.exec()
    
    def closeEvent(self, event):
        """Clean up on window close"""
        self.worker.disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Clean, modern look across platforms
    
    window = OptimizedArduinoApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()