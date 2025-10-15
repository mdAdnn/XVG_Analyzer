#!/bin/bash
echo "=== Building xvg_plotter for Linux ==="
pyinstaller --noconsole --onefile xvg_analyzer.py
echo "Build complete! Binary in dist/"
