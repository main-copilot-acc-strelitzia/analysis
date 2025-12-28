"""Main application class."""

import sys
from typing import Optional, List, Dict, Any
from core.logger import get_logger
from core.lifecycle import LifecycleManager, AppState
from core.error_handlers import MT5ConnectionError
from mt5.connector import MT5Connector
from mt5.account import AccountManager
from mt5.symbols import SymbolManager
from mt5.market_data import MarketDataManager
from analysis.forex.analyzer import ForexAnalyzer
from analysis.synthetics.analyzer import SyntheticsAnalyzer
from analysis.general.analyzer import GeneralAssetAnalyzer
from ui.cli import CLIInterface
from config.settings import ANALYSIS_CONFIG, ROBUSTNESS_CONFIG


class StrelitziaApp:
    """Main application class with session awareness."""

    def __init__(self):
        """Initialize application."""
        self.logger = get_logger()
        self.lifecycle = LifecycleManager()
        self.cli = CLIInterface()

        self.mt5_connector = MT5Connector()
        self.account_manager = AccountManager()
        self.symbol_manager = SymbolManager()
        self.market_data_manager = MarketDataManager()
        
        self._last_session_id = None  # Track session for change detection

    def initialize(self) -> bool:
        """
        Initialize application (MT5 already verified by StartupVerifier).
        Includes session awareness for account/server changes.
        
        Returns:
            bool: True if successful.
        """
        self.logger.info("Initializing Strelitzia Trader analysis engine")

        self.cli.print_header()

        # MT5 connection already verified by startup verifier
        # Just verify we can still read account
        self.cli.display_loading("Verifying account access")
        account_info = self.account_manager.get_account_info()
        if not account_info:
            self.cli.display_message("FAILED - Cannot access account information", "ERROR")
            self.logger.error("Lost connection to account information")
            return False

        self.cli.display_done()
        self.cli.print_account_info(account_info)
        
        # Initialize session tracking
        if ROBUSTNESS_CONFIG['session_change_detection_enabled']:
            session_changed = self.mt5_connector.detect_session_change()
            self._last_session_id = self.mt5_connector.get_session_id()
            if session_changed:
                self.cli.display_message(
                    f"Session initialized: {account_info['login']} @ {account_info['server']}", 
                    "INFO"
                )

        self.lifecycle.transition_to(AppState.RUNNING)
        self.logger.info("Application initialized successfully")
        return True
    
    def check_session_integrity(self) -> bool:
        """
        Check if session has changed (account/server).
        Auto-reinitialize if configured.
        
        Returns:
            bool: True if session is intact, False if reinit needed
        """
        if not ROBUSTNESS_CONFIG['session_change_detection_enabled']:
            return True
        
        try:
            session_changed = self.mt5_connector.detect_session_change()
            if session_changed:
                current_session_id = self.mt5_connector.get_session_id()
                self.logger.warning(f"Session integrity check: change detected")
                
                if ROBUSTNESS_CONFIG['auto_reinitialize_on_session_change']:
                    self.cli.display_message(
                        "Session changed - auto-reinitializing analysis engine", 
                        "WARNING"
                    )
                    # Clear symbol cache on account/server change
                    self.market_data_manager.invalidate_all_cache()
                    self.symbol_manager.refresh_symbols()
                    self._last_session_id = current_session_id
                    return self.initialize()
                else:
                    self.cli.display_message(
                        "Session changed but auto-reinit disabled - manual restart recommended",
                        "WARNING"
                    )
                    return False
            return True
        except MT5ConnectionError as e:
            # Transient MT5 connection error - retry later
            self.logger.warning(f"Transient MT5 error during session check: {e}")
            return True  # Don't fail on transient errors - allow continuation
        except Exception as e:
            # Unexpected error - log with full traceback
            self.logger.error(f"Unexpected error checking session integrity: {e}", exc_info=True)
            return False

    def run(self):
        """Run the main application loop."""
        try:
            if not self.initialize():
                self.shutdown()
                return

            self.main_menu()

        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.shutdown()

    def main_menu(self):
        """Main menu loop with periodic session checks."""
        while self.lifecycle.is_running():
            try:
                # Periodic session integrity check
                if not self.check_session_integrity():
                    self.cli.display_message("Cannot proceed - session integrity check failed", "ERROR")
                    break
                
                self.cli.display_loading("Discovering symbols")
                categories = self.symbol_manager.categorize_symbols()
                self.cli.display_done()

                if not categories:
                    self.cli.display_message("No symbols available", "ERROR")
                    break

                # Select category
                selected_category = self.cli.select_category(categories)
                if not selected_category:
                    break

                # Select symbols
                symbols = categories[selected_category]
                selected_symbols = self.cli.select_symbols(symbols)
                if not selected_symbols:
                    continue

                # Select timeframes
                selected_timeframes = self.cli.select_timeframes()
                if not selected_timeframes:
                    continue

                # Perform analysis
                self.analyze_symbols(selected_symbols, selected_timeframes, selected_category)

                # Ask if continue
                if not self.cli.confirm_action("Continue to analyze more symbols?"):
                    break

            except Exception as e:
                self.logger.error(f"Error in main menu: {e}")
                self.cli.display_message(f"An error occurred: {e}", "ERROR")

    def analyze_symbols(self, symbols: List[str], timeframes: List[str], category: str):
        """Analyze selected symbols."""
        self.logger.info(f"Starting analysis for {len(symbols)} symbols in {category}")

        for symbol in symbols:
            self.cli.display_message(f"\nAnalyzing {symbol}", "INFO")

            # Get available timeframes for this symbol
            available_timeframes = self.market_data_manager.get_available_timeframes(symbol, timeframes)
            
            if not available_timeframes:
                self.cli.display_message(
                    f"SKIP - No available timeframes for {symbol}. "
                    f"(Requested: {', '.join(timeframes)})",
                    "WARNING"
                )
                self.logger.warning(f"No available timeframes for {symbol}")
                continue

            # Notify user of any unavailable timeframes
            unavailable = set(timeframes) - set(available_timeframes)
            if unavailable:
                self.cli.display_message(
                    f"Note: Timeframes {', '.join(unavailable)} not available for {symbol}",
                    "INFO"
                )

            for timeframe in available_timeframes:
                try:
                    # Fetch market data
                    self.cli.display_loading(f"Fetching data for {symbol} {timeframe}")
                    data = self.market_data_manager.get_candles(
                        symbol, 
                        timeframe, 
                        count=ANALYSIS_CONFIG['max_candles']
                    )
                    self.cli.display_done()

                    # Check data sufficiency
                    if ROBUSTNESS_CONFIG['data_availability_check']:
                        is_sufficient, message = self.market_data_manager.check_data_sufficiency(
                            data, 
                            min_candles=ANALYSIS_CONFIG['min_candles']
                        )
                        if not is_sufficient:
                            self.cli.display_message(f"SKIP {symbol} {timeframe}: {message}", "WARNING")
                            self.logger.warning(f"Data check failed for {symbol} {timeframe}: {message}")
                            continue

                    # Validate data
                    if not self.market_data_manager.validate_data(data):
                        self.cli.display_message(f"INVALID DATA: {symbol} {timeframe}", "WARNING")
                        self.logger.warning(f"Invalid data for {symbol} {timeframe}")
                        continue

                    # Handle missing data
                    data = self.market_data_manager.handle_missing_data(data)

                    # Run analysis based on symbol category
                    self.cli.display_loading(f"Analyzing {symbol} {timeframe}")
                    result = self.analyze_with_appropriate_analyzer(symbol, timeframe, data, category)
                    self.cli.display_done()

                    # Display result
                    self.cli.display_analysis_result(result)

                    self.logger.info(
                        f"Analysis complete for {symbol} {timeframe} - "
                        f"Confluence: {result.get('confluence_score', 0):.2f}"
                    )

                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol} {timeframe}: {e}")
                    self.cli.display_message(f"Error analyzing {symbol} {timeframe}: {e}", "ERROR")

    def analyze_with_appropriate_analyzer(self, symbol: str, timeframe: str, data: Any, category: str) -> Dict[str, Any]:
        """
        Select and use appropriate analyzer based on symbol category.
        
        Uses specialized analyzers for:
        - Forex (Majors, Minors, Exotics): ForexAnalyzer (41 methods)
        - Synthetics (Volatility, Boom/Crash, Jump, Step): SyntheticsAnalyzer (37 methods)
        - Everything else (Indices, Commodities, Crypto, Other): GeneralAssetAnalyzer (30+ methods)
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe
            data: OHLCV data
            category: Symbol category
            
        Returns:
            Analysis result with confluence score and signals
        """
        analyzer = None
        method_count = 0
        
        # Select analyzer based on category
        if 'Forex' in category:
            # Forex Majors, Minors, Exotics
            analyzer = ForexAnalyzer(symbol, timeframe)
            method_count = 41
            
        elif any(keyword in category for keyword in ['Synthetic', 'Volatility', 'Boom', 'Crash', 'Jump', 'Step', 'Range']):
            # Synthetics and related indices
            analyzer = SyntheticsAnalyzer(symbol, timeframe)
            method_count = 37
            
        else:
            # Indices, Commodities, Crypto, and uncategorized
            analyzer = GeneralAssetAnalyzer(symbol, timeframe)
            method_count = 30
        
        # Perform analysis
        result = analyzer.analyze(data)
        
        # Add analyzer info to result for transparency
        result['analyzer_type'] = analyzer.__class__.__name__
        result['methods_used'] = method_count
        result['category'] = category
        result['symbol'] = symbol
        result['timeframe'] = timeframe
        
        return result

    def shutdown(self):
        """Shutdown application."""
        self.logger.info("Shutting down Strelitzia Trader")
        self.lifecycle.transition_to(AppState.SHUTTING_DOWN)

        self.market_data_manager.clear_cache()
        self.mt5_connector.disconnect()

        self.lifecycle.transition_to(AppState.SHUTDOWN)
        self.logger.info("Application shutdown complete")
