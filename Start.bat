@echo off
chcp 65001 > nul
if EXIST .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) else (
    echo ====================================================
    echo Виртуальное окружение не найдено. Пожалуйста, запустите Setup.bat сначала.
    echo ====================================================
    pause
)