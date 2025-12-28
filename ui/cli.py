"""CLI interface for Strelitzia Trader with runtime command support."""

import sys
from typing import List, Optional, Dict, Any, Callable, Tuple
from core.logger import get_logger


class CLIInterface:
    """Command-line interface for user interaction with runtime commands."""

    # Command definitions
    COMMANDS = {
        'account': ('Show current account details', 'account'),
        'refresh': ('Manually refresh symbols from MT5', 'refresh'),
        'category': ('Switch symbol category', 'category'),
        'symbols': ('Switch symbols for analysis', 'symbols'),
        'timeframes': ('Switch timeframes', 'timeframes'),
        'analyze': ('Run analysis on selected symbols', 'analyze'),
        'verbose': ('Toggle verbose logging (verbose | standard | minimal)', 'verbose'),
        'help': ('Show available commands', 'help'),
        'exit': ('Exit the application', 'exit'),
    }

    def __init__(self):
        """Initialize CLI."""
        self.logger = get_logger()
        self._command_handlers: Dict[str, Callable] = {}

    def print_header(self):
        """Print application header."""
        print("\n" + "=" * 70)
        print(" " * 15 + "STRELITZIA TRADER - MetaTrader 5 Analysis Engine")
        print(" " * 20 + "Production-Grade Market Analysis System")
        print("=" * 70 + "\n")

    def print_account_info(self, account_info: Dict[str, Any]):
        """Print account information."""
        if not account_info:
            print("ERROR: Unable to retrieve account information\n")
            return

        print("ACCOUNT INFORMATION")
        print("-" * 70)
        print(f"Login:           {account_info.get('login', 'N/A')}")
        print(f"Account:         {account_info.get('name', 'N/A')}")
        print(f"Broker Server:   {account_info.get('server', 'N/A')}")
        print(f"Currency:        {account_info.get('currency', 'N/A')}")
        print(f"Balance:         {account_info.get('balance', 'N/A'):.2f}")
        print(f"Equity:          {account_info.get('equity', 'N/A'):.2f}")
        print(f"Profit/Loss:     {account_info.get('profit', 'N/A'):.2f}")
        print(f"Leverage:        1:{account_info.get('leverage', 'N/A')}")
        print(f"Margin Level:    {account_info.get('margin_level', 'N/A'):.2f}%")
        print(f"Trade Allowed:   {'Yes' if account_info.get('trade_allowed') else 'No'}")
        print("-" * 70 + "\n")

    def display_symbol_categories(self, categories: Dict[str, List[str]]):
        """Display available symbol categories."""
        print("\nAVAILABLE SYMBOL CATEGORIES")
        print("-" * 70)
        for idx, (category, symbols) in enumerate(categories.items(), 1):
            print(f"{idx}. {category:30} ({len(symbols):2} symbols)")
        print("-" * 70 + "\n")

    def select_category(self, categories: Dict[str, List[str]]) -> Optional[str]:
        """Prompt user to select a symbol category."""
        category_list = list(categories.keys())
        self.display_symbol_categories(categories)

        while True:
            try:
                choice = input("Select category number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    return None

                choice_num = int(choice)
                if 1 <= choice_num <= len(category_list):
                    return category_list[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(category_list)}")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def display_symbols(self, symbols: List[str]):
        """Display list of symbols."""
        print("\nSYMBOLS IN CATEGORY")
        print("-" * 70)
        for idx, symbol in enumerate(symbols, 1):
            print(f"{idx:2}. {symbol}")
        print("-" * 70 + "\n")

    def select_symbols(self, symbols: List[str]) -> Optional[List[str]]:
        """Prompt user to select symbols."""
        self.display_symbols(symbols)

        while True:
            try:
                choice = input("Enter symbol numbers (comma-separated, e.g., '1,2,3'), 'all', or 'q': ").strip()

                if choice.lower() == 'all':
                    return symbols

                if choice.lower() == 'q':
                    return None

                selections = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = [symbols[i] for i in selections if 0 <= i < len(symbols)]

                if selected:
                    return selected
                else:
                    print("No valid selections. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter valid numbers.")

    def select_timeframes(self) -> Optional[List[str]]:
        """Prompt user to select timeframes."""
        timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1', 'MN1']

        print("\nAVAILABLE TIMEFRAMES")
        print("-" * 70)
        for idx, tf in enumerate(timeframes, 1):
            print(f"{idx}. {tf}")
        print("-" * 70)

        while True:
            try:
                choice = input(
                    "Enter timeframe numbers (comma-separated), "
                    "'default' (H1,D1), or 'q': "
                ).strip()

                if choice.lower() == 'default':
                    return ['H1', 'D1']

                if choice.lower() == 'q':
                    return None

                selections = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = [timeframes[i] for i in selections if 0 <= i < len(timeframes)]

                if selected:
                    return selected
                else:
                    print("No valid selections. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter valid numbers.")

    def display_analysis_result(self, result: Dict[str, Any]):
        """Display analysis result."""
        print("\nANALYSIS RESULT")
        print("=" * 70)
        print(f"Symbol:                {result.get('symbol', 'N/A')}")
        print(f"Timeframe:             {result.get('timeframe', 'N/A')}")
        print(f"Broker:                {result.get('broker', 'N/A')}")
        print(f"Rating:                {result.get('rating', 'N/A')}")
        print(f"Confluence Score:      {result.get('confluence_score', 0):.1f}/100")
        print(f"Confidence:            {result.get('confidence', 0):.1f}%")
        print(f"Bullish Signals:       {result.get('bullish_signals', 0)}")
        print(f"Bearish Signals:       {result.get('bearish_signals', 0)}")
        print(f"Total Signal Methods:  {result.get('signal_count', 0)}")
        
        if 'top_factors' in result and result['top_factors']:
            print("\nTop Contributing Factors:")
            for i, (source, weight) in enumerate(result['top_factors'][:5], 1):
                print(f"  {i}. {source}: {weight:.2f}")
        
        print("=" * 70 + "\n")

        if 'error' in result:
            print(f"ERROR: {result.get('error')}\n")

    def confirm_action(self, message: str) -> bool:
        """Prompt user for yes/no confirmation."""
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'.")

    def display_message(self, message: str, level: str = "INFO"):
        """Display a message."""
        prefix_map = {
            "INFO": "[ℹ INFO]",
            "WARNING": "[⚠ WARNING]",
            "ERROR": "[❌ ERROR]",
            "SUCCESS": "[✓ SUCCESS]",
        }
        prefix = prefix_map.get(level, "[ℹ INFO]")
        print(f"{prefix} {message}")

    def display_loading(self, message: str):
        """Display loading message."""
        print(f"\n{message}...", end=" ", flush=True)

    def display_done(self):
        """Display done message."""
        print("Done.\n")

    def show_command_help(self):
        """Show available commands."""
        print("\n" + "=" * 70)
        print("  Available Commands")
        print("=" * 70)
        for cmd, (description, _) in self.COMMANDS.items():
            print(f"  {cmd:15s} - {description}")
        print("=" * 70 + "\n")

    def prompt_for_command(self) -> Optional[str]:
        """
        Prompt user for a runtime command.
        
        Returns:
            Command name or None if user quits
        """
        while True:
            command = input("\n[Command] (type 'help' for commands): ").strip().lower()
            
            if not command:
                continue
            
            if command == 'help':
                self.show_command_help()
                continue
            
            if command in self.COMMANDS:
                return command
            
            if command in ['q', 'quit', 'exit']:
                return 'exit'
            
            print(f"Unknown command '{command}'. Type 'help' for available commands.")

    def prompt_for_analysis_mode(self) -> Optional[str]:
        """
        Prompt user to choose analysis mode.
        
        Returns:
            'single' for single timeframe, 'multi' for multi-timeframe, None to cancel
        """
        print("\n" + "=" * 70)
        print("  Analysis Mode")
        print("=" * 70)
        print("  1. Single Timeframe Analysis (faster)")
        print("  2. Multi-Timeframe Analysis (comprehensive, slower)")
        print("=" * 70)
        
        while True:
            choice = input("\nSelect mode (1, 2, or 'q' to cancel): ").strip()
            
            if choice == '1':
                return 'single'
            elif choice == '2':
                return 'multi'
            elif choice.lower() in ['q', 'quit']:
                return None
            else:
                print("Please enter 1, 2, or 'q'.")

    def prompt_logging_verbosity(self) -> Optional[str]:
        """
        Prompt user to set logging verbosity.
        
        Returns:
            Verbosity level name or None
        """
        print("\n" + "=" * 70)
        print("  Logging Verbosity")
        print("=" * 70)
        print("  1. MINIMAL (only errors)")
        print("  2. STANDARD (warnings and errors)")
        print("  3. VERBOSE (all info messages)")
        print("  4. DEBUG (very detailed)")
        print("=" * 70)
        
        mapping = {'1': 'MINIMAL', '2': 'STANDARD', '3': 'VERBOSE', '4': 'DEBUG'}
        
        while True:
            choice = input("\nSelect verbosity (1-4 or 'q'): ").strip()
            
            if choice in mapping:
                return mapping[choice]
            elif choice.lower() in ['q', 'quit']:
                return None
            else:
                print("Please enter 1, 2, 3, 4, or 'q'.")

    def display_current_selection(
        self,
        category: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        timeframes: Optional[List[str]] = None
    ):
        """Display currently selected analysis parameters."""
        print("\n" + "-" * 70)
        print("  Current Selection")
        print("-" * 70)
        if category:
            print(f"  Category:   {category}")
        if symbols:
            print(f"  Symbols:    {', '.join(symbols)}")
        if timeframes:
            print(f"  Timeframes: {', '.join(timeframes)}")
        print("-" * 70 + "\n")

