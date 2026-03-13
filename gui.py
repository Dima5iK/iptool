#gui.py
import dearpygui.dearpygui as dpg
from const import FONTS, UI_CONF
from model import NetworkState
from logic import NetworkController
class IPtoolGUI:

    def __init__(self, model: NetworkState, control:NetworkController):
        self.conf = UI_CONF()
        self.focused = self.conf.NIC_listbox_tag
        self.focused_theme = None
        self.unfocused_theme = None

        """Переменная которая хранит название элемента который сейчас обрабатывается"""
        self.model: NetworkState = model
        self.control:NetworkController = control
        self.setup_ui()

        #переменная для оторажения кнопок включения/отключения интерфейсов
        self.enable_option:str

        

    #callback

    def lmb_click_callback(self, sender, app_data):
        """Обработка ЛКМ

        Показывает детали IP, описание и тд"""

        if self.focused == self.conf.NIC_listbox_tag and app_data[1] == self.conf.NIC_listbox_tag:
            user_data = dpg.get_value(app_data[1])
            clean_name = user_data[2:]  # убираем первые два символа (стрелка и пробел)
            # Обновляем текстовые поля
            self._update_details_for_interface(clean_name)

        elif self.focused == self.conf.IP_listbox_tag and app_data[1] == self.conf.NIC_listbox_tag:
            self.focused = self.conf.NIC_listbox_tag
            self._apply_focus_theme()
        
        elif self.focused == self.conf.NIC_listbox_tag and app_data[1] == self.conf.IP_listbox_tag:
            self.focused = self.conf.IP_listbox_tag
            self._apply_focus_theme()
    
    def show_popup_callback(self,sender, app_data, user_data):
        """обработка ПКМ"""
        dpg.configure_item("interface_popup",show = True)
    
    def key_press_callback(self,sendef,key):
        """Обработка всех доступных нажатий с вызовом соответсвующих методов"""
        
        if len(self.model.get_all_interfaces()):         #если модель не пустая
            if key == dpg.mvKey_Up:
                self._vertical_move_selection(-1)

            elif key == dpg.mvKey_Left:
                self._horizontal_move_selection(-1)

            elif key == dpg.mvKey_Right:
                self._horizontal_move_selection(1)

            elif key == dpg.mvKey_Down:
                self._vertical_move_selection(1)

            elif key == dpg.mvKey_Delete:
                self._remove_ip()

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


    def resize_callback(self,sender,appdata, user_data):
        main_window_width:int = dpg.get_item_width("main_window")
        main_window_height:int = dpg.get_item_height("main_window")

        items_list:list = [self.conf.NIC_listbox_tag,self.conf.IP_listbox_tag,self.conf.info_descr_tag,
                           self.conf.info_mac_tag,self.conf.info_speed_tag, self.conf.info_rx_tag, self.conf.info_tx_tag]
        
        item_scale_list:list = [self.conf.NIC_listbox_scale, self.conf.IP_listbox_scale, self.conf.info_descr_scale, 
                                self.conf.info_mac_scale, self.conf.info_speed_scale,self.conf.info_rx_scale,
                                self.conf.info_tx_scale ]
        for iter in range(len(items_list)):
            dpg.configure_item(items_list[iter],width = int(main_window_width*item_scale_list[iter]))


        dpg.set_item_pos(self.conf.help_tooltip_text_tag,[main_window_width*self.conf.hlp_tooltip_scale[0],main_window_height*self.conf.hlp_tooltip_scale[1]])

        match ((main_window_height - 170) // 10):

            case 10:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=4)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=4)
            case 11:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=5)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=5)
            case 13:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=6)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=6)
            case 15:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=7)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=7)
            case 18:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=8)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=8)
            case 20:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=9)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=9)
            case 23:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=10)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=10)
            case 25:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=11)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=11)
            case 27:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=12)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=12)
            case 30:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=13)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=13)
            case 32:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=14)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=14)
            case 35:
                dpg.configure_item(self.conf.NIC_listbox_tag, num_items=15)
                dpg.configure_item(self.conf.IP_listbox_tag, num_items=15)
            # Для всех остальных значений можно ничего не делать или задать значение по умолчанию
            case _:
                pass  # или, например, dpg.configure_item("listbox", num_items=3)
        
    
    def register_key_handler(self):
        with dpg.handler_registry():
            dpg.add_key_press_handler(callback=self.key_press_callback)

    def register_click_handler(self):
        with dpg.item_handler_registry(tag="resize_handler"):
            dpg.add_item_resize_handler(callback=self.resize_callback)
        with dpg.item_handler_registry(tag="listbox_click"):
            dpg.add_item_clicked_handler(callback=self.lmb_click_callback, button= 0)
            dpg.add_item_clicked_handler(button=1,callback=self.show_popup_callback)

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
        if self.focused == self.conf.NIC_listbox_tag:
            self._update_details_for_interface(next_pos[2:])    #убираем два первых символа и передаем как название элемента чтобы показать детали

    def _horizontal_move_selection(self,direction:int):
        """+1 - вправо, -1 - влево"""
        if self.focused == self.conf.NIC_listbox_tag:
            if direction == 1:
                self.focused = self.conf.IP_listbox_tag
                self._apply_focus_theme()
            elif direction == -1:
                return None         #Возможно можно что то добавить сюда в будущем
        elif self.focused == self.conf.IP_listbox_tag:
            if direction == -1:
                self.focused = self.conf.NIC_listbox_tag
                self._apply_focus_theme()
            elif direction == 1:
                return None         #Сюда тоже
    
    def _is_iplist_changed(self) -> bool:
        """Если для выбранного интерфейса ip адреса поменялись """
        interface = dpg.get_value(self.conf.NIC_listbox_tag)
        model_ip_list = self.model.get_ip_list(interface[2:])
        ui_ip_list = dpg.get_item_user_data(self.conf.IP_listbox_tag)

        if model_ip_list == (ui_ip_list[:-1]):
            return False
        else:
            return True

    def _write_del_symb(self,symb:str,action:int):
        """Вводим адрес в формате A.B.C.D/M вместо +. +1 - ввод, -1 - удаление"""
        """"""
        ip_list = dpg.get_item_user_data(self.conf.IP_listbox_tag)
        if not ip_list == None:
            if dpg.get_value(self.conf.IP_listbox_tag) == ip_list[len(ip_list)-1] and self.focused == self.conf.IP_listbox_tag:        #проверка что мы не выбрали валидный IP
                if ip_list[len(ip_list)-1] == '+' and action == 1:
                    ip_list[len(ip_list)-1] = symb
                elif action == 1:
                    ip_list[len(ip_list)-1] = ip_list[len(ip_list)-1] + symb
                elif action == -1:
                    ip_list[len(ip_list)-1] = ip_list[len(ip_list)-1][:-1]

                if ip_list[len(ip_list)-1] == '':           #если удалены все символы то автоматически ставим +
                    ip_list[len(ip_list)-1] = '+'

                dpg.configure_item(self.conf.IP_listbox_tag,items=ip_list)
                dpg.set_value(self.conf.IP_listbox_tag,ip_list[len(ip_list)-1])
                dpg.set_item_user_data(self.conf.IP_listbox_tag,ip_list)
    
    def _enter_ip(self):
        """вызываем команду и вводим ip"""
        ip_list = dpg.get_item_user_data(self.conf.IP_listbox_tag)
        if dpg.get_value(self.conf.IP_listbox_tag) == ip_list[len(ip_list)-1] and self.focused == self.conf.IP_listbox_tag:
            ip = dpg.get_value(self.conf.IP_listbox_tag)
            interface = dpg.get_value(self.conf.NIC_listbox_tag)
            self.control.add_ip(interface[2:],ip)

    def _remove_ip(self):
        """Удаляем ip"""
        if self.focused == self.conf.IP_listbox_tag:
            ip_list = dpg.get_item_user_data(self.conf.IP_listbox_tag)
            interface = dpg.get_value(self.conf.NIC_listbox_tag)
            ip = dpg.get_value(self.conf.IP_listbox_tag)
            self.control.del_ip(interface[2:],ip)
            #при удалении ip смещение курсора (сейчас кидает на +, а не на ближайшие айпи)
            if len(ip_list) > 1:
                dpg.set_value(self.conf.IP_listbox_tag,ip_list[len(ip_list)-1])

    def _set_dhcp(self,sender,app_data,userdata):
        intterface_name = dpg.get_value(self.conf.NIC_listbox_tag)[2:]
        self.control.set_dhcp(intterface_name)
    
    def _disable_enable_NIC(self,sender,app_data,userdata):
        """1 - включить, 0 - Выключить интерфейс"""
        intterface_name = dpg.get_value(self.conf.NIC_listbox_tag)[2:]
        if self.enable_option == "Disabled":
            self.control.enable_interface(intterface_name)
        else:
            self.control.disable_interface(intterface_name)

    def _update_description(self, text):
        dpg.set_value(self.conf.info_descr_tag, text)

    def _update_mac(self, mac):
        dpg.set_value(self.conf.info_mac_tag, mac)

    def _update_speed(self, speed):
        """Скорость интерфейса"""
        speed = self._format_speed(speed,1)
        dpg.set_value(self.conf.info_speed_tag, speed)
    
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
        dpg.set_value(self.conf.info_rx_tag, last_sec_speed)
        
    def _update_tx(self, bytes_val, prev_bytes_val):
        last_sec_speed = bytes_val - prev_bytes_val
        last_sec_speed = self._format_speed(last_sec_speed,8)
        
        dpg.set_value(self.conf.info_tx_tag, last_sec_speed)

    def _update_ip_list(self, ip_list:list):
        ip_list = ip_list + ["+"]
        dpg.configure_item(self.conf.IP_listbox_tag,items=ip_list)
        dpg.set_item_user_data(self.conf.IP_listbox_tag,ip_list)

    def _update_details_for_interface(self, interface_name):
        """Обновляет детали для указанного имени интерфейса (без префикса)"""
        nic = self.model.get_interface_by_name(interface_name)
        nic_prev = self.model.get_interface_prev_state_by_name(interface_name)
        if not nic:
            return
        
        #обновляем только если не выбран IP_listbox или список адресов изменился иначе чем программой
        if not self.focused == self.conf.IP_listbox_tag or self._is_iplist_changed():        
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
        if self.focused == self.conf.NIC_listbox_tag:
            dpg.bind_item_theme(self.conf.NIC_listbox_tag, self.focused_theme)
            dpg.bind_item_theme(self.conf.IP_listbox_tag, self.unfocused_theme)
        else:
            dpg.bind_item_theme(self.conf.NIC_listbox_tag, self.unfocused_theme)
            dpg.bind_item_theme(self.conf.IP_listbox_tag, self.focused_theme)

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


        
        with dpg.window(label="",tag="main_window",width=self.conf.main_width,height=self.conf.main_height):
            self.draw_content()
        self.register_key_handler()
        self.register_click_handler()
        dpg.bind_item_handler_registry("main_window", "resize_handler")
        dpg.bind_item_handler_registry(self.conf.NIC_listbox_tag, "listbox_click")
        dpg.bind_item_handler_registry(self.conf.IP_listbox_tag, "listbox_click")
        dpg.create_viewport(title="IPtool",height=self.conf.main_height,width=self.conf.main_width,resizable=True, 
                            min_width= self.conf.main_min_width, min_height=self.conf.main_min_height, max_height= self.conf.main_max_height)
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
            with dpg.tab(label="IP",tag=self.conf.ip_tab_id):
                with dpg.group(horizontal=True):
                    dpg.add_listbox(
                        tag=self.conf.NIC_listbox_tag,
                        num_items=self.conf.item_num,
                        width= self.conf.main_width*self.conf.NIC_listbox_scale,
                        
                    )
                    with dpg.popup(dpg.last_item(),tag="interface_popup",min_size=[50,40]):
                        dpg.add_menu_item(label="DHCP", callback=self._set_dhcp,tag="popup_dhcp")
                        dpg.add_menu_item(label="Включить",callback=self._disable_enable_NIC,tag="popup_enable",show=False)
                        dpg.add_menu_item(label="Отключить",callback=self._disable_enable_NIC,tag="popup_disable",show=False)
                        
                    dpg.add_listbox(
                        tag=self.conf.IP_listbox_tag,
                        num_items=self.conf.item_num,
                        width=self.conf.main_width*self.conf.IP_listbox_scale
                    )
                #загрушка для верстки
                plug1 = dpg.add_text(default_value="",tag="plug1")
                dpg.bind_item_font(plug1,self.smaller_font)
                
                #описание/мак
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag=self.conf.info_descr_tag,default_value="описание",readonly=True,width=self.conf.main_width*self.conf.info_descr_scale)
                    dpg.add_input_text(tag=self.conf.info_mac_tag,default_value="MAC",readonly=True,width=self.conf.main_width*self.conf.info_mac_scale)
                #скорость/передано/получено
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag=self.conf.info_speed_tag,readonly=True, default_value="скорость",width=self.conf.main_width*self.conf.info_speed_scale)
                    dpg.add_input_text(tag=self.conf.info_rx_tag,readonly=True, default_value="RX",width=self.conf.main_width*self.conf.info_rx_scale)
                    dpg.add_input_text(tag=self.conf.info_tx_tag,readonly=True, default_value="TX",width=self.conf.main_width*self.conf.info_tx_scale)
                
                #Отрисовка знака вопроса
                hlp = dpg.add_text(default_value='?',tag=self.conf.help_tooltip_text_tag)
                dpg.bind_item_font(hlp,self.bigger_font)
                with dpg.tooltip(self.conf.help_tooltip_text_tag):
                    dpg.add_text(default_value=self.conf.help_text,tag="hlp_tooltip")
                dpg.bind_item_font("hlp_tooltip",self.smaller_font)
                dpg.set_item_pos(self.conf.help_tooltip_text_tag,[int(self.conf.main_width*self.conf.hlp_tooltip_scale[0]),int(self.conf.main_height*self.conf.hlp_tooltip_scale[1])])

        



            with dpg.tab(label="Route",tag=self.conf.route_tab_id):
                pass
        dpg.bind_item_theme(self.conf.NIC_listbox_tag,self.focused_theme)
        dpg.bind_item_theme(self.conf.IP_listbox_tag,self.unfocused_theme)
    
    #обновление содержимого
    def update_display(self):
        interfaces = self.model.get_all_interfaces()
        if not interfaces:
            return

        # Обновляем список интерфейсов
        display_names = []
        
        for nic in interfaces:
            display_names.append(f"▲ {nic.name}" if nic.status == "Up" else (f"▼ {nic.name}" if nic.status == "Disconnected" else f"  {nic.name}"))
        #names = [nic.name for nic in interfaces]
        dpg.configure_item(self.conf.NIC_listbox_tag,items=display_names)
        dpg.set_item_user_data(self.conf.NIC_listbox_tag,display_names)
        

        # Обновляем детали для выбранного (если есть)
        selected_display = dpg.get_value(self.conf.NIC_listbox_tag)
        if selected_display and isinstance(selected_display, str):
            clean_name = selected_display[2:] if len(selected_display) > 2 else selected_display
            self._update_details_for_interface(clean_name)

            self.enable_option = self.model.get_interface_by_name(dpg.get_value(self.conf.NIC_listbox_tag)[2:]).status
            if self.enable_option == "Disabled" or self.enable_option == "Not Present":
                dpg.configure_item("popup_enable",show= True)
                dpg.configure_item("popup_disable",show=False)
            else:
                dpg.configure_item("popup_enable",show= False)
                dpg.configure_item("popup_disable",show= True)

    def show(self):
        dpg.show_viewport()

    def clean_up(self):
        dpg.destroy_context()
