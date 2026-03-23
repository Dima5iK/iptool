# ip_tab.py
import dearpygui.dearpygui as dpg
from const import UI_CONF
from .base_tab import BaseTab
from ..helpers import format_speed, format_interface_status

class IPTab(BaseTab):
    def __init__(self, model, controller, focus_manager, parent_tag):
        super().__init__(model, controller, focus_manager, parent_tag)
        self.conf = UI_CONF()
        # теги элементов
        self.nic_listbox_tag = "nic_listbox"
        self.ip_listbox_tag = "ip_listbox"
        self.info_descr_tag = "info_descr"
        self.info_mac_tag = "info_mac"
        self.info_speed_tag = "info_speed"
        self.info_rx_tag = "info_rx"
        self.info_tx_tag = "info_tx"
        self.popup_tag = "interface_popup"
        self.popup_dhcp = "popup_dhcp"
        self.popup_enable = "popup_enable"
        self.popup_disable = "popup_disable"
        # состояние для включения/отключения интерфейса
        self.enable_option = None

    def build(self):
        """Создаёт все элементы вкладки IP"""
        # Создаём контейнер внутри переданной вкладки
        with dpg.group(parent=self.parent_tag):
            # Первая строка: два списка
            with dpg.group(horizontal=True):
                dpg.add_listbox(
                    tag=self.nic_listbox_tag,
                    num_items=self.conf.item_num,
                    width=int(self.conf.main_width * self.conf.NIC_listbox_scale)
                )
                # Контекстное меню для списка интерфейсов
                with dpg.popup(dpg.last_item(), tag=self.popup_tag, min_size=[50,40]):
                    dpg.add_menu_item(label="DHCP", callback=self._set_dhcp, tag=self.popup_dhcp)
                    dpg.add_menu_item(label="Включить", callback=self._disable_enable_NIC,
                                      tag=self.popup_enable, show=False)
                    dpg.add_menu_item(label="Отключить", callback=self._disable_enable_NIC,
                                      tag=self.popup_disable, show=False)

                dpg.add_listbox(
                    tag=self.ip_listbox_tag,
                    num_items=self.conf.item_num,
                    width=int(self.conf.main_width * self.conf.IP_listbox_scale)
                )

            # Пустой текст для отступа
            dpg.add_text(default_value="", tag="plug1")

            # Вторая строка: описание и MAC
            with dpg.group(horizontal=True):
                dpg.add_input_text(tag=self.info_descr_tag, default_value="описание", readonly=True,
                                   width=int(self.conf.main_width * self.conf.info_descr_scale))
                dpg.add_input_text(tag=self.info_mac_tag, default_value="MAC", readonly=True,
                                   width=int(self.conf.main_width * self.conf.info_mac_scale))

            # Третья строка: скорость, RX, TX
            with dpg.group(horizontal=True):
                dpg.add_input_text(tag=self.info_speed_tag, readonly=True, default_value="скорость",
                                   width=int(self.conf.main_width * self.conf.info_speed_scale))
                dpg.add_input_text(tag=self.info_rx_tag, readonly=True, default_value="RX",
                                   width=int(self.conf.main_width * self.conf.info_rx_scale))
                dpg.add_input_text(tag=self.info_tx_tag, readonly=True, default_value="TX",
                                   width=int(self.conf.main_width * self.conf.info_tx_scale))

        # Регистрируем фокусируемые элементы в FocusManager
        # Создаём темы (копируем из gui.py)
        active_theme = self._create_theme((61,61,65), (255,255,255))
        inactive_theme = self._create_theme((31,31,35), (180,180,180))

        self.focus_manager.register_element(self.nic_listbox_tag, active_theme, inactive_theme, position=0)
        self.focus_manager.register_element(self.ip_listbox_tag, active_theme, inactive_theme, position=1)
        # Устанавливаем начальный фокус на список интерфейсов
        self.focus_manager.set_focus(self.nic_listbox_tag)

    def _create_theme(self, bg_color, text_color):
        """Создаёт тему для listbox с указанными цветами"""
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvListbox):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, bg_color, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, text_color, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, bg_color, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, bg_color, category=dpg.mvThemeCat_Core)
        return theme

    # ---------- Обработка клавиш ----------
    def handle_key(self, key):
        """Возвращает True, если клавиша обработана"""
        focused = self.focus_manager.get_focused_element()
        if not focused:
            return False

        # Горизонтальные стрелки – переключение между списками
        if key == dpg.mvKey_Left:
            self.focus_manager.move_focus(-1)
            return True
        if key == dpg.mvKey_Right:
            self.focus_manager.move_focus(1)
            return True

        # Вертикальные стрелки – навигация внутри текущего списка
        if key == dpg.mvKey_Up:
            return self._vertical_move(-1)
        if key == dpg.mvKey_Down:
            return self._vertical_move(1)

        # Обработка ввода IP (только когда фокус на списке IP и выбран элемент '+')
        if focused == self.ip_listbox_tag:
            # Клавиши цифр, точки, слеша
            if key in (dpg.mvKey_NumPad0, dpg.mvKey_0):
                return self._write_del_symb("0", 1)
            if key in (dpg.mvKey_NumPad1, dpg.mvKey_1):
                return self._write_del_symb("1", 1)
            if key in (dpg.mvKey_NumPad2, dpg.mvKey_2):
                return self._write_del_symb("2", 1)
            if key in (dpg.mvKey_NumPad3, dpg.mvKey_3):
                return self._write_del_symb("3", 1)
            if key in (dpg.mvKey_NumPad4, dpg.mvKey_4):
                return self._write_del_symb("4", 1)
            if key in (dpg.mvKey_NumPad5, dpg.mvKey_5):
                return self._write_del_symb("5", 1)
            if key in (dpg.mvKey_NumPad6, dpg.mvKey_6):
                return self._write_del_symb("6", 1)
            if key in (dpg.mvKey_NumPad7, dpg.mvKey_7):
                return self._write_del_symb("7", 1)
            if key in (dpg.mvKey_NumPad8, dpg.mvKey_8):
                return self._write_del_symb("8", 1)
            if key in (dpg.mvKey_NumPad9, dpg.mvKey_9):
                return self._write_del_symb("9", 1)
            if key == dpg.mvKey_Decimal:
                return self._write_del_symb(".", 1)
            if key == dpg.mvKey_Divide:
                return self._write_del_symb("/", 1)
            if key == dpg.mvKey_Back:   # Backspace
                return self._write_del_symb("", -1)
            if key == dpg.mvKey_Return:
                return self._enter_ip()
            if key == dpg.mvKey_Delete:
                return self._remove_ip()

        return False

    def _vertical_move(self, direction):
        """Перемещение внутри активного списка"""
        focused = self.focus_manager.get_focused_element()
        if not focused:
            return False

        current = dpg.get_value(focused)
        items = dpg.get_item_user_data(focused)  # ранее мы сохраняли список элементов
        if not items:
            return False

        if not current:
            next_item = items[0]
        else:
            try:
                idx = items.index(current)
                next_item = items[(idx + direction) % len(items)]
            except ValueError:
                next_item = items[0]

        dpg.set_value(focused, next_item)

        # Если это список интерфейсов, обновляем детали
        if focused == self.nic_listbox_tag:
            clean_name = next_item[2:]  # убираем символ состояния
            self._update_details_for_interface(clean_name)

        return True

    # ---------- Ввод/удаление IP ----------
    def _write_del_symb(self, symb, action):
        """action: +1 добавить символ, -1 удалить последний"""
        ip_list = dpg.get_item_user_data(self.ip_listbox_tag)
        if not ip_list:
            return False

        # Проверяем, что выбран последний элемент (+ или строка ввода)
        selected = dpg.get_value(self.ip_listbox_tag)
        if selected != ip_list[-1]:
            return False

        if action == 1:
            if ip_list[-1] == '+':
                ip_list[-1] = symb
            else:
                ip_list[-1] += symb
        elif action == -1:
            ip_list[-1] = ip_list[-1][:-1]
            if ip_list[-1] == '':
                ip_list[-1] = '+'

        dpg.configure_item(self.ip_listbox_tag, items=ip_list)
        dpg.set_value(self.ip_listbox_tag, ip_list[-1])
        dpg.set_item_user_data(self.ip_listbox_tag, ip_list)
        return True

    def _enter_ip(self):
        """Добавление IP через Enter"""
        ip_list = dpg.get_item_user_data(self.ip_listbox_tag)
        if not ip_list:
            return False
        selected = dpg.get_value(self.ip_listbox_tag)
        if selected != ip_list[-1]:
            return False

        interface_display = dpg.get_value(self.nic_listbox_tag)
        if not interface_display:
            return False
        interface_name = interface_display[2:]
        ip_cidr = selected
        self.controller.add_ip(interface_name, ip_cidr)
        return True

    def _remove_ip(self):
        """Удаление IP через Delete"""
        focused = self.focus_manager.get_focused_element()
        if focused != self.ip_listbox_tag:
            return False

        ip_list = dpg.get_item_user_data(self.ip_listbox_tag)
        if not ip_list:
            return False
        selected = dpg.get_value(self.ip_listbox_tag)
        if selected == ip_list[-1]:   # нельзя удалить строку ввода
            return False

        interface_display = dpg.get_value(self.nic_listbox_tag)
        if not interface_display:
            return False
        interface_name = interface_display[2:]
        self.controller.del_ip(interface_name, selected)
        return True

    # ---------- Контекстное меню ----------
    def _set_dhcp(self, sender, app_data, user_data):
        interface_display = dpg.get_value(self.nic_listbox_tag)
        if interface_display:
            interface_name = interface_display[2:]
            self.controller.set_dhcp(interface_name)

    def _disable_enable_NIC(self, sender, app_data, user_data):
        interface_display = dpg.get_value(self.nic_listbox_tag)
        if not interface_display:
            return
        interface_name = interface_display[2:]
        if self.enable_option == "Disabled":
            self.controller.enable_interface(interface_name)
        else:
            self.controller.disable_interface(interface_name)

    # ---------- Обновление отображения ----------
    def update_display(self):
        """Обновляет все элементы данными из модели"""
        interfaces = self.model.get_all_interfaces()
        if not interfaces:
            return

        # Обновляем список интерфейсов
        display_names = []
        for nic in interfaces:
            symbol = format_interface_status(nic.status)
            display_names.append(f"{symbol} {nic.name}")
        dpg.configure_item(self.nic_listbox_tag, items=display_names)
        dpg.set_item_user_data(self.nic_listbox_tag, display_names)

        # Обновляем детали для выбранного интерфейса
        selected_display = dpg.get_value(self.nic_listbox_tag)
        if selected_display and isinstance(selected_display, str):
            clean_name = selected_display[2:]
            self._update_details_for_interface(clean_name)

            # Обновляем пункты контекстного меню
            nic = self.model.get_interface_by_name(clean_name)
            if nic:
                self.enable_option = nic.status
                if nic.status in ("Disabled", "Not Present"):
                    dpg.configure_item(self.popup_enable, show=True)
                    dpg.configure_item(self.popup_disable, show=False)
                else:
                    dpg.configure_item(self.popup_enable, show=False)
                    dpg.configure_item(self.popup_disable, show=True)

    def _update_details_for_interface(self, interface_name):
        """Обновляет нижнюю панель для указанного интерфейса"""
        nic = self.model.get_interface_by_name(interface_name)
        nic_prev = self.model.get_interface_prev_state_by_name(interface_name)
        if not nic:
            return

        # Обновляем список IP (добавляем '+')
        ip_list = nic.ip_addresses.copy()
        ip_list.append("+")
        dpg.configure_item(self.ip_listbox_tag, items=ip_list)
        dpg.set_item_user_data(self.ip_listbox_tag, ip_list)

        dpg.set_value(self.info_descr_tag, nic.description)
        dpg.set_value(self.info_mac_tag, nic.mac)
        dpg.set_value(self.info_speed_tag, format_speed(nic.speed, 1))

        prev_rx = nic_prev.received_bytes if nic_prev else nic.received_bytes
        prev_tx = nic_prev.sent_bytes if nic_prev else nic.sent_bytes
        dpg.set_value(self.info_rx_tag, format_speed(nic.received_bytes - prev_rx, 8))
        dpg.set_value(self.info_tx_tag, format_speed(nic.sent_bytes - prev_tx, 8))

    # ---------- Обработка ресайза ----------
    def on_resize(self, width, height):
        """Адаптирует размеры элементов под новые размеры окна"""
        # Обновляем ширины
        dpg.configure_item(self.nic_listbox_tag, width=int(width * self.conf.NIC_listbox_scale))
        dpg.configure_item(self.ip_listbox_tag, width=int(width * self.conf.IP_listbox_scale))
        dpg.configure_item(self.info_descr_tag, width=int(width * self.conf.info_descr_scale))
        dpg.configure_item(self.info_mac_tag, width=int(width * self.conf.info_mac_scale))
        dpg.configure_item(self.info_speed_tag, width=int(width * self.conf.info_speed_scale))
        dpg.configure_item(self.info_rx_tag, width=int(width * self.conf.info_rx_scale))
        dpg.configure_item(self.info_tx_tag, width=int(width * self.conf.info_tx_scale))

        # Вычисляем количество элементов в listbox в зависимости от высоты
        # (логика из resize_callback)
        available_height = height - 170  # примерное значение, можно уточнить
        num_items = available_height // 10
        # Ограничиваем разумными пределами
        if num_items < 4:
            num_items = 4
        elif num_items > 15:
            num_items = 15
        dpg.configure_item(self.nic_listbox_tag, num_items=num_items)
        dpg.configure_item(self.ip_listbox_tag, num_items=num_items)