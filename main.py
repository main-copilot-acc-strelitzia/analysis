"""
Main entry point for Strelitzia Trader.

This application connects to a running MetaTrader 5 terminal and analyzes
market symbols using advanced confluence scoring.

REQUIREMENTS:
- MetaTrader 5 terminal must be running
- An account must be logged in to the MT5 terminal
- No environment variables or configuration files needed

EXECUTION:
Simply run: python main.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import StrelitziaApp
from core.startup_verifier import StartupVerifier, StartupStatusDisplay
from core.logger import get_logger


def main():
    """Main entry point with explicit startup verification."""
    logger = get_logger()
    
    # Step 1: Verify startup sequence
    verifier = StartupVerifier(logger)
    startup_result = verifier.verify_startup_sequence()
    
    if startup_result is None:
        StartupStatusDisplay.show_startup_failed()
        logger.critical("Startup verification failed")
        sys.exit(1)
    
    # Step 2: Show successful startup
    StartupStatusDisplay.show_startup_complete()
    
    # Step 3: Run application
    try:
        app = StrelitziaApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user (Ctrl+C)")
        logger.info("Application stopped by user")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
