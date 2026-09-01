import dearpygui.dearpygui as dpg
from .base_tab import BaseTab

class RouteTab(BaseTab):
    def __init__(self, model, controller, focus_manager, parent_tag, font=None):
        super().__init__(model, controller, focus_manager, parent_tag, font)
        self.table_tag = "route_table"
        self.popup_tag = "route_popup"
        self.button_refresh_tag = "btn_refresh"   # пример дополнительного элемента
        self.selected_row = -1
        self.row_selectables = []
        self.current_routes = []
        self.popup_option = ["Изменить маршрут","Удалить маршрут","Добавить маршрут"]

    def build(self):
        with dpg.group(parent=self.parent_tag):
            # Кнопка обновления (для демонстрации переключения фокуса)
            #dpg.add_button(label="Обновить маршруты",tag=self.button_refresh_tag,callback=self._manual_refresh)
            #dpg.add_spacer(height=10)

            # Таблица
            with dpg.table(tag=self.table_tag, header_row=True, resizable=True,
                           policy=dpg.mvTable_SizingStretchProp,
                           borders_outerV=True, borders_innerV=True,
                           borders_outerH=True, borders_innerH=True):
                dpg.add_table_column(label="Сеть назначения")
                dpg.add_table_column(label="Маска")
                dpg.add_table_column(label="Шлюз")
                dpg.add_table_column(label="Интерфейс")
                dpg.add_table_column(label="Метрика")
                dpg.bind_item_font(self.table_tag, self.font)

            # Popup (контекстное меню)
            with dpg.popup(self.parent_tag, tag=self.popup_tag):
                dpg.add_menu_item(label="Изменить маршрут", tag="popup_menu_item1",callback=self._edit_route)
                dpg.add_menu_item(label="Удалить маршрут", tag="popup_menu_item2",callback=self._delete_route)
                dpg.add_menu_item(label="Добавить маршрут", tag="popup_menu_item3",callback=self._add_route)
                dpg.add_menu_item(label="a", tag="popup_menu_item4")
            dpg.configure_item(self.popup_tag, show=False)  # скрыть по умолчанию

        # Регистрация элементов в FocusManager
        # Создаём фиктивные темы (таблица не меняет цвет, но для единообразия)
        active_theme = self._create_dummy_theme()
        inactive_theme = self._create_dummy_theme()
        self.focus_manager.register_element(self.table_tag, active_theme, inactive_theme, position=0)
        #self.focus_manager.register_element(self.button_refresh_tag, active_theme, inactive_theme, position=1)
        # Устанавливаем начальный фокус на таблицу
        self.focus_manager.set_focus(self.table_tag)

        self._update_table([])

    def _create_dummy_theme(self):
        """Создаёт пустую тему, чтобы FocusManager мог работать (темы не применяются)"""
        with dpg.theme() as theme:
            pass
        return theme

    def _manual_refresh(self):
        """Принудительное обновление маршрутов (вызывается по кнопке или по Enter)"""
        self.update_display()
        print("Маршруты обновлены")

    def update_display(self):
        routes = self.model.routes if hasattr(self.model, 'routes') else []
        self._update_table(routes)

    def set_initial_focus(self):
        # Устанавливаем фокус на таблицу (если она зарегистрирована в FocusManager)
        if dpg.does_item_exist(self.table_tag):
            self.focus_manager.set_focus(self.table_tag)
            #print("фокус на маршрутах")

    def _update_table(self, routes: list):
        if dpg.does_item_exist(self.table_tag):
            for child in dpg.get_item_children(self.table_tag, slot=1):
                dpg.delete_item(child)

        self.current_routes = routes
        self.row_selectables = []
        self.selected_row = -1

        for idx, r in enumerate(routes):
            with dpg.table_row(parent=self.table_tag):
                selectable = dpg.add_selectable(
                    label=r.destination,
                    span_columns=True,
                    default_value=False,
                    user_data=idx,
                    callback=self._on_row_click
                )
                self.row_selectables.append(selectable)
                dpg.add_text(r.mask)
                dpg.add_text(r.gateway)
                dpg.add_text(r.interface)
                dpg.add_text(r.metric)

        if routes:
            self._select_row(0)

    def _on_row_click(self, sender, app_data, user_data):
        idx = user_data
        self._select_row(idx)

    def _select_row(self, idx):
        if self.selected_row != -1 and self.selected_row < len(self.row_selectables):
            dpg.set_value(self.row_selectables[self.selected_row], False)
        if 0 <= idx < len(self.row_selectables):
            dpg.set_value(self.row_selectables[idx], True)
            self.selected_row = idx
            route = self.current_routes[idx] if idx < len(self.current_routes) else None
            if route:
                print(f"Выбран маршрут: {route.destination} {route.mask} -> {route.gateway}")

    def handle_key(self, key):

        if not(dpg.get_item_configuration(self.popup_tag)['show']):
            self.table_handle(key)

        elif dpg.get_item_configuration(self.popup_tag)['show']:
            self.popup_handle(key)

    def table_handle(self, key):
        """обрабатывает клавишы если фокус на таблице"""
        # Если popup открыт, не перехватываем клавиши
        if dpg.get_item_configuration(self.popup_tag)['show']:
            return False

        focused = self.focus_manager.get_focused_element()
        # Если фокус на таблице
        if focused == self.table_tag:
            # Навигация по строкам
            if key == dpg.mvKey_Up:
                if self.selected_row > 0:
                    self._select_row(self.selected_row - 1)
                return True
            elif key == dpg.mvKey_Down:
                if self.selected_row < len(self.row_selectables) - 1:
                    self._select_row(self.selected_row + 1)
                return True
            # Вызов popup по Ctrl
            elif key in (dpg.mvKey_LControl, dpg.mvKey_RControl):
                if self.selected_row != -1:
                    self._show_popup()
                return True
            # Горизонтальные стрелки переключают фокус (если есть другие элементы)
            elif key == dpg.mvKey_Left or key == dpg.mvKey_Right:
                # Переключаем фокус на следующий/предыдущий зарегистрированный элемент
                direction = 1 if key == dpg.mvKey_Right else -1
                self.focus_manager.move_focus(direction)
                return True
            
        # Если фокус на другом элементе (например, кнопка), можно обработать Enter
        else:
            if key == dpg.mvKey_Return:
                # Здесь можно вызвать действие элемента, если он есть
                pass
            elif key == dpg.mvKey_Left or key == dpg.mvKey_Right:
                direction = 1 if key == dpg.mvKey_Right else -1
                self.focus_manager.move_focus(direction)
                return True

        return False

    def popup_handle(self,key):
        """обрабатывает клавиши если фокус на popup"""
        #print(dpg.get_item_parent("popup_menu_item1"))
        #print(dpg.get_item_children("route_popup")[1])

    def _show_popup(self):
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        popup_width = 200
        popup_height = 100
        pos_x = (viewport_width - popup_width) // 2
        pos_y = (viewport_height - popup_height) // 2
        dpg.set_item_pos(self.popup_tag, [pos_x, pos_y])
        dpg.configure_item(self.popup_tag, show=True)
        # Передаём фокус popup, чтобы можно было управлять стрелками внутри меню
        dpg.focus_item(self.popup_tag)
        print(dpg.get_focused_item())

    # ---------- Действия меню ----------
    def _edit_route(self):
        if self.selected_row == -1:
            return
        route = self.current_routes[self.selected_row]
        print(f"Редактирование маршрута: {route.destination} {route.mask} -> {route.gateway}")
        dpg.configure_item(self.popup_tag, show=False)
        self.focus_manager.set_focus(self.table_tag)   # возвращаем фокус на таблицу

    def _delete_route(self):
        if self.selected_row == -1:
            return
        route = self.current_routes[self.selected_row]
        print(f"Удаление маршрута: {route.destination} {route.mask} -> {route.gateway}")
        dpg.configure_item(self.popup_tag, show=False)
        self.focus_manager.set_focus(self.table_tag)

    def _add_route(self):
        print("Добавление нового маршрута")
        dpg.configure_item(self.popup_tag, show=False)
        self.focus_manager.set_focus(self.table_tag)

    def on_resize(self, width, height):
        pass