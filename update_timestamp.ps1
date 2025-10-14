# PowerShell script to update LAST_UPDATE timestamp
# Run this before git commits to automatically update the timestamp

Write-Host "🕐 Updating LAST_UPDATE timestamp..." -ForegroundColor Yellow

# Get current time in NL timezone
$nl_tz = [System.TimeZoneInfo]::FindSystemTimeZoneById("W. Europe Standard Time")
$current_time = [System.TimeZoneInfo]::ConvertTimeFromUtc([System.DateTime]::UtcNow, $nl_tz)
$formatted_time = $current_time.ToString("dd-MM-yyyy HH:mm:ss")

# Read the current file
$content = Get-Content "trading_journal.py" -Raw

# Update the LAST_UPDATE line using regex
$pattern = 'LAST_UPDATE = "[^"]*"'
$replacement = "LAST_UPDATE = `"$formatted_time`""
$new_content = $content -replace $pattern, $replacement

# Write back to file
Set-Content "trading_journal.py" -Value $new_content -NoNewline

Write-Host "✅ Updated LAST_UPDATE to: $formatted_time" -ForegroundColor Green
