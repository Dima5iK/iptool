#const.py
"""различные статичные величины и выражения"""

# путь шрифта
class FONTS:
    FONT_TAHOMA  ='C:\\Windows\\Fonts\\Tahoma.ttf'


#размеры 
class UI_CONF:
    version:float = 0.2
    main_width = 800
    main_height = 400
    
    #id  вкладок
    ip_tab_id = 1000
    route_tab_id = 1001
    
    #параметры lisbox в ip_tab_id
    item_num = 8
    help_text = ''' ▲ - linkUp \t ▼ - linkDown \t пусто - admin status disable\n Управление: \n Стелки вверх/вниз - перемещение по устройствам или адресам (можно курсором) \n Стрелки влео/вправо - перелючение между колонками 
 NumPad - ввод адреса\n Enter - задать ip-адрес\n Delete - удалить выбранный адрес\n ПКМ по устройству - переключить на DHCP(статические ip удаяются)\nv{}'''.format(version)


#логические константы

POWERSHELL_SCAN_TEMPLATE  = '''
while ($true) {{
    $result = Get-NetAdapter | ForEach-Object {{
    $adapter = $_
    $stats = $_ | Get-NetAdapterStatistics -ErrorAction SilentlyContinue
    
    # Получаем IPv4 адреса
    $ipAddresses = @()
    $ipConfigs = Get-NetIPAddress -InterfaceIndex $adapter.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue |
                 Where-Object {{$_.PrefixOrigin -ne 'WellKnown'}}
    
    if ($ipConfigs) {{
        foreach ($ip in $ipConfigs) {{
            # Формат: IP/PrefixLength (например, 192.168.1.10/24)
            $ipAddresses += "$($ip.IPAddress)/$($ip.PrefixLength)"
        }}
    }}
    
    [PSCustomObject]@{{
        Index			= $adapter.InterfaceIndex
        Name            = $adapter.Name
        Descrip         = $adapter.InterfaceDescription
		IPAddress       = if ($ipAddresses.Count -gt 0) {{ $ipAddresses }} else {{ @() }}
        MacAddress      = $adapter.MacAddress
        Status          = $adapter.Status
        Speed           = if($adapter.Speed) {{$adapter.Speed}} else {{"0"}}
        ReceivedBytes   = if ($stats) {{ $stats.ReceivedBytes }} else {{ "0" }}
        SentBytes       = if ($stats) {{ $stats.SentBytes }} else {{ "0" }}
        
    }}
}} | ConvertTo-Json -Compress

Write-Output $result
    Start-Sleep -Seconds {interval}
}}
'''
scan_interval = 1
POWERSHELL_SCAN = POWERSHELL_SCAN_TEMPLATE.format(interval = scan_interval)