import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedLayout, QScrollArea, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QVariantAnimation, QEasingCurve, QTime, QPointF, QDateTime
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
        "is_bad": False
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
        
        self.lbl_type = QLabel("Disconnected")
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
        self.lbl_type.setText("Disconnected")
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
        
        self.lbl_title = QLabel("DEVICE INFORMATION")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        self.grid = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        self.grid.addLayout(left_col)
        self.grid.addLayout(right_col)
        layout.addLayout(self.grid)
        
        self.fields = {}
        self.field_labels = []
        
        field_names = [
            ("Device Name", "name"),
            ("Manufacturer", "manufacturer"),
            ("Vendor ID", "vid"),
            ("Product ID", "pid"),
            ("Serial Number", "serial"),
            ("USB Version", "usb_version"),
            ("Capacity", "capacity"),
            ("Used Space", "used_space"),
            ("Free Space", "free_space"),
            ("File System", "file_system"),
            ("Connection Time", "conn_time"),
        ]
        
        for i, (label, key) in enumerate(field_names):
            target_col = left_col if i < 6 else right_col
            
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
        self.fields["name"].setText("No Device Connected")
        self.fields["manufacturer"].setText("Waiting...")
        self.fields["vid"].setText("N/A")
        self.fields["pid"].setText("N/A")
        self.fields["serial"].setText("N/A")
        self.fields["usb_version"].setText("N/A")
        self.fields["capacity"].setText("N/A")
        self.fields["used_space"].setText("N/A")
        self.fields["free_space"].setText("N/A")
        self.fields["file_system"].setText("N/A")
        self.fields["conn_time"].setText("N/A")
        
    def update_device(self, dev, conn_time):
        self.fields["name"].setText(dev.get("name", "Unknown"))
        self.fields["manufacturer"].setText(dev.get("manufacturer", "Unknown"))
        self.fields["vid"].setText(dev.get("vid", "N/A"))
        self.fields["pid"].setText(dev.get("pid", "N/A"))
        self.fields["serial"].setText(dev.get("serial", "N/A"))
        self.fields["usb_version"].setText(dev.get("usb_version", "N/A"))
        self.fields["capacity"].setText(dev.get("capacity", "N/A"))
        self.fields["used_space"].setText(dev.get("used_space", "N/A"))
        self.fields["free_space"].setText(dev.get("free_space", "N/A"))
        self.fields["file_system"].setText(dev.get("file_system", "N/A"))
        self.fields["conn_time"].setText(conn_time)

    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
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
        
        self.stats_layout = QHBoxLayout()
        self.lbl_capacity = QLabel("Capacity: N/A")
        self.lbl_used = QLabel("Used: N/A")
        self.lbl_free = QLabel("Free: N/A")
        
        for lbl in [self.lbl_capacity, self.lbl_used, self.lbl_free]:
            lbl.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            self.stats_layout.addWidget(lbl)
            
        layout.addLayout(self.stats_layout)
        
        bar_label_layout = QHBoxLayout()
        self.lbl_usage_title = QLabel("Storage Used")
        self.lbl_usage_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 10px; font-weight: bold;")
        
        self.lbl_percentage = QLabel("0%")
        self.lbl_percentage.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
        
        bar_label_layout.addWidget(self.lbl_usage_title)
        bar_label_layout.addStretch()
        bar_label_layout.addWidget(self.lbl_percentage)
        layout.addLayout(bar_label_layout)
        
        self.progress_bar = GlassProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.reset()
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def reset(self):
        self.lbl_capacity.setText("Capacity: N/A")
        self.lbl_used.setText("Used: N/A")
        self.lbl_free.setText("Free: N/A")
        self.lbl_percentage.setText("0%")
        self.progress_bar.setValue(0)
        
    def update_storage(self, dev):
        cap_str = dev.get("capacity", "N/A")
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
            ("USB Monitoring", "● Active", "#00e5ff"),
            ("Malware Engine", "● Running", "#00e5ff"),
            ("YARA Engine", "● Loaded", "#00e5ff"),
            ("ClamAV Status", "● Running", "#00e5ff"),
            ("Virus Database", "v2.5.8 (● Updated)", "#00e5ff"),
            ("Internet Link", "● Connected", "#00e5ff"),
        ]
        
        self.rows = []
        for label, val, col in items:
            row = QHBoxLayout()
            lbl_name = QLabel(label)
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
            
            lbl_val = QLabel(val)
            lbl_val.setStyleSheet(f"color: {col}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            row.addWidget(lbl_name)
            row.addWidget(lbl_val)
            layout.addLayout(row)
            self.rows.append((lbl_name, lbl_val))
            
        theme_manager.theme_changed.connect(self.update_health_theme)
        self.update_health_theme()
        
    def update_health_theme(self):
        accent = theme_manager.get_color("accent")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        for lbl_name, lbl_val in self.rows:
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
            text = lbl_val.text()
            if "Active" in text or "Running" in text or "Loaded" in text or "Updated" in text or "Connected" in text:
                lbl_val.setStyleSheet(f"color: {accent}; font-family: 'Inter'; font-size: 11px; font-weight: bold;")

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
        
        self.lbl_title = QLabel("LIVE PORT MONITORING")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 9px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; background: transparent; border: none;")
        
        self.lbl_status = QLabel("Idle: Scanning Ports...")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_status)
        layout.addLayout(text_layout, 1)
        
        self.setStyleSheet("background: transparent; border: none;")
        theme_manager.theme_changed.connect(self.update_theme_styles)
        
    def set_connected(self, connected, device_name=""):
        self.pulse_dot.set_connected(connected)
        if connected:
            self.lbl_status.setText(f"Connected: {device_name}")
        else:
            self.lbl_status.setText("Idle: Scanning Ports...")

    def update_theme_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 9px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; background: transparent; border: none;")
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
        self.add_log("System shield online. Monitoring active.")
        self.add_log("Virus database loaded successfully.")
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

class DashboardPage(QWidget):
    device_authorized = pyqtSignal(dict)
    device_blocked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected_device = None
        self.device_idx = 0
        
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
        
        # Change name to USB DETECTOR
        lbl_welcome = QLabel("USB DETECTOR")
        lbl_welcome.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 20px; font-weight: 900; font-family: 'Inter'; letter-spacing: 1px;")
        
        self.lbl_status = QLabel("Secure Terminal: Idle")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        
        left_header.addWidget(lbl_welcome)
        left_header.addWidget(self.lbl_status)
        header_layout.addLayout(left_header)
        
        header_layout.addStretch()
        
        # Right Header (Day Date Time & Notification small tab)
        right_header = QHBoxLayout()
        right_header.setSpacing(12)
        right_header.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Day Date Time Label
        self.lbl_datetime = QLabel()
        self.lbl_datetime.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: bold; background-color: rgba(255,255,255,8); padding: 6px 12px; border-radius: 6px; border: 0.5px solid rgba(255,255,255,15);")
        
        # Setup a QTimer to update date-time
        self.datetime_timer = QTimer(self)
        self.datetime_timer.timeout.connect(self.update_datetime_label)
        self.datetime_timer.start(1000)
        self.update_datetime_label()
        
        # Notification small tab (small card/bell icon or indicator)
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
        
        # Add Live Monitoring Panel
        self.live_monitor = LiveMonitoringPanel()
        left_layout.addWidget(self.live_monitor)
        
        # Sandbox triggers
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
        left_layout.addWidget(self.btn_trigger)
        
        # Add Notification Center
        self.notification_center = NotificationCenter()
        left_layout.addWidget(self.notification_center)
        
        split_layout.addWidget(self.left_card, 5)
        
        # Right Panel (Real-Time Metrics)
        self.right_card = GlassCard()
        right_layout = QVBoxLayout(self.right_card)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(12)
        
        lbl_metrics_title = QLabel("PERIPHERAL STATUS && RISK INTEGRITY")
        lbl_metrics_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        right_layout.addWidget(lbl_metrics_title)
        
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
        
        # Metadata Card (Maintained for full compatibility)
        self.meta_subcard = QWidget()
        self.meta_subcard.setStyleSheet("background: rgba(255,255,255,6); border-radius: 12px;")
        meta_layout = QVBoxLayout(self.meta_subcard)
        meta_layout.setContentsMargins(12, 12, 12, 12)
        meta_layout.setSpacing(6)
        
        self.lbl_meta_name = QLabel("Active Device: None")
        self.lbl_meta_name.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-family: 'Inter'; font-size: 12px; font-weight: bold;")
        self.lbl_meta_category = QLabel("Classification: Disconnected")
        self.lbl_meta_category.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        self.lbl_meta_vid_pid = QLabel("Hardware ID: N/A")
        self.lbl_meta_vid_pid.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 11px;")
        
        meta_layout.addWidget(self.lbl_meta_name)
        meta_layout.addWidget(self.lbl_meta_category)
        meta_layout.addWidget(self.lbl_meta_vid_pid)
        right_layout.addWidget(self.meta_subcard)
        
        # Add System Health Card to the right panel
        self.system_health_card = SystemHealthCard()
        right_layout.addWidget(self.system_health_card)
        
        split_layout.addWidget(self.right_card, 4)
        
        layout.addLayout(split_layout)
        
        # Row 2 (Grid of expanded details)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(16)
        
        # Card 1: Device Info Card
        self.device_info_card = DeviceInfoCard()
        row2_layout.addWidget(self.device_info_card, 5)
        
        # Card 2 & 3: Classification and Storage
        right_sub_col = QVBoxLayout()
        right_sub_col.setSpacing(16)
        
        self.device_class_card = DeviceClassificationCard()
        self.storage_card = StorageInformationCard()
        
        right_sub_col.addWidget(self.device_class_card)
        right_sub_col.addWidget(self.storage_card)
        
        row2_layout.addLayout(right_sub_col, 4)
        layout.addLayout(row2_layout)
        
        self.root_layout.addWidget(scroll)
        
        # Connect signals
        theme_manager.theme_changed.connect(self.update_styles)

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

    def update_datetime_label(self):
        current_dt = QDateTime.currentDateTime()
        self.lbl_datetime.setText(current_dt.toString("dddd, MMM d, yyyy - hh:mm:ss AP"))

    def trigger_physical_injection(self):
        if self.connected_device is not None:
            # Clear / Eject
            self.lbl_status.setText("Secure Terminal: Idle")
            self.usb_visualizer.set_connected(False)
            self.risk_ring.set_threat(False)
            self.lbl_threat_level.setText("THREAT SCORE: CLEAR")
            self.lbl_risk_sub.setText("No anomalies identified on active ports.")
            self.lbl_meta_name.setText("Active Device: None")
            self.lbl_meta_category.setText("Classification: Disconnected")
            self.lbl_meta_vid_pid.setText("Hardware ID: N/A")
            self.btn_trigger.setText("SIMULATE PHYSICAL INJECTION")
            
            # Reset extended cards
            self.device_info_card.reset()
            self.device_class_card.reset()
            self.storage_card.reset()
            self.live_monitor.set_connected(False)
            self.notification_center.add_log(f"Device ejected safely: {self.connected_device['name']}")
            
            self.connected_device = None
            return

        # Fetch Simulated Device
        device = SIMULATED_DEVICES[self.device_idx]
        self.device_idx = (self.device_idx + 1) % len(SIMULATED_DEVICES)
        
        self.connected_device = device
        self.usb_visualizer.set_connected(True, device['category'])
        self.lbl_status.setText("Peripherals Evaluation...")
        
        self.live_monitor.set_connected(True, "Evaluating peripheral...")
        self.notification_center.add_log(f"USB insertion detected: {device['name']}")
        
        # Show Glass Authorization Popup after tiny delay
        QTimer.singleShot(600, lambda: self.show_auth_popup(device))

    def show_auth_popup(self, device):
        self.popup = GlassOverlayPopup(device, self)
        self.popup.authorized.connect(self.handle_popup_action)
        self.popup.resize(self.size())
        self.popup.show()
        self.root_layout.addWidget(self.popup)
        self.root_layout.setCurrentWidget(self.popup)

    def handle_popup_action(self, authorized, device):
        self.root_layout.removeWidget(self.popup)
        self.popup.deleteLater()
        self.popup = None
        
        # Find the scroll area widget (the first widget added)
        scroll_area = self.root_layout.widget(0)
        self.root_layout.setCurrentWidget(scroll_area)
        
        conn_time = QTime.currentTime().toString("hh:mm:ss AP")
        
        if authorized:
            self.lbl_status.setText("Access Authorized")
            self.lbl_threat_level.setText("THREAT SCORE: CLEAR")
            self.lbl_risk_sub.setText("Device is successfully registered and cleared.")
            self.device_authorized.emit(device)
            
            self.live_monitor.set_connected(True, device['name'])
            self.notification_center.add_log(f"Access granted to: {device['name']}")
            self.notification_center.add_log("Classification: " + device['category'])
            self.notification_center.add_log("Scan completed: 0 threats identified.")
        else:
            self.lbl_status.setText("THREAT MITIGATED: BLOCKED")
            self.lbl_threat_level.setText("THREAT SCORE: CRITICAL")
            self.lbl_risk_sub.setText("Device classified as BadUSB threat vectors.")
            self.risk_ring.set_threat(True)
            self.device_blocked.emit(device)
            
            self.live_monitor.set_connected(True, "BLOCKED / SHIELDED")
            self.notification_center.add_log(f"CRITICAL SHIELD triggered for: {device['name']}")
            self.notification_center.add_log("Signature threat: HID Keystroke Spoof Payload detected.")
            
        # Update meta card
        self.lbl_meta_name.setText(f"Active Device: {device['name']}")
        self.lbl_meta_category.setText(f"Classification: {device['category']}")
        self.lbl_meta_vid_pid.setText(f"Hardware ID: {device['vid']}:{device['pid']}")
        self.btn_trigger.setText("EJECT EMULATOR CONNECTION")
        
        # Update extended cards
        self.device_info_card.update_device(device, conn_time)
        self.device_class_card.update_classification(device['category'])
        self.storage_card.update_storage(device)
