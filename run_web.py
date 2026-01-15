"""Run the FastAPI web UI locally.

Usage:
    python run_web.py

This script ensures imports resolve when launching from repository root.
"""
import os
import sys

THIS_DIR = os.path.dirname(__file__)
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from ui.webapp import run

if __name__ == '__main__':
    run()
