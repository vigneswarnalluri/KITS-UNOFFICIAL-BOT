# PowerShell cleanup script for the bot
Write-Host "🧹 Starting bot cleanup..." -ForegroundColor Green

# Stop the bot if it's running
$botProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*main.py*" -or $_.CommandLine -like "*main.py*" }
if ($botProcesses) {
    Write-Host "⚠️ Bot is currently running. Please stop it first before cleaning up." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C in the bot terminal to stop it, then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to continue anyway (files in use may not be deleted)"
}

# Remove session files
$sessionFiles = Get-ChildItem -Path "." -Filter "KITS_BOT_*.session*" -ErrorAction SilentlyContinue
foreach ($file in $sessionFiles) {
    try {
        Remove-Item $file.FullName -Force
        Write-Host "✅ Removed: $($file.Name)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Could not remove: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Remove log files
$logFiles = Get-ChildItem -Path "." -Filter "*.log" -ErrorAction SilentlyContinue
foreach ($file in $logFiles) {
    try {
        Remove-Item $file.FullName -Force
        Write-Host "✅ Removed: $($file.Name)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Could not remove: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Remove __pycache__ directories
$pycacheDirs = Get-ChildItem -Path "." -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue
foreach ($dir in $pycacheDirs) {
    try {
        Remove-Item $dir.FullName -Recurse -Force
        Write-Host "✅ Removed: $($dir.Name)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Could not remove: $($dir.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "🎉 Cleanup complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"
