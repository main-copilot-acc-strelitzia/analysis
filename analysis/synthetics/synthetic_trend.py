"""Synthetic trend analysis."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators


class SyntheticTrendAnalysis:
    """Analyzes trends in synthetic instruments."""

    @staticmethod
    def synthetic_trend_direction(data: pd.DataFrame) -> float:
        """
        Determine synthetic trend direction.
        
        Returns trend signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        sma = TechnicalIndicators.sma(closes, 20)

        if closes[-1] > sma[-1]:
            return 75.0
        elif closes[-1] < sma[-1]:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def synthetic_trend_strength(data: pd.DataFrame) -> float:
        """
        Measure trend strength.
        
        Returns strength 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        changes = np.diff(closes[-10:])

        upchanges = np.sum(changes > 0)
        downchanges = np.sum(changes < 0)

        if upchanges > downchanges:
            return 50.0 + ((upchanges - downchanges) / len(changes)) * 50
        else:
            return 50.0 - ((downchanges - upchanges) / len(changes)) * 50

    @staticmethod
    def synthetic_momentum_shift(data: pd.DataFrame) -> float:
        """
        Detect momentum shifts.
        
        Returns shift signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values

        recent_momentum = np.mean(np.diff(closes[-5:]))
        prior_momentum = np.mean(np.diff(closes[-10:-5]))

        if recent_momentum > prior_momentum and prior_momentum < 0:
            return 75.0  # Bullish shift
        elif recent_momentum < prior_momentum and prior_momentum > 0:
            return 25.0  # Bearish shift
        else:
            return 50.0

    @staticmethod
    def synthetic_trend_reversal_setup(data: pd.DataFrame) -> float:
        """
        Identify trend reversal setup.
        
        Returns reversal probability 0-100.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values

        # Reversal: divergence between price and momentum
        uptrend = closes[-1] > np.mean(closes[-10:])

        if uptrend:
            if np.max(highs[-5:]) < np.max(highs[-10:-5]):
                return 75.0  # Lower high reversal setup
        else:
            if np.min(lows[-5:]) > np.min(lows[-10:-5]):
                return 25.0  # Higher low reversal setup

        return 50.0

    @staticmethod
    def trend_confirmation_bar(data: pd.DataFrame) -> float:
        """
        Detect trend confirmation bars.
        
        Returns confirmation signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values
        opens = data['Open'].values

        # Last candle confirms trend
        if closes[-1] > opens[-1] and closes[-2] > opens[-2]:
            return 80.0
        elif closes[-1] < opens[-1] and closes[-2] < opens[-2]:
            return 20.0
        else:
            return 50.0

    @staticmethod
    def trend_exhaustion_signal(data: pd.DataFrame) -> float:
        """
        Signal trend exhaustion.
        
        Returns exhaustion 0-100.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        changes = np.abs(np.diff(closes[-10:]))

        if np.mean(changes[-3:]) < np.mean(changes[-6:-3]) * 0.7:
            return 75.0  # Exhaustion
        else:
            return 50.0
