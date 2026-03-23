# route_tab.py
import dearpygui.dearpygui as dpg
from .base_tab import BaseTab

class RouteTab(BaseTab):
    def build(self):
        """Заглушка для вкладки маршрутов"""
        with dpg.group(parent=self.parent_tag):
            dpg.add_text("Маршруты (в разработке)")

    def update_display(self):
        pass

    def handle_key(self, key):
        return False