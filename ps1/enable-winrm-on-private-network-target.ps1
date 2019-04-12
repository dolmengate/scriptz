Enable-PSRemoting -Force
# sets all, also use comma-delimited list for specific hosts
Set-Item wsman:\localhost\client\trustedhosts *
Restart-Service WinRM