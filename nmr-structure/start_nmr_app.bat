@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] The virtual environment was not found.
  echo Run: python -m venv .venv
  pause
  exit /b 1
)

echo Starting NMR Structure Finder...
".venv\Scripts\python.exe" -m streamlit run app.py

if errorlevel 1 (
  echo.
  echo The app could not start. Install dependencies with:
  echo .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
)
