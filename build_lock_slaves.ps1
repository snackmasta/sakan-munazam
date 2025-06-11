# Build lock_207 firmware
Write-Host "Building lock_207 firmware..."
Set-Location "slave/lock_207"
platformio run
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed for lock_207"
    Pause
    exit $LASTEXITCODE
}
Set-Location ../..

# Build lock_208 firmware
Write-Host "Building lock_208 firmware..."
Set-Location "slave/lock_208"
platformio run
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed for lock_208"
    Pause
    exit $LASTEXITCODE
}
Set-Location ../..

Write-Host "Both builds completed."
Pause
