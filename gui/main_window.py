# main_window.py
import dearpygui.dearpygui as dpg
from const import FONTS, UI_CONF
from .focus_manager import FocusManager
from .tabs import IPTab, RouteTab

class MainWindow:
    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.conf = UI_CONF()
        self.focus_manager = FocusManager()
        self.tabs = {}          # словарь {tab_id: tab_object}
        self.active_tab_tag = None

        self._setup_dpg()
        self._create_fonts()
        self._create_window()
        self._create_tabs()
        self._register_handlers()

    def _setup_dpg(self):
        dpg.create_context()
        # Глобальная тема (скругления)
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.bind_theme(global_theme)

    def _create_fonts(self):
        with dpg.font_registry():
            with dpg.font(FONTS.FONT_TAHOMA, 20, default_font=True, id="Default font"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_chars([0x25b2, 0x25bc, 0x00d7])
            self.bigger_font = dpg.add_font(FONTS.FONT_TAHOMA, 26)
            self.smaller_font = dpg.add_font(FONTS.FONT_TAHOMA, 14)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=self.bigger_font)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=self.smaller_font)
            dpg.add_font_chars([0x25b2, 0x25bc, 0x00d7], parent=self.smaller_font)
        dpg.bind_font("Default font")

    def _create_window(self):
        with dpg.window(label="", tag="main_window",
                        width=self.conf.main_width, height=self.conf.main_height):
            # Таб-бар
            self.tab_bar = dpg.add_tab_bar(tag="main_tab_bar")

    def _create_tabs(self):
        # Вкладка IP
        with dpg.tab(label="IP", parent=self.tab_bar, tag="ip_tab"):
            ip_tab = IPTab(self.model, self.controller, self.focus_manager, "ip_tab")
            ip_tab.build()
            self.tabs["ip_tab"] = ip_tab

        # Вкладка Route
        with dpg.tab(label="Route", parent=self.tab_bar, tag="route_tab"):
            route_tab = RouteTab(self.model, self.controller, self.focus_manager, "route_tab")
            route_tab.build()
            self.tabs["route_tab"] = route_tab

        # Устанавливаем начальную активную вкладку
        self.active_tab_tag = "ip_tab"
        dpg.set_value("main_tab_bar", "ip_tab")

        # Добавляем всплывающую подсказку (знак вопроса) – вынесем в IPTab или оставим здесь?
        # В текущем дизайне подсказка относится к вкладке IP, поэтому перенесём её в IPTab.build()
        # Для простоты оставим здесь, но лучше перенести в IPTab.
        # (Код подсказки из gui.py можно добавить в IPTab.build)

    def _register_handlers(self):
        # Регистрация обработчика клавиш
        with dpg.handler_registry():
            dpg.add_key_press_handler(callback=self._key_press_callback)

        # Регистрация обработчика ресайза
        with dpg.item_handler_registry(tag="resize_handler"):
            dpg.add_item_resize_handler(callback=self._resize_callback)
        dpg.bind_item_handler_registry("main_window", "resize_handler")

    def _key_press_callback(self, sender, key):
        # Определяем активную вкладку
        active_tab_tag = dpg.get_value("main_tab_bar")
        if isinstance(active_tab_tag, int):
            active_tab_tag = dpg.get_item_alias(active_tab_tag)

        tab = self.tabs.get(active_tab_tag)
        if tab:
            
            tab.handle_key(key)

    def _resize_callback(self, sender, app_data):
        width = dpg.get_item_width("main_window")
        height = dpg.get_item_height("main_window")
        for tab in self.tabs.values():
            tab.on_resize(width, height)

    def update_display(self):
        """Вызывается из главного цикла при поступлении новых данных"""
        for tab in self.tabs.values():
            tab.update_display()

    def show(self):
        dpg.create_viewport(
            title="IPtool",
            height=self.conf.main_height,
            width=self.conf.main_width,
            resizable=True,
            min_width=self.conf.main_min_width,
            min_height=self.conf.main_min_height,
            max_height=self.conf.main_max_height
        )
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()

    def clean_up(self):
        dpg.destroy_context()