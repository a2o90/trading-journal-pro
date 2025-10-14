@echo off
echo ========================================
echo   Trading Journal Pro - Keep Awake Mode
echo ========================================
echo.

echo Starting Keep-Alive System...
start "Keep-Alive" python keep_awake.py

echo Waiting 5 seconds for keep-alive to initialize...
timeout /t 5 /nobreak >nul

echo Starting Trading Journal Pro...
echo.
echo The system will stay awake while Trading Journal is running.
echo Close this window to stop both the app and keep-alive system.
echo.

streamlit run trading_journal.py --server.headless true --server.port 8501

echo.
echo Stopping Keep-Alive System...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Keep-Alive*" >nul 2>&1

echo.
echo Restoring sleep settings...
powercfg /change standby-timeout-ac 30 >nul 2>&1

echo.
echo Trading Journal Pro stopped.
pause
