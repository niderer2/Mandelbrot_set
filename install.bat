@echo off
chcp 65001 >nul
SETLOCAL ENABLEDELAYEDEXPANSION

:: Проверяем, установлен ли Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python не найден. Устанавливаем...
    powershell -Command "Start-Process -Verb RunAs -FilePath msiexec.exe -ArgumentList '/i https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe /quiet InstallAllUsers=1 PrependPath=1' -Wait"
)

:: Обновляем PATH (чтобы найти pip)
set "PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts"

:: Проверяем, установлен ли pip
pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Устанавливаем pip...
    python -m ensurepip --default-pip
)

:: Устанавливаем библиотеки
pip install --upgrade pip
pip install pillow numba

echo Установка завершена.
pause