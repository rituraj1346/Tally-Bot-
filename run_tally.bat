@echo off
echo =========================================
echo TALLY GUI AUTOMATION STARTED: %date% %time%
echo =========================================

cd /d "C:\TallySyncBot"

rem The ">>" captures everything and saves it to a text file in your folder
python run_master_tally_sync.py >> "C:\TallySyncBot\tally_sync_logs.txt" 2>&1

echo Automation Complete!