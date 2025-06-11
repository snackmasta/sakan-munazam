# This PowerShell script copies the latest built lock and light firmware to the OTA directory with the correct filenames.

$ErrorActionPreference = 'Stop'

# Define source and destination paths
$firmwares = @(
    @{ src = "slave/light_207/.pio/build/esp12e/firmware.bin"; dest = "Web/OTA/firmware_light_207.bin" },
    @{ src = "slave/light_208/.pio/build/esp12e/firmware.bin"; dest = "Web/OTA/firmware_light_208.bin" },
    @{ src = "slave/lock_207/.pio/build/esp12e/firmware.bin"; dest = "Web/OTA/firmware_lock_207.bin" },
    @{ src = "slave/lock_208/.pio/build/esp12e/firmware.bin"; dest = "Web/OTA/firmware_lock_208.bin" }
)

foreach ($fw in $firmwares) {
    if (Test-Path $fw.src) {
        Copy-Item -Path $fw.src -Destination $fw.dest -Force
        Write-Host "Copied $($fw.src) to $($fw.dest)"
    } else {
        Write-Host "Source firmware not found: $($fw.src)"
    }
}

Write-Host "Firmware copy to OTA directory completed."
Pause
