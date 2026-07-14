# route_tab.py
import dearpygui.dearpygui as dpg
from .base_tab import BaseTab

class RouteTab(BaseTab):
    def __init__(self, model, controller, focus_manager, parent_tag):
        super().__init__(model, controller, focus_manager, parent_tag)
        self.table_tag = "route_table"

    def build(self):
        with dpg.group(parent=self.parent_tag):
            # Кнопка ручного обновления (опционально)
            #dpg.add_button(label="Обновить маршруты", callback=self._manual_refresh)
            #dpg.add_spacer(height=10)
            # Таблица для маршрутов
            with dpg.table(tag=self.table_tag, header_row=True, resizable=True, 
                           policy=dpg.mvTable_SizingStretchProp, 
                           borders_outerV=True, borders_innerV=True, 
                           borders_outerH=True, borders_innerH=True):
                dpg.add_table_column(label="Сеть назначения")
                dpg.add_table_column(label="Маска")
                dpg.add_table_column(label="Шлюз")
                dpg.add_table_column(label="Интерфейс")
                dpg.add_table_column(label="Метрика")
            # Можно добавить placeholder
            self._update_table([])

    def _manual_refresh(self):
        """Принудительно обновить маршруты (вызовет опрос)"""
        # Можно вызвать метод контроллера или просто обновить из модели
        self.update_display()

    def update_display(self):
        """Обновляет таблицу маршрутов из модели"""
        routes = self.model.routes if hasattr(self.model, 'routes') else []
        self._update_table(routes)

    def _update_table(self, routes: list):
        """Очищает таблицу и заполняет новыми данными"""
        # Удаляем все строки, кроме заголовков (они находятся в слоте 1)
        # В DPG строки таблицы добавляются как дочерние элементы таблицы в слоте 1
        if dpg.does_item_exist(self.table_tag):
            # Удаляем все дочерние элементы (строки)
            for child in dpg.get_item_children(self.table_tag, slot=1):
                dpg.delete_item(child)

        # Добавляем строки
        for r in routes:
            with dpg.table_row(parent=self.table_tag):
                dpg.add_selectable(label = r.destination, span_columns= True,default_value= False)
                dpg.add_text(r.mask)
                dpg.add_text(r.gateway)
                dpg.add_text(r.interface)
                dpg.add_text(r.metric)

    def on_resize(self, width, height):
        # При ресайзе можно адаптировать ширину колонок, если нужно
        pass

    def handle_key(self, key):
        return False