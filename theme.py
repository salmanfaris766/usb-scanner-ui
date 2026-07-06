from PyQt6.QtCore import QObject, pyqtSignal

COLORS_DARK = {
    'bg': '#050505',
    'glass_bg': 'rgba(13, 13, 13, 160)',
    'glass_border': 'rgba(255, 255, 255, 20)',
    'accent': '#00e5ff',
    'text_primary': '#ffffff',
    'text_secondary': '#a1a1aa',
    'btn_bg': 'rgba(255, 255, 255, 12)',
    'btn_hover': 'rgba(0, 229, 255, 45)',
}

COLORS_LIGHT = {
    'bg': '#f5f5f7',
    'glass_bg': 'rgba(255, 255, 255, 180)',
    'glass_border': 'rgba(0, 0, 0, 15)',
    'accent': '#00e5ff',
    'text_primary': '#1d1d1f',
    'text_secondary': '#86868b',
    'btn_bg': 'rgba(0, 0, 0, 8)',
    'btn_hover': 'rgba(0, 229, 255, 30)',
}

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_theme = "dark"

    def get_color(self, name):
        colors = COLORS_DARK if self.current_theme == "dark" else COLORS_LIGHT
        return colors.get(name, '#ffffff')

    def set_theme(self, theme_name):
        if theme_name in ["dark", "light"] and self.current_theme != theme_name:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)

    @property
    def colors(self):
        return COLORS_DARK if self.current_theme == "dark" else COLORS_LIGHT

theme_manager = ThemeManager()
