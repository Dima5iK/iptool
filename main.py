#main.py
import logic
import model
import gui
import dearpygui.dearpygui as dpg
import time


def main():
    monitor = logic.PowerShellMonitor()
    network_model = model.NetworkState()
    
    monitor.start()
    ui = gui.IPtoolGUI(network_model)
    ui.show()


    while dpg.is_dearpygui_running():

        if monitor.new_data_flag:
            network_model.update_intefaces(monitor.new_data)
            monitor.new_data_flag = False
            if network_model:
                ui.update_display()
        dpg.render_dearpygui_frame()
        time.sleep(0.02)
    
    ui.clean_up()

if __name__ == "__main__":
    main()