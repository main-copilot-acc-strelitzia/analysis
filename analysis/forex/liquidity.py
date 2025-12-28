"""Liquidity and order block analysis for Forex."""

import numpy as np
import pandas as pd


class LiquidityAnalysis:
    """Analyzes liquidity and order blocks."""

    @staticmethod
    def liquidity_level_detection(data: pd.DataFrame) -> float:
        """
        Detect liquidity levels (areas with high volume).
        
        Returns liquidity signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        volumes = data['Volume'].values
        closes = data['Close'].values

        # High volume with specific price
        avg_volume = np.mean(volumes[-20:])
        high_volume_bars = volumes > avg_volume * 1.5

        if np.sum(high_volume_bars) > 3:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def liquidity_void_detection(data: pd.DataFrame) -> float:
        """
        Detect liquidity voids (areas with low volume).
        
        Returns void signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        volumes = data['Volume'].values
        avg_volume = np.mean(volumes[-20:])

        low_volume_bars = volumes < avg_volume * 0.5
        recent_low_volume = np.sum(low_volume_bars[-5:])

        if recent_low_volume >= 3:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def sweep_detection(data: pd.DataFrame) -> float:
        """
        Detect liquidity sweeps (price touching and rejecting levels).
        
        Returns sweep signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]

        # Detect wick patterns (sweep patterns)
        range_bodies = np.abs(data['Close'].values[-10:] - data['Open'].values[-10:])
        wicks = (highs - np.maximum(data['Close'].values[-10:], data['Open'].values[-10:])) + \
                (np.minimum(data['Close'].values[-10:], data['Open'].values[-10:]) - lows)

        wick_to_body = wicks / (range_bodies + 0.001)

        if np.sum(wick_to_body > 2) >= 2:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def bid_ask_imbalance(data: pd.DataFrame) -> float:
        """
        Detect bid-ask imbalances.
        
        Returns imbalance signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        # Use Close vs Open as proxy for bid/ask pressure
        closes = data['Close'].values[-10:]
        opens = data['Open'].values[-10:]

        bullish_bars = np.sum(closes > opens)
        bearish_bars = np.sum(closes < opens)

        if bullish_bars > bearish_bars * 1.5:
            return 75.0
        elif bearish_bars > bullish_bars * 1.5:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def market_maker_activity(data: pd.DataFrame) -> float:
        """
        Detect market maker activity patterns.
        
        Returns activity signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        # Market makers create patterns: reversals, support/resistance touches
        highs = data['High'].values[-15:]
        lows = data['Low'].values[-15:]
        closes = data['Close'].values[-15:]

        reversals = 0
        for i in range(2, len(highs)):
            if (highs[i-1] > highs[i-2] and lows[i-1] < lows[i-2]) or \
               (lows[i-1] < lows[i-2] and highs[i-1] > highs[i-2]):
                reversals += 1

        if reversals >= 3:
            return 70.0
        else:
            return 50.0

    @staticmethod
    def pool_level_analysis(data: pd.DataFrame) -> float:
        """
        Identify pool levels (consolidation areas with liquidity).
        
        Returns pool signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values[-20:]
        ranges = np.abs(np.diff(closes))
        avg_range = np.mean(ranges)

        # Low range = pool formation
        low_range_periods = np.sum(ranges < avg_range * 0.7)

        if low_range_periods >= 5:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def liquidity_collapse_detection(data: pd.DataFrame) -> float:
        """
        Detect sudden liquidity collapse.
        
        Returns collapse signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        volumes = data['Volume'].values[-10:]
        avg_volume = np.mean(volumes)

        # Sudden drop in volume
        if volumes[-1] < avg_volume * 0.3 and volumes[-2] > avg_volume * 0.8:
            return 85.0
        else:
            return 50.0
