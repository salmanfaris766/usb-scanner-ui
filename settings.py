from PyQt6.QtWidgets import (QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QPushButton, QGraphicsDropShadowEffect, 
                             QComboBox, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QBrush, QPen

from theme_manager import theme_manager, COLORS

# --- REUSABLE COMPONENTS ---

class GlassCard(QFrame):
    """
    Premium Liquid Glass container. 
    Strictly borderless to prevent 'black grid' artifacts.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        # Using '!important' logic in style to override any platform defaults
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['glass_bg']};
                border: none !important;
                border-radius: 24px;
            }}
        """)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(40)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(12)
        self.shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(self.shadow)

    def enterEvent(self, event):
        # Subtle hover glow without lines
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(45, 45, 45, 180);
                border: none !important;
                border-radius: 24px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['glass_bg']};
                border: none !important;
                border-radius: 24px;
            }}
        """)
        super().leaveEvent(event)

class StatusBadge(QWidget):
    """Refined status badge with zero border artifacts."""
    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        # Global clear for the widget container
        self.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        
        self.dot = QWidget()
        self.dot.setFixedSize(8, 8)
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: none;")
        
        self.label = QLabel(text.upper())
        # Explicit border: none for labels to prevent artifacts
        self.label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 800; font-family: 'Inter'; letter-spacing: 1px; border: none; background: transparent;")
        
        layout.addWidget(self.dot)
        layout.addWidget(self.label)

class TouchButton(QPushButton):
    """Large tactile button optimized for Raspberry Pi touchscreen."""
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        bg = COLORS['accent'] if primary else "rgba(255, 255, 255, 12)"
        fg = "#000000" if primary else "#FFFFFF"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 24px;
                font-weight: 800;
                font-size: 13px;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 20);
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 229, 255, 0.6);
                padding-top: 2px;
            }}
        """)

class SettingsRow(QWidget):
    """Standardized settings row with forced border cleanup."""
    def __init__(self, label, value_widget=None, parent=None):
        super().__init__(parent)
        # Ensure the row itself never draws a frame
        self.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        
        self.label = QLabel(label)
        self.label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        layout.addWidget(self.label)
        layout.addStretch()
        
        if value_widget:
            # Injecting explicit border:none into whatever widget is passed
            current_style = value_widget.styleSheet()
            value_widget.setStyleSheet(f"{current_style}; border: none !important; background: transparent;")
            layout.addWidget(value_widget)

# --- SETTINGS PAGE ---

class SettingsPage(QScrollArea):
    """
    Final Refined Settings Page for USB DETECTOR.
    Strictly gridless architecture for Raspberry Pi 7" displays.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        # Clean up the scroll area viewport
        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QWidget#scrollContainer {
                background: transparent;
                border: none;
            }
        """)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.container.setObjectName("scrollContainer")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(24, 20, 24, 140)
        self.main_layout.setSpacing(24)
        
        # 0. Header (Gridless)
        header_layout = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        
        self.title_lbl = QLabel("SETTINGS")
        self.title_lbl.setStyleSheet("color: white; font-size: 28px; font-weight: 900; letter-spacing: -1px; border: none; background: transparent;")
        
        self.sub_lbl = QLabel("Customize USB Detector")
        self.sub_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        
        title_vbox.addWidget(self.title_lbl)
        title_vbox.addWidget(self.sub_lbl)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        
        self.time_lbl = QLabel("09:41 AM")
        self.time_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        header_layout.addWidget(self.time_lbl)
        
        self.main_layout.addLayout(header_layout)

        # 1. Appearance Section
        self.add_section_title("APPEARANCE")
        app_card = GlassCard()
        app_vbox = QVBoxLayout(app_card)
        app_vbox.setContentsMargins(20, 15, 20, 15)
        
        theme_toggle_layout = QHBoxLayout()
        theme_txt = QLabel("Theme Mode")
        theme_txt.setStyleSheet("color: white; font-weight: 600; border: none; background: transparent;")
        theme_toggle_layout.addWidget(theme_txt)
        theme_toggle_layout.addStretch()
        
        self.dark_btn = TouchButton("🌙 Dark", primary=True)
        self.light_btn = TouchButton("☀ Light")
        
        # Connect buttons to Theme Manager
        self.dark_btn.clicked.connect(lambda: theme_manager.set_theme("dark"))
        self.light_btn.clicked.connect(lambda: theme_manager.set_theme("light"))
        
        theme_toggle_layout.addWidget(self.dark_btn)
        theme_toggle_layout.addWidget(self.light_btn)
        app_vbox.addLayout(theme_toggle_layout)
        self.main_layout.addWidget(app_card)

        # 2. Malware Database
        self.add_section_title("MALWARE DATABASE")
        db_card = GlassCard()
        db_vbox = QVBoxLayout(db_card)
        db_vbox.setContentsMargins(20, 20, 20, 20)
        db_vbox.setSpacing(12)
        
        db_vbox.addWidget(SettingsRow("Database Version", QLabel("v2.6.1", styleSheet="color: #A0A0A0; font-weight: 700;")))
        db_vbox.addWidget(SettingsRow("Last Updated", QLabel("Today 09:35 AM", styleSheet="color: #A0A0A0; font-weight: 700;")))
        
        status_row = QHBoxLayout()
        status_txt = QLabel("System Status")
        status_txt.setStyleSheet("color: white; font-weight: 600; border: none; background: transparent;")
        status_row.addWidget(status_txt)
        status_row.addStretch()
        status_row.addWidget(StatusBadge("Updated", COLORS['success']))
        db_vbox.addLayout(status_row)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addWidget(TouchButton("Check Updates"))
        btn_row.addWidget(TouchButton("Update Database", primary=True))
        db_vbox.addLayout(btn_row)
        self.main_layout.addWidget(db_card)

        # 3. WiFi Settings
        self.add_section_title("WIFI NETWORK")
        wifi_card = GlassCard()
        wv = QVBoxLayout(wifi_card)
        wv.setContentsMargins(20, 20, 20, 20)
        wv.addWidget(SettingsRow("Network", QLabel("Office_WiFi", styleSheet="color: white; font-weight: 800;")))
        wv.addWidget(SettingsRow("Signal", QLabel("Excellent", styleSheet=f"color: {COLORS['success']}; font-weight: 800;")))
        wv.addWidget(SettingsRow("IP Address", QLabel("192.168.1.25", styleSheet="color: #A0A0A0; font-family: 'Monospace'; font-weight: 700;")))
        wv.addWidget(TouchButton("Configure Network"))
        self.main_layout.addWidget(wifi_card)

        # 4. System Information
        self.add_section_title("SYSTEM INFORMATION")
        sys_card = GlassCard()
        sv = QVBoxLayout(sys_card)
        sv.setContentsMargins(20, 20, 20, 20)
        info_data = [
            ("OS", "Raspberry Pi OS"),
            ("CPU", "ARM Cortex-A72"),
            ("RAM", "8 GB LPDDR4"),
            ("Temp", "48°C"),
            ("Version", "USB Detector v1.0")
        ]
        for l, v in info_data:
            sv.addWidget(SettingsRow(l, QLabel(v, styleSheet="color: #A0A0A0; font-weight: 700;")))
        self.main_layout.addWidget(sys_card)

        # 5. Security Engine
        self.add_section_title("SECURITY ENGINE")
        eng_card = GlassCard()
        ev = QVBoxLayout(eng_card)
        ev.setContentsMargins(20, 15, 20, 15)
        engines = [
            ("ClamAV", "Running", COLORS['success']),
            ("YARA", "Running", COLORS['success']),
            ("USB Monitor", "Stopped", COLORS['danger']),
            ("Threat Engine", "Updating", COLORS['warning'])
        ]
        for name, status, color in engines:
            row = QHBoxLayout()
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("color: white; font-weight: 600; border: none; background: transparent;")
            row.addWidget(name_lbl)
            row.addStretch()
            row.addWidget(StatusBadge(status, color))
            ev.addLayout(row)
        self.main_layout.addWidget(eng_card)

        # 6. About
        self.add_section_title("ABOUT")
        about_card = GlassCard()
        av = QVBoxLayout(about_card)
        av.setContentsMargins(20, 20, 20, 20)
        
        name_lbl = QLabel("USB DETECTOR")
        name_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 18px; font-weight: 900; border: none; background: transparent;")
        av.addWidget(name_lbl)
        
        ver_lbl = QLabel("Version 1.0.4-STABLE")
        ver_lbl.setStyleSheet("color: white; font-weight: 600; border: none; background: transparent;")
        av.addWidget(ver_lbl)
        
        desc = QLabel("Advanced USB Security Scanner for Raspberry Pi. Designed for air-gapped environment integrity checks.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; line-height: 18px; border: none; background: transparent;")
        av.addWidget(desc)
        self.main_layout.addWidget(about_card)

        # Bottom Actions
        bottom_actions = QHBoxLayout()
        bottom_actions.setSpacing(15)
        
        self.restart_btn = TouchButton("RESTART APPLICATION")
        self.restart_btn.setStyleSheet(self.restart_btn.styleSheet().replace("border: none;", "border: 0.5px solid rgba(255,255,255,10);"))
        
        self.shutdown_btn = TouchButton("SHUTDOWN DEVICE")
        self.shutdown_btn.setStyleSheet(self.shutdown_btn.styleSheet().replace(f"background-color: rgba(255, 255, 255, 12);", f"background-color: {COLORS['danger']};"))
        
        bottom_actions.addWidget(self.restart_btn)
        bottom_actions.addWidget(self.shutdown_btn)
        self.main_layout.addLayout(bottom_actions)

        self.setWidget(self.container)

    def add_section_title(self, title):
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 800; letter-spacing: 2px; margin-top: 10px; border: none; background: transparent;")
        self.main_layout.addWidget(lbl)
