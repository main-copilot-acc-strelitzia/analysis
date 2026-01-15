"""MetaTrader 5 account information retrieval."""

import MetaTrader5 as mt5
from typing import Optional, Dict, Any
from core.logger import get_logger


class AccountManager:
    """Manages MT5 account information."""

    def __init__(self):
        """Initialize account manager."""
        self.logger = get_logger()

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve current account information.
        
        Returns:
            Optional[Dict[str, Any]]: Account info dictionary or None.
        """
        try:
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.warning("Unable to retrieve account information")
                return None

            return {
                'login': account_info.login,
                'server': account_info.server,
                'name': account_info.name,
                'currency': account_info.currency,
                'balance': account_info.balance,
                'credit': account_info.credit,
                'equity': account_info.equity,
                'profit': account_info.profit,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'margin_so_call': account_info.margin_so_call,
                'margin_so_so': account_info.margin_so_so,
                'leverage': account_info.leverage,
                'limit_orders': account_info.limit_orders,
                'trade_allowed': account_info.trade_allowed,
                'trade_expert': account_info.trade_expert,
                'stop_out_mode': getattr(account_info, 'stop_out_mode', None),
                'fifo_close': getattr(account_info, 'fifo_close', None),
            }

        except Exception as e:
            self.logger.error(f"Error retrieving account info: {e}")
            return None

    def get_balance(self) -> Optional[float]:
        """
        Get account balance.
        
        Returns:
            Optional[float]: Balance or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.balance
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving balance: {e}")
            return None

    def get_equity(self) -> Optional[float]:
        """
        Get account equity.
        
        Returns:
            Optional[float]: Equity or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.equity
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving equity: {e}")
            return None

    def get_profit(self) -> Optional[float]:
        """
        Get account profit/loss.
        
        Returns:
            Optional[float]: Profit or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.profit
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving profit: {e}")
            return None

    def get_leverage(self) -> Optional[int]:
        """
        Get account leverage.
        
        Returns:
            Optional[int]: Leverage or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.leverage
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving leverage: {e}")
            return None

    def get_server(self) -> Optional[str]:
        """
        Get broker server name.
        
        Returns:
            Optional[str]: Server name or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.server
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving server: {e}")
            return None

    def get_account_type(self) -> Optional[str]:
        """
        Get account type/name.
        
        Returns:
            Optional[str]: Account type or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.name
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving account type: {e}")
            return None

    def is_trading_allowed(self) -> bool:
        """
        Check if trading is allowed on account.
        
        Returns:
            bool: True if trading allowed.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.trade_allowed
            return False

        except Exception as e:
            self.logger.error(f"Error checking trade allowed: {e}")
            return False

    def get_margin_level(self) -> Optional[float]:
        """
        Get current margin level.
        
        Returns:
            Optional[float]: Margin level or None if unavailable.
        """
        try:
            account_info = mt5.account_info()
            if account_info:
                return account_info.margin_level
            return None

        except Exception as e:
            self.logger.error(f"Error retrieving margin level: {e}")
            return None
