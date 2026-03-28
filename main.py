# main.py
from logic import PowerShellMonitor, NetworkController,compare_states
import model
from gui import MainWindow
import dearpygui.dearpygui as dpg
import time

def main():
    monitor = PowerShellMonitor()
    network_model = model.NetworkState()
    controller = NetworkController()
    frame_time = 0.04

    monitor.start()
    ui = MainWindow(network_model, controller)
    ui.show()

    while dpg.is_dearpygui_running():
        if monitor.new_data_flag :
            network_model.update_interfaces(monitor.new_data)
            monitor.new_data_flag = False
            ui.update_display()

        dpg.render_dearpygui_frame()
        time.sleep(frame_time)

    ui.clean_up()

if __name__ == "__main__":
    main()