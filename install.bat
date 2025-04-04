@echo off
chcp 65001 >nul
SETLOCAL ENABLEDELAYEDEXPANSION

:: Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден. Установка...
    curl -o python_installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo Python установлен.
)

:: Список необходимых библиотек
set LIBS=matplotlib numba numpy pillow tqdm

:: Установка отсутствующих библиотек
for %%i in (%LIBS%) do (
    call :CHECK_LIB %%i
)

echo Все необходимые библиотеки установлены.
pause
exit /b

:CHECK_LIB
set "LIB=%~1"
python -c "import %LIB%" >nul 2>&1
if errorlevel 1 (
    echo Установка %LIB%...
    python -m pip install %LIB%
) else (
    echo %LIB% уже установлен.
)
exit /b


echo Все необходимые библиотеки установлены.
pause
