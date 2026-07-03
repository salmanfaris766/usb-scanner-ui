import sys
import math
import random
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QStackedWidget, QFrame, QLabel, 
                             QLineEdit, QPushButton, QGraphicsDropShadowEffect, QScrollArea,
                             QGridLayout, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QRect, QRectF, QPointF, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QConicalGradient, QLinearGradient, QPainterPath, QPixmap

# --- CONSTANTS & DUMMY DATABASE ---
COLORS = {
    'bg': '#07080d',               # Space black
    'glass_bg': 'rgba(20, 24, 38, 180)', # Cyber transparent glass
    'glass_border': 'rgba(0, 229, 255, 40)', # Cyber glowing border
    'accent': '#00e5ff',           # Bright Cyan
    'text_primary': '#ffffff',
    'text_secondary': '#8f9cae',
    'btn_bg': 'rgba(255, 255, 255, 12)',
    'btn_hover': 'rgba(0, 229, 255, 50)',
}

DUMMY_DEVICES = [
    {
        "name": "SanDisk Ultra USB 3.0",
        "category": "USB Flash Drive",
        "manufacturer": "SanDisk Corp.",
        "vendor_id": "0x0781",
        "product_id": "0x5581",
        "serial": "SD9182391023912",
        "usb_ver": "3.0",
        "capacity": "64 GB",
        "used": "18 GB",
        "free": "46 GB",
        "progress": 28,
        "fs": "FAT32",
        "is_storage": True
    },
    {
        "name": "Kingston DataTraveler",
        "category": "Pen Drive",
        "manufacturer": "Kingston Technology",
        "vendor_id": "0x0951",
        "product_id": "0x1666",
        "serial": "KDT9981248912",
        "usb_ver": "3.1",
        "capacity": "128 GB",
        "used": "45 GB",
        "free": "83 GB",
        "progress": 35,
        "fs": "exFAT",
        "is_storage": True
    },
    {
        "name": "Samsung T7 Portable SSD",
        "category": "External SSD",
        "manufacturer": "Samsung Electronics",
        "vendor_id": "0x04e8",
        "product_id": "0x61f5",
        "serial": "SST7SSD98124",
        "usb_ver": "3.2 (Type-C)",
        "capacity": "1000 GB",
        "used": "320 GB",
        "free": "680 GB",
        "progress": 32,
        "fs": "NTFS",
        "is_storage": True
    },
    {
        "name": "Western Digital MyPassport",
        "category": "External HDD",
        "manufacturer": "Western Digital Corp.",
        "vendor_id": "0x1058",
        "product_id": "0x25e1",
        "serial": "WDHDD2819412",
        "usb_ver": "3.0",
        "capacity": "2000 GB",
        "used": "1450 GB",
        "free": "550 GB",
        "progress": 72,
        "fs": "NTFS",
        "is_storage": True
    },
    {
        "name": "Logitech MX Mechanical KB",
        "category": "USB Keyboard",
        "manufacturer": "Logitech Inc.",
        "vendor_id": "0x046d",
        "product_id": "0xc31c",
        "serial": "LOGIKB31289",
        "usb_ver": "2.0",
        "capacity": "N/A",
        "used": "N/A",
        "free": "N/A",
        "progress": 0,
        "fs": "N/A",
        "is_storage": False
    },
    {
        "name": "Razer DeathAdder Mouse",
        "category": "USB Mouse",
        "manufacturer": "Razer Inc.",
        "vendor_id": "0x1532",
        "product_id": "0x005c",
        "serial": "RZMS291248",
        "usb_ver": "2.0",
        "capacity": "N/A",
        "used": "N/A",
        "free": "N/A",
        "progress": 0,
        "fs": "N/A",
        "is_storage": False
    },
    {
        "name": "Google Pixel 8 Pro",
        "category": "Mobile Device",
        "manufacturer": "Google LLC",
        "vendor_id": "0x18d1",
        "product_id": "0x4ee1",
        "serial": "PXL8PRO7718A",
        "usb_ver": "3.1 (Type-C)",
        "capacity": "256 GB",
        "used": "112 GB",
        "free": "144 GB",
        "progress": 43,
        "fs": "MTP / ext4",
        "is_storage": True
    },
    {
        "name": "Anker USB-C Hub HDMI",
        "category": "HDMI Device",
        "manufacturer": "Anker Co.",
        "vendor_id": "0x2109",
        "product_id": "0x2811",
        "serial": "ANKRHDMI992",
        "usb_ver": "3.0",
        "capacity": "N/A",
        "used": "N/A",
        "free": "N/A",
        "progress": 0,
        "fs": "N/A",
        "is_storage": False
    },
    {
        "name": "Sony WH-1000XM4 Adapter",
        "category": "3.5 mm Audio Device",
        "manufacturer": "Sony Corp.",
        "vendor_id": "0x054c",
        "product_id": "0x09cc",
        "serial": "SNYADJACK20",
        "usb_ver": "2.0",
        "capacity": "N/A",
        "used": "N/A",
        "free": "N/A",
        "progress": 0,
        "fs": "N/A",
        "is_storage": False
    },
    {
        "name": "SanDisk Extreme Pro SD",
        "category": "SD Card",
        "manufacturer": "SanDisk Corp.",
        "vendor_id": "0x0781",
        "product_id": "0xb052",
        "serial": "SDCARDEX88219",
        "usb_ver": "3.0 (Reader)",
        "capacity": "256 GB",
        "used": "80 GB",
        "free": "176 GB",
        "progress": 31,
        "fs": "exFAT",
        "is_storage": True
    }
]

SUPPORTED_CATEGORIES = [
    "USB Flash Drive",
    "Pen Drive",
    "External HDD",
    "External SSD",
    "USB Keyboard",
    "USB Mouse",
    "USB-C Device",
    "HDMI Device",
    "3.5 mm Audio Device",
    "SD Card",
    "Mobile Device",
    "Unknown Device"
]

# --- THEME MANAGER FALLBACK ---
try:
    from theme_manager import theme_manager, COLORS as IMPORTED_COLORS
    COLORS.update(IMPORTED_COLORS)
except ImportError:
    class ThemeManager(QObject := object):
        theme_changed = pyqtSignal(str) if 'pyqtSignal' in globals() else None
        def __init__(self):
            if hasattr(super(), '__init__'):
                super().__init__()
            self.current_theme = "dark"
        def get_color(self, name):
            return COLORS.get(name, '#ffffff')
    theme_manager = ThemeManager()

# Create pyqtSignal subclass on fallback if needed
if not hasattr(theme_manager, 'theme_changed'):
    class ThemeManagerWithSignal(QTimer): # QTimer is a QObject to support signals
        theme_changed = pyqtSignal(str)
        def __init__(self):
            super().__init__()
            self.current_theme = "dark"
        def get_color(self, name):
            return COLORS.get(name, '#ffffff')
    theme_manager = ThemeManagerWithSignal()

# --- ICONS UTILITY FALLBACK ---
try:
    from icons import get_glass_icon
except ImportError:
    def get_glass_icon(name, theme_manager, is_hover=False, is_active=False):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        accent = QColor(theme_manager.get_color("accent"))
        secondary = QColor(theme_manager.get_color("text_secondary"))
        color = accent if (is_active or is_hover) else secondary
        
        painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        if name == "dashboard":
            painter.drawArc(4, 4, 24, 24, 0 * 16, 180 * 16)
            painter.drawLine(16, 16, 24, 8)
        elif name == "scan":
            painter.drawEllipse(6, 6, 14, 14)
            painter.drawLine(18, 18, 26, 26)
        elif name == "history":
            painter.drawEllipse(6, 6, 20, 20)
            painter.drawLine(16, 16, 16, 10)
            painter.drawLine(16, 16, 20, 16)
        elif name == "settings":
            painter.drawEllipse(11, 11, 10, 10)
            for i in range(8):
                angle = i * math.pi / 4
                x1 = int(16 + 8 * math.cos(angle))
                y1 = int(16 + 8 * math.sin(angle))
                x2 = int(16 + 12 * math.cos(angle))
                y2 = int(16 + 12 * math.sin(angle))
                painter.drawLine(x1, y1, x2, y2)
        else:
            painter.drawEllipse(12, 12, 8, 8)
            
        painter.end()
        return pixmap

# --- MODERN PROCEDURAL VECTOR DEVICE ICON DRAWING ---
def draw_category_vector_icon(painter, category, x, y, size):
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    accent = QColor(theme_manager.get_color("accent"))
    painter.setPen(QPen(accent, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    
    cx, cy = x + size // 2, y + size // 2
    
    if category in ["USB Flash Drive", "Pen Drive"]:
        painter.drawRoundedRect(cx - 8, cy - 14, 16, 28, 4, 4)
        painter.drawRect(cx - 5, cy - 22, 10, 8)
        painter.drawLine(cx - 2, cy - 18, cx - 2, cy - 16)
        painter.drawLine(cx + 2, cy - 18, cx + 2, cy - 16)
    elif category == "External HDD":
        painter.drawRoundedRect(cx - 14, cy - 18, 28, 36, 6, 6)
        painter.drawEllipse(cx - 10, cy - 10, 20, 20)
        painter.drawEllipse(cx - 4, cy - 4, 8, 8)
        painter.drawLine(cx, cy + 10, cx - 3, cy - 1)
    elif category == "External SSD":
        painter.drawRoundedRect(cx - 15, cy - 18, 30, 36, 5, 5)
        painter.setFont(QFont("Inter", 8, QFont.Weight.Bold))
        painter.drawText(QRect(cx - 15, cy - 6, 30, 16), Qt.AlignmentFlag.AlignCenter, "SSD")
        painter.drawLine(cx - 10, cy - 10, cx + 10, cy - 10)
        painter.drawLine(cx - 10, cy + 10, cx + 10, cy + 10)
    elif category == "USB Keyboard":
        painter.drawRoundedRect(cx - 20, cy - 10, 40, 20, 3, 3)
        painter.drawRect(cx - 16, cy - 6, 6, 4)
        painter.drawRect(cx - 7, cy - 6, 6, 4)
        painter.drawRect(cx + 2, cy - 6, 6, 4)
        painter.drawRect(cx + 11, cy - 6, 5, 4)
        painter.drawRect(cx - 16, cy + 1, 32, 4)
    elif category == "USB Mouse":
        painter.drawEllipse(cx - 10, cy - 16, 20, 32)
        painter.drawLine(cx, cy - 16, cx, cy)
        painter.drawRect(cx - 2, cy - 10, 4, 6)
    elif category == "USB-C Device":
        painter.drawRoundedRect(cx - 14, cy - 7, 28, 14, 5, 5)
        painter.drawLine(cx - 8, cy, cx + 8, cy)
    elif category == "HDMI Device":
        path = QPainterPath()
        path.moveTo(cx - 12, cy - 10)
        path.lineTo(cx + 12, cy - 10)
        path.lineTo(cx + 8, cy + 10)
        path.lineTo(cx - 8, cy + 10)
        path.closeSubpath()
        painter.drawPath(path)
        for i in range(4):
            px = cx - 5 + i * 3
            painter.drawLine(px, cy - 6, px, cy - 2)
    elif category == "3.5 mm Audio Device":
        painter.drawArc(cx - 14, cy - 14, 28, 28, 0, 180 * 16)
        painter.drawRoundedRect(cx - 16, cy, 5, 9, 2, 2)
        painter.drawRoundedRect(cx + 11, cy, 5, 9, 2, 2)
    elif category == "SD Card":
        path = QPainterPath()
        path.moveTo(cx - 10, cy - 16)
        path.lineTo(cx + 4, cy - 16)
        path.lineTo(cx + 10, cy - 10)
        path.lineTo(cx + 10, cy + 16)
        path.lineTo(cx - 10, cy + 16)
        path.closeSubpath()
        painter.drawPath(path)
        for i in range(3):
            px = cx - 6 + i * 3
            painter.drawLine(px, cy - 12, px, cy - 7)
    elif category == "Mobile Device":
        painter.drawRoundedRect(cx - 12, cy - 18, 24, 36, 5, 5)
        painter.drawRect(cx - 10, cy - 14, 20, 26)
        painter.drawEllipse(cx - 1, cy - 16, 2, 1)
    else:
        painter.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        painter.drawText(QRect(cx - 15, cy - 15, 30, 30), Qt.AlignmentFlag.AlignCenter, "?")

# --- REUSABLE ATOMIC COMPONENTS ---
class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['glass_bg']};
                border: 0.5px solid {COLORS['glass_border']};
                border-radius: 20px;
            }}
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(25)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(0, 229, 255, 30))
        self.setGraphicsEffect(self.shadow)

class GlassProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.setFixedHeight(10)
    def setValue(self, val):
        self.value = val
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Track background
        painter.setBrush(QBrush(QColor(255, 255, 255, 15)))
        painter.setPen(Qt.PenStyle.NoPen)
        rect = QRectF(self.rect())
        painter.drawRoundedRect(rect, 5, 5)
        
        # Glowing progress fill
        if self.value > 0:
            fill_width = rect.width() * (self.value / 100.0)
            fill_rect = QRectF(0, 0, fill_width, rect.height())
            accent = QColor(theme_manager.get_color("accent"))
            
            gradient = QLinearGradient(0, 0, rect.width(), 0)
            gradient.setColorAt(0, accent)
            gradient.setColorAt(1, QColor(0, 160, 255, 180))
            
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(fill_rect, 5, 5)

class StatusBadge(QWidget):
    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)
        
        self.dot = QWidget()
        self.dot.setFixedSize(6, 6)
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 3px; border: none;")
        
        self.label = QLabel(text.upper())
        self.label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; border: none; background: transparent;")
        
        layout.addWidget(self.dot)
        layout.addWidget(self.label)

class AnimatedUSBWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(140, 120)
        self.pulse = 0
        self.flow = 0
        self.connected = False
        self.category = "Unknown Device"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)
    def set_connected(self, connected, category="Unknown Device"):
        self.connected = connected
        self.category = category
        self.update()
    def update_animation(self):
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        self.flow = (self.flow + (0.04 if self.connected else 0.02)) % 1.0
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(10, 10, -10, -10)
        center = rect.center() 
        cx, cy = center.x(), center.y()
        
        accent = QColor(theme_manager.get_color("accent"))
        
        # Radial breathing pulse
        glow_alpha = int(35 + 20 * math.sin(self.pulse))
        if self.connected:
            glow_alpha = int(60 + 25 * math.sin(self.pulse * 1.5))
        glow_color = QColor(accent)
        glow_color.setAlpha(glow_alpha)
        
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 42.0, 42.0)
        
        if self.connected:
            # Draw highly modern animated connected graphic
            draw_category_vector_icon(painter, self.category, int(cx - 20), int(cy - 20), 40)
            
            # Draw rotating orbital system details
            pen_ring = QPen(accent, 1, Qt.PenStyle.DashLine)
            painter.setPen(pen_ring)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, 50.0, 50.0)
            
            # Glowing flow particles on orbit
            particle_angle = self.flow * 2 * math.pi
            px = cx + 50 * math.cos(particle_angle)
            py = cy + 50 * math.sin(particle_angle)
            painter.setBrush(QBrush(accent))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), 4.0, 4.0)
        else:
            # USB Plug outline
            pen_color = QColor(accent)
            pen_color.setAlpha(180)
            painter.setPen(QPen(pen_color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            
            head_x, head_y = int(cx - 15), int(cy - 22)
            painter.drawRoundedRect(head_x, head_y, 30, 24, 4, 4)
            painter.drawRect(int(cx - 9), int(cy - 28), 6, 6)
            painter.drawRect(int(cx + 3), int(cy - 28), 6, 6)
            
            # Wavy signal path
            path = QPainterPath()
            path.moveTo(cx, cy + 4)
            path.cubicTo(cx, cy + 22, cx + 22, cy + 34, cx, cy + 46)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
            
            # Glowing flowing packet
            light_pos = path.pointAtPercent(self.flow)
            painter.setBrush(QBrush(accent))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(light_pos, 3.5, 3.5)

class CircularRiskRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self.angle = 0
        self.threat_active = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(30)
    def update_angle(self):
        self.angle = (self.angle + 2) % 360
        self.update()
    def set_threat(self, threat):
        self.threat_active = threat
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        
        accent = QColor(theme_manager.get_color("accent"))
        if self.threat_active:
            accent = QColor("#ff1744") # Dark red for threat status
            
        glass_border = QColor(theme_manager.get_color("glass_border"))
        if glass_border.alpha() == 0:
            glass_border = QColor(255, 255, 255, 25)
            
        painter.setPen(QPen(glass_border, 2.5))
        painter.drawEllipse(rect)
        
        pen = QPen(accent, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, int(-self.angle * 16), 110 * 16)
        
        painter.setPen(QPen(QColor(theme_manager.get_color("text_primary"))))
        painter.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        text = "100%" if self.threat_active else "0%"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

# --- THE PREMIUM FLOATING GLASS MODAL OVERLAYS ---
class GlassOverlayPopup(QFrame):
    clicked_action = pyqtSignal(str) # "inject", "eject", "allow", "cancel", "retry", "reject"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 14, 25, 245);
                border: 1px solid rgba(0, 229, 255, 80);
                border-radius: 18px;
            }
        """)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(35)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(10)
        self.shadow.setColor(QColor(0, 229, 255, 75))
        self.setGraphicsEffect(self.shadow)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 18, 20, 18)
        self.layout.setSpacing(12)
        
        # Header title
        self.title_lbl = QLabel("POPUP TITLE")
        self.title_lbl.setStyleSheet("color: #00e5ff; font-size: 14px; font-weight: 900; letter-spacing: 0.5px; border: none; background: transparent;")
        self.layout.addWidget(self.title_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Message/Body
        self.msg_lbl = QLabel("Popup detailed text goes here.")
        self.msg_lbl.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 500; border: none; background: transparent;")
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.msg_lbl)
        
        # Content placeholder for dynamic fields (e.g. ComboBox)
        self.custom_content = QWidget()
        self.custom_content.setStyleSheet("background: transparent; border: none;")
        self.custom_layout = QVBoxLayout(self.custom_content)
        self.custom_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.custom_content)
        
        # Horizontal Action Button Row
        self.btn_row = QHBoxLayout()
        self.btn_row.setSpacing(10)
        self.layout.addLayout(self.btn_row)
        
        self.hide()
    
    def setup_arrival_popup(self, device_name):
        self.title_lbl.setText("NEW DEVICE FOUND")
        self.msg_lbl.setText(f"A physical connection has been detected on port USB-3.\n\nDevice: <b>{device_name}</b>")
        self.clear_actions()
        
        inject_btn = QPushButton("INJECT")
        inject_btn.setStyleSheet(self.btn_style(is_accent=True))
        inject_btn.clicked.connect(lambda: self.trigger_and_close("inject"))
        
        eject_btn = QPushButton("EJECT")
        eject_btn.setStyleSheet(self.btn_style(is_accent=False))
        eject_btn.clicked.connect(lambda: self.trigger_and_close("eject"))
        
        self.btn_row.addWidget(eject_btn)
        self.btn_row.addWidget(inject_btn)
        self.animate_pop(340, 220)
        
    def setup_authorization_popup(self):
        self.title_lbl.setText("VERIFY CONNECTED DEVICE")
        self.msg_lbl.setText("Verification requirement active. Please specify the category of the connected USB peripheral to continue.")
        self.clear_actions()
        
        self.combo = QComboBox()
        self.combo.addItems(SUPPORTED_CATEGORIES)
        self.combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 15);
                color: white;
                border: 0.5px solid rgba(0, 229, 255, 50);
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 11px;
            }
            QComboBox QAbstractItemView {
                background-color: #07080d;
                color: white;
                selection-background-color: rgba(0, 229, 255, 50);
                border: 0.5px solid rgba(0, 229, 255, 50);
            }
        """)
        self.custom_layout.addWidget(self.combo)
        
        allow_btn = QPushButton("ALLOW")
        allow_btn.setStyleSheet(self.btn_style(is_accent=True))
        allow_btn.clicked.connect(lambda: self.trigger_and_close("allow"))
        
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setStyleSheet(self.btn_style(is_accent=False))
        cancel_btn.clicked.connect(lambda: self.trigger_and_close("cancel"))
        
        self.btn_row.addWidget(cancel_btn)
        self.btn_row.addWidget(allow_btn)
        self.animate_pop(340, 260)
        
    def setup_mismatch_popup(self):
        self.title_lbl.setText("DEVICE TYPE MISMATCH")
        self.title_lbl.setStyleSheet("color: #ff1744; font-size: 14px; font-weight: 900; letter-spacing: 0.5px; border: none; background: transparent;")
        self.msg_lbl.setText("Security Sentinel alert!\n\nThe hardware profiles mismatch the selected device authorization profile. Access has been quarantined.")
        self.clear_actions()
        
        retry_btn = QPushButton("RETRY")
        retry_btn.setStyleSheet(self.btn_style(is_accent=True))
        retry_btn.clicked.connect(lambda: self.trigger_and_close("retry"))
        
        reject_btn = QPushButton("REJECT")
        reject_btn.setStyleSheet(self.btn_style(is_accent=False, is_danger=True))
        reject_btn.clicked.connect(lambda: self.trigger_and_close("reject"))
        
        self.btn_row.addWidget(reject_btn)
        self.btn_row.addWidget(retry_btn)
        self.animate_pop(340, 220)
        
    def clear_actions(self):
        # Clear buttons
        while self.btn_row.count():
            item = self.btn_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Clear custom layouts
        while self.custom_layout.count():
            item = self.custom_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.title_lbl.setStyleSheet("color: #00e5ff; font-size: 14px; font-weight: 900; letter-spacing: 0.5px; border: none; background: transparent;")
                
    def trigger_and_close(self, action):
        self.clicked_action.emit(action)
        self.hide()
        
    def btn_style(self, is_accent=True, is_danger=False):
        if is_danger:
            return """
                QPushButton {
                    background-color: rgba(255, 23, 68, 30);
                    border: 0.5px solid #ff1744;
                    color: #ff1744;
                    font-weight: 800;
                    font-size: 11px;
                    border-radius: 10px;
                    padding: 8px 16px;
                }
                QPushButton:hover { background-color: rgba(255, 23, 68, 65); }
            """
        elif is_accent:
            return """
                QPushButton {
                    background-color: rgba(0, 229, 255, 30);
                    border: 0.5px solid #00e5ff;
                    color: #00e5ff;
                    font-weight: 800;
                    font-size: 11px;
                    border-radius: 10px;
                    padding: 8px 16px;
                }
                QPushButton:hover { background-color: rgba(0, 229, 255, 65); }
            """
        else:
            return """
                QPushButton {
                    background-color: rgba(255, 255, 255, 10);
                    border: 0.5px solid rgba(255, 255, 255, 30);
                    color: white;
                    font-weight: 800;
                    font-size: 11px;
                    border-radius: 10px;
                    padding: 8px 16px;
                }
                QPushButton:hover { background-color: rgba(255, 255, 255, 20); }
            """
            
    def animate_pop(self, target_w, target_h):
        self.show()
        self.raise_()
        parent_rect = self.parent().rect()
        tx = (parent_rect.width() - target_w) // 2
        ty = (parent_rect.height() - target_h) // 2
        
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(280)
        self.anim.setStartValue(QRect(tx + target_w//2, ty + target_h//2, 0, 0))
        self.anim.setEndValue(QRect(tx, ty, target_w, target_h))
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.start()

# --- COMPACT ACTION BUTTON (MOCKED BUT PREMIUM) ---
class CompactActionButton(QPushButton):
    def __init__(self, text, icon_name="", parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_name = icon_name
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 0, 12, 0)
        self._layout.setSpacing(5)
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        if icon_name:
            self._render_icon()
            self._layout.addWidget(self.icon_lbl)
        self.text_label = QLabel(text)
        self._layout.addWidget(self.text_label)
        self._apply_theme()
        theme_manager.theme_changed.connect(self._apply_theme)
        theme_manager.theme_changed.connect(self._render_icon)
    def _render_icon(self):
        if self.icon_name:
            px = get_glass_icon(self.icon_name, theme_manager, is_hover=self.underMouse())
            self.icon_lbl.setPixmap(px.scaled(15, 15, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    def _apply_theme(self):
        c = theme_manager
        self.text_label.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {c.get_color('text_primary')}; background: transparent; border: none;")
        self.setStyleSheet(f"""
            QPushButton {{ background-color: {c.get_color('btn_bg')}; border: 0.5px solid {c.get_color('glass_border')}; border-radius: 10px; }}
            QPushButton:hover {{ background-color: {c.get_color('btn_hover')}; border: 1px solid {c.get_color('accent')}; }}
            QPushButton:pressed {{ background-color: {c.get_color('accent')}25; }}
        """)
    def enterEvent(self, event):
        self._render_icon()
        super().enterEvent(event)
    def leaveEvent(self, event):
        self._render_icon()
        super().leaveEvent(event)

# --- NAVIGATION BUTTON & BAR ---
class NavButton(QPushButton):
    def __init__(self, label, icon_path, index, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(130, 60)
        self.index = index
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_path = icon_path
        
        layout = QVBoxLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 4, 0, 4)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        
        self.text_label = QLabel(label)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.hover_anim = QPropertyAnimation(self, b"size")
        self.update_style()
        theme_manager.theme_changed.connect(lambda: self.update_style(self.underMouse()))
        
    def update_style(self, hovered=False):
        accent = theme_manager.get_color('accent')
        secondary = theme_manager.get_color('text_secondary')
        
        is_active = self.isChecked()
        self.icon_label.setPixmap(get_glass_icon(self.icon_path, theme_manager, hovered, is_active).scaled(26, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        if is_active:
            bg = f"{accent}35"
            border = f"1px solid {accent}"
            color = theme_manager.get_color('text_primary')
        elif hovered:
            bg = "rgba(255, 255, 255, 12)"
            border = "0.5px solid rgba(0, 229, 255, 40)"
            color = theme_manager.get_color('text_primary')
        else:
            bg = "transparent"
            border = "none"
            color = secondary
            
        self.setStyleSheet(f"QPushButton {{ background: {bg}; border: {border}; border-radius: 16px; }}")
        self.text_label.setStyleSheet(f"QLabel {{ font-size: 9px; font-weight: 800; color: {color}; background: transparent; border: none; letter-spacing: 0.3px; }}")

    def enterEvent(self, event):
        if not self.isChecked():
            self.update_style(hovered=True)
        super().enterEvent(event)
    def leaveEvent(self, event):
        if not self.isChecked():
            self.update_style(hovered=False)
        super().leaveEvent(event)

class BottomNav(QFrame):
    page_changed = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(580, 72)
        self._apply_nav_theme()
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(35)
        self.shadow.setColor(QColor(0, 229, 255, 40))
        self.setGraphicsEffect(self.shadow)
        theme_manager.theme_changed.connect(self._apply_nav_theme)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(8)
        self.buttons = []
        
        nav_items = [
            ("Dashboard", "dashboard"), 
            ("Scan", "scan"), 
            ("History", "history"), 
            ("Settings", "settings")
        ]
        
        for i, (text, icon_path) in enumerate(nav_items):
            btn = NavButton(text, icon_path, i)
            btn.clicked.connect(lambda checked, idx=i: self.handle_click(idx))
            self.buttons.append(btn)
            self.layout.addWidget(btn)
        self.buttons[0].setChecked(True)
        self.buttons[0].update_style()
        
    def handle_click(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
            btn.update_style()
        self.page_changed.emit(index)
        
    def _apply_nav_theme(self):
        self.setStyleSheet("QFrame { background: rgba(10, 12, 20, 245); border: 1px solid rgba(0, 229, 255, 40); border-radius: 36px; }")

# --- BASE PAGE CLASS ---
class ScrollablePage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background: transparent; border: none;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(16, 12, 16, 110)
        self.main_layout.setSpacing(14)
        self.setWidget(self.container)

# --- MOCK SECONDARY PAGES ---
class ScanPage(ScrollablePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        title = QLabel("CYBER RADAR SCANNER")
        title.setStyleSheet("color: #00e5ff; font-size: 16px; font-weight: 900; letter-spacing: 1px;")
        self.main_layout.addWidget(title)
        
        radar_card = GlassCard()
        rv = QVBoxLayout(radar_card)
        rv.setContentsMargins(20, 20, 20, 20)
        
        self.radar_lbl = QLabel("Quarantine Radar System Standby")
        self.radar_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: 700; text-align: center;")
        self.radar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(self.radar_lbl)
        
        self.ring = CircularRiskRing()
        rv.addWidget(self.ring, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addWidget(radar_card)
        
        log_card = GlassCard()
        lv = QVBoxLayout(log_card)
        lv.addWidget(QLabel("EVENT SENTINEL LOGGER", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800;"))
        self.logs = QLabel("● SYSTEM [04:19]: Secure Shield Online\n● SENTINEL [04:19]: Active monitoring on USB Hub 3")
        self.logs.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px; color: #00e5ff; line-height: 15px;")
        lv.addWidget(self.logs)
        self.main_layout.addWidget(log_card)

class HistoryPage(ScrollablePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        title = QLabel("DETECTION REPOSITORY")
        title.setStyleSheet("color: #00e5ff; font-size: 16px; font-weight: 900; letter-spacing: 1px;")
        self.main_layout.addWidget(title)
        
        hist_card = GlassCard()
        hv = QVBoxLayout(hist_card)
        hv.setContentsMargins(15, 15, 15, 15)
        hv.setSpacing(10)
        
        hv.addWidget(QLabel("HISTORICAL SCAN RECORDS", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800;"))
        
        # Grid list
        g = QGridLayout()
        g.setSpacing(10)
        g.addWidget(QLabel("DEVICE NAME", styleSheet="color: #00e5ff; font-weight: 800; font-size: 10px;"), 0, 0)
        g.addWidget(QLabel("CLASS", styleSheet="color: #00e5ff; font-weight: 800; font-size: 10px;"), 0, 1)
        g.addWidget(QLabel("THREAT STATUS", styleSheet="color: #00e5ff; font-weight: 800; font-size: 10px;"), 0, 2)
        
        g.addWidget(QLabel("SanDisk Ultra 3.0", styleSheet="color: white; font-size: 11px;"), 1, 0)
        g.addWidget(QLabel("Flash Drive", styleSheet="color: #8f9cae; font-size: 11px;"), 1, 1)
        g.addWidget(QLabel("SECURE (0%)", styleSheet="color: #00e5ff; font-weight: bold; font-size: 11px;"), 1, 2)
        
        g.addWidget(QLabel("Samsung T7 SSD", styleSheet="color: white; font-size: 11px;"), 2, 0)
        g.addWidget(QLabel("SSD", styleSheet="color: #8f9cae; font-size: 11px;"), 2, 1)
        g.addWidget(QLabel("SECURE (0%)", styleSheet="color: #00e5ff; font-weight: bold; font-size: 11px;"), 2, 2)
        
        hv.addLayout(g)
        self.main_layout.addWidget(hist_card)

class SettingsPage(ScrollablePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        title = QLabel("SYSTEM CONFIGURATION")
        title.setStyleSheet("color: #00e5ff; font-size: 16px; font-weight: 900; letter-spacing: 1px;")
        self.main_layout.addWidget(title)
        
        set_card = GlassCard()
        sv = QVBoxLayout(set_card)
        sv.setSpacing(15)
        sv.setContentsMargins(20, 20, 20, 20)
        
        sv.addWidget(QLabel("SENTINEL THREAT PROTOCOLS", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800;"))
        
        # Interactive-style rows
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Real-time Threat Neutralizer Mode", styleSheet="color: white; font-size: 12px; font-weight: bold;"))
        row1.addStretch()
        btn1 = QPushButton("ACTIVE")
        btn1.setStyleSheet("background: rgba(0, 229, 255, 30); border: 0.5px solid #00e5ff; color: #00e5ff; font-size: 10px; font-weight: 900; border-radius: 6px; padding: 4px 10px;")
        row1.addWidget(btn1)
        sv.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Automated Port Vaccination", styleSheet="color: white; font-size: 12px; font-weight: bold;"))
        row2.addStretch()
        btn2 = QPushButton("ENABLED")
        btn2.setStyleSheet("background: rgba(0, 229, 255, 30); border: 0.5px solid #00e5ff; color: #00e5ff; font-size: 10px; font-weight: 900; border-radius: 6px; padding: 4px 10px;")
        row2.addWidget(btn2)
        sv.addLayout(row2)
        
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Acoustic Threat Siren Alert", styleSheet="color: white; font-size: 12px; font-weight: bold;"))
        row3.addStretch()
        btn3 = QPushButton("MUTED")
        btn3.setStyleSheet("background: rgba(255, 255, 255, 10); border: 0.5px solid rgba(255,255,255,30); color: white; font-size: 10px; font-weight: 900; border-radius: 6px; padding: 4px 10px;")
        row3.addWidget(btn3)
        sv.addLayout(row3)
        
        self.main_layout.addWidget(set_card)

# --- THE DYNAMIC DASHBOARD PAGE ---
class DashboardPage(ScrollablePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State control
        self.device_connected = False
        self.current_device_profile = None
        
        # Grid layout to fit touchscreen dimensions perfectly (800x480 responsive setup)
        self.grid = QGridLayout()
        self.grid.setSpacing(14)
        self.main_layout.addLayout(self.grid)
        
        # --- 1. LIVE USB MONITORING CARD ---
        self.monitor_card = GlassCard()
        mv = QVBoxLayout(self.monitor_card)
        mv.setContentsMargins(16, 16, 16, 16)
        mv.setSpacing(8)
        
        # Header Status Badge
        mh = QHBoxLayout()
        mh.addWidget(QLabel("LIVE PORT MONITOR", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"))
        mh.addStretch()
        self.monitor_badge = StatusBadge("WAITING...", "#ffb300", self)
        mh.addWidget(self.monitor_badge)
        mv.addLayout(mh)
        
        # Animated center USB
        self.usb_anim = AnimatedUSBWidget()
        mv.addWidget(self.usb_anim, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Monitoring connection status text
        self.monitor_status_lbl = QLabel("Monitoring USB Ports...")
        self.monitor_status_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 800; text-align: center;")
        self.monitor_status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mv.addWidget(self.monitor_status_lbl)
        
        self.monitor_sub_lbl = QLabel("Ready for hardware injection.")
        self.monitor_sub_lbl.setStyleSheet("color: #8f9cae; font-size: 10px; text-align: center;")
        self.monitor_sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mv.addWidget(self.monitor_sub_lbl)
        
        self.grid.addWidget(self.monitor_card, 0, 0)
        
        # --- 2. DEVICE CLASSIFICATION CARD ---
        self.class_card = GlassCard()
        cv = QVBoxLayout(self.class_card)
        cv.setContentsMargins(16, 16, 16, 16)
        cv.setSpacing(8)
        
        cv.addWidget(QLabel("DEVICE CLASSIFICATION", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"))
        cv.addStretch()
        
        # Dedicated custom container for classification painting
        self.class_icon_lbl = QWidget()
        self.class_icon_lbl.setMinimumSize(64, 64)
        self.class_icon_lbl.paintEvent = self.paint_class_icon
        cv.addWidget(self.class_icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        cv.addStretch()
        
        self.class_lbl = QLabel("No Category Detected")
        self.class_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 800; text-align: center;")
        self.class_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cv.addWidget(self.class_lbl)
        
        self.class_sub_lbl = QLabel("Hardware validation required.")
        self.class_sub_lbl.setStyleSheet("color: #8f9cae; font-size: 10px; text-align: center;")
        self.class_sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cv.addWidget(self.class_sub_lbl)
        
        self.grid.addWidget(self.class_card, 0, 1)
        
        # --- 3. DEVICE INFORMATION CARD ---
        self.info_card = GlassCard()
        iv = QVBoxLayout(self.info_card)
        iv.setContentsMargins(18, 16, 18, 16)
        iv.setSpacing(8)
        
        iv.addWidget(QLabel("HARDWARE SPECIFICATIONS", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"))
        
        self.info_placeholder = QLabel("No Device Connected\nWaiting for USB Device...")
        self.info_placeholder.setStyleSheet("color: #8f9cae; font-size: 12px; font-weight: 500; font-family: 'JetBrains Mono'; line-height: 20px;")
        self.info_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        iv.addWidget(self.info_placeholder)
        
        # Grid of actual specs (hidden initially)
        self.spec_grid_widget = QWidget()
        self.spec_grid_widget.setStyleSheet("background: transparent; border: none;")
        self.spec_grid = QGridLayout(self.spec_grid_widget)
        self.spec_grid.setContentsMargins(0, 4, 0, 0)
        self.spec_grid.setSpacing(6)
        
        # Layout templates for specs
        self.spec_labels = {}
        spec_keys = [
            ("Device Name", 0), ("Manufacturer", 1), 
            ("Vendor ID", 2), ("Product ID", 3),
            ("Serial Number", 4), ("USB Version", 5), 
            ("File System", 6), ("Connection Time", 7)
        ]
        for key, row in spec_keys:
            key_lbl = QLabel(key)
            key_lbl.setStyleSheet("color: #8f9cae; font-size: 10px; font-weight: 700; background: transparent; border: none;")
            val_lbl = QLabel("-")
            val_lbl.setStyleSheet("color: white; font-size: 10px; font-weight: 800; font-family: 'JetBrains Mono'; background: transparent; border: none;")
            self.spec_grid.addWidget(key_lbl, row, 0)
            self.spec_grid.addWidget(val_lbl, row, 1)
            self.spec_labels[key] = val_lbl
            
        self.spec_grid_widget.hide()
        iv.addWidget(self.spec_grid_widget)
        
        self.grid.addWidget(self.info_card, 1, 0)
        
        # --- 4. STORAGE INFORMATION CARD ---
        self.storage_card = GlassCard()
        sv = QVBoxLayout(self.storage_card)
        sv.setContentsMargins(18, 16, 18, 16)
        sv.setSpacing(8)
        
        sv.addWidget(QLabel("STORAGE CAPACITY UTILIZATION", styleSheet="color: #8f9cae; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;"))
        
        self.storage_placeholder = QLabel("Storage Analysis Suspended\nConnect physical storage media.")
        self.storage_placeholder.setStyleSheet("color: #8f9cae; font-size: 12px; font-weight: 500; font-family: 'JetBrains Mono'; line-height: 20px;")
        self.storage_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sv.addWidget(self.storage_placeholder)
        
        # Active Storage metrics (hidden initially)
        self.storage_metrics_widget = QWidget()
        self.storage_metrics_widget.setStyleSheet("background: transparent; border: none;")
        self.storage_metrics_vbox = QVBoxLayout(self.storage_metrics_widget)
        self.storage_metrics_vbox.setContentsMargins(0, 0, 0, 0)
        self.storage_metrics_vbox.setSpacing(8)
        
        mh_storage = QHBoxLayout()
        self.storage_use_lbl = QLabel("0% USED")
        self.storage_use_lbl.setStyleSheet("color: #00e5ff; font-size: 14px; font-weight: 900; background: transparent;")
        mh_storage.addWidget(self.storage_use_lbl)
        mh_storage.addStretch()
        self.storage_capacity_sum_lbl = QLabel("Total: -")
        self.storage_capacity_sum_lbl.setStyleSheet("color: #8f9cae; font-size: 10px; background: transparent;")
        mh_storage.addWidget(self.storage_capacity_sum_lbl)
        self.storage_metrics_vbox.addLayout(mh_storage)
        
        self.progress_bar = GlassProgressBar()
        self.storage_metrics_vbox.addWidget(self.progress_bar)
        
        # Details row
        details_row = QHBoxLayout()
        self.storage_used_detail_lbl = QLabel("Used: -")
        self.storage_used_detail_lbl.setStyleSheet("color: white; font-size: 10px; font-weight: bold; background: transparent;")
        self.storage_free_detail_lbl = QLabel("Free: -")
        self.storage_free_detail_lbl.setStyleSheet("color: #00e5ff; font-size: 10px; font-weight: bold; background: transparent;")
        details_row.addWidget(self.storage_used_detail_lbl)
        details_row.addStretch()
        details_row.addWidget(self.storage_free_detail_lbl)
        self.storage_metrics_vbox.addLayout(details_row)
        
        self.storage_metrics_widget.hide()
        sv.addWidget(self.storage_metrics_widget)
        
        self.grid.addWidget(self.storage_card, 1, 1)
        
        # --- Create Floating Modals (As overlays) ---
        self.overlay_popup = GlassOverlayPopup(self)
        self.overlay_popup.clicked_action.connect(self.handle_popup_response)
        
        # --- DEVICE DETECTION SIMULATION LOOP ---
        self.simulation_timer = QTimer(self)
        self.simulation_timer.setSingleShot(True)
        self.simulation_timer.timeout.connect(self.trigger_random_device)
        self.simulation_timer.start(4000) # Initial trigger after 4s
        
    def paint_class_icon(self, event):
        painter = QPainter(self.class_icon_lbl)
        category = self.current_device_profile["category"] if (self.device_connected and self.current_device_profile) else "None"
        draw_category_vector_icon(painter, category, 0, 0, 64)
        painter.end()
        
    def trigger_random_device(self):
        if self.device_connected:
            return
        # Choose random device
        self.current_pending_device = random.choice(DUMMY_DEVICES)
        self.overlay_popup.setup_arrival_popup(self.current_pending_device["name"])
        
    def handle_popup_response(self, action):
        if action == "inject":
            # Direct to Authorization modal
            QTimer.singleShot(150, self.overlay_popup.setup_authorization_popup)
        elif action == "eject":
            self.reset_to_empty_state()
        elif action == "cancel":
            self.reset_to_empty_state()
        elif action == "allow":
            selected_category = self.overlay_popup.combo.currentText()
            expected_category = self.current_pending_device["category"]
            
            if selected_category == expected_category:
                # MATCH! Grant full access!
                self.grant_device_access()
            else:
                # MISMATCH! Quarantine mode.
                QTimer.singleShot(150, self.overlay_popup.setup_mismatch_popup)
        elif action == "retry":
            QTimer.singleShot(150, self.overlay_popup.setup_authorization_popup)
        elif action == "reject":
            self.reset_to_empty_state()
            
    def grant_device_access(self):
        self.device_connected = True
        self.current_device_profile = self.current_pending_device
        
        # 1. Update Live Port Card
        self.monitor_badge.label.setText("CONNECTED")
        self.monitor_badge.label.setStyleSheet("color: #00e5ff; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; border: none; background: transparent;")
        self.monitor_badge.dot.setStyleSheet("background-color: #00e5ff; border-radius: 3px; border: none;")
        self.usb_anim.set_connected(True, self.current_device_profile["category"])
        self.monitor_status_lbl.setText("USB Port 3: Active Connection")
        self.monitor_sub_lbl.setText("Sentinel actively tracking interface.")
        
        # 2. Update Classification Card
        self.class_lbl.setText(self.current_device_profile["category"])
        self.class_sub_lbl.setText("Device Authorized - Access Granted")
        self.class_sub_lbl.setStyleSheet("color: #00e5ff; font-size: 10px; text-align: center; font-weight: bold;")
        self.class_icon_lbl.update()
        
        # 3. Update Specifications Card
        self.info_placeholder.hide()
        self.spec_grid_widget.show()
        
        # Populate values
        self.spec_labels["Device Name"].setText(self.current_device_profile["name"])
        self.spec_labels["Manufacturer"].setText(self.current_device_profile["manufacturer"])
        self.spec_labels["Vendor ID"].setText(self.current_device_profile["vendor_id"])
        self.spec_labels["Product ID"].setText(self.current_device_profile["product_id"])
        self.spec_labels["Serial Number"].setText(self.current_device_profile["serial"])
        self.spec_labels["USB Version"].setText(self.current_device_profile["usb_ver"])
        self.spec_labels["File System"].setText(self.current_device_profile["fs"])
        self.spec_labels["Connection Time"].setText(datetime.now().strftime("%H:%M:%S"))
        
        # 4. Update Storage Card
        self.storage_placeholder.hide()
        self.storage_metrics_widget.show()
        
        if self.current_device_profile["is_storage"]:
            self.storage_use_lbl.setText(f"{self.current_device_profile['progress']}% USED")
            self.storage_capacity_sum_lbl.setText(f"Total: {self.current_device_profile['capacity']}")
            self.progress_bar.setValue(self.current_device_profile["progress"])
            self.storage_used_detail_lbl.setText(f"Used: {self.current_device_profile['used']}")
            self.storage_free_detail_lbl.setText(f"Free: {self.current_device_profile['free']}")
        else:
            self.storage_use_lbl.setText("NON-STORAGE MEDIA")
            self.storage_capacity_sum_lbl.setText("Peripheral Device")
            self.progress_bar.setValue(0)
            self.storage_used_detail_lbl.setText("I/O Device")
            self.storage_free_detail_lbl.setText("0 GB Storage")
            
    def reset_to_empty_state(self):
        self.device_connected = False
        self.current_device_profile = None
        
        # Reset 1
        self.monitor_badge.label.setText("WAITING...")
        self.monitor_badge.label.setStyleSheet("color: #ffb300; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px; border: none; background: transparent;")
        self.monitor_badge.dot.setStyleSheet("background-color: #ffb300; border-radius: 3px; border: none;")
        self.usb_anim.set_connected(False)
        self.monitor_status_lbl.setText("Monitoring USB Ports...")
        self.monitor_sub_lbl.setText("Ready for hardware injection.")
        
        # Reset 2
        self.class_lbl.setText("No Category Detected")
        self.class_sub_lbl.setText("Hardware validation required.")
        self.class_sub_lbl.setStyleSheet("color: #8f9cae; font-size: 10px; text-align: center;")
        self.class_icon_lbl.update()
        
        # Reset 3
        self.spec_grid_widget.hide()
        self.info_placeholder.show()
        for lbl in self.spec_labels.values():
            lbl.setText("-")
            
        # Reset 4
        self.storage_metrics_widget.hide()
        self.storage_placeholder.show()
        
        # Trigger next simulated arrival in 5 seconds
        self.simulation_timer.start(5000)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Handle popup overlay centering manually on resize
        if hasattr(self, 'overlay_popup') and self.overlay_popup.isVisible():
            parent_rect = self.rect()
            pw, ph = self.overlay_popup.width(), self.overlay_popup.height()
            tx = (parent_rect.width() - pw) // 2
            ty = (parent_rect.height() - ph) // 2
            self.overlay_popup.setGeometry(tx, ty, pw, ph)

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB DETECTOR")
        self.setStyleSheet(f"background-color: {COLORS['bg']}; border: none;")
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.header = QFrame()
        self.header.setFixedHeight(75)
        self.header.setStyleSheet("background: transparent; border-bottom: 0.5px solid rgba(0, 229, 255, 30);")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(20, 0, 20, 0)
        
        brand = QVBoxLayout()
        self.title_lbl = QLabel("USB DETECTOR")
        self.title_lbl.setStyleSheet("color: #00e5ff; font-weight: 900; font-size: 20px; letter-spacing: -1px; border: none; background: transparent;")
        self.subtitle_lbl = QLabel("ADVANCED USB SECURITY SCANNER")
        self.subtitle_lbl.setStyleSheet("color: #8f9cae; font-size: 8px; font-weight: 800; letter-spacing: 2px; border: none; background: transparent;")
        brand.addWidget(self.title_lbl)
        brand.addWidget(self.subtitle_lbl)
        h_layout.addLayout(brand)
        h_layout.addStretch()
        
        self.time_lbl = QLabel()
        self.time_lbl.setStyleSheet("color: #00e5ff; font-size: 16px; font-weight: 900; border: none; background: transparent;")
        h_layout.addWidget(self.time_lbl)
        h_layout.addWidget(QLabel("🔔", styleSheet="font-size: 16px; color: #00e5ff; margin-left: 10px; border: none; background: transparent;"))
        
        self.layout.addWidget(self.header)
        
        self.stack = QStackedWidget()
        self.dashboard = DashboardPage()
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(ScanPage())
        self.stack.addWidget(HistoryPage())
        self.stack.addWidget(SettingsPage())
        self.layout.addWidget(self.stack)
        
        self.nav = BottomNav(self)
        self.nav.move(90, 380)
        self.nav.page_changed.connect(self.switch_page)
        
        theme_manager.theme_changed.connect(self.animate_theme_transition)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
    def animate_theme_transition(self, theme_name):
        overlay = QLabel(self)
        overlay.resize(self.size())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        overlay.setPixmap(pixmap)
        overlay.show()
        
        self.anim = QPropertyAnimation(overlay, b"windowOpacity")
        self.anim.setDuration(350)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(overlay.deleteLater)
        self.anim.start()
        
    def switch_page(self, index):
        for i, btn in enumerate(self.nav.buttons):
            btn.setChecked(i == index)
            btn.update_style()
        titles = ["USB DETECTOR", "SCAN", "HISTORY", "SETTINGS"]
        subtitles = ["ADVANCED USB SECURITY SCANNER", "Analyze connected USB devices", "Previous scan records", "Application preferences"]
        self.title_lbl.setText(titles[index])
        self.subtitle_lbl.setText(subtitles[index])
        self.stack.setCurrentIndex(index)
        
    def update_time(self):
        self.time_lbl.setText(datetime.now().strftime("%H:%M:%S"))
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'nav'):
            nav_x = (self.width() - self.nav.width()) // 2
            nav_y = self.height() - self.nav.height() - 15
            self.nav.move(nav_x, int(nav_y))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    window = MainWindow()
    window.resize(800, 480) # Perfectly sized for the Raspberry Pi 7-inch touchscreen
    window.show()
    sys.exit(app.exec())
