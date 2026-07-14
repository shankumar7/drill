# Set execution policy to bypass to allow loading scripts/venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

$NodePath = "c:\Users\The Moe\Desktop\drill\node-dist\node-v22.23.1-win-x64"
$env:Path = "$NodePath;" + $env:Path

Write-Host "Starting Military Drill backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; . backend\venv\Scripts\Activate.ps1; python backend/api.py"

Write-Host "Starting Next.js frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:Path = '$NodePath;' + `$env:Path; cd web-ui; npm.cmd run dev"

Write-Host "Both servers have been launched in separate windows!" -ForegroundColor Cyan
