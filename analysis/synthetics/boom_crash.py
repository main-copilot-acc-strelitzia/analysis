"""Boom and Crash indices analysis."""

import numpy as np
import pandas as pd


class BoomCrashAnalysis:
    """Analyzes Boom and Crash synthetic indices."""

    @staticmethod
    def boom_crash_reversal_signal(data: pd.DataFrame) -> float:
        """
        Detect reversal signals in Boom/Crash.
        
        Returns reversal signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values

        # Boom: higher highs, Crash: lower lows
        recent_high = np.max(highs[-5:])
        recent_low = np.min(lows[-5:])
        prior_high = np.max(highs[-10:-5])
        prior_low = np.min(lows[-10:-5])

        if recent_high > prior_high and closes[-1] < np.mean(closes[-5:]):
            return 25.0  # Boom reversal
        elif recent_low < prior_low and closes[-1] > np.mean(closes[-5:]):
            return 75.0  # Crash reversal
        else:
            return 50.0

    @staticmethod
    def boom_probability(data: pd.DataFrame) -> float:
        """
        Estimate probability of boom phase continuation.
        
        Returns boom probability 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        highs = data['High'].values

        recent_trend = np.mean(np.diff(closes[-5:]))
        high_proximity = (np.max(highs[-10:]) - closes[-1]) / np.max(highs[-10:])

        if recent_trend > 0 and high_proximity < 0.02:
            return 80.0
        elif recent_trend > 0:
            return 65.0
        else:
            return 40.0

    @staticmethod
    def crash_probability(data: pd.DataFrame) -> float:
        """
        Estimate probability of crash phase continuation.
        
        Returns crash probability 0-100 (0=high crash prob).
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        lows = data['Low'].values

        recent_trend = np.mean(np.diff(closes[-5:]))
        low_proximity = (closes[-1] - np.min(lows[-10:])) / np.min(lows[-10:])

        if recent_trend < 0 and low_proximity < 0.02:
            return 20.0
        elif recent_trend < 0:
            return 35.0
        else:
            return 60.0

    @staticmethod
    def peak_formation_detection(data: pd.DataFrame) -> float:
        """
        Detect peak formation in boom phase.
        
        Returns peak signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values
        closes = data['Close'].values

        current_high = highs[-1]
        recent_max = np.max(highs[-10:])

        if current_high >= recent_max * 0.99 and closes[-1] < highs[-1]:
            return 80.0  # Peak formed
        else:
            return 50.0

    @staticmethod
    def bottom_formation_detection(data: pd.DataFrame) -> float:
        """
        Detect bottom formation in crash phase.
        
        Returns bottom signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        lows = data['Low'].values
        closes = data['Close'].values

        current_low = lows[-1]
        recent_min = np.min(lows[-10:])

        if current_low <= recent_min * 1.01 and closes[-1] > lows[-1]:
            return 20.0  # Bottom formed
        else:
            return 50.0

    @staticmethod
    def direction_change_probability(data: pd.DataFrame) -> float:
        """
        Estimate probability of direction change.
        
        Returns change probability 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values

        # Measure trend strength
        recent_momentum = np.mean(np.diff(closes[-10:]))
        prior_momentum = np.mean(np.diff(closes[-20:-10]))

        if abs(recent_momentum) < abs(prior_momentum) * 0.5:
            return 75.0  # Weakening trend
        else:
            return 40.0

    @staticmethod
    def synthetic_cycle_phase(data: pd.DataFrame) -> str:
        """
        Identify which phase of boom/crash cycle.
        
        Returns phase: 'Early Boom', 'Mid Boom', 'Peak', 'Early Crash', 'Mid Crash', 'Bottom'
        """
        if len(data) < 10:
            return 'Mid'

        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values

        current = closes[-1]
        recent_high = np.max(highs[-10:])
        recent_low = np.min(lows[-10:])
        range_val = recent_high - recent_low

        if range_val == 0:
            return 'Consolidation'

        position = (current - recent_low) / range_val

        if position > 0.8:
            return 'Peak'
        elif position > 0.5:
            return 'Mid Boom'
        elif position > 0.2:
            return 'Early Crash'
        elif position > 0.05:
            return 'Mid Crash'
        else:
            return 'Bottom'
