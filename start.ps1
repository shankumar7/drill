# Set execution policy to bypass to allow loading scripts/venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

$NodePath = "$PSScriptRoot\node-dist\node-v22.23.1-win-x64"
$env:Path = "$NodePath;" + $env:Path

Write-Host "Cleaning up previous backend and frontend instances..." -ForegroundColor Yellow

# Terminate existing backend instances running api.py to release camera locks
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*backend/api.py*" } | ForEach-Object {
    Write-Host "Killing python process $($_.ProcessId)..." -ForegroundColor DarkYellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

# Terminate node processes on port 3000 to clear the dev server
Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.OwningProcess -gt 0) {
        Write-Host "Killing node process $($_.OwningProcess) on port 3000..." -ForegroundColor DarkYellow
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

# Sleep briefly to allow OS to release socket bindings and camera handles
Start-Sleep -Seconds 2

Write-Host "Starting Military Drill backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; . backend\venv\Scripts\Activate.ps1; python backend/api.py"

Write-Host "Starting Next.js frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:Path = '$NodePath;' + `$env:Path; cd web-ui; npm.cmd run dev"

Write-Host "Both servers have been launched in separate windows!" -ForegroundColor Cyan
