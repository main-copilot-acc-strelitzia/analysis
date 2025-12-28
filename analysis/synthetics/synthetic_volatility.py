"""Synthetic volatility analysis."""

import numpy as np
import pandas as pd


class SyntheticVolatilityAnalysis:
    """Analyzes volatility in synthetic instruments."""

    @staticmethod
    def synthetic_volatility_level(data: pd.DataFrame) -> float:
        """
        Measure current volatility level.
        
        Returns volatility 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        returns = np.abs(np.diff(closes) / closes[:-1])

        current_vol = np.std(returns[-5:])
        historical_vol = np.std(returns[-15:])

        if historical_vol == 0:
            return 50.0

        ratio = current_vol / historical_vol
        return min(ratio * 50, 100.0)

    @staticmethod
    def synthetic_volatility_expansion(data: pd.DataFrame) -> float:
        """
        Detect volatility expansion.
        
        Returns expansion signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        ranges = data['High'].values - data['Low'].values

        recent_range = np.mean(ranges[-5:])
        prior_range = np.mean(ranges[-15:-5])

        if prior_range == 0:
            return 50.0

        if recent_range > prior_range * 1.5:
            return 80.0
        elif recent_range < prior_range * 0.7:
            return 20.0
        else:
            return 50.0

    @staticmethod
    def volatility_regime_synthetic(data: pd.DataFrame) -> str:
        """
        Identify volatility regime for synthetic.
        
        Returns regime: 'High', 'Normal', 'Low'
        """
        if len(data) < 20:
            return 'Normal'

        closes = data['Close'].values
        volatility = np.std(closes[-10:]) / np.mean(closes[-10:])
        historical = np.std(closes[-20:]) / np.mean(closes[-20:])

        if volatility > historical * 1.3:
            return 'High'
        elif volatility < historical * 0.7:
            return 'Low'
        else:
            return 'Normal'

    @staticmethod
    def volatility_mean_reversion_synthetic(data: pd.DataFrame) -> float:
        """
        Detect mean reversion in volatility.
        
        Returns reversion signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        volatility = np.std(closes[-10:])
        avg_vol = np.std(closes[-20:])

        if volatility > avg_vol * 1.5:
            return 25.0  # High vol, expect reversion
        elif volatility < avg_vol * 0.6:
            return 75.0  # Low vol, expect expansion
        else:
            return 50.0

    @staticmethod
    def squeeze_and_expansion(data: pd.DataFrame) -> float:
        """
        Identify squeeze and expansion patterns.
        
        Returns pattern signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        ranges = data['High'].values - data['Low'].values

        current_range = ranges[-1]
        avg_range = np.mean(ranges[-10:])

        if current_range < avg_range * 0.5:
            return 80.0  # Squeeze
        elif current_range > avg_range * 1.8:
            return 20.0  # Expansion
        else:
            return 50.0
