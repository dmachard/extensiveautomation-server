:: -------------------------------------------------------------------
:: Copyright (c) 2010-2018 Denis Machard
:: This file is part of the extensive automation project
::
:: This library is free software; you can redistribute it and/or
:: modify it under the terms of the GNU Lesser General Public
:: License as published by the Free Software Foundation; either
:: version 2.1 of the License, or (at your option) any later version.
::
:: This library is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
:: Lesser General Public License for more details.
::
:: You should have received a copy of the GNU Lesser General Public
:: License along with this library; if not, write to the Free Software
:: Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
:: MA 02110-1301 USA
:: -------------------------------------------------------------------

@echo off

:: output folder
set Path_Output="D:\My Lab\outputs"

:: init paths
set Path_Project=%~dp0..\..\
set Path_Python=C:\Python36

:: init tools path
set Tool_Python=%Path_Python%\python.exe
set Tool_PyInstaller=%Path_Python%\Scripts\pyinstaller.exe

:: normalize paths
CALL :NORMALIZEPATH %Path_Output%
SET Path_Output=%RETVAL%
IF "%Path_Output:~-1%"=="\" SET Path_Output=%Path_Output:~0,-1%

:: make resources
%Tool_Python% -m PyQt5.pyrcc_main -o "%Path_Project%\Resources\Resources.py" "%Path_Project%\Resources\__resources.qrc"

:: build the project
echo Starting to build the project...
cd "%Path_Project%"
%Tool_Python% "%Path_Project%\ConfigureExe.py"
%Tool_PyInstaller% --clean --noconfirm BuildWinIns.spec

:: build the installer
echo Build the installer...
"%Tool_Python%" "%Path_Project%\BuildWinInno.py" "%Path_Output%" "%Path_Project%\dist\ExtensiveAutomationClient"

:: pause before exit the prompt
pause

:: function to normalize path
:NORMALIZEPATH
  SET RETVAL=%~dpfn1
  EXIT /B