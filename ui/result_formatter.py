"""
Analysis Result Formatter - Formats and displays multi-timeframe analysis results.

Displays analysis results in clean, readable CLI format with all relevant information.
"""

from typing import Optional, Dict, List
from analysis.confluence_engine import ConfluenceResult
from analysis.multi_timeframe_orchestrator import MultiTimeframeResult
from mt5.account_monitor import AccountSnapshot


class ResultFormatter:
    """Formats analysis results for display."""
    
    @staticmethod
    def format_confluence_result(
        symbol: str,
        timeframe: str,
        result: ConfluenceResult,
        broker: Optional[str] = None,
        show_top_factors: bool = True
    ) -> str:
        """
        Format a single confluence result for display.
        
        Args:
            symbol: Symbol name
            timeframe: Timeframe string
            result: ConfluenceResult object
            broker: Optional broker name
            show_top_factors: Whether to show top contributing factors
            
        Returns:
            Formatted string for display
        """
        lines = []
        
        # Header
        header = f"\n{'='*70}"
        lines.append(header)
        symbol_str = f"{symbol} ({timeframe})"
        if broker:
            symbol_str += f" @ {broker}"
        lines.append(f"  {symbol_str}")
        lines.append('='*70)
        
        # Market bias
        lines.append(f"\n  Market Bias: {result.market_bias}")
        
        # Scores
        lines.append(f"\n  Bullish Score:     {result.bullish_score:6.1f}%")
        lines.append(f"  Bearish Score:     {result.bearish_score:6.1f}%")
        lines.append(f"  Neutral Prob.:     {result.neutral_probability:6.1f}%")
        
        # Confidence
        conf_bar = ResultFormatter._confidence_bar(result.confidence_percentage)
        lines.append(f"\n  Confidence:        {result.confidence_percentage:6.1f}%  {conf_bar}")
        
        # Signal counts
        lines.append(f"\n  Total Signals:     {result.signal_count}")
        lines.append(f"  Bullish Signals:   {result.bullish_signals}")
        lines.append(f"  Bearish Signals:   {result.bearish_signals}")
        if result.neutral_signals:
            lines.append(f"  Neutral Signals:   {result.neutral_signals}")
        
        # Top factors
        if show_top_factors and result.top_factors:
            lines.append("\n  Top Contributing Factors:")
            for i, (source, weight) in enumerate(result.top_factors, 1):
                lines.append(f"    {i}. {source}: {weight:.2f}")
        
        # Warnings
        if result.confidence_percentage < 40:
            lines.append("\n  ⚠ WARNING: Low confidence - results may be unreliable")
        
        lines.append('')  # Blank line
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_multi_timeframe_result(
        result: MultiTimeframeResult,
        broker: Optional[str] = None
    ) -> str:
        """
        Format multi-timeframe result for display.
        
        Args:
            result: MultiTimeframeResult object
            broker: Optional broker name
            
        Returns:
            Formatted string for display
        """
        lines = []
        
        # Header
        header = f"\n{'='*70}"
        lines.append(header)
        symbol_str = f"{result.symbol} (Multi-Timeframe Analysis)"
        if broker:
            symbol_str += f" @ {broker}"
        lines.append(f"  {symbol_str}")
        lines.append('='*70)
        
        # Overall bias
        lines.append(f"\n  Overall Bias:      {result.overall_bias}")
        
        # Overall scores
        lines.append(f"\n  Overall Bullish:   {result.overall_bullish:6.1f}%")
        lines.append(f"  Overall Bearish:   {result.overall_bearish:6.1f}%")
        lines.append(f"  Overall Conf.:     {result.overall_confidence:6.1f}%")
        
        # Timeframe confluence
        if result.confluence:
            conf_bar = ResultFormatter._confidence_bar(result.confluence)
            lines.append(f"\n  Timeframe Confluence: {result.confluence:6.1f}%  {conf_bar}")
        
        # Per-timeframe details
        lines.append("\n  Timeframe Details:")
        lines.append("  " + "-"*66)
        lines.append("  TF       Bullish  Bearish  Conf.    Bias            Weight")
        lines.append("  " + "-"*66)
        
        for tf_bias in result.timeframes:
            tf_str = f"{tf_bias.timeframe:8s}"
            bull_str = f"{tf_bias.bullish_score:7.1f}%"
            bear_str = f"{tf_bias.bearish_score:7.1f}%"
            conf_str = f"{tf_bias.confidence:6.1f}%"
            bias_str = f"{tf_bias.bias_direction:15s}"
            weight_str = f"{tf_bias.weight:.2f}"
            
            lines.append(f"  {tf_str} {bull_str} {bear_str} {conf_str} {bias_str} {weight_str}")
        
        lines.append("  " + "-"*66)
        
        lines.append('')  # Blank line
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_account_info(snapshot: AccountSnapshot) -> str:
        """
        Format account information for display.
        
        Args:
            snapshot: AccountSnapshot object
            
        Returns:
            Formatted string for display
        """
        lines = []
        
        header = f"\n{'='*70}"
        lines.append(header)
        lines.append(f"  Account Information")
        lines.append('='*70)
        
        lines.append(f"\n  Login:              {snapshot.login}")
        lines.append(f"  Name:               {snapshot.name}")
        lines.append(f"  Company:            {snapshot.company}")
        lines.append(f"  Server:             {snapshot.server}")
        lines.append(f"  Currency:           {snapshot.currency}")
        
        lines.append(f"\n  Balance:            {snapshot.balance:15.2f} {snapshot.currency}")
        lines.append(f"  Equity:             {snapshot.equity:15.2f} {snapshot.currency}")
        lines.append(f"  Margin Level:       {snapshot.margin_level:15.2f}%")
        
        lines.append(f"\n  Last Update:        {snapshot.timestamp}")
        
        lines.append('')  # Blank line
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_error(error_message: str) -> str:
        """Format error message for display."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  ❌ ERROR")
        lines.append('='*70)
        lines.append(f"\n  {error_message}")
        lines.append('')
        return '\n'.join(lines)
    
    @staticmethod
    def format_warning(warning_message: str) -> str:
        """Format warning message for display."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  ⚠ WARNING")
        lines.append('='*70)
        lines.append(f"\n  {warning_message}")
        lines.append('')
        return '\n'.join(lines)
    
    @staticmethod
    def format_info(info_message: str) -> str:
        """Format info message for display."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  ℹ INFO")
        lines.append('='*70)
        lines.append(f"\n  {info_message}")
        lines.append('')
        return '\n'.join(lines)
    
    @staticmethod
    def _confidence_bar(confidence: float, width: int = 20) -> str:
        """Generate ASCII confidence bar."""
        filled = int((confidence / 100.0) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    @staticmethod
    def format_symbol_list(category: str, symbols: List[str]) -> str:
        """Format list of symbols for display."""
        lines = []
        lines.append(f"\n  {category}:")
        
        # Format in columns
        per_line = 5
        for i in range(0, len(symbols), per_line):
            chunk = symbols[i:i+per_line]
            formatted = "    " + " | ".join(f"{s:15s}" for s in chunk)
            lines.append(formatted)
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_menu_options(options: Dict[str, str]) -> str:
        """Format menu options for display."""
        lines = []
        lines.append("\n  Available Commands:")
        for cmd, description in options.items():
            lines.append(f"    {cmd:20s} - {description}")
        return '\n'.join(lines)
