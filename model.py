#model.py
"""Модель данных"""

from logic import NIC,Route,PowerShellMonitor
import threading
class NetworkState:
    """Модель сетей"""
    def __init__(self):
        self.interfaces = {}
        self.interfaces_previous_state = {}
        self.route:list[Route] = []
        self._lock = threading.RLock()

    def update_inetfaces(self,new_state:list[NIC]):
        """обновляет состояние интерфейсов"""
        self.interfaces_previous_state = self.interfaces
        self.interfaces = new_state
    def get_rx_speed(self,iface:NIC):

        pass
    def get_iface_index_by_name(self,name) -> int:
        """Возваращает индекс указанного интерфейса"""
        for iface in self.interfaces:
            if name == iface.name:
                return iface.index
        return None
    
    