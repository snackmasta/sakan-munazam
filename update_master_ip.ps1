$ErrorActionPreference = "Stop"

# Prompt for new master IP
$newIP = Read-Host "Enter new MASTER IP (format: 192.168.137.1)"

# Prompt for new WiFi SSID and password
$newSSID = Read-Host "Enter new WiFi SSID (leave blank to skip)"
$newPASS = Read-Host "Enter new WiFi Password (leave blank to skip)"

# Convert to comma-separated for IPAddress(...)
$newIP_commas = $newIP -replace '\.', ','

Write-Host "New MASTER IP will be: $newIP"
if ($newSSID) { Write-Host "New WiFi SSID will be: $newSSID" }
if ($newPASS) { Write-Host "New WiFi Password will be: $newPASS" }
Pause

# Get all target files (exclude WiFiUDPHandler.cpp)
$files = Get-ChildItem -Path ".\slave\*\src\main.cpp", ".\slave\*\src\OTAHandler.cpp" -File
Write-Host "[DEBUG] Number of files found: $($files.Count)" -ForegroundColor Magenta

foreach ($file in $files) {
    Write-Host "`n[DEBUG] Processing file: $($file.FullName)" -ForegroundColor Cyan

    # Show original content (first 10 lines)
    Write-Host "[DEBUG] --- Before ---" -ForegroundColor Yellow
    Get-Content $file.FullName | Select-Object -First 10 | ForEach-Object { Write-Host $_ }

    $original = Get-Content -Raw $file.FullName

    # Count matches before replacement
    $count1 = ([regex]::Matches($original, 'IPAddress\(\d{1,3},\d{1,3},\d{1,3},\d{1,3}\)')).Count
    $count2 = ([regex]::Matches($original, '"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"')).Count
    $count3 = ([regex]::Matches($original, '#define WIFI_SSID ".*"')).Count
    $count4 = ([regex]::Matches($original, '#define WIFI_PASSWORD ".*"')).Count

    # Replace IPAddress(...)
    $updated = $original -replace 'IPAddress\(\d{1,3},\d{1,3},\d{1,3},\d{1,3}\)', "IPAddress($newIP_commas)"
    # Replace "a.b.c.d" with quoted new IP
    $replacement = '"' + $newIP + '"'
    $updated = $updated -replace '"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"', $replacement
    # Replace SSID if provided
    if ($newSSID) {
        $ssidReplace = '#define WIFI_SSID "' + $newSSID + '"'
        $updated = $updated -replace '#define WIFI_SSID ".*"', $ssidReplace
        $ssidReplace2 = 'const char* ssid = "' + $newSSID + '";'
        $updated = $updated -replace 'const char\* ssid = ".*";', $ssidReplace2
    }
    # Replace password if provided
    if ($newPASS) {
        $passReplace = '#define WIFI_PASSWORD "' + $newPASS + '"'
        $updated = $updated -replace '#define WIFI_PASSWORD ".*"', $passReplace
        $passReplace2 = 'const char* password = "' + $newPASS + '";'
        $updated = $updated -replace 'const char\* password = ".*";', $passReplace2
    }

    # Save only if changed
    if ($original -ne $updated) {
        Set-Content $file.FullName $updated
        Write-Host "[DEBUG] Replacements made: IPAddress(...) = $count1, \"a.b.c.d\" = $count2, SSID = $count3, PASSWORD = $count4" -ForegroundColor Green
    } else {
        Write-Host "[DEBUG] No replacements made in this file." -ForegroundColor Red
    }

    # Show updated content (first 10 lines)
    Write-Host "[DEBUG] --- After ---" -ForegroundColor Green
    Get-Content $file.FullName | Select-Object -First 10 | ForEach-Object { Write-Host $_ }
}

Write-Host "`n[DEBUG] All done!"
Pause
