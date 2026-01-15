"""MetaTrader 5 connection handler."""

import MetaTrader5 as mt5
from typing import Optional, Dict, Any
from core.logger import get_logger


class MT5Connector:
    """Manages connection to MetaTrader 5 terminal with session awareness."""

    def __init__(self):
        """Initialize MT5 connector."""
        self.logger = get_logger()
        self._connected = False
        self._session_account = None  # Track current account
        self._session_server = None   # Track current server
        self._session_id = None       # Unique session identifier

    def connect(self) -> bool:
        """
        Establish connection to MT5 terminal.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            if not mt5.initialize():
                self.logger.error(
                    f"Failed to initialize MT5: {mt5.last_error()}"
                )
                return False

            self._connected = True
            self.logger.info("Successfully connected to MT5 terminal")
            return True

        except Exception as e:
            self.logger.error(f"Exception during MT5 connection: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Close connection to MT5 terminal.
        
        Returns:
            bool: True if disconnection successful.
        """
        try:
            if self._connected:
                mt5.shutdown()
                self._connected = False
                self.logger.info("MT5 connection closed")
                return True
            return True

        except Exception as e:
            self.logger.error(f"Exception during MT5 disconnection: {e}")
            return False

    def is_connected(self) -> bool:
        """
        Check if connected to MT5.
        
        Returns:
            bool: Connection status.
        """
        return self._connected
    
    def detect_session_change(self) -> bool:
        """
        Detect if account or server has changed during session.
        Used for auto-reinitialization of analysis engine.
        
        Returns:
            bool: True if session changed (account/server), False otherwise.
        """
        try:
            account_info = mt5.account_info()
            if account_info is None:
                self.logger.warning("Cannot verify account - MT5 may be disconnected")
                return True  # Treat as session change to trigger reinit
            
            current_account = account_info.login
            current_server = account_info.server
            
            # First run - initialize session tracking
            if self._session_account is None:
                self._session_account = current_account
                self._session_server = current_server
                self._session_id = f"{current_account}_{current_server}"
                self.logger.info(f"Session established: Account {current_account} @ {current_server}")
                return False
            
            # Check for account change
            if current_account != self._session_account:
                self.logger.warning(
                    f"Account changed: {self._session_account} → {current_account} (requires reinitialization)"
                )
                self._session_account = current_account
                self._session_id = f"{current_account}_{current_server}"
                return True
            
            # Check for server change
            if current_server != self._session_server:
                self.logger.warning(
                    f"Server changed: {self._session_server} → {current_server} (requires reinitialization)"
                )
                self._session_server = current_server
                self._session_id = f"{current_account}_{current_server}"
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting session change: {e}")
            return True  # Treat as session change on error
    
    def get_session_id(self) -> Optional[str]:
        """
        Get current session identifier (account_server).
        
        Returns:
            Optional[str]: Session ID or None if not connected.
        """
        return self._session_id

    def get_terminal_info(self) -> Optional[Dict[str, Any]]:
        """
        Get MetaTrader 5 terminal information.
        
        Returns:
            Optional[Dict[str, Any]]: Terminal info or None if unavailable.
        """
        try:
            info = mt5.terminal_info()
            if info is None:
                self.logger.warning("Unable to retrieve terminal info")
                return None

            return {
                'name': info.name,
                'language': info.language,
                'path': info.path,
                'data_path': info.data_path,
                'commondata_path': info.commondata_path,
                'build': info.build,
            }

        except Exception as e:
            self.logger.error(f"Error retrieving terminal info: {e}")
            return None

    def get_version(self) -> Optional[tuple]:
        """
        Get MetaTrader 5 version.
        
        Returns:
            Optional[tuple]: Version tuple (build, date, release) or None.
        """
        try:
            version = mt5.version()
            return version

        except Exception as e:
            self.logger.error(f"Error retrieving MT5 version: {e}")
            return None

    def check_accessibility(self) -> bool:
        """
        Check if MT5 terminal is accessible.
        
        Returns:
            bool: True if accessible, False otherwise.
        """
        try:
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                self.logger.error("MT5 terminal not accessible - not running")
                return False

            self.logger.debug(f"MT5 terminal is accessible: {terminal_info.name}")
            return True

        except Exception as e:
            self.logger.error(f"MT5 accessibility check failed: {e}")
            return False

    def get_symbols(self) -> Optional[list]:
        """
        Retrieve a list of available symbols from the MT5 terminal.

        Returns a list of dicts: {"name", "path", "visible"}
        """
        try:
            # Ensure mt5 initialized
            if not self._connected:
                try:
                    mt5.initialize()
                    self._connected = True
                except Exception:
                    self.logger.exception("Failed to initialize MT5 for symbol retrieval")
                    return None

            syms = mt5.symbols_get()
            out = []
            if syms is None:
                return out
            for s in syms:
                out.append({
                    'name': s.name,
                    'path': getattr(s, 'path', None),
                    'visible': getattr(s, 'visible', None),
                })
            return out

        except Exception as e:
            self.logger.exception(f"Error retrieving symbols: {e}")
            return None
