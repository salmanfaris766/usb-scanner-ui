from PyQt6.QtCore import QObject, pyqtSignal

COLORS_DARK = {
    'bg': '#0B1118',
    'glass_bg': 'rgba(20, 30, 42, 22)',
    'glass_border': 'rgba(0, 229, 255, 38)',
    'accent': '#00e5ff',
    'text_primary': '#ffffff',
    'text_secondary': '#8898a6',
    'btn_bg': 'rgba(255, 255, 255, 12)',
    'btn_hover': 'rgba(0, 229, 255, 45)',
}

COLORS_LIGHT = {
    'bg': '#f5f5f7',
    'glass_bg': 'rgba(255, 255, 255, 180)',
    'glass_border': 'rgba(0, 180, 216, 25)',
    'accent': '#00b4d8',
    'text_primary': '#1d1d1f',
    'text_secondary': '#86868b',
    'btn_bg': 'rgba(0, 0, 0, 8)',
    'btn_hover': 'rgba(0, 180, 216, 30)',
}

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_theme = "dark"

    def get_color(self, name):
        colors = COLORS_DARK if self.current_theme == "dark" else COLORS_LIGHT
        return colors.get(name, '#ffffff')

    def get_qcolor(self, name):
        from PyQt6.QtGui import QColor
        color_str = self.get_color(name).strip()
        if color_str.startswith("rgba(") and color_str.endswith(")"):
            parts = color_str[5:-1].split(",")
            if len(parts) == 4:
                try:
                    r = int(parts[0].strip())
                    g = int(parts[1].strip())
                    b = int(parts[2].strip())
                    a = int(parts[3].strip())
                    return QColor(r, g, b, a)
                except ValueError:
                    pass
        elif color_str.startswith("rgb(") and color_str.endswith(")"):
            parts = color_str[4:-1].split(",")
            if len(parts) == 3:
                try:
                    r = int(parts[0].strip())
                    g = int(parts[1].strip())
                    b = int(parts[2].strip())
                    return QColor(r, g, b)
                except ValueError:
                    pass
        qc = QColor(color_str)
        if qc.isValid():
            return qc
        return QColor(0, 0, 0, 0)

    def set_theme(self, theme_name):
        if theme_name in ["dark", "light"] and self.current_theme != theme_name:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)

    @property
    def colors(self):
        return COLORS_DARK if self.current_theme == "dark" else COLORS_LIGHT

theme_manager = ThemeManager()
