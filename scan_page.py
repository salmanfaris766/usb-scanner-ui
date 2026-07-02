import sys
import math
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QStackedWidget, QFrame, QLabel, 
                             QLineEdit, QPushButton, QGraphicsDropShadowEffect, QScrollArea,
                             QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QConicalGradient, QLinearGradient, QPainterPath, QRadialGradient

# --- CONFIGURATION & DESIGN SYSTEM (LIQUID CYBER) ---
COLORS = {
    "bg": "#050505",
    "surface": "#0D0D0D",
    "accent": "#00E5FF",
    "success": "#22C55E",
    "warning": "#FACC15",
    "danger": "#FF4D4D",
    "text_primary": "#FFFFFF",
    "text_secondary": "rgba(255, 255, 255, 160)",
    "glass_bg": "rgba(25, 25, 25, 220)", 
    "glass_border": "rgba(255, 255, 255, 0)", # Strictly zero to remove grid lines
    "btn_bg": "rgba(255, 255, 255, 12)",
    "btn_hover": "rgba(0, 229, 255, 35)"
}

# --- REUSABLE ATOMIC COMPONENTS ---

class GlassCard(QFrame):
    """Refined borderless glass card to prevent grid artifacts."""
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
        self.shadow.setBlurRadius(35)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(10)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(self.shadow)

class AnimatedActionButton(QPushButton):
    """
    STABILIZED BUTTON:
    Fixed 'jumping' bug by removing dynamic layout-breaking size animations.
    Uses fixed dimensions and internal border glows for feedback.
    """
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(56)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_primary = primary
        
        self.update_style()

    def update_style(self, hovered=False):
        bg = COLORS['accent'] if self.is_primary else (COLORS['btn_hover'] if hovered else COLORS['btn_bg'])
        color = "black" if self.is_primary else "white"
        border = f"1.5px solid {COLORS['accent']}" if hovered and not self.is_primary else "none"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: {border};
                border-radius: 16px;
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }}
        """)

    def enterEvent(self, event):
        self.update_style(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update_style(hovered=False)
        super().leaveEvent(event)

# --- SCANNING VISUALS ---

class LiquidOrbScanner(QWidget):
    """Stabilized 'Liquid Orb' scanning animation with precise coordinate math"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.angle = 0
        self.progress = 0
        self.is_scanning = False
        self.wave = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def set_progress(self, val):
        self.progress = val
        self.update()

    def set_scanning(self, state):
        self.is_scanning = state

    def update_animation(self):
        if self.is_scanning:
            self.angle = (self.angle + 1.2) % 360
            self.wave = (self.wave + 0.05) % 6.28318
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(25, 25, -25, -25)
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2.0

        painter.setPen(QPen(QColor(255, 255, 255, 10), 1.5))
        painter.drawEllipse(center, radius, radius)

        if self.is_scanning:
            pulse = radius * (0.82 + 0.04 * math.sin(self.wave))
            grad = QRadialGradient(center, pulse)
            grad.setColorAt(0, QColor(0, 229, 255, 40))
            grad.setColorAt(1, QColor(0, 229, 255, 0))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, pulse, pulse)

            sweep = QConicalGradient(center, -self.angle + 90)
            sweep.setColorAt(0, QColor(0, 229, 255, 160))
            sweep.setColorAt(0.2, QColor(0, 229, 255, 0))
            painter.setBrush(sweep)
            painter.drawPie(rect, int(self.angle * 16), 55 * 16)

        if self.progress > 0:
            pen = QPen(QColor(COLORS['accent']), 4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(rect, 90 * 16, int(-self.progress * 3.6 * 16))

        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.setFont(QFont("Inter", 38, QFont.Weight.Black))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self.progress)}%")

class LogItem(QWidget):
    def __init__(self, text):
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 4, 0, 4)
        
        check = QLabel("✓")
        check.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        
        msg = QLabel(text)
        msg.setStyleSheet("color: white; font-size: 13px; font-weight: 500; border: none; background: transparent;")
        
        l.addWidget(check)
        l.addWidget(msg)
        l.addStretch()

class InfoRow(QWidget):
    def __init__(self, label, value, color="white"):
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 5, 0, 5)
        
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; border: none; background: transparent;")
        
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 700; border: none; background: transparent;")
        
        l.addWidget(lbl)
        l.addStretch()
        l.addWidget(val)

class StatItem(QWidget):
    def __init__(self, label, value):
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        l = QVBoxLayout(self)
        l.setSpacing(4)
        l.setContentsMargins(0, 0, 0, 0)
        
        v = QLabel(value)
        v.setStyleSheet("color: white; font-size: 18px; font-weight: 900; border: none; background: transparent;")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        n = QLabel(label.upper())
        n.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9px; font-weight: 800; border: none; background: transparent;")
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addWidget(v)
        l.addWidget(n)

# --- MAIN SCAN PAGE ---

class ScanPage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background: transparent; border: none;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setContentsMargins(24, 20, 24, 150)
        self.main_layout.setSpacing(24)
        self.setWidget(self.container)

        # 1. Header
        header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(0)
        h_title = QLabel("Scan Device")
        h_title.setStyleSheet("color: white; font-size: 28px; font-weight: 900; letter-spacing: -0.5px; border: none; background: transparent;")
        h_sub = QLabel("Analyze connected USB hardware for threats.")
        h_sub.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        header_text.addWidget(h_title)
        header_text.addWidget(h_sub)
        header.addLayout(header_text)
        header.addStretch()
        
        dev_ind = GlassCard()
        dev_ind.setFixedSize(190, 54)
        dil = QHBoxLayout(dev_ind)
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {COLORS['success']}; border-radius: 4px; border: none;")
        dil.addWidget(dot)
        dil.addWidget(QLabel("SanDisk Ultra 3.0", styleSheet="color: white; font-size: 11px; font-weight: 800; border: none; background: transparent;"))
        header.addWidget(dev_ind)
        self.main_layout.addLayout(header)

        # 2. Hardware Info
        self.device_card = GlassCard()
        dv = QVBoxLayout(self.device_card)
        dv.setContentsMargins(24, 24, 24, 24)
        dv.addWidget(QLabel("STORAGE HARDWARE", styleSheet=f"color: {COLORS['accent']}; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; border: none; background: transparent;"))
        dv.addWidget(InfoRow("Manufacturer", "SanDisk"))
        dv.addWidget(InfoRow("Capacity", "64 GB"))
        dv.addWidget(InfoRow("File System", "FAT32"))
        self.main_layout.addWidget(self.device_card)

        # 3. Scanner
        self.control_card = GlassCard()
        cv = QVBoxLayout(self.control_card)
        cv.setContentsMargins(30, 40, 30, 40)
        cv.setSpacing(20)
        
        self.status_title = QLabel("Ready to Scan")
        self.status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_title.setStyleSheet("color: white; font-size: 24px; font-weight: 900; border: none; background: transparent;")
        cv.addWidget(self.status_title)

        self.scanner = LiquidOrbScanner()
        cv.addWidget(self.scanner, alignment=Qt.AlignmentFlag.AlignCenter)

        self.start_btn = AnimatedActionButton("START SECURITY SCAN", primary=True)
        self.start_btn.clicked.connect(self.start_scan_sequence)
        cv.addWidget(self.start_btn)
        self.main_layout.addWidget(self.control_card)

        # 4. Progress Card (Hidden)
        self.progress_card = GlassCard()
        self.progress_card.setVisible(False)
        pv = QVBoxLayout(self.progress_card)
        pv.setContentsMargins(20, 20, 20, 20)
        self.stage_lbl = QLabel("Initializing Engine...")
        self.stage_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: 800; border: none; background: transparent;")
        pv.addWidget(self.stage_lbl)
        
        met_layout = QHBoxLayout()
        self.met_elapsed = QLabel("00:00")
        self.met_remain = QLabel("00:15")
        self.met_files = QLabel("0")
        for lbl, val in [("ELAPSED", self.met_elapsed), ("REMAINING", self.met_remain), ("FILES", self.met_files)]:
            vbox = QVBoxLayout()
            vbox.addWidget(QLabel(lbl, styleSheet=f"color: {COLORS['text_secondary']}; font-size: 9px; font-weight: 800; border: none; background: transparent;"))
            val.setStyleSheet("color: white; font-size: 15px; font-weight: 900; border: none; background: transparent;")
            vbox.addWidget(val)
            met_layout.addLayout(vbox)
        pv.addLayout(met_layout)
        self.main_layout.addWidget(self.progress_card)

        # 5. Live Activity Log (Hidden until scanning is finished)
        self.log_card = GlassCard()
        self.log_card.setVisible(False)
        lv = QVBoxLayout(self.log_card)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.addWidget(QLabel("SCAN ACTIVITY SUMMARY", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 800; border: none; background: transparent;"))
        self.log_container = QVBoxLayout()
        lv.addLayout(self.log_container)
        self.main_layout.addWidget(self.log_card)

        # 6. File Inventory
        self.inv_card = GlassCard()
        self.inv_card.setVisible(False)
        iv = QVBoxLayout(self.inv_card)
        iv.setContentsMargins(24, 24, 24, 24)
        iv.addWidget(QLabel("FILE INVENTORY", styleSheet=f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 800; border: none; background: transparent;"))
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.addWidget(StatItem("Files", "1250"), 0, 0)
        grid.addWidget(StatItem("Folders", "220"), 0, 1)
        grid.addWidget(StatItem("Exec", "15"), 0, 2)
        grid.addWidget(StatItem("Arch", "8"), 1, 0)
        grid.addWidget(StatItem("Hidden", "2"), 1, 1)
        iv.addLayout(grid)
        self.main_layout.addWidget(self.inv_card)

        # 7. Threat Analysis
        self.threat_card = GlassCard()
        self.threat_card.setVisible(False)
        tv = QVBoxLayout(self.threat_card)
        tv.setContentsMargins(20, 20, 20, 20)
        self.threat_title = QLabel("Analyzing...")
        self.threat_title.setStyleSheet(f"color: {COLORS['accent']}; font-size: 18px; font-weight: 900; border: none; background: transparent;")
        tv.addWidget(self.threat_title)
        self.threat_detail_vbox = QVBoxLayout()
        tv.addLayout(self.threat_detail_vbox)
        self.main_layout.addWidget(self.threat_card)

        # 8. Post Scan Actions
        self.action_layout = QVBoxLayout()
        self.action_layout.setSpacing(12)
        self.main_layout.addLayout(self.action_layout)

    def start_scan_sequence(self):
        self.start_btn.setEnabled(False)
        self.start_btn.setText("SCANNING...")
        self.status_title.setText("Analysis in Progress")
        self.scanner.set_scanning(True)
        self.progress_card.setVisible(True)
        # Log card, inventory, and threat card kept hidden during active scan to prevent layout jumps
        self.log_card.setVisible(False) 
        self.threat_card.setVisible(False)
        self.inv_card.setVisible(False)
        
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.run_simulation)
        self.scan_step = 0
        self.scan_timer.start(80)

    def run_simulation(self):
        self.scan_step += 1
        prog = min(100, self.scan_step)
        self.scanner.set_progress(prog)
        self.met_files.setText(str(int(prog * 12.5)))
        stages = [
            (5, "Reading Device Information"),
            (15, "Verifying USB Storage"),
            (30, "Enumerating Filesystem"),
            (50, "Checking Hidden Files"),
            (70, "Inspecting Archives"),
            (85, "Analyzing Executables"),
            (95, "Calculating Risk")
        ]
        for p, s in stages:
            if prog == p:
                self.stage_lbl.setText(s)
                # Items added to log but not shown until finished
                self.log_container.addWidget(LogItem(f"{s} Complete"))
        if prog == 100:
            self.scan_timer.stop()
            self.finish_scan()

    def finish_scan(self):
        self.scanner.set_scanning(False)
        self.start_btn.setVisible(False)
        self.status_title.setText("Scan Complete")
        
        # Show all tabs once scanning is finished to ensure zero layout jumping during scan
        self.log_card.setVisible(True)
        self.threat_card.setVisible(True)
        self.inv_card.setVisible(True)
        
        self.threat_title.setText("⚠ THREAT DETECTED: Trojan.Generic")
        self.threat_title.setStyleSheet(f"color: {COLORS['danger']}; font-size: 18px; font-weight: 900; border: none; background: transparent;")
        self.threat_detail_vbox.addWidget(InfoRow("Severity", "High", COLORS['danger']))
        self.threat_detail_vbox.addWidget(InfoRow("Location", "E:\\setup_crack.exe"))
        
        while self.action_layout.count():
            item = self.action_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for label in ["QUARANTINE FILES", "EXPORT REPORT", "SCAN AGAIN"]:
            btn = AnimatedActionButton(label, primary=(label=="QUARANTINE FILES"))
            if label == "SCAN AGAIN":
                btn.clicked.connect(self.reset_scan)
            self.action_layout.addWidget(btn)

    def reset_scan(self):
        self.scanner.set_progress(0)
        self.status_title.setText("Ready to Scan")
        self.start_btn.setVisible(True)
        self.start_btn.setEnabled(True)
        self.start_btn.setText("START SECURITY SCAN")
        self.progress_card.setVisible(False)
        self.log_card.setVisible(False)
        self.threat_card.setVisible(False)
        self.inv_card.setVisible(False)
        while self.log_container.count():
            item = self.log_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        while self.threat_detail_vbox.count():
            item = self.threat_detail_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        while self.action_layout.count():
            item = self.action_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    window = QMainWindow()
    window.setFixedSize(800, 480)
    window.setStyleSheet(f"background: {COLORS['bg']};")
    window.setCentralWidget(ScanPage())
    window.show()
    sys.exit(app.exec())
