import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QScrollArea, QFrame, QGraphicsDropShadowEffect,
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPainterPath, QRadialGradient

from theme_manager import theme_manager, COLORS
from icons import get_glass_icon

class GlassCard(QFrame):
    """Refined Liquid Glass container with zero border artifacts."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['glass_bg']};
                border: none;
                border-radius: 28px;
            }}
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(40)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(15)
        self.shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(self.shadow)

class MinimalHardwareIcon(QLabel):
    """
    Premium SVG-backed hardware icons matching the Liquid Glass aesthetic.
    Dynamically resolved based on device name keywords.
    """
    def __init__(self, device_name="usb", color="#00E5FF", parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setStyleSheet("background: transparent; border: none;")
        self.device_name = device_name.lower()
        self.color = color
        self._update_icon()
        theme_manager.theme_changed.connect(self._update_icon)
        
    def _update_icon(self):
        name = self.device_name
        icon_key = "usb"
        if "hdmi" in name or "display" in name or "monitor" in name: icon_key = "hdmi"
        elif "type-c" in name or "usb-c" in name: icon_key = "type-c"
        elif "jack" in name or "audio" in name or "headphone" in name: icon_key = "jack"
        elif "mouse" in name: icon_key = "mouse"
        elif "keyboard" in name: icon_key = "keyboard"
        elif "hdd" in name or "ssd" in name or "drive" in name: icon_key = "hdd"
        elif "sd" in name or "card" in name: icon_key = "sd-card"
        elif "phone" in name or "mobile" in name: icon_key = "smartphone"
        elif "cam" in name: icon_key = "webcam"
        elif "mic" in name: icon_key = "microphone"
        elif "print" in name: icon_key = "printer"
        elif "pen" in name or "thumb" in name: icon_key = "pendrive"
        
        pixmap = get_glass_icon(icon_key, theme_manager, accent_override=self.color)
        self.setPixmap(pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class FilterChip(QPushButton):
    """Gridless filter chip with minimal glass look."""
    def __init__(self, text, active=False):
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(active)
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        self.toggled.connect(self._update_style)

    def _update_style(self):
        if self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent']};
                    color: {COLORS['bg']};
                    border: none;
                    border-radius: 22px;
                    font-weight: 900;
                    padding: 0 24px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['btn_bg']};
                    color: white;
                    border: none;
                    border-radius: 22px;
                    padding: 0 24px;
                    font-weight: 700;
                }}
            """)

class HistoryCard(GlassCard):
    """Premium expandable card with strictly allocated icons and zero artifacts."""
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.is_expanded = False
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(0)
        
        # Header Area
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Allocated Icon with Dynamic Risk Glow
        risk_color = self._get_risk_color(data['threat_level'])
        self.icon_container = QFrame()
        self.icon_container.setFixedSize(56, 56)
        self.icon_container.setStyleSheet(f"""
            background-color: {risk_color}15;
            border-radius: 20px;
            border: 1px solid {risk_color}30;
        """)
        icon_inner = QVBoxLayout(self.icon_container)
        icon_inner.setContentsMargins(0, 0, 0, 0)
        
        self.icon_widget = MinimalHardwareIcon(data['device'], risk_color)
        icon_inner.addWidget(self.icon_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 2. Text Content
        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(2)
        text_vbox.setContentsMargins(15, 0, 0, 0)
        
        self.name_lbl = QLabel(data['device'])
        self.name_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: 900; border: none; background: transparent;")
        
        self.date_lbl = QLabel(f"{data['date']} • {data.get('time', '12:00 PM')}")
        self.date_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; border: none; background: transparent;")
        
        text_vbox.addWidget(self.name_lbl)
        text_vbox.addWidget(self.date_lbl)
        
        # 3. Risk Metric
        self.score_lbl = QLabel(data['risk'])
        self.score_lbl.setStyleSheet(f"color: {risk_color}; font-size: 24px; font-weight: 900; border: none; background: transparent;")
        
        header_layout.addWidget(self.icon_container)
        header_layout.addLayout(text_vbox)
        header_layout.addStretch()
        header_layout.addWidget(self.score_lbl)
        
        self.layout.addWidget(header_widget)
        
        # 4. Hidden Details
        self.details_pane = QWidget()
        self.details_pane.setVisible(False)
        details_layout = QVBoxLayout(self.details_pane)
        details_layout.setContentsMargins(0, 20, 0, 5)
        details_layout.setSpacing(10)
        
        # Separator
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {risk_color}20;")
        details_layout.addWidget(line)
        
        grid = QGridLayout()
        grid.setSpacing(12)
        info_items = [
            ("MANUFACTURER", data.get('mfg', 'Generic')),
            ("INTERFACE", data.get('interface', 'USB 3.x')),
            ("CONNECTION", data.get('connection', 'Hardware Port')),
            ("THREAT STATUS", data.get('threat', 'No Anomalies Found'))
        ]
        for i, (l_txt, v_txt) in enumerate(info_items):
            l = QLabel(l_txt)
            l.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9px; font-weight: 900; letter-spacing: 1px;")
            v = QLabel(v_txt)
            v.setStyleSheet(f"color: {'white' if 'threat' not in l_txt.lower() else risk_color}; font-size: 13px; font-weight: 700;")
            grid.addWidget(l, i, 0)
            grid.addWidget(v, i, 1)
            
        details_layout.addLayout(grid)
        self.layout.addWidget(self.details_pane)

    def _get_risk_color(self, level):
        levels = {
            "safe": COLORS['success'],
            "low risk": COLORS['warning'],
            "medium risk": "#F97316",
            "high risk": COLORS['danger']
        }
        return levels.get(level.lower(), COLORS['accent'])

    def mousePressEvent(self, event):
        self.is_expanded = not self.is_expanded
        self.details_pane.setVisible(self.is_expanded)
        super().mousePressEvent(event)

class HistoryPage(QScrollArea):
    """
    Final Refined Scan History Page. 
    Strict Allocation of Geometric Icons to Hardware Types.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background: transparent; border: none;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(24, 20, 24, 140)
        self.main_layout.setSpacing(20)

        # Minimal Search Header
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter connection logs...")
        self.search_bar.setFixedHeight(50)
        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['glass_bg']};
                border: none;
                border-radius: 18px;
                padding: 0 20px;
                color: white;
                font-size: 14px;
            }}
        """)
        self.main_layout.addWidget(self.search_bar)

        # Modern Filter Chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(12)
        for text in ["All Devices", "Safe Only", "High Risk"]:
            chips_layout.addWidget(FilterChip(text, active=(text=="All Devices")))
        chips_layout.addStretch()
        self.main_layout.addLayout(chips_layout)

        # DATASET: allocated hardware mapping
        log_data = [
            {"device": "SanDisk Ultra Fit USB", "date": "Oct 26, 2023", "time": "10:30 AM", "risk": "5%", "threat_level": "Safe", "mfg": "SanDisk", "interface": "USB 3.1", "connection": "USB-A", "threat": "None"},
            {"device": "Generic HDMI Monitor", "date": "Oct 26, 2023", "time": "09:45 AM", "risk": "35%", "threat_level": "Medium Risk", "mfg": "Dell", "interface": "HDMI 2.0", "connection": "HDMI", "threat": "EDID Mismatch"},
            {"device": "Unknown Display Port", "date": "Oct 25, 2023", "time": "04:15 PM", "risk": "85%", "threat_level": "High Risk", "mfg": "Unknown", "interface": "DP 1.4", "connection": "DP", "threat": "Unauthorized Firmware"},
            {"device": "Sony WH-1000XM4 Jack", "date": "Oct 25, 2023", "time": "02:00 PM", "risk": "2%", "threat_level": "Safe", "mfg": "Sony", "interface": "Analog", "connection": "3.5mm", "threat": "None"},
            {"device": "Samsung USB-C Drive", "date": "Oct 24, 2023", "time": "11:20 AM", "risk": "12%", "threat_level": "Safe", "mfg": "Samsung", "interface": "Type-C", "connection": "USB-C", "threat": "None"}
        ]
        
        for entry in log_data:
            self.main_layout.addWidget(HistoryCard(entry))
            
        self.main_layout.addStretch()
        self.setWidget(self.container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    window = QWidget()
    window.setFixedSize(480, 800)
    window.setStyleSheet(f"background-color: {COLORS['bg']};")
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0,0,0,0)
    layout.addWidget(HistoryPage())
    window.show()
    sys.exit(app.exec())
