"""Analysis utilities and helpers."""

import numpy as np
from typing import List, Dict, Tuple, Optional


class AnalysisUtils:
    """Utility functions for analysis."""

    @staticmethod
    def find_peaks(data: np.ndarray, threshold: float = 0.0) -> List[int]:
        """
        Find local peaks in data.
        
        Args:
            data: Data array
            threshold: Minimum height for peak
            
        Returns:
            List[int]: Indices of peaks
        """
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1] and data[i] > threshold:
                peaks.append(i)
        return peaks

    @staticmethod
    def find_troughs(data: np.ndarray, threshold: float = float('inf')) -> List[int]:
        """
        Find local troughs in data.
        
        Args:
            data: Data array
            threshold: Maximum depth for trough
            
        Returns:
            List[int]: Indices of troughs
        """
        troughs = []
        for i in range(1, len(data) - 1):
            if data[i] < data[i-1] and data[i] < data[i+1] and data[i] < threshold:
                troughs.append(i)
        return troughs

    @staticmethod
    def find_support_resistance(prices: np.ndarray, window: int = 20) -> Tuple[List[float], List[float]]:
        """
        Find support and resistance levels.
        
        Args:
            prices: Price array
            window: Window size for extrema
            
        Returns:
            Tuple[List[float], List[float]]: Support and resistance levels
        """
        support = []
        resistance = []

        for i in range(window, len(prices) - window):
            local_min = np.min(prices[i-window:i+window])
            local_max = np.max(prices[i-window:i+window])

            if prices[i] == local_min and local_min not in support:
                support.append(local_min)
            if prices[i] == local_max and local_max not in resistance:
                resistance.append(local_max)

        return sorted(set(support)), sorted(set(resistance))

    @staticmethod
    def calculate_swing_highs(prices: np.ndarray, period: int = 5) -> List[Tuple[int, float]]:
        """
        Find swing highs.
        
        Args:
            prices: Price array
            period: Lookback period
            
        Returns:
            List[Tuple[int, float]]: Index and price of swing highs
        """
        swing_highs = []
        for i in range(period, len(prices) - period):
            if prices[i] == np.max(prices[i-period:i+period]):
                swing_highs.append((i, prices[i]))
        return swing_highs

    @staticmethod
    def calculate_swing_lows(prices: np.ndarray, period: int = 5) -> List[Tuple[int, float]]:
        """
        Find swing lows.
        
        Args:
            prices: Price array
            period: Lookback period
            
        Returns:
            List[Tuple[int, float]]: Index and price of swing lows
        """
        swing_lows = []
        for i in range(period, len(prices) - period):
            if prices[i] == np.min(prices[i-period:i+period]):
                swing_lows.append((i, prices[i]))
        return swing_lows

    @staticmethod
    def identify_trend(prices: np.ndarray, period: int = 20) -> str:
        """
        Identify trend direction.
        
        Args:
            prices: Price array
            period: Period for trend calculation
            
        Returns:
            str: 'Uptrend', 'Downtrend', or 'Sideways'
        """
        if len(prices) < period + 1:
            return 'Sideways'

        recent = prices[-period:]
        older = prices[-2*period:-period]

        recent_avg = np.mean(recent)
        older_avg = np.mean(older)

        if recent_avg > older_avg * 1.01:
            return 'Uptrend'
        elif recent_avg < older_avg * 0.99:
            return 'Downtrend'
        else:
            return 'Sideways'

    @staticmethod
    def calculate_price_change(open_price: float, close_price: float) -> float:
        """
        Calculate percentage price change.
        
        Args:
            open_price: Opening price
            close_price: Closing price
            
        Returns:
            float: Percentage change
        """
        if open_price == 0:
            return 0.0
        return ((close_price - open_price) / open_price) * 100

    @staticmethod
    def calculate_range(high: float, low: float) -> float:
        """
        Calculate price range.
        
        Args:
            high: Highest price
            low: Lowest price
            
        Returns:
            float: Range
        """
        return high - low

    @staticmethod
    def is_breakout(high: np.ndarray, low: np.ndarray, period: int = 20) -> Tuple[bool, bool]:
        """
        Detect breakout conditions.
        
        Args:
            high: High prices
            low: Low prices
            period: Lookback period
            
        Returns:
            Tuple[bool, bool]: (bullish_breakout, bearish_breakout)
        """
        if len(high) < period + 1:
            return False, False

        resistance = np.max(high[-period:-1])
        support = np.min(low[-period:-1])
        current_high = high[-1]
        current_low = low[-1]

        bullish = current_high > resistance
        bearish = current_low < support

        return bullish, bearish

    @staticmethod
    def calculate_atr_percentage(atr: float, price: float) -> float:
        """
        Calculate ATR as percentage of price.
        
        Args:
            atr: Average True Range
            price: Current price
            
        Returns:
            float: ATR percentage
        """
        if price == 0:
            return 0.0
        return (atr / price) * 100

    @staticmethod
    def confluence_score(signals: Dict[str, float]) -> float:
        """
        Calculate confluence score from multiple signals.
        
        Args:
            signals: Dictionary of signal values (0-100 scale)
            
        Returns:
            float: Confluence score (0-100)
        """
        if not signals:
            return 0.0
        values = [v for v in signals.values() if 0 <= v <= 100]
        if not values:
            return 0.0
        return np.mean(values)

    @staticmethod
    def weight_signals(signals: Dict[str, Tuple[float, float]]) -> float:
        """
        Calculate weighted signal score.
        
        Args:
            signals: Dictionary of (value, weight) tuples
            
        Returns:
            float: Weighted score
        """
        total_weight = sum(w for _, w in signals.values())
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(v * w for (v, w) in signals.values())
        return weighted_sum / total_weight

    @staticmethod
    def normalize_values(values: np.ndarray, min_val: float = 0.0, max_val: float = 100.0) -> np.ndarray:
        """
        Normalize values to range.
        
        Args:
            values: Values to normalize
            min_val: Minimum target value
            max_val: Maximum target value
            
        Returns:
            np.ndarray: Normalized values
        """
        if len(values) == 0:
            return values
        v_min = np.min(values)
        v_max = np.max(values)
        if v_max == v_min:
            return np.full_like(values, (min_val + max_val) / 2, dtype=float)
        normalized = (values - v_min) / (v_max - v_min) * (max_val - min_val) + min_val
        return normalized

    @staticmethod
    def calculate_divergence(price1: np.ndarray, price2: np.ndarray) -> np.ndarray:
        """
        Calculate divergence between two price series.
        
        Args:
            price1: First price series
            price2: Second price series
            
        Returns:
            np.ndarray: Divergence values
        """
        if len(price1) != len(price2):
            return np.array([])
        return price1 - price2

    @staticmethod
    def identify_consolidation(prices: np.ndarray, window: int = 20, threshold: float = 0.01) -> bool:
        """
        Identify consolidation phase.
        
        Args:
            prices: Price array
            window: Window size
            threshold: Volatility threshold
            
        Returns:
            bool: True if consolidating
        """
        if len(prices) < window:
            return False

        recent = prices[-window:]
        price_range = (np.max(recent) - np.min(recent)) / np.mean(recent)
        return price_range < threshold
