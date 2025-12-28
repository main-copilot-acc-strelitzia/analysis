"""Symbol discovery and categorization."""

import MetaTrader5 as mt5
from typing import Dict, Optional, Set, Callable, Any
from core.logger import get_logger
from datetime import datetime


class SymbolManager:
    """Manages symbol discovery and categorization with dynamic refresh support."""

    # Symbol name patterns for categorization
    FOREX_MAJORS = {'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'}
    FOREX_MINORS = {'EURJPY', 'EURGBP', 'EURCHF', 'EURCAD', 'EURAUD', 'EURNZD',
                    'GBPJPY', 'GBPCHF', 'GBPCAD', 'GBPAUD', 'GBPNZD',
                    'CHFJPY', 'CADCHF', 'AUDCHF', 'NZDCHF',
                    'CADJPY', 'AUDJPY', 'NZDJPY',
                    'AUDCAD', 'AUDNZD', 'CADNZD'}
    VOLATILITY_INDICES = {'VOLATILITY10', 'VOLATILITY25', 'VOLATILITY50', 'VOLATILITY75', 'VOLATILITY100',
                         'VOLATILITY10S', 'VOLATILITY25S', 'VOLATILITY50S', 'VOLATILITY75S', 'VOLATILITY100S'}
    BOOM_CRASH = {'BOOM1000', 'BOOM500', 'BOOM300', 'CRASH1000', 'CRASH500', 'CRASH300',
                 'BOOM100', 'CRASH100', 'BOOM50', 'CRASH50'}
    JUMP_INDICES = {'JUMP10', 'JUMP25', 'JUMP50', 'JUMP75', 'JUMP100',
                   'JUMP10S', 'JUMP25S', 'JUMP50S', 'JUMP75S', 'JUMP100S'}
    STEP_INDICES = {'STEP10', 'STEP25', 'STEP50', 'STEP75', 'STEP100',
                   'STEP10S', 'STEP25S', 'STEP50S', 'STEP75S', 'STEP100S'}

    def __init__(self):
        """Initialize symbol manager."""
        self.logger = get_logger()
        self._symbol_cache = {}
        self._categories_cache = {}
        self._last_refresh = None
        self._on_symbols_refreshed: list[Callable] = []
        self._on_new_symbols: list[Callable[[list[str]], None]] = []
        self._on_removed_symbols: list[Callable[[list[str]], None]] = []

    def get_all_symbols(self) -> Optional[list[str]]:
        """
        Retrieve all available symbols from MT5.
        
        Returns:
            Optional[list[str]]: List of symbols or None if error.
        """
        try:
            symbols = mt5.symbols_get()
            if symbols is None or len(symbols) == 0:
                self.logger.warning("No symbols available from MT5")
                return []

            symbol_names = [s.name for s in symbols]
            self.logger.info(f"Retrieved {len(symbol_names)} symbols from MT5")
            return symbol_names

        except Exception as e:
            self.logger.error(f"Error retrieving symbols: {e}")
            return None

    def categorize_symbols(self) -> Optional[dict[str, list[str]]]:
        """
        Categorize all symbols by type.
        
        Returns:
            Optional[dict[str, list[str]]]: Symbols grouped by category.
        """
        try:
            symbols = self.get_all_symbols()
            if symbols is None:
                return None

            categories = {
                'Forex Majors': [],
                'Forex Minors': [],
                'Forex Exotics': [],
                'Volatility Indices': [],
                'Boom and Crash': [],
                'Jump Indices': [],
                'Step Indices': [],
                'Indices': [],
                'Commodities': [],
                'Metals': [],
                'Crypto': [],
                'Other': [],
            }

            for symbol in symbols:
                upper_symbol = symbol.upper()

                if upper_symbol in self.FOREX_MAJORS:
                    categories['Forex Majors'].append(symbol)
                elif upper_symbol in self.FOREX_MINORS:
                    categories['Forex Minors'].append(symbol)
                elif upper_symbol in self.VOLATILITY_INDICES:
                    categories['Volatility Indices'].append(symbol)
                elif upper_symbol in self.BOOM_CRASH:
                    categories['Boom and Crash'].append(symbol)
                elif upper_symbol in self.JUMP_INDICES:
                    categories['Jump Indices'].append(symbol)
                elif upper_symbol in self.STEP_INDICES:
                    categories['Step Indices'].append(symbol)
                elif self._is_forex_exotic(upper_symbol):
                    categories['Forex Exotics'].append(symbol)
                elif self._is_metal(upper_symbol):
                    categories['Metals'].append(symbol)
                elif self._is_crypto(upper_symbol):
                    categories['Crypto'].append(symbol)
                elif self._is_commodity(upper_symbol):
                    categories['Commodities'].append(symbol)
                elif self._is_index(upper_symbol):
                    categories['Indices'].append(symbol)
                else:
                    categories['Other'].append(symbol)

            # Remove empty categories
            categories = {k: v for k, v in categories.items() if v}

            self.logger.info(f"Categorized {len(symbols)} symbols into {len(categories)} categories")
            self._categories_cache = categories
            return categories

        except Exception as e:
            self.logger.error(f"Error categorizing symbols: {e}")
            return None

    def _is_forex_exotic(self, symbol: str) -> bool:
        """Check if symbol is forex exotic pair."""
        forex_patterns = ['ZAR', 'TRY', 'MXN', 'BRL', 'CNY', 'INR', 'RUB', 'SGD', 'HKD', 'NOK', 'SEK', 'DKK']
        return any(pattern in symbol for pattern in forex_patterns) and any(
            c in symbol for c in ['USD', 'EUR', 'GBP']
        )

    def _is_metal(self, symbol: str) -> bool:
        """Check if symbol is a metal."""
        metals = ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM']
        return symbol in metals or any(symbol.startswith(m) for m in ['XAU', 'XAG', 'XPT', 'XPD'])

    def _is_crypto(self, symbol: str) -> bool:
        """Check if symbol is cryptocurrency."""
        crypto_patterns = ['BTC', 'ETH', 'LTC', 'XRP', 'BCH', 'ADA', 'DOT', 'LINK', 'DOGE', 'USDT']
        return any(pattern in symbol for pattern in crypto_patterns)

    def _is_commodity(self, symbol: str) -> bool:
        """Check if symbol is commodity."""
        commodities = ['WTIUSD', 'BRENTUSD', 'NATGAS', 'CORN', 'WHEAT', 'SOYBEANS', 'SUGAR', 'COFFEE']
        return symbol in commodities or any(symbol.startswith(c) for c in ['WTI', 'BRENT', 'NGAS', 'CL', 'GC', 'SI', 'CU', 'NG'])

    def _is_index(self, symbol: str) -> bool:
        """Check if symbol is an index."""
        index_patterns = ['SPX', 'NDX', 'DAX', 'CAC', 'FTSE', 'NIKKEI', 'ASX', 'SENSEX', 'HANG', 'INDEX']
        return any(pattern in symbol for pattern in index_patterns)

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a symbol.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Optional[Dict[str, Any]]: Symbol information or None.
        """
        try:
            sym_info = mt5.symbol_info(symbol)
            if sym_info is None:
                self.logger.warning(f"Symbol not found: {symbol}")
                return None

            return {
                'name': sym_info.name,
                'description': sym_info.description,
                'bid': sym_info.bid,
                'ask': sym_info.ask,
                'digits': sym_info.digits,
                'spread': sym_info.spread,
                'spread_float': sym_info.spread_float,
                'volume': sym_info.volume,
                'volume_high': sym_info.volume_high,
                'volume_low': sym_info.volume_low,
                'time': sym_info.time,
                'trade_mode': sym_info.trade_mode,
                'trade_execution': sym_info.trade_execution,
                'session_deals': sym_info.session_deals,
                'session_buy_orders': sym_info.session_buy_orders,
                'session_sell_orders': sym_info.session_sell_orders,
                'volume_real': sym_info.volume_real,
                'volume_high_real': sym_info.volume_high_real,
                'volume_low_real': sym_info.volume_low_real,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving symbol info for {symbol}: {e}")
            return None

    def get_category_symbols(self, category: str) -> list[str]:
        """
        Get symbols in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            list[str]: Symbols in the category.
        """
        if not self._categories_cache:
            self.categorize_symbols()

        return self._categories_cache.get(category, [])

    def register_symbols_refreshed_callback(self, callback: Callable) -> None:
        """Register callback when symbols are refreshed."""
        self._on_symbols_refreshed.append(callback)

    def register_new_symbols_callback(self, callback: Callable[[list[str]], None]) -> None:
        """Register callback for newly added symbols."""
        self._on_new_symbols.append(callback)

    def register_removed_symbols_callback(self, callback: Callable[[list[str]], None]) -> None:
        """Register callback for removed symbols."""
        self._on_removed_symbols.append(callback)

    def refresh(self) -> bool:
        """
        Refresh symbol list and categories from MT5.
        
        Detects new/removed symbols and triggers callbacks.
        
        Returns:
            bool: True if refresh successful, False otherwise.
        """
        try:
            # Get previous symbols
            old_symbols = set(self._symbol_cache.keys())
            
            # Fetch new symbols from MT5
            symbols = self.get_all_symbols()
            if symbols is None:
                self.logger.error("Failed to refresh symbols from MT5")
                return False
            
            new_symbols = set(symbols)
            
            # Detect changes
            added_symbols = list(new_symbols - old_symbols)
            removed_symbols = list(old_symbols - new_symbols)
            
            # Update cache
            self._symbol_cache = {s: None for s in symbols}
            
            # Re-categorize
            self.categorize_symbols()
            
            # Update timestamp
            self._last_refresh = datetime.now()
            
            # Log changes
            if added_symbols:
                self.logger.info(f"Added {len(added_symbols)} new symbols: {added_symbols[:5]}...")
            if removed_symbols:
                self.logger.info(f"Removed {len(removed_symbols)} symbols: {removed_symbols[:5]}...")
            
            # Trigger callbacks
            for callback in self._on_symbols_refreshed:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in symbols_refreshed callback: {e}")
            
            if added_symbols:
                for callback in self._on_new_symbols:
                    try:
                        callback(added_symbols)
                    except Exception as e:
                        self.logger.error(f"Error in new_symbols callback: {e}")
            
            if removed_symbols:
                for callback in self._on_removed_symbols:
                    try:
                        callback(removed_symbols)
                    except Exception as e:
                        self.logger.error(f"Error in removed_symbols callback: {e}")
            
            self.logger.info(f"Symbol refresh completed. Total symbols: {len(symbols)}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error during symbol refresh: {e}")
            return False

    def get_last_refresh_time(self) -> Optional[datetime]:
        """Get timestamp of last symbol refresh."""
        return self._last_refresh

    def symbol_exists(self, symbol: str) -> bool:
        """Check if symbol exists in current cache."""
        return symbol in self._symbol_cache

