"""Support and resistance analysis for Forex."""

import numpy as np
import pandas as pd


class SupportResistanceAnalysis:
    """Analyzes support and resistance levels."""

    @staticmethod
    def recent_support_levels(data: pd.DataFrame, count: int = 3) -> list:
        """
        Identify recent support levels.
        
        Returns list of support price levels.
        """
        if len(data) < 10:
            return []

        lows = data['Low'].values[-20:]
        indices = np.argsort(lows)[:count]

        return sorted([lows[i] for i in indices])

    @staticmethod
    def recent_resistance_levels(data: pd.DataFrame, count: int = 3) -> list:
        """
        Identify recent resistance levels.
        
        Returns list of resistance price levels.
        """
        if len(data) < 10:
            return []

        highs = data['High'].values[-20:]
        indices = np.argsort(-highs)[:count]

        return sorted([highs[i] for i in indices], reverse=True)

    @staticmethod
    def support_strength(data: pd.DataFrame) -> float:
        """
        Measure strength of nearest support.
        
        Returns support strength 0-100.
        """
        if len(data) < 20:
            return 50.0

        lows = data['Low'].values[-20:]
        closes = data['Close'].values

        support = np.min(lows)
        current = closes[-1]
        distance = current - support

        if distance < (support * 0.001):
            return 90.0
        elif distance < (support * 0.005):
            return 75.0
        elif distance < (support * 0.01):
            return 60.0
        else:
            return 40.0

    @staticmethod
    def resistance_strength(data: pd.DataFrame) -> float:
        """
        Measure strength of nearest resistance.
        
        Returns resistance strength 0-100.
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values[-20:]
        closes = data['Close'].values

        resistance = np.max(highs)
        current = closes[-1]
        distance = resistance - current

        if distance < (resistance * 0.001):
            return 90.0
        elif distance < (resistance * 0.005):
            return 75.0
        elif distance < (resistance * 0.01):
            return 60.0
        else:
            return 40.0

    @staticmethod
    def support_resistance_ratio(data: pd.DataFrame) -> float:
        """
        Calculate ratio of distance to support vs resistance.
        
        Returns ratio signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        lows = data['Low'].values[-20:]
        highs = data['High'].values[-20:]
        closes = data['Close'].values

        support = np.min(lows)
        resistance = np.max(highs)
        current = closes[-1]

        dist_to_support = current - support
        dist_to_resistance = resistance - current

        if dist_to_support == 0:
            return 100.0
        if dist_to_resistance == 0:
            return 0.0

        ratio = dist_to_support / dist_to_resistance
        # Normalize: ratio of 1 = 50, < 1 = bullish
        return min(50.0 / ratio, 100.0)

    @staticmethod
    def level_confluence(data: pd.DataFrame) -> float:
        """
        Identify confluence of S/R levels.
        
        Returns confluence score 0-100.
        """
        if len(data) < 20:
            return 50.0

        lows = data['Low'].values[-20:]
        highs = data['High'].values[-20:]

        # Find clusters of S/R
        support_levels = []
        resistance_levels = []

        for i in range(len(lows)):
            is_support = lows[i] == np.min(lows[max(0, i-3):min(i+4, len(lows))])
            is_resistance = highs[i] == np.max(highs[max(0, i-3):min(i+4, len(highs))])

            if is_support:
                support_levels.append(lows[i])
            if is_resistance:
                resistance_levels.append(highs[i])

        # Confluence if levels are close
        confluence = 0
        if len(support_levels) > 1:
            confluence += 1
        if len(resistance_levels) > 1:
            confluence += 1

        return min(50.0 + (confluence * 25), 100.0)

    @staticmethod
    def breakout_above_resistance(data: pd.DataFrame) -> float:
        """
        Detect breakout above resistance.
        
        Returns breakout signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values
        resistance = np.max(highs[-20:-5])
        current_high = highs[-1]

        if current_high > resistance * 1.005:
            return 85.0
        elif current_high > resistance:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def breakdown_below_support(data: pd.DataFrame) -> float:
        """
        Detect breakdown below support.
        
        Returns breakdown signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        lows = data['Low'].values
        support = np.min(lows[-20:-5])
        current_low = lows[-1]

        if current_low < support * 0.995:
            return 15.0
        elif current_low < support:
            return 25.0
        else:
            return 50.0
