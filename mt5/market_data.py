"""Market data retrieval from MT5."""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from core.logger import get_logger


class CacheEntry:
    """Cache entry with metadata for intelligent invalidation."""
    
    def __init__(self, data: pd.DataFrame, timeframe: str):
        self.data = data
        self.timeframe = timeframe
        self.timestamp = datetime.now()
        self.last_candle_time = data['Timestamp'].iloc[-1] if len(data) > 0 else None
    
    def is_stale(self, current_time: datetime, timeframe_minutes: int) -> bool:
        """Check if cache is stale based on the latest candle time."""
        if self.last_candle_time is None:
            return True
        
        # Data is stale if latest candle is older than 1.5x the timeframe
        threshold = timedelta(minutes=timeframe_minutes * 1.5)
        return (current_time - self.last_candle_time) > threshold


class MarketDataManager:
    """Manages market data retrieval and intelligent caching."""

    # MT5 timeframe mapping
    TIMEFRAME_MAP = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
        'W1': mt5.TIMEFRAME_W1,
        'MN1': mt5.TIMEFRAME_MN1,
    }
    
    # Timeframe to minutes mapping for cache staleness
    TIMEFRAME_MINUTES = {
        'M1': 1,
        'M5': 5,
        'M15': 15,
        'M30': 30,
        'H1': 60,
        'H4': 240,
        'D1': 1440,
        'W1': 10080,
        'MN1': 43200,
    }

    def __init__(self):
        """Initialize market data manager."""
        self.logger = get_logger()
        self._data_cache: Dict[str, Dict[str, CacheEntry]] = {}

    def get_candles(self, symbol: str, timeframe: str, count: int = 500, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Retrieve candle data from MT5 with intelligent caching.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string (M1, M5, M15, M30, H1, H4, D1, W1, MN1)
            count: Number of candles to retrieve
            force_refresh: Force refresh even if cached
            
        Returns:
            Optional[pd.DataFrame]: OHLCV data or None if error.
        """
        try:
            if timeframe not in self.TIMEFRAME_MAP:
                self.logger.error(f"Invalid timeframe: {timeframe}")
                return None

            # Check cache first
            if not force_refresh:
                cached = self.get_cached_data(symbol, timeframe)
                if cached is not None:
                    tf_minutes = self.TIMEFRAME_MINUTES.get(timeframe, 60)
                    cache_entry = self._data_cache.get(symbol, {}).get(timeframe)
                    
                    if cache_entry and not cache_entry.is_stale(datetime.now(), tf_minutes):
                        self.logger.debug(f"Using cached data for {symbol} {timeframe}")
                        return cached

            tf = self.TIMEFRAME_MAP[timeframe]

            # Get candle data
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No data retrieved for {symbol} {timeframe}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={
                'time': 'Timestamp',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume',
                'real_volume': 'RealVolume',
                'spread': 'Spread',
            })

            df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'RealVolume', 'Spread']]
            df = df.sort_values('Timestamp').reset_index(drop=True)

            # Cache the data with error handling
            try:
                if symbol not in self._data_cache:
                    self._data_cache[symbol] = {}
                self._data_cache[symbol][timeframe] = CacheEntry(df, timeframe)
                self.logger.debug(f"Cached {len(df)} candles for {symbol} {timeframe}")
            except Exception as cache_error:
                self.logger.warning(f"Failed to cache data for {symbol} {timeframe}: {cache_error}")
                # Continue without caching - don't fail the whole operation

            self.logger.debug(f"Retrieved {len(df)} candles for {symbol} {timeframe}")
            return df

        except Exception as e:
            self.logger.error(f"Error retrieving candles for {symbol} {timeframe}: {e}")
            return None

    def get_candles_from_date(self, symbol: str, timeframe: str, start_date: datetime) -> Optional[pd.DataFrame]:
        """
        Retrieve candle data from a specific date.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string
            start_date: Start date for data retrieval
            
        Returns:
            Optional[pd.DataFrame]: OHLCV data or None if error.
        """
        try:
            if timeframe not in self.TIMEFRAME_MAP:
                self.logger.error(f"Invalid timeframe: {timeframe}")
                return None

            tf = self.TIMEFRAME_MAP[timeframe]

            # Get candle data from date
            rates = mt5.copy_rates_from(symbol, tf, start_date, 500)
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No data retrieved for {symbol} from {start_date}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={
                'time': 'Timestamp',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume',
                'real_volume': 'RealVolume',
                'spread': 'Spread',
            })

            df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'RealVolume', 'Spread']]
            df = df.sort_values('Timestamp').reset_index(drop=True)

            self.logger.debug(f"Retrieved {len(df)} candles for {symbol} from {start_date}")
            return df

        except Exception as e:
            self.logger.error(f"Error retrieving candles for {symbol} from {start_date}: {e}")
            return None

    def get_multiple_timeframes(
        self,
        symbol: str,
        timeframes: List[str],
        count: int = 500
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Retrieve candles for multiple timeframes simultaneously.
        
        Args:
            symbol: Symbol name
            timeframes: List of timeframe strings
            count: Number of candles per timeframe
            
        Returns:
            Dict: {timeframe: dataframe, ...}
        """
        results = {}
        for tf in timeframes:
            results[tf] = self.get_candles(symbol, tf, count)
        return results

    def get_cached_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Get cached data if available.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string
            
        Returns:
            Optional[pd.DataFrame]: Cached data or None.
        """
        if symbol in self._data_cache and timeframe in self._data_cache[symbol]:
            return self._data_cache[symbol][timeframe].data.copy()
        return None

    def clear_cache(self, symbol: Optional[str] = None, timeframe: Optional[str] = None):
        """
        Clear data cache with granular control.
        
        Args:
            symbol: If specified, only clear data for this symbol.
            timeframe: If specified, only clear this timeframe.
        """
        if symbol and timeframe:
            if symbol in self._data_cache and timeframe in self._data_cache[symbol]:
                del self._data_cache[symbol][timeframe]
                self.logger.debug(f"Cleared cache for {symbol} {timeframe}")
        elif symbol:
            if symbol in self._data_cache:
                del self._data_cache[symbol]
                self.logger.debug(f"Cleared cache for {symbol}")
        else:
            self._data_cache.clear()
            self.logger.debug("Cleared all data cache")

    def invalidate_symbol_cache(self, symbol: str):
        """Invalidate all timeframes for a symbol (e.g., on account change)."""
        if symbol in self._data_cache:
            del self._data_cache[symbol]
            self.logger.info(f"Invalidated all cache for {symbol}")

    def invalidate_all_cache(self):
        """Invalidate all cached data (e.g., on account change or forced refresh)."""
        self._data_cache.clear()
        self.logger.info("Invalidated all cached data")

    def get_current_tick(self, symbol: str) -> Optional[Dict]:
        """
        Get current tick information.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Optional[Dict]: Tick information or None.
        """
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                self.logger.warning(f"Unable to get tick for {symbol}")
                return None

            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'volume': tick.volume,
                'time': datetime.fromtimestamp(tick.time),
                'time_msc': tick.time_msc,
                'volume_real': tick.volume_real,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving tick for {symbol}: {e}")
            return None

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate OHLCV data integrity.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            bool: True if data is valid.
        """
        try:
            if df is None or len(df) == 0:
                return False

            # Check for required columns
            required = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required):
                return False

            # Check for NaN values
            if df[required].isnull().any().any():
                self.logger.warning("Data contains NaN values")
                return False

            # Check OHLC relationships
            invalid = (df['High'] < df['Low']).sum()
            if invalid > 0:
                self.logger.warning(f"{invalid} candles have High < Low")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return False

    def handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing data in OHLCV series.
        
        Args:
            df: DataFrame with potential gaps
            
        Returns:
            pd.DataFrame: DataFrame with gaps filled.
        """
        try:
            if df is None or len(df) == 0:
                return df

            # Forward fill for missing values
            df['Open'] = df['Open'].fillna(method='ffill')
            df['Close'] = df['Close'].fillna(method='ffill')
            df['High'] = df['High'].fillna(method='ffill')
            df['Low'] = df['Low'].fillna(method='ffill')
            df['Volume'] = df['Volume'].fillna(0)

            # Backward fill for any remaining NaN
            df = df.fillna(method='bfill')

            return df

        except Exception as e:
            self.logger.error(f"Error handling missing data: {e}")
            return df


    def get_candles(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """
        Retrieve candle data from MT5.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string (M1, M5, M15, M30, H1, H4, D1, W1, MN1)
            count: Number of candles to retrieve
            
        Returns:
            Optional[pd.DataFrame]: OHLCV data or None if error.
        """
        try:
            if timeframe not in self.TIMEFRAME_MAP:
                self.logger.error(f"Invalid timeframe: {timeframe}")
                return None

            tf = self.TIMEFRAME_MAP[timeframe]

            # Get candle data
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No data retrieved for {symbol} {timeframe}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={
                'time': 'Timestamp',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume',
                'real_volume': 'RealVolume',
                'spread': 'Spread',
            })

            df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'RealVolume', 'Spread']]
            df = df.sort_values('Timestamp').reset_index(drop=True)

            # Cache the data
            if symbol not in self._data_cache:
                self._data_cache[symbol] = {}
            self._data_cache[symbol][timeframe] = df

            self.logger.debug(f"Retrieved {len(df)} candles for {symbol} {timeframe}")
            return df

        except Exception as e:
            self.logger.error(f"Error retrieving candles for {symbol} {timeframe}: {e}")
            return None

    def get_candles_from_date(self, symbol: str, timeframe: str, start_date: datetime) -> Optional[pd.DataFrame]:
        """
        Retrieve candle data from a specific date.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string
            start_date: Start date for data retrieval
            
        Returns:
            Optional[pd.DataFrame]: OHLCV data or None if error.
        """
        try:
            if timeframe not in self.TIMEFRAME_MAP:
                self.logger.error(f"Invalid timeframe: {timeframe}")
                return None

            tf = self.TIMEFRAME_MAP[timeframe]

            # Get candle data from date
            rates = mt5.copy_rates_from(symbol, tf, start_date, 500)
            if rates is None or len(rates) == 0:
                self.logger.warning(f"No data retrieved for {symbol} from {start_date}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={
                'time': 'Timestamp',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume',
                'real_volume': 'RealVolume',
                'spread': 'Spread',
            })

            df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'RealVolume', 'Spread']]
            df = df.sort_values('Timestamp').reset_index(drop=True)

            self.logger.debug(f"Retrieved {len(df)} candles for {symbol} from {start_date}")
            return df

        except Exception as e:
            self.logger.error(f"Error retrieving candles for {symbol} from {start_date}: {e}")
            return None

    def get_cached_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Get cached data if available.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string
            
        Returns:
            Optional[pd.DataFrame]: Cached data or None.
        """
        if symbol in self._data_cache and timeframe in self._data_cache[symbol]:
            return self._data_cache[symbol][timeframe].copy()
        return None

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear data cache.
        
        Args:
            symbol: If specified, only clear data for this symbol.
        """
        if symbol:
            if symbol in self._data_cache:
                del self._data_cache[symbol]
                self.logger.debug(f"Cleared cache for {symbol}")
        else:
            self._data_cache.clear()
            self.logger.debug("Cleared all data cache")

    def get_current_tick(self, symbol: str) -> Optional[Dict]:
        """
        Get current tick information.
        
        Args:
            symbol: Symbol name
            
        Returns:
            Optional[Dict]: Tick information or None.
        """
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                self.logger.warning(f"Unable to get tick for {symbol}")
                return None

            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'volume': tick.volume,
                'time': datetime.fromtimestamp(tick.time),
                'time_msc': tick.time_msc,
                'volume_real': tick.volume_real,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving tick for {symbol}: {e}")
            return None

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate OHLCV data integrity.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            bool: True if data is valid.
        """
        try:
            if df is None or len(df) == 0:
                return False

            # Check for required columns
            required = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required):
                return False

            # Check for NaN values
            if df[required].isnull().any().any():
                self.logger.warning("Data contains NaN values")
                return False

            # Check OHLC relationships
            invalid = (df['High'] < df['Low']).sum()
            if invalid > 0:
                self.logger.warning(f"{invalid} candles have High < Low")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return False

    def handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing data in OHLCV series.
        
        Args:
            df: DataFrame with potential gaps
            
        Returns:
            pd.DataFrame: DataFrame with gaps filled.
        """
        try:
            if df is None or len(df) == 0:
                return df

            # Forward fill for missing values
            df['Open'] = df['Open'].fillna(method='ffill')
            df['Close'] = df['Close'].fillna(method='ffill')
            df['High'] = df['High'].fillna(method='ffill')
            df['Low'] = df['Low'].fillna(method='ffill')
            df['Volume'] = df['Volume'].fillna(0)

            # Backward fill for any remaining NaN
            df = df.fillna(method='bfill')

            return df

        except Exception as e:
            self.logger.error(f"Error handling missing data: {e}")
            return df

    def is_timeframe_available(self, symbol: str, timeframe: str) -> bool:
        """Check if a timeframe is available for a symbol."""
        try:
            if timeframe not in self.TIMEFRAME_MAP:
                return False
            tf = self.TIMEFRAME_MAP[timeframe]
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, 1)
            return rates is not None and len(rates) > 0
        except Exception as e:
            self.logger.debug(f"Error checking {timeframe} for {symbol}: {e}")
            return False

    def get_available_timeframes(self, symbol: str, timeframe_list: Optional[List[str]] = None) -> List[str]:
        """Get list of available timeframes for a symbol."""
        if timeframe_list is None:
            timeframe_list = list(self.TIMEFRAME_MAP.keys())
        available = [tf for tf in timeframe_list if self.is_timeframe_available(symbol, tf)]
        if available:
            self.logger.info(f"Available timeframes for {symbol}: {available}")
        return available
    
    def check_data_sufficiency(self, df: pd.DataFrame, min_candles: int = 20) -> tuple:
        """
        Check if data is sufficient for analysis.
        Provides clear messaging on insufficiency.
        
        Args:
            df: DataFrame to check
            min_candles: Minimum required candles
            
        Returns:
            tuple: (is_sufficient, message)
        """
        if df is None:
            return False, "No data retrieved - symbol may be invalid or delisted"
        
        if len(df) == 0:
            return False, "Data is empty - no candles available for this timeframe"
        
        if len(df) < min_candles:
            return False, f"Insufficient data: {len(df)} candles, need {min_candles} minimum"
        
        # Check for recent data (not stale)
        latest_time = df['Timestamp'].iloc[-1]
        age = datetime.now() - latest_time
        from datetime import timedelta
        if age > timedelta(hours=24):
            return False, f"Data is stale: latest candle is {age.days} days old"
        
        return True, f"Data OK: {len(df)} candles"
    
    def normalize_symbol_precision(self, symbol: str, price: float) -> float:
        """
        Normalize price to symbol's decimal precision (cross-broker compatibility).
        Different brokers use different precisions (4 vs 5 decimals for EURUSD, etc).
        
        Args:
            symbol: Symbol name
            price: Price to normalize
            
        Returns:
            float: Normalized price
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.debug(f"Cannot normalize {symbol} - using default precision")
                return round(price, 5)  # Default to 5 decimals
            
            # Use symbol's digits property for precision
            precision = symbol_info.digits
            return round(price, precision)
        
        except Exception as e:
            self.logger.debug(f"Error normalizing {symbol} precision: {e}")
            return round(price, 5)
