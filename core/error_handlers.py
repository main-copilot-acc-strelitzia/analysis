"""
Error Handling and Robustness Utilities.

Retry logic for MT5 operations, graceful degradation,
clear error messages, disconnect/reconnect handling.
"""

import time
from typing import Callable, TypeVar, Optional, Any
from functools import wraps
import MetaTrader5 as mt5

from core.logger import Logger


T = TypeVar('T')


class MT5Error(Exception):
    """Base exception for MT5 operations."""
    pass


class MT5ConnectionError(MT5Error):
    """MT5 connection or initialization error."""
    pass


class MT5DataError(MT5Error):
    """MT5 data retrieval or validation error."""
    pass


class MT5TimeoutError(MT5Error):
    """MT5 operation timeout."""
    pass


def retry_on_disconnect(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    logger: Optional[Logger] = None
):
    """
    Retry decorator for MT5 operations that may fail due to disconnects.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay each retry
        logger: Logger instance
    """
    if logger is None:
        logger = Logger.get_instance()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Check MT5 connection
                    if not mt5.initialize():
                        raise MT5ConnectionError("MT5 not initialized")
                    
                    return func(*args, **kwargs)
                
                except MT5ConnectionError as e:
                    last_error = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            "MT5 connection error in %s (attempt %d/%d), retrying in %.1fs: %s",
                            func.__name__, attempt + 1, max_retries + 1,
                            current_delay, str(e)
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "MT5 connection error in %s after %d attempts: %s",
                            func.__name__, max_retries + 1, str(e)
                        )
                
                except Exception as e:
                    # Non-connection errors, don't retry
                    logger.error("Error in %s: %s", func.__name__, str(e))
                    raise
            
            raise last_error or MT5ConnectionError("MT5 operation failed after retries")
        
        return wrapper
    
    return decorator


def handle_missing_data(
    default_value: Any = None,
    logger: Optional[Logger] = None
):
    """
    Wrapper for handling missing data gracefully.
    
    Returns default value if operation fails.
    """
    if logger is None:
        logger = Logger.get_instance()
    
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.debug(
                    "Data retrieval error in %s, returning default: %s",
                    func.__name__, str(e)
                )
                return default_value
        
        return wrapper
    
    return decorator


class ErrorRecoveryManager:
    """Manages error recovery and disconnect handling."""
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize recovery manager."""
        self.logger = logger or Logger.get_instance()
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5
        self._in_error_state = False
    
    def record_error(self) -> bool:
        """
        Record an error occurrence.
        
        Returns:
            True if within acceptable error threshold, False if exceeded
        """
        self._consecutive_errors += 1
        
        if self._consecutive_errors >= self._max_consecutive_errors:
            self._in_error_state = True
            self.logger.error(
                "Maximum consecutive errors reached (%d). System in error state.",
                self._max_consecutive_errors
            )
            return False
        
        return True
    
    def record_success(self) -> None:
        """Record successful operation (resets error count)."""
        if self._consecutive_errors > 0:
            self.logger.info("Error recovered. Consecutive errors reset.")
            self._consecutive_errors = 0
            self._in_error_state = False
    
    def is_in_error_state(self) -> bool:
        """Check if system is in error state."""
        return self._in_error_state
    
    def reset_error_state(self) -> None:
        """Manually reset error state (after fixing underlying issue)."""
        self._consecutive_errors = 0
        self._in_error_state = False
        self.logger.info("Error state manually reset")


def validate_mt5_connection() -> bool:
    """
    Validate MT5 connection and log detailed info.
    
    Returns:
        True if connected and ready, False otherwise
    """
    logger = Logger.get_instance()
    
    try:
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        
        account = mt5.account_info()
        if account is None:
            logger.error("Cannot retrieve MT5 account info")
            return False
        
        logger.info(
            "MT5 connected: Login=%d, Server=%s, Account=%s",
            account.login, account.server, account.name
        )
        return True
    
    except Exception as e:
        logger.error("MT5 connection validation error: %s", str(e))
        return False


# ==================== VALIDATION UTILITY FUNCTIONS ====================
# These functions are available for manual validation checks and may be used
# by different symbol detection and verification routines.
# They are not called in the current main execution path but provide
# reusable validation logic.
# =========================================================================

def validate_symbol(symbol: str) -> bool:
    """
    Validate that symbol exists in MT5.
    
    Returns:
        True if symbol exists and accessible, False otherwise
    """
    logger = Logger.get_instance()
    
    try:
        if not mt5.initialize():
            logger.error("MT5 not initialized")
            return False
        
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.debug("Symbol not found: %s", symbol)
            return False
        
        if not symbol_info.visible:
            logger.warning("Symbol not visible in market watch: %s", symbol)
            return False
        
        return True
    
    except Exception as e:
        logger.error("Error validating symbol %s: %s", symbol, str(e))
        return False


def validate_timeframe(timeframe: int) -> bool:
    """
    Validate that timeframe is valid MT5 timeframe constant.
    
    Returns:
        True if valid, False otherwise
    """
    valid_timeframes = [
        mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M30,
        mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1,
        mt5.TIMEFRAME_W1, mt5.TIMEFRAME_MN1
    ]
    
    return timeframe in valid_timeframes


def get_timeframe_name(timeframe: int) -> str:
    """Get human-readable name for MT5 timeframe constant."""
    mapping = {
        mt5.TIMEFRAME_M1: "M1",
        mt5.TIMEFRAME_M5: "M5",
        mt5.TIMEFRAME_M15: "M15",
        mt5.TIMEFRAME_M30: "M30",
        mt5.TIMEFRAME_H1: "H1",
        mt5.TIMEFRAME_H4: "H4",
        mt5.TIMEFRAME_D1: "D1",
        mt5.TIMEFRAME_W1: "W1",
        mt5.TIMEFRAME_MN1: "MN1"
    }
    
    return mapping.get(timeframe, f"UNKNOWN({timeframe})")


def validate_candle_data(candles: Any) -> bool:
    """
    Validate candle data structure and completeness.
    
    Returns:
        True if candles are valid, False otherwise
    """
    logger = Logger.get_instance()
    
    if candles is None or len(candles) == 0:
        logger.debug("Empty candle data")
        return False
    
    try:
        # Check for required columns
        required_cols = ['open', 'high', 'low', 'close', 'tick_volume', 'time']
        for col in required_cols:
            if col not in candles.columns:
                logger.error("Missing required column in candle data: %s", col)
                return False
        
        # Check for NaN values (within acceptable limits)
        nan_count = candles.isnull().sum().sum()
        if nan_count > len(candles) * 0.1:  # More than 10% NaN
            logger.warning("Too many NaN values in candle data: %d", nan_count)
            return False
        
        # Check OHLC order (in general)
        # Note: Can have exceptions in forex spreads, so not strict check
        
        return True
    
    except Exception as e:
        logger.error("Error validating candle data: %s", str(e))
        return False
