#gui.py
import dearpygui.dearpygui as dpg
from const import FONTS, UI_CONF
from model import NetworkState
from logic import NetworkController
class IPtoolGUI:

    def __init__(self, model: NetworkState, control:NetworkController):
        
        self.focused = "NIC_listbox"
        self.focused_theme = None
        self.unfocused_theme = None

        """Переменная которая хранит название элемента который сейчас обрабатывается"""
        self.model: NetworkState = model
        self.control:NetworkController = control
        self.setup_ui()

        #переменная для оторажения кнопок включения/отключения интерфейсов
        self.enable_option:str

        

    
    def register_key_handler(self):
        with dpg.handler_registry():
            dpg.add_key_press_handler(callback=self.key_press_callback)

    #логика клавиш управления
    def _vertical_move_selection(self,direction:int):
        """+1 - сдвиг вниз, -1 - свдиг вверх"""

        user_date:list = dpg.get_item_user_data(self.focused)
        current_pos = dpg.get_value(self.focused)
        if not current_pos:
            next_pos = user_date[0]     #если текущего положения нет (ничего не выбрано) - то выбираем первый элемент
        else:
            try:
                idx = user_date.index(current_pos)
            except ValueError:
                next_pos = user_date[0]
            else:
                next_pos = user_date[(idx + direction) % len(user_date)]
        dpg.set_value(self.focused,next_pos)
        if self.focused == "NIC_listbox":
            self._update_details_for_interface(next_pos[2:])    #убираем два первых символа и передаем как название элемента чтобы показать детали

    def _horizontal_move_selection(self,direction:int):
        """+1 - вправо, -1 - влево"""
        if self.focused == "NIC_listbox":
            if direction == 1:
                self.focused = "IP_listbox"
                self._apply_focus_theme()
            elif direction == -1:
                return None         #Возможно можно что то добавить сюда в будущем
        elif self.focused == "IP_listbox":
            if direction == -1:
                self.focused = "NIC_listbox"
                self._apply_focus_theme()
            elif direction == 1:
                return None         #Сюда тоже
    
    def _is_iplist_changed(self) -> bool:
        """Если для выбранного интерфейса ip адреса поменялись """
        interface = dpg.get_value("NIC_listbox")
        model_ip_list = self.model.get_ip_list(interface[2:])
        ui_ip_list = dpg.get_item_user_data("IP_listbox")

        if model_ip_list == (ui_ip_list[:-1]):
            return False
        else:
            return True

    def _write_del_symb(self,symb:str,action:int):
        """Вводим адрес в формате A.B.C.D/M вместо +. +1 - ввод, -1 - удаление"""
        """"""
        ip_list = dpg.get_item_user_data("IP_listbox")
        if not ip_list == None:
            if dpg.get_value("IP_listbox") == ip_list[len(ip_list)-1] and self.focused == "IP_listbox":        #проверка что мы не выбрали валидный IP
                if ip_list[len(ip_list)-1] == '+' and action == 1:
                    ip_list[len(ip_list)-1] = symb
                elif action == 1:
                    ip_list[len(ip_list)-1] = ip_list[len(ip_list)-1] + symb
                elif action == -1:
                    ip_list[len(ip_list)-1] = ip_list[len(ip_list)-1][:-1]

                if ip_list[len(ip_list)-1] == '':           #если удалены все символы то автоматически ставим +
                    ip_list[len(ip_list)-1] = '+'

                dpg.configure_item("IP_listbox",items=ip_list)
                dpg.set_value("IP_listbox",ip_list[len(ip_list)-1])
                dpg.set_item_user_data("IP_listbox",ip_list)
    
    def _enter_ip(self):
        """вызываем команду и вводим ip"""
        ip_list = dpg.get_item_user_data("IP_listbox")
        if dpg.get_value("IP_listbox") == ip_list[len(ip_list)-1] and self.focused == "IP_listbox":
            ip = dpg.get_value("IP_listbox")
            interface = dpg.get_value("NIC_listbox")
            self.control.add_ip(interface[2:],ip)

    def _remuve_ip(self):
        """Удаляем ip"""
        if self.focused == "IP_listbox":
            ip_list = dpg.get_item_user_data("IP_listbox")
            interface = dpg.get_value("NIC_listbox")
            ip = dpg.get_value("IP_listbox")
            self.control.del_ip(interface[2:],ip)
            #при удалении ip смещение курсора (сейчас кидает на +, а не на ближайшие айпи)
            if len(ip_list) > 1:
                dpg.set_value("IP_listbox",ip_list[len(ip_list)-1])

    def _set_dhcp(self):
        intterface_name = dpg.get_value("NIC_listbox")[2:]
        self.control.set_dhcp(intterface_name)
    
    def _disable_enable_NIC(self):
        """1 - включить, 0 - Выключить интерфейс"""
        intterface_name = dpg.get_value("NIC_listbox")[2:]
        if self.enable_option == "Disabled":
            self.control.enable_interface(intterface_name)
        else:
            self.control.disable_interface(intterface_name)

    def _update_description(self, text):
        dpg.set_value("info_descr", text)

    def _update_mac(self, mac):
        dpg.set_value("info_mac", mac)

    def _update_speed(self, speed):
        """Скорость интерфейса"""
        speed = self._format_speed(speed,1)
        dpg.set_value("info_speed", speed)
    
    def _format_speed(self, bps:int,multiplier:int):
        """Форматирование скорости в Гб/с, Мб/с или Кб/с"""
        bps = bps*multiplier        # Скорость интерфейса с x1, скорость прередачи данных x8
        if bps >= 1_000_000_000:
            return f"{bps/1_000_000_000:.2f} Гбит/с"
        elif bps >= 1_000_000:
            return f"{bps/1_000_000:.2f} Мбит/с"
        elif bps >= 1_000:
            return f"{bps/1_000:.2f} Кбит/с"
        else:
            return f"{bps:.0f} бит/с"
        
    def _update_rx(self, bytes_val, prev_bytes_val):
        last_sec_speed = bytes_val - prev_bytes_val
        last_sec_speed = self._format_speed(last_sec_speed,8)
        dpg.set_value("info_rx", last_sec_speed)
        
    def _update_tx(self, bytes_val, prev_bytes_val):
        last_sec_speed = bytes_val - prev_bytes_val
        last_sec_speed = self._format_speed(last_sec_speed,8)
        
        dpg.set_value("info_tx", last_sec_speed)

    def _update_ip_list(self, ip_list:list):
        ip_list = ip_list + ["+"]
        dpg.configure_item("IP_listbox",items=ip_list)
        dpg.set_item_user_data("IP_listbox",ip_list)

    def _update_details_for_interface(self, interface_name):
        """Обновляет детали для указанного имени интерфейса (без префикса)"""
        nic = self.model.get_interface_by_name(interface_name)
        nic_prev = self.model.get_interface_prev_state_by_name(interface_name)
        if not nic:
            return
        
        #обновляем только если не выбран IP_listbox или список адресов изменился иначе чем программой
        if not self.focused == "IP_listbox" or self._is_iplist_changed():        
            self._update_ip_list(nic.ip_addresses)

        self._update_description(nic.description)
        self._update_mac(nic.mac)
        self._update_speed(nic.speed)
        #Если мы не имеем информации о предыдущем состоянии (в момент первого опроса системы) то 
        # prev_state = текущее состояние. То есть скорость равно нулю
        prev_rx = nic_prev.received_bytes if nic_prev else nic.received_bytes
        prev_tx = nic_prev.sent_bytes if nic_prev else nic.sent_bytes
        self._update_rx(nic.received_bytes, prev_rx)
        self._update_tx(nic.sent_bytes, prev_tx)
    
    #осветление
    def _set_active(self):
        """осветление"""
        with dpg.theme() as Act_theme:
            with dpg.theme_component(dpg.mvListbox):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (61,61,65),category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255,255,255),category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (61,61,65),category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (61,61,65),category=dpg.mvThemeCat_Core)
                
        return Act_theme

    #затенение
    def _set_inactive(self):
        """затенение"""
        with dpg.theme() as Inact_theme:
            with dpg.theme_component(dpg.mvListbox):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (31,31,35),category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (180,180,180),category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (31,31,35),category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (31,31,35),category=dpg.mvThemeCat_Core)
                
        return Inact_theme

    def _apply_focus_theme(self):
        if self.focused == "NIC_listbox":
            dpg.bind_item_theme("NIC_listbox", self.focused_theme)
            dpg.bind_item_theme("IP_listbox", self.unfocused_theme)
        else:
            dpg.bind_item_theme("NIC_listbox", self.unfocused_theme)
            dpg.bind_item_theme("IP_listbox", self.focused_theme)

    def setup_ui(self):
        """Инициализация DPG, шрифтов и контекста"""
        dpg.create_context()
        #шрифты
        with dpg.font_registry():
            with dpg.font(FONTS.FONT_TAHOMA, 20, default_font=True, id="Default font"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_chars([0x25b2, 0x25bc, 0x00d7 ],parent="default")
            self.bigger_font = dpg.add_font(FONTS.FONT_TAHOMA, 26)
            self.smaller_font = dpg.add_font(FONTS.FONT_TAHOMA, 14)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=self.bigger_font)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=self.smaller_font)
            dpg.add_font_chars([0x25b2, 0x25bc, 0x00d7 ],parent=self.smaller_font)
        dpg.bind_font("Default font")


        
        with dpg.window(label="",tag="main_window",width=UI_CONF.main_width,height=UI_CONF.main_height):
            self.draw_content()
        self.register_key_handler()
        dpg.create_viewport(title="IPtool",height=UI_CONF.main_height,width=UI_CONF.main_width,resizable=False)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window",True)

                #темы
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
        dpg.bind_theme(global_theme)
        self.focused_theme = self._set_active()
        self.unfocused_theme = self._set_inactive()
        self._apply_focus_theme()  # применить начальную тему
    
    def draw_content(self):
        """Отрисовка основных элементов в окне"""
        #создаем вкладки
        with dpg.tab_bar(tag="main_tab_bar"):
            #вкладка с ip
            with dpg.tab(label="IP",tag=UI_CONF.ip_tab_id):
                with dpg.group(horizontal=True):
                    dpg.add_listbox(
                        tag="NIC_listbox",
                        num_items=UI_CONF.item_num,
                        width= UI_CONF.main_width*UI_CONF.listbox_width[0],
                        callback=self.show_detail
                    )
                    with dpg.popup(dpg.last_item(),tag="interface_popup",min_size=[50,40]):
                        dpg.add_menu_item(label="DHCP", callback=self._set_dhcp,tag="popup_dhcp")
                        dpg.add_menu_item(label="Включить",callback=self._disable_enable_NIC,tag="popup_enable",show=False)
                        dpg.add_menu_item(label="Отключить",callback=self._disable_enable_NIC,tag="popup_disable",show=False)
                        
                    dpg.add_listbox(
                        tag="IP_listbox",
                        num_items=UI_CONF.item_num,
                        width=UI_CONF.main_width*UI_CONF.listbox_width[1]
                    )
                #загрушка для верстки
                plug1 = dpg.add_text(default_value="",tag="plug1")
                dpg.bind_item_font(plug1,self.smaller_font)
                
                #описание/мак
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="info_descr",default_value="описание",readonly=True,width=UI_CONF.main_width*UI_CONF.info_descr_width)
                    dpg.add_input_text(tag="info_mac",default_value="MAC",readonly=True,width=UI_CONF.main_width*UI_CONF.info_mac_width)
                #скорость/передано/получено
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="info_speed",readonly=True, default_value="скорость",width=UI_CONF.main_width*UI_CONF.info_speed_width)
                    dpg.add_input_text(tag="info_rx",readonly=True, default_value="RX",width=UI_CONF.main_width*UI_CONF.info_rx_width)
                    dpg.add_input_text(tag="info_tx",readonly=True, default_value="TX",width=UI_CONF.main_width*UI_CONF.info_tx_width)
                
                #Отрисовка знака вопроса
                hlp = dpg.add_text(default_value='?',tag="help")
                dpg.bind_item_font(hlp,self.bigger_font)
                with dpg.tooltip("help"):
                    dpg.add_text(default_value=UI_CONF.help_text,tag="hlp_tooltip")
                dpg.bind_item_font("hlp_tooltip",self.smaller_font)
                dpg.set_item_pos("help",[int(UI_CONF.main_width*UI_CONF.hlp_tooltip_scale[0]),int(UI_CONF.main_height*UI_CONF.hlp_tooltip_scale[1])])

        



            with dpg.tab(label="Route",tag=UI_CONF.route_tab_id):
                pass
        dpg.bind_item_theme("NIC_listbox",self.focused_theme)
        dpg.bind_item_theme("IP_listbox",self.unfocused_theme)
    
    #callback
    def show_detail(self, sender, app_data, user_data):
        """Показывает детали IP, описание и тд"""
        # app_data — выбранная строка с префиксом (например, "▲ Ethernet")
        clean_name = app_data[2:]  # убираем первые два символа (стрелка и пробел)
        
        # Обновляем текстовые поля
        self._update_details_for_interface(clean_name)
        
    
    def key_press_callback(self,sendef,key):
        """Обработка всех доступных нажатий с вызовом соответсвующих методов"""
        
        if len(self.model.get_all_inetfaces()):         #если модель не пустая
            if key == dpg.mvKey_Up:
                self._vertical_move_selection(-1)

            elif key == dpg.mvKey_Left:
                self._horizontal_move_selection(-1)

            elif key == dpg.mvKey_Right:
                self._horizontal_move_selection(1)

            elif key == dpg.mvKey_Down:
                self._vertical_move_selection(1)

            elif key == dpg.mvKey_Delete:
                self._remuve_ip()

            elif key == dpg.mvKey_Back and (1000 == dpg.get_value('main_tab_bar')):
                self._write_del_symb('',-1)

            if key == dpg.mvKey_Return:
                self._enter_ip()

            elif key == dpg.mvKey_NumPad0 or key == dpg.mvKey_0:
                self._write_del_symb("0",1)

            elif key == dpg.mvKey_NumPad1  or key == dpg.mvKey_1:
                self._write_del_symb("1",1)

            elif key == dpg.mvKey_NumPad2 or key == dpg.mvKey_2:
                self._write_del_symb("2",1)

            elif key == dpg.mvKey_NumPad3 or key == dpg.mvKey_3:
                self._write_del_symb("3",1)

            elif key == dpg.mvKey_NumPad4 or key == dpg.mvKey_4:
                self._write_del_symb("4",1)

            elif key == dpg.mvKey_NumPad5 or key == dpg.mvKey_5:
                self._write_del_symb("5",1)

            elif key == dpg.mvKey_NumPad6 or key == dpg.mvKey_6:
                self._write_del_symb("6",1)
        
            elif key == dpg.mvKey_NumPad7 or key == dpg.mvKey_7:
                self._write_del_symb("7",1)

            elif key == dpg.mvKey_NumPad8 or key == dpg.mvKey_8:
                self._write_del_symb("8",1)

            elif key == dpg.mvKey_NumPad9 or key == dpg.mvKey_9:
                self._write_del_symb("9",1)

            elif key == dpg.mvKey_Decimal:
                self._write_del_symb(".",1)

            elif key == dpg.mvKey_Divide:
                self._write_del_symb("/",1)


        
    
    #обновление содержимого
    def update_display(self):
        interfaces = self.model.get_all_inetfaces()
        if not interfaces:
            return

        # Обновляем список интерфейсов
        display_names = []
        
        for nic in interfaces:
            display_names.append(f"▲ {nic.name}" if nic.status == "Up" else (f"▼ {nic.name}" if nic.status == "Disconnected" else f"  {nic.name}"))
        #names = [nic.name for nic in interfaces]
        dpg.configure_item("NIC_listbox",items=display_names)
        dpg.set_item_user_data("NIC_listbox",display_names)
        

        # Обновляем детали для выбранного (если есть)
        selected_display = dpg.get_value("NIC_listbox")
        if selected_display and isinstance(selected_display, str):
            clean_name = selected_display[2:] if len(selected_display) > 2 else selected_display
            self._update_details_for_interface(clean_name)

    def show(self):
        dpg.show_viewport()

    def clean_up(self):
        dpg.destroy_context()
