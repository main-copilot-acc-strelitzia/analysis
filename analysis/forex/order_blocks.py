"""Order block identification for Forex."""

import numpy as np
import pandas as pd


class OrderBlockAnalysis:
    """Identifies order blocks (institutional supply/demand)."""

    @staticmethod
    def bullish_order_block(data: pd.DataFrame) -> float:
        """
        Identify bullish order blocks (demand zones).
        
        Returns bullish OB signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        opens = data['Open'].values
        volumes = data['Volume'].values

        # Bullish OB: Strong impulsive candle followed by pullback
        for i in range(len(data) - 5, len(data) - 1):
            candle_size = abs(closes[i] - opens[i])
            avg_candle = np.mean(np.abs(closes[i-5:i] - opens[i-5:i]))

            # Big bullish candle with volume
            if opens[i] < closes[i] and candle_size > avg_candle * 2 and volumes[i] > np.mean(volumes[i-5:i]) * 1.3:
                # Check if price pulls back
                low_after = np.min(closes[i+1:])
                if low_after < closes[i]:
                    return 80.0

        return 50.0

    @staticmethod
    def bearish_order_block(data: pd.DataFrame) -> float:
        """
        Identify bearish order blocks (supply zones).
        
        Returns bearish OB signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        opens = data['Open'].values
        volumes = data['Volume'].values

        # Bearish OB: Strong impulsive candle followed by pullback
        for i in range(len(data) - 5, len(data) - 1):
            candle_size = abs(closes[i] - opens[i])
            avg_candle = np.mean(np.abs(closes[i-5:i] - opens[i-5:i]))

            # Big bearish candle with volume
            if opens[i] > closes[i] and candle_size > avg_candle * 2 and volumes[i] > np.mean(volumes[i-5:i]) * 1.3:
                # Check if price pulls back
                high_after = np.max(closes[i+1:])
                if high_after > closes[i]:
                    return 20.0

        return 50.0

    @staticmethod
    def order_block_rejection(data: pd.DataFrame) -> float:
        """
        Identify order block rejection patterns.
        
        Returns rejection signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        rejections = 0
        for i in range(5, len(data)):
            # Price touches support/resistance and rejects
            if lows[i] < np.min(lows[i-5:i-1]) and closes[i] > closes[i-1]:
                rejections += 1
            if highs[i] > np.max(highs[i-5:i-1]) and closes[i] < closes[i-1]:
                rejections += 1

        if rejections >= 2:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def institutional_activity_marker(data: pd.DataFrame) -> float:
        """
        Identify markers of institutional activity at OBs.
        
        Returns activity marker signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        # Institutional markers: low volume consolidation, sudden expansion
        volumes = data['Volume'].values[-20:]

        consolidation = np.sum(volumes < np.mean(volumes) * 0.8)
        expansion = np.sum(volumes > np.mean(volumes) * 1.5)

        if consolidation >= 5 and expansion >= 3:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def mitigation_level_detection(data: pd.DataFrame) -> float:
        """
        Detect order block mitigation (when price returns to OB).
        
        Returns mitigation signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values

        # Check if recent price touches previous support/resistance
        for i in range(len(data) - 10, len(data) - 1):
            recent_low = lows[i]
            recent_high = highs[i]

            # Check against prior levels
            prior_resistance = np.max(highs[max(0, i-20):i-5])
            prior_support = np.min(lows[max(0, i-20):i-5])

            if abs(recent_high - prior_resistance) / prior_resistance < 0.001:
                return 75.0
            if abs(recent_low - prior_support) / prior_support < 0.001:
                return 75.0

        return 50.0

    @staticmethod
    def fair_value_gap_ob_confirmation(data: pd.DataFrame) -> float:
        """
        Confirm OBs using fair value gap (FVG) patterns.
        
        Returns confirmation signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values

        # FVG: imbalance between candles
        for i in range(2, len(data)):
            # Bullish FVG: Low > previous high
            if lows[i] > highs[i-2]:
                return 80.0
            # Bearish FVG: High < previous low
            if highs[i] < lows[i-2]:
                return 20.0

        return 50.0
