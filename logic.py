#logic.py
"""Классы и методы к ним"""

from const import POWERSHELL_SCAN
import subprocess, threading,json
from model import NIC
import time
import re
from model import Route

def compare_states(prev_state:dict,curr_state:dict) -> bool:
    """Сравниваем прошлое состояние модели и текущее\n
        true - состояние изменилось\n
        false - состояние не изменилось"""

    if prev_state.keys() & curr_state.keys() == curr_state.keys():
        return False
    else:
        return(True)
    pass

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

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def _update_loop(self):
        while self.running:
            routes = self._fetch_routes()
            if routes is not None:
                with self.lock:
                    self.model.routes = routes
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
        """Парсит вывод route print -4 и возвращает список Route."""
        lines = output.splitlines()
        routes = []

        # Ищем строку с заголовками (русская или английская версия)
        header_pattern = re.compile(r'(Сетевой адрес|Network Address)')
        data_start = None
        for i, line in enumerate(lines):
            if header_pattern.search(line):
                data_start = i + 1
                break

        if data_start is None:
            # Если не нашли заголовок, попробуем найти строку, где первое поле похоже на IP
            # или просто начнём с первой непустой строки после "==="
            for i, line in enumerate(lines):
                if line.strip().startswith('==='):
                    data_start = i + 1
                    break
            if data_start is None:
                return []

        # Проходим по строкам до пустой строки или до следующей разделительной линии
        for line in lines[data_start:]:
            line = line.strip()
            if not line or line.startswith('==='):
                break
            parts = line.split()
            # Ожидаем минимум 5 полей: dest, mask, gateway, interface, metric
            if len(parts) >= 5:
                dest, mask, gateway, interface, metric = parts[0], parts[1], parts[2], parts[3], parts[4]
                routes.append(Route(dest, mask, gateway, interface, metric))
            # Иногда строка может содержать "On-link" в качестве шлюза и интерфейс с пробелом?
            # В таком случае split всё равно разобьёт, но может получиться больше частей.
            # Для простоты оставляем как есть.

        return routes