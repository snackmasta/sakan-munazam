# Build light_207 firmware
Write-Host "Building light_207 firmware..."
Set-Location "slave/light_207"
platformio run
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed for light_207"
    Pause
    exit $LASTEXITCODE
}
Set-Location ../..

# Build light_208 firmware
Write-Host "Building light_208 firmware..."
Set-Location "slave/light_208"
platformio run
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed for light_208"
    Pause
    exit $LASTEXITCODE
}
Set-Location ../..

Write-Host "Both builds completed."
Pause
