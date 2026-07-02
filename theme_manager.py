import json
import os
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

DARK_COLORS = {
    "bg": "#050505",
    "surface": "#0D0D0D",
    "accent": "#00E5FF",
    "success": "#22C55E",
    "warning": "#FACC15",
    "danger": "#FF4D4D",
    "text_primary": "#FFFFFF",
    "text_secondary": "rgba(255, 255, 255, 180)",
    "glass_bg": "rgba(30, 30, 30, 220)", 
    "glass_border": "rgba(255, 255, 255, 20)",
    "btn_bg": "rgba(255, 255, 255, 15)",
    "btn_hover": "rgba(0, 229, 255, 40)"
}

LIGHT_COLORS = {
    "bg": "#F5F5F7",
    "surface": "#FFFFFF",
    "accent": "#0097A7",            # Deeper teal — reads cleanly on white
    "success": "#16A34A",           # Muted emerald — softer than neon green
    "warning": "#D97706",           # Warm amber — legible on light surfaces
    "danger": "#DC2626",            # Rich crimson — visible without being neon
    "text_primary": "#1C1C1E",      # Apple-style soft slate
    "text_secondary": "rgba(60, 60, 67, 140)",
    "glass_bg": "rgba(255, 255, 255, 200)",       # Frosted white glass
    "glass_border": "rgba(0, 0, 0, 8)",           # Near-invisible border
    "btn_bg": "rgba(0, 150, 167, 8)",             # Tinted with accent for cohesion
    "btn_hover": "rgba(0, 151, 167, 25)"          # Soft teal tint on hover
}

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config_path = "config.json"
        self.current_theme = "dark"
        self._colors = dict(DARK_COLORS)
        self.load_theme()

    def load_theme(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "dark")
            except Exception:
                pass
        self._apply_colors_dict()

    def save_theme(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception:
            pass

    def _apply_colors_dict(self):
        source = LIGHT_COLORS if self.current_theme == "light" else DARK_COLORS
        # Update the mutable dictionary so any future inline usages pick up the new colors
        for k, v in source.items():
            self._colors[k] = v

    def set_theme(self, theme_name):
        if theme_name not in ["light", "dark"] or theme_name == self.current_theme:
            return
        old_theme = self.current_theme
        self.current_theme = theme_name
        self._apply_colors_dict()
        self.save_theme()
        
        # We need to traverse all widgets and update stylesheets 
        # by doing string replacement on the evaluated f-strings.
        self._update_all_stylesheets(old_theme, theme_name)
        self.theme_changed.emit(theme_name)

    def _update_all_stylesheets(self, old_theme, new_theme):
        app = QApplication.instance()
        if not app:
            return
        
        old_dict = DARK_COLORS if old_theme == "dark" else LIGHT_COLORS
        new_dict = LIGHT_COLORS if new_theme == "light" else DARK_COLORS

        # To avoid replacing substrings accidentally (e.g. #000 matching inside #000000)
        # We can sort the keys by length descending if needed, but these are distinct enough.
        # We also need to map "white" and "black" explicitly if they are hardcoded in stylesheets
        extra_mappings = []
        if old_theme == "dark":
            extra_mappings = [("color: white", f"color: {new_dict['text_primary']}")]
        else:
            extra_mappings = [("color: black", f"color: {new_dict['text_primary']}"), 
                              (f"color: {old_dict['text_primary']}", "color: white")]

        def replace_colors(style):
            if not style:
                return style
            new_style = style
            # Apply strict dict mappings first
            for k in old_dict:
                new_style = new_style.replace(old_dict[k], new_dict[k])
            
            # Apply extra edge case mappings
            for old_val, new_val in extra_mappings:
                new_style = new_style.replace(old_val, new_val)
                
            return new_style

        # Recursively update stylesheets on all widgets
        for widget in app.allWidgets():
            style = widget.styleSheet()
            if style:
                updated = replace_colors(style)
                if updated != style:
                    widget.setStyleSheet(updated)
            
            # Repaint forcefully if the widget has a custom paint event
            widget.update()

    def get_color(self, key):
        return self._colors.get(key, "#000000")

# Global singleton
theme_manager = ThemeManager()
COLORS = theme_manager._colors
