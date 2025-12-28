"""Session-based analysis for Forex."""

import numpy as np
import pandas as pd
from datetime import datetime, time


class SessionAnalysis:
    """Analyzes Forex by trading sessions."""

    @staticmethod
    def london_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during London session (8:00-16:30 GMT).
        
        Returns London session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]

        # Typical London session behavior: strong volatility
        london_range = np.max(closes) - np.min(closes)
        avg_range = np.mean([np.max(data['Close'].values[max(0, i-5):i+1]) - 
                            np.min(data['Close'].values[max(0, i-5):i+1]) 
                            for i in range(5, len(data), 5)])

        if avg_range == 0:
            return 50.0

        if london_range > avg_range * 1.3:
            return 75.0
        elif london_range < avg_range * 0.7:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def tokyo_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during Tokyo session (21:00-06:00 GMT).
        
        Returns Tokyo session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]

        # Tokyo typically lower volatility
        tokyo_range = np.max(closes) - np.min(closes)

        if tokyo_range > np.mean(closes[-1]) * 0.02:
            return 75.0
        else:
            return 25.0

    @staticmethod
    def new_york_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during New York session (13:00-22:00 GMT).
        
        Returns New York session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]

        # NY session typically strong, especially first hour
        ny_range = np.max(closes) - np.min(closes)

        if ny_range > np.mean(closes[-1]) * 0.025:
            return 80.0
        else:
            return 40.0

    @staticmethod
    def sydney_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during Sydney session (21:00-06:00 GMT).
        
        Returns Sydney session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]
        opens = data['Open'].values[-5:]

        # Sydney session typically opens with some volatility
        movement = np.abs(closes - opens)
        avg_movement = np.mean(movement)

        if avg_movement > np.mean(closes[-1]) * 0.015:
            return 65.0
        else:
            return 45.0

    @staticmethod
    def overlap_analysis(data: pd.DataFrame) -> float:
        """
        Analyze overlap sessions (highest volatility periods).
        
        Returns overlap signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]

        ranges = highs - lows
        avg_range = np.mean(ranges)

        if ranges[-1] > avg_range * 1.5:
            return 80.0
        else:
            return 40.0

    @staticmethod
    def session_open_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price movement at session opens.
        
        Returns open signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        opens = data['Open'].values[-5:]
        closes = data['Close'].values[-5:]

        # Typical opening gaps
        gaps = np.abs(opens - np.roll(closes, 1)[1:])
        avg_gap = np.mean(gaps)

        current_gap = abs(opens[-1] - closes[-2]) if len(closes) > 1 else 0

        if current_gap > avg_gap * 1.3:
            return 70.0
        else:
            return 50.0

    @staticmethod
    def session_volatility_pattern(data: pd.DataFrame) -> float:
        """
        Identify session volatility patterns.
        
        Returns pattern signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        returns = np.abs(np.diff(closes) / closes[:-1])

        recent_vol = np.mean(returns[-5:])
        prior_vol = np.mean(returns[-10:-5])

        if prior_vol == 0:
            return 50.0

        if recent_vol > prior_vol * 1.3:
            return 75.0
        elif recent_vol < prior_vol * 0.7:
            return 25.0
        else:
            return 50.0
