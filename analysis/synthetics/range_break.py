"""Range break instruments analysis."""

import numpy as np
import pandas as pd


class RangeBreakAnalysis:
    """Analyzes range break synthetic instruments."""

    @staticmethod
    def range_establishment(data: pd.DataFrame) -> float:
        """
        Detect range establishment.
        
        Returns range signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]

        range_width = np.max(highs) - np.min(lows)
        avg_candle_range = np.mean(highs - lows)

        if avg_candle_range == 0:
            return 50.0

        range_ratio = range_width / (avg_candle_range * len(highs))

        if range_ratio > 5:
            return 80.0
        elif range_ratio > 3:
            return 65.0
        else:
            return 50.0

    @staticmethod
    def range_bound_detection(data: pd.DataFrame) -> float:
        """
        Detect if price is range-bound.
        
        Returns range-bound signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values[-20:]
        highs = data['High'].values[-20:]
        lows = data['Low'].values[-20:]

        # Range-bound: bouncing between support/resistance
        upper_bounce = 0
        lower_bounce = 0

        top = np.max(highs)
        bottom = np.min(lows)
        mid = (top + bottom) / 2

        for i in range(1, len(closes)):
            if closes[i-1] < mid and closes[i] > mid:
                lower_bounce += 1
            elif closes[i-1] > mid and closes[i] < mid:
                upper_bounce += 1

        bounces = upper_bounce + lower_bounce

        if bounces > 3:
            return 80.0
        elif bounces > 1:
            return 60.0
        else:
            return 40.0

    @staticmethod
    def breakout_probability(data: pd.DataFrame) -> float:
        """
        Estimate probability of range breakout.
        
        Returns breakout probability 0-100.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        highs = data['High'].values[-15:]
        lows = data['Low'].values[-15:]

        resistance = np.max(highs)
        support = np.min(lows)
        current = closes[-1]

        dist_to_resistance = (resistance - current) / resistance
        dist_to_support = (current - support) / support if support != 0 else 1

        if dist_to_resistance < 0.01:
            return 85.0
        elif dist_to_support < 0.01:
            return 15.0
        else:
            return 50.0

    @staticmethod
    def false_breakout_detection(data: pd.DataFrame) -> float:
        """
        Detect likelihood of false breakout.
        
        Returns false breakout probability 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        # False breakout: price breaks but returns into range
        for i in range(5, len(data)):
            recent_high = np.max(highs[i-5:i])
            recent_low = np.min(lows[i-5:i])

            if highs[i] > recent_high and closes[i] < np.mean(closes[i-5:i]):
                return 75.0  # Likely false

            if lows[i] < recent_low and closes[i] > np.mean(closes[i-5:i]):
                return 75.0  # Likely false

        return 40.0

    @staticmethod
    def breakout_momentum(data: pd.DataFrame) -> float:
        """
        Measure momentum of breakout.
        
        Returns momentum 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values[-10:]
        momentum = np.mean(np.diff(closes))

        if momentum > 0:
            normalized = min(abs(momentum) / (np.mean(closes) / 100) * 50, 100.0)
            return 50.0 + normalized
        else:
            normalized = min(abs(momentum) / (np.mean(closes) / 100) * 50, 100.0)
            return 50.0 - normalized

    @staticmethod
    def volume_breakout_confirmation(data: pd.DataFrame) -> float:
        """
        Confirm breakout with volume.
        
        Returns confirmation 0-100.
        """
        if len(data) < 15:
            return 50.0

        volumes = data['Volume'].values
        closes = data['Close'].values
        
        recent_vol = volumes[-1]
        avg_vol = np.mean(volumes[-10:])

        recent_momentum = closes[-1] - closes[-5]

        if (recent_vol > avg_vol * 1.5 and recent_momentum > 0) or \
           (recent_vol > avg_vol * 1.5 and recent_momentum < 0):
            return 80.0
        elif recent_vol > avg_vol:
            return 60.0
        else:
            return 40.0

    @staticmethod
    def range_exhaustion(data: pd.DataFrame) -> float:
        """
        Detect range exhaustion (buildup before breakout).
        
        Returns exhaustion signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        ranges = data['High'].values - data['Low'].values
        volumes = data['Volume'].values

        # Narrowing range with volume decline
        recent_range = np.mean(ranges[-5:])
        prior_range = np.mean(ranges[-10:-5])

        recent_vol = np.mean(volumes[-5:])
        prior_vol = np.mean(volumes[-10:-5])

        if recent_range < prior_range * 0.7 and recent_vol < prior_vol * 0.8:
            return 80.0
        else:
            return 50.0
