import logic
import time


monitor = logic.PowerShellMonitor()


monitor.start()

for iter in range(5):
    time.sleep(1.5)
    nics = monitor.new_data
    for nic in nics:
        print(nic.description,nic.name, nic.ip_addresses, nic.mac)
    #print(monitor.new_data)
        pass
    print("________________________________")
    


monitor.stop()