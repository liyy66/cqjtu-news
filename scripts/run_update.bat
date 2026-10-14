@echo off
chcp 65001 >NUL
setlocal
set PY=C:\Users\td\.workbuddy\binaries\python\envs\default\Scripts\python.exe
set PYTHONIOENCODING=utf-8
cd /d C:\Users\td\WorkBuddy\2026-10-12-22-31-04
echo === crawl start %date% %time% ===
"%PY%" scripts\crawl_news.py front
"%PY%" scripts\daily_update.py
echo === crawl done %date% %time% ===
endlocal