import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt, QDateTime, QPointF
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QLinearGradient, QPixmap, QBrush
from theme import theme_manager
from navigation import BottomNavigationBar
from dashboard import DashboardPage
from scan_page import ScanPage
from history import HistoryPage
from settings import SettingsPage

class PremiumBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("premiumBackgroundWidget")
        
        # Build noise pixmap for highly performant, CPU-friendly grain tiling on Raspberry Pi
        self._noise_pixmap = QPixmap(128, 128)
        self._noise_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(self._noise_pixmap)
        for x in range(128):
            for y in range(128):
                # Subtle grain dots
                alpha = random.randint(4, 9)
                painter.setPen(QColor(255, 255, 255, alpha))
                painter.drawPoint(x, y)
        painter.end()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        is_dark = (theme_manager.current_theme == "dark")
        
        if is_dark:
            # Base dark graphite layer
            painter.fillRect(self.rect(), QColor("#0B1118"))
            
            # Subtle deep blue linear gradient
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#111A24"))
            grad.setColorAt(1.0, QColor("#0B1118"))
            painter.fillRect(self.rect(), QBrush(grad))
            
            # Soft cybernetic radial cyan glow behind main contents
            radial = QRadialGradient(w / 2.0, h / 2.2, max(w, h) * 0.7)
            radial.setColorAt(0.0, QColor(0, 229, 255, 22))
            radial.setColorAt(0.4, QColor(0, 180, 216, 6))
            radial.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), QBrush(radial))
        else:
            # Base light grey layer
            painter.fillRect(self.rect(), QColor("#f5f5f7"))
            
            # Soft blue-ish linear gradient
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#e8edf5"))
            grad.setColorAt(1.0, QColor("#f5f5f7"))
            painter.fillRect(self.rect(), QBrush(grad))
            
            # Soft radial light-blue glow
            radial = QRadialGradient(w / 2.0, h / 2.2, max(w, h) * 0.7)
            radial.setColorAt(0.0, QColor(0, 180, 216, 12))
            radial.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), QBrush(radial))
            
        # Draw tiled noise grain texture
        painter.save()
        painter.setOpacity(0.35 if is_dark else 0.2)
        brush = QBrush(self._noise_pixmap)
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        painter.restore()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USB Security Detector && Terminal Sandbox")
        self.resize(800, 600)
        
        # Central Widget & Main Layout
        self.central_widget = PremiumBackgroundWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)
        
        # Pages Stack
        self.pages_stack = QStackedWidget()
        
        self.page_dashboard = DashboardPage()
        self.page_scan = ScanPage()
        self.page_history = HistoryPage()
        self.page_settings = SettingsPage()
        
        self.pages_stack.addWidget(self.page_dashboard)
        self.pages_stack.addWidget(self.page_scan)
        self.pages_stack.addWidget(self.page_history)
        self.pages_stack.addWidget(self.page_settings)
        
        # Bottom Navigation
        self.nav_bar = BottomNavigationBar()
        
        # Center the navigation bar inside a layout with flexible spacers
        self.nav_container_layout = QHBoxLayout()
        self.nav_container_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_container_layout.addStretch(1)
        self.nav_container_layout.addWidget(self.nav_bar)
        self.nav_container_layout.addStretch(1)
        
        self.main_layout.addWidget(self.pages_stack, 1)
        self.main_layout.addLayout(self.nav_container_layout)
        
        # Connect navigation switching with transition animation
        self.nav_bar.tab_changed.connect(self.switch_page)
        
        # Connect functional bridges between pages
        self.page_dashboard.device_authorized.connect(self.log_device_authorized)
        self.page_dashboard.device_blocked.connect(self.log_device_blocked)
        self.page_scan.scan_completed.connect(self.page_dashboard.on_scan_completed)
        
        self.update_theme_styles()
        theme_manager.theme_changed.connect(self.update_theme_styles)

    def switch_page(self, idx):
        target_page = self.pages_stack.widget(idx)
        self.pages_stack.setCurrentIndex(idx)
        
        try:
            from animations import setup_fade_in_animation
            # Trigger standard smooth fade-in entrance transition
            self._fade_anim, self._opacity_effect = setup_fade_in_animation(target_page, 250)
            self._fade_anim.finished.connect(lambda: target_page.setGraphicsEffect(None))
            self._fade_anim.start()
        except (ImportError, ModuleNotFoundError):
            # Fallback if animations.py is not available in the user's workspace
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            
            opacity_effect = QGraphicsOpacityEffect(target_page)
            target_page.setGraphicsEffect(opacity_effect)
            
            self._fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
            self._fade_anim.setDuration(250)
            self._fade_anim.setStartValue(0.0)
            self._fade_anim.setEndValue(1.0)
            self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self._opacity_effect = opacity_effect
            self._fade_anim.finished.connect(lambda: target_page.setGraphicsEffect(None))
            self._fade_anim.start()

    def log_device_authorized(self, device):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.page_history.add_log_entry(device, timestamp, "ALLOWED")

    def log_device_blocked(self, device):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.page_history.add_log_entry(device, timestamp, "BLOCKED")

    def update_theme_styles(self):
        # Trigger repaint on our custom background widget when theme changes
        self.central_widget.update()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
