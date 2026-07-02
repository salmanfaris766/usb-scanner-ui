import sys
import math
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QStackedWidget, QFrame, QLabel, 
                             QLineEdit, QPushButton, QGraphicsDropShadowEffect, QScrollArea,
                             QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QConicalGradient, QLinearGradient, QPainterPath, QPixmap

# --- MODULAR IMPORTS ---
try:
    from scan_page import ScanPage
    from history import HistoryPage
    from settings import SettingsPage
except ImportError:
    class ScanPage(QWidget): pass
    class HistoryPage(QWidget): pass
    class SettingsPage(QWidget): pass

from theme_manager import theme_manager, COLORS
from icons import get_glass_icon

# Colors are now managed by theme_manager.COLORS

# --- REUSABLE ATOMIC COMPONENTS ---

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['glass_bg']};
                border: 0.5px solid {COLORS['glass_border']};
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        self.dot = QWidget()
        self.dot.setFixedSize(8, 8)
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: none;")
        self.label = QLabel(text.upper())
        self.label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 800; font-family: 'Inter'; letter-spacing: 1px; border: none;")
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
        head_x, head_y = int(cx - 25), int(cy - 35)
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
        
        # Parse dynamic colors
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

class CompactActionButton(QPushButton):
    """Compact, SVG-icon quick action button."""
    def __init__(self, text, icon_name="", parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_name = icon_name
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 0, 14, 0)
        self._layout.setSpacing(6)
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        if icon_name:
            self._render_icon()
            self._layout.addWidget(self.icon_lbl)
        self.text_label = QLabel(text)
        self._layout.addWidget(self.text_label)
        self._apply_theme()
        theme_manager.theme_changed.connect(lambda: self._apply_theme())
        theme_manager.theme_changed.connect(lambda: self._render_icon())

    def _render_icon(self):
        if self.icon_name:
            px = get_glass_icon(self.icon_name, theme_manager, is_hover=self.underMouse())
            self.icon_lbl.setPixmap(px.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def _apply_theme(self):
        c = theme_manager
        self.text_label.setStyleSheet(f"font-size: 11px; font-weight: 800; color: {c.get_color('text_primary')}; background: transparent; border: none;")
        self.setStyleSheet(f"""
            QPushButton {{ background-color: {c.get_color('btn_bg')}; border: 0.5px solid {c.get_color('glass_border')}; border-radius: 14px; }}
            QPushButton:hover {{ background-color: {c.get_color('btn_hover')}; border: 1px solid {c.get_color('accent')}; }}
            QPushButton:pressed {{ background-color: {c.get_color('accent')}30; }}
        """)

    def enterEvent(self, event):
        self._render_icon()
        super().enterEvent(event)
    def leaveEvent(self, event):
        self._render_icon()
        super().leaveEvent(event)

# --- NAVIGATION ARCHITECTURE ---

class NavButton(QPushButton):
    def __init__(self, label, icon_path, index, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(140, 64)
        self.index = index
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_path = icon_path
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 6, 0, 6)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Apply strict transparent background to icon container
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        self.set_icon(icon_path)
        
        self.text_label = QLabel(label)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.hover_anim = QPropertyAnimation(self, b"size")
        self.update_style()
        theme_manager.theme_changed.connect(lambda: self.update_style(self.underMouse()))

    def set_icon(self, path):
        # We now use the SVG generator from icons.py, but fallback to pixmap if needed.
        pass

    def update_style(self, hovered=False):
        accent = theme_manager.get_color('accent')
        secondary = theme_manager.get_color('text_secondary')
        
        # Load premium glass SVG icon
        is_active = self.isChecked()
        self.icon_label.setPixmap(get_glass_icon(self.icon_path, theme_manager, hovered, is_active).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        if is_active:
            bg = f"{accent}45" if len(accent) == 7 else "rgba(0, 229, 255, 45)"
            border = f"1px solid {accent}"
            color = theme_manager.get_color('text_primary')
        elif hovered:
            bg_col = "0,0,0" if theme_manager.current_theme == "light" else "255,255,255"
            bg = f"rgba({bg_col}, 15)"
            border = f"0.5px solid rgba({bg_col}, 40)"
            color = theme_manager.get_color('text_primary')
        else:
            bg = "transparent"
            border = "none"
            color = secondary

        self.setStyleSheet(f"QPushButton {{ background: {bg}; border: {border}; border-radius: 32px; }}")
        self.text_label.setStyleSheet(f"QLabel {{ font-size: 10px; font-weight: 900; color: {color}; background: transparent; border: none; letter-spacing: 0.5px; }}")

    def enterEvent(self, event):
        if not self.isChecked():
            self.update_style(hovered=True)
            self.hover_anim.stop()
            self.hover_anim.setDuration(200)
            self.hover_anim.setEndValue(QSize(140, 68))
            self.hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isChecked():
            self.update_style(hovered=False)
            self.hover_anim.stop()
            self.hover_anim.setDuration(200)
            self.hover_anim.setEndValue(QSize(140, 64))
            self.hover_anim.start()
        super().leaveEvent(event)

class BottomNav(QFrame):
    page_changed = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(620, 84)
        self._apply_nav_theme()
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(45)
        self.shadow.setColor(QColor(0, 229, 255, 50))
        self.setGraphicsEffect(self.shadow)
        theme_manager.theme_changed.connect(lambda: self._apply_nav_theme())
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 12, 0)
        self.layout.setSpacing(10)
        self.buttons = []
        
        # MAPPED TO NEW SVG ICON KEYS
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
        if theme_manager.current_theme == "light":
            self.setStyleSheet("QFrame { background: rgba(255, 255, 255, 230); border: 1px solid rgba(0, 0, 0, 8); border-radius: 42px; }")
        else:
            self.setStyleSheet("QFrame { background: rgba(20, 20, 20, 240); border: 1px solid rgba(255, 255, 255, 15); border-radius: 42px; }")

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
        self.main_layout.setContentsMargins(24, 16, 24, 140)
        self.main_layout.setSpacing(24)
        self.setWidget(self.container)

class DashboardPage(ScrollablePage):
    scan_requested = pyqtSignal()
    history_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_card = GlassCard()
        sv = QVBoxLayout(self.status_card)
        sv.setContentsMargins(28, 28, 28, 28)
        sv.setSpacing(12)
        sv.addWidget(QLabel("DEVICE STATUS", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; border: none;"))
        sv.addWidget(QLabel("No Device Connected", styleSheet="color: white; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; border: none;"))
        sv.addWidget(QLabel("Waiting for a USB storage device...", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 14px; border: none;"))
        self.usb_anim = AnimatedUSBWidget()
        sv.addWidget(self.usb_anim, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_card)
        self.threat_card = GlassCard()
        tv = QHBoxLayout(self.threat_card)
        tv.setContentsMargins(24, 24, 24, 24)
        tv.setSpacing(20)
        tv.addWidget(CircularRiskRing())
        info_vbox = QVBoxLayout()
        info_vbox.addWidget(QLabel("OVERALL RISK", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 800; letter-spacing: 1px; border: none;"))
        info_vbox.addWidget(QLabel("Secure Environment", styleSheet="color: white; font-size: 18px; font-weight: 800; border: none;"))
        info_vbox.addWidget(QLabel("Status: No Threat Analysis Yet", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 12px; border: none;"))
        tv.addLayout(info_vbox)
        tv.addStretch()
        self.main_layout.addWidget(self.threat_card)
        self.main_layout.addWidget(QLabel("QUICK ACTIONS", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; border: none;"))
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        self.scan_btn = CompactActionButton("Scan", "scan")
        self.scan_btn.clicked.connect(self.scan_requested.emit)
        self.history_btn = CompactActionButton("History", "history")
        self.history_btn.clicked.connect(self.history_requested.emit)
        self.settings_btn = CompactActionButton("Settings", "settings")
        self.settings_btn.clicked.connect(self.settings_requested.emit)
        actions_row.addWidget(self.scan_btn)
        actions_row.addWidget(self.history_btn)
        actions_row.addWidget(self.settings_btn)
        actions_row.addStretch()
        self.main_layout.addLayout(actions_row)

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
        self.header.setFixedHeight(90)
        self.header.setStyleSheet("background: transparent; border-bottom: 0.5px solid rgba(255, 255, 255, 10);")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(30, 0, 30, 0)
        brand = QVBoxLayout()
        self.title_lbl = QLabel("USB DETECTOR")
        self.title_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-weight: 900; font-size: 24px; letter-spacing: -1.2px; border: none;")
        self.subtitle_lbl = QLabel("ADVANCED USB SECURITY SCANNER")
        self.subtitle_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9px; font-weight: 800; letter-spacing: 2.5px; border: none;")
        brand.addWidget(self.title_lbl)
        brand.addWidget(self.subtitle_lbl)
        h_layout.addLayout(brand)
        h_layout.addStretch()
        self.time_lbl = QLabel()
        self.time_lbl.setStyleSheet(f"color: {COLORS['accent']}; font-size: 20px; font-weight: 900; border: none;")
        h_layout.addWidget(self.time_lbl)
        h_layout.addWidget(QLabel("🔔", styleSheet=f"font-size: 20px; color: {COLORS['accent']}; margin-left: 15px; border: none;"))
        self.layout.addWidget(self.header)
        self.stack = QStackedWidget()
        self.dashboard = DashboardPage()
        self.dashboard.scan_requested.connect(lambda: self.switch_page(1))
        self.dashboard.history_requested.connect(lambda: self.switch_page(2))
        self.dashboard.settings_requested.connect(lambda: self.switch_page(3))
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(ScanPage())
        self.stack.addWidget(HistoryPage())
        self.stack.addWidget(SettingsPage())
        self.layout.addWidget(self.stack)
        self.nav = BottomNav(self)
        self.nav.move(90, 380)
        self.nav.page_changed.connect(self.switch_page)
        
        # Connect to theme manager for cross-fade animations
        theme_manager.theme_changed.connect(self.animate_theme_transition)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def animate_theme_transition(self, theme_name):
        # Create a screenshot of the window BEFORE styles update 
        # (Actually, styles just updated in ThemeManager, so this creates an overlay that fades out to reveal the new theme)
        overlay = QLabel(self)
        overlay.resize(self.size())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        overlay.setPixmap(pixmap)
        overlay.show()
        
        self.anim = QPropertyAnimation(overlay, b"windowOpacity")
        self.anim.setDuration(400)
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
            nav_y = self.height() - self.nav.height() - 30
            self.nav.move(nav_x, int(nav_y))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())