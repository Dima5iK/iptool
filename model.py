#model.py
"""Модель данных"""

from logic import NIC,Route
import threading
class NetworkState:
    """Модель сетей"""
    def __init__(self):
        self.interfaces = {}
        self.interfaces_previous_state = {}
        self.route:list[Route] = []
        self._lock = threading.RLock()

    def update_inetfaces(self,new_data:list[NIC]):
        """обновляет состояние интерфейсов"""
        with self._lock:
            self.interfaces_previous_state = self.interfaces
            self.interfaces = {nic.index: nic for nic in new_data}

    def get_rx_speed(self,iface:NIC):

        pass


    