"""
Startup Verification Module - Ensures explicit, deterministic startup sequence.

Verifies all requirements before app starts:
- MT5 availability
- Account connectivity
- Symbol availability
- User clarity at every step
"""

from typing import Optional, Dict, Any
import MetaTrader5 as mt5
from core.logger import Logger


class StartupVerifier:
    """
    Explicit startup verification with clear messaging.
    
    Ensures:
    1. MT5 is running and accessible
    2. Account information is readable
    3. Symbols can be fetched
    4. User understands what account is active
    5. All failures have clear instructions
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize startup verifier."""
        self.logger = logger or Logger.get_instance()
    
    def verify_startup_sequence(self) -> Optional[Dict[str, Any]]:
        """
        Execute complete startup verification sequence.
        
        Returns:
            Dict with startup results or None if critical failure
        """
        print("\n" + "="*70)
        print("  STRELITZIA TRADER - MetaTrader 5 Analysis Engine")
        print("  Production-Grade Market Analysis System")
        print("="*70 + "\n")
        
        # Step 1: Check MT5 availability
        print("[STEP 1] Verifying MetaTrader 5 Availability...")
        mt5_status = self._verify_mt5_availability()
        if not mt5_status:
            return None
        
        # Step 2: Establish MT5 connection
        print("\n[STEP 2] Establishing MT5 Connection...")
        connection_status = self._verify_mt5_connection()
        if not connection_status:
            return None
        
        # Step 3: Get account information
        print("\n[STEP 3] Reading Account Information...")
        account_info = self._verify_account_info()
        if not account_info:
            return None
        
        # Step 4: Display broker context
        print("\n[STEP 4] Displaying Broker Context...")
        self._display_broker_context(account_info)
        
        # Step 5: Verify symbol availability
        print("\n[STEP 5] Verifying Symbol Availability...")
        symbol_count = self._verify_symbol_availability()
        if symbol_count is None or symbol_count == 0:
            return None
        
        print(f"  ✓ {symbol_count} symbols available from {account_info['server']}")
        
        # Step 6: Ready for user input
        print("\n[STEP 6] Ready for User Input...")
        print("  ✓ System ready")
        print("  ✓ Waiting for user to select category and symbols")
        
        return {
            'account': account_info,
            'symbols': symbol_count,
            'broker': account_info.get('company', 'Unknown'),
            'server': account_info.get('server', 'Unknown'),
            'status': 'ready'
        }
    
    def _verify_mt5_availability(self) -> bool:
        """
        Check if MT5 is running and accessible.
        
        Returns:
            True if MT5 is available, False otherwise
        """
        print("  Checking if MetaTrader 5 terminal is running...")
        
        try:
            # Attempt to check MT5
            initialized = mt5.initialize()
            
            if initialized:
                print("  ✓ MetaTrader 5 is running and accessible")
                return True
            else:
                # MT5 not initialized
                print("\n" + "!"*70)
                print("  ERROR: MetaTrader 5 Terminal Not Accessible")
                print("!"*70)
                print("\n  REQUIRED ACTION:")
                print("  ─────────────────────────────────────────────────────")
                print("  1. Ensure MetaTrader 5 terminal is running")
                print("  2. If using Wine on Linux/Mac:")
                print("     - Verify Wine is properly configured")
                print("     - Check that MT5 executable is accessible via Wine")
                print("  3. Ensure MT5 terminal window is open and responsive")
                print("  4. If MT5 is running:")
                print("     - Close and restart MT5")
                print("     - Try this application again")
                print("  ─────────────────────────────────────────────────────\n")
                self.logger.critical("MT5 not available")
                return False
        
        except Exception as e:
            print("\n" + "!"*70)
            print("  ERROR: Cannot Access MetaTrader 5")
            print("!"*70)
            print(f"\n  Technical Detail: {str(e)}")
            print("\n  REQUIRED ACTION:")
            print("  ─────────────────────────────────────────────────────")
            print("  1. Ensure MetaTrader 5 is installed")
            print("  2. Ensure MetaTrader 5 terminal is running")
            print("  3. Ensure you have the MetaTrader5 Python module installed:")
            print("     pip install MetaTrader5")
            print("  4. Try again")
            print("  ─────────────────────────────────────────────────────\n")
            self.logger.critical(f"MT5 access error: {e}")
            return False
    
    def _verify_mt5_connection(self) -> bool:
        """
        Establish MT5 connection.
        
        Returns:
            True if connected, False otherwise
        """
        print("  Connecting to MT5 terminal...")
        
        try:
            if not mt5.initialize():
                print("  ✗ Failed to initialize MT5")
                return False
            
            # Try to get account info to verify connection
            account = mt5.account_info()
            if account is None:
                print("  ✗ Connected to MT5 but cannot read account info")
                print("\n  This may indicate:")
                print("  - No account logged in to MT5 terminal")
                print("  - MT5 account is not connected to server")
                print("  - MT5 permissions issue\n")
                return False
            
            print("  ✓ Successfully connected to MT5 terminal")
            return True
        
        except Exception as e:
            print(f"  ✗ Connection error: {e}")
            self.logger.error(f"MT5 connection error: {e}")
            return False
    
    def _verify_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Read account information.
        
        Returns:
            Dict with account info or None if failed
        """
        print("  Reading account information...")
        
        try:
            account = mt5.account_info()
            
            if account is None:
                print("  ✗ Cannot read account information")
                print("  Ensure an account is logged in to MT5 terminal\n")
                return None
            
            account_info = {
                'login': account.login,
                'name': account.name,
                'company': account.company,
                'server': account.server,
                'currency': account.currency,
                'balance': account.balance,
                'equity': account.equity,
                'margin_level': account.margin_level,
            }
            
            print(f"  ✓ Account information retrieved")
            print(f"    - Login: {account_info['login']}")
            print(f"    - Name: {account_info['name']}")
            print(f"    - Server: {account_info['server']}")
            print(f"    - Company: {account_info['company']}")
            
            return account_info
        
        except Exception as e:
            print(f"  ✗ Error reading account: {e}")
            self.logger.error(f"Account info error: {e}")
            return None
    
    def _display_broker_context(self, account_info: Dict[str, Any]):
        """
        Display current broker and account context to user.
        
        This ensures user always knows which account is active.
        """
        print("  Broker Context (ACTIVE ACCOUNT):")
        print("  ─────────────────────────────────────────────────────")
        print(f"    Broker:          {account_info['company']}")
        print(f"    Account Number:  {account_info['login']}")
        print(f"    Account Name:    {account_info['name']}")
        print(f"    Server:          {account_info['server']}")
        print(f"    Currency:        {account_info['currency']}")
        print(f"    Balance:         {account_info['balance']:.2f}")
        print(f"    Equity:          {account_info['equity']:.2f}")
        print(f"    Margin Level:    {account_info['margin_level']:.2f}%")
        print("  ─────────────────────────────────────────────────────")
        print("  ✓ This account will be used for all analysis")
    
    def _verify_symbol_availability(self) -> Optional[int]:
        """
        Verify that symbols can be fetched from MT5.
        
        Returns:
            Number of available symbols or None if error
        """
        print("  Fetching available symbols from MT5...")
        
        try:
            symbols = mt5.symbols_get()
            
            if symbols is None or len(symbols) == 0:
                print("  ✗ No symbols available from MT5")
                print("\n  This may indicate:")
                print("  - No account logged in to MT5 terminal")
                print("  - MT5 terminal connection issue")
                print("  - Broker provides no symbols\n")
                return None
            
            symbol_count = len(symbols)
            print(f"  ✓ Retrieved {symbol_count} symbols from MT5")
            
            # Sample a few symbols to show they're real
            sample_symbols = [s.name for s in symbols[:3]]
            print(f"    Sample: {', '.join(sample_symbols)}")
            
            return symbol_count
        
        except Exception as e:
            print(f"  ✗ Error fetching symbols: {e}")
            self.logger.error(f"Symbol fetch error: {e}")
            return None


class StartupStatusDisplay:
    """Display startup status with clear formatting."""
    
    @staticmethod
    def show_startup_complete():
        """Show startup completion message."""
        print("\n" + "="*70)
        print("  STARTUP COMPLETE - SYSTEM READY")
        print("="*70)
        print("\n  Next: Select symbol category and symbols to analyze")
        print("\n")
    
    @staticmethod
    def show_startup_failed():
        """Show startup failed message."""
        print("\n" + "!"*70)
        print("  STARTUP FAILED")
        print("!"*70)
        print("\n  Please resolve the error above and try again.")
        print("\n")
    
    @staticmethod
    def show_waiting_for_user():
        """Show waiting for user message."""
        print("\n" + "-"*70)
        print("  Waiting for user input...")
        print("-"*70 + "\n")
