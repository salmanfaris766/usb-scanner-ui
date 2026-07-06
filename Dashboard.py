import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedLayout, QScrollArea, QFrame, QGraphicsOpacityEffect, QComboBox, QGridLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QVariantAnimation, QEasingCurve, QTime, QPointF, QDateTime, QPropertyAnimation
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from theme import theme_manager
from widgets import GlassCard, AnimatedUSBWidget, CircularRiskRing, StatusBadge, draw_category_vector_icon, GlassProgressBar

SIMULATED_DEVICES = [
    {
        "name": "SanDisk Ultra USB 3.0",
        "manufacturer": "SanDisk",
        "vid": "0x0781",
        "pid": "0x5583",
        "serial": "SDX2026A12345",
        "usb_version": "USB 3.0",
        "capacity": "64 GB",
        "used_space": "18 GB",
        "free_space": "46 GB",
        "file_system": "FAT32",
        "category": "USB Flash Drive",
        "classification": "USB Flash Drive",
        "is_bad": False
    },
    {
        "name": "Kingston DataTraveler",
        "manufacturer": "Kingston",
        "vid": "0x0930",
        "pid": "0x6543",
        "serial": "LGK2026A7712",
        "usb_version": "USB 3.1",
        "capacity": "128 GB",
        "used_space": "32 GB",
        "free_space": "96 GB",
        "file_system": "exFAT",
        "category": "Pen Drive",
        "classification": "Pen Drive",
        "is_bad": False
    },
    {
        "name": "Samsung T7 Portable SSD",
        "manufacturer": "Samsung",
        "vid": "0x04E8",
        "pid": "0x61F5",
        "serial": "SAMS2026T7990",
        "usb_version": "USB 3.2",
        "capacity": "1 TB",
        "used_space": "280 GB",
        "free_space": "744 GB",
        "file_system": "exFAT",
        "category": "External SSD",
        "classification": "External SSD",
        "is_bad": False
    },
    {
        "name": "Logitech MX Master Mouse",
        "manufacturer": "Logitech",
        "vid": "0x046D",
        "pid": "0xC52B",
        "serial": "LOGI9182C771",
        "usb_version": "USB 2.0",
        "capacity": "N/A",
        "used_space": "0 GB",
        "free_space": "0 GB",
        "file_system": "N/A",
        "category": "USB Mouse",
        "classification": "USB Mouse",
        "is_bad": False
    },
    {
        "name": "Dell Premium USB Mouse",
        "manufacturer": "Dell",
        "vid": "0x413C",
        "pid": "0x301A",
        "serial": "DELL65421MOU",
        "usb_version": "USB 2.0",
        "capacity": "N/A",
        "used_space": "0 GB",
        "free_space": "0 GB",
        "file_system": "N/A",
        "category": "USB Mouse",
        "classification": "USB Mouse",
        "is_bad": False
    },
    {
        "name": "Anker USB-C Hub Controller",
        "manufacturer": "Anker",
        "vid": "0x2109",
        "pid": "0x0817",
        "serial": "ANKR2026HUB",
        "usb_version": "USB-C",
        "capacity": "N/A",
        "used_space": "0 GB",
        "free_space": "0 GB",
        "file_system": "N/A",
        "category": "USB-C Device",
        "classification": "USB-C Device",
        "is_bad": False
    },
    {
        "name": "HDMI Capture Adapter",
        "manufacturer": "Anker",
        "vid": "0x1B1C",
        "pid": "0x1C2D",
        "serial": "HDMI99281ACC",
        "usb_version": "USB 3.0",
        "capacity": "N/A",
        "used_space": "0 GB",
        "free_space": "0 GB",
        "file_system": "N/A",
        "category": "HDMI Device",
        "classification": "HDMI Device",
        "is_bad": False
    },
    {
        "name": "3.5 mm Audio Adapter",
        "manufacturer": "Anker",
        "vid": "0x0B05",
        "pid": "0x1902",
        "serial": "AUD99281SND",
        "usb_version": "USB 2.0",
        "capacity": "N/A",
        "used_space": "0 GB",
        "free_space": "0 GB",
        "file_system": "N/A",
        "category": "3.5 mm Audio Device",
        "classification": "3.5 mm Audio Device",
        "is_bad": True
    },
    {
        "name": "Sony Professional SD Card",
        "manufacturer": "Sony",
        "vid": "0x054C",
        "pid": "0x09C2",
        "serial": "SDSK56482AX",
        "usb_version": "USB 3.0",
        "capacity": "32 GB",
        "used_space": "8 GB",
        "free_space": "24 GB",
        "file_system": "FAT32",
        "category": "SD Card",
        "classification": "SD Card",
        "is_bad": False
    },
    {
        "name": "Stealth Rubber Ducky V2",
        "manufacturer": "Corsair",
        "vid": "0x04D9",
        "pid": "0x1702",
        "serial": "SNX2A45B9137",
        "usb_version": "USB 2.0",
        "capacity": "N/A",
        "used_space": "0 GB",
        "free_space": "0 GB",
        "file_system": "N/A",
        "category": "USB Keyboard",
        "classification": "USB Keyboard",
        "is_bad": True
    },
]

class GlassOverlayPopup(QWidget):
    authorized = pyqtSignal(bool, dict)

    def __init__(self, device_data, parent=None):
        super().__init__(parent)
        self.device_data = device_data
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = GlassCard(self)
        self.card.setFixedSize(380, 240)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)
        
        # Threat Alert vs Normal Authorization Header
        title_text = "SECURITY AUTHORIZATION" if not device_data['is_bad'] else "CRITICAL ATTACK SHIELDED"
        color_theme = theme_manager.get_color("accent") if not device_data['is_bad'] else "#ff1744"
        
        self.lbl_title = QLabel(title_text)
        self.lbl_title.setStyleSheet(f"color: {color_theme}; font-family: 'Inter'; font-weight: 800; font-size: 15px; letter-spacing: 1px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_device = QLabel(f"{device_data['name']}\nType: {device_data['category']} ({device_data['vid']}:{device_data['pid']})")
        self.lbl_device.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-weight: 500; font-size: 13px; line-height: 18px;")
        self.lbl_device.setWordWrap(True)
        self.lbl_device.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_warning = QLabel(
            "WARNING: This device behaves like a Human Interface Device (Keyboard) but is disguised as simple storage." 
            if device_data['is_bad'] else 
            "The connected peripheral is awaiting classification validation."
        )
        self.lbl_warning.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        
        if device_data['is_bad']:
            self.btn_action = QPushButton("ISOLATE && SHIELD")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #ff1744; color: white; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px;
                }
                QPushButton:hover { background-color: #d50000; }
            """)
            self.btn_action.clicked.connect(lambda: self.authorized.emit(False, self.device_data))
            btn_layout.addWidget(self.btn_action)
        else:
            self.btn_allow = QPushButton("ALLOW DEVICE")
            self.btn_allow.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_manager.get_color('accent')}; color: black; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px;
                }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)
            self.btn_allow.clicked.connect(lambda: self.authorized.emit(True, self.device_data))
            
            self.btn_deny = QPushButton("BLOCK")
            self.btn_deny.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,10); color: white; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px; border: 0.5px solid rgba(255,255,255,20);
                }
                QPushButton:hover { background-color: rgba(255,255,255,18); }
            """)
            self.btn_deny.clicked.connect(lambda: self.authorized.emit(False, self.device_data))
            
            btn_layout.addWidget(self.btn_deny)
            btn_layout.addWidget(self.btn_allow)
            
        card_layout.addWidget(self.lbl_title)
        card_layout.addWidget(self.lbl_device)
        card_layout.addWidget(self.lbl_warning)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(self.card)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

class NewDeviceFoundPopup(QWidget):
    action_clicked = pyqtSignal(bool, dict) # True for Inject, False for Eject

    def __init__(self, device_data, parent=None):
        super().__init__(parent)
        self.device_data = device_data
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = GlassCard(self)
        self.card.setFixedSize(380, 240)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)
        
        self.lbl_title = QLabel("NEW DEVICE FOUND")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-weight: 800; font-size: 15px; letter-spacing: 1px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_device = QLabel(f"{device_data['name']}")
        self.lbl_device.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-weight: 700; font-size: 14px; line-height: 18px;")
        self.lbl_device.setWordWrap(True)
        self.lbl_device.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_warning = QLabel("A new USB device has been detected.\nWould you like to connect this device?")
        self.lbl_warning.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 12px;")
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        
        self.btn_eject = QPushButton("EJECT")
        self.btn_eject.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,10); color: white; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px; border: 0.5px solid rgba(255,255,255,20);
            }
            QPushButton:hover { background-color: rgba(255,255,255,18); }
        """)
        self.btn_eject.clicked.connect(lambda: self.action_clicked.emit(False, self.device_data))
        
        self.btn_inject = QPushButton("INJECT")
        self.btn_inject.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')}; color: black; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        self.btn_inject.clicked.connect(lambda: self.action_clicked.emit(True, self.device_data))
        
        btn_layout.addWidget(self.btn_eject)
        btn_layout.addWidget(self.btn_inject)
        
        card_layout.addWidget(self.lbl_title)
        card_layout.addWidget(self.lbl_device)
        card_layout.addWidget(self.lbl_warning)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(self.card)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

TRUSTED_DEVICES = [
    "SanDisk Ultra USB 3.0",
    "Kingston DataTraveler",
    "Samsung T7 SSD",
    "Samsung T7 Portable SSD",
    "Logitech USB Keyboard",
    "Dell USB Mouse",
    "Dell Premium USB Mouse"
]

def check_device_type_match(selected, actual):
    selected_clean = selected.lower().replace("adapter", "device").strip()
    actual_clean = actual.lower().replace("adapter", "device").strip()
    return (selected_clean == actual_clean) or (selected_clean in actual_clean) or (actual_clean in selected_clean)

class UnknownDevicePopup(QWidget):
    action_clicked = pyqtSignal(str, str, dict) # action ('scan' or 'block'), selected_type, device_data

    def __init__(self, device_data, parent=None):
        super().__init__(parent)
        self.device_data = device_data
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = GlassCard(self)
        self.card.setFixedSize(400, 360)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)
        
        self.lbl_title = QLabel("New Device Found")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-weight: 800; font-size: 15px; letter-spacing: 1px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        details_layout = QGridLayout()
        details_layout.setSpacing(8)
        
        lbl_name_tag = QLabel("Device Name:")
        lbl_name_tag.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-weight: 600; font-size: 12px;")
        self.lbl_name_val = QLabel(device_data['name'])
        self.lbl_name_val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-weight: bold; font-size: 12px;")
        self.lbl_name_val.setWordWrap(True)
        
        lbl_type_tag = QLabel("Detected Device Type:")
        lbl_type_tag.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-weight: 600; font-size: 12px;")
        self.lbl_type_val = QLabel(device_data['category'])
        self.lbl_type_val.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-weight: bold; font-size: 12px;")
        
        details_layout.addWidget(lbl_name_tag, 0, 0)
        details_layout.addWidget(self.lbl_name_val, 0, 1)
        details_layout.addWidget(lbl_type_tag, 1, 0)
        details_layout.addWidget(self.lbl_type_val, 1, 1)
        
        self.lbl_msg = QLabel("A USB device has been detected.\nPlease select the type of device you want to scan.")
        self.lbl_msg.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_question = QLabel("What type of device would you like to scan?")
        self.lbl_question.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: 600;")
        self.lbl_question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.combo_types = QComboBox()
        self.combo_types.addItems([
            "USB Flash Drive",
            "Pen Drive",
            "External HDD",
            "External SSD",
            "USB Keyboard",
            "USB Mouse",
            "USB-C Device",
            "HDMI Adapter",
            "3.5 mm Audio Device",
            "SD Card",
            "Mobile Device",
            "Unknown Device"
        ])
        
        bg_color = "#1e2c3a" if theme_manager.current_theme == 'dark' else "#ffffff"
        text_color = "#ffffff" if theme_manager.current_theme == 'dark' else "#000000"
        self.combo_types.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(255, 255, 255, 12);
                color: {theme_manager.get_color('text_primary')};
                border: 0.5px solid rgba(255, 255, 255, 20);
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'Inter';
                font-size: 12px;
                min-width: 220px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_color};
                color: {text_color};
                border: 0.5px solid rgba(255, 255, 255, 20);
                selection-background-color: {theme_manager.get_color('accent')};
                selection-color: black;
            }}
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        
        self.btn_block = QPushButton("Block")
        self.btn_block.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,10); color: white; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px; border: 0.5px solid rgba(255,255,255,20);
            }
            QPushButton:hover { background-color: rgba(255,255,255,18); }
        """)
        self.btn_block.clicked.connect(self.on_block_clicked)
        
        self.btn_scan = QPushButton("Scan")
        self.btn_scan.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')}; color: black; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        self.btn_scan.clicked.connect(self.on_scan_clicked)
        
        btn_layout.addWidget(self.btn_block)
        btn_layout.addWidget(self.btn_scan)
        
        card_layout.addWidget(self.lbl_title)
        card_layout.addLayout(details_layout)
        card_layout.addWidget(self.lbl_msg)
        card_layout.addWidget(self.lbl_question)
        card_layout.addWidget(self.combo_types, 0, Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(self.card)

    def on_block_clicked(self):
        self.action_clicked.emit("block", self.combo_types.currentText(), self.device_data)

    def on_scan_clicked(self):
        self.action_clicked.emit("scan", self.combo_types.currentText(), self.device_data)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

class VerificationSuccessPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = GlassCard(self)
        self.card.setFixedSize(380, 180)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)
        
        self.lbl_title = QLabel("Device Verified")
        self.lbl_title.setStyleSheet("color: #00e676; font-family: 'Inter'; font-weight: 800; font-size: 15px; letter-spacing: 1px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_msg = QLabel("Device type verified successfully.\nStarting security scan...")
        self.lbl_msg.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 13px; font-weight: bold;")
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(self.lbl_title)
        card_layout.addWidget(self.lbl_msg)
        layout.addWidget(self.card)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 160))

class DeviceMismatchPopup(QWidget):
    action_clicked = pyqtSignal(str, dict) # 'retry' or 'block', device_data

    def __init__(self, detected_type, selected_type, device_data, parent=None):
        super().__init__(parent)
        self.device_data = device_data
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.card = GlassCard(self)
        self.card.setFixedSize(400, 300)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)
        
        self.lbl_title = QLabel("Device Type Mismatch")
        self.lbl_title.setStyleSheet("color: #ff1744; font-family: 'Inter'; font-weight: 800; font-size: 15px; letter-spacing: 1px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_msg = QLabel("The selected device type does not match the connected device.")
        self.lbl_msg.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 12px; font-weight: bold;")
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        grid = QGridLayout()
        grid.setSpacing(8)
        
        lbl_det_tag = QLabel("Detected Device:")
        lbl_det_tag.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-weight: 600; font-size: 12px;")
        lbl_det_val = QLabel(detected_type)
        lbl_det_val.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-weight: bold; font-size: 12px;")
        
        lbl_sel_tag = QLabel("Selected Device:")
        lbl_sel_tag.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-weight: 600; font-size: 12px;")
        lbl_sel_val = QLabel(selected_type)
        lbl_sel_val.setStyleSheet("color: #ff1744; font-family: 'Inter'; font-weight: bold; font-size: 12px;")
        
        grid.addWidget(lbl_det_tag, 0, 0)
        grid.addWidget(lbl_det_val, 0, 1)
        grid.addWidget(lbl_sel_tag, 1, 0)
        grid.addWidget(lbl_sel_val, 1, 1)
        
        self.lbl_submsg = QLabel("Please verify the connected device before scanning.")
        self.lbl_submsg.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_submsg.setWordWrap(True)
        self.lbl_submsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        
        self.btn_retry = QPushButton("Retry")
        self.btn_retry.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')}; color: black; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        self.btn_retry.clicked.connect(lambda: self.action_clicked.emit("retry", self.device_data))
        
        self.btn_block = QPushButton("Block Device")
        self.btn_block.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 10); color: white; border-radius: 10px; padding: 10px; font-weight: bold; font-family: 'Inter'; font-size: 12px; border: 0.5px solid rgba(255, 255, 255, 20);
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 18); }
        """)
        self.btn_block.clicked.connect(lambda: self.action_clicked.emit("block", self.device_data))
        
        btn_layout.addWidget(self.btn_retry)
        btn_layout.addWidget(self.btn_block)
        
        card_layout.addWidget(self.lbl_title)
        card_layout.addWidget(self.lbl_msg)
        card_layout.addLayout(grid)
        card_layout.addWidget(self.lbl_submsg)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(self.card)

class ClassificationIconWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.category = "Unknown Device"
        self.setFixedSize(40, 40)
        
    def set_category(self, category):
        self.category = category
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        draw_category_vector_icon(painter, self.category, 0, 0, 40)

class DeviceClassificationCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        self.lbl_title = QLabel("DEVICE CLASSIFICATION")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        content = QHBoxLayout()
        content.setSpacing(12)
        
        self.icon_widget = ClassificationIconWidget()
        content.addWidget(self.icon_widget)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.lbl_type = QLabel("No Device Detected")
        self.lbl_type.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 13px; font-weight: bold;")
        
        self.lbl_desc = QLabel("Waiting for USB Device peripheral insertion...")
        self.lbl_desc.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_desc.setWordWrap(True)
        
        text_layout.addWidget(self.lbl_type)
        text_layout.addWidget(self.lbl_desc)
        content.addLayout(text_layout, 1)
        
        layout.addLayout(content)
        theme_manager.theme_changed.connect(self.update_theme_styles)
        self.update_theme_styles()
        
    def reset(self):
        self.icon_widget.set_category("Unknown Device")
        self.lbl_type.setText("No Device Detected")
        self.lbl_desc.setText("Waiting for USB Device peripheral insertion...")
        
    def update_classification(self, category):
        self.icon_widget.set_category(category)
        self.lbl_type.setText(category)
        
        descriptions = {
            "USB Flash Drive": "Removable flash storage device for quick file transfers.",
            "Pen Drive": "Ultra-portable NAND flash memory storage peripheral.",
            "External HDD": "High-capacity mechanical external storage disk drive.",
            "External SSD": "Solid-state rapid external storage partition.",
            "USB Keyboard": "Standard alphanumeric input device, potential keystroke vector.",
            "USB Mouse": "Precision optical pointer cursor control device.",
            "USB-C Device": "Universal bus high-speed multi-role controller.",
            "HDMI Device": "Direct digital video stream capture and display output controller.",
            "3.5 mm Audio Device": "External acoustic transceiver and sound processing card.",
            "SD Card": "Miniature flash memory expansion standard.",
            "Mobile Device": "Interactive handheld terminal with internal communication chips.",
            "Unknown Device": "Unidentified or generic universal serial bus controller."
        }
        self.lbl_desc.setText(descriptions.get(category, "Unclassified external hardware controller connected."))

    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_type.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 13px; font-weight: bold;")
        self.lbl_desc.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")

class DeviceInfoCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel("DEVICE INFORMATION")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        header_layout.addWidget(self.lbl_title)
        
        self.badge_widget = QFrame()
        self.badge_widget.setObjectName("badgeWidget")
        self.badge_layout = QHBoxLayout(self.badge_widget)
        self.badge_layout.setContentsMargins(8, 4, 8, 4)
        self.badge_lbl = QLabel("No Device")
        self.badge_lbl.setStyleSheet("font-family: 'Inter'; font-size: 9px; font-weight: bold; text-transform: uppercase;")
        self.badge_layout.addWidget(self.badge_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.badge_widget)
        layout.addLayout(header_layout)
        
        self.grid_widget = QWidget()
        self.grid_layout = QHBoxLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(12)
        
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        self.grid_layout.addLayout(left_col)
        self.grid_layout.addLayout(right_col)
        layout.addWidget(self.grid_widget)
        
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setContentsMargins(0, 10, 0, 10)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_placeholder_main = QLabel("No Device Connected")
        self.lbl_placeholder_main.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 13px; font-weight: bold;")
        self.lbl_placeholder_sub = QLabel("Waiting for USB Device...")
        self.lbl_placeholder_sub.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        
        placeholder_layout.addWidget(self.lbl_placeholder_main, 0, Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(self.lbl_placeholder_sub, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder_widget)
        
        self.fields = {}
        self.field_labels = []
        
        field_names = [
            ("Device Name", "name"),
            ("Manufacturer", "manufacturer"),
            ("Vendor ID", "vid"),
            ("Product ID", "pid"),
            ("Serial Number", "serial"),
            ("USB Version", "usb_version"),
            ("Connected Port", "port"),
            
            ("Connection Speed", "speed"),
            ("Capacity", "capacity"),
            ("Used Space", "used_space"),
            ("Free Space", "free_space"),
            ("File System", "file_system"),
            ("Connection Time", "conn_time"),
            ("Connected For", "timer"),
        ]
        
        for i, (label, key) in enumerate(field_names):
            target_col = left_col if i < 7 else right_col
            
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px; font-weight: 600;")
            
            val = QLabel("N/A")
            val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            row.addWidget(lbl)
            row.addWidget(val)
            target_col.addLayout(row)
            self.fields[key] = val
            self.field_labels.append((lbl, val))
            
        self.reset()
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def reset(self):
        self.grid_widget.hide()
        self.placeholder_widget.show()
        self.badge_widget.hide()
        for val in self.fields.values():
            val.setText("N/A")
        
    def update_device(self, dev, conn_time, authorized=True):
        self.placeholder_widget.hide()
        self.grid_widget.show()
        
        if not authorized:
            self.badge_widget.setStyleSheet("background-color: rgba(255, 23, 68, 0.15); border: 1px solid rgba(255, 23, 68, 0.4); border-radius: 6px;")
            self.badge_lbl.setText("Blocked Device")
            self.badge_lbl.setStyleSheet("color: #ff1744; font-family: 'Inter'; font-size: 9px; font-weight: 900;")
            self.badge_widget.show()
        else:
            self.badge_widget.setStyleSheet("background-color: rgba(0, 230, 118, 0.15); border: 1px solid rgba(0, 230, 118, 0.4); border-radius: 6px;")
            self.badge_lbl.setText("Trusted Device")
            self.badge_lbl.setStyleSheet("color: #00e676; font-family: 'Inter'; font-size: 9px; font-weight: 900;")
            self.badge_widget.show()
            
        self.fields["name"].setText(dev.get("name", "Unknown"))
        self.fields["manufacturer"].setText(dev.get("manufacturer", "Unknown"))
        self.fields["vid"].setText(dev.get("vid", "N/A"))
        self.fields["pid"].setText(dev.get("pid", "N/A"))
        self.fields["serial"].setText(dev.get("serial", "N/A"))
        
        usb_ver = dev.get("usb_version", "USB 2.0")
        self.fields["usb_version"].setText(usb_ver)
        
        speed_map = {
            "USB 2.0": "480 Mbps",
            "USB 3.0": "5 Gbps",
            "USB 3.1": "10 Gbps",
            "USB 3.2": "20 Gbps",
            "USB-C": "10 Gbps"
        }
        speed_str = speed_map.get(usb_ver, "480 Mbps")
        port_str = "USB-C Port 1" if "C" in usb_ver else "USB Port 1"
        
        self.fields["port"].setText(port_str)
        self.fields["speed"].setText(speed_str)
        self.fields["capacity"].setText(dev.get("capacity", "N/A"))
        self.fields["used_space"].setText(dev.get("used_space", "N/A"))
        self.fields["free_space"].setText(dev.get("free_space", "N/A"))
        self.fields["file_system"].setText(dev.get("file_system", "N/A"))
        self.fields["conn_time"].setText(conn_time)
        self.fields["timer"].setText("00:00:00")

    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_placeholder_main.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 13px; font-weight: bold;")
        self.lbl_placeholder_sub.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        for lbl, val in self.field_labels:
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px; font-weight: 600;")
            val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")

class StorageInformationCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        self.lbl_title = QLabel("STORAGE INFORMATION")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        # Placeholder Widget
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_layout.setContentsMargins(0, 10, 0, 10)
        self.lbl_placeholder = QLabel("No Storage Device Connected")
        self.lbl_placeholder.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 12px; font-style: italic;")
        placeholder_layout.addWidget(self.lbl_placeholder, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder_widget)
        
        # Stats Widget
        self.stats_widget = QWidget()
        stats_layout_inner = QVBoxLayout(self.stats_widget)
        stats_layout_inner.setContentsMargins(0, 0, 0, 0)
        stats_layout_inner.setSpacing(10)
        
        self.stats_layout = QHBoxLayout()
        self.lbl_capacity = QLabel("Capacity: N/A")
        self.lbl_used = QLabel("Used: N/A")
        self.lbl_free = QLabel("Free: N/A")
        
        for lbl in [self.lbl_capacity, self.lbl_used, self.lbl_free]:
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            self.stats_layout.addWidget(lbl)
            
        stats_layout_inner.addLayout(self.stats_layout)
        
        bar_label_layout = QHBoxLayout()
        self.lbl_usage_title = QLabel("Storage Used")
        self.lbl_usage_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 10px; font-weight: bold;")
        
        self.lbl_percentage = QLabel("0%")
        self.lbl_percentage.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
        
        bar_label_layout.addWidget(self.lbl_usage_title)
        bar_label_layout.addStretch()
        bar_label_layout.addWidget(self.lbl_percentage)
        stats_layout_inner.addLayout(bar_label_layout)
        
        self.progress_bar = GlassProgressBar()
        stats_layout_inner.addWidget(self.progress_bar)
        
        layout.addWidget(self.stats_widget)
        
        self.reset()
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def reset(self):
        self.placeholder_widget.show()
        self.stats_widget.hide()
        self.lbl_capacity.setText("Capacity: N/A")
        self.lbl_used.setText("Used: N/A")
        self.lbl_free.setText("Free: N/A")
        self.lbl_percentage.setText("0%")
        self.progress_bar.setValue(0)
        
    def update_storage(self, dev):
        cap_str = dev.get("capacity", "N/A")
        if cap_str == "N/A" or not cap_str:
            self.reset()
            return
            
        self.placeholder_widget.hide()
        self.stats_widget.show()
        
        used_str = dev.get("used_space", "0 GB")
        free_str = dev.get("free_space", "N/A")
        
        self.lbl_capacity.setText(f"Capacity: {cap_str}")
        self.lbl_used.setText(f"Used: {used_str}")
        self.lbl_free.setText(f"Free: {free_str}")
        
        try:
            if cap_str == "N/A" or ("GB" not in cap_str and "TB" not in cap_str):
                percent = 0
            else:
                cap_val = float(cap_str.split()[0])
                if "TB" in cap_str:
                    cap_val *= 1024
                used_val = float(used_str.split()[0])
                if "TB" in used_str:
                    used_val *= 1024
                percent = int((used_val / cap_val) * 100) if cap_val > 0 else 0
        except Exception:
            percent = 0
            
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(percent)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.valueChanged.connect(self._on_anim_val)
        self.anim.start()
        
    def _on_anim_val(self, val):
        self.progress_bar.setValue(val)
        self.lbl_percentage.setText(f"{int(val)}%")

    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_placeholder.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 12px; font-style: italic;")
        for lbl in [self.lbl_capacity, self.lbl_used, self.lbl_free]:
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
        self.lbl_usage_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 10px; font-weight: bold;")
        self.lbl_percentage.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")

class SystemHealthCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        self.lbl_title = QLabel("SYSTEM SHIELD INTEGRITY")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        items = [
            ("USB Monitoring", "Active"),
            ("Malware Engine", "Running"),
            ("ClamAV", "Running"),
            ("YARA", "Loaded"),
            ("Database", "Updated Today"),
            ("Internet", "Connected"),
        ]
        
        self.rows = []
        for label, val in items:
            row = QHBoxLayout()
            lbl_name = QLabel(label)
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
            
            lbl_val = QLabel(val)
            lbl_val.setStyleSheet("color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            row.addWidget(lbl_name)
            row.addWidget(lbl_val)
            layout.addLayout(row)
            self.rows.append((lbl_name, lbl_val))
            
        theme_manager.theme_changed.connect(self.update_health_theme)
        self.update_health_theme()
        
    def update_health_theme(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        for lbl_name, lbl_val in self.rows:
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
            lbl_val.setStyleSheet("color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")

class PulsingDotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.pulse = 0
        self.connected = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)
        
    def tick(self):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        self.update()
        
    def set_connected(self, connected):
        self.connected = connected
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        
        accent = QColor(theme_manager.get_color("accent"))
        glow_alpha = int(80 + 70 * math.sin(self.pulse))
        accent.setAlpha(glow_alpha)
        
        painter.setBrush(QBrush(accent))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 6 + 2 * math.sin(self.pulse), 6 + 2 * math.sin(self.pulse))
        
        solid_color = QColor(theme_manager.get_color("accent"))
        painter.setBrush(QBrush(solid_color))
        painter.drawEllipse(QPointF(cx, cy), 3.5, 3.5)

class LiveMonitoringPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        self.pulse_dot = PulsingDotWidget()
        layout.addWidget(self.pulse_dot)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.lbl_title = QLabel("USB MONITORING ACTIVE")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; background: transparent; border: none;")
        
        self.lbl_status = QLabel("Waiting for USB Device...")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_status)
        layout.addLayout(text_layout, 1)
        
        self.setStyleSheet("background: transparent; border: none;")
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def set_connected(self, connected, device_name="", authorized=True):
        self.pulse_dot.set_connected(connected)
        if connected:
            if device_name == "Evaluating peripheral...":
                self.lbl_title.setText("EVALUATING PORT INTRUSION...")
                self.lbl_status.setText("Checking descriptors...")
            elif not authorized:
                self.lbl_title.setText("THREAT MITIGATED: BLOCKED")
                self.lbl_status.setText("Device Isolated")
            else:
                self.lbl_title.setText("MONITORING CONNECTED DEVICE")
                self.lbl_status.setText(f"Active: {device_name}")
        else:
            self.lbl_title.setText("USB MONITORING ACTIVE")
            self.lbl_status.setText("Waiting for USB Device...")

    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; background: transparent; border: none;")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold; background: transparent; border: none;")

class NotificationCenter(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)
        
        self.lbl_title = QLabel("ALERTS && CONSOLE LOG")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        self.console = QVBoxLayout()
        self.console.setSpacing(4)
        layout.addLayout(self.console)
        
        self.logs = []
        self.add_log("Application Started")
        self.add_log("Virus Database Updated")
        self.add_log("USB Monitoring Enabled")
        theme_manager.theme_changed.connect(self.update_log_styles)
        
    def add_log(self, msg):
        time_str = QTime.currentTime().toString("hh:mm:ss")
        log_text = f"[{time_str}] {msg}"
        
        lbl = QLabel(log_text)
        lbl.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'JetBrains Mono'; font-size: 9px; background: transparent; border: none;")
        lbl.setWordWrap(True)
        
        self.console.addWidget(lbl)
        self.logs.append(lbl)
        
        if len(self.logs) > 5:
            oldest = self.logs.pop(0)
            self.console.removeWidget(oldest)
            oldest.deleteLater()
            
    def update_log_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        for lbl in self.logs:
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'JetBrains Mono'; font-size: 9px; background: transparent; border: none;")

class SecurityRecommendationCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        self.lbl_title = QLabel("SECURITY RECOMMENDATION")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        self.lbl_rec = QLabel("Waiting for a USB Device. Insert a USB storage device to begin monitoring.")
        self.lbl_rec.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 12px; font-weight: bold;")
        self.lbl_rec.setWordWrap(True)
        layout.addWidget(self.lbl_rec)
        
        self.lbl_details = QLabel("All ports are actively audited and sandboxed.")
        self.lbl_details.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_details.setWordWrap(True)
        layout.addWidget(self.lbl_details)
        
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def reset(self):
        self.lbl_rec.setText("Waiting for a USB Device. Insert a USB storage device to begin monitoring.")
        self.lbl_details.setText("All ports are actively audited and sandboxed.")
        self.update_theme_styles()
        
    def update_recommendation(self, dev, authorized):
        if not authorized:
            self.lbl_rec.setText("CRITICAL: Potentially suspicious device blocked.")
            self.lbl_details.setText("Threat signature matched. Ensure peripheral is inspected before authorization.")
        else:
            self.lbl_rec.setText("Device appears safe. Recommended: Run Quick Scan.")
            self.lbl_details.setText("No immediate active malware footprints detected during port evaluation.")
        self.update_theme_styles()
            
    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_rec.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 12px; font-weight: bold;")
        self.lbl_details.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")

class LastScanSummaryCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        self.lbl_title = QLabel("LAST SCAN SUMMARY")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(16)
        self.grid_layout.setVerticalSpacing(6)
        
        self.fields = {}
        self.field_labels = []
        
        fields_config = [
            ("Date:", "date", "15-Jul-2026"),
            ("Time:", "time", "10:45 AM"),
            ("Device:", "device", "SanDisk Ultra USB 3.0"),
            ("Files Scanned:", "files", "1,248"),
            ("Threats Found:", "threats", "0"),
            ("Risk Score:", "risk_score", "0%"),
            ("Duration:", "duration", "14 Seconds"),
            ("Status:", "status", "Completed Successfully")
        ]
        
        for idx, (label_text, key, default_val) in enumerate(fields_config):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px; font-weight: 600;")
            
            val = QLabel(default_val)
            val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            val.setWordWrap(True)
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            self.grid_layout.addWidget(lbl, idx, 0)
            self.grid_layout.addWidget(val, idx, 1)
            
            self.fields[key] = val
            self.field_labels.append((lbl, val))
            
        layout.addWidget(self.grid_widget)
        
        theme_manager.theme_changed.connect(self.update_theme_styles)
        self.update_theme_styles()
        
    def reset(self):
        self.fields["date"].setText("15-Jul-2026")
        self.fields["time"].setText("10:45 AM")
        self.fields["device"].setText("SanDisk Ultra USB 3.0")
        self.fields["files"].setText("1,248")
        self.fields["threats"].setText("0")
        self.fields["risk_score"].setText("0%")
        self.fields["duration"].setText("14 Seconds")
        self.fields["status"].setText("Completed Successfully")
        self.update_theme_styles()
        
    def update_scan(self, scan_data):
        date_val = scan_data.get("date", "Today")
        if date_val == "Today":
            date_val = QDateTime.currentDateTime().toString("dd-MMM-yyyy")
        self.fields["date"].setText(date_val)
        
        time_val = scan_data.get("time")
        if not time_val:
            time_val = QTime.currentTime().toString("hh:mm AP")
        self.fields["time"].setText(time_val)
        
        device_name = scan_data.get("device")
        if not device_name:
            parent = self.parent()
            while parent is not None:
                if hasattr(parent, 'connected_device'):
                    if parent.connected_device:
                        device_name = parent.connected_device.get('name', 'N/A')
                    break
                parent = parent.parent()
            if not device_name:
                device_name = "SanDisk Ultra USB 3.0"
        self.fields["device"].setText(device_name)
        
        files = scan_data.get("files", 1248)
        if isinstance(files, int):
            files_str = f"{files:,}"
        else:
            files_str = str(files)
        self.fields["files"].setText(files_str)
        
        threats = scan_data.get("threats", 0)
        self.fields["threats"].setText(str(threats))
        
        if threats > 0:
            self.fields["risk_score"].setText("100%")
            self.fields["status"].setText("Threat Detected / Blocked")
        else:
            self.fields["risk_score"].setText("0%")
            self.fields["status"].setText("Completed Successfully")
            
        dur = scan_data.get("duration", "14 Seconds")
        self.fields["duration"].setText(dur)
        
        self.update_theme_styles()
        
    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        for lbl, val in self.field_labels:
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px; font-weight: 600;")
            val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            
        threats_text = self.fields["threats"].text()
        try:
            threats_count = int(threats_text.replace(",", ""))
        except ValueError:
            threats_count = 0
            
        if threats_count > 0:
            self.fields["threats"].setStyleSheet("color: #ff1744; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            self.fields["status"].setStyleSheet("color: #ff1744; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            self.fields["risk_score"].setStyleSheet("color: #ff1744; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
        else:
            self.fields["threats"].setStyleSheet("color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            self.fields["status"].setStyleSheet("color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            self.fields["risk_score"].setStyleSheet("color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")

class TrustedDevicesCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        self.lbl_title = QLabel("TRUSTED DEVICES")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        self.device_labels = []
        for dev_name in ["SanDisk Ultra USB 3.0", "Kingston DataTraveler", "Samsung T7 SSD"]:
            lbl = QLabel(f"✓  {dev_name}")
            lbl.setStyleSheet(f"color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            layout.addWidget(lbl)
            self.device_labels.append(lbl)
            
        self.lbl_more = QLabel("+2 More Trusted Devices")
        self.lbl_more.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px; font-style: italic;")
        layout.addWidget(self.lbl_more)
        
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_more.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px; font-style: italic;")
        for lbl in self.device_labels:
            lbl.setStyleSheet(f"color: #00e676; font-family: 'Inter'; font-size: 11px; font-weight: bold;")

class DashboardPage(QWidget):
    device_authorized = pyqtSignal(dict)
    device_blocked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected_device = None
        self.device_idx = 0
        
        self.connection_time_elapsed = 0
        self.is_timer_running = False
        
        self.root_layout = QStackedLayout(self)
        self.root_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        scroll.setWidget(self.content_widget)
        
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header block
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        left_header = QVBoxLayout()
        left_header.setSpacing(4)
        
        lbl_welcome = QLabel("USB DETECTOR")
        lbl_welcome.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 20px; font-weight: 900; font-family: 'Inter'; letter-spacing: 1px;")
        
        self.lbl_subtitle = QLabel("Advanced USB Security Scanner")
        self.lbl_subtitle.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'Inter'; font-weight: 600; letter-spacing: 0.5px;")
        
        self.lbl_status = QLabel("Secure Terminal: Idle")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        
        left_header.addWidget(lbl_welcome)
        left_header.addWidget(self.lbl_subtitle)
        left_header.addWidget(self.lbl_status)
        header_layout.addLayout(left_header)
        
        header_layout.addStretch()
        
        # Right Header (Day Date Time & Notification small tab)
        right_header = QHBoxLayout()
        right_header.setSpacing(12)
        right_header.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.lbl_datetime = QLabel()
        self.lbl_datetime.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: bold; background-color: rgba(255,255,255,8); padding: 6px 12px; border-radius: 6px; border: 0.5px solid rgba(255,255,255,15);")
        
        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime_label)
        self.datetime_timer.start(1000)
        self.update_datetime_label()
        
        self.notif_tab = QFrame()
        self.notif_tab.setObjectName("notifTab")
        self.notif_tab.setStyleSheet(f"""
            QFrame#notifTab {{
                background-color: rgba(255,255,255,8);
                border: 0.5px solid rgba(255,255,255,15);
                border-radius: 8px;
            }}
            QLabel {{
                border: none;
                background-color: transparent;
            }}
        """)
        notif_layout = QHBoxLayout(self.notif_tab)
        notif_layout.setContentsMargins(8, 6, 8, 6)
        notif_layout.setSpacing(6)
        
        lbl_bell = QLabel("🔔")
        lbl_bell.setStyleSheet("font-size: 12px; background: transparent; border: none;")
        
        self.lbl_notif_count = QLabel("1")
        self.lbl_notif_count.setStyleSheet("color: #ff1744; font-size: 10px; font-weight: 900; background: transparent; border: none;")
        
        notif_layout.addWidget(lbl_bell)
        notif_layout.addWidget(self.lbl_notif_count)
        
        right_header.addWidget(self.lbl_datetime)
        right_header.addWidget(self.notif_tab)
        header_layout.addLayout(right_header)
        
        layout.addLayout(header_layout)
        
        # Main Layout (Split View)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(16)
        
        # Left Panel (Interactive USB Sandbox)
        self.left_card = GlassCard()
        left_layout = QVBoxLayout(self.left_card)
        left_layout.setContentsMargins(16, 16, 16, 16)
        
        lbl_usb_title = QLabel("DEVICE EMULATION TERMINAL")
        lbl_usb_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        left_layout.addWidget(lbl_usb_title)
        
        self.usb_visualizer = AnimatedUSBWidget()
        left_layout.addWidget(self.usb_visualizer, 1, Qt.AlignmentFlag.AlignCenter)
        
        self.live_monitor = LiveMonitoringPanel()
        left_layout.addWidget(self.live_monitor)
        
        self.btn_trigger = QPushButton("SIMULATE PHYSICAL INJECTION")
        self.btn_trigger.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')};
                color: #000000;
                border-radius: 12px;
                padding: 12px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton:hover {{
                opacity: 0.95;
            }}
        """)
        self.btn_trigger.clicked.connect(self.trigger_physical_injection)
        self.btn_trigger.hide()
        
        self.notification_center = NotificationCenter()
        left_layout.addWidget(self.notification_center)
        
        split_layout.addWidget(self.left_card, 5)
        
        # Right Panel (Real-Time Metrics)
        self.right_card = GlassCard()
        right_layout = QVBoxLayout(self.right_card)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)
        
        # Risk Ring View
        risk_h_layout = QHBoxLayout()
        self.risk_ring = CircularRiskRing()
        risk_info_layout = QVBoxLayout()
        self.lbl_threat_level = QLabel("THREAT SCORE: CLEAR")
        self.lbl_threat_level.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-weight: 700; font-size: 14px;")
        self.lbl_risk_sub = QLabel("No anomalies identified on active ports.")
        self.lbl_risk_sub.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_risk_sub.setWordWrap(True)
        risk_info_layout.addWidget(self.lbl_threat_level)
        risk_info_layout.addWidget(self.lbl_risk_sub)
        
        risk_h_layout.addWidget(self.risk_ring)
        risk_h_layout.addLayout(risk_info_layout, 1)
        right_layout.addLayout(risk_h_layout)
        
        # Device Status Card (Metadata subcard enhanced)
        self.meta_subcard = QWidget()
        self.meta_subcard.setStyleSheet("background: rgba(255,255,255,6); border-radius: 12px;")
        meta_layout = QVBoxLayout(self.meta_subcard)
        meta_layout.setContentsMargins(12, 12, 12, 12)
        meta_layout.setSpacing(6)
        
        self.lbl_meta_title = QLabel("DEVICE STATUS")
        self.lbl_meta_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        meta_layout.addWidget(self.lbl_meta_title)
        
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        
        self.status_dot = QWidget()
        self.status_dot.setFixedSize(8, 8)
        self.status_dot.setStyleSheet("background-color: #8898a6; border-radius: 4px;")
        status_row.addWidget(self.status_dot)
        
        self.lbl_meta_name = QLabel("No Device Connected")
        self.lbl_meta_name.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 12px; font-weight: bold;")
        status_row.addWidget(self.lbl_meta_name, 1)
        meta_layout.addLayout(status_row)
        
        self.lbl_meta_category = QLabel("Waiting for USB Device...")
        self.lbl_meta_category.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        
        self.lbl_meta_vid_pid = QLabel("Hardware ID: N/A")
        self.lbl_meta_vid_pid.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        
        meta_layout.addWidget(self.lbl_meta_category)
        meta_layout.addWidget(self.lbl_meta_vid_pid)
        right_layout.addWidget(self.meta_subcard)
        
        self.system_health_card = SystemHealthCard()
        right_layout.addWidget(self.system_health_card)
        
        split_layout.addWidget(self.right_card, 4)
        
        layout.addLayout(split_layout)
        
        # Row 2 (Grid of expanded details)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(16)
        
        self.device_info_card = DeviceInfoCard()
        row2_layout.addWidget(self.device_info_card, 5)
        
        right_sub_col = QVBoxLayout()
        right_sub_col.setSpacing(16)
        
        self.device_class_card = DeviceClassificationCard()
        self.storage_card = StorageInformationCard()
        self.recommendation_card = SecurityRecommendationCard()
        self.last_scan_card = LastScanSummaryCard()
        self.trusted_devices_card = TrustedDevicesCard()
        
        right_sub_col.addWidget(self.device_class_card)
        right_sub_col.addWidget(self.storage_card)
        right_sub_col.addWidget(self.recommendation_card)
        right_sub_col.addWidget(self.last_scan_card)
        right_sub_col.addWidget(self.trusted_devices_card)
        
        row2_layout.addLayout(right_sub_col, 4)
        layout.addLayout(row2_layout)
        
        self.root_layout.addWidget(scroll)
        
        # Hide standard cards initially
        self.device_info_card.hide()
        self.device_class_card.hide()
        self.storage_card.hide()
        self.recommendation_card.hide()
        
        # Start a 4-second timer to automatically trigger device detection
        self.start_simulated_detection_timer(4000)
        
        theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()

    def update_styles(self):
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        self.btn_trigger.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('accent')};
                color: #000000;
                border-radius: 12px;
                padding: 12px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton:hover {{
                opacity: 0.95;
            }}
        """)
        self.lbl_threat_level.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-weight: 700; font-size: 14px;")
        self.lbl_meta_name.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 12px; font-weight: bold;")
        self.lbl_subtitle.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'Inter'; font-weight: 600; letter-spacing: 0.5px;")
        self.lbl_meta_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_meta_category.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_meta_vid_pid.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")

    def update_datetime_label(self):
        current_dt = QDateTime.currentDateTime()
        self.lbl_datetime.setText(current_dt.toString("dddd, MMM d, yyyy - hh:mm:ss AP"))
        
        if self.is_timer_running:
            self.connection_time_elapsed += 1
            hours = self.connection_time_elapsed // 3600
            minutes = (self.connection_time_elapsed % 3600) // 60
            seconds = self.connection_time_elapsed % 60
            timer_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.device_info_card.fields["timer"].setText(timer_str)

    def start_simulated_detection_timer(self, delay_ms):
        if hasattr(self, 'detection_timer') and self.detection_timer is not None:
            self.detection_timer.stop()
            self.detection_timer.deleteLater()
        self.detection_timer = QTimer(self)
        self.detection_timer.setSingleShot(True)
        self.detection_timer.timeout.connect(self.trigger_automatic_device_found)
        self.detection_timer.start(delay_ms)

    def trigger_automatic_device_found(self):
        if self.connected_device is not None:
            return
            
        device = SIMULATED_DEVICES[self.device_idx]
        self.device_idx = (self.device_idx + 1) % len(SIMULATED_DEVICES)
        self.detect_new_device(device)

    def detect_new_device(self, device):
        self.show_unknown_device_popup(device)

    def handle_trusted_device_found(self, device):
        self.notification_center.add_log("Trusted Device Detected")
        self.notification_center.add_log("Automatically Authorized")
        self.start_scanning_workflow(device)

    def show_unknown_device_popup(self, device):
        self.clear_popups()
        
        self.unknown_popup = UnknownDevicePopup(device, self)
        self.unknown_popup.action_clicked.connect(self.handle_unknown_popup_action)
        self.unknown_popup.resize(self.size())
        
        self.fade_in_widget(self.unknown_popup, 400)
        self.root_layout.addWidget(self.unknown_popup)
        self.root_layout.setCurrentWidget(self.unknown_popup)

    def handle_unknown_popup_action(self, action, selected_type, device):
        if action == "block":
            self.clear_popups()
            self.handle_popup_action(False, device)
        elif action == "scan":
            match = check_device_type_match(selected_type, device['category'])
            if match:
                self.show_verification_success_popup(device)
            else:
                self.show_device_mismatch_popup(device['category'], selected_type, device)

    def show_verification_success_popup(self, device):
        self.clear_popups()
        
        self.success_popup = VerificationSuccessPopup(self)
        self.success_popup.resize(self.size())
        self.fade_in_widget(self.success_popup, 400)
        self.root_layout.addWidget(self.success_popup)
        self.root_layout.setCurrentWidget(self.success_popup)
        
        QTimer.singleShot(2000, lambda: self.finish_verification_success(device))

    def finish_verification_success(self, device):
        self.clear_popups()
        self.start_scanning_workflow(device)

    def show_device_mismatch_popup(self, detected_type, selected_type, device):
        self.clear_popups()
        
        self.mismatch_popup = DeviceMismatchPopup(detected_type, selected_type, device, self)
        self.mismatch_popup.action_clicked.connect(self.handle_mismatch_action)
        self.mismatch_popup.resize(self.size())
        self.fade_in_widget(self.mismatch_popup, 400)
        self.root_layout.addWidget(self.mismatch_popup)
        self.root_layout.setCurrentWidget(self.mismatch_popup)

    def handle_mismatch_action(self, action, device):
        self.clear_popups()
        if action == "retry":
            self.show_unknown_device_popup(device)
        elif action == "block":
            self.handle_popup_action(False, device)

    def clear_popups(self):
        for attr in ['new_device_popup', 'popup', 'success_popup', 'mismatch_popup', 'unknown_popup']:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                if widget is not None:
                    try:
                        self.root_layout.removeWidget(widget)
                        widget.deleteLater()
                    except Exception:
                        pass
                    setattr(self, attr, None)
                    
        scroll_area = self.root_layout.widget(0)
        self.root_layout.setCurrentWidget(scroll_area)

    def start_scanning_workflow(self, device):
        self.connected_device = device
        self.usb_visualizer.set_connected(True, device['category'])
        self.lbl_status.setText("Peripherals Evaluation...")
        
        self.live_monitor.set_connected(True, "Evaluating peripheral...")
        
        self.lbl_meta_name.setText("Evaluating Device...")
        self.lbl_meta_category.setText("Analyzing port credentials...")
        self.lbl_meta_vid_pid.setText("Hardware ID: Evaluating...")
        self.status_dot.setStyleSheet("background-color: #ffb300; border-radius: 4px;")
        
        self.is_timer_running = False
        self.connection_time_elapsed = 0
        
        self.notification_center.add_log(f"USB insertion detected: {device['name']}")
        
        # Switch to Scan page and start scan if MainWindow is available
        from PyQt6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'pages_stack') and hasattr(widget, 'nav_bar'):
                widget.nav_bar.set_active_tab(1)  # Tab 1 is Scan Page
                if hasattr(widget, 'page_scan'):
                    widget.page_scan.start_scan()
                break
                
        QTimer.singleShot(2000, lambda: self.complete_authorization_workflow(device))

    def complete_authorization_workflow(self, device):
        self.lbl_status.setText("Access Authorized")
        self.lbl_threat_level.setText("THREAT SCORE: CLEAR")
        self.lbl_risk_sub.setText("Device is successfully registered and cleared.")
        self.device_authorized.emit(device)
        
        self.live_monitor.set_connected(True, device['name'], authorized=True)
        self.notification_center.add_log(f"Access granted to: {device['name']}")
        self.notification_center.add_log("Classification: " + device['category'])
        self.notification_center.add_log("Scan completed: 0 threats identified.")
        
        self.is_timer_running = True
        self.connection_time_elapsed = 0
        
        self.lbl_meta_name.setText("USB Connected")
        self.lbl_meta_category.setText("Device Authorized")
        self.lbl_meta_vid_pid.setText(f"Hardware ID: {device['vid']}:{device['pid']}")
        self.status_dot.setStyleSheet("background-color: #00e676; border-radius: 4px;")
        
        self.recommendation_card.update_recommendation(device, authorized=True)
        
        conn_time = QTime.currentTime().toString("hh:mm:ss AP")
        self.device_info_card.update_device(device, conn_time, authorized=True)
        self.device_class_card.update_classification(device['category'])
        self.storage_card.update_storage(device)
        
        self.fade_in_widget(self.device_info_card, 400)
        self.fade_in_widget(self.device_class_card, 400)
        self.fade_in_widget(self.recommendation_card, 400)
        
        if device.get("capacity", "N/A") != "N/A":
            self.fade_in_widget(self.storage_card, 400)
        else:
            self.storage_card.hide()
            
        if hasattr(self, 'btn_trigger') and self.btn_trigger is not None:
            self.btn_trigger.setText("EJECT EMULATOR CONNECTION")

    def start_authorization_workflow(self, device):
        self.detect_new_device(device)

    def trigger_physical_injection(self):
        if self.connected_device is not None:
            self.reset_to_idle(logged_eject_device=self.connected_device)
        else:
            device = SIMULATED_DEVICES[self.device_idx]
            self.device_idx = (self.device_idx + 1) % len(SIMULATED_DEVICES)
            self.detect_new_device(device)

    def reset_to_idle(self, logged_eject_device=None):
        self.clear_popups()
        self.lbl_status.setText("Secure Terminal: Idle")
        self.usb_visualizer.set_connected(False)
        self.risk_ring.set_threat(False)
        self.lbl_threat_level.setText("THREAT SCORE: CLEAR")
        self.lbl_risk_sub.setText("No anomalies identified on active ports.")
        
        self.lbl_meta_name.setText("No Device Connected")
        self.lbl_meta_category.setText("Waiting for USB Device...")
        self.lbl_meta_vid_pid.setText("Hardware ID: N/A")
        self.status_dot.setStyleSheet("background-color: #8898a6; border-radius: 4px;")
        
        self.device_info_card.reset()
        self.device_class_card.reset()
        self.storage_card.reset()
        self.recommendation_card.reset()
        
        self.device_info_card.hide()
        self.device_class_card.hide()
        self.storage_card.hide()
        self.recommendation_card.hide()
        
        self.live_monitor.set_connected(False)
        if logged_eject_device:
            self.notification_center.add_log(f"Device ejected safely: {logged_eject_device['name']}")
            
        self.is_timer_running = False
        self.connection_time_elapsed = 0
        self.connected_device = None
        
        self.start_simulated_detection_timer(5000)

    def fade_in_widget(self, widget, duration=400):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        widget.show()
        
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        widget._fade_anim = anim
        anim.start()

    def show_auth_popup(self, device):
        self.popup = GlassOverlayPopup(device, self)
        self.popup.authorized.connect(self.handle_popup_action)
        self.popup.resize(self.size())
        
        self.fade_in_widget(self.popup, 400)
        self.root_layout.addWidget(self.popup)
        self.root_layout.setCurrentWidget(self.popup)

    def handle_popup_action(self, authorized, device):
        if hasattr(self, 'popup') and self.popup is not None:
            popup = self.popup
            self.root_layout.removeWidget(popup)
            popup.deleteLater()
            self.popup = None
        
        scroll_area = self.root_layout.widget(0)
        self.root_layout.setCurrentWidget(scroll_area)
        
        conn_time = QTime.currentTime().toString("hh:mm:ss AP")
        
        if authorized:
            self.lbl_status.setText("Access Authorized")
            self.lbl_threat_level.setText("THREAT SCORE: CLEAR")
            self.lbl_risk_sub.setText("Device is successfully registered and cleared.")
            self.device_authorized.emit(device)
            
            self.live_monitor.set_connected(True, device['name'], authorized=True)
            self.notification_center.add_log(f"Access granted to: {device['name']}")
            self.notification_center.add_log("Classification: " + device['category'])
            self.notification_center.add_log("Scan completed: 0 threats identified.")
            
            self.is_timer_running = True
            self.connection_time_elapsed = 0
            
            self.lbl_meta_name.setText("USB Connected")
            self.lbl_meta_category.setText("Device Authorized")
            self.lbl_meta_vid_pid.setText(f"Hardware ID: {device['vid']}:{device['pid']}")
            self.status_dot.setStyleSheet("background-color: #00e676; border-radius: 4px;")
            
            self.recommendation_card.update_recommendation(device, authorized=True)
            
            # Populate and show standard details cards only on successful authorization
            self.device_info_card.update_device(device, conn_time, authorized=authorized)
            self.device_class_card.update_classification(device['category'])
            self.storage_card.update_storage(device)
            
            self.fade_in_widget(self.device_info_card, 400)
            self.fade_in_widget(self.device_class_card, 400)
            self.fade_in_widget(self.recommendation_card, 400)
            
            if device.get("capacity", "N/A") != "N/A":
                self.fade_in_widget(self.storage_card, 400)
            else:
                self.storage_card.hide()
        else:
            self.reset_to_idle()
            self.notification_center.add_log("Device Blocked Successfully")
            self.device_blocked.emit(device)
            
        if hasattr(self, 'btn_trigger') and self.btn_trigger is not None:
            self.btn_trigger.setText("EJECT EMULATOR CONNECTION")

    def on_scan_completed(self, scan_data):
        self.last_scan_card.update_scan(scan_data)
        self.notification_center.add_log(f"Scan complete: {scan_data['files']} audited, {scan_data['threats']} threats.")
