@echo off
echo 🕐 Updating LAST_UPDATE timestamp...

REM Run the Python script to update timestamp
python update_timestamp.py

REM Add the updated file to staging
git add trading_journal.py

echo ✅ Timestamp updated and staged for commit
echo.
echo Ready to commit! Use: git commit -m "Your message"
pause
