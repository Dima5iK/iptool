# base_tab.py
from abc import ABC, abstractmethod

class BaseTab(ABC):
    """Абстрактный базовый класс для всех вкладок"""
    def __init__(self, model, controller, focus_manager, parent_tag):
        self.model = model
        self.controller = controller
        self.focus_manager = focus_manager
        self.parent_tag = parent_tag   # тег родительского элемента (tab)
        self.tag = None                # тег корневой группы вкладки (если нужно)

    @abstractmethod
    def build(self):
        """Создаёт содержимое вкладки внутри parent_tag"""
        pass

    @abstractmethod
    def update_display(self):
        """Обновляет отображение на основе текущих данных модели"""
        pass

    @abstractmethod
    def handle_key(self, key):
        """Обрабатывает нажатие клавиши. Возвращает True, если клавиша обработана."""
        return False

    def on_resize(self, width, height):
        """Вызывается при изменении размеров главного окна"""
        pass

    def on_focus_gained(self):
        """Вызывается, когда вкладка становится активной"""
        pass

    def on_focus_lost(self):
        """Вызывается, когда вкладка перестаёт быть активной"""
        pass