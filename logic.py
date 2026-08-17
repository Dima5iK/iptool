#logic.py
"""Классы и методы к ним"""

from const import POWERSHELL_SCAN
import subprocess, threading,json
from model import NIC, Route
import time
import re
from model import Route

def compare_states(prev_state: dict, curr_state: dict) -> bool:
    """Возвращает True, если состояние изменилось (набор имён или любые значимые поля)"""
    # Проверяем набор ключей
    if set(prev_state.keys()) != set(curr_state.keys()):
        return True

    # Для каждого интерфейса сравниваем значимые поля
    for name, curr_nic in curr_state.items():
        prev_nic = prev_state.get(name)
        if prev_nic is None:
            return True  # такого не должно быть, но на всякий случай
        # Сравниваем поля (можно добавить и другие)
        if (curr_nic.ip_addresses != prev_nic.ip_addresses or
            curr_nic.status != prev_nic.status or
            curr_nic.speed != prev_nic.speed or
            curr_nic.description != prev_nic.description or
            curr_nic.mac != prev_nic.mac or
            curr_nic.received_bytes != prev_nic.received_bytes or
            curr_nic.sent_bytes != prev_nic.sent_bytes):
            return True

    return False

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
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        self.proc = subprocess.Popen(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', POWERSHELL_SCAN],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='cp866',
            startupinfo=startupinfo
        )
        # Запускаем поток чтения
        threading.Thread(target=self._iface_reader, daemon=True).start()

    def _iface_reader(self):
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

class NetworkController:
    """Здесь описаны команды управления"""
    def cmd_execute(self, args:list):
        """Тсполнение команды в субпроцессе"""
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(args, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def verify_ip(self,ip_cidr:str) -> bool:
        """проверка корректности адреса"""
        try:
            if '/' not in ip_cidr:
                return False
            ip,cidr = ip_cidr.split('/')
            try:
                int_cidr = int(cidr)
                if int_cidr < 0 or int_cidr > 32:
                    return False
            except ValueError:
                return False
            
            ancd = ip.split('.')
            if( len (ancd) != 4):
                return False
            for octet in ancd:
                if not octet:
                    return False
                int_octet = int(octet)
                if int_octet < 0 or int_octet > 255:
                    return False
            return True

        except(ValueError,AttributeError):
            return False
    
    def cidr_to_mask(self,cidr:str):
        """Преобразуем бинарную маску в формат 255.255.255.0"""
        
        mask_bin = (0xFFFFFFFF << (32 - int(cidr))) & 0xFFFFFFFF
        # Преобразуем бинарную маску в формат 255.255.255.0
        return ".".join([str((mask_bin >> (24 - i * 8)) & 0xFF) for i in range(4)])

    def add_ip(self,interface:str,ip_cidr:str):
        if self.verify_ip(ip_cidr):
            ip,cidr = ip_cidr.split('/')
            mask = self.cidr_to_mask(cidr)
            cmd = ('netsh interface ipv4 add address "{}" {} {}'.format(interface,ip,mask))
            self.cmd_execute(cmd)

    def del_ip(self,interface:str,ip_cidr:str):
        if '/' in ip_cidr:
            ip,cidr = ip_cidr.split('/')
            cmd = ('netsh interface ipv4 del address "{}" {}'.format(interface,ip))
            self.cmd_execute(cmd)
        else:
            return None
    def set_dhcp(self,interface:str):
        cmd = ('netsh interface ip set address "{}" dhcp'.format(interface))
        self.cmd_execute(cmd)

    def enable_interface(self,interface_name:str):
        cmd = ('netsh interface set interface "{}" admin=enable'.format(interface_name))
        self.cmd_execute(cmd)

    def disable_interface(self,interface_name:str):
        cmd = ('netsh interface set interface "{}" admin=disable'.format(interface_name))
        self.cmd_execute(cmd)


class RouteMonitor:
    def __init__(self, model, interval: int = 5):
        self.model = model
        self.interval = interval
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.new_data_flag = False          # флаг, что маршруты обновились
        self.new_data:list[Route] = []
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._route_reader, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _route_reader(self):
        while self.running:
            routes = self._fetch_routes()
            if routes is not None:
                with self.lock:
                    self.new_data = routes
                    #self.model.routes = routes
                    self.new_data_flag = True
            time.sleep(self.interval)

    def _fetch_routes(self):
        """Выполняет route print -4 и возвращает список объектов Route или None при ошибке."""
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(
                ['route', 'print', '-4'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='cp866',          # кодировка консоли Windows
                startupinfo=startupinfo
            )
            stdout, stderr = proc.communicate(timeout=10)
            if proc.returncode != 0:
                return None
            return self._parse_route_output(stdout)
        except Exception:
            return None


    def _parse_route_output(self, output: str) -> list[Route]:
        # Регулярка для строк, начинающихся с IP-адреса (четыре октета)
        ip_pattern = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+')
        routes = []
        persistent_section = False

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            # Определяем начало секции постоянных маршрутов
            if 'Постоянные маршруты:' in line:
                persistent_section = True
                continue

            # Пропускаем разделители и строки без IP в начале
            if not ip_pattern.match(line):
                continue

            parts = line.split()

            # --- Активные маршруты (5 полей) ---
            if not persistent_section and len(parts) >= 5:
                dest, mask, gateway, interface, metric = parts[0], parts[1], parts[2], parts[3], parts[4]
                if not self._is_ignored_route(dest, mask):
                    routes.append(Route(dest, mask, gateway, interface, metric))

            # --- Постоянные маршруты (4 поля, последнее может содержать пробелы) ---
            elif persistent_section and len(parts) >= 4:
                dest, mask, gateway = parts[0], parts[1], parts[2]
                # Объединяем всё, что после gateway, в одну строку (метрика)
                metric = ' '.join(parts[3:])
                if not self._is_ignored_route(dest, mask):
                    routes.append(Route(dest, mask, gateway, "Persistent", metric))

        return routes
    
    def _is_ignored_route(self, dest: str, mask: str) -> bool:
        """Возвращает True, если маршрут служебный и его нужно исключить"""
        ignored = {
            ("127.0.0.0", "255.0.0.0"),
            ("127.0.0.1", "255.255.255.255"),
            ("127.255.255.255", "255.255.255.255"),
            ("169.254.0.0", "255.255.0.0"),
            ("224.0.0.0", "240.0.0.0"),
            ("255.255.255.255", "255.255.255.255"),
        }
        if (dest, mask) in ignored:
            return True
        # Дополнительно отсеиваем /32 адреса из 169.254.0.0/16
        if dest.startswith("169.254.") and mask == "255.255.255.255":
            return True
        return False