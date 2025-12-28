#!/usr/bin/env python3
"""
MT5 Account & Symbol Detector
Comprehensive cross-platform application for detecting MT5 accounts and symbols.

Supports: Windows, Linux (with WINE), macOS
Author: Strelitzia System
Date: December 27, 2025
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time

# Try to import MetaTrader5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️  MetaTrader5 package not found. Install with: pip install MetaTrader5")


class OSDetector:
    """Detect operating system and manage MT5 startup."""
    
    @staticmethod
    def get_os() -> str:
        """
        Detect operating system.
        Returns: 'Windows', 'Linux', or 'Darwin' (macOS)
        """
        system = platform.system()
        return system
    
    @staticmethod
    def get_os_name() -> str:
        """Get human-readable OS name."""
        os_map = {
            'Windows': 'Windows',
            'Linux': 'Linux (WINE)',
            'Darwin': 'macOS'
        }
        return os_map.get(OSDetector.get_os(), 'Unknown')
    
    @staticmethod
    def is_mt5_running() -> bool:
        """Check if MT5 process is running."""
        current_os = OSDetector.get_os()
        
        if current_os == 'Windows':
            try:
                import psutil
                return any('terminal.exe' in proc.name().lower() for proc in psutil.process_iter())
            except ImportError:
                # Fallback: try to get MT5 window
                try:
                    import win32gui
                    return win32gui.FindWindow(None, 'MetaTrader 5') != 0
                except:
                    return False
        
        elif current_os == 'Linux':
            try:
                result = subprocess.run(['pgrep', '-f', 'wine.*terminal.exe'], 
                                      capture_output=True, timeout=2)
                return result.returncode == 0
            except:
                return False
        
        elif current_os == 'Darwin':  # macOS
            try:
                result = subprocess.run(['pgrep', '-f', 'Wine.*terminal.exe'], 
                                      capture_output=True, timeout=2)
                return result.returncode == 0
            except:
                return False
        
        return False
    
    @staticmethod
    def start_mt5_wine() -> bool:
        """
        Start MT5 using WINE on Linux.
        Returns: True if started successfully, False otherwise
        """
        try:
            # Try to find MT5 installation using pathlib for cross-platform compatibility
            home = Path.home()
            possible_paths = [
                home / '.wine/drive_c/Program Files/MetaTrader 5/terminal.exe',
                home / '.wine/drive_c/Program Files (x86)/MetaTrader 5/terminal.exe',
                Path('/opt/mt5/terminal.exe'),
                Path('/usr/local/mt5/terminal.exe')
            ]
            
            mt5_exe = None
            for path in possible_paths:
                if path.exists():
                    mt5_exe = str(path)
                    break
            
            if not mt5_exe:
                print("❌ MT5 installation not found. Please install MT5 via WINE first.")
                return False
            
            print(f"📡 Starting MT5 from: {mt5_exe}")
            subprocess.Popen(['wine', mt5_exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for MT5 to fully initialize
            print("⏳ Waiting for MT5 to initialize... (30 seconds)")
            for i in range(30):
                time.sleep(1)
                if OSDetector.is_mt5_running():
                    print("✅ MT5 started successfully!")
                    return True
                sys.stdout.write(f"\r  {i+1}/30 seconds... ")
                sys.stdout.flush()
            
            return False
        except Exception as e:
            print(f"❌ Error starting MT5: {e}")
            return False
    
    @staticmethod
    def ensure_mt5_running():
        """Ensure MT5 is running, prompt user if not."""
        if OSDetector.is_mt5_running():
            return True
        
        print("\n" + "="*60)
        print("⚠️  MetaTrader 5 is not running")
        print("="*60)
        
        current_os = OSDetector.get_os()
        
        if current_os == 'Windows':
            response = input("\n❓ Would you like to start MT5? (y/n): ").lower()
            if response == 'y':
                try:
                    # Try to find and start MT5
                    subprocess.Popen('C:\\Program Files\\MetaTrader 5\\terminal.exe')
                    time.sleep(10)
                    if OSDetector.is_mt5_running():
                        return True
                except:
                    print("❌ Could not start MT5. Please start it manually.")
                    return False
            else:
                print("❌ Cannot proceed without MT5 running.")
                return False
        
        elif current_os == 'Linux':
            response = input("\n❓ Would you like to start MT5 via WINE? (y/n): ").lower()
            if response == 'y':
                return OSDetector.start_mt5_wine()
            else:
                print("❌ Cannot proceed without MT5 running.")
                return False
        
        elif current_os == 'Darwin':  # macOS
            print("\n📋 Please start MT5 manually (WineBottler or similar)")
            print("Once MT5 is running, press Enter to continue...")
            input()
            if OSDetector.is_mt5_running():
                return True
            else:
                print("❌ MT5 still not running.")
                return False
        
        return False


class CrossPlatformLogger:
    """Handle cross-platform logging to file and console."""
    
    def __init__(self, log_file: str = 'mt5_symbol_log.txt'):
        """Initialize logger."""
        self.log_file = log_file
        self.os_name = OSDetector.get_os_name()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_startup(self):
        """Log application startup."""
        self.logger.info(f"{'='*60}")
        self.logger.info(f"MT5 Account & Symbol Detector Started")
        self.logger.info(f"Operating System: {self.os_name}")
        self.logger.info(f"Python Version: {platform.python_version()}")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"{'='*60}")
    
    def log_account(self, account_info: Dict):
        """Log account information."""
        self.logger.info(f"ACCOUNT | Login: {account_info.get('login', 'N/A')} | "
                        f"Broker: {account_info.get('server', 'N/A')} | "
                        f"Balance: {account_info.get('balance', 'N/A')}")
    
    def log_symbol(self, account: int, symbol: str, details: Dict):
        """Log symbol information."""
        self.logger.info(f"SYMBOL | Account: {account} | Symbol: {symbol} | "
                        f"Type: {details.get('type', 'N/A')} | "
                        f"Pip: {details.get('pip', 'N/A')}")
    
    def log_error(self, error_type: str, message: str):
        """Log error."""
        self.logger.error(f"ERROR | {error_type} | {message}")
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(f"INFO | {message}")


class MT5Connector:
    """Manage MT5 connection and initialization."""
    
    def __init__(self, logger: CrossPlatformLogger):
        """Initialize MT5 connector."""
        self.logger = logger
        self.connected = False
    
    def connect(self) -> bool:
        """
        Connect to MT5 terminal.
        Returns: True if successful, False otherwise
        """
        if not MT5_AVAILABLE:
            self.logger.log_error('MT5_IMPORT', 'MetaTrader5 package not installed')
            return False
        
        try:
            if not mt5.initialize():
                self.logger.log_error('MT5_INIT', f'Failed to initialize MT5: {mt5.last_error()}')
                return False
            
            self.connected = True
            self.logger.log_info('MT5 connection established')
            return True
        except Exception as e:
            self.logger.log_error('MT5_CONNECT', str(e))
            return False
    
    def disconnect(self):
        """Disconnect from MT5."""
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            self.logger.log_info('MT5 connection closed')
    
    def is_connected(self) -> bool:
        """Check if connected to MT5."""
        return self.connected


class AccountManager:
    """Retrieve and manage MT5 accounts."""
    
    def __init__(self, connector: MT5Connector, logger: CrossPlatformLogger):
        """Initialize account manager."""
        self.connector = connector
        self.logger = logger
        self.accounts = []
    
    def detect_accounts(self) -> List[Dict]:
        """
        Detect all logged-in accounts in MT5.
        Returns: List of account information dictionaries
        """
        if not self.connector.is_connected():
            self.logger.log_error('ACCOUNT_DETECTION', 'Not connected to MT5')
            return []
        
        try:
            # Get current account info
            account_info = mt5.account_info()
            
            if account_info is None:
                self.logger.log_error('ACCOUNT_DETECTION', 'No account information available')
                return []
            
            account_dict = {
                'login': account_info.login,
                'server': account_info.server,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'currency': account_info.currency,
                'leverage': account_info.leverage,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit,
                'name': account_info.name,
            }
            
            self.accounts = [account_dict]
            self.logger.log_account(account_dict)
            return self.accounts
        
        except Exception as e:
            self.logger.log_error('ACCOUNT_DETECTION', str(e))
            return []
    
    def get_accounts(self) -> List[Dict]:
        """Get list of detected accounts."""
        return self.accounts


class SymbolManager:
    """Retrieve and manage MT5 symbols."""
    
    SYMBOL_CATEGORIES = {
        'Forex': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'NZDUSD', 'USDCAD',
                  'EURJPY', 'GBPJPY', 'EURGBP', 'EURCAD', 'EURCHF', 'AUDJPY', 'CADJPY'],
        'Synthetics': ['Boom', 'Crash', 'RiseFall', 'HighLow', 'StepRise', 'StepFall',
                      'Volatility', 'VIX'],
        'Commodities': ['XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'WTI', 'BRENT', 
                       'NATGAS', 'COPPER', 'GOLD', 'SILVER'],
        'Crypto': ['BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'BCHUSD', 'ADAUSD'],
        'Indices': ['SPX', 'FTSE', 'DAX', 'CAC40', 'NIKKEI', 'ASX', 'HSI'],
        'Stocks': []
    }
    
    def __init__(self, connector: MT5Connector, logger: CrossPlatformLogger):
        """Initialize symbol manager."""
        self.connector = connector
        self.logger = logger
        self.symbols = []
    
    def detect_symbols(self, account_login: int) -> Dict[str, List[Dict]]:
        """
        Detect all available symbols for an account.
        Returns: Dictionary of symbols grouped by category
        """
        if not self.connector.is_connected():
            self.logger.log_error('SYMBOL_DETECTION', 'Not connected to MT5')
            return {}
        
        try:
            # Get all symbols
            all_symbols = mt5.symbols_get()
            
            if not all_symbols:
                self.logger.log_error('SYMBOL_DETECTION', 'No symbols available')
                return {}
            
            # Organize symbols by category
            categorized = {
                'Forex': [],
                'Synthetics': [],
                'Commodities': [],
                'Crypto': [],
                'Indices': [],
                'Stocks': [],
                'Other': []
            }
            
            for symbol in all_symbols:
                symbol_info = self._get_symbol_details(symbol)
                if symbol_info:
                    category = self._categorize_symbol(symbol.name)
                    categorized[category].append(symbol_info)
                    self.logger.log_symbol(account_login, symbol.name, symbol_info)
            
            self.symbols = categorized
            return categorized
        
        except Exception as e:
            self.logger.log_error('SYMBOL_DETECTION', str(e))
            return {}
    
    def _categorize_symbol(self, symbol_name: str) -> str:
        """Categorize a symbol by name."""
        symbol_upper = symbol_name.upper()
        
        for category, symbols_list in self.SYMBOL_CATEGORIES.items():
            if any(sym in symbol_upper for sym in symbols_list):
                return category
        
        # Additional checks
        if any(x in symbol_upper for x in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']):
            if symbol_upper.count('USD') == 1 or any(x in symbol_upper for x in ['EURUSD', 'GBPUSD']):
                return 'Forex'
        
        if any(x in symbol_upper for x in ['XAU', 'XAG', 'XPT', 'XPD']):
            return 'Commodities'
        
        if any(x in symbol_upper for x in ['BTC', 'ETH', 'XRP', 'LTC', 'BCH']):
            return 'Crypto'
        
        if any(x in symbol_upper for x in ['BOOM', 'CRASH', 'RISE', 'FALL', 'VOLATILITY']):
            return 'Synthetics'
        
        return 'Other'
    
    def _get_symbol_details(self, symbol) -> Optional[Dict]:
        """Get detailed information for a symbol."""
        try:
            return {
                'name': symbol.name,
                'description': symbol.description,
                'pip': symbol.point,
                'digits': symbol.digits,
                'bid': symbol.bid,
                'ask': symbol.ask,
                'type': self._get_symbol_type(symbol),
                'contract_size': symbol.trade_contract_size,
                'margin': symbol.margin_initial if hasattr(symbol, 'margin_initial') else 'N/A',
                'point_value': symbol.trade_contract_size * symbol.point,
                'trade_mode': symbol.trade_mode,
                'session_open': getattr(symbol, 'session_open', 'N/A'),
                'session_close': getattr(symbol, 'session_close', 'N/A'),
            }
        except Exception as e:
            self.logger.log_error('SYMBOL_DETAILS', f'Symbol: {symbol.name}, Error: {str(e)}')
            return None
    
    @staticmethod
    def _get_symbol_type(symbol) -> str:
        """Get symbol type as human-readable string."""
        type_map = {
            0: 'Forex',
            1: 'CFD',
            2: 'Future',
            3: 'Stock',
            4: 'Crypto'
        }
        try:
            return type_map.get(symbol.type, 'Unknown')
        except:
            return 'Unknown'
    
    def get_symbols(self) -> Dict[str, List[Dict]]:
        """Get organized symbols."""
        return self.symbols


class TerminalUI:
    """Terminal user interface for account and symbol selection."""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(title: str):
        """Print formatted header."""
        print("\n" + "="*80)
        print(f"  {title}".ljust(80))
        print("="*80 + "\n")
    
    @staticmethod
    def print_section(title: str):
        """Print formatted section."""
        print(f"\n{title}")
        print("-" * 80)
    
    @staticmethod
    def display_accounts(accounts: List[Dict]) -> Optional[Dict]:
        """Display accounts and allow selection."""
        if not accounts:
            print("\n❌ No accounts found!")
            return None
        
        TerminalUI.print_header("Available MT5 Accounts")
        
        for idx, account in enumerate(accounts, 1):
            print(f"\n📊 Account {idx}:")
            print(f"  Login:       {account.get('login', 'N/A')}")
            print(f"  Server:      {account.get('server', 'N/A')}")
            print(f"  Name:        {account.get('name', 'N/A')}")
            print(f"  Balance:     {account.get('balance', 'N/A')} {account.get('currency', 'N/A')}")
            print(f"  Equity:      {account.get('equity', 'N/A')} {account.get('currency', 'N/A')}")
            print(f"  Leverage:    1:{account.get('leverage', 'N/A')}")
            print(f"  Margin:      {account.get('margin', 'N/A')} {account.get('currency', 'N/A')}")
            print(f"  Margin Free: {account.get('margin_free', 'N/A')} {account.get('currency', 'N/A')}")
            print(f"  Profit:      {account.get('profit', 'N/A')} {account.get('currency', 'N/A')}")
        
        if len(accounts) == 1:
            return accounts[0]
        
        while True:
            try:
                choice = int(input(f"\n👉 Select account (1-{len(accounts)}): "))
                if 1 <= choice <= len(accounts):
                    return accounts[choice - 1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(accounts)}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    @staticmethod
    def display_symbols(symbols_dict: Dict[str, List[Dict]]):
        """Display all symbols organized by category."""
        TerminalUI.print_header("Available Symbols")
        
        total_symbols = sum(len(v) for v in symbols_dict.values())
        print(f"📈 Total Symbols Available: {total_symbols}\n")
        
        for category, symbols in symbols_dict.items():
            if symbols:
                TerminalUI.print_section(f"{category} ({len(symbols)} symbols)")
                
                # Display in columns for better readability
                for idx, symbol in enumerate(symbols, 1):
                    print(f"\n  {idx}. {symbol['name']}")
                    print(f"     Description: {symbol['description']}")
                    print(f"     Type: {symbol['type']}")
                    print(f"     Pip/Point: {symbol['pip']}")
                    print(f"     Digits: {symbol['digits']}")
                    print(f"     Current Bid: {symbol['bid']}")
                    print(f"     Current Ask: {symbol['ask']}")
                    print(f"     Contract Size: {symbol['contract_size']}")
                    print(f"     Point Value: {symbol['point_value']}")
                    print(f"     Margin: {symbol['margin']}")
                    print(f"     Trade Mode: {symbol['trade_mode']}")
    
    @staticmethod
    def display_summary(accounts: List[Dict], symbols_dict: Dict[str, List[Dict]]):
        """Display summary statistics."""
        TerminalUI.print_header("Summary Statistics")
        
        print(f"📊 Total Accounts Found: {len(accounts)}")
        
        total_symbols = sum(len(v) for v in symbols_dict.values())
        print(f"📈 Total Symbols Available: {total_symbols}")
        
        print(f"\n📋 Symbols by Category:")
        for category, symbols in symbols_dict.items():
            if symbols:
                print(f"  • {category}: {len(symbols)} symbols")


class MT5DetectorApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize application."""
        self.logger = CrossPlatformLogger()
        self.os_detector = OSDetector()
        self.connector = MT5Connector(self.logger)
        self.account_manager = None
        self.symbol_manager = None
    
    def run(self):
        """Run the application."""
        try:
            TerminalUI.clear_screen()
            TerminalUI.print_header("MT5 Account & Symbol Detector")
            
            self.logger.log_startup()
            
            # Check OS
            print(f"🖥️  Detected OS: {self.os_detector.get_os_name()}")
            
            # Ensure MT5 is running
            if not self.os_detector.ensure_mt5_running():
                print("\n❌ Cannot proceed without MT5 running.")
                self.logger.log_error('STARTUP', 'MT5 not available')
                return
            
            print("\n✅ MT5 is running")
            
            # Connect to MT5
            print("\n🔗 Connecting to MT5...")
            if not self.connector.connect():
                print("\n❌ Failed to connect to MT5")
                self.logger.log_error('STARTUP', 'Failed to connect to MT5')
                return
            
            print("✅ Connected to MT5")
            
            # Initialize managers
            self.account_manager = AccountManager(self.connector, self.logger)
            self.symbol_manager = SymbolManager(self.connector, self.logger)
            
            # Detect accounts
            print("\n🔍 Detecting accounts...")
            accounts = self.account_manager.detect_accounts()
            
            if not accounts:
                print("\n❌ No accounts found in MT5")
                self.logger.log_error('STARTUP', 'No accounts detected')
                return
            
            print(f"✅ Found {len(accounts)} account(s)")
            
            # Display accounts and get selection
            selected_account = TerminalUI.display_accounts(accounts)
            
            if not selected_account:
                return
            
            # Detect symbols for selected account
            print(f"\n🔍 Detecting symbols for account {selected_account['login']}...")
            symbols = self.symbol_manager.detect_symbols(selected_account['login'])
            
            if not symbols:
                print("\n❌ No symbols found")
                self.logger.log_error('SYMBOL_DETECTION', 'No symbols detected')
                return
            
            print(f"✅ Found {sum(len(v) for v in symbols.values())} symbols")
            
            # Display symbols
            TerminalUI.display_symbols(symbols)
            
            # Display summary
            TerminalUI.display_summary(accounts, symbols)
            
            # Save report
            self._save_detailed_report(selected_account, symbols)
            
            print("\n" + "="*80)
            print("✅ Application completed successfully!")
            print(f"📁 Logs saved to: {self.logger.log_file}")
            print("="*80 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Application interrupted by user")
            self.logger.log_info('Application interrupted by user')
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.logger.log_error('RUNTIME', str(e))
        
        finally:
            self.connector.disconnect()
    
    def _save_detailed_report(self, account: Dict, symbols: Dict[str, List[Dict]]):
        """Save detailed report to file."""
        try:
            report_file = f"mt5_report_{account['login']}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("MT5 Account & Symbol Report\n")
                f.write("="*80 + "\n\n")
                
                f.write("ACCOUNT INFORMATION\n")
                f.write("-"*80 + "\n")
                f.write(f"Login: {account['login']}\n")
                f.write(f"Server: {account['server']}\n")
                f.write(f"Name: {account['name']}\n")
                f.write(f"Currency: {account['currency']}\n")
                f.write(f"Balance: {account['balance']}\n")
                f.write(f"Equity: {account['equity']}\n")
                f.write(f"Leverage: 1:{account['leverage']}\n")
                f.write(f"Margin: {account['margin']}\n")
                f.write(f"Margin Free: {account['margin_free']}\n")
                f.write(f"Margin Level: {account['margin_level']}\n")
                f.write(f"Profit: {account['profit']}\n\n")
                
                for category, symbol_list in symbols.items():
                    if symbol_list:
                        f.write(f"\n{category.upper()} ({len(symbol_list)} symbols)\n")
                        f.write("-"*80 + "\n")
                        
                        for symbol in symbol_list:
                            f.write(f"\nSymbol: {symbol['name']}\n")
                            f.write(f"  Description: {symbol['description']}\n")
                            f.write(f"  Type: {symbol['type']}\n")
                            f.write(f"  Pip: {symbol['pip']}\n")
                            f.write(f"  Digits: {symbol['digits']}\n")
                            f.write(f"  Bid: {symbol['bid']}\n")
                            f.write(f"  Ask: {symbol['ask']}\n")
                            f.write(f"  Contract Size: {symbol['contract_size']}\n")
                            f.write(f"  Point Value: {symbol['point_value']}\n")
                            f.write(f"  Margin: {symbol['margin']}\n")
                            f.write(f"  Trade Mode: {symbol['trade_mode']}\n")
            
            print(f"\n📄 Detailed report saved to: {report_file}")
            self.logger.log_info(f"Report saved to {report_file}")
        
        except Exception as e:
            self.logger.log_error('REPORT_SAVE', str(e))


def main():
    """Main entry point."""
    app = MT5DetectorApp()
    app.run()


if __name__ == '__main__':
    main()
