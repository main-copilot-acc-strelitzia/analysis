"""Market structure analysis for Forex."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators
from analysis.shared.utils import AnalysisUtils


class MarketStructureAnalysis:
    """Analyzes Forex market structure."""

    @staticmethod
    def higher_highs_lower_lows(data: pd.DataFrame) -> float:
        """
        Detect higher highs and lower lows pattern (uptrend).
        
        Returns signal strength 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]

        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        lower_highs = sum(1 for i in range(1, len(highs)) if highs[i] < highs[i-1])

        if higher_highs > lower_highs:
            return 75.0
        elif lower_highs > higher_highs:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def support_resistance_test(data: pd.DataFrame) -> float:
        """
        Identify support/resistance tests and bounces.
        
        Returns strength of support/resistance structure.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values[-20:]
        support, resistance = AnalysisUtils.find_support_resistance(closes, window=5)

        if not support or not resistance:
            return 50.0

        current_close = closes[-1]
        bounces = 0

        for level in support:
            if abs(current_close - level) < (closes[-1] * 0.01):
                bounces += 1

        return min(50.0 + (bounces * 10), 100.0)

    @staticmethod
    def order_block_identification(data: pd.DataFrame) -> float:
        """
        Identify bullish and bearish order blocks.
        
        Order blocks are areas where price may react strongly.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        volumes = data['Volume'].values

        # Find volume spikes with directional moves
        avg_volume = np.mean(volumes[-20:])
        recent_volume = volumes[-5:]

        volume_spike = np.sum(recent_volume > avg_volume * 1.5)
        recent_movement = abs(closes[-1] - closes[-5]) / closes[-5] * 100

        signal = min(50.0 + (volume_spike * 10) + (recent_movement * 5), 100.0)
        return signal

    @staticmethod
    def liquidity_analysis(data: pd.DataFrame) -> float:
        """
        Analyze market liquidity and sweep patterns.
        
        Returns liquidity quality score.
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values[-20:]
        lows = data['Low'].values[-20:]
        volumes = data['Volume'].values[-20:]

        # High liquidity indicators
        avg_range = np.mean(highs - lows)
        high_volume_bars = np.sum(volumes > np.mean(volumes) * 1.2)
        range_uniformity = 1.0 - np.std(highs - lows) / np.mean(highs - lows) if np.mean(highs - lows) > 0 else 0

        liquidity_score = 50.0 + (high_volume_bars * 5) + (range_uniformity * 20)
        return min(liquidity_score, 100.0)

    @staticmethod
    def market_regime(data: pd.DataFrame) -> str:
        """
        Identify current market regime.
        
        Returns regime type: 'Impulsive', 'Corrective', 'Consolidating'
        """
        if len(data) < 20:
            return 'Consolidating'

        closes = data['Close'].values[-20:]
        highs = data['High'].values[-20:]
        lows = data['Low'].values[-20:]

        volatility = np.std(closes) / np.mean(closes)
        range_pct = (np.max(highs) - np.min(lows)) / np.mean(closes) * 100

        if volatility > 0.02 and range_pct > 2.0:
            return 'Impulsive'
        elif volatility < 0.008 or range_pct < 0.5:
            return 'Consolidating'
        else:
            return 'Corrective'

    @staticmethod
    def price_action_patterns(data: pd.DataFrame) -> float:
        """
        Detect price action patterns (swing, reversals).
        
        Returns pattern confidence 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]
        closes = data['Close'].values[-10:]

        swing_high = np.max(highs[-5:])
        swing_low = np.min(lows[-5:])

        if closes[-1] > swing_high * 0.99 and closes[-1] > closes[-2]:
            return 75.0
        elif closes[-1] < swing_low * 1.01 and closes[-1] < closes[-2]:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def imbalance_detection(data: pd.DataFrame) -> float:
        """
        Detect fair value gaps and imbalances.
        
        Returns imbalance strength 0-100.
        """
        if len(data) < 5:
            return 50.0

        for i in range(len(data) - 3, 0, -1):
            current_low = data['Low'].iloc[i]
            prev_high = data['High'].iloc[i-1]
            current_high = data['High'].iloc[i]
            prev_low = data['Low'].iloc[i-1]

            # Bullish imbalance
            if current_low > prev_high:
                return 75.0

            # Bearish imbalance
            if current_high < prev_low:
                return 25.0

        return 50.0
