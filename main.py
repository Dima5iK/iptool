# main.py
from logic import PowerShellMonitor, NetworkController,compare_states, RouteMonitor
import model
from gui import MainWindow
import dearpygui.dearpygui as dpg
import time
import const
def main():
    monitor = PowerShellMonitor()
    
    network_model = model.NetworkState()
    route_monitor = RouteMonitor(network_model, interval=const.rote_scan_interval)
    controller = NetworkController()
    frame_time = 0.04

    monitor.start()
    route_monitor.start()
    #инициализация основного окна, вкладок, шрифтов и тд
    ui = MainWindow(network_model, controller)
    ui.show()

    #цикл опроса сетевых интерфейсов и обновления данных 
    while dpg.is_dearpygui_running():
        if monitor.new_data_flag :
            network_model.update_interfaces(monitor.new_data)
            monitor.new_data_flag = False
            if compare_states(network_model.interfaces_previous_state,network_model.interfaces):
                ui.update_display()

    # Обновление маршрутов (можно отдельно, если нужно)
        if route_monitor.new_data_flag:
            network_model.routes = route_monitor.new_data
            route_monitor.new_data_flag = False
            # Можно обновить только вкладку Route, но для простоты вызываем общее обновление
            if network_model._is_routes_changed():
                ui.update_display()

        dpg.render_dearpygui_frame()
        time.sleep(frame_time)

    ui.clean_up()

if __name__ == "__main__":
    main()