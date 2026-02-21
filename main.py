#main.py
from logic import PowerShellMonitor, NetworkController
import model
import gui
import dearpygui.dearpygui as dpg
import time


def main():
    monitor = PowerShellMonitor()
    network_model = model.NetworkState()
    controller = NetworkController()
    frame_time:float = 0.04         #Интервал отрисовки кадров
    monitor.start()
    ui = gui.IPtoolGUI(network_model,controller)
    ui.show()


    while dpg.is_dearpygui_running():

        if monitor.new_data_flag:
            network_model.update_intefaces(monitor.new_data)
            monitor.new_data_flag = False
            if network_model:
                ui.update_display()
                
                
        dpg.render_dearpygui_frame()
        
        time.sleep(frame_time)
    
    ui.clean_up()

if __name__ == "__main__":
    main()