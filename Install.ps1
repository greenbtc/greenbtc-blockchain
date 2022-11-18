$ErrorActionPreference = "Stop"

if ([Environment]::Is64BitOperatingSystem -eq $false)
{
    Write-Output "Chia requires a 64-bit Windows installation"
    Exit 1
}

if (-not (Get-Item -ErrorAction SilentlyContinue "$env:windir\System32\msvcp140.dll").Exists)
{
    Write-Output "Unable to find Visual C++ Runtime DLLs"
    Write-Output ""
    Write-Output "Download and install the Visual C++ Redistributable for Visual Studio 2019 package from:"
    Write-Output "https://visualstudio.microsoft.com/downloads/#microsoft-visual-c-redistributable-for-visual-studio-2019"
    Exit 1
}

if ($null -eq (Get-Command git -ErrorAction SilentlyContinue))
{
    Write-Output "Unable to find git"
    Exit 1
}



python -m venv venv

venv\scripts\python -m pip install --upgrade pip setuptools wheel
venv\scripts\pip install --extra-index-url https://pypi.chia.net/simple/ miniupnpc==2.2.2
venv\scripts\pip install --editable . --extra-index-url https://pypi.chia.net/simple/

Write-Output ""
Write-Output "Chia blockchain .\Install.ps1 complete."
Write-Output "For assistance join us on Keybase in the #support chat channel:"
Write-Output "https://keybase.io/team/greenbtc_network.public"
Write-Output ""
Write-Output "Try the Quick Start Guide to running greenbtc-blockchain:"
Write-Output "https://github.com/Chia-Network/greenbtc-blockchain/wiki/Quick-Start-Guide"
Write-Output ""
Write-Output "To install the GUI type '.\Install-gui.ps1' after '.\venv\scripts\Activate.ps1'."
Write-Output ""
Write-Output "Type '.\venv\Scripts\Activate.ps1' and then 'greenbtc init' to begin."
