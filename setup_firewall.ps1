# Script must be run as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    Break
}

# Configure firewall for all profiles
Write-Host "Configuring firewall profiles..." -ForegroundColor Green

# Get the ICS adapter's name and IP
$icsAdapter = Get-NetAdapter | Where-Object { $_.Name -like "*Local Area Connection* 13*" }
$icsIP = Get-NetIPAddress -InterfaceIndex $icsAdapter.ifIndex -AddressFamily IPv4

Write-Host "Configuring for ICS adapter: $($icsAdapter.Name) with IP: $($icsIP.IPAddress)" -ForegroundColor Cyan

# Configure profiles to be more permissive for ICS
$profiles = @('Public', 'Private', 'Domain')
foreach ($profile in $profiles) {
    Set-NetFirewallProfile -Profile $profile -Enabled True -DefaultInboundAction Block -DefaultOutboundAction Allow
    # Enable specific features for better connectivity
    Set-NetFirewallProfile -Profile $profile -AllowInboundRules True -AllowLocalFirewallRules True -AllowUnicastResponseToMulticast True -NotifyOnListen True
}

# Function to create or update firewall rules
function Set-FirewallRule {
    param(
        [string]$DisplayName,
        [string]$Direction,
        [string]$Protocol,
        [int]$Port,
        [string]$Description
    )
    
    # Remove existing rule if it exists
    Remove-NetFirewallRule -DisplayName $DisplayName -ErrorAction SilentlyContinue    # Create new rule with ICS-specific network access
    New-NetFirewallRule -DisplayName $DisplayName `
        -Direction $Direction `
        -Protocol $Protocol `
        -LocalPort $Port `
        -RemotePort Any `
        -LocalAddress $icsIP.IPAddress `
        -RemoteAddress Any `
        -Enabled True `
        -Action Allow `
        -Profile Public,Private,Domain `
        -InterfaceType Any `
        -Program Any `
        -Service Any `
        -EdgeTraversalPolicy Allow `
        -Description $Description
}

Write-Host "Setting up firewall rules for Sakan Munazam..." -ForegroundColor Green

# UDP Rules for IoT Device Communication (Port 4210)
Write-Host "Creating UDP rules for IoT devices..." -ForegroundColor Cyan
Set-FirewallRule -DisplayName "Sakan-UDP-In" -Direction Inbound -Protocol UDP -Port 4210 -Description "Allow incoming UDP communication for IoT devices"
Set-FirewallRule -DisplayName "Sakan-UDP-Out" -Direction Outbound -Protocol UDP -Port 4210 -Description "Allow outgoing UDP communication for IoT devices"

# HTTP Rules for OTA Updates (Port 3000)
Write-Host "Creating HTTP rules for OTA updates..." -ForegroundColor Cyan
Set-FirewallRule -DisplayName "Sakan-OTA-HTTP-In" -Direction Inbound -Protocol TCP -Port 3000 -Description "Allow incoming HTTP for OTA updates"
Set-FirewallRule -DisplayName "Sakan-OTA-HTTP-Out" -Direction Outbound -Protocol TCP -Port 3000 -Description "Allow outgoing HTTP for OTA updates"

# HTTP/HTTPS Rules for Web Interface (Ports 80, 443)
Write-Host "Creating HTTP/HTTPS rules for web interface..." -ForegroundColor Cyan
Set-FirewallRule -DisplayName "Sakan-Web-HTTP-In" -Direction Inbound -Protocol TCP -Port 80 -Description "Allow incoming HTTP for web interface"
Set-FirewallRule -DisplayName "Sakan-Web-HTTP-Out" -Direction Outbound -Protocol TCP -Port 80 -Description "Allow outgoing HTTP for web interface"
Set-FirewallRule -DisplayName "Sakan-Web-HTTPS-In" -Direction Inbound -Protocol TCP -Port 443 -Description "Allow incoming HTTPS for web interface"
Set-FirewallRule -DisplayName "Sakan-Web-HTTPS-Out" -Direction Outbound -Protocol TCP -Port 443 -Description "Allow outgoing HTTPS for web interface"

Write-Host "`nFirewall rules have been created successfully!" -ForegroundColor Green
Write-Host "The following ports are now open for all networks:" -ForegroundColor Yellow
Write-Host "- UDP 4210 (IoT Device Communication)" -ForegroundColor Yellow
Write-Host "- TCP 3000 (OTA Updates)" -ForegroundColor Yellow
Write-Host "- TCP 80   (HTTP Web Interface)" -ForegroundColor Yellow
Write-Host "- TCP 443  (HTTPS Web Interface)" -ForegroundColor Yellow
