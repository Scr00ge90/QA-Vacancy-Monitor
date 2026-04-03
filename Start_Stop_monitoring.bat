@echo off
chcp 65001 > nul
title QA Telegram Monitor

set "BASE_DIR=%~dp0"
set "PYTHON=C:\Users\vpak9\AppData\Local\Python\bin\python.exe"
set "SCRIPT=%BASE_DIR%monitor.py"
set "PID_FILE=%BASE_DIR%monitor_pid.txt"
set "LOG_DIR=%BASE_DIR%logs"

:MENU
cls
echo ==============================
echo       QA Telegram Monitor
echo ==============================
echo 1. Zapustit skript
echo 2. Ostanovit skript
echo 3. Log za segodnya
echo 4. Status
echo 5. Otkryt papku s logami
echo 6. Vyhod
echo ==============================
set /p choice=Choice: 

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto LOG_TODAY
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto OPEN_LOGS
if "%choice%"=="6" exit
goto MENU

:START
if exist "%PID_FILE%" (
    set /p EXISTING_PID=<"%PID_FILE%"
    echo Skript uzhe zapushchen.
    pause
    goto MENU
)
echo Zapusk...
start "QA Monitor" "%PYTHON%" "%SCRIPT%"
echo Skript zapushchen.
pause
goto MENU

:STOP
if not exist "%PID_FILE%" (
    echo Skript ne zapushchen.
    pause
    goto MENU
)
set /p PID=<"%PID_FILE%"
echo Ostanovka PID %PID%...
taskkill /PID %PID% /F /T > nul 2>&1
if exist "%PID_FILE%" del "%PID_FILE%"
echo Ostanovleno.
pause
goto MENU

:LOG_TODAY
set "TODAY=%date:~0,4%-%date:~5,2%-%date:~8,2%"
set "LOG_FILE=%LOG_DIR%\sent_log_%TODAY%.txt"
if exist "%LOG_FILE%" (
    type "%LOG_FILE%"
) else (
    echo Log za segodnya ne najden.
)
pause
goto MENU

:STATUS
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    echo [STATUS] Skript rabotaet - PID: %PID%
) else (
    echo [STATUS] Skript ne zapushchen
)
set "TODAY=%date:~0,4%-%date:~5,2%-%date:~8,2%"
set "LOG_FILE=%LOG_DIR%\sent_log_%TODAY%.txt"
if exist "%LOG_FILE%" (
    for /f %%a in ('type "%LOG_FILE%" ^| find /c /v ""') do echo [LOG] Otklikov segodnya: %%a
) else (
    echo [LOG] Segodnya otklikov ne bylo
)
pause
goto MENU

:OPEN_LOGS
if exist "%LOG_DIR%" (
    explorer "%LOG_DIR%"
) else (
    echo Papka logov ne najdena.
)
pause
goto MENU
