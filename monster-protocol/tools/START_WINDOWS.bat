@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0start_demo.py" goto missing_files

py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 goto run_py
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 goto run_python

echo Python 3.10 or newer was not found.
echo Install Python, or open project\game.json in GDevelop and click Preview.
echo In the Teacher archive, open demo\game.json instead.
goto done

:run_py
py -3 "%~dp0start_demo.py" --port 0
goto done

:run_python
python "%~dp0start_demo.py" --port 0
goto done

:missing_files
echo start_demo.py is missing. Extract the ENTIRE archive before running this file.

:done
pause
endlocal
