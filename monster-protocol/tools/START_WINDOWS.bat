@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 start_demo.py
  goto done
)
where python >nul 2>nul
if not errorlevel 1 (
  python start_demo.py
  goto done
)
echo Python не найден. Откройте game.json из папки project или demo в GDevelop и нажмите Предпросмотр.
:done
pause
