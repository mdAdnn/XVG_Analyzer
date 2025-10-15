#!/bin/bash
echo "=== Building xvg_plotter for Linux ==="
pyinstaller --noconsole --onefile xvg_plotter.py
echo "Build complete! Binary in dist/"
