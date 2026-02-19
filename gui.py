#gui.py
import dearpygui.dearpygui as dpg
from const import FONTS, UI_CONF
from model import NetworkState
class IPtoolGUI:

    def __init__(self, model: NetworkState):
        self.setup_ui()
        self.model: NetworkState = model


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
        
        dpg.bind_font("Default font")

        with dpg.window(label="",tag="main_window",width=UI_CONF.main_width,height=UI_CONF.main_height):
            self.draw_content()
        
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
        #убираем "▲ "
        app_data = app_data[2:]
        #print(type(self.model.get_ip_list(app_data)), self.model.get_ip_list(app_data))
        dpg.configure_item("IP_listbox",items = self.model.get_ip_list(app_data))
        
    
    #обновление содержимого
    def update_display(self):
        interfaces = self.model.get_all_inetfaces()
        if not interfaces:
            return

        # Обновляем список интерфейсов
        display_names = []
        user_data_indexes = []
        for nic in interfaces:
            display_names.append(f" ▲ {nic.name}" if nic.status == "Up" else f" ▼ {nic.name}")
        names = [nic.name for nic in interfaces]
        dpg.configure_item("NIC_listbox",items=display_names)
        dpg.set_item_user_data("NIC_listbox",names)


    def show(self):
        dpg.show_viewport()

    def clean_up(self):
        dpg.destroy_context()
