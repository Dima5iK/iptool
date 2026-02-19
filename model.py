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

    def update_intefaces(self,new_data:list[NIC]):
        """обновляет состояние интерфейсов"""
        with self._lock:
            self.interfaces_previous_state = self.interfaces
            self.interfaces = {nic.index: nic for nic in new_data}

    def get_all_inetfaces(self) -> list[NIC]:
        """Возвращает список всех интерфейсов """
        with self._lock:
            return list(self.interfaces.values())
        
    def get_interface_by_name(self, name: str) -> NIC | None:
        """Возвращает интерфейс по указанному имени"""
        with self._lock:
            for nic in self.interfaces.values():
                if nic.name == name:
                    return nic
        return None
    
    def get_interface_prev_state_by_name(self,name:str) -> NIC | None:
        """Возвращает предыдущее состояние интерфейса по имени"""
        with self._lock:
            for nic in self.interfaces_previous_state.values():
                if nic.name == name:
                    return nic
        return None
    
    def get_ip_list(self,interface_name:str) -> list[str]:
        """Возвращает список ip/mask для указанного интерфейса по его имени"""

        with self._lock:
            for nic in self.interfaces.values():
                if nic.name == interface_name:
                    return nic.ip_addresses
        return []
    
    def get_descr(self,interface_name:str) -> str:
        """Возвращает описание интерфейса по"""

    def get_rx_speed(self,iface:NIC):

        pass


    