#!/usr/bin/env python3
"""
MT5 Account & Symbol Detector - Quick Start Examples

This file contains practical examples of how to use the detector application
and how to programmatically access the MT5Detector classes.

Author: Strelitzia System
Date: December 27, 2025
"""

# ==============================================================================
# EXAMPLE 1: Run the application directly
# ==============================================================================
"""
From command line:

# Windows
python mt5_account_symbol_detector.py

# Linux/macOS
python3 mt5_account_symbol_detector.py

Or directly:
./mt5_account_symbol_detector.py

Expected output:
- OS detection
- MT5 startup (if needed)
- Account selection menu
- Symbol listing by category
- Saved reports
"""


# ==============================================================================
# EXAMPLE 2: Programmatic use - Basic connection
# ==============================================================================

def example_basic_connection():
    """Example: Connect to MT5 and get basic account info."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, CrossPlatformLogger
    )
    
    # Initialize logger
    logger = CrossPlatformLogger()
    
    # Initialize connector
    connector = MT5Connector(logger)
    
    # Connect to MT5
    if not connector.connect():
        print("Failed to connect to MT5")
        return
    
    # Initialize account manager
    account_manager = AccountManager(connector, logger)
    
    # Detect accounts
    accounts = account_manager.detect_accounts()
    
    if accounts:
        account = accounts[0]
        print(f"Connected to account: {account['login']}")
        print(f"Broker: {account['server']}")
        print(f"Balance: {account['balance']} {account['currency']}")
    
    # Disconnect
    connector.disconnect()


# ==============================================================================
# EXAMPLE 3: Get all symbols for an account
# ==============================================================================

def example_get_symbols():
    """Example: Retrieve and display all symbols."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    if not accounts:
        print("No accounts found")
        connector.disconnect()
        return
    
    # Get symbols for first account
    account_login = accounts[0]['login']
    
    symbol_manager = SymbolManager(connector, logger)
    symbols = symbol_manager.detect_symbols(account_login)
    
    # Display symbols
    for category, symbol_list in symbols.items():
        print(f"\n{category}: {len(symbol_list)} symbols")
        for symbol in symbol_list[:5]:  # Show first 5
            print(f"  - {symbol['name']}: Bid={symbol['bid']}, Ask={symbol['ask']}")
    
    connector.disconnect()


# ==============================================================================
# EXAMPLE 4: Filter symbols by specific criteria
# ==============================================================================

def example_filter_symbols():
    """Example: Find specific symbols matching criteria."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    symbol_manager = SymbolManager(connector, logger)
    symbols = symbol_manager.detect_symbols(accounts[0]['login'])
    
    # Filter: Find all symbols with bid/ask spread < 0.0002
    tight_spreads = []
    for category, symbol_list in symbols.items():
        for symbol in symbol_list:
            spread = symbol['ask'] - symbol['bid']
            if spread < 0.0002:
                tight_spreads.append((symbol['name'], spread))
    
    print(f"\nSymbols with tight spreads (< 0.0002):")
    for symbol_name, spread in sorted(tight_spreads, key=lambda x: x[1]):
        print(f"  {symbol_name}: {spread:.6f}")
    
    connector.disconnect()


# ==============================================================================
# EXAMPLE 5: Export symbols to CSV
# ==============================================================================

def example_export_to_csv():
    """Example: Export symbol data to CSV file."""
    
    import csv
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    symbol_manager = SymbolManager(connector, logger)
    symbols = symbol_manager.detect_symbols(accounts[0]['login'])
    
    # Write to CSV
    with open('symbols_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Symbol', 'Category', 'Type', 'Bid', 'Ask', 'Pip', 'Digits'])
        
        for category, symbol_list in symbols.items():
            for symbol in symbol_list:
                writer.writerow([
                    symbol['name'],
                    category,
                    symbol['type'],
                    symbol['bid'],
                    symbol['ask'],
                    symbol['pip'],
                    symbol['digits']
                ])
    
    print("✅ Exported to symbols_export.csv")
    connector.disconnect()


# ==============================================================================
# EXAMPLE 6: Monitor account in real-time
# ==============================================================================

def example_monitor_account():
    """Example: Monitor account balance changes over time."""
    
    import time
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    
    print("Monitoring account... (30 seconds)")
    
    previous_balance = None
    for i in range(6):
        accounts = account_manager.detect_accounts()
        if accounts:
            account = accounts[0]
            balance = account['balance']
            
            if previous_balance is not None:
                change = balance - previous_balance
                print(f"[{i*5}s] Balance: {balance} (Change: {change:+.2f})")
            else:
                print(f"[{i*5}s] Balance: {balance}")
            
            previous_balance = balance
        
        if i < 5:
            time.sleep(5)
    
    connector.disconnect()


# ==============================================================================
# EXAMPLE 7: Get detailed symbol information
# ==============================================================================

def example_symbol_details():
    """Example: Get detailed information for a specific symbol."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    symbol_manager = SymbolManager(connector, logger)
    symbols = symbol_manager.detect_symbols(accounts[0]['login'])
    
    # Find EURUSD
    target_symbol = 'EURUSD'
    for category, symbol_list in symbols.items():
        for symbol in symbol_list:
            if symbol['name'] == target_symbol:
                print(f"\n📊 {target_symbol} Details:")
                print(f"  Description: {symbol['description']}")
                print(f"  Category: {category}")
                print(f"  Type: {symbol['type']}")
                print(f"  Current Bid: {symbol['bid']}")
                print(f"  Current Ask: {symbol['ask']}")
                print(f"  Spread: {(symbol['ask'] - symbol['bid']):.6f}")
                print(f"  Pip Size: {symbol['pip']}")
                print(f"  Digits: {symbol['digits']}")
                print(f"  Contract Size: {symbol['contract_size']}")
                print(f"  Point Value: {symbol['point_value']}")
                print(f"  Margin: {symbol['margin']}")
                print(f"  Trade Mode: {symbol['trade_mode']}")
                return
    
    print(f"❌ Symbol {target_symbol} not found")
    connector.disconnect()


# ==============================================================================
# EXAMPLE 8: Analyze market volatility by symbol
# ==============================================================================

def example_analyze_volatility():
    """Example: Analyze bid-ask spread as volatility indicator."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    symbol_manager = SymbolManager(connector, logger)
    symbols = symbol_manager.detect_symbols(accounts[0]['login'])
    
    # Analyze spreads
    print("\n📊 Spread Analysis (Volatility Indicator):\n")
    
    for category, symbol_list in symbols.items():
        if not symbol_list:
            continue
        
        spreads = []
        for symbol in symbol_list:
            spread = symbol['ask'] - symbol['bid']
            spread_pips = spread / symbol['pip']
            spreads.append((symbol['name'], spread_pips))
        
        avg_spread = sum(s[1] for s in spreads) / len(spreads) if spreads else 0
        
        print(f"{category}:")
        print(f"  Average spread: {avg_spread:.2f} pips")
        
        # Show highest volatility (largest spread)
        top_volatile = sorted(spreads, key=lambda x: x[1], reverse=True)[:3]
        print(f"  Highest volatility: {', '.join(f'{s[0]} ({s[1]:.1f}p)' for s in top_volatile)}")
        print()
    
    connector.disconnect()


# ==============================================================================
# EXAMPLE 9: Compare spreads across brokers
# ==============================================================================

def example_compare_brokers():
    """Example: Compare the same symbol across different accounts/brokers."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    print("\n📊 Available Accounts/Brokers:")
    for idx, account in enumerate(accounts, 1):
        print(f"{idx}. {account['name']} ({account['server']})")
    
    # Note: The current implementation shows one account at a time
    # In multi-account scenario, this would compare spreads
    
    connector.disconnect()


# ==============================================================================
# EXAMPLE 10: Generate trading analysis report
# ==============================================================================

def example_trading_report():
    """Example: Generate a comprehensive trading analysis report."""
    
    from mt5_account_symbol_detector import (
        MT5Connector, AccountManager, SymbolManager, CrossPlatformLogger
    )
    from datetime import datetime
    
    logger = CrossPlatformLogger()
    connector = MT5Connector(logger)
    
    if not connector.connect():
        return
    
    account_manager = AccountManager(connector, logger)
    accounts = account_manager.detect_accounts()
    
    if not accounts:
        print("No accounts found")
        return
    
    account = accounts[0]
    
    symbol_manager = SymbolManager(connector, logger)
    symbols = symbol_manager.detect_symbols(account['login'])
    
    # Generate report
    report_file = f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TRADING ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Report Date: {datetime.now().isoformat()}\n")
        f.write(f"Account: {account['login']} ({account['server']})\n")
        f.write(f"Balance: {account['balance']} {account['currency']}\n")
        f.write(f"Equity: {account['equity']} {account['currency']}\n\n")
        
        total_symbols = sum(len(v) for v in symbols.values())
        f.write(f"Total Symbols Available: {total_symbols}\n\n")
        
        for category, symbol_list in symbols.items():
            if symbol_list:
                f.write(f"\n{category.upper()} ({len(symbol_list)} symbols)\n")
                f.write("-"*80 + "\n")
                
                for symbol in symbol_list:
                    f.write(f"\n{symbol['name']}:\n")
                    f.write(f"  Bid/Ask: {symbol['bid']}/{symbol['ask']}\n")
                    f.write(f"  Spread: {(symbol['ask'] - symbol['bid']):.6f}\n")
                    f.write(f"  Type: {symbol['type']}\n")
    
    print(f"✅ Report saved to: {report_file}")
    connector.disconnect()


# ==============================================================================
# Main execution
# ==============================================================================

if __name__ == '__main__':
    """
    Run examples based on user selection.
    
    Usage:
    python3 examples.py [example_number]
    
    Examples:
    1: Basic connection
    2: Get all symbols
    3: Filter symbols
    4: Export to CSV
    5: Monitor account
    6: Symbol details
    7: Analyze volatility
    8: Compare brokers
    9: Trading report
    """
    
    import sys
    
    examples = {
        '1': ('Basic Connection', example_basic_connection),
        '2': ('Get All Symbols', example_get_symbols),
        '3': ('Filter Symbols', example_filter_symbols),
        '4': ('Export to CSV', example_export_to_csv),
        '5': ('Monitor Account', example_monitor_account),
        '6': ('Symbol Details', example_symbol_details),
        '7': ('Analyze Volatility', example_analyze_volatility),
        '8': ('Compare Brokers', example_compare_brokers),
        '9': ('Trading Report', example_trading_report),
    }
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num in examples:
            print(f"\n▶️  Running: {examples[example_num][0]}\n")
            examples[example_num][1]()
        else:
            print(f"❌ Unknown example: {example_num}")
    else:
        print("\n" + "="*80)
        print("MT5 Detector - Available Examples")
        print("="*80 + "\n")
        
        for key, (name, _) in examples.items():
            print(f"{key}. {name}")
        
        print("\n" + "="*80)
        print("Usage: python3 examples.py [example_number]")
        print("="*80 + "\n")
        
        while True:
            choice = input("Select example (1-9) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                break
            if choice in examples:
                print(f"\n▶️  Running: {examples[choice][0]}\n")
                examples[choice][1]()
            else:
                print("❌ Invalid choice")
