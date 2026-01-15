"""Confluence analysis for Forex."""

import numpy as np


class ConfluenceAnalysis:
    """Analyzes confluence of multiple signals."""

    @staticmethod
    def _numeric_list(values):
        """Return list of numeric values coercible to float from an iterable."""
        nums = []
        for v in values:
            try:
                nums.append(float(v))
            except Exception:
                continue
        return nums

    @staticmethod
    def calculate_confluence_score(signals: dict) -> float:
        """
        Calculate overall confluence score from multiple signals.
        
        Args:
            signals: Dictionary of signal values (0-100 scale)
            
        Returns:
            Confluence score 0-100.
        """
        if not signals:
            return 50.0

        values = ConfluenceAnalysis._numeric_list(signals.values())

        if len(values) == 0:
            return 50.0

        # Average of numeric signals only
        return float(np.mean(values))

    @staticmethod
    def weighted_confluence(signals: dict, weights: dict) -> float:
        """
        Calculate weighted confluence score.
        
        Args:
            signals: Dictionary of signal values
            weights: Dictionary of weights for each signal
            
        Returns:
            Weighted confluence score 0-100.
        """
        if not signals or not weights:
            return 50.0

        total_weight = sum(weights.values())
        if total_weight == 0:
            return 50.0
        weighted_sum = 0.0
        for k in signals.keys():
            sig_val = signals.get(k, 50)
            try:
                sig = float(sig_val)
            except Exception:
                sig = 50.0
            weighted_sum += sig * weights.get(k, 0)

        return weighted_sum / total_weight

    @staticmethod
    def signal_agreement_level(signals: dict) -> float:
        """
        Measure how much signals agree with each other.
        
        Returns agreement level 0-100.
        """
        if len(signals) < 2:
            return 50.0

        values = ConfluenceAnalysis._numeric_list(signals.values())

        # Calculate standard deviation of numeric signals
        if len(values) == 0:
            return 50.0
        std_dev = float(np.std(values))

        # Low std = high agreement
        if std_dev < 10:
            return 90.0
        elif std_dev < 15:
            return 80.0
        elif std_dev < 20:
            return 70.0
        elif std_dev < 30:
            return 50.0
        else:
            return 30.0

    @staticmethod
    def bullish_confluence_count(signals: dict, threshold: float = 60) -> int:
        """
        Count number of bullish signals.
        
        Args:
            signals: Dictionary of signal values
            threshold: Signal threshold for bullish
            
        Returns:
            Count of bullish signals.
        """
        count = 0
        for v in signals.values():
            try:
                if float(v) >= threshold:
                    count += 1
            except Exception:
                continue
        return count

    @staticmethod
    def bearish_confluence_count(signals: dict, threshold: float = 40) -> int:
        """
        Count number of bearish signals.
        
        Args:
            signals: Dictionary of signal values
            threshold: Signal threshold for bearish
            
        Returns:
            Count of bearish signals.
        """
        count = 0
        for v in signals.values():
            try:
                if float(v) <= threshold:
                    count += 1
            except Exception:
                continue
        return count

    @staticmethod
    def neutral_confluence_count(signals: dict, lower: float = 40, upper: float = 60) -> int:
        """
        Count number of neutral signals.
        
        Args:
            signals: Dictionary of signal values
            lower: Lower threshold
            upper: Upper threshold
            
        Returns:
            Count of neutral signals.
        """
        count = 0
        for v in signals.values():
            try:
                fv = float(v)
            except Exception:
                continue
            if lower < fv < upper:
                count += 1
        return count

    @staticmethod
    def confluence_strength_rating(confluence_score: float) -> str:
        """
        Rate confluence strength.
        
        Args:
            confluence_score: Confluence score (0-100)
            
        Returns:
            Rating: 'Strong Bullish', 'Bullish', 'Neutral', 'Bearish', 'Strong Bearish'
        """
        if confluence_score >= 75:
            return 'Strong Bullish'
        elif confluence_score >= 60:
            return 'Bullish'
        elif confluence_score <= 25:
            return 'Strong Bearish'
        elif confluence_score <= 40:
            return 'Bearish'
        else:
            return 'Neutral'

    @staticmethod
    def confluence_quality(signals: dict) -> float:
        """
        Measure quality of confluence (consistency + agreement).
        
        Returns quality score 0-100.
        """
        if len(signals) < 3:
            return 50.0

        agreement = ConfluenceAnalysis.signal_agreement_level(signals)
        numeric_vals = ConfluenceAnalysis._numeric_list(signals.values())
        mean_signal = float(np.mean(numeric_vals)) if numeric_vals else 50.0

        # Quality = agreement + strength
        strength = max(abs(mean_signal - 50), 0) / 50 * 100
        return (agreement + strength) / 2

    @staticmethod
    def key_level_confluence(price: float, levels: dict) -> float:
        """
        Measure confluence at key price levels.
        
        Args:
            price: Current price
            levels: Dictionary of price levels and their signals
            
        Returns:
            Confluence at current price 0-100.
        """
        if not levels:
            return 50.0

        # Find closest levels
        min_distance = float('inf')
        closest_signals = []

        for level, signal in levels.items():
            distance = abs(price - level)
            if distance < min_distance:
                min_distance = distance
                closest_signals = [signal]
            elif distance == min_distance:
                closest_signals.append(signal)

        if not closest_signals:
            return 50.0

        return float(np.mean(closest_signals))
