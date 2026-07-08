import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from theme import theme_manager
from widgets import GlassCard

# Import new widgets from scan_widgets
from scan_widgets import (CircularProgressRing, AnimatedUSBScanner, 
                          InventoryCard, ThreatCard, WarningCard, ScanStatsCard, 
                          LogCard, ActivityCard, SuspiciousFilePopup, LogContainerCard)

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
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(4)
        
        lbl_welcome = QLabel("CYBER RECONNAISSANCE SCANNER")
        lbl_welcome.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-weight: 800; font-family: 'Inter'; letter-spacing: 1.5px;")
        self.lbl_status = QLabel("Deep Physical Scanning Engine")
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        
        header_layout.addWidget(lbl_welcome)
        header_layout.addWidget(self.lbl_status)
        layout.addLayout(header_layout)
        
        # Main Glass Card body layout
        self.card = GlassCard()
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        self.lbl_scan_info = QLabel("Initiate deep scan to audit all low-level communication registers on USB endpoints.")
        self.lbl_scan_info.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-family: 'Inter'; font-size: 13px;")
        self.lbl_scan_info.setWordWrap(True)
        card_layout.addWidget(self.lbl_scan_info)
        
        # Hidden log box to retain 100% backward compatibility with other scripts referencing self.log_box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.hide()
        card_layout.addWidget(self.log_box)
        
        # Main Horizontal Layout for Dual-Panel Interface
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(24)
        
        # --- LEFT PANEL (Visualizers, Ring & Controls) ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)
        
        # 4. Animated USB scanner visualizer
        self.usb_scanner = AnimatedUSBScanner()
        left_panel.addWidget(self.usb_scanner, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 3. Circular progress ring
        self.progress_bar = CircularProgressRing()
        left_panel.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 9. Estimated Scan Stats (Elapsed, Remaining, Speed, Threats)
        self.stats_card = ScanStatsCard()
        left_panel.addWidget(self.stats_card)
        
        # Scan triggering action
        self.btn_scan = QPushButton("LAUNCH SYSTEM AUDIT")
        self.btn_scan.clicked.connect(self.start_scan)
        left_panel.addWidget(self.btn_scan)
        
        # 17. Post Scan Actions
        self.post_scan_widget = QWidget()
        post_scan_layout = QHBoxLayout(self.post_scan_widget)
        post_scan_layout.setContentsMargins(0, 0, 0, 0)
        post_scan_layout.setSpacing(10)
        
        self.btn_export = QPushButton("EXPORT REPORT")
        self.btn_quarantine = QPushButton("QUARANTINE FILES")
        self.btn_again = QPushButton("SCAN AGAIN")
        self.btn_again.clicked.connect(self.start_scan)
        
        post_scan_layout.addWidget(self.btn_export)
        post_scan_layout.addWidget(self.btn_quarantine)
        post_scan_layout.addWidget(self.btn_again)
        left_panel.addWidget(self.post_scan_widget)
        self.post_scan_widget.hide()
        
        panels_layout.addLayout(left_panel, 1)
        
        # --- RIGHT PANEL (Logs, Activity timeline, and Warnings) ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(14)
        
        # 2. Activity Timeline
        self.activity_card = ActivityCard()
        right_panel.addWidget(self.activity_card)
        
        # 6. File Inventory Card
        self.inventory_card = InventoryCard()
        right_panel.addWidget(self.inventory_card)
        
        # 7. Threat Summary Card
        self.threat_card = ThreatCard()
        right_panel.addWidget(self.threat_card)
        
        # Dynamic Warning Banners Area
        self.warnings_container = QWidget()
        self.warnings_container.setStyleSheet("background: transparent;")
        self.warnings_layout = QVBoxLayout(self.warnings_container)
        self.warnings_layout.setContentsMargins(0, 0, 0, 0)
        self.warnings_layout.setSpacing(8)
        right_panel.addWidget(self.warnings_container)
        
        # 1. Premium Scrollable Logs Card synced with the layout
        self.log_container = LogContainerCard()
        self.logs_scroll = self.log_container.logs_scroll
        self.logs_layout = self.log_container.logs_layout
        
        # Set height of logs container card to leave room for other components
        self.log_container.setMinimumHeight(240)
        right_panel.addWidget(self.log_container, 1)
        
        panels_layout.addLayout(right_panel, 1)
        
        card_layout.addLayout(panels_layout)
        
        # Wrap the GlassCard inside a premium transparent QScrollArea to ensure a smooth, unified page scroll flow
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(128, 128, 128, 60);
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(128, 128, 128, 90);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        self.scroll_area.setWidget(self.card)
        layout.addWidget(self.scroll_area, 1)
        
        # Floating Suspicious File Popup (Absolute position over this widget)
        self.popup = SuspiciousFilePopup(self)
        
        # Scan Timers setup
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self.advance_scan)
        self.scan_progress = 0
        self.log_idx = 0
        
        # Seconds tracker for elapsed & remaining
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_stats_timer)
        self.elapsed_seconds = 0
        self.threat_count = 0
        
        # Trigger flags to avoid duplicate pops
        self._trigger_double_ext = False
        self._trigger_hidden = False
        self._trigger_autorun = False
        self._trigger_malware = False
        
        theme_manager.theme_changed.connect(self.update_styles)
        self.update_styles()

    def update_styles(self):
        self.lbl_status.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 24px; font-weight: 800; font-family: 'Inter';")
        accent = theme_manager.get_color('accent')
        text_primary = theme_manager.get_color('text_primary')
        
        # Main Launch Audit Button Style
        btn_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}aa, stop:1 {accent}77);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 22px;
                padding: 12px 24px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 12px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}, stop:1 {accent}cc);
                border: 1px solid {accent};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}cc, stop:1 {accent}99);
                padding-top: 13px;
                padding-bottom: 11px;
            }}
        """
        self.btn_scan.setStyleSheet(btn_style)
        
        # Color-synced Export Button Style (Cyber Accent Glass look)
        export_btn_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}33, stop:1 {accent}11);
                color: {text_primary};
                border: 1px solid {accent}66;
                border-radius: 18px;
                padding: 10px 18px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}66, stop:1 {accent}33);
                border: 1px solid {accent};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}88, stop:1 {accent}55);
            }}
        """
        self.btn_export.setStyleSheet(export_btn_style)
        
        # Color-synced Quarantine Button Style (Security Alert alert-red)
        quarantine_btn_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff174444, stop:1 #ff174422);
                color: {text_primary};
                border: 1px solid #ff174466;
                border-radius: 18px;
                padding: 10px 18px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff174488, stop:1 #ff174444);
                border: 1px solid #ff1744;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff1744aa, stop:1 #ff174477);
            }}
        """
        self.btn_quarantine.setStyleSheet(quarantine_btn_style)
        
        # Color-synced Scan Again Button Style (Vibrant solid accent highlight)
        again_btn_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}aa, stop:1 {accent}66);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 18px;
                padding: 10px 18px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}, stop:1 {accent}cc);
                border: 1px solid {accent};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {accent}cc, stop:1 {accent}99);
            }}
        """
        self.btn_again.setStyleSheet(again_btn_style)
        
        # Update logs container theme styling
        self.log_container.update_styles()

    def start_scan(self):
        self.log_box.clear()
        self.scan_progress = 0
        self.log_idx = 0
        self.progress_bar.setValue(0)
        self.lbl_scan_info.setText("Audit running. Processing deep peripheral verification metrics...")
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("SCANNING IN PROGRESS...")
        
        # Reset tracker metrics
        self.threat_count = 0
        self.elapsed_seconds = 0
        self._trigger_double_ext = False
        self._trigger_hidden = False
        self._trigger_autorun = False
        self._trigger_malware = False
        
        self.clear_logs_and_warnings()
        self.activity_card.reset()
        self.threat_card.update_threat_report(0, "SAFE", "No anomalies detected. Device signature matches trusted definitions.")
        
        self.btn_scan.show()
        self.post_scan_widget.hide()
        
        # Visual resets
        self.usb_scanner.set_scanning(True)
        self.inventory_card.start_animation(4000)
        self.progress_bar.set_blue_glow(False)
        self.progress_bar.set_draw_check(False)
        self.lbl_status.setText("Deep Physical Scanning Engine")
        
        # Timers activation
        self.scan_timer.start(250)
        self.stats_timer.start(1000)

    def advance_scan(self):
        self.scan_progress += random.randint(4, 9)
        if self.scan_progress >= 100:
            self.scan_progress = 100
            self.progress_bar.setValue(100)
            
            # Stop basic scan timers
            self.scan_timer.stop()
            self.stats_timer.stop()
            
            # Stop scan scanner loop
            self.usb_scanner.set_scanning(False)
            
            # 16. Scan Completion Animation Phase
            self.progress_bar.set_blue_glow(True)
            self.lbl_scan_info.setText("Completing post-processing integrity verification...")
            
            # Write remainder of base logs
            while self.log_idx < len(SCAN_LOGS):
                msg = f"[{self.scan_progress}%] {SCAN_LOGS[self.log_idx]}"
                self.log_box.append(msg)
                self.add_log_card(SCAN_LOGS[self.log_idx])
                self.log_idx += 1
                
            # Play a timed delay transition checkmark (800ms)
            QTimer.singleShot(900, self.finish_scan_animation)
            return
            
        self.progress_bar.setValue(self.scan_progress)
        self.update_timeline_and_alerts(self.scan_progress)
        
        # Output logs proportionally
        expected_log_idx = int((self.scan_progress / 100.0) * len(SCAN_LOGS))
        while self.log_idx <= expected_log_idx and self.log_idx < len(SCAN_LOGS):
            msg = f"[{self.scan_progress}%] {SCAN_LOGS[self.log_idx]}"
            self.log_box.append(msg)
            self.add_log_card(SCAN_LOGS[self.log_idx])
            self.log_idx += 1

    def update_timeline_and_alerts(self, progress):
        # Update stage highlights based on progress boundaries
        if progress < 15:
            self.activity_card.set_stage_status(0, 'scanning')
        elif progress < 30:
            self.activity_card.set_stage_status(0, 'completed')
            self.activity_card.set_stage_status(1, 'scanning')
        elif progress < 45:
            self.activity_card.set_stage_status(1, 'completed')
            self.activity_card.set_stage_status(2, 'scanning')
            
            # 12. Double Extension Warning at ~32%
            if not self._trigger_double_ext:
                self._trigger_double_ext = True
                self.add_warning("Double Extension Detected", "invoice.pdf.exe masquerading as document.", "MEDIUM")
                self.popup_suspicious("invoice.pdf.exe", "E:\\invoice.pdf.exe", "Double extension detected (pdf.exe). High likelihood of masquerading malware.")
                self.threat_count += 1
                self.stats_card.set_threats(self.threat_count)
                
        elif progress < 60:
            self.activity_card.set_stage_status(2, 'completed')
            self.activity_card.set_stage_status(3, 'scanning')
            
            # 11. Hidden File Detection Warning at ~48%
            if not self._trigger_hidden:
                self._trigger_hidden = True
                self.add_warning("Hidden File Detected", "Risk Increased due to hidden system binary .hidden.exe.", "MEDIUM")
                self.threat_count += 1
                self.stats_card.set_threats(self.threat_count)
                
        elif progress < 75:
            self.activity_card.set_stage_status(3, 'completed')
            self.activity_card.set_stage_status(4, 'scanning')
            
            # 13. Autorun Execution Warning at ~64%
            if not self._trigger_autorun:
                self._trigger_autorun = True
                self.add_warning("Potential Auto-Execution Detected", "autorun.inf detected pointing to untrusted payload.", "HIGH")
                self.threat_count += 1
                self.stats_card.set_threats(self.threat_count)
                
        elif progress < 90:
            self.activity_card.set_stage_status(4, 'completed')
            self.activity_card.set_stage_status(5, 'scanning')
            
            # 15. Malware Detection at ~80%
            if not self._trigger_malware:
                self._trigger_malware = True
                self.threat_count += 1
                self.stats_card.set_threats(self.threat_count)
                self.threat_card.update_threat_report(
                    68, "HIGH", 
                    "Severe risk. Active malicious signature trace found. Quarantine recommended.",
                    "Trojan.Generic", "E:\\Downloads\\setup.exe"
                )
                
        elif progress < 100:
            self.activity_card.set_stage_status(5, 'completed')
            self.activity_card.set_stage_status(6, 'scanning')

    def finish_scan_animation(self):
        # Trigger completed look
        self.progress_bar.set_draw_check(True)
        self.lbl_status.setText("Scan Complete")
        self.lbl_scan_info.setText("Reconnaissance scan finalized. Host endpoints audit complete.")
        
        # Complete all activity items
        for idx in range(7):
            self.activity_card.set_stage_status(idx, 'completed')
            
        # Swap main buttons
        self.btn_scan.hide()
        self.post_scan_widget.show()
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("LAUNCH SYSTEM AUDIT")
        
        # Emit scan completed details with accurate counters
        self.scan_completed.emit({
            "date": "Today",
            "files": 1250,
            "threats": self.threat_count,
            "duration": f"{self.elapsed_seconds} sec"
        })

    def update_stats_timer(self):
        if self.scan_progress > 0 and self.scan_progress < 100:
            self.elapsed_seconds += 1
            rate = self.scan_progress / self.elapsed_seconds if self.elapsed_seconds > 0 else 0.1
            remaining = int((100 - self.scan_progress) / rate) if rate > 0 else 8
            speed = random.randint(20, 24)
            self.stats_card.update_stats(self.elapsed_seconds, remaining, speed)

    def add_log_card(self, message):
        card = LogCard(message)
        # Add before the layout spacer
        self.logs_layout.insertWidget(self.logs_layout.count() - 1, card)
        QTimer.singleShot(40, lambda: self.logs_scroll.verticalScrollBar().setValue(
            self.logs_scroll.verticalScrollBar().maximum()
        ))

    def add_warning(self, title, description, level):
        card = WarningCard(title, description, level)
        self.warnings_layout.addWidget(card)

    def popup_suspicious(self, name, path, reason):
        self.popup.show_popup(name, path, reason)

    def clear_logs_and_warnings(self):
        # Clear log list
        for i in reversed(range(self.logs_layout.count())):
            item = self.logs_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        # Clear warning banner cards
        for i in reversed(range(self.warnings_layout.count())):
            item = self.warnings_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        self.stats_card.set_threats(0)
        self.stats_card.update_stats(0, 0, 0)
