"""
Account Monitor - Runtime account change detection and broker switching support.

Periodically polls MT5 account information and detects account changes
(login, server, broker). Supports runtime broker switching without app restart.
"""

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional
from datetime import datetime

import MetaTrader5 as mt5

from core.logger import Logger


@dataclass
class AccountSnapshot:
    """Snapshot of account state at a point in time."""
    
    login: int
    server: str
    name: str
    company: str
    currency: str
    balance: float
    equity: float
    margin_level: float
    timestamp: datetime
    
    def is_same_account(self, other: "AccountSnapshot") -> bool:
        """Check if two snapshots represent the same account."""
        if other is None:
            return False
        return (
            self.login == other.login and
            self.server == other.server and
            self.company == other.company
        )
    
    def has_changed_significantly(self, other: "AccountSnapshot") -> bool:
        """Check if account state has changed significantly (balance, equity, margin)."""
        if other is None:
            return True
        
        # Significant changes: balance/equity change > 10% or margin level changes
        balance_change = abs(self.balance - other.balance) / max(abs(other.balance), 1)
        equity_change = abs(self.equity - other.equity) / max(abs(other.equity), 1)
        margin_change = abs(self.margin_level - other.margin_level)
        
        return balance_change > 0.10 or equity_change > 0.10 or margin_change > 5


class AccountMonitor:
    """
    Monitors MT5 account for changes and detects broker switching.
    
    Runs in background thread. Periodically captures account snapshot.
    Triggers callbacks when account changes detected.
    """
    
    def __init__(
        self,
        poll_interval: int = 5,
        logger: Optional[Logger] = None
    ):
        """
        Initialize account monitor.
        
        Args:
            poll_interval: Seconds between account polls (default 5)
            logger: Logger instance for logging events
        """
        self.poll_interval = poll_interval
        self.logger = logger or Logger.get_instance()
        
        self._monitoring = False
        self._thread: Optional[threading.Thread] = None
        self._last_snapshot: Optional[AccountSnapshot] = None
        self._on_account_changed: list[Callable[[AccountSnapshot, AccountSnapshot], None]] = []
        self._on_disconnected: list[Callable[[], None]] = []
        self._lock = threading.Lock()
    
    def register_account_changed_callback(
        self,
        callback: Callable[[AccountSnapshot, AccountSnapshot], None]
    ) -> None:
        """
        Register callback for account changes.
        
        Callback signature: callback(old_snapshot, new_snapshot)
        """
        with self._lock:
            self._on_account_changed.append(callback)
    
    def register_disconnected_callback(
        self,
        callback: Callable[[], None]
    ) -> None:
        """Register callback for MT5 disconnect events."""
        with self._lock:
            self._on_disconnected.append(callback)
    
    def start(self) -> None:
        """Start background monitoring thread."""
        with self._lock:
            if self._monitoring:
                self.logger.warning("Account monitor already running")
                return
            
            self._monitoring = True
            self._thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="AccountMonitor"
            )
            self._thread.start()
            self.logger.info("Account monitor started (interval: %ds)", self.poll_interval)
    
    def stop(self) -> None:
        """Stop background monitoring thread."""
        with self._lock:
            if not self._monitoring:
                return
            
            self._monitoring = False
        
        if self._thread:
            self._thread.join(timeout=5)
        
        self.logger.info("Account monitor stopped")
    
    def get_current_snapshot(self) -> Optional[AccountSnapshot]:
        """Get current cached account snapshot."""
        with self._lock:
            return self._last_snapshot
    
    def _capture_snapshot(self) -> Optional[AccountSnapshot]:
        """
        Capture current account snapshot from MT5.
        
        Returns:
            AccountSnapshot or None if MT5 not connected
        """
        try:
            if not mt5.initialize():
                return None
            
            account_info = mt5.account_info()
            if account_info is None:
                return None
            
            return AccountSnapshot(
                login=account_info.login,
                server=account_info.server,
                name=account_info.name,
                company=account_info.company,
                currency=account_info.currency,
                balance=account_info.balance,
                equity=account_info.equity,
                margin_level=account_info.margin_level,
                timestamp=datetime.now()
            )
        
        except Exception as e:
            self.logger.debug("Error capturing account snapshot: %s", str(e))
            return None
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while True:
            with self._lock:
                if not self._monitoring:
                    break
            
            try:
                snapshot = self._capture_snapshot()
                
                if snapshot is None:
                    # MT5 disconnected
                    with self._lock:
                        if self._last_snapshot is not None:
                            self._last_snapshot = None
                            callbacks = list(self._on_disconnected)
                    
                    for callback in callbacks:
                        try:
                            callback()
                        except Exception as e:
                            self.logger.error("Error in disconnect callback: %s", str(e))
                
                else:
                    # MT5 connected
                    with self._lock:
                        old_snapshot = self._last_snapshot
                        self._last_snapshot = snapshot
                        
                        # Check if account changed
                        account_changed = (
                            old_snapshot is None or
                            not snapshot.is_same_account(old_snapshot)
                        )
                        
                        if account_changed:
                            callbacks = list(self._on_account_changed)
                        else:
                            callbacks = []
                    
                    if account_changed and old_snapshot is not None:
                        self.logger.warning(
                            "Account changed detected! Old login: %d, New login: %d, Server: %s",
                            old_snapshot.login,
                            snapshot.login,
                            snapshot.server
                        )
                        
                        for callback in callbacks:
                            try:
                                callback(old_snapshot, snapshot)
                            except Exception as e:
                                self.logger.error("Error in account changed callback: %s", str(e))
            
            except Exception as e:
                self.logger.error("Error in account monitor loop: %s", str(e))
            
            time.sleep(self.poll_interval)
