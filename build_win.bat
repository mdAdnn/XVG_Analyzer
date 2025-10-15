@echo off
echo === Building xvg_plotter for Windows ===
pyinstaller --noconsole --onefile xvg_plotter.py
echo Build complete! EXE in dist/
pause
