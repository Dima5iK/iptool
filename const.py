#const.py
"""различные статичные величины и выражения"""



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