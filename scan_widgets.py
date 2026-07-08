import sys
import random
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QScrollArea, QFrame, 
                             QGridLayout, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPointF, QVariantAnimation, QEasingCurve, QDateTime, QPropertyAnimation
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont, QLinearGradient, QPainterPath, QColor
from theme import theme_manager
from widgets import GlassCard

class GreenCheckIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(22, 22)
        self.anim_progress = 0.0
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(350)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.valueChanged.connect(self._on_anim)
        self.anim.start()

    def _on_anim(self, val):
        self.anim_progress = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        
        # Circle background
        bg_color = QColor("#00e676")
        bg_color.setAlpha(max(0, min(255, int(35 + 220 * self.anim_progress))))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)
        
        # Checkmark line
        if self.anim_progress > 0.2:
            pen = QPen(QColor("#ffffff"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            # Path of checkmark
            p = QPainterPath()
            p.moveTo(rect.left() + rect.width() * 0.3, rect.top() + rect.height() * 0.5)
            p.lineTo(rect.left() + rect.width() * 0.45, rect.top() + rect.height() * 0.65)
            p.lineTo(rect.left() + rect.width() * 0.7, rect.top() + rect.height() * 0.35)
            painter.drawPath(p)

class CircularProgressRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.value = 0.0
        self.display_value = 0.0
        self.blue_glow_active = False
        self.draw_check = False
        
        # Pulse animation
        self.pulse = 0.0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._update_pulse)
        self.pulse_timer.start(30)

        # Smooth value transition animation
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.valueChanged.connect(self._on_anim_value)

    def setValue(self, val):
        self.value = float(val)
        if self.anim.state() == QVariantAnimation.State.Running:
            self.anim.stop()
        self.anim.setStartValue(self.display_value)
        self.anim.setEndValue(self.value)
        self.anim.start()

    def _on_anim_value(self, val):
        self.display_value = val
        self.update()

    def set_blue_glow(self, active):
        self.blue_glow_active = active
        self.update()

    def set_draw_check(self, draw):
        self.draw_check = draw
        self.update()

    def _update_pulse(self):
        self.pulse = (self.pulse + 0.06) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect()).adjusted(14, 14, -14, -14)
        thickness = 10.0
        
        # Consistent bounding box for both background and arc
        draw_rect = rect.adjusted(thickness/2, thickness/2, -thickness/2, -thickness/2)
        
        # Background Track
        bg_pen = QPen(QColor(255, 255, 255, 12) if theme_manager.current_theme == "dark" else QColor(0, 0, 0, 12), thickness)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawEllipse(draw_rect)
        
        # Draw Progress Arc
        if self.display_value > 0 or self.draw_check:
            val_pct = 100.0 if self.draw_check else self.display_value
            angle = (val_pct / 100.0) * 360.0
            
            # Simple soft single-stroke glow beneath the main arc (no concentric grid lines)
            glow_color = QColor(0, 180, 216) if self.blue_glow_active else QColor(theme_manager.get_color("accent"))
            glow_opacity = int(40 + 15 * math.sin(self.pulse))
            glow_color.setAlpha(max(0, min(255, glow_opacity)))
            glow_pen = QPen(glow_color, thickness + 4.0)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            painter.drawArc(draw_rect, 90 * 16, int(-angle * 16))
            
            # Main Arc
            main_color = QColor("#0077b6") if self.blue_glow_active else QColor(theme_manager.get_color("accent"))
            gradient = QLinearGradient(draw_rect.topLeft(), draw_rect.bottomRight())
            gradient.setColorAt(0, main_color)
            gradient.setColorAt(1, QColor("#00b4d8"))
            
            arc_pen = QPen(QBrush(gradient), thickness)
            arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(arc_pen)
            painter.drawArc(draw_rect, 90 * 16, int(-angle * 16))
            
        # Draw inside - standard percentage string only (checkmark inside tick fully removed as requested)
        painter.setPen(QPen(QColor(theme_manager.get_color("text_primary"))))
        font_size = int(self.width() * 0.14)
        painter.setFont(QFont("Inter", font_size, QFont.Weight.Bold))
        val_pct = 100 if self.draw_check else int(self.display_value)
        text = f"{val_pct}%"
        painter.drawText(draw_rect, Qt.AlignmentFlag.AlignCenter, text)

class AnimatedUSBScanner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 160)
        self.angle = 0.0
        self.wave_pos = 0.0
        self.wave_direction = 1
        self.pulse = 0.0
        self.particles = []
        self.scanning = False
        
        for _ in range(16):
            self.particles.append({
                'x': random.uniform(-65, 65),
                'y': random.uniform(-65, 65),
                'speed': random.uniform(0.6, 1.6),
                'size': random.uniform(1.5, 3.5),
                'angle': random.uniform(0, 2 * math.pi)
            })
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def set_scanning(self, active):
        self.scanning = active

    def update_animation(self):
        if self.scanning:
            self.angle = (self.angle + 1.8) % 360
            self.wave_pos += self.wave_direction * 0.025
            if self.wave_pos >= 1.0:
                self.wave_pos = 1.0
                self.wave_direction = -1
            elif self.wave_pos <= 0.0:
                self.wave_pos = 0.0
                self.wave_direction = 1
                
            for p in self.particles:
                p['x'] += math.cos(p['angle']) * p['speed']
                p['y'] += math.sin(p['angle']) * p['speed']
                if p['x']**2 + p['y']**2 > 75**2:
                    p['x'] = 0
                    p['y'] = 0
                    p['angle'] = random.uniform(0, 2 * math.pi)
        else:
            # Slowly decay rotation
            self.angle = (self.angle + 0.3) % 360
            
        self.pulse = (self.pulse + 0.05) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect())
        center = rect.center()
        cx, cy = center.x(), center.y()
        
        accent = QColor(theme_manager.get_color("accent"))
        
        # Ambient Pulse Glow
        glow_alpha = int(40 + 20 * math.sin(self.pulse))
        if self.scanning:
            glow_alpha = int(75 + 30 * math.sin(self.pulse * 1.5))
        glow_color = QColor(accent)
        glow_color.setAlpha(glow_alpha)
        
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 54.0, 54.0)
        
        # Draw central USB connector icon
        pen_color = QColor(theme_manager.get_color("text_primary"))
        painter.setPen(QPen(pen_color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Styling USB
        hx, hy = int(cx - 15), int(cy - 24)
        painter.drawRoundedRect(hx, hy, 30, 24, 4, 4)
        painter.drawRect(int(cx - 9), int(cy - 20), 5, 5)
        painter.drawRect(int(cx + 4), int(cy - 20), 5, 5)
        painter.drawRect(int(cx - 18), int(cy), 36, 14)
        painter.drawLine(int(cx), int(cy + 14), int(cx), int(cy + 32))
        
        # Rotating outer scanning ring
        ring_pen = QPen(accent, 1.5, Qt.PenStyle.DashLine)
        painter.setPen(ring_pen)
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle)
        painter.drawEllipse(QPointF(0, 0), 70.0, 70.0)
        painter.restore()
        
        if self.scanning:
            # Moving scan wave
            wave_y = cy - 35 + (self.wave_pos * 70)
            wave_grad = QLinearGradient(cx - 55, wave_y, cx + 55, wave_y)
            laser_color = QColor(accent)
            laser_color.setAlpha(190)
            transparent_color = QColor(accent)
            transparent_color.setAlpha(0)
            wave_grad.setColorAt(0, transparent_color)
            wave_grad.setColorAt(0.5, laser_color)
            wave_grad.setColorAt(1, transparent_color)
            
            laser_pen = QPen(QBrush(wave_grad), 3)
            painter.setPen(laser_pen)
            painter.drawLine(int(cx - 60), int(wave_y), int(cx + 60), int(wave_y))
            
            # Flowing particles
            painter.setPen(Qt.PenStyle.NoPen)
            for p in self.particles:
                part_color = QColor(accent)
                dist = math.sqrt(p['x']**2 + p['y']**2)
                alpha = int(240 * (1.0 - dist / 75.0))
                part_color.setAlpha(max(0, min(255, alpha)))
                painter.setBrush(QBrush(part_color))
                painter.drawEllipse(QPointF(cx + p['x'], cy + p['y']), p['size'], p['size'])

class DeviceInfoCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)
        
        lbl_title = QLabel("DEVICE INFORMATION")
        lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(lbl_title)
        
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        
        self.fields = {}
        field_names = [
            ("Device Name", "USB Mass Storage"),
            ("Manufacturer", "Kingston Technology"),
            ("Vendor ID", "0x0951"),
            ("Product ID", "0x1666"),
            ("Serial Number", "SN-928A-BD283"),
            ("USB Version", "USB 3.2 Gen 2"),
            ("Capacity", "64 GB"),
            ("File System", "exFAT"),
            ("Classification", "Secure Storage")
        ]
        
        for idx, (name, val) in enumerate(field_names):
            row = idx // 2
            col = (idx % 2) * 2
            
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'Inter'; font-weight: 500;")
            
            lbl_val = QLabel(val)
            lbl_val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 11px; font-family: 'JetBrains Mono'; font-weight: 600;")
            
            self.fields[name] = lbl_val
            
            self.grid.addWidget(lbl_name, row, col)
            self.grid.addWidget(lbl_val, row, col + 1)
            
        layout.addLayout(self.grid)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
    def fade_in(self):
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(500)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

    def update_field(self, name, val):
        if name in self.fields:
            self.fields[name].setText(val)

class InventoryCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)
        
        lbl_title = QLabel("FILE INVENTORY")
        lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(lbl_title)
        
        self.items = {}
        item_configs = [
            ("Files", 1250),
            ("Folders", 220),
            ("Executables", 15),
            ("Archives", 8),
            ("Hidden", 2)
        ]
        
        for name, target in item_configs:
            h_layout = QHBoxLayout()
            
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 12px; font-family: 'Inter';")
            
            lbl_count = QLabel("0")
            lbl_count.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 14px; font-family: 'JetBrains Mono'; font-weight: 700;")
            
            h_layout.addWidget(lbl_name)
            h_layout.addStretch()
            h_layout.addWidget(lbl_count)
            
            layout.addLayout(h_layout)
            self.items[name] = {
                'label': lbl_count,
                'target': target,
                'current': 0
            }
            
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
            
    def start_animation(self, duration=3000):
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(duration)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self._on_anim_update)
        self.anim.start()
        
    def _on_anim_update(self, progress):
        for name, data in self.items.items():
            val = int(data['target'] * progress)
            data['label'].setText(str(val))

class ThreatCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)
        
        self.lbl_title = QLabel("ENDPOINT THREAT REPORT")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        h_score_layout = QHBoxLayout()
        h_score_layout.setSpacing(16)
        h_score_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.risk_ring = CircularProgressRing()
        self.risk_ring.setFixedSize(90, 90)
        h_score_layout.addWidget(self.risk_ring)
        
        v_level_layout = QVBoxLayout()
        v_level_layout.setSpacing(4)
        v_level_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_level = QLabel("SAFE")
        self.lbl_level.setStyleSheet("color: #00e676; font-size: 18px; font-weight: 800; font-family: 'Inter';")
        self.lbl_recommendation = QLabel("No anomalies detected. Device signature matches trusted definitions.")
        self.lbl_recommendation.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'Inter';")
        self.lbl_recommendation.setWordWrap(True)
        
        v_level_layout.addWidget(self.lbl_level)
        v_level_layout.addWidget(self.lbl_recommendation)
        h_score_layout.addLayout(v_level_layout, 1)
        
        layout.addLayout(h_score_layout)
        
        # Malware detection area (hidden by default)
        self.malware_widget = QWidget()
        malware_layout = QVBoxLayout(self.malware_widget)
        malware_layout.setContentsMargins(12, 12, 12, 12)
        malware_layout.setSpacing(6)
        self.malware_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255, 23, 68, 15);
                border: 1px solid rgba(255, 23, 68, 30);
                border-radius: 8px;
            }}
        """)
        
        self.lbl_malware_title = QLabel("DETECTION TRACE:")
        self.lbl_malware_title.setStyleSheet("color: #ff1744; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_malware_name = QLabel("Threat Name: Trojan.Generic")
        self.lbl_malware_name.setStyleSheet("color: #ffffff; font-size: 11px; font-family: 'JetBrains Mono'; font-weight: 700;")
        self.lbl_malware_location = QLabel("Location: E:\\Downloads\\setup.exe")
        self.lbl_malware_location.setStyleSheet("color: #a1a1aa; font-size: 11px; font-family: 'JetBrains Mono';")
        self.lbl_malware_location.setWordWrap(True)
        
        malware_layout.addWidget(self.lbl_malware_title)
        malware_layout.addWidget(self.lbl_malware_name)
        malware_layout.addWidget(self.lbl_malware_location)
        
        layout.addWidget(self.malware_widget)
        self.malware_widget.hide()
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
    def update_threat_report(self, score, level, rec, malware_name=None, malware_loc=None):
        self.risk_ring.setValue(score)
        self.lbl_level.setText(level)
        self.lbl_recommendation.setText(rec)
        
        if level == "SAFE":
            self.lbl_level.setStyleSheet("color: #00e676; font-size: 18px; font-weight: 800; font-family: 'Inter';")
            self.malware_widget.hide()
        elif level == "LOW":
            self.lbl_level.setStyleSheet("color: #ffeb3b; font-size: 18px; font-weight: 800; font-family: 'Inter';")
            self.malware_widget.hide()
        elif level == "MEDIUM":
            self.lbl_level.setStyleSheet("color: #ff9800; font-size: 18px; font-weight: 800; font-family: 'Inter';")
            self.malware_widget.hide()
        else: # HIGH / CRITICAL
            self.lbl_level.setStyleSheet("color: #ff1744; font-size: 18px; font-weight: 800; font-family: 'Inter';")
            if malware_name and malware_loc:
                self.lbl_malware_name.setText(f"Threat Name: {malware_name}")
                self.lbl_malware_location.setText(f"Location: {malware_loc}")
                self.malware_widget.show()

class WarningCard(QWidget):
    def __init__(self, title, description, risk_level="MEDIUM", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        color_map = {
            "SAFE": "#00e676",
            "LOW": "#ffeb3b",
            "MEDIUM": "#ff9800",
            "HIGH": "#ff1744"
        }
        color = color_map.get(risk_level, "#ff9800")
        
        bg_color = "rgba(0, 0, 0, 40)" if theme_manager.current_theme == 'dark' else "rgba(255, 255, 255, 120)"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid {color}55;
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        
        self.lbl_icon = QLabel("⚠")
        self.lbl_icon.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 900;")
        layout.addWidget(self.lbl_icon)
        
        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 11px; font-weight: 800; font-family: 'Inter';")
        
        lbl_desc = QLabel(description)
        lbl_desc.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-family: 'Inter';")
        lbl_desc.setWordWrap(True)
        
        v_layout.addWidget(lbl_title)
        v_layout.addWidget(lbl_desc)
        
        layout.addLayout(v_layout, 1)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

class ScanStatsCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(16)
        
        self.threats_block = QVBoxLayout()
        self.threats_block.setSpacing(2)
        lbl_threat_title = QLabel("THREATS DETECTED")
        lbl_threat_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        self.lbl_threat_val = QLabel("0")
        self.lbl_threat_val.setStyleSheet("color: #00e676; font-size: 24px; font-weight: 800; font-family: 'JetBrains Mono';")
        self.threats_block.addWidget(lbl_threat_title)
        self.threats_block.addWidget(self.lbl_threat_val)
        layout.addLayout(self.threats_block)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"background-color: {theme_manager.get_color('glass_border')}; width: 1px;")
        layout.addWidget(sep)
        
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(10)
        
        lbl_elapsed_title = QLabel("ELAPSED")
        lbl_elapsed_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-family: 'Inter'; font-weight: 700;")
        self.lbl_elapsed_val = QLabel("00:00")
        self.lbl_elapsed_val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 13px; font-family: 'JetBrains Mono'; font-weight: 700;")
        
        lbl_remaining_title = QLabel("REMAINING")
        lbl_remaining_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-family: 'Inter'; font-weight: 700;")
        self.lbl_remaining_val = QLabel("00:00")
        self.lbl_remaining_val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 13px; font-family: 'JetBrains Mono'; font-weight: 700;")
        
        lbl_speed_title = QLabel("SPEED")
        lbl_speed_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-family: 'Inter'; font-weight: 700;")
        self.lbl_speed_val = QLabel("0 MB/s")
        self.lbl_speed_val.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 13px; font-family: 'JetBrains Mono'; font-weight: 700;")
        
        self.stats_grid.addWidget(lbl_elapsed_title, 0, 0)
        self.stats_grid.addWidget(self.lbl_elapsed_val, 1, 0)
        self.stats_grid.addWidget(lbl_remaining_title, 0, 1)
        self.stats_grid.addWidget(self.lbl_remaining_val, 1, 1)
        self.stats_grid.addWidget(lbl_speed_title, 0, 2)
        self.stats_grid.addWidget(self.lbl_speed_val, 1, 2)
        
        layout.addLayout(self.stats_grid, 1)
        
    def set_threats(self, count):
        self.lbl_threat_val.setText(str(count))
        if count > 0:
            self.lbl_threat_val.setStyleSheet("color: #ff1744; font-size: 24px; font-weight: 800; font-family: 'JetBrains Mono';")
            self.pulse_anim = QVariantAnimation(self)
            self.pulse_anim.setDuration(300)
            self.pulse_anim.setStartValue(1.0)
            self.pulse_anim.setEndValue(1.3)
            self.pulse_anim.valueChanged.connect(self._on_pulse_threat)
            self.pulse_anim.start()
        else:
            self.lbl_threat_val.setStyleSheet("color: #00e676; font-size: 24px; font-weight: 800; font-family: 'JetBrains Mono';")
            
    def _on_pulse_threat(self, scale):
        font = QFont("JetBrains Mono", int(18 * scale), QFont.Weight.Bold)
        self.lbl_threat_val.setFont(font)
        
    def update_stats(self, elapsed_sec, remaining_sec, speed_mbs):
        m_el, s_el = divmod(int(elapsed_sec), 60)
        m_rem, s_rem = divmod(int(remaining_sec), 60)
        
        self.lbl_elapsed_val.setText(f"{m_el:02d}:{s_el:02d}")
        self.lbl_remaining_val.setText(f"{m_rem:02d}:{s_rem:02d}" if remaining_sec > 0 else "00:00")
        self.lbl_speed_val.setText(f"{speed_mbs} MB/s")

class LogCard(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        bg_color = "rgba(255, 255, 255, 15)" if theme_manager.current_theme == 'dark' else "rgba(0, 0, 0, 8)"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: none;
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        
        # Icon
        self.icon_widget = GreenCheckIcon()
        layout.addWidget(self.icon_widget)
        
        # Message
        self.lbl_message = QLabel(message)
        self.lbl_message.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 11px; font-family: 'JetBrains Mono'; border: none; background: transparent;")
        self.lbl_message.setWordWrap(True)
        layout.addWidget(self.lbl_message, 1)
        
        # Timestamp
        self.lbl_time = QLabel(QDateTime.currentDateTime().toString("hh:mm:ss"))
        self.lbl_time.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-family: 'JetBrains Mono'; border: none; background: transparent;")
        layout.addWidget(self.lbl_time)
        
        # Fade-in Animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(400)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

class LogContainerCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(12)
        
        self.lbl_title = QLabel("SCAN LOG TRACE")
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(self.lbl_title)
        
        self.logs_scroll = QScrollArea()
        self.logs_scroll.setWidgetResizable(True)
        self.logs_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.logs_scroll.setStyleSheet("background: transparent; border: none;")
        
        self.logs_content = QWidget()
        self.logs_content.setStyleSheet("background: transparent;")
        self.logs_layout = QVBoxLayout(self.logs_content)
        self.logs_layout.setContentsMargins(0, 0, 0, 0)
        self.logs_layout.setSpacing(6)
        self.logs_layout.addStretch()
        self.logs_scroll.setWidget(self.logs_content)
        
        # ScrollBar styling
        self.logs_scroll.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(128, 128, 128, 40);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(128, 128, 128, 70);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        layout.addWidget(self.logs_scroll)
        
    def update_styles(self):
        self.lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")

class ActivityCard(GlassCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(10)
        
        lbl_title = QLabel("ACTIVITY TIMELINE")
        lbl_title.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 10px; font-weight: 800; font-family: 'Inter'; letter-spacing: 0.8px;")
        layout.addWidget(lbl_title)
        
        self.stages = [
            "Reading Device",
            "Checking Firmware",
            "Inspecting Archives",
            "Hidden File Detection",
            "Autorun Detection",
            "Malware Scan",
            "Risk Score Calculation"
        ]
        
        self.items = []
        for stage in self.stages:
            h_layout = QHBoxLayout()
            h_layout.setSpacing(10)
            
            lbl_dot = QLabel("●")
            lbl_dot.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 12px;")
            
            lbl_name = QLabel(stage)
            lbl_name.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'Inter'; font-weight: 500;")
            
            h_layout.addWidget(lbl_dot)
            h_layout.addWidget(lbl_name)
            h_layout.addStretch()
            
            layout.addLayout(h_layout)
            self.items.append({
                'dot': lbl_dot,
                'name': lbl_name,
                'status': 'pending' # pending, scanning, completed
            })
            
    def set_stage_status(self, stage_idx, status):
        if stage_idx < 0 or stage_idx >= len(self.items):
            return
            
        item = self.items[stage_idx]
        item['status'] = status
        
        accent = theme_manager.get_color("accent")
        if status == 'completed':
            item['dot'].setText("✔")
            item['dot'].setStyleSheet("color: #00e676; font-size: 11px; font-weight: 900;")
            item['name'].setStyleSheet("color: #00e676; font-size: 11px; font-family: 'Inter'; font-weight: 600;")
        elif status == 'scanning':
            item['dot'].setText("●")
            item['dot'].setStyleSheet(f"color: {accent}; font-size: 12px;")
            item['name'].setStyleSheet(f"color: {accent}; font-size: 11px; font-family: 'Inter'; font-weight: 700;")
        else: # pending
            item['dot'].setText("●")
            item['dot'].setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 12px;")
            item['name'].setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'Inter'; font-weight: 500;")

    def reset(self):
        for idx in range(len(self.items)):
            self.set_stage_status(idx, 'pending')

class SuspiciousFilePopup(QWidget):
    action_taken = pyqtSignal(str) # 'keep' or 'isolate'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("suspiciousPopup")
        if parent:
            self.resize(parent.size())
            parent.installEventFilter(self)
            
        self.card = GlassCard(self)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(32, 32, 32, 32)
        self.card_layout.setSpacing(16)
        
        lbl_title = QLabel("SUSPICIOUS FILE DETECTED")
        lbl_title.setStyleSheet("color: #ff1744; font-size: 13px; font-weight: 900; font-family: 'Inter'; letter-spacing: 1.5px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(lbl_title)
        
        self.lbl_filename = QLabel("File: invoice.pdf.exe")
        self.lbl_filename.setStyleSheet(f"color: {theme_manager.get_color('text_primary')}; font-size: 14px; font-weight: 700; font-family: 'Inter';")
        self.lbl_filename.setWordWrap(True)
        self.card_layout.addWidget(self.lbl_filename)
        
        self.lbl_filepath = QLabel("Path: E:\\invoice.pdf.exe")
        self.lbl_filepath.setStyleSheet(f"color: {theme_manager.get_color('text_secondary')}; font-size: 11px; font-family: 'JetBrains Mono';")
        self.lbl_filepath.setWordWrap(True)
        self.card_layout.addWidget(self.lbl_filepath)
        
        self.lbl_reason = QLabel("Reason: Double extension detected (pdf.exe). High likelihood of masquerading malware.")
        self.lbl_reason.setStyleSheet("color: #ff9800; font-size: 11px; font-family: 'Inter'; font-weight: 600;")
        self.lbl_reason.setWordWrap(True)
        self.card_layout.addWidget(self.lbl_reason)
        
        h_btn = QHBoxLayout()
        h_btn.setSpacing(12)
        
        self.btn_keep = QPushButton("KEEP")
        self.btn_isolate = QPushButton("ISOLATE")
        
        h_btn.addWidget(self.btn_keep)
        h_btn.addWidget(self.btn_isolate)
        self.card_layout.addLayout(h_btn)
        
        self.btn_keep.clicked.connect(self._on_keep)
        self.btn_isolate.clicked.connect(self._on_isolate)
        
        self.setStyleSheet_custom()
        theme_manager.theme_changed.connect(self.setStyleSheet_custom)
        
        self.hide()
        
    def setStyleSheet_custom(self):
        self.btn_keep.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('btn_bg')};
                color: {theme_manager.get_color('text_primary')};
                border: 1px solid {theme_manager.get_color('glass_border')};
                border-radius: 18px;
                padding: 10px 20px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('btn_hover')};
            }}
        """)
        self.btn_isolate.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff1744aa, stop:1 #ff174477);
                color: #ffffff;
                border: 1px solid rgba(255, 23, 68, 50);
                border-radius: 18px;
                padding: 10px 20px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff1744, stop:1 #ff1744cc);
            }}
        """)
        
    def show_popup(self, filename, filepath, reason):
        self.lbl_filename.setText(f"File: {filename}")
        self.lbl_filepath.setText(f"Path: {filepath}")
        self.lbl_reason.setText(f"Reason: {reason}")
        self.show()
        self.raise_()
        self._reposition()
        
    def _reposition(self):
        if self.parent():
            self.resize(self.parent().size())
            card_width, card_height = 360, 260
            self.card.setGeometry(
                int((self.width() - card_width) / 2),
                int((self.height() - card_height) / 2),
                card_width,
                card_height
            )
            
    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == event.Type.Resize:
            self._reposition()
        return super().eventFilter(obj, event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
    def _on_keep(self):
        self.action_taken.emit("keep")
        self.hide()
        
    def _on_isolate(self):
        self.action_taken.emit("isolate")
        self.hide()
