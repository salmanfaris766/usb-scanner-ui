import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from theme import theme_manager
from widgets import GlassCard, GlassProgressBar

SCAN_LOGS = [
    "Initializing hardware port listener...",
    "Querying connected descriptors from system buses...",
    "Parsing raw USB descriptor structures...",
    "Validating vendor ID (VID) and product ID (PID)...",
    "Checking layout and keystroke rates for anomalous HID triggers...",
    "Scanning firmware signature fields against database...",
    "Evaluating driver mismatch logs and power draw patterns...",
    "Electrical integrity status: STABLE (5V, 100mA)",
    "Port scan successfully completed. 0 physical threat threats found.",
]

class ScanPage(QWidget):
    scan_completed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        lbl_welcome = QLabel("CYBER RECONNAISSANCE SCANNER")
        lbl_welcome.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-weight: 800; font-family: 'Inter'; letter-spacing: 1.5px;")
        self.lbl_status = QLabel("Deep Physical Scanning Engine")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        
        layout.addWidget(lbl_welcome)
        layout.addWidget(self.lbl_status)
        
        # Body layout
        self.card = GlassCard()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)
        
        self.lbl_scan_info = QLabel("Initiate deep scan to audit all low-level communication registers on USB endpoints.")
        self.lbl_scan_info.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 13px;")
        self.lbl_scan_info.setWordWrap(True)
        card_layout.addWidget(self.lbl_scan_info)
        
        self.progress_bar = GlassProgressBar()
        card_layout.addWidget(self.progress_bar)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Scan logs will be reported here dynamically...")
        self.log_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 50) if {theme_manager.current_theme == 'dark'} else rgba(255, 255, 255, 80);
                color: {theme_manager.get_color('text_primary')};
                border: 0.5px solid {theme_manager.get_color('glass_border')};
                border-radius: 12px;
                font-family: 'JetBrains Mono';
                font-size: 11px;
                padding: 10px;
            }}
        """)
        card_layout.addWidget(self.log_box, 1)
        
        self.btn_scan = QPushButton("LAUNCH SYSTEM AUDIT")
        self.btn_scan.setStyleSheet(f"""
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
        self.btn_scan.clicked.connect(self.start_scan)
        card_layout.addWidget(self.btn_scan)
        
        layout.addWidget(self.card, 1)
        
        # Scan Timer setup
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.advance_scan)
        self.scan_progress = 0
        self.log_idx = 0
        
        theme_manager.theme_changed.connect(self.update_styles)

    def update_styles(self):
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        self.btn_scan.setStyleSheet(f"""
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
        self.log_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0, 0, 0, 50) if {theme_manager.current_theme == 'dark'} else rgba(255, 255, 255, 80);
                color: {theme_manager.get_color('text_primary')};
                border: 0.5px solid {theme_manager.get_color('glass_border')};
                border-radius: 12px;
                font-family: 'JetBrains Mono';
                font-size: 11px;
                padding: 10px;
            }}
        """)

    def start_scan(self):
        self.log_box.clear()
        self.scan_progress = 0
        self.log_idx = 0
        self.progress_bar.setValue(0)
        self.lbl_scan_info.setText("Audit running. Processing deep peripheral verification metrics...")
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("SCANNING IN PROGRESS...")
        self.scan_timer.start(250)

    def advance_scan(self):
        self.scan_progress += random.randint(4, 9)
        if self.scan_progress >= 100:
            self.scan_progress = 100
            self.progress_bar.setValue(100)
            self.scan_timer.stop()
            self.btn_scan.setEnabled(True)
            self.btn_scan.setText("LAUNCH SYSTEM AUDIT")
            self.lbl_scan_info.setText("Reconnaissance scan finalized. Host endpoints cleared.")
            # write final logs
            while self.log_idx < len(SCAN_LOGS):
                self.log_box.append(f"[{self.scan_progress}%] {SCAN_LOGS[self.log_idx]}")
                self.log_idx += 1
            
            # Emit scan completed details
            self.scan_completed.emit({
                "date": "Today",
                "files": random.randint(180, 320),
                "threats": 0,
                "duration": f"{random.randint(10, 18)} sec"
            })
            return
            
        self.progress_bar.setValue(self.scan_progress)
        
        # Output logs proportionally
        expected_log_idx = int((self.scan_progress / 100.0) * len(SCAN_LOGS))
        while self.log_idx <= expected_log_idx and self.log_idx < len(SCAN_LOGS):
            self.log_box.append(f"[{self.scan_progress}%] {SCAN_LOGS[self.log_idx]}")
            self.log_idx += 1
