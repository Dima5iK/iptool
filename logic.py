#logic.py
"""Классы и методы к ним"""

from const import POWERSHELL_SCAN
import subprocess, threading,json
from model import NetworkState, NIC



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
    def cmd_execute(self,cmd):
        """Тсполнение команды в субпроцессе"""
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(cmd, shell=True, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
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
