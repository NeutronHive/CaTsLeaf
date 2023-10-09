@echo off
setlocal enabledelayedexpansion

rem Define the URL to the Nmap installer
set "nmap_url=https://nmap.org/dist/nmap-7.94-setup.exe"

rem Define the installation directory
set "install_dir=C:\Program Files\Nmap"

rem Download the Nmap installer
echo Downloading Nmap installer...
curl -o nmap-setup.exe "%nmap_url%"

rem Install Nmap silently
echo Installing Nmap...
start /wait nmap-setup.exe /S

rem Check if the installation was successful
if exist "%install_dir%\nmap.exe" (
    echo Nmap has been installed successfully.
    rem Add Nmap to the system PATH
    setx PATH "%PATH%;%install_dir%" /M
    echo Nmap has been added to the system PATH.
) else (
    echo Failed to install Nmap. Please check the installation.
)

rem Clean up the installer
del nmap-setup.exe

endlocal
