"""Base analysis class for all symbol type analyzers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from core.logger import get_logger


class BaseAnalyzer(ABC):
    """
    Abstract base class for all asset type analyzers.
    
    All analyzers must implement the analyze() method which returns
    a structured analysis result with a confluence score.
    """

    def __init__(self, symbol: str, timeframe: str):
        """
        Initialize base analyzer.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe for analysis
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = get_logger()

    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on symbol data.
        
        Must be implemented by subclasses.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dict[str, Any]: Analysis results with 'confluence_score' key
        """
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data.
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            bool: True if data is valid
        """
        if data is None or len(data) < 20:
            self.logger.warning(f"Insufficient data for {self.symbol}")
            return False

        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            self.logger.error(f"Missing required columns in data for {self.symbol}")
            return False

        return True

    def create_result(self, **kwargs) -> Dict[str, Any]:
        """
        Create standardized analysis result with optional explanations.
        
        Args:
            **kwargs: Analysis result fields (can include 'explanation' key)
            
        Returns:
            Dict[str, Any]: Standardized result
        """
        result = {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'confluence_score': 0.0,
            'analysis': {},
            'explanation': '',  # Human-readable explanation of signals
            'signal_sources': [],  # List of which signals contributed to score
        }
        result.update(kwargs)
        return result
    
    def create_signal_explanation(self, signal_name: str, confidence: float, reason: str) -> Dict[str, Any]:
        """
        Create a human-readable explanation for a signal.
        Helps users understand why a particular bias was produced.
        
        Args:
            signal_name: Name of the signal (e.g., 'Moving Average Crossover')
            confidence: Confidence level (0-100)
            reason: Brief explanation of why this signal fired
            
        Returns:
            Dict[str, Any]: Structured signal explanation
        """
        return {
            'signal': signal_name,
            'confidence': confidence,
            'reason': reason,
            'direction': 'BULLISH' if confidence > 50 else 'BEARISH' if confidence < 50 else 'NEUTRAL',
        }
