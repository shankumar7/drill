# Set execution policy to bypass to allow loading scripts/venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

Write-Host "Starting Military Drill backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; . backend\venv\Scripts\Activate.ps1; python backend/api.py"

Write-Host "Starting Next.js frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd web-ui; npm run dev"

Write-Host "Both servers have been launched in separate windows!" -ForegroundColor Cyan
