# Trading Journal Pro - Keep Awake Mode (PowerShell)
# This script starts the Trading Journal with sleep prevention

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Trading Journal Pro - Keep Awake Mode" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Keep-Alive System..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "keep_awake.py" -WindowStyle Minimized

Write-Host "Waiting 3 seconds for keep-alive to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "Starting Trading Journal Pro..." -ForegroundColor Green
Write-Host ""
Write-Host "The system will stay awake while Trading Journal is running." -ForegroundColor Cyan
Write-Host "Close this window to stop both the app and keep-alive system." -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
& streamlit run trading_journal.py --server.headless true --server.port 8501

Write-Host ""
Write-Host "Stopping Keep-Alive System..." -ForegroundColor Yellow

# Stop keep-alive process
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*Keep-Alive*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Trading Journal Pro stopped." -ForegroundColor Red
Read-Host "Press Enter to exit"
