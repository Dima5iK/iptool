# focus_manager.py
import dearpygui.dearpygui as dpg

class FocusManager:
    """Управляет фокусом между зарегистрированными элементами и их темами"""
    def __init__(self):
        self._elements = []          # список тегов в порядке навигации
        self._themes = {}             # тег -> (active_theme, inactive_theme)
        self._focused_index = 0

    def register_element(self, tag, active_theme, inactive_theme, position=None):
        """Регистрирует элемент для управления фокусом.
        Если position не указан, добавляется в конец."""
        if tag in self._themes:
            # удаляем старую запись
            self._elements.remove(tag)
        if position is None:
            self._elements.append(tag)
        else:
            self._elements.insert(position, tag)
        self._themes[tag] = (active_theme, inactive_theme)
        # начальное состояние – неактивное
        dpg.bind_item_theme(tag, inactive_theme)

    def set_focus(self, tag):
        """Устанавливает фокус на указанный элемент"""
        print("focus_manager.set_fous:", tag)
        if tag not in self._elements:
            return
        # снимаем фокус с текущего
        if self._elements:
            current = self._elements[self._focused_index]
            dpg.bind_item_theme(current, self._themes[current][1])
        # устанавливаем новый
        self._focused_index = self._elements.index(tag)
        dpg.bind_item_theme(tag, self._themes[tag][0])

    def move_focus(self, direction: int):
        """direction: +1 вперёд (вправо/вниз), -1 назад (влево/вверх)"""
        if not self._elements:
            return
        new_index = (self._focused_index + direction) % len(self._elements)
        self.set_focus(self._elements[new_index])

    def get_focused_element(self):
        """Возвращает тег элемента, находящегося в фокусе, или None"""
        if self._elements:
            return self._elements[self._focused_index]
        return None