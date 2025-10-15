@echo off
echo === Building xvg_plotter for Windows ===
pyinstaller --noconsole --onefile xvg_analyzer.py
echo Build complete! EXE in dist/
pause
