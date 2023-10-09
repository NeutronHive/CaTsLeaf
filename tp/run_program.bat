@echo off
setlocal

rem Set the Python version you want to install (e.g., Python 3.9.7)
set PYTHON_VERSION=3.11.1

rem Set the installation directory (change it to your preferred directory)
set INSTALL_DIR=C:\Python%PYTHON_VERSION%

rem Download the Python installer
echo Downloading Python %PYTHON_VERSION%...
curl -o python-installer.exe https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe

rem Install Python
echo Installing Python %PYTHON_VERSION%...
python-installer.exe /quiet InstallAllUsers=1 TargetDir="%INSTALL_DIR%" PrependPath=1

rem Clean up the installer
del python-installer.exe


rem Add Python to the system PATH
setx PATH "%PATH%;%INSTALL_DIR%"

rem Verify Python installation
python --version

echo Python %PYTHON_VERSION% has been successfully installed to %INSTALL_DIR%.
echo You may need to restart your command prompt or IDE to use Python.

endlocal