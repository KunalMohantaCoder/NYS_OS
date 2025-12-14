@echo off
echo Fixing dependencies for Python 3.14 compatibility...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install/upgrade urllib3 to latest version (compatible with Python 3.14)
python -m pip install --upgrade "urllib3>=2.0.0"

REM Install/upgrade requests
python -m pip install --upgrade "requests>=2.31.0"

REM Install other dependencies
python -m pip install -r requirements.txt

echo.
echo Dependencies updated!
echo You may need to restart your terminal/IDE for changes to take effect.
pause

