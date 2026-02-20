#gui.py
import dearpygui.dearpygui as dpg
from const import FONTS, UI_CONF
from model import NetworkState
class IPtoolGUI:

    def __init__(self, model: NetworkState):
        
        self.focused = "NIC_listbox"
        """Переменная которая хранит название элемента который сейчас обрабатывается"""
        self.model: NetworkState = model
        self.setup_ui()
        

    
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
                print(type(user_date),user_date)
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
            elif direction == -1:
                return None         #Возможно можно что то добавить сюда в будущем
        elif self.focused == "IP_listbox":
            if direction == -1:
                self.focused = "NIC_listbox"
            elif direction == 1:
                return None         #Сюда тоже
        
        
    def _update_description(self, text):
        dpg.set_value("info_descr", text)

    def _update_mac(self, mac):
        dpg.set_value("info_mac", mac)

    def _update_speed(self, speed):
        """Скорость интерфейса"""
        speed = self._format_speed(speed)
        dpg.set_value("info_speed", speed)
    
    def _format_speed(self, bps):
        """Форматирование скорости в Гб/с, Мб/с или Кб/с"""
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
        last_sec_speed = self._format_speed(last_sec_speed)
        dpg.set_value("info_rx", last_sec_speed)
        
    def _update_tx(self, bytes_val, prev_bytes_val):

        last_sec_speed = bytes_val - prev_bytes_val
        last_sec_speed = self._format_speed(last_sec_speed)
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


    def setup_ui(self):
        """Инициализация DPG, шрифтов и контекста"""
        dpg.create_context()
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
        dpg.create_viewport(title="IPtool",height=UI_CONF.main_height,width=UI_CONF.main_width)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window",True)
    
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
                        width= UI_CONF.main_width*0.5,
                        callback=self.show_detail
                    )
                    dpg.add_listbox(
                        tag="IP_listbox",
                        num_items=UI_CONF.item_num,
                        width=UI_CONF.main_width*0.45
                    )
                #загрушка для верстки
                plug1 = dpg.add_text(default_value="",tag="plug1")
                dpg.bind_item_font(plug1,self.smaller_font)
                #описание/мак
                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="info_descr",default_value="описание",readonly=True,width=UI_CONF.main_width*0.60)
                    dpg.add_input_text(tag="info_mac",default_value="MAC",readonly=True,width=UI_CONF.main_width*0.33)
                #скорость/передано/получено

                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="info_speed",readonly=True, default_value="скорость",width=UI_CONF.main_width*0.24)
                    dpg.add_input_text(tag="info_rx",readonly=True, default_value="RX",width=UI_CONF.main_width*0.35)
                    dpg.add_input_text(tag="info_tx",readonly=True, default_value="TX",width=UI_CONF.main_width*0.33)
                
                #Отрисовка знака вопроса
                hlp = dpg.add_text(default_value='?',tag="help")
                dpg.bind_item_font(hlp,self.bigger_font)
                with dpg.tooltip("help"):
                    dpg.add_text(default_value=UI_CONF.help_text,tag="hlp_tooltip")
                dpg.bind_item_font("hlp_tooltip",self.smaller_font)
                dpg.set_item_pos("help",[int(UI_CONF.main_width*0.93),int(UI_CONF.main_height*0.8)])
        



            with dpg.tab(label="Route",tag=UI_CONF.route_tab_id):
                pass
    
    #callback
    def show_detail(self, sender, app_data, user_data):
        """Показывает детали IP, описание и тд"""
        # app_data — выбранная строка с префиксом (например, "▲ Ethernet")
        clean_name = app_data[2:]  # убираем первые два символа (стрелка и пробел)
        

        # Обновляем текстовые поля
        self._update_details_for_interface(clean_name)
        

        #print(type(self.model.get_ip_list(app_data)), self.model.get_ip_list(app_data))
        #dpg.configure_item("IP_listbox",items = self.model.get_ip_list(app_data))
    
    def key_press_callback(self,sendef,key):
        """Обработка всех доступных нажатий с вызовом соответсвующих методов"""
        if key == dpg.mvKey_Up:
            self._vertical_move_selection(-1)
        elif key == dpg.mvKey_Left:
            self._horizontal_move_selection(-1)
            print(self.focused)
        elif key == dpg.mvKey_Right:
            self._horizontal_move_selection(1)
            print(self.focused)
        elif key == dpg.mvKey_Down:
            self._vertical_move_selection(1)
        elif key == dpg.mvKey_Delete:
            pass
        elif key == dpg.mvKey_Back and (1000 == dpg.get_value('main_tab_bar')):
            pass
        
    
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
