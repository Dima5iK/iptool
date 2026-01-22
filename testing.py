import logic
import time
from model import NetworkState

monitor = logic.PowerShellMonitor()
network_model = NetworkState()

monitor.start()

for iter in range(50):
    time.sleep(0.2)
    if monitor.new_data_flag:
        nics = monitor.new_data
        monitor.new_data_flag = False
        for nic in nics:
            print(nic.description,nic.name, nic.ip_addresses, nic.mac,nic.received_bytes)
        #print(monitor.new_data)
            pass
        print("________________________________")
    print("tick:",iter)


monitor.stop()