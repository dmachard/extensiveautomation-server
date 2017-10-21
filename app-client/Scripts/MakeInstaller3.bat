:: -------------------------------------------------------------------
:: Copyright (c) 2010-2017 Denis Machard
:: This file is part of the extensive testing project
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

set Acronym=Client
set Project=%~dp0..\
set Output=E:\My Lab\01 ExtensiveTesting\02 - Output\

set PythonVersion=34
set Python=C:\Python%PythonVersion%\python.exe
set PythonPath=C:\Python%PythonVersion%\
set PyQtPath=Lib\site-packages\PyQt4\
set PyRcc=pyrcc4.exe

:: convert xml translations files
%PythonPath%\%PyQtPath%\lrelease.exe "%Project%\Translations\us_US.ts"
%PythonPath%\%PyQtPath%\lrelease.exe "%Project%\Translations\fr_FR.ts"

:: build resources
echo Building translations resources...
%PythonPath%\%PyQtPath%\%PyRcc% -py3 -o "%Project%\Translations\Translations.py" "%Project%\Translations\__resources.qrc"

:: build images resources
echo Building translations resources...
%PythonPath%\%PyQtPath%\%PyRcc% -py3 -o "%Project%\Resources\Resources.py" "%Project%\Resources\__resources.qrc"

:: build executable
cd "%Project%"
%Python% "%Project%\ConfigureExe.py"
%Python% "%Project%\BuildWin.py" py2exe

"%Python%" "%Project%\BuildWinInstaller.py" "%Output%\"

pause