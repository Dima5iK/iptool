#logic.py
"""Классы и методы к ним"""

from const import POWERSHELL_SCAN
import subprocess, threading,json



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
        self.status:str = status  # "Up"/"Down"
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


class PowerShellMonitor:
    """Класс создает и запускает процесс с источником данных"""
    def __init__(self):
        self.proc = None
        self.new_data:list[NIC] = []  # Сюда будем складывать данные
        self.running = False
        self.lock = threading.Lock()
        self.new_data_flag:bool = False         
        """Флаг новых данных"""

    def _parse_json_to_nics(self, data):
        """реобразует сырой JSON в список объектов NIC"""
        nics:list[NIC] = []
        
        for adapter_data in data:
            raw_ips = adapter_data.get('IPAddress', [])
            if isinstance(raw_ips, dict) and not raw_ips:
                ip_addresses = []
            elif isinstance(raw_ips, str):
                ip_addresses = [raw_ips] if raw_ips else []
            elif isinstance(raw_ips, list):
                ip_addresses = raw_ips
            else:
                ip_addresses = []
            nic = NIC(
                index=adapter_data.get('Index'),
                name=adapter_data.get('Name'),
                description=adapter_data.get('Descrip'),
                #ip_addresses=self.get_IP_obj_from_str(adapter_data.get('IPAddress', [])), слишком сложно
                ip_addresses=ip_addresses,
                mac=adapter_data.get('MacAddress'),
                status=adapter_data.get('Status'),
                speed=str(adapter_data.get('Speed', '0')),
                received_bytes=int(adapter_data.get('ReceivedBytes', 0)),
                sent_bytes=int(adapter_data.get('SentBytes', 0))
            )
            nics.append(nic)
        return nics


    def start(self):
        """Запускает PowerShell с заданным скриптом"""
        self.running = True
        self.proc = subprocess.Popen(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', POWERSHELL_SCAN],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='cp866'
        )
        # Запускаем поток чтения
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        """Читает вывод PowerShell в фоновом потоке"""
        while self.running and self.proc.poll() is None:

            line = self.proc.stdout.readline()
            if line:
                try:
                    json_data = json.loads(line.strip())
                    nic_list:list[NIC] = []
                    #парсинг
                    nic_list = self._parse_json_to_nics(json_data)
                                                               
                    with self.lock:
                        self.new_data = nic_list
                        self.new_data_flag = True
                except json.JSONDecodeError:
                    pass

    

    def stop(self):
        """Останавливает мониторинг"""
        self.running = False
        if self.proc:
            self.proc.terminate()


