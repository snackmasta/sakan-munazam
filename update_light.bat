@echo off
REM Copy firmware for light_207 and light_208 to Web/OTA directory

set SRC_207=slave\light_207\.pio\build\esp12e\firmware.bin
set SRC_208=slave\light_208\.pio\build\esp12e\firmware.bin
set DEST=Web\OTA

if exist %SRC_207% (
    copy /Y %SRC_207% %DEST%\firmware_light_207.bin
    echo Copied firmware_light_207.bin
) else (
    echo Firmware for light_207 not found: %SRC_207%
)

if exist %SRC_208% (
    copy /Y %SRC_208% %DEST%\firmware_light_208.bin
    echo Copied firmware_light_208.bin
) else (
    echo Firmware for light_208 not found: %SRC_208%
)

pause
