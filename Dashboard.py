import sys
import math
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
                             QPushButton, QGraphicsDropShadowEffect, QScrollArea,
                             QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QConicalGradient, QLinearGradient, QPainterPath

from theme_manager import theme_manager, COLORS
from icons import get_glass_icon

# --- REUSABLE ATOMIC COMPONENTS ---
class GlassCard(QFrame):
    """Premium Liquid Glass container."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['glass_bg']};
                border: none;
                border-radius: 24px;
            }}
        """)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(12)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(self.shadow)

class StatusBadge(QWidget):
    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        
        self.dot = QWidget()
        self.dot.setFixedSize(8, 8)
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: none;")
        
        self.label = QLabel(text.upper())
        self.label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 800; font-family: 'Inter'; letter-spacing: 1px; border: none; background: transparent;")
        
        layout.addWidget(self.dot)
        layout.addWidget(self.label)

class AnimatedUSBWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 180)
        self.pulse = 0
        self.flow = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)
    def update_animation(self):
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        self.flow = (self.flow + 0.02) % 1.0
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect()).adjusted(20, 20, -20, -20)
        center = rect.center() 
        cx, cy = center.x(), center.y()
        
        # Parse dynamic accent color
        accent = QColor(theme_manager.get_color("accent"))
        
        glow_alpha = int(30 + 20 * math.sin(self.pulse))
        glow_color = QColor(accent)
        glow_color.setAlpha(glow_alpha)
        
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 60.0, 60.0)
        
        pen_color = QColor(accent)
        pen_color.setAlpha(200)
        painter.setPen(QPen(pen_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        
        head_x = int(cx - 25)
        head_y = int(cy - 35)
        painter.drawRoundedRect(head_x, head_y, 50, 40, 6, 6)
        painter.drawRect(int(cx - 15), int(cy - 45), 10, 10)
        painter.drawRect(int(cx + 5), int(cy - 45), 10, 10)
        
        path = QPainterPath()
        path.moveTo(cx, cy + 5)
        path.cubicTo(cx, cy + 40, cx + 40, cy + 60, cx, cy + 80)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        
        light_pos = path.pointAtPercent(self.flow)
        painter.setBrush(QBrush(accent))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(light_pos, 4.0, 4.0)

class CircularRiskRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.start(30)
    def update_angle(self):
        self.angle = (self.angle + 2) % 360
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(5, 5, -5, -5)
        
        accent = QColor(theme_manager.get_color("accent"))
        text_primary = QColor(theme_manager.get_color("text_primary"))
        glass_border = QColor(theme_manager.get_color("glass_border"))
        if glass_border.alpha() == 0:
            glass_border = QColor(theme_manager.get_color("text_primary"))
            glass_border.setAlpha(20)
            
        painter.setPen(QPen(glass_border, 3))
        painter.drawEllipse(rect)
        pen = QPen(accent, 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, int(-self.angle * 16), 90 * 16)
        painter.setPen(QPen(text_primary))
        painter.setFont(QFont("Inter", 14, QFont.Weight.Black))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "0%")

class ActionButton(QPushButton):
    """Ultra-compact action button for horizontal row layout."""
    def __init__(self, text, icon_name="", parent=None):
        super().__init__(parent)
        self.setFixedSize(84, 36) # More compact size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_name = icon_name
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(4)
        
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        if icon_name:
            self._update_icon()
            layout.addWidget(self.icon_lbl)
            
        self.text_lbl = QLabel(text)
        self.text_lbl.setStyleSheet(f"font-size: 9px; font-weight: 800; color: {theme_manager.get_color('text_primary')}; background: transparent; border: none;")
        layout.addWidget(self.text_lbl)
        
        self._update_style()
        
        # Re-render icon and text on theme change
        theme_manager.theme_changed.connect(lambda: self._update_icon())
        theme_manager.theme_changed.connect(lambda: self._update_style())

    def _update_icon(self):
        if self.icon_name:
            pixmap = get_glass_icon(self.icon_name, theme_manager, is_hover=self.underMouse(), is_active=False)
            self.icon_lbl.setPixmap(pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _update_style(self):
        self.text_lbl.setStyleSheet(f"font-size: 9px; font-weight: 800; color: {theme_manager.get_color('text_primary')}; background: transparent; border: none;")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('btn_bg')};
                border: 0.5px solid {theme_manager.get_color('glass_border')};
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('btn_hover')};
                border: 1px solid {theme_manager.get_color('accent')};
            }}
            QPushButton:pressed {{
                background-color: {theme_manager.get_color('accent')}40;
                margin: 1px;
            }}
        """)
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self._update_icon()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._update_icon()

# --- MODULAR DASHBOARD PAGE ---
class DashboardPage(QScrollArea):
    """
    Refined Dashboard Module for USB DETECTOR.
    Optimized for horizontal space and compact interaction.
    """
    scan_requested = pyqtSignal()
    history_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background: transparent; border: none;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(24, 16, 24, 120)
        self.main_layout.setSpacing(24)
        self.setWidget(self.container)
        
        # 1. Device Status Card
        self.status_card = GlassCard()
        sv = QVBoxLayout(self.status_card)
        sv.setContentsMargins(28, 28, 28, 28)
        sv.setSpacing(12)
        
        lbl_status = QLabel("DEVICE STATUS")
        lbl_status.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; border: none; background: transparent;")
        sv.addWidget(lbl_status)
        
        lbl_conn = QLabel("No Device Connected")
        lbl_conn.setStyleSheet("color: white; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; border: none; background: transparent;")
        sv.addWidget(lbl_conn)
        
        lbl_wait = QLabel("Waiting for a USB storage device...")
        lbl_wait.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px; border: none; background: transparent;")
        sv.addWidget(lbl_wait)
        
        self.usb_anim = AnimatedUSBWidget()
        sv.addWidget(self.usb_anim, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_card)

        # 2. Threat Summary Card
        self.threat_card = GlassCard()
        tv = QHBoxLayout(self.threat_card)
        tv.setContentsMargins(24, 24, 24, 24)
        tv.setSpacing(20)
        tv.addWidget(CircularRiskRing())
        
        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(4)
        
        lbl_risk = QLabel("OVERALL RISK")
        lbl_risk.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 800; letter-spacing: 1px; border: none; background: transparent;")
        info_vbox.addWidget(lbl_risk)
        
        lbl_secure = QLabel("Secure Environment")
        lbl_secure.setStyleSheet("color: white; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        info_vbox.addWidget(lbl_secure)
        
        lbl_analysis = QLabel("Status: No Threat Analysis Yet")
        lbl_analysis.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; border: none; background: transparent;")
        info_vbox.addWidget(lbl_analysis)
        
        tv.addLayout(info_vbox)
        tv.addStretch()
        self.main_layout.addWidget(self.threat_card)

        # 3. Compact Quick Actions Bar
        actions_vbox = QVBoxLayout()
        actions_vbox.setSpacing(12)
        
        lbl_actions = QLabel("QUICK ACTIONS")
        lbl_actions.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; border: none; background: transparent;")
        actions_vbox.addWidget(lbl_actions)
        
        # Tight horizontal row for buttons
        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        
        self.scan_btn = ActionButton("Scan", "scan")
        self.scan_btn.clicked.connect(self.scan_requested.emit)
        
        self.history_btn = ActionButton("History", "history")
        self.history_btn.clicked.connect(self.history_requested.emit)
        
        self.settings_btn = ActionButton("Settings", "settings")
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        
        actions_row.addWidget(self.scan_btn)
        actions_row.addWidget(self.history_btn)
        actions_row.addWidget(self.settings_btn)
        actions_row.addStretch()
        
        actions_vbox.addLayout(actions_row)
        self.main_layout.addLayout(actions_vbox)