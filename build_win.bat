@echo off
REM ===============================================
REM Fast Build & Test for XVG Analyzer EXE
REM ===============================================

REM Activate virtual environment
call venv\Scripts\activate

REM Clean previous builds
echo Cleaning old build/dist folders...
rmdir /s /q build
rmdir /s /q dist

REM Build EXE
echo Building xvg_analyzer.exe...
pyinstaller --onefile --windowed --name xvg_analyzer xvg_analyzer.py

IF EXIST dist\xvg_analyzer.exe (
    echo ✅ Build complete!
    echo Launching EXE for testing...
    start dist\xvg_analyzer.exe
) ELSE (
    echo ❌ Build failed!
)

pause