import logic
import time
from model import NetworkState

monitor = logic.PowerShellMonitor()
network_model = NetworkState()

monitor.start()

for iter in range(100):
    time.sleep(0.2)
    if monitor.new_data_flag:
        network_model.update_inetfaces(monitor.new_data)
        monitor.new_data_flag = False
        



monitor.stop()