"""
Safety module to prevent any trading operations.

This module enforces the analysis-only mode of Strelitzia Trader.
It blocks any attempt to place orders, modify accounts, or execute trades.

The application is strictly an analysis tool and must NEVER:
- Place any orders (buy/sell/stop-loss/take-profit)
- Modify account settings
- Execute trades
- Change leverage or margin
- Modify positions
"""

from typing import Any, Callable
from functools import wraps
from core.logger import get_logger


def analysis_only_mode(func: Callable) -> Callable:
    """
    Decorator to enforce analysis-only mode on a function.
    Prevents execution of trading/account-modifying functions.
    
    Args:
        func: Function to wrap
        
    Returns:
        Callable: Wrapped function that raises error if called
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger()
        logger.critical(f"BLOCKED TRADING OPERATION: {func.__name__}")
        raise RuntimeError(
            f"SAFETY VIOLATION: {func.__name__} is not allowed in analysis-only mode. "
            "Strelitzia Trader is strictly an analysis application and cannot execute trades."
        )
    return wrapper


class TradingBlocker:
    """
    Prevents trading operations through MT5 API.
    
    This class monitors MT5 function calls and blocks any that would:
    - Place orders
    - Modify account settings
    - Close/modify positions
    """
    
    def __init__(self):
        """Initialize trading blocker."""
        self.logger = get_logger()
        self.blocked_operations = [
            'order_send',
            'order_modify',
            'order_cancel',
            'order_check',
            'deal_comment',
            'position_modify',
            'position_close',
        ]
        self.logger.info("Trading blocker initialized - analysis-only mode enforced")
    
    def is_trading_function(self, function_name: str) -> bool:
        """
        Check if a function is trading-related and should be blocked.
        
        Args:
            function_name: Name of the function
            
        Returns:
            bool: True if function is trading-related
        """
        function_lower = function_name.lower()
        return any(op in function_lower for op in self.blocked_operations)
    
    def block_if_trading(self, function_name: str) -> None:
        """
        Block execution if function is trading-related.
        
        Args:
            function_name: Name of the function
            
        Raises:
            RuntimeError: If function is trading-related
        """
        if self.is_trading_function(function_name):
            self.logger.critical(f"BLOCKED: Trading operation '{function_name}' attempted")
            raise RuntimeError(
                f"SAFETY VIOLATION: Cannot execute '{function_name}' in analysis-only mode.\n"
                f"Strelitzia Trader is a market analysis tool only - it does not place trades."
            )


class SafeAccountAccessor:
    """
    Provides safe read-only access to account information.
    Logs all account accesses for audit trail.
    """
    
    def __init__(self):
        """Initialize safe accessor."""
        self.logger = get_logger()
        self.access_count = 0
    
    def log_account_access(self, access_type: str, details: str) -> None:
        """
        Log account information access.
        Part of audit trail for analysis-only mode compliance.
        
        Args:
            access_type: Type of access (e.g., 'read_balance', 'read_positions')
            details: Additional details
        """
        self.access_count += 1
        self.logger.info(f"Account access #{self.access_count}: {access_type} - {details}")
    
    def safe_read_balance(self) -> float:
        """
        Safely read account balance (read-only, no modification).
        
        Returns:
            float: Account balance
        """
        import MetaTrader5 as mt5
        try:
            account_info = mt5.account_info()
            if account_info:
                balance = account_info.balance
                self.log_account_access("read_balance", f"balance={balance}")
                return balance
            return 0.0
        except Exception as e:
            self.logger.error(f"Error reading balance: {e}")
            return 0.0
    
    def safe_read_positions(self) -> list:
        """
        Safely read open positions (read-only, no modification).
        
        Returns:
            list: Open positions (for informational purposes only)
        """
        import MetaTrader5 as mt5
        try:
            positions = mt5.positions_get()
            count = len(positions) if positions else 0
            self.log_account_access("read_positions", f"count={count}")
            return list(positions) if positions else []
        except Exception as e:
            self.logger.error(f"Error reading positions: {e}")
            return []


# Global trading blocker instance
_trading_blocker = TradingBlocker()
_account_accessor = SafeAccountAccessor()


def get_trading_blocker() -> TradingBlocker:
    """Get global trading blocker instance."""
    return _trading_blocker


def get_safe_account_accessor() -> SafeAccountAccessor:
    """Get global safe account accessor instance."""
    return _account_accessor
