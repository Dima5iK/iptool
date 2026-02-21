#model.py
"""Модель данных"""

import threading

class IP:
    """Слишком сложно, не используется"""
    def __init__(self, ip:str, cidr:str):
        self.ip:str = ip
        self.cidr:str = str(cidr)
    
    def get_ip(self) -> str:
        return self.ip
    
    def get_cidr(self) -> str:
        return self.cidr
    
class NIC:
    def __init__(self, index:int, name:str, description:str, ip_addresses:list[str], 
                 mac:str, status:str, speed:int, received_bytes:int, sent_bytes:int):
        self.index:int = index
        self.name:str = name
        self.description = description
        self.ip_addresses:list[str] = ip_addresses  # Список строк
        self.mac:str = mac
        self.status:str = status  # "Up"/"Down/Disable"
        self.speed:int = int(speed)
        self.received_bytes:int = int(received_bytes)
        self.sent_bytes:int = int(sent_bytes)

    def get_ip_cidr(self):
        return self.ip_addresses.get_ip() + '/' + self.ip_addresses.get_cidr()
    

class Route:
    def __init__(self, destination, mask, gateway,  metric):
        self.destination:str = destination
        self.mask:str = mask                # "255.255.255.0" или CIDR 24
        self.gateway:str = gateway          # "192.168.1.1" или "On-link"
        self.metric:str = metric



    def get_route(self) -> str:
        """возвращает полную строку destination, mask, gateway,  metric"""
        return (self.destination + self.mask + self.gateway + self.metric)


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
            self.interfaces = {nic.name: nic for nic in new_data}

    def get_all_inetfaces(self) -> list[NIC]:
        """Возвращает список всех интерфейсов """
        with self._lock:
            return list(self.interfaces.values())
        
    def get_interface_by_name(self, name: str) -> NIC | None:
        """Возвращает интерфейс по указанному имени"""
        with self._lock:
            return self.interfaces.get(name)
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


    