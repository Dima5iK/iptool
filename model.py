#model.py
"""Модель данных"""

from logic import NIC,Route,PowerShellMonitor
import threading
class NetworkState:
    """Модель сетей"""
    def __init__(self):
        self.interfaces:list[NIC] = []
        self.route:list[Route] = []
        self._lock = threading.RLock()


    def get_iface_index_by_name(self,name) -> int:
        """Возваращает индекс указанного интерфейса"""
        for iface in self.interfaces:
            if name == iface.name:
                return iface.index
        return None
        